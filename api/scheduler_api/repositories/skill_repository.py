from typing import Optional
from uuid import UUID
from sqlmodel import Session, select
from scheduler_api.db.models.core.skill import Skill


class SkillRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_all(self) -> list[Skill]:
        statement = select(Skill)
        result = self.session.exec(statement)
        return list(result.all())

    def get_by_id(self, skill_id: UUID) -> Optional[Skill]:
        return self.session.get(Skill, skill_id)

    def add(self, skill: Skill) -> Skill:
        self.session.add(skill)
        return skill

    def delete(self, skill: Skill) -> None:
        self.session.delete(skill)
