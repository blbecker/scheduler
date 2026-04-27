# scheduler_api/services/skill_service.py
from scheduler_api.repositories.skill_repository import SkillRepository
from scheduler_api.mappers.skill_mapper import (
    to_response,
    from_create,
    apply_update,
)
from scheduler_api.schemas.skill import SkillCreate, SkillUpdate, SkillResponse


class SkillService:
    def __init__(self, repo: SkillRepository):
        self.repo = repo

    def list_skills(self) -> list[SkillResponse]:
        return [to_response(s) for s in self.repo.get_all()]

    def get_skill(self, skill_id: int) -> SkillResponse | None:
        skill = self.repo.get_by_id(skill_id)
        return to_response(skill) if skill else None

    def create_skill(self, dto: SkillCreate) -> SkillResponse:
        model = from_create(dto)
        saved = self.repo.add(model)
        return to_response(saved)

    def update_skill(self, skill_id: int, dto: SkillUpdate) -> SkillResponse | None:
        existing = self.repo.get_by_id(skill_id)
        if not existing:
            return None

        updated = apply_update(existing, dto)
        saved = self.repo.add(updated)
        return to_response(saved)

    def delete_skill(self, skill_id: int) -> bool:
        return self.repo.delete(skill_id)
