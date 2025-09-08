# app/schemas/task.py
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    completed: bool = False


class TaskCreate(TaskBase):
    pass


class TaskUpdate(TaskBase):
    pass


class TaskResponse(TaskBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int


class PaginatedTaskResponse(BaseModel):
    tasks: List[TaskResponse]
    total: int
    skip: int
    limit: int
