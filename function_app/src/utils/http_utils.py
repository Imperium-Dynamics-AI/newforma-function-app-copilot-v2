"""
HTTP Response Utilities - Consolidates HTTP response formatting for handlers.

This module provides reusable functions for formatting HTTP responses with
proper headers and JSON serialization.
"""

import json
import azure.functions as func


def json_response(data: dict, status: int = 200) -> func.HttpResponse:
    """
    Return a JSON HTTP response with correct headers.

    Args:
        data (dict): The data to serialize as JSON.
        status (int): The HTTP status code. Defaults to 200.

    Returns:
        func.HttpResponse: An Azure Function HTTP response with JSON content type.
    """
    return func.HttpResponse(
        body=json.dumps(data, default=str),
        status_code=status,
        mimetype="application/json",
        headers={"Content-Type": "application/json"},
    )
