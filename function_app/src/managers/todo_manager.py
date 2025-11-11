from src.repositories.todo_repository import TodoRepository

class TodoManager:
    def __init__(self):
        self.repo = TodoRepository()

    async def create_list(self, user_email: str, list_name: str):
        try:
            return await self.repo.create_list(user_email, list_name)
        except Exception as e:
            return {"error": str(e)}
