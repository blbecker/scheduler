# scheduler_api/schemas/schedule_template.py
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional, List


class ScheduleTemplate(BaseModel):
    name: str


class ScheduleTemplateUpdate(BaseModel):
    name: Optional[str] = None


class ScheduleTemplateResponse(BaseModel):
    id: UUID
    name: str
    created_at: datetime
    updated_at: datetime
