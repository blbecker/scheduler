from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlmodel import SQLModel, Field, Relationship, Column, JSON
from uuid import UUID, uuid4
import json


class ScheduleLayout(SQLModel, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(index=True)
    description: Optional[str] = None
    date_range_start: datetime = Field(index=True)
    date_range_end: datetime = Field(index=True)

    # Store worker_ids as JSON array
    worker_ids: List[UUID] = Field(
        default_factory=list, sa_column=Column(JSON, nullable=False, default="[]")
    )

    # Store shift_templates as JSON array
    shift_templates: List[Dict[str, Any]] = Field(
        default_factory=list, sa_column=Column(JSON, nullable=False, default="[]")
    )

    # Store constraints as JSON object
    constraints: Dict[str, Any] = Field(
        default_factory=dict, sa_column=Column(JSON, nullable=False, default="{}")
    )

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ScheduleLayoutUpdate(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None
    date_range_start: Optional[datetime] = None
    date_range_end: Optional[datetime] = None
    worker_ids: Optional[List[UUID]] = None
    shift_templates: Optional[List[Dict[str, Any]]] = None
    constraints: Optional[Dict[str, Any]] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)
