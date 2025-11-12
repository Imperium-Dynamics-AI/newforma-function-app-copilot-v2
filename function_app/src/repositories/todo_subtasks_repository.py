"""
TodoSubtasksRepository - data access layer for To-Do Subtasks using Microsoft Graph API.
"""

from datetime import datetime, timezone
from typing import Any, Dict, Optional

from src.repositories.graph_client import GraphClient
from src.common.exceptions import (
    ListNotFoundError,
    TaskNotFoundError,
    SubtaskNotFoundError,
    DuplicateSubtaskError,
    EmptyFieldError,
)
from src.logging.logger import get_logger
from src.utils.repository_utils import (
    get_list_id_by_name,
    get_task_id_by_name,
    get_subtask_id_by_name,
)
from src.utils.url_builder import URLBuilder

logger = get_logger(__name__)


class TodoSubtasksRepository:
    """
    Repository class for interacting with To-Do Subtasks via Graph API.
    Handles all data access operations for subtask CRUD operations.
    """

    def __init__(self, graph_client: GraphClient) -> None:
        """
        Initialize the TodoSubtasksRepository with a GraphClient instance.
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

    async def get_subtask_id_by_name(
        self, user_email: str, list_id: str, task_id: str, subtask_name: str
    ) -> Optional[str]:
        """
        Get a subtask ID by subtask title (case-insensitive match).
        """
        return await get_subtask_id_by_name(
            self.graph_client, user_email, list_id, task_id, subtask_name
        )

    async def create_subtask(
        self, user_email: str, list_name: str, task_name: str, title: str
    ) -> Dict[str, Any]:
        """
        Create a new subtask for a task by looking up task and list by name.
        """
        if not title or not title.strip():
            logger.warning("Attempt to create subtask with empty title for task '%s'", task_name)
            raise EmptyFieldError("Subtask title")

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

        existing_subtask_id = await self.get_subtask_id_by_name(user_email, list_id, task_id, title)
        if existing_subtask_id:
            logger.warning(
                "Attempt to create duplicate subtask '%s' for task '%s'", title, task_name
            )
            raise DuplicateSubtaskError(title)

        endpoint = URLBuilder.todo_subtasks(user_email, list_id, task_id)
        payload = {"displayName": title.strip()}

        try:
            resp = await self.graph_client.request("POST", endpoint, json_body=payload)
            logger.info(
                "Successfully created subtask '%s' for task '%s' in list '%s' for user %s",
                title.strip(),
                task_name,
                list_name,
                user_email,
            )
            created_at = resp.get("createdDateTime")
            if not created_at:
                created_at = datetime.now(timezone.utc).isoformat()

            return {
                "subtask_id": resp.get("id"),
                "task_id": task_id,
                "title": resp.get("displayName"),
                "completed": resp.get("isChecked", False),
                "created_at": created_at,
            }
        except (ListNotFoundError, TaskNotFoundError, DuplicateSubtaskError):
            raise
        except Exception as e:
            logger.error(
                "Failed to create subtask '%s' for task '%s': %s",
                title,
                task_name,
                str(e),
                exc_info=True,
            )
            raise

    async def get_subtasks(self, user_email: str, list_name: str, task_name: str) -> Dict[str, Any]:
        """
        Get all subtasks for a task by looking up task and list by name.
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

        endpoint = URLBuilder.todo_subtasks(user_email, list_id, task_id)
        try:
            resp = await self.graph_client.request("GET", endpoint)
            logger.info("Successfully retrieved subtasks for task '%s'", task_name)
            subtasks_data = resp.get("value", [])
            subtasks = [
                {
                    "subtask_id": subtask.get("id"),
                    "task_id": task_id,
                    "title": subtask.get("displayName"),
                    "completed": subtask.get("isChecked", False),
                    "created_at": subtask.get("createdDateTime"),
                }
                for subtask in subtasks_data
            ]
            return {"subtasks": subtasks}
        except (ListNotFoundError, TaskNotFoundError):
            raise
        except Exception as e:
            logger.error(
                "Failed to retrieve subtasks for task '%s': %s", task_name, str(e), exc_info=True
            )
            raise

    async def edit_subtask(
        self, user_email: str, list_name: str, task_name: str, subtask_name: str, new_title: str
    ) -> None:
        """
        Edit a subtask title by looking up subtask, task, and list by name..
        """
        if not new_title or not new_title.strip():
            logger.warning("Attempt to edit subtask '%s' with empty title", subtask_name)
            raise EmptyFieldError("Subtask title")

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

        # Get subtask ID by name
        subtask_id = await self.get_subtask_id_by_name(user_email, list_id, task_id, subtask_name)
        if not subtask_id:
            logger.warning("Subtask '%s' not found for task '%s'", subtask_name, task_name)
            raise SubtaskNotFoundError(subtask_name)

        # Check if new title already exists
        existing_subtask_id = await self.get_subtask_id_by_name(
            user_email, list_id, task_id, new_title
        )
        if existing_subtask_id and existing_subtask_id != subtask_id:
            logger.warning("Attempt to rename subtask to existing title '%s'", new_title)
            raise DuplicateSubtaskError(new_title)

        endpoint = URLBuilder.todo_subtask(user_email, list_id, task_id, subtask_id)
        payload = {"displayName": new_title.strip()}

        try:
            await self.graph_client.request("PATCH", endpoint, json_body=payload)
            logger.info(
                "Successfully edited subtask '%s' for task '%s' with new title '%s'",
                subtask_name,
                task_name,
                new_title.strip(),
            )
        except (ListNotFoundError, TaskNotFoundError, SubtaskNotFoundError, DuplicateSubtaskError):
            raise
        except Exception as e:
            logger.error("Failed to edit subtask '%s': %s", subtask_name, str(e), exc_info=True)
            raise

    async def delete_subtask(
        self, user_email: str, list_name: str, task_name: str, subtask_name: str
    ) -> None:
        """
        Delete a subtask by looking up subtask, task, and list by name.
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

        # Get subtask ID by name
        subtask_id = await self.get_subtask_id_by_name(user_email, list_id, task_id, subtask_name)
        if not subtask_id:
            logger.warning("Subtask '%s' not found for task '%s'", subtask_name, task_name)
            raise SubtaskNotFoundError(subtask_name)

        endpoint = URLBuilder.todo_subtask(user_email, list_id, task_id, subtask_id)
        try:
            await self.graph_client.request("DELETE", endpoint)
            logger.info("Successfully deleted subtask '%s' from task '%s'", subtask_name, task_name)
        except (ListNotFoundError, TaskNotFoundError, SubtaskNotFoundError):
            raise
        except Exception as e:
            logger.error("Failed to delete subtask '%s': %s", subtask_name, str(e), exc_info=True)
            raise
