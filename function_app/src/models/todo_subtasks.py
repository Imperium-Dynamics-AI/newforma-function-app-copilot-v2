# handlers/models/todo_subtasks.py
"""
Pydantic models for To-Do subtasks.
"""

from datetime import datetime
from typing import List

from pydantic import BaseModel, Field

from src.models.todo_base import TodoBase


class CreateSubtaskRequest(TodoBase):
    """
    Request model for creating a new subtask.
    """

    task_id: str
    title: str = Field(..., min_length=1, max_length=200)


class SubtaskResponse(BaseModel):
    """
    Response model for a single subtask.
    """

    subtask_id: str
    task_id: str
    title: str
    completed: bool
    created_at: datetime


class EditSubtaskRequest(TodoBase):
    """
    Request model for editing a subtask.
    """

    subtask_id: str
    new_title: str = Field(..., min_length=1, max_length=200)


class DeleteSubtaskRequest(TodoBase):
    """
    Request model for deleting a subtask.
    """

    subtask_id: str


class SubtasksResponse(BaseModel):
    """
    Response model for multiple subtasks.
    """

    subtasks: List[SubtaskResponse]
