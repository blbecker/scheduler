from datetime import time, date
from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID, uuid4
from .associations import ScheduleTemplateShiftLink


class ScheduleTemplate(SQLModel, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    start_date: date
    end_date: date

    shifts: List["ShiftTemplate"] = Relationship(
        back_populates="schedule_templates", link_model=ScheduleTemplateShiftLink
    )


class ShiftTemplate(SQLModel, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    start_time: time
    end_time: time

    schedule_templates: List["ScheduleTemplate"] = Relationship(
        back_populates="shifts", link_model=ScheduleTemplateShiftLink
    )
