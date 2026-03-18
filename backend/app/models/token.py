"""
RefreshToken SQLAlchemy model.
"""
import logging
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.base import TimestampMixin

logger = logging.getLogger(__name__)


class RefreshToken(TimestampMixin, Base):
    """Stores JWT refresh tokens for users."""

    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    token = Column(String(500), unique=True, index=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)

    # Relationships
    user = relationship("User", back_populates="refresh_tokens", lazy="select")
