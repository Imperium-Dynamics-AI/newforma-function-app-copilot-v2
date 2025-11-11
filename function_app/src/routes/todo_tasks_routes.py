# routes/todo_tasks_routes.py
"""
Module for registering To-Do task routes.
"""

import azure.functions as func

from src.handlers.todo_tasks_handler import TodoTasksHandler


def register_tasks_routes(app: func.FunctionApp):
    """
    Register HTTP routes for To-Do tasks.

    Args:
        app (func.FunctionApp): The Azure FunctionApp instance to register routes on.
    """

    # Create a new task
    @app.function_name(name="create_todo_task")
    @app.route(route="todo/tasks/create", methods=["POST"])
    async def create_task(req: func.HttpRequest) -> func.HttpResponse:
        """Handle POST /todo/tasks/create."""
        return await TodoTasksHandler().create_task(req)

    # Get all tasks in a list
    @app.function_name(name="get_todo_tasks")
    @app.route(route="todo/tasks", methods=["GET"])
    async def get_tasks(req: func.HttpRequest) -> func.HttpResponse:
        """Handle GET /todo/tasks?list_id=...&user_email=..."""
        return await TodoTasksHandler().get_tasks(req)

    # Edit a task title
    @app.function_name(name="edit_todo_task")
    @app.route(route="todo/tasks/edit", methods=["PUT"])
    async def edit_task(req: func.HttpRequest) -> func.HttpResponse:
        """Handle PUT /todo/tasks/edit."""
        return await TodoTasksHandler().edit_task(req)

    # Update task status
    @app.function_name(name="update_task_status")
    @app.route(route="todo/tasks/update/status", methods=["PUT"])
    async def update_status(req: func.HttpRequest) -> func.HttpResponse:
        """Handle PUT /todo/tasks/update/status."""
        return await TodoTasksHandler().update_status(req)

    # Update task description
    @app.function_name(name="update_task_description")
    @app.route(route="todo/tasks/update/description", methods=["PUT"])
    async def update_description(req: func.HttpRequest) -> func.HttpResponse:
        """Handle PUT /todo/tasks/update/description."""
        return await TodoTasksHandler().update_description(req)

    # Update task due date
    @app.function_name(name="update_task_duedate")
    @app.route(route="todo/tasks/update/duedate", methods=["PUT"])
    async def update_duedate(req: func.HttpRequest) -> func.HttpResponse:
        """Handle PUT /todo/tasks/update/duedate."""
        return await TodoTasksHandler().update_duedate(req)

    # Delete a task
    @app.function_name(name="delete_todo_task")
    @app.route(route="todo/tasks/delete", methods=["DELETE"])
    async def delete_task(req: func.HttpRequest) -> func.HttpResponse:
        """Handle DELETE /todo/tasks/delete."""
        return await TodoTasksHandler().delete_task(req)
