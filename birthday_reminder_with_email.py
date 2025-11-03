import re
import azure.functions as func
import logging
import requests
import json
from azure.identity import ClientSecretCredential
from datetime import datetime, timedelta
from dateutil.parser import parse
from constants import CLIENT_ID, CLIENT_SECRET, TENANT_ID
from recurring_yearly_absolute_event import absoluteYearlyRecurringEvents
from datetime import date, timedelta

# API URLs
GRAPH_API_URL = "https://graph.microsoft.com/v1.0"

# Function to get access token
def get_access_token():
    credential = ClientSecretCredential(
        tenant_id=TENANT_ID,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET
    )
    token = credential.get_token("https://graph.microsoft.com/.default")
    return token.token

def oDataAccessToken(RESOURCE):

    
    token_url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/token"
    payload = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "resource": RESOURCE
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
   
    response = requests.post(token_url, data=payload, headers=headers)
    response.raise_for_status()
   
    return response.json()["access_token"]

# Function to retrieve user ID based on email
def get_user_id_by_email(email, access_token):
    url = f"{GRAPH_API_URL}/users/{email}?$select=id,mail"
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        user = response.json()
        return user['id'], None
    return None, "User not found."

# Function to get contact details from OData API
def get_contact_by_email(contact_email, access_token, resource_url):
    logging.info(f"Getting contact details for {contact_email}...")

    # Define the headers with the access token
    headers = {'Authorization': f'Bearer {access_token}'}

    # Construct the URL with $filter to include contactemail
    contact_api_url = (
        f"{resource_url}/api/data/v9.2/contacts?"
        f"$filter=emailaddress1 eq '{contact_email}'&$select=emailaddress1,birthdate,contactid"
    )

    try:
        # Make the API request
        response = requests.get(contact_api_url, headers=headers)

        # Check if the request was successful
        if response.status_code == 200:
            contacts = response.json().get("value", [])
            # If a matching contact is found, return the birthdate and contactid
            if contacts:
                logging.info(f"Successfully retrieved birthday and contact ID for {contact_email} {contacts}.")
                return contacts[0].get("birthdate"), contacts[0].get("contactid")
            else:
                logging.warning(f"No contact found with the email {contact_email}.")
                return None, None
        else:
            # Log the error if the API request fails
            logging.error(f"API request failed with status code {response.status_code}: {response.text}")
            return None, None
    except requests.exceptions.RequestException as e:
        # Log any exceptions that occur during the API request
        logging.error(f"An error occurred while making the API request: {e}")
        return None, None

# Function to create an event
def create_event(user_id, access_token, event_date, timezone,email):
    try:
        
        url = f"{GRAPH_API_URL}/users/{user_id}/calendar/events"
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        event_data = {
            "subject": f"Birthday Reminder of {email}",
           "start": {"dateTime": f"{event_date}T00:00:00", "timeZone": timezone},
            "end": {"dateTime": f"{event_date}T00:15:00", "timeZone": timezone},
            "body": {"contentType": "Text", "content": "Don't forget to wish!"}
        }
        response = requests.post(url, headers=headers, data=json.dumps(event_data))
        return True
    except Exception as e:
        logging.error(f"Error creating event: {e}")
        return False

# Function to create a note
def create_note(contact_id, access_token, event_date, resource_url):
    url = f"{resource_url}/api/data/v9.2/annotations"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    note_data = {
        "subject": "Birthday Reminder",
        "notetext": f"Reminder for birthday on {event_date}",
        "objectid_contact@odata.bind": f"/contacts({contact_id})"  # Linking note to the contact
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(note_data))
        if response.status_code in [200, 201, 204]:
            return True
        else:
            return False
    except requests.exceptions.RequestException as e:
        logging.error(f"Error creating note: {e}")
        return False

# Function to get the next birthday
def get_next_birthday(birthday):
    # Parse birthday to extract month and day
    birth_date = datetime.strptime(birthday, "%Y-%m-%d")
    current_year = datetime.now().year

    # Create a new birthday date with the current year
    next_birthday = datetime(current_year, birth_date.month, birth_date.day)

    # If birthday has already passed this year, use next year
    if next_birthday < datetime.now():
        next_birthday = datetime(current_year + 1, birth_date.month, birth_date.day)

    return next_birthday



def adjust_date_by_days(event_date: date, days_prior: int):
    # Subtract days_prior from the event date
    adjusted_datetime = event_date - timedelta(days=days_prior)

    # Extract the adjusted day and month
    absolute_day_of_month = adjusted_datetime.day
    absolute_month = adjusted_datetime.month
    
    return absolute_day_of_month, absolute_month

import json
import logging
import requests

