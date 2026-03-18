from typing import Optional


class AppException(Exception):
    """Base exception class for all application exceptions."""

    status_code: int = 500
    code: str = "INTERNAL_ERROR"

    def __init__(self, message: str, code: Optional[str] = None, status_code: Optional[int] = None) -> None:
        self.message = message
        if code is not None:
            self.code = code
        if status_code is not None:
            self.status_code = status_code
        super().__init__(self.message)


class NotFoundError(AppException):
    """Raised when a requested resource is not found."""

    status_code: int = 404
    code: str = "NOT_FOUND"

    def __init__(self, message: str = "Resource not found") -> None:
        super().__init__(message=message)


class ConflictError(AppException):
    """Raised when a resource already exists or there is a conflict."""

    status_code: int = 409
    code: str = "CONFLICT"

    def __init__(self, message: str = "Resource already exists") -> None:
        super().__init__(message=message)


class UnauthorizedError(AppException):
    """Raised when authentication is required but not provided or is invalid."""

    status_code: int = 401
    code: str = "UNAUTHORIZED"

    def __init__(self, message: str = "Authentication required") -> None:
        super().__init__(message=message)


class ForbiddenError(AppException):
    """Raised when the authenticated user lacks permission to perform an action."""

    status_code: int = 403
    code: str = "FORBIDDEN"

    def __init__(self, message: str = "Permission denied") -> None:
        super().__init__(message=message)


class ValidationError(AppException):
    """Raised when input data fails validation."""

    status_code: int = 422
    code: str = "VALIDATION_ERROR"

    def __init__(self, message: str = "Validation failed") -> None:
        super().__init__(message=message)
