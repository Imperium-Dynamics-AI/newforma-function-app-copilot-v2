import logging
import requests
import json
from azure.identity import ClientSecretCredential
import azure.functions as func
from utils import (
    get_user_id_by_email,
    get_access_token,
    get_todo_list_id,
    get_task_id_by_name,
    get_subtask_id_by_name,
    decoder,
)
from constants import GRAPH_API_URL


def delete_todo_list(req: func.HttpRequest) -> func.HttpResponse:
    try:
        req_body = req.get_json()
        email = req_body.get("email")
        list_name = req_body.get("listName")
        list_name = decoder(list_name)

        if not all([email, list_name]):
            return func.HttpResponse(
                "false",
                status_code=200,
            )

        access_token = get_access_token()
        user_id = get_user_id_by_email(email, access_token)
        if not user_id:
            return func.HttpResponse(
                "User not found.",
                status_code=404,
                mimetype="application/json",
            )

        list_id = get_todo_list_id(email, list_name)
        if not list_id:
            return func.HttpResponse(
                "false",
                status_code=200,
            )

        # API URL for deleting a To-Do list
        url = f"{GRAPH_API_URL}/users/{user_id}/todo/lists/{list_id}"

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        response = requests.delete(url, headers=headers)

        if response.status_code == 204:
            return func.HttpResponse(
                "To-Do List Deleted Successfully.",
                status_code=200,
            )
        else:
            logging.error(
                f"Error deleting To-Do List: {response.status_code} - {response.text}"
            )
            return func.HttpResponse(
                "false",
                status_code=200,
            )

    except Exception as e:
        logging.error(f"Error processing request: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": f"Internal Server Error: {str(e)}"}),
            status_code=500,
            mimetype="application/json",
        )


def delete_task(req: func.HttpRequest) -> func.HttpResponse:
    try:
        req_body = req.get_json()
        email = req_body.get("email")
        list_name = req_body.get("listName")
        task_name = req_body.get("taskName")
        task_name = decoder(task_name)

        if not all([email, list_name, task_name]):
            return func.HttpResponse(
                "false",
                status_code=200,
            )

        access_token = get_access_token()
        user_id = get_user_id_by_email(email, access_token)
        if not user_id:
            return func.HttpResponse(
                "User not found.",
                status_code=404,
            )

        list_id = get_todo_list_id(email, list_name)
        if not list_id:
            return func.HttpResponse(
                "false",
                status_code=200,
            )

        task_id = get_task_id_by_name(email, list_id, task_name)
        if not task_id:
            return func.HttpResponse(
                "false",
                status_code=200,
            )

        # API URL for deleting a task
        url = f"{GRAPH_API_URL}/users/{user_id}/todo/lists/{list_id}/tasks/{task_id}"

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        response = requests.delete(url, headers=headers)

        if response.status_code == 204:
            return func.HttpResponse(
                "Task Deleted Successfully.",
                status_code=200,
            )
        else:
            logging.error(
                f"Error deleting task: {response.status_code} - {response.text}"
            )
            return func.HttpResponse(
                "false",
                status_code=200,
            )

    except Exception as e:
        logging.error(f"Error processing request: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": f"Internal Server Error: {str(e)}"}),
            status_code=500,
            mimetype="application/json",
        )


def delete_subtask(req: func.HttpRequest) -> func.HttpResponse:
    try:
        req_body = req.get_json()
        email = req_body.get("email")
        list_name = req_body.get("listName")
        task_name = req_body.get("taskName")
        subtask_name = req_body.get("subtaskName")

        if not all([email, list_name, task_name, subtask_name]):
            return func.HttpResponse(
                "false",
                status_code=200,
            )

        access_token = get_access_token()
        user_id = get_user_id_by_email(email, access_token)
        if not user_id:
            return func.HttpResponse(
                "User not found.",
                status_code=404,
            )

        list_id = get_todo_list_id(email, list_name)
        if not list_id:
            return func.HttpResponse(
                "false",
                status_code=200,
            )

        task_id = get_task_id_by_name(email, list_id, task_name)
        if not task_id:
            return func.HttpResponse(
                "false",
                status_code=200,
            )

        subtask_id = get_subtask_id_by_name(email, list_id, task_id, subtask_name)
        if not subtask_id:
            return func.HttpResponse(
                "false",
                status_code=200,
            )

        # API URL for deleting a subtask
        url = f"{GRAPH_API_URL}/users/{user_id}/todo/lists/{list_id}/tasks/{task_id}/checklistItems/{subtask_id}"

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        response = requests.delete(url, headers=headers)

        if response.status_code == 204:
            return func.HttpResponse(
                "Subtask Deleted Successfully.",
                status_code=200,
            )
        else:
            logging.error(
                f"Error deleting subtask: {response.status_code} - {response.text}"
            )
            return func.HttpResponse(
                "false",
                status_code=200,
            )

    except Exception as e:
        logging.error(f"Error processing request: {str(e)}")
        return func.HttpResponse(
            "error: Internal Server Error: {str(e)}",
            status_code=500,
        )
