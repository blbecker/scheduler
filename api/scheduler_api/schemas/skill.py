from pydantic import BaseModel
from uuid import UUID


class SkillBase(BaseModel):
    name: str


class SkillCreate(SkillBase):
    pass


class SkillRead(SkillBase):
    id: UUID


class SkillUpdate(SkillBase):
    pass
