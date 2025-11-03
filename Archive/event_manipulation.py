import logging
import requests
from constants import GRAPH_API_URL
from utils import (
    get_access_token,
    get_user_display_name,
    get_user_id_by_email,
    parse_time,
    getEventID,
    parse_email_string,
    check_email,
    getEventAttendees,
    decoder,
    getCalendarView,
    get_series_master_id,
    is_recurring_event,
)
import azure.functions as func


def getEventsByDate(req: func.HttpRequest) -> func.HttpResponse:
    try:
        req_body = req.get_json()
        email = req_body.get("email")
        date = req_body.get("date")  # Date in YYYY-MM-DD format
        timezone = req_body.get("timezone")

        if not email or not date or not timezone:
            return func.HttpResponse("false", status_code=200)

        subjects = getCalendarView(date, email, timezone)

        if subjects != "false":
            return func.HttpResponse(subjects, status_code=200)
        else:
            return func.HttpResponse("false", status_code=200)

    except Exception as e:
        logging.error(f"Error processing request: {str(e)}")
        return func.HttpResponse(f"Internal Server Error: {str(e)}", status_code=200)


def deleteEvent(req: func.HttpRequest) -> func.HttpResponse:
    try:
        req_body = req.get_json()
        email = req_body.get("email")
        title = req_body.get("title")
        title = decoder(title)
        date = req_body.get("date")
        timezone = req_body.get("timezone")
        event_id = getEventID(
            title, date, email, timezone
        )  # The ID of the event to be deleted

        if not email or not event_id:
            return func.HttpResponse(
                "false",
                status_code=200,
            )
        masterID = get_series_master_id(event_id, email)
        if masterID is not None:
            if is_recurring_event(masterID, email):
                event_id = masterID
        # Get access token and user ID
        access_token = get_access_token()
        user_id = get_user_id_by_email(email, access_token)
        if not user_id:
            return func.HttpResponse("User not found.", status_code=404)

        # start_datetime, end_datetime = convert_timezone(timezone, date)

        # Prepare the URL to delete the event using Microsoft Graph API
        url = f"{GRAPH_API_URL}/users/{user_id}/events/{event_id}"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        # Make the DELETE request to Microsoft Graph API
        response = requests.delete(url, headers=headers)

        if (
            response.status_code == 204
        ):  # Successful deletion returns status 204 No Content
            return func.HttpResponse("Event Deleted Successfully.", status_code=200)
        else:
            logging.error(
                f"Error deleting event: {response.status_code} - {response.text}"
            )
            return func.HttpResponse("false", status_code=200)

    except Exception as e:
        logging.error(f"Error processing request: {str(e)}")
        return func.HttpResponse(f"Internal Server Error: {str(e)}", status_code=500)


def editEventSubject(req: func.HttpRequest) -> func.HttpResponse:
    try:
        req_body = req.get_json()
        email = req_body.get("email")
        subject = req_body.get("subject")
        current_title = req_body.get("title")
        current_title = decoder(current_title)
        date = req_body.get("date")
        timezone = req_body.get("timezone")
        event_id = getEventID(current_title, date, email, timezone)

        if not all([email, subject]):
            return func.HttpResponse(
                "false",
                status_code=200,
            )
        masterID = get_series_master_id(event_id, email)
        if masterID is not None:
            if is_recurring_event(masterID, email):
                event_id = masterID

        access_token = get_access_token()
        user_id = get_user_id_by_email(email, access_token)
        if not user_id:
            return func.HttpResponse("User not found.", status_code=404)

        # event data -- payload
        event_data = {"subject": subject}

        url = f"{GRAPH_API_URL}/users/{user_id}/events/{event_id}"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        response = requests.patch(url, headers=headers, json=event_data)

        if response.status_code == 200:
            return func.HttpResponse("Event Updated Successfully.", status_code=200)
        else:
            logging.error(
                f"Error updating event: {response.status_code} - {response.text}"
            )
            return func.HttpResponse("false", status_code=200)

    except Exception as e:
        logging.error(f"Error processing request: {str(e)}")
        return func.HttpResponse(f"Internal Server Error: {str(e)}", status_code=500)


