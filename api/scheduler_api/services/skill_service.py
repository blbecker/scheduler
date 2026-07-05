# scheduler_api/services/skill_service.py
from uuid import UUID
from typing import List, Optional
from fastapi import HTTPException, status

from scheduler_api.repositories.skill_repository import SkillRepository
from scheduler_api.mappers.skill_mapper import (
    to_response,
    from_create,
    apply_update,
)
from scheduler_api.schemas.skill import Skill, SkillUpdate, SkillResponse


class SkillService:
    def __init__(self, repo: SkillRepository):
        self.repo = repo

    def list_skills(self) -> List[SkillResponse]:
        repo = self.repo
        models = repo.get_all()
        return [to_response(s) for s in models]

    def get_skill(self, skill_id: UUID) -> Optional[SkillResponse]:
        repo = self.repo
        skill = repo.get_by_id(skill_id)
        return to_response(skill) if skill else None

    def create_skill(self, dto: Skill) -> SkillResponse:
        repo = self.repo
        model = from_create(dto)
        saved = repo.add(model)
        return to_response(saved)

    def update_skill(self, skill_id: UUID, dto: SkillUpdate) -> Optional[SkillResponse]:
        repo = self.repo
        existing = repo.get_by_id(skill_id)
        if not existing:
            return None

        updated = apply_update(existing, dto)
        saved = repo.add(updated)
        return to_response(saved)

    def delete_skill(self, skill_id: UUID) -> None:
        repo = self.repo
        skill = repo.get_by_id(skill_id)
        if not skill:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Skill with id {skill_id} not found",
            )
        repo.delete(skill)
        # No flush needed for delete operations
