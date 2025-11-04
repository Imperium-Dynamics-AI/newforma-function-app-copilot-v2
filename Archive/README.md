# Calendar Events and Outlook To-Do Azure Functions – Readme

---

## Overview

This collection of Azure Functions provides a lightweight HTTP API to:

* **Manage Calendar Events** in Microsoft 365 via the Graph API
* **Send Birthday Reminders**, optionally via email
* **CRUD Outlook To-Do Items**

All functions leverage a shared **utility module** for authentication, user lookup, date/time parsing, and Graph API calls.

---

## Prerequisites

* Python 3.8+
* Azure Functions Core Tools (v4)
* An Azure subscription with:

  * **Azure Functions** app
  * **Managed Identity** or **App Registration** with delegated Graph permissions for `Calendars.ReadWrite` and `Tasks.ReadWrite`
* Environment variables (in Azure or local.settings.json):

  * `CLIENT_ID`, `CLIENT_SECRET`, `TENANT_ID` (for `ClientSecretCredential`)
  * `GRAPH_API_URL` (typically `https://graph.microsoft.com/v1.0`)
  * (Optional) SMTP credentials if using email notifications

---

## Setup & Configuration

1. **Clone & Install**

   ```bash
   git clone <repo-url>
   cd <project-folder>
   pip install -r requirements.txt
   ```
2. **Configure local.settings.json**

   ```json
   {
     "IsEncrypted": false,
     "Values": {
       "AzureWebJobsStorage": "<storage-conn-str>",
       "FUNCTIONS_WORKER_RUNTIME": "python",
       "CLIENT_ID": "...",
       "CLIENT_SECRET": "...",
       "TENANT_ID": "...",
       "GRAPH_API_URL": "https://graph.microsoft.com/v1.0"
     }
   }
   ```
3. **Deploy** to Azure Functions

   ```bash
   func azure functionapp publish <your-function-app>
   ```

---

## Authentication & Utilities

All functions import from **utils.py**, which provides:

* **`get_access_token()`** – Acquires a Graph API token via `ClientSecretCredential`.&#x20;
* **`get_user_id_by_email(email, token)`** – Fetches a user’s Azure AD object ID by email.&#x20;
* **Date/Time Helpers**

  * `parse_time(date, time_str)` – Converts `YYYY-MM-DD` + `HH:MM` to ISO-8601.
  * `convert_timezone(...)`, `parse_date(...)` – For filtering and time-zone conversion.
* **To-Do Helpers**

  * `get_todo_list_id(email, list_name)`
  * `get_task_id_by_name(email, list_id, task_name)`
  * `get_subtask_id_by_name(email, list_id, task_id, subtask_name)`

---

## Function App Structure

* **`function_app.py`**
  Registers all HTTP-triggered Azure Functions and routes requests to their respective handlers.
* **`constants.py`**
  Defines `GRAPH_API_URL` and other shared constants.
* **Function modules** – Each implements one HTTP endpoint.

---

## Calendar Event Functions

### One-Time Event Creation

* **File:** `create_event.py`
* **Endpoint:** `POST /createEvent`
* **Request JSON:**

  ```json
  {
    "email": "<user-email>",
    "subject": "Meeting",
    "description": "...",
    "startDate": "2025-07-01",
    "startTime": "09:00",
    "endTime": "10:00",
    "location": "Conference Room",
    "timezone": "Asia/Karachi"
  }
  ```
* **Behavior:**

  1. Validate required fields.
  2. Acquire token & user ID.
  3. Build event payload.
  4. `POST https://graph.microsoft.com/v1.0/users/{userId}/events`.
  5. Return 200 if created, else error text.

### Recurring Events

All recurring handlers follow the same pattern: parse JSON, validate, call `parse_time()`, then construct a **`recurrence`** object before posting to `/users/{userId}/events`.

#### Daily

* **File:** `recurring_daily_event.py`
* **Recurrence Pattern:**

  ````json
  "recurrence": {
    "pattern": { "type":"daily", "interval": <n> },
    "range": { "type":"endDate", "startDate":..., "endDate":... }
  }
  ``` :contentReference[oaicite:2]{index=2}
  ````

#### Weekly

* **File:** `recurring_weekly_event.py`
* **Pattern:**

  ````json
  "pattern": { "type":"weekly", "interval":<n>, "daysOfWeek":["Monday","Friday",…] }
  ``` :contentReference[oaicite:3]{index=3}
  ````