def editEventDescription(req: func.HttpRequest) -> func.HttpResponse:
    try:
        req_body = req.get_json()
        email = req_body.get("email")
        description = req_body.get("description")
        current_title = req_body.get("title")
        current_title = decoder(current_title)
        date = req_body.get("date")
        timezone = req_body.get("timezone")
        event_id = getEventID(current_title, date, email, timezone)

        if not all([email, description]):
            return func.HttpResponse(
                "false",
                status_code=200,
            )

        masterID = get_series_master_id(event_id, email)
        if masterID is not None:
            if is_recurring_event(masterID, email):
                event_id = masterID

        access_token = get_access_token()
        user_id = get_user_id_by_email(email, access_token)
        if not user_id:
            return func.HttpResponse("User not found.", status_code=404)

        # event data -- payload
        event_data = {"body": {"contentType": "HTML", "content": description}}

        url = f"{GRAPH_API_URL}/users/{user_id}/events/{event_id}"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        response = requests.patch(url, headers=headers, json=event_data)

        if response.status_code == 200:
            return func.HttpResponse("Event Updated Successfully.", status_code=200)
        else:
            logging.error(
                f"Error updating event: {response.status_code} - {response.text}"
            )
            return func.HttpResponse("false", status_code=200)

    except Exception as e:
        logging.error(f"Error processing request: {str(e)}")
        return func.HttpResponse(f"Internal Server Error: {str(e)}", status_code=500)


def editEventDateTime(req: func.HttpRequest) -> func.HttpResponse:
    try:
        req_body = req.get_json()
        email = req_body.get("email")
        title = req_body.get("title")
        title = decoder(title)
        date = req_body.get("date")
        start_date = req_body.get("startDate")  # Date in YYYY-MM-DD format
        end_date = req_body.get("endDate")  # End recurrence date in YYYY-MM-DD format
        start_time = req_body.get("startTime")  # Start time in HH:MM format
        end_time = req_body.get("endTime")  # End time in HH:MM format
        time_zone = req_body.get("timezone")
        event_id = getEventID(title, date, email, time_zone)

        if is_recurring_event(event_id, email):
            return func.HttpResponse("recurrence", status_code=200)

        if not (start_date, end_date):
            start_date, end_date = date

        if not all([email, start_time, end_time, start_date, end_date]):
            return func.HttpResponse(
                "false",
                status_code=200,
            )

        access_token = get_access_token()
        user_id = get_user_id_by_email(email, access_token)
        if not user_id:
            return func.HttpResponse("User not found.", status_code=404)

        start_datetime = parse_time(start_date, start_time)
        end_datetime = parse_time(end_date, end_time)

        # event data -- payload
        event_data = {
            "start": {"dateTime": start_datetime, "timeZone": time_zone},
            "end": {"dateTime": end_datetime, "timeZone": time_zone},
        }

        url = f"{GRAPH_API_URL}/users/{user_id}/events/{event_id}"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        response = requests.patch(url, headers=headers, json=event_data)

        if response.status_code == 200:
            return func.HttpResponse("Event Updated Successfully.", status_code=200)
        else:
            logging.error(
                f"Error updating event: {response.status_code} - {response.text}"
            )
            return func.HttpResponse("false", status_code=200)

    except Exception as e:
        logging.error(f"Error processing request: {str(e)}")
        return func.HttpResponse(f"Internal Server Error: {str(e)}", status_code=500)