def create_crm_activity(contact_id, user_id_for_owner, access_token, activity_type, subject, description, due_date, resource_url):
    
    url = f"{resource_url}/api/data/v9.2/tasks"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    activity_data = {
        "subject": subject,
        "description": description,
        "scheduledend": due_date,
        "regardingobjectid_contact@odata.bind": f"/contacts({contact_id})",
        "activitytypecode": activity_type,
        "ownerid@odata.bind": f"/systemusers({user_id_for_owner})",  # Assign owner ID
        "owninguser_task@odata.bind":f"/systemusers({user_id_for_owner})"  # Assign owner ID
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(activity_data))
        
        if response.status_code in [200, 201, 204]:
            return True
        else:
            logging.error(f"Failed to create CRM activity: {response.status_code}, {response.text}")
            return False

    except requests.exceptions.RequestException as e:
        logging.error(f"Error creating CRM activity: {e}")
        return False



def get_user_id_by_email_sales(email: str, access_token: str, resource_url: str):
    
    try:
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        # Query OData API to filter user by email
        url = f"{resource_url}/api/data/v9.2/systemusers?$filter=internalemailaddress eq '{email}'"
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            users = data.get("value", [])

            if users:
                return users[0].get("systemuserid")  # Return first matching user ID
            else:
                return None  # No user found

        else:
            print(f"Error fetching user: {response.status_code}, {response.text}")
            return None

    except Exception as e:
        print(f"Exception occurred: {e}")
        return None

# Azure Function handler
def EventCreatorWithEmail(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Processing request... EventCreatorWithEmail')

    try:
        req_body = req.get_json()
    except ValueError:
        return func.HttpResponse("Invalid JSON body.", status_code=400)

    email = req_body.get('email')
    contact_email = req_body.get('contact_email')
    days_prior = req_body.get('days_prior')
    resource_url = req_body.get('resource_url')
    timezone = req_body.get('timezone')
    subject = req_body.get("subject", f"BirthDay Reminder for {contact_email}")
    description = req_body.get("description", "Don't forget to wish!")
    current_year = datetime.now().year
    end_date = req_body.get("end_date", f"{current_year + 5}-{datetime.now().month:02d}-{datetime.now().day:02d}")
    location = req_body.get("location", "Online")

    # Required parameters list
    required_params = [email, contact_email, days_prior, resource_url, timezone,subject,description,end_date,location]

    # Check for missing parameters
    if None in required_params or "" in required_params:
        return func.HttpResponse("Missing parameters.", status_code=400)

    try:
        days_prior = int(days_prior)
    except ValueError:
        return func.HttpResponse("Invalid days_prior format.", status_code=400)

    access_token = get_access_token()

    user_id, message = get_user_id_by_email(email, access_token)
    if not user_id:
        return func.HttpResponse('false', status_code=400)

    odataAccessToken = oDataAccessToken(resource_url)

    birthday, contactID = get_contact_by_email(contact_email, odataAccessToken, resource_url)
    if not contactID:
        return func.HttpResponse("false", status_code=400)
    if not birthday:
        return func.HttpResponse("No Birthday", status_code=200)

    try:
        birthday_date = get_next_birthday(birthday)
        event_date = (birthday_date - timedelta(days=days_prior)).strftime("%Y-%m-%d")
    except ValueError as e:
        logging.error(f"Invalid date format: {e}")
        return func.HttpResponse("Invalid date format for birthday.", status_code=400)

    # res1 = create_event(user_id, access_token, event_date, timezone,contact_email)
    # Create a note related to the contact
    #res2 = create_note(contactID, odataAccessToken, event_date, resource_url)

    # Subtract the days_prior and add 5 days
    adjusted_datetime = birthday_date - timedelta(days=days_prior) - timedelta(days=15)
    logging.info(f"adjusted_datetime: {adjusted_datetime}")
    start_date = adjusted_datetime.strftime("%Y-%m-%d")
    logging.info(f"start_date: {start_date}")
    start_time = "00:00"
    end_time = "00:15"
    
    absolute_day_of_month , absolute_month =adjust_date_by_days(birthday_date, days_prior)
    logging.info(f"absolute_day_of_month: {absolute_day_of_month}, absolute_month: {absolute_month}")

    

    # Create a yearly recurring event
    recurring_event_payload = {
        "email": email,
        "subject": subject,
        "description": description,
        "startDate": start_date,
        "startTime": start_time,
        "endTime": end_time,
        "interval": 1,
        "DayofMonth": absolute_day_of_month,
        "MonthofYear": absolute_month,
        "location": location,
        "endDate": end_date,
        "timezone": timezone,
    }
    user_id_for_owner=get_user_id_by_email_sales(email,odataAccessToken,resource_url)
    if not user_id_for_owner:
        return func.HttpResponse('User Not Found In Sales Enviroment', status_code=200)
    # Pass the formatted payload to the function
    res3 = absoluteYearlyRecurringEvents(recurring_event_payload)
    activity_type = "task"  # You can change this to the appropriate activity type
    subject = f"Birthday Reminder for {contact_email}"
    description = f"Don't forget to wish {contact_email} on their birthday on {birthday_date}."
    res4 = create_crm_activity(contactID,user_id_for_owner, odataAccessToken, activity_type, subject, description, birthday_date.strftime("%Y-%m-%d"),resource_url)
    if res3 and res4:
        return func.HttpResponse(birthday_date.strftime("%Y-%m-%d"), status_code=200)
    else:
        return func.HttpResponse('Failed', status_code=400)