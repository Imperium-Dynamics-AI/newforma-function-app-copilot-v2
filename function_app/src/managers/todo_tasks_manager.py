"""
TodoTasksManager - business logic layer for To-Do Tasks.
Delegates data operations to TodoTasksRepository and handles errors by raising custom exceptions.
"""

from typing import Any, Dict, List, Optional

from src.common.exceptions import (
    TodoAPIError,
    ValidationError,
    ListNotFoundError,
    TaskNotFoundError,
    DuplicateTaskError,
    InvalidStatusError,
)
from src.repositories.todo_tasks_repository import TodoTasksRepository
from src.logging.logger import get_logger
from src.utils.manager_utils import validate_non_empty_string

logger = get_logger(__name__)


class TodoTasksManager:
    """
    Manager class for handling To-Do Tasks business logic.
    Provides high-level operations for task management with validation and error handling.
    """

    def __init__(self, repository: TodoTasksRepository) -> None:
        """
        Initialize the TodoTasksManager with a TodoTasksRepository instance.

        Args:
            repository (TodoTasksRepository): The repository for task data access operations.
        """
        self.repo = repository

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
        Create a new task in a To-Do list.

        Args:
            user_email (str): The user's email.
            list_name (str): The name of the list.
            title (str): The task title.
            description (Optional[str]): The task description.
            due_date (Optional[str]): The task due date.
            time_zone (str): The timezone for the due date (default: "UTC").

        Returns:
            Dict[str, Any]: Dictionary representing the created task.

        Raises:
            ValidationError: If title is empty.
            ListNotFoundError: If the list is not found.
            DuplicateTaskError: If a task with the same title already exists.
            TodoAPIError: If an error occurs during creation.
        """
        try:
            validated_title = validate_non_empty_string(title, "Task title")
            result = await self.repo.create_task(
                user_email, list_name, validated_title, description, due_date, time_zone
            )
            logger.info("Task created successfully: %s", result.get("task_id"))
            return result
        except (ValidationError, ListNotFoundError, DuplicateTaskError):
            raise
        except Exception as e:
            logger.error("Error creating task '%s': %s", title, str(e), exc_info=True)
            raise TodoAPIError(detail=str(e)) from e

    async def get_tasks(self, user_email: str, list_name: str) -> List[Dict[str, Any]]:
        """
        Get all tasks in a To-Do list.

        Args:
            user_email (str): The user's email.
            list_name (str): The name of the list.

        Returns:
            List[Dict[str, Any]]: List of task dictionaries.

        Raises:
            ListNotFoundError: If the list is not found.
            TodoAPIError: If an error occurs during retrieval.
        """
        try:
            logger.info("Fetching tasks for list '%s' for user %s", list_name, user_email)
            result = await self.repo.get_tasks(user_email, list_name)
            tasks = result.get("tasks", [])
            logger.info("Retrieved %d tasks for list '%s'", len(tasks), list_name)
            return tasks
        except ListNotFoundError:
            raise
        except Exception as e:
            logger.error("Error fetching tasks for list '%s': %s", list_name, str(e), exc_info=True)
            raise TodoAPIError(detail=str(e)) from e

    async def edit_task(
        self, user_email: str, list_name: str, task_name: str, new_title: str
    ) -> None:
        """
        Edit a task title.

        Args:
            user_email (str): The user's email.
            list_name (str): The name of the list.
            task_name (str): The current task title.
            new_title (str): The new task title.

        Raises:
            ValidationError: If new_title is empty.
            ListNotFoundError: If the list is not found.
            TaskNotFoundError: If the task is not found.
            DuplicateTaskError: If a task with new_title already exists.
            TodoAPIError: If an error occurs during edit.
        """
        try:
            validated_title = validate_non_empty_string(new_title, "Task title")
            logger.info(
                "Editing task '%s' in list '%s' with new title '%s'",
                task_name,
                list_name,
                validated_title,
            )
            await self.repo.edit_task(user_email, list_name, task_name, validated_title)
            logger.info("Task '%s' edited successfully", task_name)
        except (ValidationError, ListNotFoundError, TaskNotFoundError, DuplicateTaskError):
            raise
        except Exception as e:
            logger.error("Error editing task '%s': %s", task_name, str(e), exc_info=True)
            raise TodoAPIError(detail=str(e)) from e

    async def update_task_status(
        self, user_email: str, list_name: str, task_name: str, status: str
    ) -> None:
        """
        Update a task's status.

        Args:
            user_email (str): The user's email.
            list_name (str): The name of the list.
            task_name (str): The task title.
            status (str): The new status.

        Raises:
            ValidationError: If status is invalid.
            ListNotFoundError: If the list is not found.
            TaskNotFoundError: If the task is not found.
            InvalidStatusError: If the status is invalid.
            TodoAPIError: If an error occurs during update.
        """
        try:
            valid_statuses = ["notStarted", "inProgress", "completed", "waitingOnOthers"]
            if status not in valid_statuses:
                logger.warning(
                    "Attempt to update task '%s' with invalid status: %s", task_name, status
                )
                raise ValidationError(detail=f"Invalid status. Must be one of {valid_statuses}")

            logger.info("Updating task '%s' status to '%s'", task_name, status)
            await self.repo.update_task_status(user_email, list_name, task_name, status)
            logger.info("Task '%s' status updated successfully", task_name)
        except (ValidationError, ListNotFoundError, TaskNotFoundError, InvalidStatusError):
            raise
        except Exception as e:
            logger.error("Error updating task '%s' status: %s", task_name, str(e), exc_info=True)
            raise TodoAPIError(detail=str(e)) from e

    async def update_task_description(
        self, user_email: str, list_name: str, task_name: str, description: str
    ) -> None:
        """
        Update a task's description.

        Args:
            user_email (str): The user's email.
            list_name (str): The name of the list.
            task_name (str): The task title.
            description (str): The new description.

        Raises:
            ListNotFoundError: If the list is not found.
            TaskNotFoundError: If the task is not found.
            TodoAPIError: If an error occurs during update.
        """
        try:
            logger.info("Updating task '%s' description", task_name)
            await self.repo.update_task_description(user_email, list_name, task_name, description)
            logger.info("Task '%s' description updated successfully", task_name)
        except (ListNotFoundError, TaskNotFoundError):
            raise
        except Exception as e:
            logger.error(
                "Error updating task '%s' description: %s", task_name, str(e), exc_info=True
            )
            raise TodoAPIError(detail=str(e)) from e

    async def update_task_duedate(
        self,
        user_email: str,
        list_name: str,
        task_name: str,
        due_date: str,
        time_zone: str = "UTC",
    ) -> None:
        """
        Update a task's due date.

        Args:
            user_email (str): The user's email.
            list_name (str): The name of the list.
            task_name (str): The task title.
            due_date (str): The new due date.
            time_zone (str): The timezone for the due date (default: "UTC").

        Raises:
            ListNotFoundError: If the list is not found.
            TaskNotFoundError: If the task is not found.
            TodoAPIError: If an error occurs during update.
        """
        try:
            logger.info("Updating task '%s' due date with timezone %s", task_name, time_zone)
            await self.repo.update_task_duedate(
                user_email, list_name, task_name, due_date, time_zone
            )
            logger.info("Task '%s' due date updated successfully", task_name)
        except (ListNotFoundError, TaskNotFoundError):
            raise
        except Exception as e:
            logger.error("Error updating task '%s' due date: %s", task_name, str(e), exc_info=True)
            raise TodoAPIError(detail=str(e)) from e

    async def delete_task(self, user_email: str, list_name: str, task_name: str) -> None:
        """
        Delete a task.

        Args:
            user_email (str): The user's email.
            list_name (str): The name of the list.
            task_name (str): The task title to delete.

        Raises:
            ListNotFoundError: If the list is not found.
            TaskNotFoundError: If the task is not found.
            TodoAPIError: If an error occurs during deletion.
        """
        try:
            logger.info(
                "Deleting task '%s' from list '%s' for user %s", task_name, list_name, user_email
            )
            await self.repo.delete_task(user_email, list_name, task_name)
            logger.info("Task '%s' deleted successfully", task_name)
        except (ListNotFoundError, TaskNotFoundError):
            raise
        except Exception as e:
            logger.error("Error deleting task '%s': %s", task_name, str(e), exc_info=True)
            raise TodoAPIError(detail=str(e)) from e
