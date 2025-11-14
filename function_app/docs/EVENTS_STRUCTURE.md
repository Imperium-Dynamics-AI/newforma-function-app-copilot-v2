# Events Functionality Structure - Implementation Guide

## Overview
This document outlines the complete structure for the Calendar Events functionality, following the exact architectural pattern established by the TODO functionality.

## Architecture Layers

The Events functionality follows a 5-layer architecture:

```
Routes → Handler → Manager → Repository → GraphClient → Microsoft Graph API
```

### Layer Responsibilities

1. **Routes Layer** (`src/routes/events_routes.py`)
   - Registers HTTP endpoints with Azure Function App
   - Maps routes to handler methods
   - Minimal logic - just routing

2. **Handler Layer** (`src/handlers/events_handler.py`)
   - Processes HTTP requests
   - Parses JSON body and validates with Pydantic models
   - Calls manager methods
   - Returns formatted JSON responses with appropriate status codes
   - Handles exceptions and converts to HTTP error responses

3. **Manager Layer** (`src/managers/events_manager.py`)
   - Contains business logic and validation rules
   - Transforms request models to repository method calls
   - Converts simple formats (email lists) to Graph API formats (attendee objects)
   - Handles domain-specific error cases
   - Logs operations

4. **Repository Layer** (`src/repositories/events_repository.py`)
   - Direct interaction with Microsoft Graph API via GraphClient
   - Performs CRUD operations on calendar events
   - Constructs Graph API endpoints using URLBuilder
   - Handles low-level data transformations
   - Minimal business logic

5. **Models Layer** (`src/models/event_*.py`) - Already exists
   - Pydantic models for request/response validation
   - Type definitions for common event structures

## Files Created

### 1. `src/repositories/events_repository.py`
**Purpose**: Data access layer for calendar events

**Key Methods**:
- `create_event()` - Create one-time or recurring events
- `get_events_by_date_range()` - Query events by date/time range
- `get_event_by_title_and_date()` - Find specific event by title and date
- `update_event_subject()` - Update event title
- `update_event_description()` - Update event body/description
- `update_event_datetime()` - Update event start/end times
- `add_attendees_to_event()` - Add attendees to existing event
- `modify_event_attendees()` - Replace entire attendees list
- `delete_event()` - Delete calendar event
- `get_event_by_id()` - Retrieve event by ID

**Dependencies**: GraphClient, URLBuilder

### 2. `src/managers/events_manager.py`
**Purpose**: Business logic layer for events

**Key Methods**:

**Creation Methods**:
- `create_one_time_event()` - Create non-recurring event
- `create_recurring_event()` - Create generic recurring event
- `create_daily_recurring_event()` - Daily recurrence
- `create_weekly_recurring_event()` - Weekly recurrence on specific days
- `create_monthly_recurring_event()` - Monthly recurrence on specific day
- `create_yearly_recurring_event()` - Yearly recurrence on specific day/month

**Query Methods**:
- `get_events_by_date()` - Get all events for a specific date

**Update Methods**:
- `edit_event_subject()` - Update event title
- `edit_event_description()` - Update event description
- `edit_event_datetime()` - Update event date/time
- `add_attendees()` - Add attendees
- `modify_attendees()` - Replace attendees list

**Delete Methods**:
- `delete_event()` - Delete event by title and date

**Helper Methods**:
- `_convert_attendees_to_graph_format()` - Transform email list to Graph attendee objects
- `_build_recurrence_object()` - Construct recurrence configuration
- `_validate_time_range()` - Validate start/end times
- `_combine_date_and_time()` - Merge date and time strings to ISO format

**Dependencies**: EventsRepository

### 3. `src/handlers/events_handler.py`
**Purpose**: HTTP request handler

