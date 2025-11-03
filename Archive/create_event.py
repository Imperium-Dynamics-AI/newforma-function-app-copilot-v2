import re
import azure.functions as func
import logging
import requests
import json
import pytz
from azure.identity import ClientSecretCredential
from datetime import datetime, timedelta
from dateutil.parser import parse
from constants import CLIENT_ID, CLIENT_SECRET, TENANT_ID
from utils import getEventTimeByTitle

from utils import decoder

# Microsoft Graph API URL
GRAPH_API_URL = "https://graph.microsoft.com/v1.0"


# Function to get access token using client credentials
def get_access_token():
    credential = ClientSecretCredential(
        tenant_id=TENANT_ID, client_id=CLIENT_ID, client_secret=CLIENT_SECRET
    )
    token = credential.get_token("https://graph.microsoft.com/.default")
    return token.token


# Function to retrieve user ID based on the email
def get_user_id_by_email(email, access_token):
    url = f"{GRAPH_API_URL}/users?$filter=mail eq '{email}'&$select=id"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        users = response.json().get("value", [])
        if users:
            return users[0]["id"]
        else:
            return None
    else:
        logging.error(
            f"Error retrieving user ID: {response.status_code} - {response.text}"
        )
        return None


# Function to preprocess time string
def preprocess_time(time_str):
    time_str = re.sub(r"\bo'clock\b", "", time_str, flags=re.IGNORECASE)
    time_str = time_str.strip()
    return time_str


# Function to parse the time into ISO 8601 format
def parse_time(date, time_str):
    try:
        time_str = preprocess_time(time_str)
        time_parsed = parse(time_str)

        # Handle multiple date formats
        formats = ["%Y-%m-%d", "%m/%d/%Y", "%m-%d-%Y"]
        combined = None

        for fmt in formats:
            try:
                combined = datetime.strptime(date, fmt).replace(
                    hour=time_parsed.hour, minute=time_parsed.minute, second=0, microsecond=0
                )
                break
            except ValueError:
                continue

        if not combined:
            raise ValueError(f"Date format not supported: {date}")

        return combined.strftime("%Y-%m-%dT%H:%M:%S")
    except Exception as e:
        raise ValueError(f"Invalid time or date format: {time_str}, {date}. Error: {str(e)}")


def createEvent(req: func.HttpRequest) -> func.HttpResponse:
    try:
        req_body = req.get_json()
        email = req_body.get("email")
        subject = req_body.get("subject")
        subject = decoder(subject)
        description = req_body.get("description")
        date = req_body.get("date")           # Date in YYYY-MM-DD format
        start_time = req_body.get("startTime")  # Start time in HH:MM format
        end_time = req_body.get("endTime")      # End time in HH:MM format
        time_zone = req_body.get("timezone")    # e.g., "Asia/Karachi" or "America/New_York"

        # Check that all required fields are provided.
        if not all([email, subject, description, date, start_time, end_time, time_zone]):
            return func.HttpResponse("false", status_code=200)

        # ----- NEW: Check for an existing event with the same title and time on the same date -----
        # Use the utility function to fetch the event times (converted to the target timezone)
        existing_event = getEventTimeByTitle(email, date, subject, time_zone)
        if "error" not in existing_event:
            # Convert the user-provided start and end times to ISO format using your parse_time function.
            user_start_iso = parse_time(date, start_time)  # e.g., "2025-02-03 17:00:00"
            user_end_iso = parse_time(date, end_time)      # e.g., "2025-02-03 17:15:00"
            
            # Convert the user times to datetime objects
            user_start_dt = datetime.fromisoformat(user_start_iso)
            user_end_dt = datetime.fromisoformat(user_end_iso)
            
            # If the datetime objects are naive (no tzinfo), attach the provided timezone.
            tz_obj = pytz.timezone(time_zone)
            if user_start_dt.tzinfo is None:
                user_start_dt = tz_obj.localize(user_start_dt)
            if user_end_dt.tzinfo is None:
                user_end_dt = tz_obj.localize(user_end_dt)
            
            # Convert the event times from the utility function into datetime objects.
            existing_start_dt = datetime.fromisoformat(existing_event["start"]["dateTime"])
            existing_end_dt = datetime.fromisoformat(existing_event["end"]["dateTime"])
            
            # Compare the datetimes
            if user_start_dt == existing_start_dt and user_end_dt == existing_end_dt:
                return func.HttpResponse(
                    "false",
                    status_code=200,
                )
        # -----------------------------------------------------------------------------------------

        # Get access token and user ID for creating the event.
        access_token = get_access_token()
        user_id = get_user_id_by_email(email, access_token)
        if not user_id:
            return func.HttpResponse("User not found.", status_code=404)

        # Parse the start and end date-time strings (using your existing utility).
        start_datetime = parse_time(date, start_time)
        end_datetime = parse_time(date, end_time)

        # Prepare the payload for the new event.
        event_data = {
            "subject": subject,
            "start": {"dateTime": start_datetime, "timeZone": time_zone},
            "end": {"dateTime": end_datetime, "timeZone": time_zone},
            "body": {"contentType": "Text", "content": description},
        }

        GRAPH_API_URL = "https://graph.microsoft.com/v1.0"  # Actual GRAPH API URL
        url = f"{GRAPH_API_URL}/users/{user_id}/calendar/events"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        response = requests.post(url, headers=headers, json=event_data)

        if response.status_code == 201:
            return func.HttpResponse("Event Created Successfully.", status_code=201)
        else:
            logging.error(
                f"Error creating event: {response.status_code} - {response.text}"
            )
            return func.HttpResponse("false", status_code=200)

    except Exception as e:
        logging.error(f"Error processing request: {str(e)}")
        return func.HttpResponse(f"Internal Server Error: {str(e)}", status_code=500)

