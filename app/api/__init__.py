# app/api/__init__.py
"""
API package with versioning support
"""
from fastapi import APIRouter

from .v1 import api_router as v1_router
from .v2 import api_router as v2_router

# Main API router that includes all versions
api_router = APIRouter()

# Include versioned routers
api_router.include_router(v1_router, prefix="/v1", tags=["v1"])
api_router.include_router(v2_router, prefix="/v2", tags=["v2"])

__all__ = ["api_router", "v1_router", "v2_router"]