**Key Methods** (all async):
- `create_one_time_event()` - POST handler for one-time events
- `create_recurring_event()` - POST handler for generic recurring events
- `create_daily_recurring_event()` - POST handler for daily recurrence
- `create_weekly_recurring_event()` - POST handler for weekly recurrence
- `create_monthly_recurring_event()` - POST handler for monthly recurrence
- `create_yearly_recurring_event()` - POST handler for yearly recurrence
- `get_events_by_date()` - POST handler to retrieve events by date
- `edit_event_subject()` - PUT handler to update title
- `edit_event_description()` - PUT handler to update description
- `edit_event_datetime()` - PUT handler to update date/time
- `add_attendees()` - POST handler to add attendees
- `modify_attendees()` - PUT handler to replace attendees
- `delete_event()` - DELETE handler to delete event

**Dependencies**: EventsManager

### 4. `src/routes/events_routes.py`
**Purpose**: Route registration

**Registered Endpoints**:

| Route | Method | Function | Purpose |
|-------|--------|----------|---------|
| `/events/create` | POST | `create_one_time_event` | Create one-time event |
| `/events/create/recurring` | POST | `create_recurring_event` | Create recurring event (generic) |
| `/events/create/recurring/daily` | POST | `create_daily_recurring_event` | Create daily recurring event |
| `/events/create/recurring/weekly` | POST | `create_weekly_recurring_event` | Create weekly recurring event |
| `/events/create/recurring/monthly` | POST | `create_monthly_recurring_event` | Create monthly recurring event |
| `/events/create/recurring/yearly` | POST | `create_yearly_recurring_event` | Create yearly recurring event |
| `/events/date` | POST | `get_events_by_date` | Get events for specific date |
| `/events/edit/subject` | PUT | `edit_event_subject` | Update event title |
| `/events/edit/description` | PUT | `edit_event_description` | Update event description |
| `/events/edit/datetime` | PUT | `edit_event_datetime` | Update event date/time |
| `/events/attendees/add` | POST | `add_attendees` | Add attendees to event |
| `/events/attendees/modify` | PUT | `modify_attendees` | Replace attendees list |
| `/events/delete` | DELETE | `delete_event` | Delete event |

**Dependencies**: EventsHandler (via get_events_handler)

## Files Modified

### 1. `src/common/exceptions.py`
**Added Event-specific Exceptions**:
- `EventNotFoundError` - When event doesn't exist
- `DuplicateEventError` - When duplicate event creation attempted
- `InvalidTimeRangeError` - When end time is before start time
- `InvalidRecurrenceError` - When recurrence configuration is invalid

### 2. `src/dependencies.py`
**Added Factory Functions**:
- `get_events_repository()` - Creates EventsRepository with GraphClient
- `get_events_manager()` - Creates EventsManager with EventsRepository
- `get_events_handler()` - Creates EventsHandler with EventsManager

### 3. `function_app.py`
**Updated to Register Events Routes**:
- Imported `events_routes`
- Called `events_routes.register_events_routes(app)`

## Data Flow Example

### Creating a One-Time Event

1. **Client Request**: POST to `/events/create` with JSON body
2. **Route Layer**: `events_routes.create_one_time_event()` receives request
3. **Handler Layer**: `EventsHandler.create_one_time_event()`
   - Parses JSON with `parse_json(req, CreateEventRequest)`
   - Validates with Pydantic model
   - Calls manager method
4. **Manager Layer**: `EventsManager.create_one_time_event()`
   - Validates business rules (subject not empty, times valid)
   - Combines date and time strings
   - Converts attendee emails to Graph format
   - Calls repository method
5. **Repository Layer**: `EventsRepository.create_event()`
   - Builds Graph API endpoint URL
   - Constructs Graph API payload
   - Makes HTTP POST via GraphClient
   - Returns formatted response
6. **Response Flow**: Returns through layers
   - Manager logs success and returns data
   - Handler wraps in JSON response with 201 status
   - Route returns HttpResponse to client

## Request/Response Models

All models are already defined in `src/models/event_events.py`:

