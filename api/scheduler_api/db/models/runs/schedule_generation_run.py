import uuid
from datetime import datetime
from typing import Any
from sqlalchemy import Column, String, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlmodel import Field

from scheduler_api.db.models.base import BaseModel
from scheduler_api.db.models.enums import ScheduleGenerationStatus


class ScheduleGenerationRunModel(BaseModel, table=True):
    __tablename__ = "schedule_generation_runs"

    schedule_template_id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("schedule_templates.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        )
    )

    schedule_id: uuid.UUID | None = Field(
        default=None,
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("schedules.id", ondelete="SET NULL"),
            nullable=True,
            index=True,
        ),
    )

    status: ScheduleGenerationStatus = Field(
        sa_column=Column(String, nullable=False, index=True)
    )

    started_at: datetime | None = Field(
        sa_column=Column(DateTime(timezone=True), nullable=True)
    )

    finished_at: datetime | None = Field(
        sa_column=Column(DateTime(timezone=True), nullable=True)
    )

    parameters: dict[str, Any] = Field(
        sa_column=Column(JSONB, nullable=False),
        default_factory=dict,
    )
