"""
Business logic for authentication: register, login, token refresh, logout, OAuth.
"""
import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.auth.jwt import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.config import settings
from app.exceptions import ConflictError, NotFoundError, UnauthorizedError
from app.models.token import RefreshToken
from app.models.user import User

logger = logging.getLogger(__name__)


def register_user(
    db: Session,
    email: str,
    password: str,
    full_name: str | None = None,
) -> User:
    """Create a new email/password user. Raises ConflictError if email is taken."""
    if db.query(User).filter(User.email == email).first():
        raise ConflictError("Email already registered")

    user = User(
        email=email,
        hashed_password=hash_password(password),
        full_name=full_name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    logger.info("Registered new user: %s", email)
    return user


def login_user(db: Session, email: str, password: str) -> tuple[str, str]:
    """Authenticate a user and return (access_token, refresh_token)."""
    user = db.query(User).filter(User.email == email).first()
    if not user or not user.hashed_password or not verify_password(password, user.hashed_password):
        raise UnauthorizedError("Invalid email or password")
    if not user.is_active:
        raise UnauthorizedError("Account is inactive")

    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = _create_and_store_refresh_token(db, user.id)
    logger.info("User logged in: %s", email)
    return access_token, refresh_token


def refresh_tokens(db: Session, refresh_token_str: str) -> tuple[str, str]:
    """Rotate a refresh token and return a new (access_token, refresh_token) pair."""
    stored = db.query(RefreshToken).filter(RefreshToken.token == refresh_token_str).first()
    if not stored:
        raise UnauthorizedError("Invalid refresh token")

    expires = stored.expires_at
    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=timezone.utc)
    if expires < datetime.now(timezone.utc):
        db.delete(stored)
        db.commit()
        raise UnauthorizedError("Refresh token expired")

    payload = decode_token(refresh_token_str)
    if not payload or payload.get("type") != "refresh":
        raise UnauthorizedError("Invalid refresh token")

    # Rotate: delete old token, issue new pair
    db.delete(stored)
    new_access = create_access_token({"sub": payload["sub"]})
    new_refresh = _create_and_store_refresh_token(db, int(payload["sub"]))
    logger.info("Rotated refresh token for user_id=%s", payload["sub"])
    return new_access, new_refresh


def logout_user(db: Session, refresh_token_str: str) -> None:
    """Revoke a refresh token (no-op if already absent)."""
    stored = db.query(RefreshToken).filter(RefreshToken.token == refresh_token_str).first()
    if stored:
        db.delete(stored)
        db.commit()
        logger.info("Refresh token revoked for user_id=%s", stored.user_id)


def get_or_create_oauth_user(
    db: Session,
    email: str,
    full_name: str | None,
    google_id: str,
    avatar_url: str | None,
) -> User:
    """Return an existing user (updating OAuth fields) or create a new OAuth user."""
    user = db.query(User).filter(User.email == email).first()
    if user:
        if not user.is_active:
            raise UnauthorizedError("Account is inactive")
        user.google_id = google_id
        if avatar_url:
            user.avatar_url = avatar_url
        db.commit()
        db.refresh(user)
        logger.info("Updated OAuth fields for existing user: %s", email)
        return user

    user = User(
        email=email,
        full_name=full_name,
        oauth_provider="google",
        google_id=google_id,
        avatar_url=avatar_url,
        is_verified=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    logger.info("Created new OAuth user: %s", email)
    return user


def _create_and_store_refresh_token(db: Session, user_id: int) -> str:
    """Generate a refresh token, persist it, and return the token string."""
    token_str = create_refresh_token({"sub": str(user_id)})
    expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    rt = RefreshToken(user_id=user_id, token=token_str, expires_at=expires_at)
    db.add(rt)
    db.commit()
    return token_str
