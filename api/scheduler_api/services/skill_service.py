# scheduler_api/services/skill_service.py
from typing import List, Optional
from scheduler_api.models import Skill
from scheduler_api.repositories.skill_repository import SkillRepository


class SkillService:
    def __init__(self, repo: SkillRepository):
        self.repo = repo

    def list_skills(self) -> List[Skill]:
        return self.repo.get_all()

    def get_skill(self, skill_id: int) -> Optional[Skill]:
        return self.repo.get_by_id(skill_id)

    def create_skill(self, name: str, birthdate, email: str = None) -> Skill:
        skill = Skill(name=name, birthdate=birthdate, email=email)
        return self.repo.add(skill)
