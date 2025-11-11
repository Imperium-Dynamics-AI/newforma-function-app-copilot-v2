from src.services.todo_service import TodoService
class TodoManager:
    def __init__(self):
        self.service = TodoService()

    async def create_list(self, user_email: str, list_name: str):
        try:
            return await self.service.create_list(user_email, list_name)
        except Exception as e:
            return {"error": str(e)}
        

    async def fetch_lists(self, user_email: str):
        try:
            return await self.service.fetch_lists(user_email)
        except Exception as e:
            return {"error": str(e)}
