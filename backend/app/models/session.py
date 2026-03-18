"""
QASession and QAOutput SQLAlchemy models.
"""
import enum
import logging
from sqlalchemy import Column, Integer, String, Text, JSON, ForeignKey, Enum, Index
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.base import TimestampMixin

logger = logging.getLogger(__name__)


class SessionStatus(str, enum.Enum):
    """Possible states for a QA session."""

    pending = "pending"
    generating = "generating"
    complete = "complete"
    failed = "failed"


class QASession(TimestampMixin, Base):
    """Represents a single AI QA generation session."""

    __tablename__ = "qa_sessions"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name = Column(String(255), nullable=False)
    requirement = Column(Text, nullable=False)

    # Structured context stored as JSON:
    # {
    #   "product": str,
    #   "platform": str,
    #   "users_roles": str,
    #   "rules_constraints": str,
    #   "risks": str,
    #   "environment": str
    # }
    context = Column(JSON, nullable=True)

    template = Column(String(50), default="full", nullable=False)
    status = Column(
        Enum(SessionStatus, name="session_status_enum"),
        default=SessionStatus.pending,
        nullable=False,
    )

    # Relationships
    user = relationship("User", back_populates="qa_sessions", lazy="select")
    output = relationship(
        "QAOutput",
        back_populates="session",
        uselist=False,
        cascade="all, delete-orphan",
        lazy="select",
    )

    __table_args__ = (
        Index("ix_qa_sessions_user_id_status", "user_id", "status"),
    )


class QAOutput(TimestampMixin, Base):
    """Stores the AI-generated QA artifacts for a QASession."""

    __tablename__ = "qa_outputs"

    id = Column(Integer, primary_key=True, nullable=False)
    session_id = Column(
        Integer,
        ForeignKey("qa_sessions.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )

    # Scenario map stored as JSON:
    # {
    #   "main_flows": [str, ...],
    #   "alternate_flows": [str, ...],
    #   "error_flows": [str, ...],
    #   "permission_flows": [str, ...],
    #   "integration_flows": [str, ...]
    # }
    scenario_map = Column(JSON, nullable=True)

    # Test cases stored as JSON list of dicts:
    # [
    #   {
    #     "test_id": str,
    #     "scenario": str,
    #     "type": str,
    #     "preconditions": str,
    #     "steps": [str, ...],
    #     "test_data": str,
    #     "expected_result": str,
    #     "priority": str,
    #     "risk_notes": str
    #   },
    #   ...
    # ]
    test_cases = Column(JSON, nullable=True)

    # List of assumption strings
    assumptions = Column(JSON, nullable=True)

    # List of open question strings
    questions = Column(JSON, nullable=True)

    # Checklist result stored as JSON:
    # {
    #   "positive_negative": bool,
    #   "boundary_conditions": bool,
    #   "permissions_roles": bool,
    #   "state_based": bool,
    #   "clear_expected_results": bool,
    #   "no_duplicates": bool,
    #   "traceability": bool
    # }
    checklist_result = Column(JSON, nullable=True)

    # Relationships
    session = relationship("QASession", back_populates="output", lazy="select")
