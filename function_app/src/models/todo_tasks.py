# handlers/models/todo_tasks.py
"""
Pydantic models for To-Do tasks.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from src.models.todo_base import TodoBase


class CreateTaskRequest(TodoBase):
    """
    Request model for creating a new task.
    """

    list_id: str
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    time_zone: str


class TaskResponse(BaseModel):
    """
    Response model for a single task.
    """

    task_id: str
    list_id: str
    title: str
    description: Optional[str]
    status: str = Field(..., pattern="^(pending|completed)$")
    due_date: Optional[datetime]
    created_at: datetime
    time_zone: str


class EditTaskRequest(TodoBase):
    """
    Request model for editing a task title.
    """

    task_id: str
    new_title: str = Field(..., min_length=1, max_length=200)


class UpdateTaskStatusRequest(TodoBase):
    """
    Request model for updating task status.
    """

    task_id: str
    status: str = Field(..., pattern="^(pending|completed)$")


class UpdateTaskDescriptionRequest(TodoBase):
    """
    Request model for updating task description.
    """

    task_id: str
    description: Optional[str] = None


class UpdateTaskDueDateRequest(TodoBase):
    """
    Request model for updating task due date.
    """

    task_id: str
    due_date: Optional[datetime] = None
    time_zone: str


class DeleteTaskRequest(TodoBase):
    """
    Request model for deleting a task.
    """

    task_id: str


class TasksResponse(BaseModel):
    """
    Response model for multiple tasks.
    """

    tasks: List[TaskResponse]
