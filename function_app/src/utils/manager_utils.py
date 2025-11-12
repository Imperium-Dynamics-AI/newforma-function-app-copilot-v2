"""
Manager Validation Utilities - Consolidates validation logic for managers.

This module provides reusable validation functions for business logic operations,
including field validation and error handling patterns.
"""

from src.common.exceptions import ValidationError
from src.logging.logger import get_logger

logger = get_logger(__name__)


def validate_non_empty_string(value: str, field_name: str) -> str:
    """
    Validate that a string value is not empty.

    Args:
        value (str): The value to validate.
        field_name (str): The name of the field for error messages.

    Returns:
        str: The stripped value if valid.

    Raises:
        ValidationError: If the value is empty or whitespace-only.
    """
    if not value or not value.strip():
        logger.warning("Validation failed: %s cannot be empty", field_name)
        raise ValidationError(detail=f"{field_name} cannot be empty")
    return value.strip()


def validate_required_params(**params) -> dict:
    """
    Validate that multiple required parameters are not empty.

    Args:
        **params: Keyword arguments where key is the parameter name and value is the value.

    Returns:
        dict: Dictionary with validated (stripped) values.

    Raises:
        ValidationError: If any parameter is empty or whitespace-only.
    """
    validated = {}
    for param_name, param_value in params.items():
        validated[param_name] = validate_non_empty_string(param_value, param_name)
    return validated
