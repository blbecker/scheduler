from datetime import time, date
from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID, uuid4
from .associations import ScheduleTemplateShiftLink


class ScheduleTemplate(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    start_date: date
    end_date: date

    shift_templates: List["ShiftTemplate"] = Relationship(
        back_populates="schedule_templates", link_model=ScheduleTemplateShiftLink
    )


class ShiftTemplate(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    start_time: time
    end_time: time

    schedule_templates: List["ScheduleTemplate"] = Relationship(
        back_populates="shift_templates", link_model=ScheduleTemplateShiftLink
    )
