import azure.functions as func
from src.handlers.todo_handler import TodoHandler
import json

app = func.FunctionApp()
todo_handler = TodoHandler()


@app.function_name(name="create_todo")
@app.route(route="create_todo", methods=["POST"])
async def create_todo(req: func.HttpRequest) -> func.HttpResponse:
    response, status_code = await todo_handler.handle_create_todo_request(req)
    return func.HttpResponse(
        json.dumps(response),
        status_code=status_code,
        mimetype="application/json"
    )
