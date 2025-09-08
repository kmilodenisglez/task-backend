# app/v1/__init__.py
"""
Routers package - API route handlers
"""
from fastapi import APIRouter

from .auth import router as auth_router
from .tasks import router as tasks_router

api_router = APIRouter()

# Include all routers under /api
api_router.include_router(tasks_router, prefix="/tasks", tags=["tasks"])
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])

# Exportar para facilitar el import
__all__ = [
    "auth_router",
    "tasks_router",
    "api_router",
]
