# src/services/auth_service.py
from azure.identity.aio import DefaultAzureCredential
from src.config.settings import settings


class AuthService:
    def __init__(self):
        # Use DefaultAzureCredential for local dev, managed identity, or environment creds
        self.credential = DefaultAzureCredential()
        self.scope = [settings.graph_api_scope]

    async def get_token(self) -> str:
        """
        Returns a valid access token for Microsoft Graph.
        """
        token = await self.credential.get_token(*self.scope)
        return token.token
