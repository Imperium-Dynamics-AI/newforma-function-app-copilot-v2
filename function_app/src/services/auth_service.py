"""
This module provides authentication services for obtaining access tokens
to interact with Microsoft Graph API.
"""

from azure.identity.aio import DefaultAzureCredential

from src.config.settings import settings


class AuthService:
    """
    Service for handling authentication and token retrieval for Microsoft Graph API.
    """

    def __init__(self):
        """
        Initializes the AuthService with a DefaultAzureCredential and the scope
        for Microsoft Graph API.
        """
        self.credential = DefaultAzureCredential()
        self.scope = [settings.graph_api_scope]

    async def get_token(self) -> str:
        """
        Returns a valid access token for Microsoft Graph.
        """
        token = await self.credential.get_token(*self.scope)
        return token.token
