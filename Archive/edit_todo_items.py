import logging
import requests
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


def edit_todo_list_name(req: func.HttpRequest) -> func.HttpResponse:
    try:
        req_body = req.get_json()
        email = req_body.get("email")
        old_list_name = req_body.get("oldListName")
        old_list_name = decoder(old_list_name)
        new_list_name = req_body.get("newListName")

        if not all([email, old_list_name, new_list_name]):
            return func.HttpResponse(
                "false",
                status_code=200,
            )

        access_token = get_access_token()
        user_id = get_user_id_by_email(email, access_token)
        if not user_id:
            return func.HttpResponse("User not found.", status_code=404)

        list_id = get_todo_list_id(email, old_list_name)
        if not list_id:
            return func.HttpResponse("false", status_code=200)

        # API URL for updating a To-Do list name
        url = f"{GRAPH_API_URL}/users/{user_id}/todo/lists/{list_id}"

        # Request payload
        update_data = {"displayName": new_list_name}

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        response = requests.patch(url, headers=headers, json=update_data)

        if response.status_code == 200:
            return func.HttpResponse(
                "To-Do List Name Updated Successfully.", status_code=200
            )
        else:
            logging.error(
                f"Error updating To-Do List name: {response.status_code} - {response.text}"
            )
            return func.HttpResponse("false", status_code=200)

    except Exception as e:
        logging.error(f"Error processing request: {str(e)}")
        return func.HttpResponse(f"Internal Server Error: {str(e)}", status_code=500)


def edit_task_title(req: func.HttpRequest) -> func.HttpResponse:
    try:
        req_body = req.get_json()
        email = req_body.get("email")
        list_name = req_body.get("listName")
        list_name = decoder(list_name)

        old_task_title = req_body.get("oldTaskName")
        old_task_title = decoder(old_task_title)
        new_task_title = req_body.get("newTaskName")

        if not all([email, list_name, old_task_title, new_task_title]):
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
            return func.HttpResponse(
                "false",
                status_code=200,
            )

        task_id = get_task_id_by_name(email, list_id, old_task_title)
        if not task_id:
            return func.HttpResponse(
                "false",
                status_code=200,
            )

        # API URL for updating a task title
        url = f"{GRAPH_API_URL}/users/{user_id}/todo/lists/{list_id}/tasks/{task_id}"

        # Request payload
        update_data = {"title": new_task_title}

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        response = requests.patch(url, headers=headers, json=update_data)

        if response.status_code == 200:
            return func.HttpResponse(
                "Task Title Updated Successfully.", status_code=200
            )
        else:
            logging.error(
                f"Error updating Task title: {response.status_code} - {response.text}"
            )
            return func.HttpResponse(
                "false",
                status_code=200,
            )

    except Exception as e:
        logging.error(f"Error processing request: {str(e)}")
        return func.HttpResponse(f"Internal Server Error: {str(e)}", status_code=500)


def edit_subtask_title(req: func.HttpRequest) -> func.HttpResponse:
    try:
        req_body = req.get_json()
        email = req_body.get("email")
        list_name = req_body.get("listName")
        task_name = req_body.get("taskName")
        old_subtask_title = decoder("oldSubtaskTitle")
        new_subtask_title = req_body.get("newSubtaskName")

        if not all([email, list_name, task_name, old_subtask_title, new_subtask_title]):
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

        subtask_id = get_subtask_id_by_name(email, list_id, task_id, old_subtask_title)
        if not subtask_id:
            return func.HttpResponse(
                "false",
                status_code=200,
            )

        # API URL for updating a subtask title
        url = f"{GRAPH_API_URL}/users/{user_id}/todo/lists/{list_id}/tasks/{task_id}/checklistItems/{subtask_id}"

        # Request payload
        update_data = {"displayName": new_subtask_title}

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        response = requests.patch(url, headers=headers, json=update_data)

        if response.status_code == 200:
            return func.HttpResponse(
                "Subtask Title Updated Successfully.", status_code=200
            )
        else:
            logging.error(
                f"Error updating Subtask title: {response.status_code} - {response.text}"
            )
            return func.HttpResponse(
                "false",
                status_code=200,
            )

    except Exception as e:
        logging.error(f"Error processing request: {str(e)}")
        return func.HttpResponse(f"Internal Server Error: {str(e)}", status_code=500)


