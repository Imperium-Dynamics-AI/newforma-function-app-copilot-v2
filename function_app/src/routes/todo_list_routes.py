# routes/todo_lists_routes.py
"""
Module for registering To-Do list routes.
"""

import azure.functions as func

from src.handlers.todo_lists_handler import TodoListsHandler


def register_lists_routes(app: func.FunctionApp):
    """
    Register HTTP routes for To-Do lists.

    Args:
        app (func.FunctionApp): The Azure FunctionApp instance to register routes on.
    """

    # Create a new To-Do list
    @app.function_name(name="create_todo_list")
    @app.route(route="todo/lists/create", methods=["POST"])
    async def create_list(req: func.HttpRequest) -> func.HttpResponse:
        """Handle POST /todo/lists/create."""
        return await TodoListsHandler().create_list(req)

    # Get all To-Do lists
    @app.function_name(name="get_todo_lists")
    @app.route(route="todo/lists", methods=["GET"])
    async def get_lists(req: func.HttpRequest) -> func.HttpResponse:
        """Handle GET /todo/lists?user_email=..."""
        return await TodoListsHandler().get_lists(req)

    # Edit a To-Do list name
    @app.function_name(name="edit_todo_list")
    @app.route(route="todo/lists/edit", methods=["PUT"])
    async def edit_list(req: func.HttpRequest) -> func.HttpResponse:
        """Handle PUT /todo/lists/edit."""
        return await TodoListsHandler().edit_list(req)

    # Delete a To-Do list
    @app.function_name(name="delete_todo_list")
    @app.route(route="todo/lists/delete", methods=["DELETE"])
    async def delete_list(req: func.HttpRequest) -> func.HttpResponse:
        """Handle DELETE /todo/lists/delete."""
        return await TodoListsHandler().delete_list(req)
