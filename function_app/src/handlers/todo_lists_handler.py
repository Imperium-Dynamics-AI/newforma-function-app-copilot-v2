# handlers/todo_lists_handler.py
"""
Handler for To-Do list operations.
"""

import logging

import azure.functions as func

from src.common.exceptions import TodoAPIError, ValidationError
from src.managers.todo_manager import TodoManager
from src.models.todo_lists import (
    CreateListRequest,
    DeleteListRequest,
    EditListRequest,
    ListResponse,
    ListsResponse,
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


class TodoListsHandler:
    """Processes HTTP requests for To-Do lists."""

    def __init__(self) -> None:
        """
        Initialize the TodoListsHandler with a TodoManager instance.
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

    async def create_list(self, req: func.HttpRequest) -> func.HttpResponse:
        """Create a new To-Do list."""
        try:
            data = self._parse_json(req, CreateListRequest)
            result = await self.manager.create_list(data.user_email, data.list_name)
            response = ListResponse(**result).model_dump()
            return _json_response(response, 201)
        except TodoAPIError as e:
            return _json_response(e.to_response(), e.status_code)

    async def get_lists(self, req: func.HttpRequest) -> func.HttpResponse:
        """Return all lists for a user (user_email in query string)."""
        try:
            user_email = req.params.get("user_email")
            if not user_email:
                raise ValidationError("Query parameter 'user_email' is required")
            todo_lists = await self.manager.get_lists(user_email)
            response = ListsResponse(
                lists=[ListResponse(**todo_list) for todo_list in todo_lists]
            ).model_dump()
            return _json_response(response)
        except TodoAPIError as e:
            return _json_response(e.to_response(), e.status_code)

    async def edit_list(self, req: func.HttpRequest) -> func.HttpResponse:
        """Edit an existing To-Do list."""
        try:
            data = self._parse_json(req, EditListRequest)
            await self.manager.edit_list(data.user_email, data.list_id, data.new_name)
            return _json_response({"message": "List updated"}, 200)
        except TodoAPIError as e:
            return _json_response(e.to_response(), e.status_code)

    async def delete_list(self, req: func.HttpRequest) -> func.HttpResponse:
        """Delete a To-Do list."""
        try:
            data = self._parse_json(req, DeleteListRequest)
            await self.manager.delete_list(data.user_email, data.list_id)
            return _json_response({"message": "List deleted"}, 200)
        except TodoAPIError as e:
            return _json_response(e.to_response(), e.status_code)
