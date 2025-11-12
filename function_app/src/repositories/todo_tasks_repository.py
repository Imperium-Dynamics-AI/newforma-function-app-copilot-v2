"""
TodoTasksRepository - data access layer for To-Do Tasks using Microsoft Graph API.
"""

from datetime import datetime, timezone
from typing import Any, Dict, Optional

from src.repositories.graph_client import GraphClient
from src.common.exceptions import (
    ListNotFoundError,
    TaskNotFoundError,
    DuplicateTaskError,
    InvalidStatusError,
    EmptyFieldError,
)
from src.logging.logger import get_logger
from src.utils.repository_utils import get_list_id_by_name, get_task_id_by_name
from src.utils.url_builder import URLBuilder

logger = get_logger(__name__)


class TodoTasksRepository:
    """
    Repository class for interacting with To-Do Tasks via Graph API.
    Handles all data access operations for task CRUD operations.
    """

    def __init__(self, graph_client: GraphClient) -> None:
        """
        Initialize the TodoTasksRepository with a GraphClient instance.
        """
        self.graph_client = graph_client

    async def get_list_id_by_name(self, user_email: str, list_name: str) -> Optional[str]:
        """
        Get a To-Do list ID by list name (case-insensitive match).
        """
        return await get_list_id_by_name(self.graph_client, user_email, list_name)

    async def get_task_id_by_name(
        self, user_email: str, list_id: str, task_name: str
    ) -> Optional[str]:
        """
        Get a task ID by task title (case-insensitive match).
        """
        return await get_task_id_by_name(self.graph_client, user_email, list_id, task_name)

    async def create_task(
        self,
        user_email: str,
        list_name: str,
        title: str,
        description: Optional[str] = None,
        due_date: Optional[str] = None,
        time_zone: str = "UTC",
    ) -> Dict[str, Any]:
        """
        Create a new task in a To-Do list by list name.

        Args:
            time_zone (str): The timezone for the due date (default: "UTC").
        """
        if not title or not title.strip():
            logger.warning("Attempt to create task with empty title in list '%s'", list_name)
            raise ValueError("Task title cannot be empty")

        list_id = await self.get_list_id_by_name(user_email, list_name)
        if not list_id:
            logger.warning("List '%s' not found for user %s", list_name, user_email)
            raise ListNotFoundError(list_name)

        # Check if task already exists
        existing_task_id = await self.get_task_id_by_name(user_email, list_id, title)
        if existing_task_id:
            logger.warning("Attempt to create duplicate task '%s' in list '%s'", title, list_name)
            raise DuplicateTaskError(title)

        endpoint = URLBuilder.todo_tasks_by_list(user_email, list_id)
        payload = {"title": title.strip()}
        if description:
            payload["body"] = {"content": description, "contentType": "text"}
        if due_date:
            payload["dueDateTime"] = {"dateTime": due_date, "timeZone": time_zone}

        try:
            resp = await self.graph_client.request("POST", endpoint, json_body=payload)
            logger.info(
                "Successfully created task '%s' in list '%s' with timezone %s for user %s",
                title.strip(),
                list_name,
                time_zone,
                user_email,
            )
            created_at = resp.get("createdDateTime")
            if not created_at:
                created_at = datetime.now(timezone.utc).isoformat()

            return {
                "task_id": resp.get("id"),
                "list_id": list_id,
                "title": resp.get("title"),
                "description": resp.get("body", {}).get("content"),
                "status": resp.get("status", "notStarted"),
                "due_date": resp.get("dueDateTime", {}).get("dateTime"),
                "created_at": created_at,
            }
        except (ListNotFoundError, DuplicateTaskError):
            raise
        except Exception as e:
            logger.error(
                "Failed to create task '%s' in list '%s': %s",
                title,
                list_name,
                str(e),
                exc_info=True,
            )
            raise

    async def get_tasks(self, user_email: str, list_name: str) -> Dict[str, Any]:
        """
        Get all tasks in a To-Do list by list name.
        """

        list_id = await self.get_list_id_by_name(user_email, list_name)
        if not list_id:
            logger.warning("List '%s' not found for user %s", list_name, user_email)
            raise ListNotFoundError(list_name)

        endpoint = URLBuilder.todo_tasks_by_list(user_email, list_id)
        try:
            resp = await self.graph_client.request("GET", endpoint)
            logger.info("Successfully retrieved tasks for list '%s'", list_name)
            tasks_data = resp.get("value", [])
            tasks = [
                {
                    "task_id": task.get("id"),
                    "list_id": list_id,
                    "title": task.get("title"),
                    "description": task.get("body", {}).get("content"),
                    "status": task.get("status", "notStarted"),
                    "due_date": task.get("dueDateTime", {}).get("dateTime"),
                    "created_at": task.get("createdDateTime"),
                }
                for task in tasks_data
            ]
            return {"tasks": tasks}
        except ListNotFoundError:
            raise
        except Exception as e:
            logger.error(
                "Failed to retrieve tasks for list '%s': %s", list_name, str(e), exc_info=True
            )
            raise

    async def edit_task(
        self, user_email: str, list_name: str, task_name: str, new_title: str
    ) -> None:
        """
        Edit a task title by looking up task and list by name.
        """
        if not new_title or not new_title.strip():
            logger.warning("Attempt to edit task '%s' with empty title", task_name)
            raise EmptyFieldError("Task title")

        list_id = await self.get_list_id_by_name(user_email, list_name)
        if not list_id:
            logger.warning("List '%s' not found for user %s", list_name, user_email)
            raise ListNotFoundError(list_name)

        task_id = await self.get_task_id_by_name(user_email, list_id, task_name)
        if not task_id:
            logger.warning(
                "Task '%s' not found in list '%s' for user %s", task_name, list_name, user_email
            )
            raise TaskNotFoundError(task_name)

        # Check if new title already exists
        existing_task_id = await self.get_task_id_by_name(user_email, list_id, new_title)
        if existing_task_id and existing_task_id != task_id:
            logger.warning("Attempt to rename task to existing title '%s'", new_title)
            raise DuplicateTaskError(new_title)

        endpoint = URLBuilder.todo_task(user_email, task_id)
        payload = {"title": new_title.strip()}

        try:
            await self.graph_client.request("PATCH", endpoint, json_body=payload)
            logger.info(
                "Successfully edited task '%s' in list '%s' with new title '%s'",
                task_name,
                list_name,
                new_title.strip(),
            )
        except (ListNotFoundError, TaskNotFoundError, DuplicateTaskError):
            raise
        except Exception as e:
            logger.error("Failed to edit task '%s': %s", task_name, str(e), exc_info=True)
            raise

    async def update_task_status(
        self, user_email: str, list_name: str, task_name: str, status: str
    ) -> None:
        """
        Update a task's status by looking up task and list by name.
        """
        valid_statuses = ["notStarted", "inProgress", "completed", "waitingOnOthers"]
        if status not in valid_statuses:
            logger.warning("Attempt to update task with invalid status: %s", status)
            raise InvalidStatusError(status, valid_statuses)

        list_id = await self.get_list_id_by_name(user_email, list_name)
        if not list_id:
            logger.warning("List '%s' not found for user %s", list_name, user_email)
            raise ListNotFoundError(list_name)

        task_id = await self.get_task_id_by_name(user_email, list_id, task_name)
        if not task_id:
            logger.warning(
                "Task '%s' not found in list '%s' for user %s", task_name, list_name, user_email
            )
            raise TaskNotFoundError(task_name)

        endpoint = URLBuilder.todo_task(user_email, task_id)
        payload = {"status": status}

        try:
            await self.graph_client.request("PATCH", endpoint, json_body=payload)
            logger.info("Successfully updated task '%s' status to '%s'", task_name, status)
        except ListNotFoundError:
            raise
        except Exception as e:
            logger.error("Failed to update task '%s' status: %s", task_name, str(e), exc_info=True)
            raise

    async def update_task_description(
        self, user_email: str, list_name: str, task_name: str, description: str
    ) -> None:
        """
        Update a task's description by looking up task and list by name.
        """

        list_id = await self.get_list_id_by_name(user_email, list_name)
        if not list_id:
            logger.warning("List '%s' not found for user %s", list_name, user_email)
            raise ListNotFoundError(list_name)

        task_id = await self.get_task_id_by_name(user_email, list_id, task_name)
        if not task_id:
            logger.warning(
                "Task '%s' not found in list '%s' for user %s", task_name, list_name, user_email
            )
            raise TaskNotFoundError(task_name)

        endpoint = URLBuilder.todo_task(user_email, task_id)
        payload = {"body": {"content": description, "contentType": "text"}}

        try:
            await self.graph_client.request("PATCH", endpoint, json_body=payload)
            logger.info("Successfully updated task '%s' description", task_name)
        except ListNotFoundError:
            raise
        except Exception as e:
            logger.error(
                "Failed to update task '%s' description: %s", task_name, str(e), exc_info=True
            )
            raise

    async def update_task_duedate(
        self, user_email: str, list_name: str, task_name: str, due_date: str, time_zone: str = "UTC"
    ) -> None:
        """
        Update a task's due date by looking up task and list by name.

        Args:
            time_zone (str): The timezone for the due date (default: "UTC").
        """

        list_id = await self.get_list_id_by_name(user_email, list_name)
        if not list_id:
            logger.warning("List '%s' not found for user %s", list_name, user_email)
            raise ListNotFoundError(list_name)

        task_id = await self.get_task_id_by_name(user_email, list_id, task_name)
        if not task_id:
            logger.warning(
                "Task '%s' not found in list '%s' for user %s", task_name, list_name, user_email
            )
            raise TaskNotFoundError(task_name)

        endpoint = URLBuilder.todo_task(user_email, task_id)
        payload = {"dueDateTime": {"dateTime": due_date, "timeZone": time_zone}}

        try:
            await self.graph_client.request("PATCH", endpoint, json_body=payload)
            logger.info(
                "Successfully updated task '%s' due date with timezone %s",
                task_name,
                time_zone,
            )
        except ListNotFoundError:
            raise
        except Exception as e:
            logger.error(
                "Failed to update task '%s' due date: %s", task_name, str(e), exc_info=True
            )
            raise

    async def delete_task(self, user_email: str, list_name: str, task_name: str) -> None:
        """
        Delete a task by looking up task and list by name.
        """

        list_id = await self.get_list_id_by_name(user_email, list_name)
        if not list_id:
            logger.warning("List '%s' not found for user %s", list_name, user_email)
            raise ListNotFoundError(list_name)

        task_id = await self.get_task_id_by_name(user_email, list_id, task_name)
        if not task_id:
            logger.warning(
                "Task '%s' not found in list '%s' for user %s", task_name, list_name, user_email
            )
            raise TaskNotFoundError(task_name)

        endpoint = URLBuilder.todo_task(user_email, task_id)
        try:
            await self.graph_client.request("DELETE", endpoint)
            logger.info("Successfully deleted task '%s' from list '%s'", task_name, list_name)
        except ListNotFoundError:
            raise
        except Exception as e:
            logger.error("Failed to delete task '%s': %s", task_name, str(e), exc_info=True)
            raise
