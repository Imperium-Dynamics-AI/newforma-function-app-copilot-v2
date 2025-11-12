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

    list_name: str = Field(..., min_length=1, max_length=100)
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
    description: Optional[str] = None
    status: str = Field(default="notStarted")
    due_date: Optional[datetime] = None
    created_at: Optional[datetime] = None


class EditTaskRequest(TodoBase):
    """
    Request model for editing a task title.
    """

    list_name: str = Field(..., min_length=1, max_length=100)
    task_name: str = Field(..., min_length=1, max_length=200)
    new_title: str = Field(..., min_length=1, max_length=200)


class UpdateTaskStatusRequest(TodoBase):
    """
    Request model for updating task status.
    """

    list_name: str = Field(..., min_length=1, max_length=100)
    task_name: str = Field(..., min_length=1, max_length=200)
    status: str = Field(
        ..., description="Status: notStarted, inProgress, completed, or waitingOnOthers"
    )


class UpdateTaskDescriptionRequest(TodoBase):
    """
    Request model for updating task description.
    """

    list_name: str = Field(..., min_length=1, max_length=100)
    task_name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None


class UpdateTaskDueDateRequest(TodoBase):
    """
    Request model for updating task due date.
    """

    list_name: str = Field(..., min_length=1, max_length=100)
    task_name: str = Field(..., min_length=1, max_length=200)
    due_date: Optional[datetime] = None
    time_zone: str


class DeleteTaskRequest(TodoBase):
    """
    Request model for deleting a task.
    """

    list_name: str = Field(..., min_length=1, max_length=100)
    task_name: str


class TasksResponse(BaseModel):
    """
    Response model for multiple tasks.
    """

    tasks: List[TaskResponse]
