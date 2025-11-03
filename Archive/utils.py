import logging
import requests
from azure.identity import ClientSecretCredential
from datetime import datetime
from dateutil.parser import parse
import re
import pytz
from fuzzywuzzy import fuzz
from validate_email_address import validate_email
from constants import CLIENT_ID, CLIENT_SECRET, GRAPH_API_URL, TENANT_ID


# Get access token
def get_access_token():
    credential = ClientSecretCredential(
        tenant_id=TENANT_ID, client_id=CLIENT_ID, client_secret=CLIENT_SECRET
    )
    token = credential.get_token("https://graph.microsoft.com/.default")
    return token.token


# Function to retrieve user ID based on the user's email
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


# Function to get user's display name given the email
def get_user_display_name(email):
    try:
        access_token = get_access_token()
        # Microsoft Graph API endpoint for users
        url = f"https://graph.microsoft.com/v1.0/users/{email}"

        # Headers for the API request
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        # Make the API request
        response = requests.get(url, headers=headers)

        # Check if the response is successful
        if response.status_code == 200:
            user_data = response.json()
            return user_data.get("displayName")
        else:
            print(
                f"Failed to fetch user details. Status code: {response.status_code}, Error: {response.text}"
            )
            return None

    except Exception as e:
        print(f"An error occurred while fetching the display name: {e}")
        return None


def fuzzy_match_string(str1, str2):
    # Calculate the similarity ratio
    similarity_ratio = fuzz.ratio(str1, str2)

    # Check if the ratio is greater than or equal to 90%
    if similarity_ratio >= 95:
        return True
    else:
        return False


def getEventID(title, date, email, timezone):
    access_token = get_access_token()
    user_id = get_user_id_by_email(email, access_token)

    # Construct the API URL for calendarView
    url = f"{GRAPH_API_URL}/users/{user_id}/calendarView"

    # Set request headers
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    # Append times to the given date
    date = datetime.strptime(date, "%Y-%m-%d").date()
    startDateTime, endDateTime = convert_timezone(timezone, date)

    # Define query parameters
    params = {
        "startDateTime": startDateTime,
        "endDateTime": endDateTime,
        "$select": "subject,start,end,type,recurrence,seriesMasterId",
        "$orderby": "start/dateTime",
    }

    # Make the GET request
    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        events = response.json().get("value", [])
        for event in events:
            if event.get("seriesMasterId"):
                if fuzzy_match_string(event.get("subject", "").lower(), title.lower()):
                    return event.get("seriesMasterId")
            else:
                if fuzzy_match_string(event.get("subject", "").lower(), title.lower()):
                    return event.get("id")
        return None  # No matching event found
    else:
        print(f"Error: {response.status_code} - {response.text}")
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
                    hour=time_parsed.hour,
                    minute=time_parsed.minute,
                    second=0,
                    microsecond=0,
                )
                break
            except ValueError:
                continue

        if not combined:
            raise ValueError(f"Date format not supported: {date}")

        return combined.strftime("%Y-%m-%dT%H:%M:%S")
    except Exception as e:
        raise ValueError(
            f"Invalid time or date format: {time_str}, {date}. Error: {str(e)}"
        )


# ------------------------------------------TO-DO UTILITY----------------------------------------------


# Function to retrieve To-Do lists ID of a user
def get_todo_list_id(email, list_name):
    access_token = get_access_token()
    user_id = get_user_id_by_email(email, access_token)
    url = f"{GRAPH_API_URL}/users/{user_id}/todo/lists"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        todo_lists = response.json().get("value", [])

        for todo in todo_lists:
            if (
                todo["displayName"].lower() == list_name.lower()
            ):  # Case-insensitive match
                return todo["id"]

        logging.info(f"No To-Do list found with the name '{list_name}'.")
        return None
    else:
        logging.error(
            f"Error retrieving To-Do lists: {response.status_code} - {response.text}"
        )
        return None


# Function to get task ID by task title
def get_task_id_by_name(email, list_id, task_name):
    access_token = get_access_token()
    user_id = get_user_id_by_email(email, access_token)
    url = f"{GRAPH_API_URL}/users/{user_id}/todo/lists/{list_id}/tasks"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        tasks = response.json().get("value", [])

        for task in tasks:
            if task["title"].lower() == task_name.lower():  # Case-insensitive match
                return task["id"]

        logging.info(f"No task found with the name '{task_name}'.")
        return None
    else:
        logging.error(
            f"Error retrieving tasks: {response.status_code} - {response.text}"
        )
        return None


