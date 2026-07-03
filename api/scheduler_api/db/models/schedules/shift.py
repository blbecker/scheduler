import uuid
from datetime import datetime
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlmodel import Field, Relationship

from scheduler_api.db.models.base import BaseModel
from scheduler_api.db.models.associations.shift_worker_link import ShiftWorkerLink
from scheduler_api.db.models.associations.shift_skill_link import ShiftSkillLink


class Shift(BaseModel, table=True):
    __tablename__ = "shifts"

    schedule_id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("schedules.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        )
    )

    shift_template_id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("shift_templates.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        )
    )

    name: str = Field(sa_column=Column(String, nullable=False))

    start_time: datetime
    end_time: datetime

    schedule: "Schedule" = Relationship(back_populates="shifts")

    workers: list["Worker"] = Relationship(
        back_populates="shifts",
        link_model=ShiftWorkerLink,
    )

    skills: list["Skill"] = Relationship(
        back_populates="shifts",
        link_model=ShiftSkillLink,
    )
