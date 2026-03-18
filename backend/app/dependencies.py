"""
Top-level FastAPI dependencies re-exported for convenience.

get_db is provided by app.database (DATABASE-AGENT).
get_current_user / get_current_active_user are provided by app.auth.dependencies.
"""
import logging

from app.database import get_db  # noqa: F401
from app.auth.dependencies import get_current_user, get_current_active_user  # noqa: F401

logger = logging.getLogger(__name__)