#### Monthly (Absolute Day)

* **File:** `recurring_monthly_absolute_event.py`
* **Pattern:**

  ````json
  "pattern": {
    "type":"absoluteMonthly",
    "interval":<n>,
    "dayOfMonth": <1–31>
  }
  ``` :contentReference[oaicite:4]{index=4}
  ````

#### Yearly (Absolute Day & Month)

* **File:** `recurring_yearly_absolute_event.py`
* **Pattern:**

  ````json
  "pattern": {
    "type":"absoluteYearly",
    "interval":<n>,
    "dayOfMonth":<d>,
    "month":<m>
  }
  ``` :contentReference[oaicite:5]{index=5}
  ````

---

## Birthday Reminder Functions

### Simple Reminder

* **File:** `birthday_reminder.py`
* **Endpoint:** `GET /birthdayReminder?email=<>&date=YYYY-MM-DD`
* **Behavior:**

  1. Fetch calendar view for the date.
  2. Filter events with “birthday” in subject.
  3. Return list of names.

### Email Notification

* **File:** `birthday_reminder_with_email.py`
* **Endpoint:** `POST /birthdayReminderEmail`
* **Request:**

  ```json
  {
    "email": "...",
    "date": "2025-07-01",
    "smtpServer": "...",
    "smtpUser": "...",
    "smtpPass": "..."
  }
  ```
* **Behavior:**

  1. As above, then compose an email summary.
  2. Send via SMTP to the user.

---

## Outlook To-Do Functions

Each operates against the Graph To-Do API under `/users/{userId}/todo/lists/{listId}/tasks`.

### Create To-Do Item

* **File:** `createTodoItems.py`
* **Endpoint:** `POST /todo/create`
* **Body:**

  ```json
  { "email":"...", "listName":"Tasks","title":"Buy milk","dueDate":"2025-07-02" }
  ```

### Fetch To-Do Items

* **File:** `fetchItems.py`
* **Endpoint:** `GET /todo/items?email=...&listName=...`
* **Response:** JSON array of tasks.

### Edit To-Do Item

* **File:** `editItems.py`
* **Endpoint:** `PATCH /todo/edit`
* **Body:**

  ```json
  { "email":"...", "listName":"Tasks", "taskName":"Buy milk", "newTitle":"Buy almond milk" }
  ```

### Delete To-Do Item

* **File:** `deleteItems.py`
* **Endpoint:** `DELETE /todo/delete`
* **Body:**

  ```json
  { "email":"...", "listName":"Tasks", "taskName":"Buy milk" }
  ```

All To-Do handlers use utility lookups (`get_todo_list_id`, `get_task_id_by_name`) to resolve IDs before sending Graph requests.&#x20;

---

## Endpoints Summary

| HTTP Verb | Path                     | Description                       |
| --------- | ------------------------ | --------------------------------- |
| POST      | `/createEvent`           | Create one-time calendar event    |
| POST      | `/recurring/daily`       | Create daily recurring event      |
| POST      | `/recurring/weekly`      | Create weekly recurring event     |
| POST      | `/recurring/monthly`     | Create monthly absolute-day event |
| POST      | `/recurring/yearly`      | Create yearly absolute event      |
| GET       | `/birthdayReminder`      | List birthdays on given date      |
| POST      | `/birthdayReminderEmail` | Birthday summary via email        |
| POST      | `/todo/create`           | Create a To-Do task               |
| GET       | `/todo/items`            | Fetch tasks from a To-Do list     |
| PATCH     | `/todo/edit`             | Modify a To-Do task               |
| DELETE    | `/todo/delete`           | Delete a To-Do task               |

---

## Logging & Error Handling

* **Logging:**

  * Each function logs input payloads, constructed Graph payloads, and responses.
  * Utility functions log retrieval errors.
* **HTTP Responses:**

  * **200/201** on success
  * **4xx** for missing parameters or not-found cases
  * **500** for unhandled exceptions

---

## Further Reading

* **Azure Functions Python developer guide**
* **Microsoft Graph API docs** for [Calendar](https://docs.microsoft.com/graph/api/resources/event) and [To-Do](https://docs.microsoft.com/graph/api/resources/todo-overview)
* **Azure Identity library** for Python authentication

---
