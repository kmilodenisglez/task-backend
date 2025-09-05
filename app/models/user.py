# app/models/user.py
from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .task import Task


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(unique=True, index=True, nullable=False)
    name: Mapped[Optional[str]] = mapped_column(nullable=True)
    hashed_password: Mapped[Optional[str]] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    # Relationship with tasks
    tasks: Mapped[List["Task"]] = relationship("Task", back_populates="user", cascade="all, delete-orphan")
