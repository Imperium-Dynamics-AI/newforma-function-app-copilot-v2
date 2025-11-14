"""
Module for registering Calendar Events routes in the Azure Function App.

This module defines 4 main HTTP endpoints for event management:
- POST /events/create - Create events (normal & recurring)
- POST /events/get - Get events by date
- PUT /events/edit - Edit any event property (unified)
- DELETE /events/delete - Delete events
"""

import azure.functions as func

from src.dependencies import get_events_handler


def register_events_routes(app: func.FunctionApp):
    """
    Register HTTP routes for Calendar Events operations.
    
    Registers 4 simple endpoints with flexible backend logic:
    1. Create - handles both one-time and recurring events
    2. Get - retrieves events by date
    3. Edit - unified endpoint for all event updates
    4. Delete - removes events

    Args:
        app (func.FunctionApp): The Azure FunctionApp instance to register routes on.
    """

    @app.function_name(name="create_event")
    @app.route(route="events/create", methods=["POST"])
    async def create_event(req: func.HttpRequest) -> func.HttpResponse:
        """
        Handle POST /events/create
        
        Universal event creation endpoint that handles:
        - One-time events (with 'date' field)
        - Recurring events (with 'recurrence' object or specific recurrence fields)
        
        Backend automatically detects event type and routes to appropriate logic.
        
        Returns:
            func.HttpResponse: JSON with created event data (201) or error.
        """
        handler = get_events_handler()
        return await handler.create_event(req)

    @app.function_name(name="get_events")
    @app.route(route="events/get", methods=["POST"])
    async def get_events(req: func.HttpRequest) -> func.HttpResponse:
        """
        Handle POST /events/get
        
        Retrieves all events for a specific date.
        
        Expected JSON body: { user_email, date, timezone }
        
        Returns:
            func.HttpResponse: JSON with list of events (200) or error.
        """
        handler = get_events_handler()
        return await handler.get_events(req)

    @app.function_name(name="edit_event")
    @app.route(route="events/edit", methods=["PUT"])
    async def edit_event(req: func.HttpRequest) -> func.HttpResponse:
        """
        Handle PUT /events/edit
        
        Unified endpoint for editing any event property.
        Accepts optional fields and only updates provided fields:
        - subject: Update event title
        - description: Update event body
        - startTime/endTime/startDate/endDate: Update event timing
        - attendees: Update attendees (with action: 'add' or 'replace')
        - location: Update event location
        
        Backend routes to specific granular functions based on provided fields.
        Uses Microsoft Graph's PATCH capability to update multiple fields in one call.
        
        Expected JSON body: { user_email, title, date, timezone, ...optional fields }
        
        Returns:
            func.HttpResponse: JSON with success message (200) or error.
        """
        handler = get_events_handler()
        return await handler.edit_event(req)

    @app.function_name(name="delete_event")
    @app.route(route="events/delete", methods=["DELETE"])
    async def delete_event(req: func.HttpRequest) -> func.HttpResponse:
        """
        Handle DELETE /events/delete
        
        Deletes a calendar event by title and date.
        
        Expected JSON body: { user_email, title, date, timezone }
        
        Returns:
            func.HttpResponse: JSON with success message (200) or error.
        """
        handler = get_events_handler()
        return await handler.delete_event(req)
