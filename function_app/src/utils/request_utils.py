"""
Request Parsing Utilities - Consolidates request parsing and validation for handlers.

This module provides reusable functions for parsing and validating HTTP request
JSON payloads against Pydantic models.
"""

import azure.functions as func
from src.common.exceptions import ValidationError
from src.logging.logger import get_logger

logger = get_logger(__name__)


def parse_json(req: func.HttpRequest, model):
    """
    Parse JSON from HTTP request and validate against a Pydantic model.

    Args:
        req (func.HttpRequest): The Azure Function HTTP request.
        model: A Pydantic model class to validate the JSON against.

    Returns:
        The validated model instance.

    Raises:
        ValidationError: If JSON is invalid or validation fails.
    """
    try:
        payload = req.get_json()
    except ValueError as exc:
        logger.warning("Invalid JSON payload received")
        raise ValidationError("Invalid JSON payload") from exc

    try:
        return model.model_validate(payload)
    except ValueError as exc:
        logger.warning("Validation error: %s", str(exc))
        raise ValidationError(f"Validation error: {str(exc)}") from exc


def get_required_query_param(req: func.HttpRequest, param_name: str) -> str:
    """
    Get a required query parameter from the request.

    Args:
        req (func.HttpRequest): The Azure Function HTTP request.
        param_name (str): The name of the required parameter.

    Returns:
        str: The parameter value.

    Raises:
        ValidationError: If the parameter is missing.
    """
    value = req.params.get(param_name)
    if not value:
        logger.warning("Query parameter '%s' is required but not provided", param_name)
        raise ValidationError(f"Query parameter '{param_name}' is required")
    return value


def get_required_query_params(req: func.HttpRequest, param_names: list) -> dict:
    """
    Get multiple required query parameters from the request.

    Args:
        req (func.HttpRequest): The Azure Function HTTP request.
        param_names (list): List of parameter names to retrieve.

    Returns:
        dict: Dictionary with parameter names as keys and values.

    Raises:
        ValidationError: If any parameter is missing.
    """
    params = {}
    for param_name in param_names:
        params[param_name] = get_required_query_param(req, param_name)
    return params
