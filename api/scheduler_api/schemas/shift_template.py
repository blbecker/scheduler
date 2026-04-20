from datetime import time
from typing import Optional
from uuid import UUID
from pydantic import BaseModel


class ShiftTemplateBaseDTO(BaseModel):
    start_time: time
    end_time: time


class ShiftTemplateCreateDTO(ShiftTemplateBaseDTO):
    required_skill_ids: list[UUID]


class ShiftTemplateUpdateDTO(BaseModel):
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    required_skill_ids: Optional[list[UUID]] = None


class ShiftTemplateDTO(ShiftTemplateBaseDTO):
    id: UUID
    required_skill_ids: list[UUID]

    class Config:
        from_attributes = True
