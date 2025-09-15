"""
Enhanced tasks API v2 with additional features
"""

from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app import models
from app.database import get_db
from app.schemas.auth import CurrentUser
from app.schemas.task import PaginatedTaskResponse
from app.utils.auth import get_current_user
from app.utils.logging import get_logger

router = APIRouter()
logger = get_logger("tasks_v2")


@router.get("/", response_model=PaginatedTaskResponse)
async def read_tasks_v2(
    skip: int = Query(0, ge=0, description="Number of tasks to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of tasks to return"),
    completed: Optional[bool] = Query(None, description="Filter by completion status"),
    search: Optional[str] = Query(None, description="Search in title and description"),
    created_after: Optional[datetime] = Query(
        None, description="Filter tasks created after this date"
    ),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    Enhanced task listing with advanced filtering and search.
    """
    logger.info(
        "Fetching tasks with filters",
        extra={
            "user_id": current_user.id,
            "filters": {
                "skip": skip,
                "limit": limit,
                "completed": completed,
                "search": search,
                "created_after": created_after.isoformat() if created_after else None,
            },
        },
    )

    # Build query conditions
    conditions = [models.Task.user_id == current_user.id]

    if completed is not None:
        conditions.append(models.Task.completed == completed)

    if search:
        search_condition = or_(
            models.Task.title.ilike(f"%{search}%"),
            models.Task.description.ilike(f"%{search}%"),
        )
        conditions.append(search_condition)

    if created_after:
        conditions.append(models.Task.created_at >= created_after)

    # Count total tasks
    count_result = await db.execute(
        select(func.count(models.Task.id)).where(and_(*conditions))
    )
    total = count_result.scalar_one()

    # Fetch paginated tasks
    result = await db.execute(
        select(models.Task)
        .where(and_(*conditions))
        .order_by(models.Task.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    tasks = result.scalars().all()

    logger.info(
        "Tasks fetched successfully",
        extra={"user_id": current_user.id, "total": total, "returned": len(tasks)},
    )

    return {"tasks": tasks, "total": total, "skip": skip, "limit": limit}


@router.get("/stats", response_model=dict)
async def get_task_stats(
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    Get task statistics for the current user.
    """
    logger.info("Fetching task statistics", extra={"user_id": current_user.id})

    # Total tasks
    total_result = await db.execute(
        select(func.count(models.Task.id)).where(models.Task.user_id == current_user.id)
    )
    total_tasks = total_result.scalar_one()

    # Completed tasks
    completed_result = await db.execute(
        select(func.count(models.Task.id)).where(
            and_(models.Task.user_id == current_user.id, models.Task.completed)
        )
    )
    completed_tasks = completed_result.scalar_one()

    # Tasks created this week
    week_ago = datetime.utcnow() - timedelta(days=7)
    weekly_result = await db.execute(
        select(func.count(models.Task.id)).where(
            and_(
                models.Task.user_id == current_user.id,
                models.Task.created_at >= week_ago,
            )
        )
    )
    weekly_tasks = weekly_result.scalar_one()

    stats = {
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "pending_tasks": total_tasks - completed_tasks,
        "completion_rate": round(
            (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0, 2
        ),
        "tasks_this_week": weekly_tasks,
    }

    logger.info(
        "Task statistics calculated", extra={"user_id": current_user.id, "stats": stats}
    )

    return stats
