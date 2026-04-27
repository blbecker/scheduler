# scheduler_api/schemas/shift.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from uuid import UUID


class ShiftCreate(BaseModel):
    start_time: datetime
    end_time: datetime
    location: Optional[str] = None
    notes: Optional[str] = None


class ShiftUpdate(BaseModel):
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    location: Optional[str] = None
    notes: Optional[str] = None


class ShiftResponse(BaseModel):
    id: UUID
    start_time: datetime
    end_time: datetime
    location: Optional[str]
    notes: Optional[str]
