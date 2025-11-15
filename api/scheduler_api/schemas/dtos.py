from typing import List
from pydantic import BaseModel
from datetime import time


class SkillDTO(BaseModel):
    id: str
    name: str


class ShiftTemplateDTO(BaseModel):
    id: str
    start_time: time
    end_time: time
    required_skill_ids: List[str]


class ScheduleTemplateDTO(BaseModel):
    id: str
    start_date: str
    end_date: str
    shifts: List[ShiftTemplateDTO]


class WorkerDTO(BaseModel):
    id: str
    name: str
    skill_ids: List[str]
