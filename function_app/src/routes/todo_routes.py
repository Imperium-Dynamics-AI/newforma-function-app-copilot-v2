# src/routes/todo_routes.py

import json

import azure.functions as func
from src.handlers.todo_handler import TodoHandler

todo_handler = TodoHandler()


def register_todo_routes(app: func.FunctionApp):

    @app.function_name(name="create_todo")
    @app.route(route="create_todo", methods=["POST"])
    async def create_todo(req: func.HttpRequest) -> func.HttpResponse:
        response, status_code = await todo_handler.handle_create_todo_request(req)
        return func.HttpResponse(
            json.dumps(response), status_code=status_code, mimetype="application/json"
        )
    

    @app.function_name(name="fetch_todo")
    @app.route(route="fetch_todo", methods=["POST"])  # Using POST for now (could also be GET)
    async def fetch_todo(req: func.HttpRequest) -> func.HttpResponse:
        response, status_code = await todo_handler.handle_fetch_todo_request(req)
        return func.HttpResponse(
            json.dumps(response), status_code=status_code, mimetype="application/json"
        )