def addAttendeesToEvent(req: func.HttpRequest) -> func.HttpResponse:
    try:
        req_body = req.get_json()
        email = req_body.get("email")
        title = req_body.get("title")  # The title of the existing event
        title = decoder(title)
        date = req_body.get("date")
        attendees = req_body.get("attendees")  # List of attendee emails
        timezone = req_body.get("timezone")
        event_id = getEventID(title, date, email, timezone)
        attendees = parse_email_string(attendees)
        if not all([email, event_id, attendees]):
            return func.HttpResponse(
                "false",
                status_code=200,
            )

        access_token = get_access_token()
        user_id = get_user_id_by_email(email, access_token)
        if not user_id:
            return func.HttpResponse("User not found.", status_code=404)

        # Prepare attendees payload (cleaning and handling the payload)
        attendee_objects = []
        for attendee_email in attendees:
            if "@" in attendee_email:  # Basic validation for email
                if check_email(attendee_email):
                    name = get_user_display_name(attendee_email)
                    attendee_objects.append(
                        {
                            "emailAddress": {
                                "address": attendee_email.strip(),
                                "name": name if name else attendee_email.strip(),
                            },
                            "type": "required",
                        }
                    )
                else:
                    return func.HttpResponse("false", status_code=200)

        if not attendee_objects:
            return func.HttpResponse("false 1", status_code=200)

        # Event data -- payload to add attendees
        event_data = {"attendees": attendee_objects}

        url = f"https://graph.microsoft.com/v1.0/users/{user_id}/events/{event_id}"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        response = requests.patch(url, headers=headers, json=event_data)

        if response.status_code == 200:
            return func.HttpResponse("Attendees added successfully.", status_code=200)
        else:
            logging.error(
                f"Error adding attendees to event: {response.status_code} - {response.text}"
            )
            return func.HttpResponse("false", status_code=200)

    except Exception as e:
        logging.error(f"Error processing request: {str(e)}")
        return func.HttpResponse(f"Internal Server Error: {str(e)}", status_code=500)


# Function to modify attendees in event
def modifyAttendees(req: func.HttpRequest) -> func.HttpResponse:
    try:
        req_body = req.get_json()
        email = req_body.get("email")
        title = req_body.get("title")  # The title of the existing event
        title = decoder(title)
        date = req_body.get("date")
        attendees = req_body.get("attendees")  # List of attendee emails
        timezone = req_body.get("timezone")
        event_id = getEventID(title, date, email, timezone)
        attendees = parse_email_string(attendees)

        existing_attendees = getEventAttendees(email, date, title, timezone)

        for attendee in existing_attendees:
            attendees.append(attendee)

        attendees_set = set(attendees)
        attendees = list(attendees_set)

        if not all([email, event_id, attendees]):
            return func.HttpResponse(
                "false",
                status_code=200,
            )

        access_token = get_access_token()
        user_id = get_user_id_by_email(email, access_token)
        if not user_id:
            return func.HttpResponse("User not found.", status_code=404)

        # Prepare attendees payload (cleaning and handling the payload)
        attendee_objects = []
        for attendee_email in attendees:
            if "@" in attendee_email:  # Basic validation for email
                if check_email(attendee_email):
                    name = get_user_display_name(attendee_email)
                    attendee_objects.append(
                        {
                            "emailAddress": {
                                "address": attendee_email.strip(),
                                "name": name if name else attendee_email.strip(),
                            },
                            "type": "required",
                        }
                    )
                else:
                    return func.HttpResponse("false", status_code=200)

        if not attendee_objects:
            return func.HttpResponse("false", status_code=200)

        # Event data -- payload to add attendees
        event_data = {"attendees": attendee_objects}

        url = f"https://graph.microsoft.com/v1.0/users/{user_id}/events/{event_id}"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        response = requests.patch(url, headers=headers, json=event_data)

        if response.status_code == 200:
            return func.HttpResponse("Attendees added successfully.", status_code=200)
        else:
            logging.error(
                f"Error adding attendees to event: {response.status_code} - {response.text}"
            )
            return func.HttpResponse("false", status_code=200)

    except Exception as e:
        logging.error(f"Error processing request: {str(e)}")
        return func.HttpResponse(f"Internal Server Error: {str(e)}", status_code=500)
