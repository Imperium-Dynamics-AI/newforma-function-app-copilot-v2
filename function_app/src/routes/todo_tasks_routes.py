# routes/todo_tasks_routes.py
"""
Module for registering To-Do task routes.
"""

import azure.functions as func

from src.dependencies import get_todo_tasks_handler


def register_tasks_routes(app: func.FunctionApp):
    """
    Register HTTP routes for To-Do tasks.

    Args:
        app (func.FunctionApp): The Azure FunctionApp instance to register routes on.
    """

    @app.function_name(name="create_todo_task")
    @app.route(route="todo/tasks/create", methods=["POST"])
    async def create_task(req: func.HttpRequest) -> func.HttpResponse:
        """Handle POST /todo/tasks/create."""
        handler = get_todo_tasks_handler()
        return await handler.create_task(req)

    @app.function_name(name="get_todo_tasks")
    @app.route(route="todo/tasks", methods=["GET"])
    async def get_tasks(req: func.HttpRequest) -> func.HttpResponse:
        """Handle GET /todo/tasks?list_id=...&user_email=..."""
        handler = get_todo_tasks_handler()
        return await handler.get_tasks(req)

    @app.function_name(name="edit_todo_task")
    @app.route(route="todo/tasks/edit", methods=["PUT"])
    async def edit_task(req: func.HttpRequest) -> func.HttpResponse:
        """Handle PUT /todo/tasks/edit."""
        handler = get_todo_tasks_handler()
        return await handler.edit_task(req)

    @app.function_name(name="delete_todo_task")
    @app.route(route="todo/tasks/delete", methods=["DELETE"])
    async def delete_task(req: func.HttpRequest) -> func.HttpResponse:
        """Handle DELETE /todo/tasks/delete."""
        handler = get_todo_tasks_handler()
        return await handler.delete_task(req)
