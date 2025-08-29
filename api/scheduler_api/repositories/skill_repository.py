from typing import List, Optional
from sqlmodel import select
from scheduler_api.models import Skill
from scheduler_api.db import get_session


class SkillRepository:
    def get_all(self) -> List[Skill]:
        with get_session() as session:
            return session.exec(select(Skill)).all()

    def get_by_id(self, skill_id: int) -> Optional[Skill]:
        with get_session() as session:
            return session.get(Skill, skill_id)

    def add(self, skill: Skill) -> Skill:
        with get_session() as session:
            session.add(skill)
            session.commit()
            session.refresh(skill)
            return skill
