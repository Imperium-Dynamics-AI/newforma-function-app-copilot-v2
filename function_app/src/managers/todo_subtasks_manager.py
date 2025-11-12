"""
TodoSubtasksManager - business logic layer for To-Do Subtasks.
Delegates data operations to TodoSubtasksRepository and handles errors by raising custom exceptions.
"""

from typing import Any, Dict, List

from src.common.exceptions import (
    TodoAPIError,
    ValidationError,
    ListNotFoundError,
    TaskNotFoundError,
    SubtaskNotFoundError,
    DuplicateSubtaskError,
)
from src.repositories.todo_subtasks_repository import TodoSubtasksRepository
from src.logging.logger import get_logger
from src.utils.manager_utils import validate_non_empty_string

logger = get_logger(__name__)


class TodoSubtasksManager:
    """
    Manager class for handling To-Do Subtasks business logic.
    Provides high-level operations for subtask management with validation and error handling.
    """

    def __init__(self, repository: TodoSubtasksRepository) -> None:
        """
        Initialize the TodoSubtasksManager with a TodoSubtasksRepository instance.

        Args:
            repository (TodoSubtasksRepository): The repository for subtask data access operations.
        """
        self.repo = repository

    async def create_subtask(
        self, user_email: str, list_name: str, task_name: str, title: str
    ) -> Dict[str, Any]:
        """
        Create a new subtask for a task.

        Args:
            user_email (str): The user's email.
            list_name (str): The name of the list.
            task_name (str): The name of the task.
            title (str): The subtask title.

        Returns:
            Dict[str, Any]: Dictionary representing the created subtask.

        Raises:
            ValidationError: If title is empty.
            ListNotFoundError: If the list is not found.
            TaskNotFoundError: If the task is not found.
            DuplicateSubtaskError: If a subtask with the same title already exists.
            TodoAPIError: If an error occurs during creation.
        """
        try:
            validated_title = validate_non_empty_string(title, "Subtask title")
            logger.info(
                "Creating subtask '%s' for task '%s' in list '%s' for user %s",
                validated_title,
                task_name,
                list_name,
                user_email,
            )
            result = await self.repo.create_subtask(
                user_email, list_name, task_name, validated_title
            )
            logger.info("Subtask created successfully: %s", result.get("subtask_id"))
            return result
        except (ValidationError, ListNotFoundError, TaskNotFoundError, DuplicateSubtaskError):
            raise
        except Exception as e:
            logger.error("Error creating subtask '%s': %s", title, str(e), exc_info=True)
            raise TodoAPIError(detail=str(e)) from e

    async def get_subtasks(
        self, user_email: str, list_name: str, task_name: str
    ) -> List[Dict[str, Any]]:
        """
        Get all subtasks for a task.

        Args:
            user_email (str): The user's email.
            list_name (str): The name of the list.
            task_name (str): The name of the task.

        Returns:
            List[Dict[str, Any]]: List of subtask dictionaries.

        Raises:
            ListNotFoundError: If the list is not found.
            TaskNotFoundError: If the task is not found.
            TodoAPIError: If an error occurs during retrieval.
        """
        try:
            logger.info(
                "Fetching subtasks for task '%s' in list '%s' for user %s",
                task_name,
                list_name,
                user_email,
            )
            result = await self.repo.get_subtasks(user_email, list_name, task_name)
            subtasks = result.get("subtasks", [])
            logger.info("Retrieved %d subtasks for task '%s'", len(subtasks), task_name)
            return subtasks
        except (ListNotFoundError, TaskNotFoundError):
            raise
        except Exception as e:
            logger.error(
                "Error fetching subtasks for task '%s': %s", task_name, str(e), exc_info=True
            )
            raise TodoAPIError(detail=str(e)) from e

    async def edit_subtask(
        self, user_email: str, list_name: str, task_name: str, subtask_name: str, new_title: str
    ) -> None:
        """
        Edit a subtask title.

        Args:
            user_email (str): The user's email.
            list_name (str): The name of the list.
            task_name (str): The name of the task.
            subtask_name (str): The current subtask title.
            new_title (str): The new subtask title.

        Raises:
            ValidationError: If new_title is empty.
            ListNotFoundError: If the list is not found.
            TaskNotFoundError: If the task is not found.
            SubtaskNotFoundError: If the subtask is not found.
            DuplicateSubtaskError: If a subtask with new_title already exists.
            TodoAPIError: If an error occurs during edit.
        """
        try:
            validated_title = validate_non_empty_string(new_title, "Subtask title")
            logger.info(
                "Editing subtask '%s' for task '%s' in list '%s' with new title '%s'",
                subtask_name,
                task_name,
                list_name,
                validated_title,
            )
            await self.repo.edit_subtask(
                user_email, list_name, task_name, subtask_name, validated_title
            )
            logger.info("Subtask '%s' edited successfully", subtask_name)
        except (
            ValidationError,
            ListNotFoundError,
            TaskNotFoundError,
            SubtaskNotFoundError,
            DuplicateSubtaskError,
        ):
            raise
        except Exception as e:
            logger.error("Error editing subtask '%s': %s", subtask_name, str(e), exc_info=True)
            raise TodoAPIError(detail=str(e)) from e

    async def delete_subtask(
        self, user_email: str, list_name: str, task_name: str, subtask_name: str
    ) -> None:
        """
        Delete a subtask.

        Args:
            user_email (str): The user's email.
            list_name (str): The name of the list.
            task_name (str): The name of the task.
            subtask_name (str): The subtask title to delete.

        Raises:
            ListNotFoundError: If the list is not found.
            TaskNotFoundError: If the task is not found.
            SubtaskNotFoundError: If the subtask is not found.
            TodoAPIError: If an error occurs during deletion.
        """
        try:
            logger.info(
                "Deleting subtask '%s' from task '%s' in list '%s' for user %s",
                subtask_name,
                task_name,
                list_name,
                user_email,
            )
            await self.repo.delete_subtask(user_email, list_name, task_name, subtask_name)
            logger.info("Subtask '%s' deleted successfully", subtask_name)
        except (ListNotFoundError, TaskNotFoundError, SubtaskNotFoundError):
            raise
        except Exception as e:
            logger.error("Error deleting subtask '%s': %s", subtask_name, str(e), exc_info=True)
            raise TodoAPIError(detail=str(e)) from e
