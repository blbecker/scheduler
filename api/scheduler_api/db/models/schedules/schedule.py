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

    schedule_solve_id: uuid.UUID | None = Field(
        default=None,
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("schedule_solves.id", ondelete="SET NULL"),
            nullable=True,
            index=True,
        ),
    )

    name: str = Field(sa_column=Column(String, nullable=False))

    shifts: list["ShiftModel"] = Relationship(back_populates="schedule")
