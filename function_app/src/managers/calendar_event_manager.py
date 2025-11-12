"""
CalendarEventManager - business logic layer for calendar events.
Handles calendar event operations.
"""

from src.repositories.calendar_repository import CalendarRepository


class CalendarEventManager:
    """
    Manager class for handling calendar event business logic.
    """

    def __init__(self, repository: CalendarRepository) -> None:
        """
        Initialize the CalendarEventManager with a CalendarRepository instance.

        Args:
            repository (CalendarRepository): The repository for calendar data access.
        """
        self.repository = repository
