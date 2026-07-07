# scheduler_api/schemas/schedule_generation_run.py
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional, Any
from scheduler_api.db.models.enums import ScheduleGenerationStatus


class ScheduleGenerationRunCreate(BaseModel):
    schedule_template_id: UUID
    parameters: dict[str, Any]


class ScheduleGenerationRunUpdate(BaseModel):
    schedule_template_id: Optional[UUID] = None
    schedule_id: Optional[UUID] = None
    status: Optional[ScheduleGenerationStatus] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    parameters: Optional[dict[str, Any]] = None


class ScheduleGenerationRunResponse(BaseModel):
    id: UUID
    schedule_template_id: UUID
    schedule_id: Optional[UUID]
    status: ScheduleGenerationStatus
    started_at: Optional[datetime]
    finished_at: Optional[datetime]
    parameters: dict[str, Any]
    created_at: datetime
    updated_at: datetime
