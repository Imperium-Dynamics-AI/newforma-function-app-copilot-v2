from src.repositories.graph_client import GraphClient
from src.utils.url_builder import UrlBuilder
class TodoRepository:
    def __init__(self):
        self.graph_client = GraphClient()
        self.url_builder = UrlBuilder()

    async def create_list(self, user_email: str, list_name: str):
        endpoint = self.url_builder.create_list_url(user_email)
        payload = {"displayName": list_name}
        return await self.graph_client.request("POST", endpoint, json_body=payload)
    
    async def fetch_lists(self, user_email: str):
        endpoint = self.url_builder.fetch_lists_url(user_email)
        return await self.graph_client.request("GET", endpoint)
