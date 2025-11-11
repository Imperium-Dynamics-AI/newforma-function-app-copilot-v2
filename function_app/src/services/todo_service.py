# src/services/todo_service.py
from src.repositories.todo_repository import TodoRepository

class TodoService:
    def __init__(self):
        self.repo = TodoRepository()

    async def create_list(self, user_id: str, display_name: str):
        if not display_name:
            raise ValueError("display_name is required")
        return await self.repo.create_list(user_id, display_name)
