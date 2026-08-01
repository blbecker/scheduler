# scheduler_api/schemas/shift.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from uuid import UUID

from scheduler_api.schemas.skill import SkillResponse


class ShiftCreate(BaseModel):
    shift_template_id: UUID
    name: str
    start_time: datetime
    end_time: datetime


class ShiftUpdate(BaseModel):
    shift_template_id: Optional[UUID] = None
    name: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


class ShiftResponse(BaseModel):
    id: UUID
    shift_template_id: UUID
    name: str
    start_time: datetime
    end_time: datetime
    created_at: datetime
    updated_at: datetime


class ShiftDetailResponse(ShiftResponse):
    """Shift response with relationships (skills and assignment)."""

    skills: List[SkillResponse] = []
    assignment: Optional[dict] = None  # Will contain assignment info if exists
