# handlers/todo_tasks_handler.py
"""
Handler for To-Do task operations.
"""

import azure.functions as func

from src.common.exceptions import TodoAPIError, ValidationError
from src.managers.todo_tasks_manager import TodoTasksManager
from src.models.todo_tasks import (
    CreateTaskRequest,
    DeleteTaskRequest,
    EditTaskRequest,
    UpdateTaskStatusRequest,
    UpdateTaskDescriptionRequest,
    UpdateTaskDueDateRequest,
)
from src.logging.logger import get_logger
from src.utils.http_utils import json_response
from src.utils.request_utils import parse_json, get_required_query_params

logger = get_logger(__name__)


class TodoTasksHandler:
    """Processes HTTP requests for To-Do tasks."""

    def __init__(self, manager: TodoTasksManager) -> None:
        """
        Initialize the TodoTasksHandler with a TodoTasksManager instance.

        Args:
            manager (TodoTasksManager): Manager for todo task operations.
        """
        self.manager = manager

    async def create_task(self, req: func.HttpRequest) -> func.HttpResponse:
        """Create a new To-Do task."""
        try:
            data = parse_json(req, CreateTaskRequest)
            due_date = ""
            if data.due_date:
                if isinstance(data.due_date, str):
                    due_date = data.due_date
                else:
                    due_date = data.due_date.isoformat()
                if len(due_date) == 10:
                    due_date = f"{due_date}T23:59:59"

            logger.info(
                "Creating task '%s' in list '%s' for user %s with timezone %s",
                data.title,
                data.list_name,
                data.user_email,
                data.time_zone,
            )
            task_response = await self.manager.create_task(
                data.user_email,
                data.list_name,
                data.title,
                data.description,
                due_date,
                data.time_zone,
            )
            logger.info("Task created successfully: %s", task_response.get("task_id"))
            return json_response(task_response, 201)
        except ValidationError as e:
            logger.error("Validation error creating task: %s", e.detail)
            return json_response(e.to_response(), e.status_code)
        except TodoAPIError as e:
            logger.error("API error creating task: %s", e.detail)
            return json_response(e.to_response(), e.status_code)

    async def get_tasks(self, req: func.HttpRequest) -> func.HttpResponse:
        """Get all tasks in a list (list_name and user_email in query string)."""
        try:
            params = get_required_query_params(req, ["user_email", "list_name"])
            user_email = params["user_email"]
            list_name = params["list_name"]

            logger.info("Retrieving tasks from list '%s' for user %s", list_name, user_email)
            tasks = await self.manager.get_tasks(user_email, list_name)
            logger.info("Retrieved %d tasks from list '%s'", len(tasks), list_name)
            return json_response({"tasks": tasks}, 200)
        except ValidationError as e:
            logger.error("Validation error retrieving tasks: %s", e.detail)
            return json_response(e.to_response(), e.status_code)
        except TodoAPIError as e:
            logger.error("API error retrieving tasks: %s", e.detail)
            return json_response(e.to_response(), e.status_code)

    async def edit_task(self, req: func.HttpRequest) -> func.HttpResponse:
        """Edit a task title."""
        try:
            data = parse_json(req, EditTaskRequest)
            logger.info(
                "Editing task '%s' in list '%s' to title '%s' for user %s",
                data.task_name,
                data.list_name,
                data.new_title,
                data.user_email,
            )
            await self.manager.edit_task(
                data.user_email, data.list_name, data.task_name, data.new_title
            )
            logger.info("Task '%s' edited successfully", data.task_name)
            return json_response(
                {"message": "Task updated successfully", "task_name": data.task_name}, 200
            )
        except ValidationError as e:
            logger.error("Validation error editing task: %s", e.detail)
            return json_response(e.to_response(), e.status_code)
        except TodoAPIError as e:
            logger.error("API error editing task: %s", e.detail)
            return json_response(e.to_response(), e.status_code)

    async def update_task_status(self, req: func.HttpRequest) -> func.HttpResponse:
        """Update task status."""
        try:
            data = parse_json(req, UpdateTaskStatusRequest)
            logger.info(
                "Updating task '%s' in list '%s' status to %s for user %s",
                data.task_name,
                data.list_name,
                data.status,
                data.user_email,
            )
            await self.manager.update_task_status(
                data.user_email, data.list_name, data.task_name, data.status
            )
            logger.info("Task '%s' status updated successfully", data.task_name)
            return json_response(
                {"message": "Task status updated successfully", "task_name": data.task_name}, 200
            )
        except ValidationError as e:
            logger.error("Validation error updating task status: %s", e.detail)
            return json_response(e.to_response(), e.status_code)
        except TodoAPIError as e:
            logger.error("API error updating task status: %s", e.detail)
            return json_response(e.to_response(), e.status_code)

    async def update_task_description(self, req: func.HttpRequest) -> func.HttpResponse:
        """Update task description."""
        try:
            data = parse_json(req, UpdateTaskDescriptionRequest)
            logger.info(
                "Updating task '%s' in list '%s' description for user %s",
                data.task_name,
                data.list_name,
                data.user_email,
            )
            await self.manager.update_task_description(
                data.user_email, data.list_name, data.task_name, data.description or ""
            )
            logger.info("Task '%s' description updated successfully", data.task_name)
            return json_response(
                {"message": "Task description updated successfully", "task_name": data.task_name},
                200,
            )
        except ValidationError as e:
            logger.error("Validation error updating task description: %s", e.detail)
            return json_response(e.to_response(), e.status_code)
        except TodoAPIError as e:
            logger.error("API error updating task description: %s", e.detail)
            return json_response(e.to_response(), e.status_code)

    async def update_task_duedate(self, req: func.HttpRequest) -> func.HttpResponse:
        """Update task due date."""
        try:
            data = parse_json(req, UpdateTaskDueDateRequest)
            due_date = ""
            if data.due_date:
                if isinstance(data.due_date, str):
                    due_date = data.due_date
                else:
                    due_date = data.due_date.isoformat()
                if len(due_date) == 10:
                    due_date = f"{due_date}T23:59:59"

            logger.info(
                "Updating task '%s' in list '%s' due date with timezone %s for user %s",
                data.task_name,
                data.list_name,
                data.time_zone,
                data.user_email,
            )
            await self.manager.update_task_duedate(
                data.user_email,
                data.list_name,
                data.task_name,
                due_date,
                data.time_zone,
            )
            logger.info("Task '%s' due date updated successfully", data.task_name)
            return json_response(
                {"message": "Task due date updated successfully", "task_name": data.task_name}, 200
            )
        except ValidationError as e:
            logger.error("Validation error updating task due date: %s", e.detail)
            return json_response(e.to_response(), e.status_code)
        except TodoAPIError as e:
            logger.error("API error updating task due date: %s", e.detail)
            return json_response(e.to_response(), e.status_code)

    async def delete_task(self, req: func.HttpRequest) -> func.HttpResponse:
        """Delete a task."""
        try:
            data = parse_json(req, DeleteTaskRequest)
            logger.info(
                "Deleting task '%s' from list '%s' for user %s",
                data.task_name,
                data.list_name,
                data.user_email,
            )
            await self.manager.delete_task(data.user_email, data.list_name, data.task_name)
            logger.info("Task '%s' deleted successfully", data.task_name)
            return json_response(
                {"message": "Task deleted successfully", "task_name": data.task_name}, 200
            )
        except ValidationError as e:
            logger.error("Validation error deleting task: %s", e.detail)
            return json_response(e.to_response(), e.status_code)
        except TodoAPIError as e:
            logger.error("API error deleting task: %s", e.detail)
            return json_response(e.to_response(), e.status_code)
