"""
API v2 - Future version with enhanced features
"""

from fastapi import APIRouter

from .auth import router as auth_router
from .tasks import router as tasks_router

api_router = APIRouter()

# Include routers with enhanced features
api_router.include_router(tasks_router, prefix="/tasks", tags=["tasks-v2"])
api_router.include_router(auth_router, prefix="/auth", tags=["auth-v2"])

__all__ = ["api_router", "auth_router", "tasks_router"]
