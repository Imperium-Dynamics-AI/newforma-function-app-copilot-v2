from typing import Optional


class AppError(Exception):
    """Base exception for application errors."""

    status_code = 500
    message = "An unexpected error occurred."

    def __init__(
        self, message: Optional[str] = None, status_code: Optional[int] = None
    ):
        self.message = message or self.message
        self.status_code = status_code or self.status_code
        super().__init__(self.message)


class BadRequestError(AppError):
    status_code = 400
    message = "Bad request."


class NotFoundError(AppError):
    status_code = 404
    message = "Resource not found."


class ConflictError(AppError):
    status_code = 409
    message = "Conflict occurred."


class ValidationError(AppError):
    status_code = 422
    message = "Validation failed."
