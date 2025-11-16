from datetime import date
from typing import Optional
from uuid import UUID
from pydantic import BaseModel

from scheduler_api.schemas.shift_template import (
    ShiftTemplateDTO,
    ShiftTemplateCreateDTO,
    ShiftTemplateUpdateDTO,
)


class ScheduleTemplateBaseDTO(BaseModel):
    start_date: date
    end_date: date


class ScheduleTemplateCreateDTO(ScheduleTemplateBaseDTO):
    shifts: list[ShiftTemplateCreateDTO]


class ScheduleTemplateUpdateDTO(BaseModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    shifts: Optional[list[ShiftTemplateUpdateDTO]] = None


class ScheduleTemplateDTO(ScheduleTemplateBaseDTO):
    id: UUID
    shifts: list[ShiftTemplateDTO]

    class Config:
        from_attributes = True