# Function to get subtask ID
def get_subtask_id_by_name(email, list_id, task_id, subtask_name):
    access_token = get_access_token()
    user_id = get_user_id_by_email(email, access_token)
    url = f"{GRAPH_API_URL}/users/{user_id}/todo/lists/{list_id}/tasks/{task_id}/checklistItems"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        subtasks = response.json().get("value", [])

        for subtask in subtasks:
            if (
                subtask["displayName"].lower() == subtask_name.lower()
            ):  # Case-insensitive match
                return subtask["id"]

        logging.info(f"No subtask found with the name '{subtask_name}'.")
        return None
    else:
        logging.error(
            f"Error retrieving subtasks: {response.status_code} - {response.text}"
        )
        return None


def parse_date(date):
    try:
        # Handle multiple date formats
        formats = ["%Y-%m-%d", "%m/%d/%Y", "%m-%d-%Y"]
        parsed_date = None

        for fmt in formats:
            try:
                parsed_date = datetime.strptime(date, fmt)
                break
            except ValueError:
                continue

        if not parsed_date:
            raise ValueError(f"Date format not supported: {date}")

        return parsed_date.strftime("%Y-%m-%d")
    except Exception as e:
        raise ValueError(f"Invalid date format: {date}. Error: {str(e)}")


def parse_email_string(email_string):
    """
    Parses a single string of emails separated by commas and returns a list of cleaned email addresses.

    Args:
        email_string (str): A string containing emails separated by commas.

    Returns:
        list: A list of email addresses as strings.
    """
    try:
        # Split the string by commas and strip any surrounding whitespace
        email_list = [
            email.strip() for email in email_string.split(",") if email.strip()
        ]
        return email_list
    except Exception as e:
        raise ValueError(f"Invalid email string: {email_string}. Error: {str(e)}")


def convert_time(time_obj, target_tz):
    """
    Converts the time in time_obj (which should have 'dateTime' and 'timeZone')
    to the target timezone.
    """
    # Parse the datetime string.
    dt = datetime.fromisoformat(time_obj["dateTime"])

    # Determine the source timezone from the event. Default to UTC if not provided.
    source_tz = pytz.timezone(time_obj.get("timeZone", "UTC"))

    # If the datetime is naive, localize it.
    if dt.tzinfo is None:
        dt = source_tz.localize(dt)

    # Convert the datetime to the target timezone.
    target_tz_obj = pytz.timezone(target_tz)
    converted_dt = dt.astimezone(target_tz_obj)

    return {"dateTime": converted_dt.isoformat(), "timeZone": target_tz}


def getEventTimeByTitle(email, date, title, target_timezone):
    try:
        access_token = get_access_token()
        user_id = get_user_id_by_email(email, access_token)
        if not user_id:
            return {"error": "User not found"}

        # Parse and build the date range for filtering events.
        date = parse_date(date)
        start_datetime = f"{date}T00:00:00"
        end_datetime = f"{date}T23:59:59"

        url = f"{GRAPH_API_URL}/users/{user_id}/events"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }
        params = {
            "$filter": (
                f"start/dateTime ge '{start_datetime}' and start/dateTime le '{end_datetime}' "
                f"and subject eq '{title}'"
            ),
            "$select": "start,end",
        }

        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            events = response.json().get("value", [])
            if events:
                # Retrieve the original start and end time objects.
                start_time_obj = events[0].get("start")
                end_time_obj = events[0].get("end")

                converted_start = convert_time(start_time_obj, target_timezone)
                converted_end = convert_time(end_time_obj, target_timezone)
                return {"start": converted_start, "end": converted_end}
            return {"error": "Event not found"}
        else:
            logging.error(
                f"Error fetching event time: {response.status_code} - {response.text}"
            )
            return {"error": "Failed to fetch event time"}

    except Exception as e:
        logging.error(f"Error processing request: {str(e)}")
        return {"error": f"Internal Server Error: {str(e)}"}


def check_email(email):
    is_valid = validate_email(email)  # verify=True performs an SMTP check
    return is_valid  # True or False


