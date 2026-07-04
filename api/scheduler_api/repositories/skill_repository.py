from typing import Optional
from uuid import UUID
from sqlmodel import Session, select
from scheduler_api.db.models.core.skill import SkillModel


class SkillRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_all(self) -> list[SkillModel]:
        statement = select(SkillModel)
        result = self.session.exec(statement)
        return list(result.all())

    def get_by_id(self, skill_id: UUID) -> Optional[SkillModel]:
        return self.session.get(SkillModel, skill_id)

    def add(self, skill: SkillModel) -> SkillModel:
        self.session.add(skill)
        return skill

    def delete(self, skill: SkillModel) -> None:
        self.session.delete(skill)
