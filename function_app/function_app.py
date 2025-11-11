# function_app.py

import azure.functions as func
from src.routes.todo_routes import register_todo_routes

app = func.FunctionApp()

# Register all routes
register_todo_routes(app)
