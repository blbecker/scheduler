# scheduler_api/schemas/schedule_crud.py
from typing import Optional, List
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

from scheduler_api.schemas.assignment import ShiftAssignmentResponse
from scheduler_api.schemas.shift import ShiftResponse


class ScheduleCreate(BaseModel):
    schedule_template_id: UUID
    name: str


class ScheduleUpdate(BaseModel):
    schedule_template_id: Optional[UUID] = None
    name: Optional[str] = None


class ScheduleResponse(BaseModel):
    id: UUID
    schedule_template_id: UUID
    name: str
    created_at: datetime
    updated_at: datetime


class ScheduleDetailResponse(ScheduleResponse):
    """Schedule response with relationships (shifts and assignments)."""

    shifts: List[ShiftResponse] = []
    shift_assignments: List[ShiftAssignmentResponse] = []


class ScheduleListResponse(BaseModel):
    """List of schedules response."""

    schedules: List[ScheduleResponse] = []
    total: int = 0
