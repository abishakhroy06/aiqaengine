"""
Auth router: register, login, token refresh/logout, profile, Google OAuth.
"""
import logging

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.auth.google import get_google_auth_url, get_google_tokens, get_google_user
from app.auth.jwt import create_access_token
from app.config import settings
from app.database import get_db
from app.exceptions import AppException
from app.models.user import User
from app.schemas.auth import (
    RefreshRequest,
    RegisterRequest,
    Token,
    UpdateProfileRequest,
    UserResponse,
)
from app.services.auth_service import (
    _create_and_store_refresh_token,
    get_or_create_oauth_user,
    login_user,
    logout_user,
    refresh_tokens,
    register_user,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(req: RegisterRequest, db: Session = Depends(get_db)) -> User:
    """Register a new user with email and password."""
    return register_user(db, req.email, req.password, req.full_name)


@router.post("/login", response_model=Token)
async def login(
    form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> Token:
    """Authenticate with email (username field) and password; returns token pair."""
    access_token, refresh_token = login_user(db, form.username, form.password)
    return Token(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=Token)
async def refresh(req: RefreshRequest, db: Session = Depends(get_db)) -> Token:
    """Exchange a valid refresh token for a new access/refresh token pair."""
    access_token, refresh_token = refresh_tokens(db, req.refresh_token)
    return Token(access_token=access_token, refresh_token=refresh_token)


@router.post("/logout")
async def logout(req: RefreshRequest, db: Session = Depends(get_db)) -> dict:
    """Revoke the provided refresh token."""
    logout_user(db, req.refresh_token)
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserResponse)
async def me(user: User = Depends(get_current_user)) -> User:
    """Return the profile of the currently authenticated user."""
    return user


@router.get("/google")
async def google_login() -> RedirectResponse:
    """Redirect the browser to Google's OAuth2 consent screen."""
    redirect_uri = f"{settings.FRONTEND_URL}/auth/callback"
    url = get_google_auth_url(redirect_uri)
    return RedirectResponse(url)


@router.get("/google/callback")
async def google_callback(code: str, db: Session = Depends(get_db)) -> Token:
    """Handle the Google OAuth2 callback and return a token pair."""
    redirect_uri = f"{settings.FRONTEND_URL}/auth/callback"

    tokens = await get_google_tokens(code, redirect_uri)
    if "error" in tokens:
        raise HTTPException(status_code=400, detail=f"Google OAuth error: {tokens['error']}")

    google_user = await get_google_user(tokens["access_token"])
    if "error" in google_user:
        raise HTTPException(status_code=400, detail="Failed to get Google user info")

    user = get_or_create_oauth_user(
        db,
        email=google_user["email"],
        full_name=google_user.get("name"),
        google_id=google_user["id"],
        avatar_url=google_user.get("picture"),
    )

    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = _create_and_store_refresh_token(db, user.id)
    return Token(access_token=access_token, refresh_token=refresh_token)
