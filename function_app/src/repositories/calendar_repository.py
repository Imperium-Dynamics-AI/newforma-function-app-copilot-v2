"""
CalendarRepository - data access layer for Calendar resources using Microsoft Graph API.
"""

from src.repositories.graph_client import GraphClient


class CalendarRepository:
    """
    Repository class for interacting with calendar data via Graph API.
    """

    def __init__(self, graph_client: GraphClient):
        """
        Initialize the CalendarRepository with a GraphClient instance.

        Args:
            graph_client (GraphClient): The HTTP client for Graph API requests.
        """
        self.graph_client = graph_client
