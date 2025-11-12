"""
URL Builder utility for constructing Graph API endpoints.

This module provides functions to build complete Graph API URLs from templates,
centralizing URL construction logic for better maintainability and consistency.
"""

from src.common import graph_urls


class URLBuilder:
    """Builder class for constructing Graph API URLs from templates."""

    @staticmethod
    def build(url_template: str, **kwargs) -> str:
        """
        Build a URL by formatting the template with provided keyword arguments.

        Args:
            url_template (str): The URL template string with placeholders
                                (e.g., "/users/{user_email}")
            **kwargs: Keyword arguments to format into the template

        Returns:
            str: The formatted URL

        Raises:
            KeyError: If a required placeholder is missing from kwargs
            ValueError: If the url_template is empty or None
        """
        if not url_template:
            raise ValueError("url_template cannot be empty or None")

        try:
            return url_template.format(**kwargs)
        except KeyError as e:
            raise KeyError(f"Missing required parameter for URL template: {str(e)}") from e

    @staticmethod
    def user_profile(user_email: str) -> str:
        """Build user profile endpoint."""
        return URLBuilder.build(graph_urls.USER_PROFILE, user_email=user_email)

    @staticmethod
    def todo_lists(user_email: str) -> str:
        """Build to-do lists endpoint."""
        return URLBuilder.build(graph_urls.TODO_LISTS, user_email=user_email)

    @staticmethod
    def todo_list(user_email: str, list_id: str) -> str:
        """Build specific to-do list endpoint."""
        return URLBuilder.build(graph_urls.TODO_LIST, user_email=user_email, list_id=list_id)

    @staticmethod
    def todo_tasks_by_list(user_email: str, list_id: str) -> str:
        """Build tasks within a specific list endpoint."""
        return URLBuilder.build(
            graph_urls.TODO_TASKS_BY_LIST, user_email=user_email, list_id=list_id
        )

    @staticmethod
    def todo_task_by_list(user_email: str, list_id: str, task_id: str) -> str:
        """Build specific task within a list endpoint."""
        return URLBuilder.build(
            graph_urls.TODO_TASK_BY_LIST,
            user_email=user_email,
            list_id=list_id,
            task_id=task_id,
        )

    @staticmethod
    def todo_tasks(user_email: str) -> str:
        """Build global to-do tasks endpoint (all tasks for user)."""
        return URLBuilder.build(graph_urls.TODO_TASKS, user_email=user_email)

    @staticmethod
    def todo_task(user_email: str, task_id: str) -> str:
        """Build specific to-do task endpoint (global)."""
        return URLBuilder.build(graph_urls.TODO_TASK, user_email=user_email, task_id=task_id)

    @staticmethod
    def todo_subtasks(user_email: str, list_id: str, task_id: str) -> str:
        """Build subtasks (checklistItems) endpoint."""
        return URLBuilder.build(
            graph_urls.TODO_SUBTASKS,
            user_email=user_email,
            list_id=list_id,
            task_id=task_id,
        )

    @staticmethod
    def todo_subtask(user_email: str, list_id: str, task_id: str, subtask_id: str) -> str:
        """Build specific subtask endpoint."""
        return URLBuilder.build(
            graph_urls.TODO_SUBTASK,
            user_email=user_email,
            list_id=list_id,
            task_id=task_id,
            subtask_id=subtask_id,
        )

    @staticmethod
    def calendar_events(user_email: str) -> str:
        """Build calendar events endpoint."""
        return URLBuilder.build(graph_urls.CALENDAR_EVENTS, user_email=user_email)

    @staticmethod
    def calendar_event(user_email: str, event_id: str) -> str:
        """Build specific calendar event endpoint."""
        return URLBuilder.build(graph_urls.CALENDAR_EVENT, user_email=user_email, event_id=event_id)

    @staticmethod
    def with_query_params(url: str, **params) -> str:
        """
        Append query parameters to a URL.

        Args:
            url (str): The base URL
            **params: Query parameters as key-value pairs

        Returns:
            str: URL with query parameters appended

        Example:
            url = URLBuilder.with_query_params(
                URLBuilder.todo_lists(user_email),
                filter="displayName eq 'Work'",
                select="id,displayName"
            )
        """
        if not params:
            return url

        query_parts = []
        for key, value in params.items():
            query_parts.append(f"${key}={value}")

        query_string = "&".join(query_parts)
        separator = "&" if "?" in url else "?"
        return f"{url}{separator}{query_string}"
