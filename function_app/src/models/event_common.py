# src/models/event_common.py
"""
Reusable Pydantic submodels for Event models.
These mirror the Graph payload shapes (time, body, location, attendees, recurrence).
"""

from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


class EventTime(BaseModel):
    """
    Represents an event time object as used by Microsoft Graph.
    Keep date/time as strings here (manager layer handles parsing/validation).
    dateTime: ISO-like string (YYYY-MM-DDTHH:MM:SS) or the raw strings from the client.
    timeZone: IANA or Windows timezone string (kept flexible).
    """

    dateTime: str = Field(
        ..., description="DateTime string (e.g. 'YYYY-MM-DDTHH:MM:SS')"
    )
    timeZone: str = Field(..., description="Timezone (e.g. 'Asia/Karachi')")


class EventBody(BaseModel):
    """
    Event body payload. contentType should be 'Text' or 'HTML'.
    """

    contentType: str = Field(
        "Text",
        description="Content type: 'Text' or 'HTML'",
        regex=r"^(Text|HTML)$",
    )
    content: str = Field(..., description="Body content")


class EventLocation(BaseModel):
    """
    Simple location wrapper matching Graph's location.displayName usage.
    """

    displayName: str = Field(..., min_length=1, max_length=200)


class EmailAddress(BaseModel):
    """
    Internal emailAddress structure used by Graph attendees.
    """

    address: EmailStr = Field(..., description="Attendee email address")
    name: Optional[str] = Field(None, description="Attendee display name (optional)")


class EventAttendee(BaseModel):
    """
    Graph-style attendee object. Handlers/managers can accept a simpler list of emails
    and convert to this shape before sending to Graph.
    """

    emailAddress: EmailAddress
    type: str = Field(
        "required", description="Attendee type: 'required'|'optional'|'resource'"
    )

    class Config:
        schema_extra = {
            "example": {
                "emailAddress": {"address": "alice@example.com", "name": "Alice"},
                "type": "required",
            }
        }


class RecurrencePattern(BaseModel):
    """
    Recurrence pattern fields. Not all fields are required for every pattern type.
    - type: 'daily', 'weekly', 'absoluteMonthly', 'absoluteYearly', etc.
    - interval: positive integer (default 1)
    - daysOfWeek: used for weekly recurrence (list of weekday names)
    - dayOfMonth: used for absolute monthly/yearly recurrence
    - month: used for absolute yearly recurrence (1-12)
    """

    type: str = Field(
        ...,
        description="Recurrence type (e.g. 'daily','weekly','absoluteMonthly','absoluteYearly')",
    )
    interval: int = Field(
        1, ge=1, description="Recurrence interval (e.g. every X days/weeks/months)"
    )
    daysOfWeek: Optional[List[str]] = Field(
        None, description="List of weekdays for weekly recurrence (e.g. ['Monday'])"
    )
    dayOfMonth: Optional[int] = Field(
        None,
        ge=1,
        le=31,
        description="Day of month for absolute monthly/yearly recurrence",
    )
    month: Optional[int] = Field(
        None,
        ge=1,
        le=12,
        description="Month number for absolute yearly recurrence (1-12)",
    )


class RecurrenceRange(BaseModel):
    """
    Recurrence range describing the start and end date for the recurrence series.
    startDate and endDate are kept as strings (YYYY-MM-DD) — manager will handle parsing.
    """

    type: str = Field(..., description="Range type (e.g. 'endDate')")
    startDate: str = Field(
        ..., description="Start date for the recurrence (YYYY-MM-DD)"
    )
    endDate: str = Field(..., description="End date for the recurrence (YYYY-MM-DD)")


class Recurrence(BaseModel):
    """
    Full recurrence object combining pattern and range.
    """

    pattern: RecurrencePattern
    range: RecurrenceRange
