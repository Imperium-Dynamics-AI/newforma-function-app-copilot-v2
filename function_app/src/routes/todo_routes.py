# routes/todo_routes.py
"""
Module for registering all To-Do routes in the Azure Function App.
"""

import azure.functions as func

from src.routes.todo_list_routes import register_lists_routes
from src.routes.todo_subtasks_routes import register_subtasks_routes
from src.routes.todo_tasks_routes import register_tasks_routes


def register(app: func.FunctionApp):
    """
    Register all HTTP routes for the To-Do application with the Azure FunctionApp instance.

    Args:
        app (func.FunctionApp): The Azure FunctionApp instance to register routes on.
    """
    register_lists_routes(app)
    register_tasks_routes(app)
    register_subtasks_routes(app)
