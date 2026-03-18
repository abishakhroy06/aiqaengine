"""
Google OAuth helpers: build auth URL, exchange code for tokens, fetch user info.
"""
import logging

from httpx import AsyncClient

from app.config import settings

logger = logging.getLogger(__name__)

GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/auth"


def get_google_auth_url(redirect_uri: str) -> str:
    """Build the Google OAuth2 authorization URL."""
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "email profile",
        "access_type": "offline",
    }
    query = "&".join(f"{k}={v}" for k, v in params.items())
    return f"{GOOGLE_AUTH_URL}?{query}"


async def get_google_tokens(code: str, redirect_uri: str) -> dict:
    """Exchange an authorization code for Google OAuth tokens."""
    async with AsyncClient() as client:
        response = await client.post(
            GOOGLE_TOKEN_URL,
            data={
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": redirect_uri,
            },
        )
        return response.json()


async def get_google_user(access_token: str) -> dict:
    """Fetch the authenticated user's profile from Google."""
    async with AsyncClient() as client:
        response = await client.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        return response.json()
