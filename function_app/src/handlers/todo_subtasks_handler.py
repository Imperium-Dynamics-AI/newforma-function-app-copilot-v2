# handlers/todo_subtasks_handler.py
"""
Handler for To-Do subtask operations.
"""

import azure.functions as func

from src.common.exceptions import TodoAPIError, ValidationError
from src.managers.todo_subtasks_manager import TodoSubtasksManager
from src.models.todo_subtasks import (
    CreateSubtaskRequest,
    DeleteSubtaskRequest,
    EditSubtaskRequest,
)
from src.logging.logger import get_logger
from src.utils.http_utils import json_response
from src.utils.request_utils import parse_json, get_required_query_params

logger = get_logger(__name__)


class TodoSubtasksHandler:
    """Processes HTTP requests for To-Do subtasks."""

    def __init__(self, manager: TodoSubtasksManager) -> None:
        """
        Initialize the TodoSubtasksHandler with a TodoSubtasksManager instance.

        Args:
            manager (TodoSubtasksManager): Manager for todo subtask operations.
        """
        self.manager = manager

    async def create_subtask(self, req: func.HttpRequest) -> func.HttpResponse:
        """Create a new subtask for a task."""
        try:
            data = parse_json(req, CreateSubtaskRequest)
            logger.info(
                "Creating subtask '%s' for task '%s' in list '%s' for user %s",
                data.title,
                data.task_name,
                data.list_name,
                data.user_email,
            )
            subtask_response = await self.manager.create_subtask(
                data.user_email, data.list_name, data.task_name, data.title
            )
            logger.info("Subtask created successfully: %s", subtask_response.get("subtask_id"))
            return json_response(subtask_response, 201)
        except ValidationError as e:
            logger.error("Validation error creating subtask: %s", e.detail)
            return json_response(e.to_response(), e.status_code)
        except TodoAPIError as e:
            logger.error("API error creating subtask: %s", e.detail)
            return json_response(e.to_response(), e.status_code)

    async def get_subtasks(self, req: func.HttpRequest) -> func.HttpResponse:
        """Get all subtasks for a task."""
        try:
            params = get_required_query_params(req, ["user_email", "list_name", "task_name"])
            user_email = params["user_email"]
            list_name = params["list_name"]
            task_name = params["task_name"]

            logger.info(
                "Fetching subtasks for task '%s' in list '%s' for user %s",
                task_name,
                list_name,
                user_email,
            )
            subtasks = await self.manager.get_subtasks(user_email, list_name, task_name)
            logger.info("Retrieved %d subtasks for task '%s'", len(subtasks), task_name)
            return json_response({"subtasks": subtasks}, 200)
        except ValidationError as e:
            logger.error("Validation error fetching subtasks: %s", e.detail)
            return json_response(e.to_response(), e.status_code)
        except TodoAPIError as e:
            logger.error("API error fetching subtasks: %s", e.detail)
            return json_response(e.to_response(), e.status_code)

    async def edit_subtask(self, req: func.HttpRequest) -> func.HttpResponse:
        """Edit a subtask title."""
        try:
            data = parse_json(req, EditSubtaskRequest)
            logger.info(
                "Editing subtask '%s' for task '%s' in list '%s' for user %s with new title '%s'",
                data.subtask_name,
                data.task_name,
                data.list_name,
                data.user_email,
                data.new_title,
            )
            await self.manager.edit_subtask(
                data.user_email, data.list_name, data.task_name, data.subtask_name, data.new_title
            )
            logger.info("Subtask '%s' edited successfully", data.subtask_name)
            return json_response(
                {
                    "message": "Subtask title updated successfully",
                    "subtask_name": data.subtask_name,
                },
                200,
            )
        except ValidationError as e:
            logger.error("Validation error editing subtask: %s", e.detail)
            return json_response(e.to_response(), e.status_code)
        except TodoAPIError as e:
            logger.error("API error editing subtask: %s", e.detail)
            return json_response(e.to_response(), e.status_code)

    async def delete_subtask(self, req: func.HttpRequest) -> func.HttpResponse:
        """Delete a subtask."""
        try:
            data = parse_json(req, DeleteSubtaskRequest)
            logger.info(
                "Deleting subtask '%s' for task '%s' in list '%s' for user %s",
                data.subtask_name,
                data.task_name,
                data.list_name,
                data.user_email,
            )
            await self.manager.delete_subtask(
                data.user_email, data.list_name, data.task_name, data.subtask_name
            )
            logger.info("Subtask '%s' deleted successfully", data.subtask_name)
            return json_response(
                {"message": "Subtask deleted successfully", "subtask_name": data.subtask_name}, 200
            )
        except ValidationError as e:
            logger.error("Validation error deleting subtask: %s", e.detail)
            return json_response(e.to_response(), e.status_code)
        except TodoAPIError as e:
            logger.error("API error deleting subtask: %s", e.detail)
            return json_response(e.to_response(), e.status_code)
