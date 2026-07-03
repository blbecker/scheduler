# scheduler_api/schemas/schedule_crud.py
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional


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
