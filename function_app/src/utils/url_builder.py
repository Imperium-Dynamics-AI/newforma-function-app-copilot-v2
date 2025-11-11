# src/utils/url_builder.py
from src.config.settings import settings

class UrlBuilder:
    """
    Centralized builder for all Microsoft Graph API endpoint URLs.
    Uses the base URL from the settings object.
    """

    BASE_URL = settings.graph_api_url  # Read from settings.py

    # ---------------------------
    # To Do List Endpoints
    # ---------------------------

    def create_list_url(self, user_email: str) -> str:
        """
        Build the endpoint for creating a new To Do list for the given user.
        """
        return f"{self.BASE_URL}/users/{user_email}/todo/lists"

    def fetch_lists_url(self, user_email: str) -> str:
        """
        Build the endpoint for fetching all To Do lists for the given user.
        """
        return f"{self.BASE_URL}/users/{user_email}/todo/lists"