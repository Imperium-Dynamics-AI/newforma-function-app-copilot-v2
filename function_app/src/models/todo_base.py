# handlers/models/todo_base.py
"""
Shared base models for Todo resources.
"""

import re

from pydantic import BaseModel, Field, field_validator


class TodoBase(BaseModel):
    """
    Base model for Todo resources with common fields.
    """

    user_email: str = Field(default=None, description="Owner of the resource")

    @field_validator("email")
    def validate_email(self, v: str) -> str:
        """Validate email format"""
        if not v or "@" not in v:
            raise ValueError("Email must contain '@'")
        if not re.match(r"^[^@]+@[^@]+\.[^@]+$", v):
            raise ValueError("Invalid email format")
        return v.lower()
