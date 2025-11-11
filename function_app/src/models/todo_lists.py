# handlers/models/todo_lists.py
"""
Pydantic models for To-Do lists.
"""

from datetime import datetime
from typing import List

from pydantic import BaseModel, EmailStr, Field

from src.models.todo_base import TodoBase


class CreateListRequest(TodoBase):
    """
    Request model for creating a new To-Do list.
    """

    list_name: str = Field(..., min_length=1, max_length=100)


class ListResponse(BaseModel):
    """
    Response model for a single To-Do list.
    """

    list_id: str
    list_name: str
    user_email: EmailStr
    created_at: datetime


class EditListRequest(TodoBase):
    """
    Request model for editing a To-Do list.
    """

    list_id: str
    new_name: str = Field(..., min_length=1, max_length=100)


class DeleteListRequest(TodoBase):
    """
    Request model for deleting a To-Do list.
    """

    list_id: str


class ListsResponse(BaseModel):
    """
    Response model for multiple To-Do lists.
    """

    lists: List[ListResponse]
