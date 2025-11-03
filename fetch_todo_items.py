import logging
import requests
from azure.identity import ClientSecretCredential
import azure.functions as func
from utils import (
    get_user_id_by_email,
    get_access_token,
    get_todo_list_id,
    get_task_id_by_name,
    decoder,
)
from constants import GRAPH_API_URL

def get_todo_lists(req: func.HttpRequest) -> func.HttpResponse:
    try:
        req_body = req.get_json()
        email = req_body.get("email")

        if not email:
            return func.HttpResponse("false", status_code=200)

        access_token = get_access_token()
        user_id = get_user_id_by_email(email, access_token)
        if not user_id:
            return func.HttpResponse("User not found.", status_code=404)

        url = f"{GRAPH_API_URL}/users/{user_id}/todo/lists"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            lists = response.json().get("value", [])
            list_titles = "\n".join(f"- {lst['displayName']}" for lst in lists)
            return func.HttpResponse(list_titles, status_code=200)
        else:
            logging.error(
                f"Error retrieving lists: {response.status_code} - {response.text}"
            )
            return func.HttpResponse(
                "false", status_code=200
            )

    except Exception as e:
        logging.error(f"Error processing request: {str(e)}")
        return func.HttpResponse(f"Internal Server Error: {str(e)}", status_code=500)


def get_task_titles_in_list(req: func.HttpRequest) -> func.HttpResponse:
    try:
        req_body = req.get_json()
        email = req_body.get("email")
        list_name = req_body.get("listName")
        list_name = decoder(list_name)
        list_id = get_todo_list_id(email, list_name)
        if not email or not list_id:
            return func.HttpResponse(
                "false", status_code=200
            )

        access_token = get_access_token()
        user_id = get_user_id_by_email(email, access_token)
        if not user_id:
            return func.HttpResponse("User not found.", status_code=404)

        url = f"{GRAPH_API_URL}/users/{user_id}/todo/lists/{list_id}/tasks"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            tasks = response.json().get("value", [])
            task_titles = "\n".join(f'- {task["title"]}' for task in tasks)
            return func.HttpResponse(task_titles, status_code=200)
        else:
            logging.error(
                f"Error retrieving tasks: {response.status_code} - {response.text}"
            )
            return func.HttpResponse(
                "false", status_code=200
            )

    except Exception as e:
        logging.error(f"Error processing request: {str(e)}")
        return func.HttpResponse(f"Internal Server Error: {str(e)}", status_code=500)


def get_subtasks(req: func.HttpRequest) -> func.HttpResponse:
    try:
        req_body = req.get_json()
        email = req_body.get("email")
        list_name = req_body.get("listName")
        task_name = req_body.get("taskName")

        if not all([email, list_name, task_name]):
            return func.HttpResponse(
                "false", status_code=200
            )

        access_token = get_access_token()
        user_id = get_user_id_by_email(email, access_token)
        if not user_id:
            return func.HttpResponse("User not found.", status_code=404)

        list_id = get_todo_list_id(email, list_name)
        if not list_id:
            return func.HttpResponse("To-Do List not found.", status_code=404)

        task_id = get_task_id_by_name(email, list_id, task_name)
        if not task_id:
            return func.HttpResponse(                
                "false",
                status_code=200,)

        url = f"{GRAPH_API_URL}/users/{user_id}/todo/lists/{list_id}/tasks/{task_id}/checklistItems"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            subtasks = response.json().get("value", [])
            subtask_titles = "\n".join(f'- {subtask["displayName"]}' for subtask in subtasks)
            return func.HttpResponse(subtask_titles, status_code=200)
        else:
            logging.error(
                f"Error retrieving subtasks: {response.status_code} - {response.text}"
            )
            return func.HttpResponse(
                "false", status_code=200
            )

    except Exception as e:
        logging.error(f"Error processing request: {str(e)}")
        return func.HttpResponse(f"Internal Server Error: {str(e)}", status_code=500)

