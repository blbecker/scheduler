import uuid
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlmodel import Field, Relationship

from scheduler_api.db.models.base import BaseModel


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

    shifts: list["ShiftModel"] = Relationship(back_populates="schedule")
