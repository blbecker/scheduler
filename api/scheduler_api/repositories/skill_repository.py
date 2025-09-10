from typing import List, Optional
from scheduler_api.models import Skill
from sqlmodel import Session


class SkillRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_all(self) -> List[Skill]:
        with self.session as session:
            return session.query(Skill).all()

    def get_by_id(self, skill_id: int) -> Optional[Skill]:
        with self.session as session:
            return session.get(Skill, skill_id)

    def add(self, skill: Skill) -> Skill:
        with self.session as session:
            session.add(skill)
            session.commit()
            session.refresh(skill)
            return skill

    def update(self, skill: Skill) -> Optional[Skill]:
        with self.session as session:
            existing_skill = session.get(Skill, skill.id)
            if existing_skill is None:
                return None
            skill_data = skill.dict(exclude_unset=True)
            for key, value in skill_data.items():
                setattr(existing_skill, key, value)
            session.add(existing_skill)
            session.commit()
            session.refresh(existing_skill)
            return existing_skill

    def delete(self, skill_id: int) -> bool:
        with self.session as session:
            skill = session.get(Skill, skill_id)
            if skill is None:
                return False
            session.delete(skill)
            session.commit()
            return True
