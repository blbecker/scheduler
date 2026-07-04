# scheduler_api/schemas/skill.py
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional


class Skill(BaseModel):
    name: str
    description: Optional[str] = None


class SkillUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class SkillResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime
