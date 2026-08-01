import uuid
from datetime import datetime
from typing import Any, TYPE_CHECKING
from sqlalchemy import Column, String, ForeignKey, DateTime, Integer, Float
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlmodel import Field, Relationship

from scheduler_api.db.models.base import BaseModel
from scheduler_api.db.models.enums import ScheduleSolveStatus

if TYPE_CHECKING:
    from scheduler_api.db.models.templates.schedule_template import (
        ScheduleTemplateModel,
    )
    from scheduler_api.db.models.schedules.schedule import ScheduleModel


class ScheduleSolveModel(BaseModel, table=True):
    __tablename__ = "schedule_solves"

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

    status: ScheduleSolveStatus = Field(
        sa_column=Column(String, nullable=False, index=True)
    )

    # Celery integration
    celery_task_id: str | None = Field(
        default=None, sa_column=Column(String, nullable=True, index=True)
    )

    # Progress tracking
    current_generation: int | None = Field(
        default=None, sa_column=Column(Integer, nullable=True)
    )

    best_fitness: float | None = Field(
        default=None, sa_column=Column(Float, nullable=True)
    )

    progress: float = Field(default=0.0, sa_column=Column(Float, nullable=False))

    error_details: str | None = Field(
        default=None, sa_column=Column(String, nullable=True)
    )

    # Timestamps
    started_at: datetime | None = Field(
        sa_column=Column(DateTime(timezone=True), nullable=True)
    )

    finished_at: datetime | None = Field(
        sa_column=Column(DateTime(timezone=True), nullable=True)
    )

    # Parameters
    parameters: dict[str, Any] = Field(
        sa_column=Column(JSONB, nullable=False), default_factory=dict
    )

    # Relationships
    schedule_template: "ScheduleTemplateModel" = Relationship(
        back_populates="schedule_solves"
    )
    schedule: "ScheduleModel" = Relationship()
