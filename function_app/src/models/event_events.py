# src/models/event_events.py
"""
Event request and response models for handlers.
Follows the same style as your todo models: small request models that inherit EventBase,
and response models that surface IDs and timestamps.
"""

from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, EmailStr, Field, constr
from src.models.event_base import EventBase
from src.models.event_common import (
    EventAttendee,
    EventBody,
    EventLocation,
    EventTime,
    Recurrence,
)

# -------------------------
# Create / Read models
# -------------------------


# -------------------------
# Base Model for Creation
# -------------------------
class EventCommonCreate(EventBase):
    """
    Base model for creating events with common fields across all event types.
    Includes subject, description, time details, timezone, attendees, location, and content type.
    """

    subject: constr(min_length=1, max_length=200) = Field(
        ..., description="Event subject/title"
    )
    description: Optional[str] = Field(
        None, description="Event description/body content"
    )
    startTime: str = Field(..., description="Start time string (HH:MM)")
    endTime: str = Field(..., description="End time string (HH:MM)")
    timezone: str = Field(..., description="Timezone (e.g. 'Asia/Karachi')")
    attendees: Optional[List[EmailStr]] = Field(
        None, description="Optional list of attendee emails"
    )
    location: Optional[str] = Field(
        None, description="Optional human-readable location (displayName)"
    )
    contentType: Optional[Literal["Text", "HTML"]] = Field(
        "Text", description="Body content type"
    )


# -------------------------
# One-time Event
# -------------------------
class CreateEventRequest(EventCommonCreate):
    """
    Model for creating a one-time event.
    """

    date: str = Field(..., description="Date string (YYYY-MM-DD) for a one-time event")


# -------------------------
# Generic Recurring Event
# -------------------------
class CreateRecurringEventRequest(EventCommonCreate):
    """
    Generic recurring event model with explicit Recurrence object.
    """

    startDate: str = Field(..., description="Series start date (YYYY-MM-DD)")
    endTime: str = Field(..., description="Series end time (HH:MM)")
    recurrence: Recurrence = Field(
        ..., description="Recurrence object (pattern + range)"
    )
    contentType: Optional[Literal["Text", "HTML"]] = Field(
        "HTML", description="Recurring events use HTML by default"
    )


# -------------------------
# Specific Recurring Events
# -------------------------
class CreateDailyRecurringEventRequest(EventCommonCreate):
    """
    Daily recurring event.
    """

    startDate: str = Field(..., description="Start date (YYYY-MM-DD)")
    endDate: str = Field(..., description="Recurrence series end date (YYYY-MM-DD)")
    interval: int = Field(1, ge=1, description="Recur every `interval` days")


class CreateWeeklyRecurringEventRequest(EventCommonCreate):
    """
    Weekly recurring event.
    """

    startDate: str = Field(..., description="Start date (YYYY-MM-DD)")
    endDate: str = Field(..., description="Recurrence end date (YYYY-MM-DD)")
    interval: int = Field(1, ge=1, description="Recur every `interval` weeks")
    daysOfWeek: Optional[List[str]] = Field(
        None, description="List of weekdays (e.g., ['Monday'])"
    )


class CreateAbsoluteMonthlyRecurringEventRequest(EventCommonCreate):
    """
    Monthly recurring event on a specific day.
    """

    startDate: str = Field(..., description="Start date (YYYY-MM-DD)")
    endDate: str = Field(..., description="Recurrence end date (YYYY-MM-DD)")
    interval: int = Field(1, ge=1, description="Recur every `interval` months")
    DayofMonth: int = Field(
        ..., ge=1, le=31, description="Absolute day of month (1-31)"
    )


