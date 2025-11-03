import json
import logging
import requests
from constants import GRAPH_API_URL
from utils import get_access_token, get_user_id_by_email, parse_time
import azure.functions as func

def absoluteYearlyRecurringEvents(data) -> func.HttpResponse:
    try:
        # Check if data is an HTTP request (req) or a JSON dictionary
        if isinstance(data, func.HttpRequest):
            req = data
            req_body = req.get_json()
            email = req_body.get("email")
            subject = req_body.get("subject")
            description = req_body.get("description")
            startDate = req_body.get("startDate")
            start_time = req_body.get("startTime")
            end_time = req_body.get("endTime")
            interval = req_body.get("interval", 1)
            absolute_day_of_month = req_body.get("DayofMonth")
            absolute_month = req_body.get("MonthofYear")
            location = req_body.get("location", "Online")
            end_date = req_body.get("endDate")
            timezone = req_body.get("timezone")
        else:
            # If it's a dictionary (JSON format)
            email = data.get("email")
            subject = data.get("subject")
            description = data.get("description")
            startDate = data.get("startDate")
            start_time = data.get("startTime")
            end_time = data.get("endTime")
            interval = data.get("interval", 1)
            absolute_day_of_month = data.get("DayofMonth")
            absolute_month = data.get("MonthofYear")
            location = data.get("location", "Online")
            end_date = data.get("endDate")
            timezone = data.get("timezone")

        # Check if all necessary parameters are present
        if not all([email, subject, description, startDate, start_time, end_time, absolute_day_of_month, absolute_month, end_date, timezone]):
            if isinstance(data, func.HttpRequest):
                return func.HttpResponse("Missing parameters.", status_code=400)
            else:
                return False  # Return False for JSON input if parameters are missing

        # Get access token and user ID
        access_token = get_access_token()
        user_id = get_user_id_by_email(email, access_token)
        if not user_id:
            if isinstance(data, func.HttpRequest):
                return func.HttpResponse("User not found.", status_code=404)
            else:
                return False  # Return False for JSON input if user is not found

        # Convert start and end times to ISO 8601 format
        start_datetime = parse_time(startDate, start_time)
        end_datetime = parse_time(startDate, end_time)
        logging.info(f'start_datetime: {start_datetime}')
        logging.info(f'end_datetime: {end_datetime}')

        # Prepare event data
        event_data = {
            "subject": subject,
            "body": {"contentType": "HTML", "content": description},
            "start": {"dateTime": start_datetime, "timeZone": timezone},
            "end": {"dateTime": end_datetime, "timeZone": timezone},
            "recurrence": {
                "pattern": {
                    "type": "absoluteYearly",
                    "interval": interval,
                    "dayOfMonth": absolute_day_of_month,
                    "month": absolute_month,
                },
                "range": {
                    "type": "endDate",
                    "startDate": startDate,
                    "endDate": end_date,
                },
            },
            "location": {"displayName": location},
        }

        # Log the event data for debugging
        logging.info(f"Event Data: {json.dumps(event_data, indent=2)}")

        # Create event
        url = f"{GRAPH_API_URL}/users/{user_id}/events"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        response = requests.post(url, headers=headers, data=json.dumps(event_data))
        logging.info(f"Response: {response.status_code} - {response.text}")
        if response.status_code == 201:
            if isinstance(data, func.HttpRequest):
                return func.HttpResponse("Event created successfully.", status_code=200)
            else:
                return True  # Return True for JSON input if event is created successfully
        else:
            logging.error(f"Error creating event: {response.status_code} - {response.text}")
            if isinstance(data, func.HttpRequest):
                return func.HttpResponse("Error creating event.", status_code=500)
            else:
                return False  # Return False for JSON input if event creation fails

    except Exception as e:
        logging.error(f"Error processing request: {str(e)}")
        if isinstance(data, func.HttpRequest):
            return func.HttpResponse(f"Internal Server Error: {str(e)}", status_code=500)
        else:
            return False  # Return False for JSON input if an exception occurs
