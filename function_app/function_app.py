"""
This module defines the Azure Function App and routes HTTP requests to the appropriate handlers.
"""

import azure.functions as func
from src.routes import todo_routes

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

todo_routes.register(app)
