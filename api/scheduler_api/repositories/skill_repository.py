from typing import List, Optional
from scheduler_api.db.models import Skill
from sqlmodel import Session


class SkillRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_all(self) -> list[Skill]:
        return self.session.query(Skill).all()

    def get_by_id(self, skill_id: int) -> Skill | None:
        return self.session.get(Skill, skill_id)

    def add(self, skill: Skill) -> Skill:
        self.session.add(skill)
        self.session.commit()
        self.session.refresh(skill)
        return skill

    def delete(self, skill_id: int) -> bool:
        obj = self.session.get(Skill, skill_id)
        if not obj:
            return False
        self.session.delete(obj)
        self.session.commit()
        return True
