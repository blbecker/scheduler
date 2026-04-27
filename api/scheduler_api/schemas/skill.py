# scheduler_api/schemas/skill.py
from pydantic import BaseModel
from uuid import UUID
from typing import Optional


class SkillCreate(BaseModel):
    name: str


class SkillUpdate(BaseModel):
    name: Optional[str] = None


class SkillResponse(BaseModel):
    id: UUID
    name: str