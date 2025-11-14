# src/models/event_base.py
"""
Shared base model for Event resources.
"""

from src.models.todo_base import TodoBase


class EventBase(TodoBase):
    """
    Base model for Event resources. Inherits `user_email` from TodoBase.
    Keeps event models consistent with todo models (user_email required).
    """

    pass
