# scheduler_api/schemas/worker.py
from pydantic import BaseModel
from uuid import UUID
from datetime import date
from typing import Optional


class WorkerCreate(BaseModel):
    name: str
    birthdate: date
    email: Optional[str] = None
    phone: Optional[str] = None


class WorkerUpdate(BaseModel):
    name: Optional[str] = None
    birthdate: Optional[date] = None
    email: Optional[str] = None
    phone: Optional[str] = None


class WorkerResponse(BaseModel):
    id: UUID
    name: str
    birthdate: date
    email: Optional[str]
    phone: Optional[str]