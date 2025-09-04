# app/models/__init__.py
"""
Models package - SQLAlchemy database models
"""
# Import Base first
from .base import Base
from .task import Task

# Import models in the correct order to avoid relationship problems


# Ensure all relationships are configured
def configure_mappers():
    """Configure all SQLAlchemy mappers"""
    from sqlalchemy.orm import configure_mappers

    configure_mappers()


__all__ = ["Base", "Task", "configure_mappers"]
