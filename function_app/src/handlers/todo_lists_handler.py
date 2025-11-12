# handlers/todo_lists_handler.py
"""
Handler for To-Do list operations.
"""

import azure.functions as func

from src.common.exceptions import TodoAPIError, ValidationError
from src.managers.todo_lists_manager import TodoListsManager
from src.models.todo_lists import (
    CreateListRequest,
    DeleteListRequest,
    EditListRequest,
)
from src.logging.logger import get_logger
from src.utils.http_utils import json_response
from src.utils.request_utils import parse_json, get_required_query_param

logger = get_logger(__name__)


class TodoListsHandler:
    """Processes HTTP requests for To-Do lists."""

    def __init__(self, manager: TodoListsManager) -> None:
        """
        Initialize the TodoListsHandler with a TodoListsManager instance.

        Args:
            manager (TodoListsManager): Manager for todo list operations.
        """
        self.manager = manager

    async def create_list(self, req: func.HttpRequest) -> func.HttpResponse:
        """Create a new To-Do list."""
        try:
            data = parse_json(req, CreateListRequest)
            logger.info("Creating list '%s' for user %s", data.list_name, data.user_email)
            create_list_response = await self.manager.create_list(data.user_email, data.list_name)
            logger.info("List created successfully: %s", create_list_response.list_id)
            return json_response(create_list_response.model_dump(mode="json"), 201)
        except ValidationError as e:
            logger.error("Validation error creating list: %s", e.detail)
            return json_response(e.to_response(), e.status_code)
        except TodoAPIError as e:
            logger.error("API error creating list: %s", e.detail)
            return json_response(e.to_response(), e.status_code)

    async def get_lists(self, req: func.HttpRequest) -> func.HttpResponse:
        """Return all lists for a user (user_email in query string)."""
        try:
            user_email = get_required_query_param(req, "user_email")
            logger.info("Retrieving lists for user %s", user_email)
            response = await self.manager.get_lists(user_email)
            logger.info("Retrieved %d lists for user %s", len(response.lists), user_email)
            return json_response(response.model_dump(mode="json"), 200)
        except ValidationError as e:
            logger.error("Validation error retrieving lists: %s", e.detail)
            return json_response(e.to_response(), e.status_code)
        except TodoAPIError as e:
            logger.error("API error retrieving lists: %s", e.detail)
            return json_response(e.to_response(), e.status_code)

    async def edit_list(self, req: func.HttpRequest) -> func.HttpResponse:
        """Edit an existing To-Do list."""
        try:
            data = parse_json(req, EditListRequest)
            logger.info(
                "Editing list '%s' to name '%s' for user %s",
                data.list_name,
                data.new_name,
                data.user_email,
            )
            await self.manager.edit_list(data.user_email, data.list_name, data.new_name)
            logger.info("List '%s' edited successfully", data.list_name)
            return json_response(
                {
                    "message": "List updated successfully",
                    "old_list_name": data.list_name,
                    "new_list_name": data.new_name,
                },
                200,
            )
        except ValidationError as e:
            logger.error("Validation error editing list: %s", e.detail)
            return json_response(e.to_response(), e.status_code)
        except TodoAPIError as e:
            logger.error("API error editing list: %s", e.detail)
            return json_response(e.to_response(), e.status_code)

    async def delete_list(self, req: func.HttpRequest) -> func.HttpResponse:
        """Delete a To-Do list."""
        try:
            data = parse_json(req, DeleteListRequest)
            logger.info("Deleting list '%s' for user %s", data.list_name, data.user_email)
            await self.manager.delete_list(data.user_email, data.list_name)
            logger.info("List '%s' deleted successfully", data.list_name)
            return json_response(
                {"message": "List deleted successfully", "list_name": data.list_name}, 200
            )
        except ValidationError as e:
            logger.error("Validation error deleting list: %s", e.detail)
            return json_response(e.to_response(), e.status_code)
        except TodoAPIError as e:
            logger.error("API error deleting list: %s", e.detail)
            return json_response(e.to_response(), e.status_code)
