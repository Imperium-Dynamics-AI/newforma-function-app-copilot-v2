"""
Graph API URL endpoints and patterns.

This module centralizes all Microsoft Graph API endpoint definitions for easy maintenance
and updates. All URL patterns are defined here to ensure consistency across the application.
"""

# User endpoints
USER_PROFILE = "/users/{user_email}"

# Calendar endpoints
CALENDAR_EVENTS = "/users/{user_email}/calendar/events"
CALENDAR_EVENT = "/users/{user_email}/calendar/events/{event_id}"

# To-Do Lists endpoints
TODO_LISTS = "/users/{user_email}/todo/lists"
TODO_LIST = "/users/{user_email}/todo/lists/{list_id}"

# To-Do Tasks endpoints
TODO_TASKS_BY_LIST = "/users/{user_email}/todo/lists/{list_id}/tasks"
TODO_TASK_BY_LIST = "/users/{user_email}/todo/lists/{list_id}/tasks/{task_id}"

# To-Do Subtasks (checklistItems) endpoints
TODO_SUBTASKS = "/users/{user_email}/todo/lists/{list_id}/tasks/{task_id}/checklistItems"
TODO_SUBTASK = (
    "/users/{user_email}/todo/lists/{list_id}/tasks/{task_id}/checklistItems/{subtask_id}"
)

# Query parameters for filtering
FILTER_BY_NAME = "$filter=displayName eq '{name}'"
SELECT_FIELDS = "$select={fields}"