**Request Models**:
- `CreateEventRequest` - One-time event
- `CreateRecurringEventRequest` - Generic recurring
- `CreateDailyRecurringEventRequest` - Daily recurring
- `CreateWeeklyRecurringEventRequest` - Weekly recurring
- `CreateAbsoluteMonthlyRecurringEventRequest` - Monthly recurring
- `CreateAbsoluteYearlyRecurringEventRequest` - Yearly recurring
- `GetEventsByDateRequest` - Query by date
- `DeleteEventRequest` - Delete event
- `EditEventSubjectRequest` - Update title
- `EditEventDescriptionRequest` - Update description
- `EditEventDateTimeRequest` - Update date/time
- `AddAttendeesRequest` - Add attendees
- `ModifyAttendeesRequest` - Replace attendees

**Response Models**:
- `EventResponse` - Single event response
- `EventsResponse` - Multiple events response

**Common Models** (in `event_common.py`):
- `EventTime` - DateTime and timezone
- `EventBody` - Content and content type
- `EventLocation` - Location display name
- `EmailAddress` - Email and name
- `EventAttendee` - Full attendee object
- `RecurrencePattern` - Recurrence pattern config
- `RecurrenceRange` - Recurrence range config
- `Recurrence` - Complete recurrence object

## Error Handling Pattern

Following TODO pattern:

```python
try:
    # Validate input
    validated_data = validate_input(data)
    
    # Call repository
    result = await self.repo.some_method(validated_data)
    
    # Log success
    logger.info("Operation succeeded")
    
    return result
    
except (ValidationError, EventNotFoundError, DuplicateEventError):
    # Re-raise domain exceptions
    raise
    
except Exception as e:
    # Log unexpected errors
    logger.error("Unexpected error: %s", str(e), exc_info=True)
    # Wrap in TodoAPIError
    raise TodoAPIError(detail=str(e)) from e
```

## Dependency Injection Flow

```
get_events_handler()
  └─> get_events_manager()
       └─> get_events_repository()
            └─> get_graph_client()
                 └─> get_auth_manager()
```

## Implementation Status

✅ **Completed**:
- All model definitions (event_base.py, event_common.py, event_events.py)
- Repository structure with full docstrings
- Manager structure with full docstrings
- Handler structure with full docstrings
- Route definitions
- Exception definitions
- Dependency injection setup
- Function app registration

⏳ **Pending** (Implementation logic to be added):
- Repository method implementations (GraphClient calls)
- Manager method implementations (business logic)
- Handler method implementations (request parsing and response formatting)

## Next Steps for Implementation

When implementing the actual logic:

1. **Start with Repository Layer**:
   - Implement GraphClient calls
   - Test with Graph API
   - Handle Graph API errors

2. **Implement Manager Layer**:
   - Add business validation
   - Implement data transformations
   - Add error handling and logging

3. **Implement Handler Layer**:
   - Parse requests with Pydantic models
   - Call manager methods
   - Format responses

4. **Testing**:
   - Unit tests for each layer
   - Integration tests for complete flows
   - Test error scenarios

## Consistency with TODO Pattern

The Events functionality maintains exact consistency with TODO:

- ✅ Same architectural layers
- ✅ Same naming conventions
- ✅ Same error handling patterns
- ✅ Same dependency injection approach
- ✅ Same logging strategy
- ✅ Same request/response patterns
- ✅ Same validation approach
- ✅ Same documentation style

## Key Design Decisions

1. **Events identified by title + date**: Like tasks are identified by name within a list, events are identified by their title and date for operations.

2. **Attendees as email lists**: Simple email string lists in requests are converted to Graph attendee objects in the manager layer.

3. **Multiple recurrence creation methods**: Specific methods for daily/weekly/monthly/yearly provide convenience, while generic method offers flexibility.

4. **Timezone handling**: All date/time operations include timezone parameter for proper handling across different locations.

5. **Content type flexibility**: Events support both Text and HTML body content types.

## Important Notes

- All function signatures include proper type hints
- All classes and methods have detailed docstrings
- Error handling follows the established exception hierarchy
- Logging is consistent throughout
- The structure is ready for implementation - just add the `pass` statement logic
