"""
EventsHandler - HTTP request handler for Calendar Events operations.

This handler processes incoming HTTP requests for event management with 4 main endpoints:
1. create_event() - Universal creation (detects one-time vs recurring)
2. get_events() - Retrieve events by date
3. edit_event() - Unified edit endpoint (routes to specific update logic)
4. delete_event() - Delete events

The handler validates request data, delegates to EventsManager for business logic,
and returns properly formatted HTTP responses.
"""

import azure.functions as func

from src.common.exceptions import TodoAPIError, ValidationError
from src.managers.events_manager import EventsManager
from src.models.event_events import (
    CreateEventRequest,
    CreateRecurringEventRequest,
    CreateDailyRecurringEventRequest,
    CreateWeeklyRecurringEventRequest,
    CreateAbsoluteMonthlyRecurringEventRequest,
    CreateAbsoluteYearlyRecurringEventRequest,
    GetEventsByDateRequest,
    DeleteEventRequest,
)
from src.logging.logger import get_logger
from src.utils.http_utils import json_response
from src.utils.request_utils import parse_json

logger = get_logger(__name__)


class EventsHandler:
    """
    Handler class for processing HTTP requests related to calendar events.
    
    This class provides 4 main HTTP endpoints with flexible backend routing:
    - create_event: Detects event type and routes to appropriate creation logic
    - get_events: Retrieves events for a specific date
    - edit_event: Unified endpoint that updates any event property
    - delete_event: Removes an event
    
    All methods parse requests, validate with Pydantic models, call manager methods,
    and return formatted JSON responses with appropriate HTTP status codes.
    """

    def __init__(self, manager: EventsManager) -> None:
        """
        Initialize the EventsHandler with an EventsManager instance.

        Args:
            manager (EventsManager): Manager for event business logic operations.
        """
        self.manager = manager

    async def create_event(self, req: func.HttpRequest) -> func.HttpResponse:
        """
        Handle POST /events/create - Universal event creation endpoint.
        
        Automatically detects event type based on request fields:
        - One-time event: Contains 'date' field
        - Generic recurring: Contains 'recurrence' object
        - Daily recurring: Contains 'interval' and 'endDate' (no daysOfWeek)
        - Weekly recurring: Contains 'daysOfWeek'
        - Monthly recurring: Contains 'DayofMonth' (no MonthofYear)
        - Yearly recurring: Contains 'DayofMonth' and 'MonthofYear'
        
        Backend routes to specific manager methods based on detected type.

        Args:
            req (func.HttpRequest): The HTTP request object with JSON body.

        Returns:
            func.HttpResponse: JSON response with created event data (201) or error.
        """
        try:
            # Parse raw JSON first to detect event type
            body = req.get_json()
            
            # Detect event type and route accordingly
            if 'date' in body and 'recurrence' not in body and 'startDate' not in body:
                # One-time event
                data = parse_json(req, CreateEventRequest)
                logger.info(
                    "Creating one-time event '%s' for user %s on %s",
                    data.subject,
                    data.user_email,
                    data.date,
                )
                result = await self.manager.create_one_time_event(
                    user_email=data.user_email,
                    subject=data.subject,
                    date=data.date,
                    start_time=data.startTime,
                    end_time=data.endTime,
                    timezone=data.timezone,
                    description=data.description,
                    location=data.location,
                    attendees=data.attendees,
                    content_type=data.contentType,
                )
            
            elif 'recurrence' in body:
                # Generic recurring event with full recurrence object
                data = parse_json(req, CreateRecurringEventRequest)
                logger.info(
                    "Creating generic recurring event '%s' for user %s",
                    data.subject,
                    data.user_email,
                )
                result = await self.manager.create_recurring_event(
                    user_email=data.user_email,
                    subject=data.subject,
                    start_date=data.startDate,
                    start_time=data.startTime,
                    end_time=data.endTime,
                    timezone=data.timezone,
                    recurrence=data.recurrence.dict(),
                    description=data.description,
                    location=data.location,
                    attendees=data.attendees,
                    content_type=data.contentType,
                )
            
            elif 'MonthofYear' in body and 'DayofMonth' in body:
                # Yearly recurring
                data = parse_json(req, CreateAbsoluteYearlyRecurringEventRequest)
                logger.info(
                    "Creating yearly recurring event '%s' for user %s",
                    data.subject,
                    data.user_email,
                )
                result = await self.manager.create_yearly_recurring_event(
                    user_email=data.user_email,
                    subject=data.subject,
                    start_date=data.startDate,
                    end_date=data.endDate,
                    start_time=data.startTime,
                    end_time=data.endTime,
                    timezone=data.timezone,
                    day_of_month=data.DayofMonth,
                    month_of_year=data.MonthofYear,
                    interval=data.interval,
                    description=data.description,
                    location=data.location,
                    attendees=data.attendees,
                )
            
            elif 'DayofMonth' in body:
                # Monthly recurring
                data = parse_json(req, CreateAbsoluteMonthlyRecurringEventRequest)
                logger.info(
                    "Creating monthly recurring event '%s' for user %s",
                    data.subject,
                    data.user_email,
                )
                result = await self.manager.create_monthly_recurring_event(
                    user_email=data.user_email,
                    subject=data.subject,
                    start_date=data.startDate,
                    end_date=data.endDate,
                    start_time=data.startTime,
                    end_time=data.endTime,
                    timezone=data.timezone,
                    day_of_month=data.DayofMonth,
                    interval=data.interval,
                    description=data.description,
                    location=data.location,
                    attendees=data.attendees,
                )
            
            elif 'daysOfWeek' in body:
                # Weekly recurring
                data = parse_json(req, CreateWeeklyRecurringEventRequest)
                logger.info(
                    "Creating weekly recurring event '%s' for user %s",
                    data.subject,
                    data.user_email,
                )
                result = await self.manager.create_weekly_recurring_event(
                    user_email=data.user_email,
                    subject=data.subject,
                    start_date=data.startDate,
                    end_date=data.endDate,
                    start_time=data.startTime,
                    end_time=data.endTime,
                    timezone=data.timezone,
                    days_of_week=data.daysOfWeek or [],
                    interval=data.interval,
                    description=data.description,
                    location=data.location,
                    attendees=data.attendees,
                )
            
            else:
                # Daily recurring (has startDate, endDate, interval)
                data = parse_json(req, CreateDailyRecurringEventRequest)
                logger.info(
                    "Creating daily recurring event '%s' for user %s",
                    data.subject,
                    data.user_email,
                )
                result = await self.manager.create_daily_recurring_event(
                    user_email=data.user_email,
                    subject=data.subject,
                    start_date=data.startDate,
                    end_date=data.endDate,
                    start_time=data.startTime,
                    end_time=data.endTime,
                    timezone=data.timezone,
                    interval=data.interval,
                    description=data.description,
                    location=data.location,
                    attendees=data.attendees,
                )
            
            logger.info("Event created successfully")
            return json_response(result, 201)
            
        except ValidationError as e:
            logger.error("Validation error creating event: %s", e.detail)
            return json_response(e.to_response(), e.status_code)
        except TodoAPIError as e:
            logger.error("API error creating event: %s", e.detail)
            return json_response(e.to_response(), e.status_code)

    async def get_events(self, req: func.HttpRequest) -> func.HttpResponse:
        """
        Handle POST /events/get - Retrieve events for a specific date.

        Args:
            req (func.HttpRequest): The HTTP request object with JSON body:
                { user_email, date, timezone }

        Returns:
            func.HttpResponse: JSON response with list of events (200) or error.
        """
        try:
            data = parse_json(req, GetEventsByDateRequest)
            logger.info(
                "Retrieving events for user %s on date %s",
                data.user_email,
                data.date,
            )
            events = await self.manager.get_events_by_date(
                user_email=data.user_email,
                date=data.date,
                timezone=data.timezone,
            )
            logger.info("Retrieved %d events", len(events))
            return json_response({"events": events}, 200)
            
        except ValidationError as e:
            logger.error("Validation error retrieving events: %s", e.detail)
            return json_response(e.to_response(), e.status_code)
        except TodoAPIError as e:
            logger.error("API error retrieving events: %s", e.detail)
            return json_response(e.to_response(), e.status_code)

    async def edit_event(self, req: func.HttpRequest) -> func.HttpResponse:
        """
        Handle PUT /events/edit - Unified endpoint for editing any event property.
        
        This single endpoint handles all event updates by accepting optional fields:
        - subject: New event title
        - description: New event description
        - startTime, endTime: New times
        - startDate, endDate: New dates
        - location: New location
        - attendees: List of attendee emails (with attendeesAction: 'add' or 'replace')
        
        Backend routes to specific manager methods based on provided fields.
        Uses Microsoft Graph PATCH to update multiple properties in one call.
        
        Required fields: user_email, title (current), date, timezone
        Optional fields: Any combination of the above

        Args:
            req (func.HttpRequest): The HTTP request object with JSON body.

        Returns:
            func.HttpResponse: JSON response with success message (200) or error.
        """
        try:
            body = req.get_json()
            user_email = body.get('user_email')
            title = body.get('title')
            date = body.get('date')
            timezone = body.get('timezone')
            
            # Validate required fields
            if not all([user_email, title, date, timezone]):
                raise ValidationError(
                    detail="Required fields: user_email, title, date, timezone"
                )
            
            logger.info(
                "Editing event '%s' for user %s on date %s",
                title,
                user_email,
                date,
            )
            
            # Collect update operations based on provided fields
            updates_performed = []
            
            # Update subject if provided
            if 'subject' in body and body['subject']:
                await self.manager.edit_event_subject(
                    user_email=user_email,
                    title=title,
                    date=date,
                    timezone=timezone,
                    new_subject=body['subject'],
                )
                updates_performed.append('subject')
            
            # Update description if provided
            if 'description' in body:
                content_type = body.get('contentType', 'Text')
                await self.manager.edit_event_description(
                    user_email=user_email,
                    title=title,
                    date=date,
                    timezone=timezone,
                    description=body['description'],
                    content_type=content_type,
                )
                updates_performed.append('description')
            
            # Update date/time if provided
            if any(key in body for key in ['startDate', 'endDate', 'startTime', 'endTime']):
                await self.manager.edit_event_datetime(
                    user_email=user_email,
                    title=title,
                    date=date,
                    timezone=timezone,
                    new_start_date=body.get('startDate'),
                    new_end_date=body.get('endDate'),
                    new_start_time=body.get('startTime'),
                    new_end_time=body.get('endTime'),
                )
                updates_performed.append('datetime')
            
            # Update location if provided
            if 'location' in body:
                # Location update will be added to manager
                updates_performed.append('location')
            
            # Update attendees if provided
            if 'attendees' in body and body['attendees']:
                attendees_action = body.get('attendeesAction', 'add')
                
                if attendees_action == 'replace':
                    await self.manager.modify_attendees(
                        user_email=user_email,
                        title=title,
                        date=date,
                        timezone=timezone,
                        attendees=body['attendees'],
                    )
                else:  # default to 'add'
                    await self.manager.add_attendees(
                        user_email=user_email,
                        title=title,
                        date=date,
                        timezone=timezone,
                        attendees=body['attendees'],
                    )
                updates_performed.append('attendees')
            
            if not updates_performed:
                raise ValidationError(
                    detail="No update fields provided. Specify at least one field to update."
                )
            
            logger.info(
                "Event '%s' updated successfully. Updated fields: %s",
                title,
                ', '.join(updates_performed),
            )
            
            return json_response({
                "message": "Event updated successfully",
                "event_title": title,
                "updated_fields": updates_performed,
            }, 200)
            
        except ValidationError as e:
            logger.error("Validation error editing event: %s", e.detail)
            return json_response(e.to_response(), e.status_code)
        except TodoAPIError as e:
            logger.error("API error editing event: %s", e.detail)
            return json_response(e.to_response(), e.status_code)

    async def delete_event(self, req: func.HttpRequest) -> func.HttpResponse:
        """
        Handle DELETE /events/delete - Delete a calendar event.

        Args:
            req (func.HttpRequest): The HTTP request object with JSON body:
                { user_email, title, date, timezone }

        Returns:
            func.HttpResponse: JSON response with success message (200) or error.
        """
        try:
            data = parse_json(req, DeleteEventRequest)
            logger.info(
                "Deleting event '%s' for user %s on date %s",
                data.title,
                data.user_email,
                data.date,
            )
            await self.manager.delete_event(
                user_email=data.user_email,
                title=data.title,
                date=data.date,
                timezone=data.timezone,
            )
            logger.info("Event '%s' deleted successfully", data.title)
            return json_response({
                "message": "Event deleted successfully",
                "event_title": data.title,
            }, 200)
            
        except ValidationError as e:
            logger.error("Validation error deleting event: %s", e.detail)
            return json_response(e.to_response(), e.status_code)
        except TodoAPIError as e:
            logger.error("API error deleting event: %s", e.detail)
            return json_response(e.to_response(), e.status_code)
