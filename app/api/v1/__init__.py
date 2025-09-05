"""
Routers package - API route handlers
"""
from fastapi import APIRouter

from .auth import router as auth_router
from .tasks import router as task_router

__all__ = ["auth_router", "task_router"]

api_router = APIRouter()

# Include all routers under /api
api_router.include_router(task_router, prefix="/v1")
api_router.include_router(auth_router, prefix="/v1")