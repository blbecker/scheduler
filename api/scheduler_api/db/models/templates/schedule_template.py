from typing import TYPE_CHECKING
from sqlalchemy import Column, String
from sqlmodel import Field, Relationship

from scheduler_api.db.models.base import BaseModel

if TYPE_CHECKING:
    from scheduler_api.db.models.solves.schedule_solve import ScheduleSolveModel
    from scheduler_api.db.models.schedules.schedule import ScheduleModel


class ScheduleTemplateModel(BaseModel, table=True):
    __tablename__ = "schedule_templates"

    name: str = Field(sa_column=Column(String, nullable=False))

    shift_templates: list["ShiftTemplateModel"] = Relationship(
        back_populates="schedule_template"
    )

    schedule_solves: list["ScheduleSolveModel"] = Relationship(
        back_populates="schedule_template"
    )
    schedules: list["ScheduleModel"] = Relationship(back_populates="schedule_template")
