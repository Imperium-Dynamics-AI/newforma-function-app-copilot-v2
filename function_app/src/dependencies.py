"""
Dependency Injection Module
Provides factory functions for creating instances with proper dependency hierarchy:
AuthManager → GraphClient → Repositories → Managers → Handlers
"""

from src.repositories.calendar_repository import CalendarRepository
from src.repositories.todo_lists_repository import TodoListsRepository
from src.repositories.todo_tasks_repository import TodoTasksRepository
from src.repositories.todo_subtasks_repository import TodoSubtasksRepository
from src.repositories.user_repository import UserRepository
from src.repositories.graph_client import GraphClient
from src.managers.auth_manager import AuthManager
from src.managers.birthday_reminder_manager import BirthdayReminderManager
from src.managers.calendar_event_manager import CalendarEventManager
from src.managers.todo_lists_manager import TodoListsManager
from src.managers.todo_tasks_manager import TodoTasksManager
from src.managers.todo_subtasks_manager import TodoSubtasksManager
from src.handlers.event_handler import EventHandler
from src.handlers.todo_lists_handler import TodoListsHandler
from src.handlers.todo_subtasks_handler import TodoSubtasksHandler
from src.handlers.todo_tasks_handler import TodoTasksHandler


# ==================== AuthManager ====================


def get_auth_manager() -> AuthManager:
    """
    Factory function to create and return an AuthManager instance.
    AuthManager handles token retrieval for all Graph API requests.
    This is the base dependency for GraphClient.

    Returns:
        AuthManager: Instance of AuthManager for authentication and token management.
    """
    return AuthManager()


# ==================== GraphClient ====================


def get_graph_client() -> GraphClient:
    """
    Factory function to create and return a GraphClient instance.
    Injects AuthManager for token retrieval.
    This is the base dependency for all repositories.

    Returns:
        GraphClient: Instance of GraphClient for Graph API communication.
    """
    auth_manager = get_auth_manager()
    return GraphClient(auth_manager=auth_manager)


# ==================== Repositories ====================


def get_calendar_repository() -> CalendarRepository:
    """
    Factory function to create and return a CalendarRepository instance.
    Injects GraphClient as a dependency.

    Returns:
        CalendarRepository: Instance of CalendarRepository with GraphClient injected.
    """
    graph_client = get_graph_client()
    return CalendarRepository(graph_client=graph_client)


def get_todo_lists_repository() -> TodoListsRepository:
    """
    Factory function to create and return a TodoListsRepository instance.
    Injects GraphClient as a dependency.

    Returns:
        TodoListsRepository: Instance of TodoListsRepository with GraphClient injected.
    """
    graph_client = get_graph_client()
    return TodoListsRepository(graph_client=graph_client)


def get_todo_tasks_repository() -> TodoTasksRepository:
    """
    Factory function to create and return a TodoTasksRepository instance.
    Injects GraphClient as a dependency.

    Returns:
        TodoTasksRepository: Instance of TodoTasksRepository with GraphClient injected.
    """
    graph_client = get_graph_client()
    return TodoTasksRepository(graph_client=graph_client)


def get_todo_subtasks_repository() -> TodoSubtasksRepository:
    """
    Factory function to create and return a TodoSubtasksRepository instance.
    Injects GraphClient as a dependency.

    Returns:
        TodoSubtasksRepository: Instance of TodoSubtasksRepository with GraphClient injected.
    """
    graph_client = get_graph_client()
    return TodoSubtasksRepository(graph_client=graph_client)


def get_user_repository() -> UserRepository:
    """
    Factory function to create and return a UserRepository instance.
    Injects GraphClient as a dependency.

    Returns:
        UserRepository: Instance of UserRepository with GraphClient injected.
    """
    graph_client = get_graph_client()
    return UserRepository(graph_client=graph_client)


# ==================== Managers ====================


def get_todo_lists_manager() -> TodoListsManager:
    """
    Factory function to create and return a TodoListsManager instance.
    Injects TodoListsRepository as a dependency.

    Returns:
        TodoListsManager: Instance of TodoListsManager with TodoListsRepository injected.
    """
    todo_lists_repository = get_todo_lists_repository()
    return TodoListsManager(repository=todo_lists_repository)


def get_todo_tasks_manager() -> TodoTasksManager:
    """
    Factory function to create and return a TodoTasksManager instance.
    Injects TodoTasksRepository as a dependency.

    Returns:
        TodoTasksManager: Instance of TodoTasksManager with TodoTasksRepository injected.
    """
    todo_tasks_repository = get_todo_tasks_repository()
    return TodoTasksManager(repository=todo_tasks_repository)


def get_todo_subtasks_manager() -> TodoSubtasksManager:
    """
    Factory function to create and return a TodoSubtasksManager instance.
    Injects TodoSubtasksRepository as a dependency.

    Returns:
        TodoSubtasksManager: Instance of TodoSubtasksManager with TodoSubtasksRepository injected.
    """
    todo_subtasks_repository = get_todo_subtasks_repository()
    return TodoSubtasksManager(repository=todo_subtasks_repository)


def get_birthday_reminder_manager() -> BirthdayReminderManager:
    """
    Factory function to create and return a BirthdayReminderManager instance.
    Injects UserRepository as a dependency.

    Returns:
        BirthdayReminderManager: Instance of BirthdayReminderManager with UserRepository injected.
    """
    user_repository = get_user_repository()
    return BirthdayReminderManager(user_repository=user_repository)


def get_calendar_event_manager() -> CalendarEventManager:
    """
    Factory function to create and return a CalendarEventManager instance.
    Injects CalendarRepository as a dependency.

    Returns:
        CalendarEventManager: Instance of CalendarEventManager with CalendarRepository injected.
    """
    calendar_repository = get_calendar_repository()
    return CalendarEventManager(repository=calendar_repository)


# ==================== Handlers ====================


def get_todo_lists_handler() -> TodoListsHandler:
    """
    Factory function to create and return a TodoListsHandler instance.
    Injects TodoListsManager as a dependency.

    Returns:
        TodoListsHandler: Instance of TodoListsHandler with TodoListsManager injected.
    """
    todo_lists_manager = get_todo_lists_manager()
    return TodoListsHandler(manager=todo_lists_manager)


def get_todo_tasks_handler() -> TodoTasksHandler:
    """
    Factory function to create and return a TodoTasksHandler instance.
    Injects TodoTasksManager as a dependency.

    Returns:
        TodoTasksHandler: Instance of TodoTasksHandler with TodoTasksManager injected.
    """
    todo_tasks_manager = get_todo_tasks_manager()
    return TodoTasksHandler(manager=todo_tasks_manager)


def get_todo_subtasks_handler() -> TodoSubtasksHandler:
    """
    Factory function to create and return a TodoSubtasksHandler instance.
    Injects TodoSubtasksManager as a dependency.

    Returns:
        TodoSubtasksHandler: Instance of TodoSubtasksHandler with TodoSubtasksManager injected.
    """
    todo_subtasks_manager = get_todo_subtasks_manager()
    return TodoSubtasksHandler(manager=todo_subtasks_manager)


def get_event_handler() -> EventHandler:
    """
    Factory function to create and return an EventHandler instance.
    Injects CalendarEventManager and AuthManager as dependencies.

    Returns:
        EventHandler: Instance of EventHandler with managers injected.
    """
    calendar_event_manager = get_calendar_event_manager()
    auth_manager = get_auth_manager()
    return EventHandler(calendar_event_manager=calendar_event_manager, auth_manager=auth_manager)
