from typing import List, Optional
from scheduler_api.models import Skill
from sqlmodel import Session
from uuid import UUID
import logging

logger = logging.getLogger(__name__)


class SkillRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_all(self) -> List[Skill]:
        return self.session.query(Skill).all()

    def get_by_id(self, skill_id: int) -> Optional[Skill]:
        return self.session.get(Skill, skill_id)

    def add(self, skill: Skill) -> Skill:
        logger.debug(f"Adding new skill: {skill}")
        self.session.add(skill)
        self.session.commit()
        self.session.refresh(skill)
        return skill

    def update(self, id: UUID, skill: Skill) -> Optional[Skill]:
        existing_skill = self.session.get(Skill, id)
        if existing_skill is None:
            return None
        skill_data = skill.model_dump(exclude_unset=True)
        for key, value in skill_data.items():
            setattr(existing_skill, key, value)
        self.session.add(existing_skill)
        self.session.commit()
        self.session.refresh(existing_skill)
        return existing_skill

    def delete(self, skill_id: int) -> bool:
        skill = self.session.get(Skill, skill_id)
        if skill is None:
            return False
        self.session.delete(skill)
        self.session.commit()
        return True
