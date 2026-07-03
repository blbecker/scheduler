from sqlalchemy import Column, String
from sqlmodel import Field, Relationship

from scheduler_api.db.models.base import BaseModel


class ScheduleTemplate(BaseModel, table=True):
    __tablename__ = "schedule_templates"

    name: str = Field(sa_column=Column(String, nullable=False))

    shift_templates: list["ShiftTemplate"] = Relationship(
        back_populates="schedule_template"
    )
