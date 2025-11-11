"""
TodoRepository - data access layer for To-Do resources using Microsoft Graph API.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from src.repositories.graph_client import GraphClient


class TodoRepository:
    """
    Repository class for interacting with Microsoft To Do via Graph API.
    """

    def __init__(self) -> None:
        """
        Initialize the TodoRepository with a GraphClient instance.
        """
        self.graph_client = GraphClient()

    async def create_list(self, user_email: str, list_name: str) -> Dict[str, Any]:
        """
        Create a new To-Do list via Microsoft Graph API.

        Args:
            user_email (str): The user's email or principal name.
            list_name (str): The display name of the list.

        Returns:
            Dict[str, Any]: The raw response from the Graph API.
        """
        endpoint = f"/users/{user_email}/todo/lists"
        payload = {"displayName": list_name}
        return await self.graph_client.request("POST", endpoint, json_body=payload)

    async def get_lists(self, user_email: str) -> List[Dict[str, Any]]:
        """
        Get all To-Do lists for a user.

        Args:
            user_email (str): The user's email.

        Returns:
            List[Dict[str, Any]]: List of raw list data from Graph API.
        """

    async def edit_list(self, user_email: str, list_id: str, new_name: str) -> None:
        """
        Edit a To-Do list name.

        Args:
            user_email (str): The user's email.
            list_id (str): The ID of the list.
            new_name (str): The new display name.
        """

    async def delete_list(self, user_email: str, list_id: str) -> None:
        """
        Delete a To-Do list.

        Args:
            user_email (str): The user's email.
            list_id (str): The ID of the list.
        """

    async def create_task(
        self,
        user_email: str,
        list_id: str,
        title: str,
        description: Optional[str],
        due_date: Optional[datetime],
    ) -> Dict[str, Any]:
        """
        Create a new task in a list.

        Args:
            user_email (str): The user's email.
            list_id (str): The ID of the list.
            title (str): The task title.
            description (Optional[str]): The task description.
            due_date (Optional[datetime]): The due date.

        Returns:
            Dict[str, Any]: Raw task data from Graph API.
        """

    async def get_tasks(self, user_email: str, list_id: str) -> List[Dict[str, Any]]:
        """
        Get all tasks in a list.

        Args:
            user_email (str): The user's email.
            list_id (str): The ID of the list.

        Returns:
            List[Dict[str, Any]]: List of raw task data.
        """

    async def edit_task(self, user_email: str, task_id: str, new_title: str) -> None:
        """
        Edit a task title.

        Args:
            user_email (str): The user's email.
            task_id (str): The ID of the task.
            new_title (str): The new title.
        """

    async def update_task_status(
        self, user_email: str, task_id: str, status: str
    ) -> None:
        """
        Update task status.

        Args:
            user_email (str): The user's email.
            task_id (str): The ID of the task.
            status (str): The new status ("pending" or "completed").
        """

    async def update_task_description(
        self, user_email: str, task_id: str, description: Optional[str]
    ) -> None:
        """
        Update task description.

        Args:
            user_email (str): The user's email.
            task_id (str): The ID of the task.
            description (Optional[str]): The new description.
        """

    async def update_task_duedate(
        self, user_email: str, task_id: str, due_date: Optional[datetime]
    ) -> None:
        """
        Update task due date.

        Args:
            user_email (str): The user's email.
            task_id (str): The ID of the task.
            due_date (Optional[datetime]): The new due date.
        """

    async def delete_task(self, user_email: str, task_id: str) -> None:
        """
        Delete a task.

        Args:
            user_email (str): The user's email.
            task_id (str): The ID of the task.
        """

    async def create_subtask(
        self, user_email: str, task_id: str, title: str
    ) -> Dict[str, Any]:
        """
        Create a new subtask (checklist item).

        Args:
            user_email (str): The user's email.
            task_id (str): The ID of the parent task.
            title (str): The subtask title.

        Returns:
            Dict[str, Any]: Raw subtask data from Graph API.
        """

    async def get_subtasks(self, user_email: str, task_id: str) -> List[Dict[str, Any]]:
        """
        Get all subtasks for a task.

        Args:
            user_email (str): The user's email.
            task_id (str): The ID of the task.

        Returns:
            List[Dict[str, Any]]: List of raw subtask data.
        """

    async def edit_subtask(
        self, user_email: str, subtask_id: str, new_title: str
    ) -> None:
        """
        Edit a subtask title.

        Args:
            user_email (str): The user's email.
            subtask_id (str): The ID of the subtask.
            new_title (str): The new title.
        """

    async def delete_subtask(self, user_email: str, subtask_id: str) -> None:
        """
        Delete a subtask.

        Args:
            user_email (str): The user's email.
            subtask_id (str): The ID of the subtask.
        """
