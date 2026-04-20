from pydantic import BaseModel
from uuid import UUID
from typing import List, Optional
from datetime import datetime


class ShiftBase(BaseModel):
    start_time: datetime
    end_time: datetime
    location: Optional[str] = None
    notes: Optional[str] = None

    skills: List[UUID]
    workers: List[UUID]


class ShiftCreate(ShiftBase):
    pass


class ShiftRead(ShiftBase):
    id: UUID


class ShiftUpdate(ShiftBase):
    pass
