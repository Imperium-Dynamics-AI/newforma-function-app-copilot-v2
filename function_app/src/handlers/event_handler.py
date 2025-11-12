"""
Handler for calendar event operations.
"""

import logging
import json

import azure.functions as func

from src.managers.calendar_event_manager import CalendarEventManager
from src.managers.auth_manager import AuthManager

log = logging.getLogger(__name__)


def _json_response(data: dict, status: int = 200) -> func.HttpResponse:
    """Helper to return JSON with correct headers."""
    return func.HttpResponse(
        body=json.dumps(data),
        status_code=status,
        mimetype="application/json",
        headers={"Content-Type": "application/json"},
    )


class EventHandler:
    """Processes HTTP requests for calendar events."""

    def __init__(
        self, calendar_event_manager: CalendarEventManager, auth_manager: AuthManager
    ) -> None:
        """
        Initialize the EventHandler with manager instances.

        Args:
            calendar_event_manager (CalendarEventManager): Manager for calendar event operations.
            auth_manager (AuthManager): Manager for authentication operations.
        """
        self.calendar_event_manager = calendar_event_manager
        self.auth_manager = auth_manager
