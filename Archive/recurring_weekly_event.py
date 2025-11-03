import json
import logging
import requests
from constants import GRAPH_API_URL
from utils import get_access_token, get_user_id_by_email, parse_time
import azure.functions as func


def weeklyRecurringEvents(req: func.HttpRequest) -> func.HttpResponse:
    try:
        req_body = req.get_json()
        email = req_body.get("email")
        subject = req_body.get("subject")
        description = req_body.get("description")
        startDate = req_body.get("startDate")  # Date in YYYY-MM-DD format
        start_time = req_body.get("startTime")  # Start time in HH:MM format
        end_time = req_body.get("endTime")  # End time in HH:MM format
        interval = req_body.get("interval", 1)
        days_of_week = req_body.get("daysOfWeek", ["Monday"])  # Default to Monday
        location = req_body.get("location", "online")
        end_date = req_body.get("endDate")
        timezone = req_body.get("timezone")

        if not all(
            [email, subject, description, startDate, start_time, end_time, end_date,timezone]
        ):
            return func.HttpResponse(
                "false",
                status_code=200,
            )

        # Get access token and user ID
        access_token = get_access_token()
        user_id = get_user_id_by_email(email, access_token)
        if not user_id:
            return func.HttpResponse("User not found.", status_code=404)

        # Convert start and end times to ISO 8601 format
        start_datetime = parse_time(startDate, start_time)
        end_datetime = parse_time(startDate, end_time)

        # Prepare event data
        event_data = {
            "subject": subject,
            "body": {"contentType": "HTML", "content": description},
            "start": {"dateTime": start_datetime, "timeZone": timezone},
            "end": {"dateTime": end_datetime, "timeZone": timezone},
            "recurrence": {
                "pattern": {
                    "type": "weekly",
                    "interval": interval,
                    "daysOfWeek": [day.capitalize() for day in days_of_week],
                },
                "range": {
                    "type": "endDate",
                    "startDate": startDate,
                    "endDate": end_date,
                },
            },
            "location": {"displayName": location},
        }

        # Create event
        url = f"{GRAPH_API_URL}/users/{user_id}/events"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        response = requests.post(url, headers=headers, data=json.dumps(event_data))
        if response.status_code == 201:
            return func.HttpResponse("Event created successfully.", status_code=200)
        else:
            logging.error(
                f"Error creating event: {response.status_code} - {response.text}"
            )
            return func.HttpResponse(
                "false",
                status_code=200,
            )

    except Exception as e:
        logging.error(f"Error processing request: {str(e)}")
        return func.HttpResponse(f"Internal Server Error: {str(e)}", status_code=500)
