"""
TodoListsManager - business logic layer for To-Do Lists.
Delegates data operations to TodoListsRepository and handles errors by raising custom exceptions.
"""

from src.common.exceptions import (
    TodoAPIError,
    ValidationError,
    ListNotFoundError,
    DuplicateListError,
)
from src.repositories.todo_lists_repository import TodoListsRepository
from src.models.todo_lists import ListResponse, ListsResponse
from src.logging.logger import get_logger
from src.utils.manager_utils import validate_non_empty_string

logger = get_logger(__name__)


class TodoListsManager:
    """
    Manager class for handling To-Do Lists business logic.
    Provides high-level operations for list management with validation and error handling.
    """

    def __init__(self, repository: TodoListsRepository) -> None:
        """
        Initialize the TodoListsManager with a TodoListsRepository instance.

        Args:
            repository (TodoListsRepository): The repository for list data access operations.
        """
        self.repo = repository

    async def create_list(self, user_email: str, list_name: str) -> ListResponse:
        """
        Create a new To-Do list.

        Args:
            user_email (str): The user's email.
            list_name (str): The name of the list.

        Returns:
            ListResponse: A ListResponse model representing the created list.

        Raises:
            ValidationError: If list_name is empty.
            DuplicateListError: If a list with the same name already exists.
            TodoAPIError: If an error occurs during creation.
        """
        try:
            validated_name = validate_non_empty_string(list_name, "List name")
            logger.info("Creating list '%s' for user %s", validated_name, user_email)
            raw = await self.repo.create_list(user_email, validated_name)
            response = ListResponse.model_validate(raw)
            logger.info("List created successfully: %s", response.list_id)
            return response
        except (ValidationError, DuplicateListError):
            raise
        except Exception as e:
            logger.error("Error creating list '%s': %s", list_name, str(e), exc_info=True)
            raise TodoAPIError(detail=str(e)) from e

    async def get_lists(self, user_email: str) -> ListsResponse:
        """
        Get all To-Do lists for a user.

        Args:
            user_email (str): The user's email.

        Returns:
            ListsResponse: A ListsResponse model containing all lists for the user.

        Raises:
            TodoAPIError: If an error occurs during retrieval.
        """
        try:
            logger.info("Fetching all lists for user %s", user_email)
            raw = await self.repo.get_lists(user_email)
            response = ListsResponse.model_validate(raw)
            logger.info("Retrieved %d lists for user %s", len(response.lists), user_email)
            return response
        except Exception as e:
            logger.error("Error fetching lists for user %s: %s", user_email, str(e), exc_info=True)
            raise TodoAPIError(detail=str(e)) from e

    async def edit_list(self, user_email: str, list_name: str, new_name: str) -> None:
        """
        Edit a To-Do list name.

        Args:
            user_email (str): The user's email.
            list_name (str): The current name of the list.
            new_name (str): The new name for the list.

        Raises:
            ValidationError: If new_name is empty.
            ListNotFoundError: If the list is not found.
            DuplicateListError: If a list with new_name already exists.
            TodoAPIError: If an error occurs during edit.
        """
        try:
            validated_name = validate_non_empty_string(new_name, "List name")
            logger.info("Editing list '%s' with new name '%s'", list_name, validated_name)
            await self.repo.edit_list(user_email, list_name, validated_name)
            logger.info("List '%s' edited successfully", list_name)
        except (ValidationError, ListNotFoundError, DuplicateListError):
            raise
        except Exception as e:
            logger.error("Error editing list '%s': %s", list_name, str(e), exc_info=True)
            raise TodoAPIError(detail=str(e)) from e

    async def delete_list(self, user_email: str, list_name: str) -> None:
        """
        Delete a To-Do list.

        Args:
            user_email (str): The user's email.
            list_name (str): The name of the list to delete.

        Raises:
            ListNotFoundError: If the list is not found.
            TodoAPIError: If an error occurs during deletion.
        """
        try:
            logger.info("Deleting list '%s' for user %s", list_name, user_email)
            await self.repo.delete_list(user_email, list_name)
            logger.info("List '%s' deleted successfully", list_name)
        except ListNotFoundError:
            raise
        except Exception as e:
            logger.error("Error deleting list '%s': %s", list_name, str(e), exc_info=True)
            raise TodoAPIError(detail=str(e)) from e
