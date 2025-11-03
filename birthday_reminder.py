import re
import azure.functions as func
import logging
import requests
import json
from azure.identity import ClientSecretCredential
from datetime import datetime, timedelta
from dateutil.parser import parse

from constants import CLIENT_ID, CLIENT_SECRET, TENANT_ID

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
def get_user_id(name, access_token):
    url = f"{GRAPH_API_URL}/users?$filter=displayName eq '{name}'&$select=id,mail"
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        users = response.json().get("value", [])
        if len(users) > 1:
            result = "\n".join([f"- **{user['displayName']}** ({user['mail']})" for user in users])
            return None, f"## Multiple Users Found:\n{result}", 1
        elif users:
            return users[0]['id'], None, 0
    return None, "false", 2


def get_user_id_by_email(email, access_token):
    url = f"{GRAPH_API_URL}/users/{email}?$select=id,mail,displayName"
    headers = {'Authorization': f'Bearer {access_token}'}
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        user = response.json()
        return user.get('id')
    elif response.status_code == 404:
        return None
    else:
        return None



# Function to get birthday from OData API
def get_birthday(name, access_token, resource_url):
    logging.info(f"Getting birthday for {name}...")

    # Define the headers with the access token
    headers = {'Authorization': f'Bearer {access_token}'}

    # Construct the URL with $filter and $select to include contactid
    contact_api_url = (
        f"{resource_url}/api/data/v9.2/contacts?"
        f"$filter=fullname eq '{name}'&$select=fullname,birthdate,contactid"
    )

    try:
        # Make the API request
        response = requests.get(contact_api_url, headers=headers)

        # Check if the request was successful
        if response.status_code == 200:
            contacts = response.json().get("value", [])
            # If a matching contact is found, return the birthdate and contactid
            if contacts:
                logging.info(f"Successfully retrieved birthday and contact ID for {name}.")
                return contacts[0].get("birthdate"), contacts[0].get("contactid")
            else:
                logging.warning(f"No contact found with the name {name}.")
                return None
        else:
            # Log the error if the API request fails
            logging.error(f"API request failed with status code {response.status_code}: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        # Log any exceptions that occur during the API request
        logging.error(f"An error occurred while making the API request: {e}")
        return None

# Function to create an event
def create_event(user_id, access_token, event_date, timezone,user):
    try:
        url = f"{GRAPH_API_URL}/users/{user_id}/calendar/events"
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        event_data = {
            "subject": f"Birthday Reminder {user}",
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

# Azure Function handler
def EventCreator(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Processing request...')
    try:
        req_body = req.get_json()
    except ValueError:
        return func.HttpResponse("Invalid JSON body.", status_code=200)
   
    name = req_body.get('name')
    days_prior = req_body.get('days_prior')
    resource_url = req_body.get('resource_url')  # Take resource URL dynamically from body
    email = req_body.get('email')  # Take email dynamically from body
    timezone = req_body.get('timezone')  # Take timezone dynamically from body
   
    if not name or not days_prior or not resource_url or not email or not timezone:
        return func.HttpResponse("Missing parameters.", status_code=200)
   
    try:
        days_prior = int(days_prior)
    except ValueError:
        return func.HttpResponse("Invalid days_prior format.", status_code=200)
   
    access_token = get_access_token()
   
    user_id, markdown_response, code = get_user_id(name, access_token)
   
    if code == 1:
        return func.HttpResponse(markdown_response, status_code=200)
    elif code == 2:
        return func.HttpResponse("false", status_code=200)
   
    user_id = get_user_id_by_email(email, access_token)
    if not user_id:
        return func.HttpResponse("no email found", status_code=200)
   
    odataAccessToken = oDataAccessToken(resource_url)
   
    birthday, contactID = get_birthday(name, odataAccessToken, resource_url)
    if not birthday:
        return func.HttpResponse("no birthday", status_code=200)
   
    try:
        birthday_date = get_next_birthday(birthday)
        event_date = (birthday_date - timedelta(days=days_prior)).strftime("%Y-%m-%d")
    except ValueError as e:
        logging.error(f"Invalid date format: {e}")
        return func.HttpResponse("Invalid date format for birthday.", status_code=400)
   
    logging.info(f"Creating event for {name}'s birthday on {event_date} birthday: {birthday_date}...")
    res1 = create_event(user_id, access_token, event_date, timezone,name)
    logging.info(f"Creating note for {name}'s birthday on {event_date} userid: {contactID}...")
    res2 = create_note(contactID, odataAccessToken, event_date, resource_url)
    if res1 and res2:
        return func.HttpResponse('Created', status_code=200)
    else:
        return func.HttpResponse('Failed', status_code=200)