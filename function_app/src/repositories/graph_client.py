# src/repositories/graph_client.py
import aiohttp
from src.services.auth_service import AuthService
from src.config.settings import settings

class GraphClient:
    def __init__(self):
        self.auth_service = AuthService()

    async def request(self, method: str, endpoint: str, json_body=None):
        token = await self.auth_service.get_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        url = f"{settings.graph_api_url}{endpoint}"
        async with aiohttp.ClientSession() as session:
            async with session.request(method, url, headers=headers, json=json_body) as resp:
                if resp.status >= 400:
                    text = await resp.text()
                    raise RuntimeError(f"Graph API error {resp.status}: {text}")
                return await resp.json()

    async def get(self, endpoint: str):
        return await self.request("GET", endpoint)

    async def post(self, endpoint: str, json_body=None):
        return await self.request("POST", endpoint, json_body)
