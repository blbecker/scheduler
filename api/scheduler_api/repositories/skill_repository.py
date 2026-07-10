from typing import Optional, Sequence
from uuid import UUID
from sqlmodel import Session, select
from sqlalchemy.sql.expression import any_
from scheduler_api.db.models.core.skill import SkillModel


class SkillRepository:
    """
    Repository for skill data access.

    Repositories are responsible for data access only.
    They never commit or rollback transactions - services own transaction boundaries.
    """

    def __init__(self, session: Session):
        self.session = session

    def get_all(self) -> list[SkillModel]:
        """Get all skills."""
        statement = select(SkillModel)
        result = self.session.exec(statement)
        return list(result.all())

    def get_by_id(self, skill_id: UUID) -> Optional[SkillModel]:
        """Get skill by ID."""
        return self.session.get(SkillModel, skill_id)

    def get_by_ids(self, skill_ids: Sequence[UUID]) -> list[SkillModel]:
        """Get skills by IDs."""
        if not skill_ids:
            return []
        
        # Convert UUIDs to strings for the IN clause
        statement = select(SkillModel).where(SkillModel.id.in_(skill_ids))
        result = self.session.exec(statement)
        return list(result.all())

    def add(self, skill: SkillModel) -> SkillModel:
        """
        Add a skill to the session.

        Note: Does not commit - service owns transaction boundaries.
        """
        self.session.add(skill)
        # No commit - service owns transaction
        return skill

    def delete(self, skill: SkillModel) -> None:
        """
        Delete a skill from the session.

        Note: Does not commit - service owns transaction boundaries.
        """
        self.session.delete(skill)
        # No commit - service owns transaction
