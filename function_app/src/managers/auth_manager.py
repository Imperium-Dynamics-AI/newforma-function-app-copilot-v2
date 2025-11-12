"""
AuthManager - business logic layer for authentication.
Handles authentication-related operations and token retrieval for Microsoft Graph API.
"""

from azure.identity.aio import DefaultAzureCredential
from src.config.settings import settings


class AuthManager:
    """
    Manager class for handling authentication business logic and token management.
    Provides access tokens for Microsoft Graph API authentication.
    """

    def __init__(self) -> None:
        """
        Initialize the AuthManager.

        We avoid creating a long-lived DefaultAzureCredential here to prevent
        unclosed aiohttp sessions. Instead, `get_token` will create and close
        a credential per call.
        """
        self.scope = [settings.graph_api_scope]

    async def get_token(self) -> str:
        """
        Retrieve a valid OAuth 2.0 access token for Microsoft Graph API.

        Creates a short-lived DefaultAzureCredential, obtains a token and
        closes the credential to ensure no aiohttp ClientSession is left open.

        Returns:
            str: A valid bearer token for authenticating Graph API requests.
        """
        credential = DefaultAzureCredential()
        try:
            token = await credential.get_token(*self.scope)
            return token.token
        finally:
            await credential.close()
