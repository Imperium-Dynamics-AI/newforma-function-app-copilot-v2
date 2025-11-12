"""
Repository Lookup Utilities - Consolidates common lookup functions for repositories.

This module provides reusable functions for looking up resources by name in the
Microsoft Graph API, supporting case-insensitive matching with proper logging
and error handling.
"""

from typing import Optional
from src.logging.logger import get_logger

logger = get_logger(__name__)


async def get_resource_id_by_name(
    graph_client,
    endpoint: str,
    resource_name: str,
    display_name_field: str = "displayName",
    resource_type: str = "resource",
) -> Optional[str]:
    """
    Generic function to get a resource ID by name (case-insensitive match).

    Args:
        graph_client: The GraphClient instance for API requests.
        endpoint (str): The Graph API endpoint to query.
        resource_name (str): The resource name to search for.
        display_name_field (str): The field name for display name. Defaults to "displayName".
        resource_type (str): The resource type for logging. Defaults to "resource".

    Returns:
        Optional[str]: The resource ID if found, None otherwise.

    Raises:
        Exception: If the request to Graph API fails.
    """
    try:
        resp = await graph_client.request("GET", endpoint)
        items_data = resp.get("value", [])

        for item in items_data:
            if item.get(display_name_field, "").lower() == resource_name.lower():
                resource_id = item.get("id")
                logger.info(
                    "Found %s '%s' with ID %s",
                    resource_type,
                    resource_name,
                    resource_id,
                )
                return resource_id

        logger.info("No %s found with the name '%s'", resource_type, resource_name)
        return None
    except Exception as e:
        logger.error(
            "Failed to retrieve %s ID for '%s': %s",
            resource_type,
            resource_name,
            str(e),
            exc_info=True,
        )
        raise


async def get_list_id_by_name(graph_client, user_email: str, list_name: str) -> Optional[str]:
    """
    Get a To-Do list ID by list name (case-insensitive match).

    Args:
        graph_client: The GraphClient instance for API requests.
        user_email (str): The user's email.
        list_name (str): The display name of the list.

    Returns:
        Optional[str]: The list ID if found, None otherwise.

    Raises:
        Exception: If the request to Graph API fails.
    """
    endpoint = f"/users/{user_email}/todo/lists"
    return await get_resource_id_by_name(graph_client, endpoint, list_name, "displayName", "list")


async def get_task_id_by_name(
    graph_client, user_email: str, list_id: str, task_name: str
) -> Optional[str]:
    """
    Get a task ID by task title (case-insensitive match).

    Args:
        graph_client: The GraphClient instance for API requests.
        user_email (str): The user's email.
        list_id (str): The ID of the list.
        task_name (str): The task title.

    Returns:
        Optional[str]: The task ID if found, None otherwise.

    Raises:
        Exception: If the request to Graph API fails.
    """
    endpoint = f"/users/{user_email}/todo/lists/{list_id}/tasks"
    return await get_resource_id_by_name(graph_client, endpoint, task_name, "title", "task")


async def get_subtask_id_by_name(
    graph_client, user_email: str, list_id: str, task_id: str, subtask_name: str
) -> Optional[str]:
    """
    Get a subtask ID by subtask title (case-insensitive match).

    Args:
        graph_client: The GraphClient instance for API requests.
        user_email (str): The user's email.
        list_id (str): The ID of the list.
        task_id (str): The ID of the task.
        subtask_name (str): The subtask title.

    Returns:
        Optional[str]: The subtask ID if found, None otherwise.

    Raises:
        Exception: If the request to Graph API fails.
    """
    endpoint = f"/users/{user_email}/todo/lists/{list_id}/tasks/{task_id}/checklistItems"
    return await get_resource_id_by_name(graph_client, endpoint, subtask_name, "title", "subtask")
