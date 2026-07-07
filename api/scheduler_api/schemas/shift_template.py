# scheduler_api/schemas/shift_template.py
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime, time
from typing import Optional


class ShiftTemplateCreate(BaseModel):
    schedule_template_id: UUID
    name: str
    start_time: time
    end_time: time


class ShiftTemplateUpdate(BaseModel):
    schedule_template_id: Optional[UUID] = None
    name: Optional[str] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None


class ShiftTemplateResponse(BaseModel):
    id: UUID
    schedule_template_id: UUID
    name: str
    start_time: time
    end_time: time
    created_at: datetime
    updated_at: datetime
