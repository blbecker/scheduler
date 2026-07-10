# scheduler_api/schemas/schedule_solve.py
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional, Any
from scheduler_api.db.models.enums import ScheduleSolveStatus


class ScheduleSolveCreate(BaseModel):
    schedule_template_id: UUID
    parameters: dict[str, Any]


class ScheduleSolveUpdate(BaseModel):
    schedule_template_id: Optional[UUID] = None
    schedule_id: Optional[UUID] = None
    status: Optional[ScheduleSolveStatus] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    parameters: Optional[dict[str, Any]] = None
    celery_task_id: Optional[str] = None
    current_generation: Optional[int] = None
    best_fitness: Optional[float] = None
    progress: Optional[float] = None
    error_details: Optional[str] = None


class ScheduleSolveResponse(BaseModel):
    id: UUID
    schedule_template_id: UUID
    schedule_id: Optional[UUID]
    status: ScheduleSolveStatus
    started_at: Optional[datetime]
    finished_at: Optional[datetime]
    parameters: dict[str, Any]
    celery_task_id: Optional[str]
    current_generation: Optional[int]
    best_fitness: Optional[float]
    progress: float
    error_details: Optional[str]
    created_at: datetime
    updated_at: datetime
