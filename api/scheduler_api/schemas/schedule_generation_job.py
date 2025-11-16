from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel


class ScheduleGenerationJobCreateDTO(BaseModel):
    schedule_template_id: UUID
    scorer_ids: list[UUID] = []
    notes: Optional[str] = None


class ScheduleGenerationJobDTO(BaseModel):
    id: UUID
    schedule_template_id: UUID

    status: str  # pending | running | completed | failed | cancelled
    progress: Optional[float] = None  # 0.0–1.0

    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None

    result_schedule_id: Optional[UUID] = None

    notes: Optional[str] = None

    class Config:
        from_attributes = True
