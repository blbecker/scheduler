from typing import List, Optional
from decimal import Decimal
from datetime import date
from pydantic import BaseModel
from uuid import UUID


class WorkerBase(BaseModel):
    name: str
    birthdate: date
    hourly_rate: Decimal
    email: Optional[str] = None
    phone: Optional[str] = None

    skills: List[UUID]


class WorkerCreate(WorkerBase):
    pass


class WorkerRead(WorkerBase):
    id: UUID


class WorkerUpdate(WorkerBase):
    pass
