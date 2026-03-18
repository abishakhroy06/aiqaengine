"""
JWT utilities: password hashing and token creation/decoding.
"""
import logging
from datetime import datetime, timedelta, timezone

import bcrypt
from jose import JWTError, jwt

from app.config import settings

logger = logging.getLogger(__name__)


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a plaintext password against a bcrypt hash."""
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def hash_password(password: str) -> str:
    """Hash a plaintext password using bcrypt."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def create_access_token(data: dict) -> str:
    """Create a short-lived JWT access token."""
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode(
        {**data, "exp": expire, "type": "access"},
        settings.SECRET_KEY,
        settings.ALGORITHM,
    )


def create_refresh_token(data: dict) -> str:
    """Create a long-lived JWT refresh token."""
    import uuid
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    return jwt.encode(
        {**data, "exp": expire, "type": "refresh", "jti": str(uuid.uuid4())},
        settings.SECRET_KEY,
        settings.ALGORITHM,
    )


def decode_token(token: str) -> dict | None:
    """Decode and verify a JWT token. Returns None on any error."""
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        logger.debug("JWT decode failed — token invalid or expired")
        return None