def update_task_status(req: func.HttpRequest) -> func.HttpResponse:
    try:
        req_body = req.get_json()
        email = req_body.get("email")
        list_name = req_body.get("listName")
        list_name = decoder(list_name)
        task_name = req_body.get("taskName")
        task_name = decoder(task_name)
        status = req_body.get(
            "status"
        )  # Expected values: 'notStarted', 'inProgress', 'completed'

        if not all([email, list_name, task_name, status]):
            return func.HttpResponse(
                "false",
                status_code=200,
            )

        if status not in ["notStarted", "inProgress", "completed"]:  # Tell Usman smth
            return func.HttpResponse(
                "Invalid status value. Allowed values: 'notStarted', 'inProgress', 'completed'",
                status_code=400,
            )

        access_token = get_access_token()
        user_id = get_user_id_by_email(email, access_token)
        if not user_id:
            return func.HttpResponse("User not found.", status_code=404)

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

        # API URL for updating a task status
        url = f"{GRAPH_API_URL}/users/{user_id}/todo/lists/{list_id}/tasks/{task_id}"

        # Request payload
        update_data = {"status": status}

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        response = requests.patch(url, headers=headers, json=update_data)

        if response.status_code == 200:
            return func.HttpResponse(
                "Task Status Updated Successfully.", status_code=200
            )
        else:
            logging.error(
                f"Error updating Task status: {response.status_code} - {response.text}"
            )
            return func.HttpResponse(
                "false",
                status_code=200,
            )

    except Exception as e:
        logging.error(f"Error processing request: {str(e)}")
        return func.HttpResponse(f"Internal Server Error: {str(e)}", status_code=500)


def update_task_description(req: func.HttpRequest) -> func.HttpResponse:
    try:
        req_body = req.get_json()
        email = req_body.get("email")
        list_name = req_body.get("listName")
        list_name = decoder(list_name)
        task_name = req_body.get("taskName")
        task_name = decoder(task_name)
        description = req_body.get("description")

        if not all([email, list_name, task_name, description]):
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

        # API URL for updating a task description
        url = f"{GRAPH_API_URL}/users/{user_id}/todo/lists/{list_id}/tasks/{task_id}"

        # Request payload
        update_data = {"body": {"content": description, "contentType": "text"}}

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        response = requests.patch(url, headers=headers, json=update_data)

        if response.status_code == 200:
            return func.HttpResponse(
                "Task Description Updated Successfully.", status_code=200
            )
        else:
            logging.error(
                f"Error updating Task description: {response.status_code} - {response.text}"
            )
            return func.HttpResponse(
                "false",
                status_code=200,
            )

    except Exception as e:
        logging.error(f"Error processing request: {str(e)}")
        return func.HttpResponse(f"Internal Server Error: {str(e)}", status_code=500)


def update_duedate(req: func.HttpRequest) -> func.HttpResponse:
    try:
        req_body = req.get_json()
        email = req_body.get("email")
        list_name = req_body.get("listName")
        list_name = decoder(list_name)
        task_name = req_body.get("taskName")
        task_name = decoder(task_name)

        due_date = req_body.get("dueDate")
        timezone = req_body.get("timezone")

        if not all([email, list_name, task_name, due_date, timezone]):
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

        # API URL for updating a task description
        url = f"{GRAPH_API_URL}/users/{user_id}/todo/lists/{list_id}/tasks/{task_id}"
        due_datetime = f"{due_date}T23:59:00"

        # Request payload
        task_data = {
            "dueDateTime": {"dateTime": due_datetime, "timeZone": timezone},
        }

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        response = requests.patch(url, headers=headers, json=task_data)

        if response.status_code == 200:
            return func.HttpResponse(
                "Task Description Updated Successfully.", status_code=200
            )
        else:
            logging.error(
                f"Error updating Task description: {response.status_code} - {response.text}"
            )
            return func.HttpResponse(
                "false",
                status_code=200,
            )

    except Exception as e:
        logging.error(f"Error processing request: {str(e)}")
        return func.HttpResponse(f"Internal Server Error: {str(e)}", status_code=500)
