# src/repositories/user_repository.py
from src.repositories.graph_client import GraphClient

class UserRepository:
    def __init__(self):
        self.client = GraphClient()

    async def get_user_id_by_email(self, email: str) -> str | None:
        """
        Resolves a user's Azure AD ID given their email.
        Returns None if user not found.
        """
        endpoint = f"/users/{email}"
        resp = await self.client.get(endpoint)
        return resp.get("id")
