# app/api/v1/tasks.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/api/v1/tasks", tags=["tasks"])

# Detect testing mode
from app.config import settings

# Define el tipo de sesión según el modo
if settings.testing:
    DBSession = Session
else:
    DBSession = AsyncSession


@router.post("/", response_model=schemas.TaskResponse)
async def create_task(task: schemas.TaskCreate, db: DBSession = Depends(get_db)):
    db_task = models.Task(**task.model_dump())
    db.add(db_task)

    if settings.testing:
        db.commit()  # Síncrono para testing
        db.refresh(db_task)
    else:
        await db.commit()  # Asíncrono para producción
        await db.refresh(db_task)

    return db_task


@router.get("/", response_model=list[schemas.TaskResponse])
async def read_tasks(skip: int = 0, limit: int = 100, db: DBSession = Depends(get_db)):
    if settings.testing:
        # Modo síncrono para testing
        tasks = db.query(models.Task).offset(skip).limit(limit).all()
    else:
        # Modo asíncrono para producción
        result = await db.execute(select(models.Task).offset(skip).limit(limit))
        tasks = result.scalars().all()

    return tasks


@router.get("/{task_id}", response_model=schemas.TaskResponse)
async def read_task(task_id: int, db: DBSession = Depends(get_db)):
    if settings.testing:
        # Modo síncrono para testing
        task = db.query(models.Task).filter(models.Task.id == task_id).first()
    else:
        # Modo asíncrono para producción
        result = await db.execute(select(models.Task).where(models.Task.id == task_id))
        task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.put("/{task_id}", response_model=schemas.TaskResponse)
async def update_task(task_id: int, task: schemas.TaskUpdate, db: DBSession = Depends(get_db)):
    if settings.testing:
        # Modo síncrono para testing
        db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    else:
        # Modo asíncrono para producción
        result = await db.execute(select(models.Task).where(models.Task.id == task_id))
        db_task = result.scalar_one_or_none()

    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")

    for key, value in task.model_dump(exclude_unset=True).items():
        setattr(db_task, key, value)

    if settings.testing:
        db.commit()  # Síncrono para testing
        db.refresh(db_task)
    else:
        await db.commit()  # Asíncrono para producción
        await db.refresh(db_task)

    return db_task


@router.delete("/{task_id}")
async def delete_task(task_id: int, db: DBSession = Depends(get_db)):
    if settings.testing:
        # Modo síncrono para testing
        db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    else:
        # Modo asíncrono para producción
        result = await db.execute(select(models.Task).where(models.Task.id == task_id))
        db_task = result.scalar_one_or_none()

    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")

    db.delete(db_task)

    if settings.testing:
        db.commit()  # Síncrono para testing
    else:
        await db.commit()  # Asíncrono para producción

    return {"detail": "Task deleted"}
