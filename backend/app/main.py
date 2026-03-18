import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.exceptions import AppException

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title=settings.APP_NAME, version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    logger.warning("AppException: code=%s message=%s", exc.code, exc.message)
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message, "code": exc.code},
    )


@app.get("/health")
async def health() -> dict:
    return {"status": "healthy", "app": settings.APP_NAME}


# Phase 2 routers are included below.
# Each import is wrapped in a try/except so the app still starts during the
# foundation phase before those modules are created.

try:
    from app.routers import auth as auth_router  # noqa: F401
    app.include_router(auth_router.router, prefix="/api/v1/auth", tags=["auth"])
    logger.info("Loaded auth router")
except (ImportError, AttributeError):
    logger.info("Auth router not yet available — skipping")

try:
    from app.routers import users as users_router  # noqa: F401
    app.include_router(users_router.router, prefix="/api/v1/users", tags=["users"])
    logger.info("Loaded users router")
except (ImportError, AttributeError):
    logger.info("Users router not yet available — skipping")

try:
    from app.routers import sessions as sessions_router  # noqa: F401
    app.include_router(sessions_router.router, prefix="/api/v1/sessions", tags=["sessions"])
    logger.info("Loaded sessions router")
except (ImportError, AttributeError):
    logger.info("Sessions router not yet available — skipping")
