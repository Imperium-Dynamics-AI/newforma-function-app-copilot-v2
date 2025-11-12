"""
UserRepository - data access layer for User resources using Microsoft Graph API.
"""

from src.repositories.graph_client import GraphClient
from src.utils.url_builder import URLBuilder


class UserRepository:
    """
    Repository class for interacting with user data via Graph API.
    """

    def __init__(self, graph_client: GraphClient):
        """
        Initialize the UserRepository with a GraphClient instance.

        Args:
            graph_client (GraphClient): The HTTP client for Graph API requests.
        """
        self.client = graph_client

    async def get_user_id_by_email(self, email: str) -> str | None:
        """
        Resolves a user's Azure AD ID given their email.

        Args:
            email (str): The user's email address.

        Returns:
            str | None: The user's Azure AD ID, or None if user not found.
        """
        endpoint = URLBuilder.user_profile(email)
        resp = await self.client.get(endpoint)
        return resp.get("id")
