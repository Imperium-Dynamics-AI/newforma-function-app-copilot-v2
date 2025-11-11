# handlers/todo_tasks_handler.py
"""
Handler for To-Do task operations.
"""

import logging

import azure.functions as func

from src.common.exceptions import TodoAPIError, ValidationError
from src.managers.todo_manager import TodoManager
from src.models.todo_tasks import (
    CreateTaskRequest,
    DeleteTaskRequest,
    EditTaskRequest,
    TaskResponse,
    TasksResponse,
    UpdateTaskDescriptionRequest,
    UpdateTaskDueDateRequest,
    UpdateTaskStatusRequest,
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


class TodoTasksHandler:
    """Processes HTTP requests for To-Do tasks."""

    def __init__(self, manager: TodoManager) -> None:
        """
        Initialize the TodoTasksHandler with a TodoManager instance.
        """
        self.manager = manager

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

    async def create_task(self, req: func.HttpRequest) -> func.HttpResponse:
        """Create a new task."""
        try:
            data = self._parse_json(req, CreateTaskRequest)
            result = await self.manager.create_task(
                data.user_email,
                data.list_id,
                data.title,
                data.description,
                data.due_date,
            )
            response = TaskResponse(**result).model_dump()
            return _json_response(response, 201)
        except TodoAPIError as e:
            return _json_response(e.to_response(), e.status_code)

    async def get_tasks(self, req: func.HttpRequest) -> func.HttpResponse:
        """Get all tasks for a list."""
        try:
            list_id = req.params.get("list_id")
            user_email = req.params.get("user_email")
            if not list_id or not user_email:
                raise ValidationError(
                    "Query params 'list_id' and 'user_email' are required"
                )
            tasks = await self.manager.get_tasks(user_email, list_id)
            response = TasksResponse(
                tasks=[TaskResponse(**task) for task in tasks]
            ).model_dump()
            return _json_response(response)
        except TodoAPIError as e:
            return _json_response(e.to_response(), e.status_code)

    async def edit_task(self, req: func.HttpRequest) -> func.HttpResponse:
        """Edit a task title."""
        try:
            data = self._parse_json(req, EditTaskRequest)
            await self.manager.edit_task(data.user_email, data.task_id, data.new_title)
            return _json_response({"message": "Task title updated"}, 200)
        except TodoAPIError as e:
            return _json_response(e.to_response(), e.status_code)

    async def update_status(self, req: func.HttpRequest) -> func.HttpResponse:
        """Update task status."""
        try:
            data = self._parse_json(req, UpdateTaskStatusRequest)
            await self.manager.update_task_status(
                data.user_email, data.task_id, data.status
            )
            return _json_response({"message": "Task status updated"}, 200)
        except TodoAPIError as e:
            return _json_response(e.to_response(), e.status_code)

    async def update_description(self, req: func.HttpRequest) -> func.HttpResponse:
        """Update task description."""
        try:
            data = self._parse_json(req, UpdateTaskDescriptionRequest)
            await self.manager.update_task_description(
                data.user_email, data.task_id, data.description
            )
            return _json_response({"message": "Task description updated"}, 200)
        except TodoAPIError as e:
            return _json_response(e.to_response(), e.status_code)

    async def update_duedate(self, req: func.HttpRequest) -> func.HttpResponse:
        """Update task due date."""
        try:
            data = self._parse_json(req, UpdateTaskDueDateRequest)
            await self.manager.update_task_duedate(
                data.user_email, data.task_id, data.due_date
            )
            return _json_response({"message": "Task due date updated"}, 200)
        except TodoAPIError as e:
            return _json_response(e.to_response(), e.status_code)

    async def delete_task(self, req: func.HttpRequest) -> func.HttpResponse:
        """Delete a task."""
        try:
            data = self._parse_json(req, DeleteTaskRequest)
            await self.manager.delete_task(data.user_email, data.task_id)
            return _json_response({"message": "Task deleted"}, 200)
        except TodoAPIError as e:
            return _json_response(e.to_response(), e.status_code)
