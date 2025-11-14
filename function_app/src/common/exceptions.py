# handlers/exceptions.py
"""
Custom exception hierarchy for the Todo API.
All exceptions inherit from TodoAPIError so a single catch can be used.
"""

from typing import Any, Dict, Optional


class TodoAPIError(Exception):
    """Base exception for all Todo-API errors."""

    status_code = 500

    def __init__(
        self, detail: str = "An error occurred", error_code: str = "INTERNAL_ERROR", **kwargs
    ):
        self.detail = detail
        self.error_code = error_code
        self.extra: Dict[str, Any] = kwargs

    def to_response(self) -> Dict[str, Any]:
        """
        Convert the exception to a response dictionary.

        Returns:
            Dict[str, Any]: Error response dictionary.
        """
        response = {
            "error": self.detail,
            "error_code": self.error_code,
        }
        response.update(self.extra)
        return response


class ValidationError(TodoAPIError):
    """Raised when request data fails validation."""

    status_code = 400

    def __init__(
        self, detail: str = "Validation failed", error_code: str = "VALIDATION_ERROR", **kwargs
    ):
        super().__init__(detail, error_code, **kwargs)


class NotFoundError(TodoAPIError):
    """Raised when a requested resource does not exist."""

    status_code = 404

    def __init__(
        self,
        resource: str,
        identifier: Optional[str] = None,
        error_code: str = "NOT_FOUND",
        **kwargs,
    ):
        detail = f"{resource} not found"
        if identifier:
            detail += f": {identifier}"
        super().__init__(detail, error_code, **kwargs)


class ConflictError(TodoAPIError):
    """Raised on duplicate creation or illegal state change."""

    status_code = 409

    def __init__(self, detail: str = "Conflict", error_code: str = "CONFLICT", **kwargs):
        super().__init__(detail, error_code, **kwargs)


class UnauthorizedError(TodoAPIError):
    """Raised when the user is not allowed to perform the action."""

    status_code = 401

    def __init__(self, detail: str = "Unauthorized", error_code: str = "UNAUTHORIZED", **kwargs):
        super().__init__(detail, error_code, **kwargs)


class ListNotFoundError(NotFoundError):
    """Raised when a To-Do list is not found."""

    def __init__(self, list_name: str, **kwargs):
        super().__init__("List", list_name, error_code="LIST_NOT_FOUND", **kwargs)


class TaskNotFoundError(NotFoundError):
    """Raised when a task is not found."""

    def __init__(self, task_name: str, **kwargs):
        super().__init__("Task", task_name, error_code="TASK_NOT_FOUND", **kwargs)


class SubtaskNotFoundError(NotFoundError):
    """Raised when a subtask is not found."""

    def __init__(self, subtask_name: str, **kwargs):
        super().__init__("Subtask", subtask_name, error_code="SUBTASK_NOT_FOUND", **kwargs)


class DuplicateListError(ConflictError):
    """Raised when attempting to create a duplicate list."""

    def __init__(self, list_name: str, **kwargs):
        detail = f"A list with the name '{list_name}' already exists"
        super().__init__(detail, error_code="DUPLICATE_LIST", **kwargs)


class DuplicateTaskError(ConflictError):
    """Raised when attempting to create a duplicate task."""

    def __init__(self, task_name: str, **kwargs):
        detail = f"A task with the title '{task_name}' already exists in this list"
        super().__init__(detail, error_code="DUPLICATE_TASK", **kwargs)


class DuplicateSubtaskError(ConflictError):
    """Raised when attempting to create a duplicate subtask."""

    def __init__(self, subtask_name: str, **kwargs):
        detail = f"A subtask with the title '{subtask_name}' already exists for this task"
        super().__init__(detail, error_code="DUPLICATE_SUBTASK", **kwargs)


class InvalidStatusError(ValidationError):
    """Raised when an invalid task status is provided."""

    def __init__(self, status: str, valid_statuses: list = None, **kwargs):
        if valid_statuses is None:
            valid_statuses = ["notStarted", "inProgress", "completed", "waitingOnOthers"]
        detail = f"Invalid status '{status}'. Must be one of {valid_statuses}"
        super().__init__(detail, error_code="INVALID_STATUS", **kwargs)


class EmptyFieldError(ValidationError):
    """Raised when a required field is empty."""

    def __init__(self, field_name: str, **kwargs):
        detail = f"{field_name} cannot be empty"
        super().__init__(detail, error_code="EMPTY_FIELD", **kwargs)


class GraphAPIError(TodoAPIError):
    """Raised when the Microsoft Graph API request fails."""

    def __init__(self, detail: str = "Graph API request failed", http_status: int = 500, **kwargs):
        self.status_code = http_status
        super().__init__(detail, error_code="GRAPH_API_ERROR", **kwargs)


class MissingParameterError(ValidationError):
    """Raised when a required parameter is missing."""

    def __init__(self, parameter_name: str, **kwargs):
        detail = f"Required parameter '{parameter_name}' is missing"
        super().__init__(detail, error_code="MISSING_PARAMETER", **kwargs)


# ==================== Event-specific Exceptions ====================


class EventNotFoundError(NotFoundError):
    """Raised when a calendar event is not found."""

    def __init__(self, event_identifier: str, **kwargs):
        super().__init__("Event", event_identifier, error_code="EVENT_NOT_FOUND", **kwargs)


class DuplicateEventError(ConflictError):
    """Raised when attempting to create a duplicate event."""

    def __init__(self, event_title: str, **kwargs):
        detail = f"An event with the title '{event_title}' already exists at this time"
        super().__init__(detail, error_code="DUPLICATE_EVENT", **kwargs)


class InvalidTimeRangeError(ValidationError):
    """Raised when event time range is invalid (end before start)."""

    def __init__(self, detail: str = "Invalid time range: end time must be after start time", **kwargs):
        super().__init__(detail, error_code="INVALID_TIME_RANGE", **kwargs)


class InvalidRecurrenceError(ValidationError):
    """Raised when recurrence pattern parameters are invalid."""

    def __init__(self, detail: str = "Invalid recurrence configuration", **kwargs):
        super().__init__(detail, error_code="INVALID_RECURRENCE", **kwargs)
