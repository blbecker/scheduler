from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from uuid import UUID


class ScheduleLayoutCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    date_range_start: datetime
    date_range_end: datetime
    worker_ids: List[UUID] = Field(default_factory=list)
    shift_templates: List[Dict[str, Any]] = Field(default_factory=list)
    constraints: Dict[str, Any] = Field(default_factory=dict)


class ScheduleLayoutUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    date_range_start: Optional[datetime] = None
    date_range_end: Optional[datetime] = None
    worker_ids: Optional[List[UUID]] = None
    shift_templates: Optional[List[Dict[str, Any]]] = None
    constraints: Optional[Dict[str, Any]] = None


class ScheduleLayoutResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    date_range_start: datetime
    date_range_end: datetime
    worker_ids: List[UUID]
    shift_templates: List[Dict[str, Any]]
    constraints: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ScheduleLayoutGenerateResponse(BaseModel):
    layout_id: UUID
    task_id: str
    status: str
    message: str
