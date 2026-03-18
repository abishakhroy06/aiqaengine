"""
User SQLAlchemy model.
"""
import logging
from sqlalchemy import Column, Integer, String, Boolean, Index
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.base import TimestampMixin

logger = logging.getLogger(__name__)


class User(TimestampMixin, Base):
    """Represents a registered user (email/password or OAuth)."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=True)
    full_name = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    oauth_provider = Column(String(50), nullable=True)
    google_id = Column(String(255), unique=True, index=True, nullable=True)
    avatar_url = Column(String(500), nullable=True)

    # Relationships
    qa_sessions = relationship(
        "QASession",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="select",
    )
    refresh_tokens = relationship(
        "RefreshToken",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="select",
    )

    __table_args__ = (
        Index("ix_users_email_active", "email", "is_active"),
    )
