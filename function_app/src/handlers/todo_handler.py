import logging
from src.managers.todo_manager import TodoManager

class TodoHandler:
    def __init__(self):
        self.manager = TodoManager()

    async def handle_create_todo_request(self, req):
        logging.info("Processing create_todo request...")

        try:
            req_body = req.get_json()
        except ValueError:
            return {"error": "Invalid JSON payload"}, 400

        # Basic manual validation
        user_email = req_body.get("user_email")
        list_name = req_body.get("list_name")

        if not user_email or not list_name:
            return {"error": "Both 'user_email' and 'list_name' are required."}, 400

        # Pass to manager
        result = await self.manager.create_list(user_email, list_name)

        if "error" in result:
            return result, 400

        return result, 200
