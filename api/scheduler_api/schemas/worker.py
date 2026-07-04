# scheduler_api/schemas/worker.py
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional


class Worker(BaseModel):
    name: str


class WorkerUpdate(BaseModel):
    name: Optional[str] = None


class WorkerResponse(BaseModel):
    id: UUID
    name: str
    created_at: datetime
    updated_at: datetime
