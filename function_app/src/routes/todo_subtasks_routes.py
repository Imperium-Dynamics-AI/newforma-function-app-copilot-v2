# routes/todo_subtasks_routes.py
"""
Module for registering To-Do subtask routes.
"""

import azure.functions as func

from src.dependencies import get_todo_subtasks_handler


def register_subtasks_routes(app: func.FunctionApp):
    """
    Register HTTP routes for To-Do subtasks.

    Args:
        app (func.FunctionApp): The Azure FunctionApp instance to register routes on.
    """

    @app.function_name(name="create_todo_subtask")
    @app.route(route="todo/subtasks/create", methods=["POST"])
    async def create_subtask(req: func.HttpRequest) -> func.HttpResponse:
        """Handle POST /todo/subtasks/create."""
        handler = get_todo_subtasks_handler()
        return await handler.create_subtask(req)

    @app.function_name(name="get_todo_subtasks")
    @app.route(route="todo/subtasks", methods=["GET"])
    async def get_subtasks(req: func.HttpRequest) -> func.HttpResponse:
        """Handle GET /todo/subtasks?task_id=...&user_email=..."""
        handler = get_todo_subtasks_handler()
        return await handler.get_subtasks(req)

    @app.function_name(name="edit_todo_subtask")
    @app.route(route="todo/subtasks/edit", methods=["PUT"])
    async def edit_subtask(req: func.HttpRequest) -> func.HttpResponse:
        """Handle PUT /todo/subtasks/edit."""
        handler = get_todo_subtasks_handler()
        return await handler.edit_subtask(req)

    @app.function_name(name="delete_todo_subtask")
    @app.route(route="todo/subtasks/delete", methods=["DELETE"])
    async def delete_subtask(req: func.HttpRequest) -> func.HttpResponse:
        """Handle DELETE /todo/subtasks/delete."""
        handler = get_todo_subtasks_handler()
        return await handler.delete_subtask(req)
