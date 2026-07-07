import uuid
from datetime import datetime
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlmodel import Field, Relationship

from scheduler_api.db.models.base import BaseModel
from scheduler_api.db.models.associations.shift_worker_link import ShiftWorkerLinkModel
from scheduler_api.db.models.associations.shift_skill_link import ShiftSkillLinkModel


class ShiftModel(BaseModel, table=True):
    __tablename__ = "shifts"

    schedule_id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("schedules.id", ondelete="CASCADE"),
            nullable=False,
            index=True)
    )

    shift_template_id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("shift_templates.id", ondelete="CASCADE"),
            nullable=False,
            index=True)
    )

    name: str = Field(sa_column=Column(String, nullable=False))

    start_time: datetime
    end_time: datetime

    schedule: "ScheduleModel" = Relationship(back_populates="shifts")

    workers: list["WorkerModel"] = Relationship(
        back_populates="shifts",
        link_model=ShiftWorkerLinkModel)

    skills: list["SkillModel"] = Relationship(
        back_populates="shifts",
        link_model=ShiftSkillLinkModel)
