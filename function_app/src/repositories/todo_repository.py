from src.repositories.graph_client import GraphClient

class TodoRepository:
    def __init__(self):
        self.graph_client = GraphClient()

    async def create_list(self, user_email: str, list_name: str):
        endpoint = f"/users/{user_email}/todo/lists"
        payload = {"displayName": list_name}
        return await self.graph_client.request("POST", endpoint, json_body=payload)
