# handlers/todo_subtasks_handler.py
"""
Handler for To-Do subtask operations.
"""

import logging

import azure.functions as func

from src.common.exceptions import TodoAPIError, ValidationError
from src.managers.todo_manager import TodoManager
from src.models.todo_subtasks import (
    CreateSubtaskRequest,
    DeleteSubtaskRequest,
    EditSubtaskRequest,
    SubtaskResponse,
    SubtasksResponse,
)

log = logging.getLogger(__name__)


def _json_response(data: dict, status: int = 200) -> func.HttpResponse:
    """Helper to return JSON with correct headers."""
    return func.HttpResponse(
        body=data,
        status_code=status,
        mimetype="application/json",
        headers={"Content-Type": "application/json"},
    )


class TodoSubtasksHandler:
    """Processes HTTP requests for To-Do subtasks."""

    def __init__(self) -> None:
        """
        Initialize the TodoSubtasksHandler with a TodoManager instance.
        """
        self.manager = TodoManager()

    @staticmethod
    def _parse_json(req: func.HttpRequest, model):
        """Parse JSON and validate against a Pydantic model."""
        try:
            payload = req.get_json()
        except ValueError as exc:
            raise ValidationError("Invalid JSON payload") from exc

        try:
            return model.model_validate(payload)
        except ValueError as exc:
            raise ValidationError(f"Validation error: {exc}") from exc

    async def create_subtask(self, req: func.HttpRequest) -> func.HttpResponse:
        """Create a new subtask."""
        try:
            data = self._parse_json(req, CreateSubtaskRequest)
            result = await self.manager.create_subtask(
                data.user_email, data.task_id, data.title
            )
            response = SubtaskResponse(**result).model_dump()
            return _json_response(response, 201)
        except TodoAPIError as e:
            return _json_response(e.to_response(), e.status_code)

    async def get_subtasks(self, req: func.HttpRequest) -> func.HttpResponse:
        """Get all subtasks for a task."""
        try:
            task_id = req.params.get("task_id")
            user_email = req.params.get("user_email")
            if not task_id or not user_email:
                raise ValidationError(
                    "Query params 'task_id' and 'user_email' are required"
                )
            subtasks = await self.manager.get_subtasks(user_email, task_id)
            response = SubtasksResponse(
                subtasks=[SubtaskResponse(**subtask) for subtask in subtasks]
            ).model_dump()
            return _json_response(response)
        except TodoAPIError as e:
            return _json_response(e.to_response(), e.status_code)

    async def edit_subtask(self, req: func.HttpRequest) -> func.HttpResponse:
        """Edit a subtask."""
        try:
            data = self._parse_json(req, EditSubtaskRequest)
            await self.manager.edit_subtask(
                data.user_email, data.subtask_id, data.new_title
            )
            return _json_response({"message": "Subtask updated"}, 200)
        except TodoAPIError as e:
            return _json_response(e.to_response(), e.status_code)

    async def delete_subtask(self, req: func.HttpRequest) -> func.HttpResponse:
        """Delete a subtask."""
        try:
            data = self._parse_json(req, DeleteSubtaskRequest)
            await self.manager.delete_subtask(data.user_email, data.subtask_id)
            return _json_response({"message": "Subtask deleted"}, 200)
        except TodoAPIError as e:
            return _json_response(e.to_response(), e.status_code)
