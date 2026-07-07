from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, Field
from uuid import UUID


class ScheduleLayoutCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    date_range_start: datetime
    date_range_end: datetime
    worker_ids: list[UUID] = Field(default_factory=list)
    shift_templates: list[dict[str, Any]] = Field(default_factory=list)
    constraints: dict[str, Any] = Field(default_factory=dict)


class ScheduleLayoutUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    date_range_start: Optional[datetime] = None
    date_range_end: Optional[datetime] = None
    worker_ids: Optional[list[UUID]] = None
    shift_templates: Optional[list[dict[str, Any]]] = None
    constraints: Optional[dict[str, Any]] = None


class ScheduleLayoutResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    date_range_start: datetime
    date_range_end: datetime
    worker_ids: list[UUID]
    shift_templates: list[dict[str, Any]]
    constraints: dict[str, Any]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ScheduleLayoutGenerateResponse(BaseModel):
    layout_id: UUID
    task_id: str
    status: str
    message: str
