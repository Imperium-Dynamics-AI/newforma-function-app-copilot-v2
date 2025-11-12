"""
BirthdayReminderManager - business logic layer for birthday reminders.
Handles birthday reminder operations.
"""

from src.repositories.user_repository import UserRepository


class BirthdayReminderManager:
    """
    Manager class for handling birthday reminder business logic.
    """

    def __init__(self, user_repository: UserRepository) -> None:
        """
        Initialize the BirthdayReminderManager with a UserRepository instance.

        Args:
            user_repository (UserRepository): The repository for user data access.
        """
        self.user_repository = user_repository
