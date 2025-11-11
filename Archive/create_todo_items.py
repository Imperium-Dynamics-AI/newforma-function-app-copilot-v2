import json
import logging

import azure.functions as func
import requests
from fetch_todo_items import get_task_titles_in_list, get_todo_lists
from utils import (
    get_access_token,
    get_task_id_by_name,
    get_todo_list_id,
    get_user_id_by_email,
)
from fetch_todo_items import get_todo_lists, get_task_titles_in_list


# Function to create a todo list


def createTodoList(req: func.HttpRequest) -> func.HttpResponse:
    try:
        req_body = req.get_json()
        email = req_body.get("email")
        list_name = req_body.get("listName")

        if not all([email, list_name]):
            return func.HttpResponse("false", status_code=200)

        access_token = get_access_token()
        user_id = get_user_id_by_email(email, access_token)
        if not user_id:
            return func.HttpResponse("User not found.", status_code=404)

        # ----- NEW: Check for an existing To-Do list with the same name -----
        # Reuse the get_todo_lists function to fetch current lists.
        lists_response = get_todo_lists(req)
        if lists_response.status_code == 200:
            lists_body = lists_response.get_body()
            # Ensure we work with a string
            if isinstance(lists_body, bytes):
                lists_text = lists_body.decode("utf-8")
            else:
                lists_text = lists_body

            # Each list is expected to be on a new line prefixed with "- "
            existing_lists = []
            for line in lists_text.splitlines():
                line = line.strip()
                if line.startswith("- "):
                    existing_lists.append(line[2:].strip())

            # Check (case-insensitively) if the list name already exists.
            if any(
                list_name.lower() == existing.lower() for existing in existing_lists
            ):
                return func.HttpResponse("false", status_code=200)
        else:
            logging.error("Error retrieving existing To-Do lists.")
            return func.HttpResponse(
                "Error checking existing To-Do lists.", status_code=500
            )
        # ---------------------------------------------------------------------

        # API URL for creating a To-Do list
        GRAPH_API_URL = "https://graph.microsoft.com/v1.0"
        url = f"{GRAPH_API_URL}/users/{user_id}/todo/lists"

        # Request payload
        list_data = {"displayName": list_name}

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        response = requests.post(url, headers=headers, json=list_data)

        if response.status_code == 201:
            return func.HttpResponse(
                "To-Do List Created Successfully.", status_code=201
            )
        else:
            logging.error(
                f"Error creating To-Do list: {response.status_code} - {response.text}"
            )
            return func.HttpResponse("false", status_code=200)

    except Exception as e:
        logging.error(f"Error processing request: {str(e)}")
        return func.HttpResponse(f"Internal Server Error: {str(e)}", status_code=500)


# Function to create tasks within an existing list
def createTodoTask(req: func.HttpRequest) -> func.HttpResponse:
    try:
        req_body = req.get_json()
        email = req_body.get("email")
        list_name = req_body.get("listName")
        task_title = req_body.get("taskName")
        task_content = req_body.get("taskContent")
        due_date = req_body.get("dueDate")  # Expected in YYYY-MM-DD format
        timezone = req_body.get("timezone")
        
        # Validate required fields.
        if not all([email, list_name, task_title, task_content, due_date, timezone]):
            return func.HttpResponse("false", status_code=200)

        access_token = get_access_token()
        user_id = get_user_id_by_email(email, access_token)
        if not user_id:
            return func.HttpResponse("User not found.", status_code=404)

        list_id = get_todo_list_id(email, list_name)
        if not list_id:
            return func.HttpResponse("false", status_code=200)

        # ----- NEW: Check for an existing task with the same title in the list -----
        tasks_response = get_task_titles_in_list(req)
        if tasks_response.status_code == 200:
            tasks_body = tasks_response.get_body()
            # Decode the response body if it is in bytes.
            if isinstance(tasks_body, bytes):
                tasks_text = tasks_body.decode("utf-8")
            else:
                tasks_text = tasks_body

            # Each task title is expected to be on a new line prefixed with "- "
            existing_titles = []
            for line in tasks_text.splitlines():
                line = line.strip()
                if line.startswith("- "):
                    existing_titles.append(line[2:].strip())

            # Check if a task with the same title (case-insensitive) already exists.
            if any(task_title.lower() == title.lower() for title in existing_titles):
                return func.HttpResponse("false", status_code=200)
        else:
            logging.error("Error retrieving existing tasks.")
            return func.HttpResponse("Error checking existing tasks.", status_code=500)
        # ---------------------------------------------------------------------

        # API URL for creating a To-Do task
        GRAPH_API_URL = "https://graph.microsoft.com/v1.0"
        url = f"{GRAPH_API_URL}/users/{user_id}/todo/lists/{list_id}/tasks"

        # Convert due date to ISO 8601 format with time set to 23:59
        due_datetime = f"{due_date}T23:59:00"

        # Request payload for the new task
        task_data = {
            "title": task_title,
            "body": {"content": task_content, "contentType": "text"},
            "dueDateTime": {"dateTime": due_datetime, "timeZone": timezone},
        }

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        response = requests.post(url, headers=headers, json=task_data)

        if response.status_code == 201:
            return func.HttpResponse(
                "To-Do Task Created Successfully.", status_code=200
            )
        else:
            logging.error(
                f"Error creating To-Do task: {response.status_code} - {response.text}"
            )
            return func.HttpResponse("false", status_code=200)

    except Exception as e:
        logging.error(f"Error processing request: {str(e)}")
        return func.HttpResponse(f"Internal Server Error: {str(e)}", status_code=500)


# Function to create subtasks in a task within an existing list
def create_subtask(req: func.HttpRequest) -> func.HttpResponse:
    try:
        req_body = req.get_json()
        email = req_body.get("email")
        list_name = req_body.get("listName")
        task_name = req_body.get("taskName")
        subtask_title = req_body.get("subtaskName")

        if not all([email, list_name, task_name, subtask_title]):
            return func.HttpResponse(
                "false",
                status_code=200,
            )

        access_token = get_access_token()
        user_id = get_user_id_by_email(email, access_token)
        if not user_id:
            return func.HttpResponse("User not found.", status_code=404)

        list_id = get_todo_list_id(email, list_name)
        if not list_id:
            return func.HttpResponse("false", status_code=200)

        task_id = get_task_id_by_name(email, list_id, task_name)
        if not task_id:
            return func.HttpResponse("false", status_code=200)

        # API URL for creating a subtask
        GRAPH_API_URL = "https://graph.microsoft.com/v1.0"
        url = f"{GRAPH_API_URL}/users/{user_id}/todo/lists/{list_id}/tasks/{task_id}/checklistItems"

        # Request payload
        subtask_data = {"displayName": subtask_title}

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        response = requests.post(url, headers=headers, json=subtask_data)

        if response.status_code == 201:
            return func.HttpResponse("Subtask Created Successfully.", status_code=201)
        else:
            logging.error(
                f"Error creating subtask: {response.status_code} - {response.text}"
            )
            return func.HttpResponse("false", status_code=200)

    except Exception as e:
        logging.error(f"Error processing request: {str(e)}")
        return func.HttpResponse(f"Internal Server Error: {str(e)}", status_code=500)
