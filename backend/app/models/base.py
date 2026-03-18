"""
Base mixins for SQLAlchemy models.
"""
import logging
from sqlalchemy import Column, DateTime, Boolean
from sqlalchemy.sql import func

logger = logging.getLogger(__name__)


class TimestampMixin:
    """Mixin that adds created_at and updated_at timestamp columns."""

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        onupdate=func.now(),
        nullable=True,
    )


class SoftDeleteMixin:
    """Mixin that adds soft-delete support via is_deleted and deleted_at columns."""

    is_deleted = Column(Boolean, default=False, nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
