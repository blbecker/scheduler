# scheduler_api/services/skill_service.py
from typing import List, Optional
from scheduler_api.models import Skill
from scheduler_api.repositories.skill_repository import SkillRepository
from uuid import UUID
from scheduler_api.schemas.skill import SkillCreate, SkillUpdate
from scheduler_api.mappers.skill_mapper import (
    skill_create_to_model,
    skill_update_to_model,
)


class SkillService:
    def __init__(self, repo: SkillRepository):
        self.repo = repo

    def list_skills(self) -> List[Skill]:
        return self.repo.get_all()

    def get_skill(self, skill_id: UUID) -> Optional[Skill]:
        return self.repo.get_by_id(skill_id)

    def create_skill(self, skill: SkillCreate) -> Skill:
        skill_model = skill_create_to_model(skill)
        return self.repo.add(skill_model)

    def update_skill(self, id: UUID, skill: SkillUpdate) -> Optional[Skill]:
        skill_model = skill_update_to_model(skill)
        return self.repo.update(id, skill_model)

    def delete_skill(self, skill_id: UUID) -> bool:
        return self.repo.delete(skill_id)
