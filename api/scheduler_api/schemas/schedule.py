from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CoalescedShift(BaseModel):
    model_config = ConfigDict(frozen=True)

    worker_id: UUID
    job_id: UUID
    start: datetime
    end: datetime
    slot_indices: tuple[int, ...]


class GenerateScheduleInput(BaseModel):
    total_seconds_to_wait: int = Field(gt=0, le=3600)


class GenerateScheduleResult(BaseModel):
    status: str
    seconds_waited: int
