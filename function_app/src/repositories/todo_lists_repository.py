"""
TodoListsRepository - data access layer for To-Do Lists using Microsoft Graph API.
"""

from datetime import datetime, timezone
from typing import Any, Dict, Optional

from src.repositories.graph_client import GraphClient
from src.common.exceptions import (
    ListNotFoundError,
    DuplicateListError,
)
from src.logging.logger import get_logger
from src.utils.repository_utils import get_list_id_by_name
from src.utils.url_builder import URLBuilder

logger = get_logger(__name__)


class TodoListsRepository:
    """
    Repository class for interacting with To-Do Lists via Graph API.
    Handles all data access operations for list CRUD operations.
    """

    def __init__(self, graph_client: GraphClient) -> None:
        """
        Initialize the TodoListsRepository with a GraphClient instance.

        Args:
            graph_client (GraphClient): The HTTP client for Graph API requests.
        """
        self.graph_client = graph_client

    async def get_list_id_by_name(self, user_email: str, list_name: str) -> Optional[str]:
        """
        Get a To-Do list ID by list name (case-insensitive match).

        Args:
            user_email (str): The user's email.
            list_name (str): The display name of the list.

        Returns:
            Optional[str]: The list ID if found, None otherwise.

        Raises:
            Exception: If the request to Graph API fails.
        """
        return await get_list_id_by_name(self.graph_client, user_email, list_name)

    async def create_list(self, user_email: str, list_name: str) -> Dict[str, Any]:
        """
        Create a new To-Do list via Microsoft Graph API.
        Checks for duplicate list names (case-insensitive).

        Args:
            user_email (str): The user's email or principal name.
            list_name (str): The display name of the list.

        Returns:
            Dict[str, Any]: Dictionary with list_id, list_name, user_email, and created_at.

        Raises:
            ConflictError: If a list with the same name already exists.
            Exception: If the request to Graph API fails.
        """
        existing_list_id = await self.get_list_id_by_name(user_email, list_name)
        if existing_list_id:
            logger.warning(
                "Attempt to create duplicate list '%s' for user %s", list_name, user_email
            )
            raise DuplicateListError(list_name)

        endpoint = URLBuilder.todo_lists(user_email)
        payload = {"displayName": list_name}
        try:
            resp = await self.graph_client.request("POST", endpoint, json_body=payload)
            logger.info("Successfully created list '%s' for user %s", list_name, user_email)
            created_at = resp.get("createdDateTime")
            if not created_at:
                created_at = datetime.now(timezone.utc).isoformat()

            return {
                "list_id": resp.get("id"),
                "list_name": resp.get("displayName"),
                "user_email": user_email,
                "created_at": created_at,
            }
        except Exception as e:
            logger.error(
                "Failed to create list '%s' for user %s: %s",
                list_name,
                user_email,
                str(e),
                exc_info=True,
            )
            raise

    async def get_lists(self, user_email: str) -> Dict[str, Any]:
        """
        Get all To-Do lists for a user.

        Args:
            user_email (str): The user's email.

        Returns:
            Dict[str, Any]: Dict with 'lists' key containing list of lists.

        Raises:
            Exception: If the request to Graph API fails.
        """
        endpoint = URLBuilder.todo_lists(user_email)
        try:
            resp = await self.graph_client.request("GET", endpoint)
            logger.info("Successfully retrieved lists for user %s", user_email)
            lists_data = resp.get("value", [])
            lists = [
                {
                    "list_id": lst.get("id"),
                    "list_name": lst.get("displayName"),
                    "user_email": user_email,
                    "created_at": lst.get("createdDateTime"),
                }
                for lst in lists_data
            ]
            return {"lists": lists}
        except Exception as e:
            logger.error(
                "Failed to retrieve lists for user %s: %s", user_email, str(e), exc_info=True
            )
            raise

    async def edit_list(self, user_email: str, list_name: str, new_name: str) -> None:
        """
        Edit a To-Do list name by looking up the list by name.

        Args:
            user_email (str): The user's email.
            list_name (str): The current display name of the list.
            new_name (str): The new display name.

        Raises:
            ListNotFoundError: If the list with list_name is not found.
            DuplicateListError: If a list with new_name already exists.
            Exception: If the request to Graph API fails.
        """

        list_id = await self.get_list_id_by_name(user_email, list_name)
        if not list_id:
            logger.warning("List '%s' not found for user %s", list_name, user_email)
            raise ListNotFoundError(list_name)

        # Check if new name already exists
        existing_list_id = await self.get_list_id_by_name(user_email, new_name)
        if existing_list_id and existing_list_id != list_id:
            logger.warning("Attempt to rename list to existing name '%s'", new_name)
            raise DuplicateListError(new_name)

        endpoint = URLBuilder.todo_list(user_email, list_id)
        payload = {"displayName": new_name}

        try:
            await self.graph_client.request("PATCH", endpoint, json_body=payload)
            logger.info(
                "Successfully edited list '%s' for user %s with new name '%s'",
                list_name,
                user_email,
                new_name,
            )
        except Exception as e:
            logger.error(
                "Failed to edit list '%s' for user %s: %s",
                list_name,
                user_email,
                str(e),
                exc_info=True,
            )
            raise

    async def delete_list(self, user_email: str, list_name: str) -> None:
        """
        Delete a To-Do list by looking up the list by name.

        Args:
            user_email (str): The user's email.
            list_name (str): The display name of the list to delete.

        Raises:
            ListNotFoundError: If the list is not found.
            Exception: If the request to Graph API fails.
        """

        list_id = await self.get_list_id_by_name(user_email, list_name)
        if not list_id:
            logger.warning("List '%s' not found for user %s", list_name, user_email)
            raise ListNotFoundError(list_name)

        endpoint = URLBuilder.todo_list(user_email, list_id)
        try:
            await self.graph_client.request("DELETE", endpoint)
            logger.info("Successfully deleted list '%s' for user %s", list_name, user_email)
        except Exception as e:
            logger.error(
                "Failed to delete list '%s' for user %s: %s",
                list_name,
                user_email,
                str(e),
                exc_info=True,
            )
            raise
