# app/api/v1/tasks.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app import models, schemas
from app.database import get_db
from app.schemas.auth import CurrentUser
from app.schemas.task import PaginatedTaskResponse
from app.utils.auth import get_current_user

router = APIRouter()


@router.post("/", response_model=schemas.TaskResponse)
async def create_task(
    task: schemas.TaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    db_task = models.Task(**task.model_dump(), user_id=current_user.id)
    db.add(db_task)

    await db.commit()
    await db.refresh(db_task)

    return db_task


@router.get("/", response_model=PaginatedTaskResponse)
async def read_tasks(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    Retrieve paginated tasks for the authenticated user with total count.
    """
    # Count total tasks for the user
    count_result = await db.execute(
        select(func.count(models.Task.id)).where(models.Task.user_id == current_user.id)
    )
    total = count_result.scalar_one()

    # Fetch paginated tasks
    result = await db.execute(
        select(models.Task)
        .where(models.Task.user_id == current_user.id)
        .offset(skip)
        .limit(limit)
    )
    tasks = result.scalars().all()

    return {"tasks": tasks, "total": total, "skip": skip, "limit": limit}


@router.get("/{task_id}", response_model=schemas.TaskResponse)
async def read_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    # Fetch the task and ensure it belongs to the current user
    result = await db.execute(select(models.Task).where(models.Task.id == task_id))
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to access this task"
        )

    return task


@router.put("/{task_id}", response_model=schemas.TaskResponse)
async def update_task(
    task_id: int,
    task: schemas.TaskUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    # Find the task and ensure it belongs to the current user
    result = await db.execute(select(models.Task).where(models.Task.id == task_id))
    db_task = result.scalar_one_or_none()

    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")

    if db_task.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to update this task"
        )

    # Apply updates
    for key, value in task.model_dump(exclude_unset=True).items():
        setattr(db_task, key, value)

    await db.commit()
    await db.refresh(db_task)
    return db_task


@router.delete("/{task_id}")
async def delete_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    # Find the task and ensure it belongs to the current user
    result = await db.execute(select(models.Task).where(models.Task.id == task_id))
    db_task = result.scalar_one_or_none()

    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")

    if db_task.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to delete this task"
        )

    await db.delete(db_task)
    await db.commit()
    return {"detail": "Task deleted"}