class CreateAbsoluteYearlyRecurringEventRequest(EventCommonCreate):
    """
    Yearly recurring event on a specific day and month.
    """

    startDate: str = Field(..., description="Start date (YYYY-MM-DD)")
    endDate: str = Field(..., description="Recurrence end date (YYYY-MM-DD)")
    interval: int = Field(1, ge=1, description="Recur every `interval` years")
    DayofMonth: int = Field(
        ..., ge=1, le=31, description="Absolute day of month (1-31)"
    )
    MonthofYear: int = Field(..., ge=1, le=12, description="Month of year (1-12)")


# -------------------------
# Update / Delete / Attendee models
# -------------------------
class GetEventsByDateRequest(EventBase):
    """
    Request to fetch events for a given date.
    """

    date: str = Field(..., description="Date in YYYY-MM-DD format")
    timezone: str = Field(..., description="Timezone")


class DeleteEventRequest(EventBase):
    """
    Request to delete an event. Old code locates events by title/date/timezone and then deletes by id.
    """

    title: constr(min_length=1, max_length=200) = Field(
        ..., description="Title/subject of the target event"
    )
    date: str = Field(..., description="Date of the event (YYYY-MM-DD)")
    timezone: str = Field(..., description="Timezone for event lookup")


class EditEventSubjectRequest(EventBase):
    """
    Request to change an event's subject/title.
    `title` = current title, `subject` = new subject (matches old code).
    """

    title: constr(min_length=1, max_length=200) = Field(
        ..., description="Current title"
    )
    date: str = Field(..., description="Date of the event (YYYY-MM-DD)")
    timezone: str = Field(..., description="Timezone for lookup")
    subject: constr(min_length=1, max_length=200) = Field(
        ..., description="New subject/title"
    )


class EditEventDescriptionRequest(EventBase):
    title: constr(min_length=1, max_length=200) = Field(
        ..., description="Current title"
    )
    date: str = Field(..., description="Date of the event (YYYY-MM-DD)")
    timezone: str = Field(..., description="Timezone for lookup")
    description: str = Field(..., description="New description/body content")


class EditEventDateTimeRequest(EventBase):
    """
    Edit event date/time. If the event is recurring, previous code returned 'recurrence' and prevented patch.
    Keep same fields as older implementation.
    """

    title: constr(min_length=1, max_length=200) = Field(
        ..., description="Current title"
    )
    date: str = Field(..., description="Original event date (YYYY-MM-DD)")
    startDate: Optional[str] = Field(None, description="New start date (YYYY-MM-DD)")
    endDate: Optional[str] = Field(
        None,
        description="New end date (YYYY-MM-DD) - used for recurrence end or multi-day events",
    )
    startTime: str = Field(..., description="New start time (HH:MM)")
    endTime: str = Field(..., description="New end time (HH:MM)")
    timezone: str = Field(..., description="Timezone for the new times")


class AddAttendeesRequest(EventBase):
    """
    Add attendees to an existing event identified by title+date+timezone (old behaviour).
    Accepts attendees as list of emails (manager will convert to Graph attendee objects).
    """

    title: constr(min_length=1, max_length=200) = Field(...)
    date: str = Field(..., description="Event date (YYYY-MM-DD)")
    timezone: str = Field(..., description="Timezone")
    attendees: List[EmailStr] = Field(..., description="List of attendee emails to add")


class ModifyAttendeesRequest(AddAttendeesRequest):
    """
    Merge existing attendees with provided ones — old code did this before sending to Graph.
    Inherits fields from AddAttendeesRequest.
    """

    pass


# -------------------------
# Response models
# -------------------------
class EventResponse(BaseModel):
    """
    Response model representing an event returned from the API to the client.
    """

    event_id: str = Field(..., description="Graph event id")
    subject: str
    start: EventTime
    end: EventTime
    body: Optional[EventBody] = None
    location: Optional[EventLocation] = None
    attendees: Optional[List[EventAttendee]] = None
    recurrence: Optional[Recurrence] = None
    created_at: Optional[datetime] = None


class EventsResponse(BaseModel):
    """
    Response wrapper for multiple events (list view).
    """

    events: List[EventResponse]
