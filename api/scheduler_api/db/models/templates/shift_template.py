import uuid
from datetime import time
from sqlalchemy import Column, String, Time, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlmodel import Field, Relationship

from scheduler_api.db.models.base import BaseModel


class ShiftTemplateModel(BaseModel, table=True):
    __tablename__ = "shift_templates"

    schedule_template_id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("schedule_templates.id", ondelete="CASCADE"),
            nullable=False,
            index=True)
    )

    name: str = Field(sa_column=Column(String, nullable=False))
    start_time: time = Field(sa_column=Column(Time, nullable=False))
    end_time: time = Field(sa_column=Column(Time, nullable=False))

    schedule_template: "ScheduleTemplateModel" = Relationship(
        back_populates="shift_templates"
    )
