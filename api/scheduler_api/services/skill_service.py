# scheduler_api/services/skill_service.py
from uuid import UUID
from typing import Optional
from sqlmodel import Session

from scheduler_api.repositories.skill_repository import SkillRepository
from scheduler_api.mappers.skill_mapper import to_response, from_create, apply_update
from scheduler_api.schemas.skill import SkillCreate, SkillUpdate, SkillResponse


class SkillService:
    """
    Service for skill operations.

    Services own transaction boundaries.
    Repositories are data access only and never commit/rollback transactions.
    """

    def __init__(self, session: Session):
        """
        Initialize skill service.

        Args:
            session: SQLModel session for database operations
        """
        self.session = session
        self.repo = SkillRepository(session)

    def list_skills(self) -> list[SkillResponse]:
        """
        List all skills.

        Returns:
            List of skill responses
        """
        models = self.repo.get_all()
        return [to_response(model) for model in models]

    def get_skill(self, skill_id: UUID) -> Optional[SkillResponse]:
        """
        Get skill by ID.

        Args:
            skill_id: Skill UUID

        Returns:
            Skill response or None if not found
        """
        skill = self.repo.get_by_id(skill_id)
        return to_response(skill) if skill else None

    def create_skill(self, dto: SkillCreate) -> SkillResponse:
        """
        Create a new skill.

        Args:
            dto: Skill creation data

        Returns:
            Created skill response
        """
        model = from_create(dto)
        saved = self.repo.add(model)
        self.session.flush()
        self.session.commit()
        return to_response(saved)

    def update_skill(self, skill_id: UUID, dto: SkillUpdate) -> Optional[SkillResponse]:
        """
        Update an existing skill.

        Args:
            skill_id: Skill UUID
            dto: Skill update data

        Returns:
            Updated skill response or None if not found
        """
        skill = self.repo.get_by_id(skill_id)
        if not skill:
            return None

        updated = apply_update(skill, dto)
        self.session.flush()
        self.session.commit()
        return to_response(updated)

    def delete_skill(self, skill_id: UUID) -> None:
        """
        Delete a skill.

        Args:
            skill_id: Skill UUID

        Raises:
            ValueError: If skill not found
        """
        skill = self.repo.get_by_id(skill_id)
        if not skill:
            raise ValueError(f"Skill with id {skill_id} not found")
        self.repo.delete(skill)
        self.session.flush()
        self.session.commit()
