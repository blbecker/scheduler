import uuid
from typing import TYPE_CHECKING
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlmodel import Field, Relationship

from scheduler_api.db.models.base import BaseModel

if TYPE_CHECKING:
    from scheduler_api.db.models.templates.schedule_template import (
        ScheduleTemplateModel,
    )
    from scheduler_api.db.models.assignments.shift_assignment import (
        ShiftAssignmentModel,
    )


class ScheduleModel(BaseModel, table=True):
    __tablename__ = "schedules"

    schedule_template_id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("schedule_templates.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        )
    )

    name: str = Field(sa_column=Column(String, nullable=False))

    shift_assignments: list["ShiftAssignmentModel"] = Relationship(
        back_populates="schedule",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )

    schedule_template: "ScheduleTemplateModel" = Relationship(
        back_populates="schedules"
    )
