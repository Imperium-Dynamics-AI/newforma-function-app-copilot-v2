# handlers/exceptions.py
"""
Custom exception hierarchy for the Todo API.
All exceptions inherit from TodoAPIError so a single catch can be used.
"""

from typing import Any, Dict, Optional


class TodoAPIError(Exception):
    """Base exception for all Todo-API errors."""

    status_code: int = 500
    detail: str = "Internal Server Error"

    def to_response(self) -> Dict[str, Any]:
        """
        Convert the exception to a response dictionary.

        Returns:
            Dict[str, Any]: Error response dictionary.
        """
        return {"error": self.detail}


class ValidationError(TodoAPIError):
    """Raised when request data fails validation."""

    status_code = 400

    def __init__(self, detail: str = "Validation failed"):
        self.detail = detail


class NotFoundError(TodoAPIError):
    """Raised when a requested resource does not exist."""

    status_code = 404

    def __init__(self, resource: str, identifier: Optional[str] = None):
        self.detail = f"{resource} not found"
        if identifier:
            self.detail += f": {identifier}"


class ConflictError(TodoAPIError):
    """Raised on duplicate creation or illegal state change."""

    status_code = 409

    def __init__(self, detail: str = "Conflict"):
        self.detail = detail


class UnauthorizedError(TodoAPIError):
    """Raised when the user is not allowed to perform the action."""

    status_code = 401

    def __init__(self, detail: str = "Unauthorized"):
        self.detail = detail
