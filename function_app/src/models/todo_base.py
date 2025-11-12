# handlers/models/todo_base.py
"""
Shared base models for Todo resources.
"""


from pydantic import BaseModel, EmailStr, Field


class TodoBase(BaseModel):
    """
    Base model for Todo resources with common fields.
    """

    user_email: EmailStr = Field(..., description="Owner of the resource")