def getEventAttendees(email, date, title, timezone):
    try:
        # Step 1: Get access token
        access_token = get_access_token()

        # Step 2: Get user ID
        user_id = get_user_id_by_email(email, access_token)
        if not user_id:
            return {"error": "User not found"}

        # Step 3: Parse and build the date range for filtering events.
        # date = parse_date(date)
        # start_datetime = f"{date}T00:00:00"
        # end_datetime = f"{date}T23:59:59"
        eventID = getEventID(title, date, email, timezone)
        print(eventID)
        url = f"{GRAPH_API_URL}/users/{user_id}/events/{eventID}"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            attendees = response.json().get("attendees", [])
            if attendees:
                emails = [
                    attendee["emailAddress"]["address"]
                    for attendee in attendees
                    if "emailAddress" in attendee
                ]
                return emails
            return {"error": "Event not found"}
        else:
            logging.error(
                f"Error fetching event attendees: {response.status_code} - {response.text}"
            )
            return {"error": "Failed to fetch event attendees"}

    except Exception as e:
        logging.error(f"Error processing request: {str(e)}")
        return {"error": f"Internal Server Error: {str(e)}"}


def decoder(title):
    title = title.replace("\u200b", "").replace("\u200c", "").replace("\u200d", "")
    return title


def convert_timezone(timezone, date):
    local_timezone = pytz.timezone(timezone)
    local_start_datetime = local_timezone.localize(
        datetime.combine(date, datetime.min.time())
    )
    local_end_datetime = local_timezone.localize(
        datetime.combine(date, datetime.max.time())
    )
    start_datetime = local_start_datetime.isoformat()
    end_datetime = local_end_datetime.isoformat()

    return start_datetime, end_datetime


def getCalendarView(date, email, timezone):
    access_token = get_access_token()
    user_id = get_user_id_by_email(email, access_token)

    # Construct the API URL for calendarView
    url = f"{GRAPH_API_URL}/users/{user_id}/calendarView"

    # Set request headers
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    # Append times to the given date
    # startDateTime = f"{date}T00:00:00Z"
    # endDateTime = f"{date}T23:59:59Z"
    date = datetime.strptime(date, "%Y-%m-%d").date()
    startDateTime, endDateTime = convert_timezone(timezone, date)

    # Define query parameters
    params = {
        "startDateTime": startDateTime,
        "endDateTime": endDateTime,
        "$select": "subject,start,end,type,recurrence,seriesMasterId",
        "$orderby": "start/dateTime",
    }

    # Make the GET request
    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        events = response.json().get("value", [])
        subjects = ""
        for event in events:
            subjects = "- " + event.get("subject") + "\n" + subjects
        return subjects
    else:
        logging.error(
            f"Error fetching events: {response.status_code} - {response.text}"
        )
        return "false"


def is_recurring_event(event_id, email):
    """
    Checks if an event with the given event_id is recurring.

    Args:
        event_id (str): The ID of the event.
        email (str): The user's email address.

    Returns:
        bool: True if the event is recurring, False otherwise.
    """
    # Assumes you have these helper functions implemented
    access_token = get_access_token()
    userID = get_user_id_by_email(email, access_token)

    # Explicitly request the recurrence property
    url = f"{GRAPH_API_URL}/users/{userID}/events/{event_id}?$select=recurrence"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        logging.error(
            f"Error fetching event {event_id}: {response.status_code} - {response.text}"
        )
        return False  # or raise an exception if preferred

    event = response.json()

    # Debug print to inspect the returned payload
    print("Full event payload:", event)
    print("Recurrence field:", event.get("recurrence"))

    # If the 'recurrence' field exists and is not null, then it's a recurring event.
    return event.get("recurrence") is not None


def get_series_master_id(event_id: str, email: str) -> str:
    """
    Retrieves the seriesMasterId for the specified event of a user.

    Args:
        event_id (str): The ID of the event.
        email (str): The user's email address.

    Returns:
        str: The seriesMasterId if it exists; otherwise, None.
    """
    try:
        # Get the access token and user ID via your helper functions
        access_token = get_access_token()
        user_id = get_user_id_by_email(email, access_token)

        # Construct the URL and specify $select=seriesMasterId to only return that field.
        url = (
            f"{GRAPH_API_URL}/users/{user_id}/events/{event_id}?$select=seriesMasterId"
        )
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            logging.error(
                f"Error fetching event {event_id}: {response.status_code} - {response.text}"
            )
            return None

        event_data = response.json()
        logging.debug(f"Fetched event data: {event_data}")
        return event_data.get("seriesMasterId")

    except Exception as e:
        logging.error(f"Exception occurred while fetching seriesMasterId: {str(e)}")
        return None
