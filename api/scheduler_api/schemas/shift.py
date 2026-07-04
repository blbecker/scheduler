# scheduler_api/schemas/shift.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from uuid import UUID


class Shift(BaseModel):
    schedule_id: UUID
    shift_template_id: UUID
    name: str
    start_time: datetime
    end_time: datetime


class ShiftUpdate(BaseModel):
    schedule_id: Optional[UUID] = None
    shift_template_id: Optional[UUID] = None
    name: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


class ShiftResponse(BaseModel):
    id: UUID
    schedule_id: UUID
    shift_template_id: UUID
    name: str
    start_time: datetime
    end_time: datetime
    created_at: datetime
    updated_at: datetime
