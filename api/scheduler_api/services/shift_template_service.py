# scheduler_api/services/shift_template_service.py
from uuid import UUID
from typing import Optional
from sqlmodel import Session
from sqlalchemy.exc import IntegrityError

from scheduler_api.repositories.shift_template_repository import ShiftTemplateRepository
from scheduler_api.repositories.skill_repository import SkillRepository
from scheduler_api.mappers.shift_template_mapper import (
    to_response,
    from_create,
    apply_update,
)
from scheduler_api.schemas.shift_template import (
    ShiftTemplateCreate,
    ShiftTemplateResponse,
    ShiftTemplateUpdate,
)


class ShiftTemplateService:
    """
    Service for shift template operations.

    Services own transaction boundaries.
    Repositories are data access only and never commit/rollback transactions.
    """

    def __init__(self, session: Session):
        """
        Initialize shift template service.

        Args:
            session: SQLModel session for database operations
        """
        self.session = session
        self.shift_template_repo = ShiftTemplateRepository(session)
        self.skill_repo = SkillRepository(session)

    def _get_skill_models(self, skill_ids: list[UUID]) -> list:
        """
        Get skill models for the given skill IDs.
        
        Args:
            skill_ids: List of skill UUIDs
            
        Returns:
            List of SkillModel instances
            
        Raises:
            ValueError: If any skill ID is not found (will be caught by DB constraint)
        """
        if not skill_ids:
            return []
        
        # Fetch skill models
        skill_models = self.skill_repo.get_by_ids(skill_ids)
        return skill_models

    def list_shift_templates(self) -> list[ShiftTemplateResponse]:
        """
        List all shift templates.

        Returns:
            List of shift template responses
        """
        models = self.shift_template_repo.get_all()
        return [to_response(model) for model in models]

    def get_shift_template(self, id: UUID) -> Optional[ShiftTemplateResponse]:
        """
        Get shift template by ID.

        Args:
            id: Shift template ID

        Returns:
            Shift template response if found, None otherwise
        """
        model = self.shift_template_repo.get_by_id(id)
        return to_response(model) if model else None

    def create_shift_template(self, dto: ShiftTemplateCreate) -> ShiftTemplateResponse:
        """
        Create a new shift template.

        Args:
            dto: Shift template creation data

        Returns:
            Created shift template response

        Raises:
            ValueError: If database constraint violation occurs (e.g., invalid skill IDs)
        """
        # Create base model without skills
        model = from_create(dto)
        
        # Get skill models for the skill IDs
        skill_models = self._get_skill_models(dto.skill_ids)
        
        # Set the skills relationship - SQLModel will create association records
        model.skills = skill_models
        
        # Save the model
        saved_model = self.shift_template_repo.add(model)
        
        try:
            self.session.flush()
            self.session.commit()
        except IntegrityError as e:
            self.session.rollback()
            raise ValueError(f"Database constraint violation: {str(e)}")
            
        return to_response(saved_model)

    def update_shift_template(
        self, id: UUID, dto: ShiftTemplateUpdate
    ) -> Optional[ShiftTemplateResponse]:
        """
        Update an existing shift template.

        Args:
            id: Shift template ID to update
            dto: Shift template update data

        Returns:
            Updated shift template response if found, None otherwise

        Raises:
            ValueError: If database constraint violation occurs (e.g., invalid skill IDs)
        """
        model = self.shift_template_repo.get_by_id(id)
        if not model:
            return None

        # Update basic fields
        updated_model = apply_update(model, dto)
        
        # Handle skill updates if skill_ids is provided
        if dto.skill_ids is not None:
            # Get skill models for the new skill IDs
            skill_models = self._get_skill_models(dto.skill_ids)
            # Set the skills relationship - SQLModel will update association records
            updated_model.skills = skill_models
        
        self.shift_template_repo.add(updated_model)
        
        try:
            self.session.flush()
            self.session.commit()
        except IntegrityError as e:
            self.session.rollback()
            raise ValueError(f"Database constraint violation: {str(e)}")
            
        return to_response(updated_model)

    def delete_shift_template(self, id: UUID) -> None:
        """
        Delete a shift template.

        Args:
            id: Shift template ID to delete

        Raises:
            ValueError: If shift template not found
        """
        model = self.shift_template_repo.get_by_id(id)
        if not model:
            raise ValueError(f"Shift template with id {id} not found")
        self.shift_template_repo.delete(model)
        self.session.flush()
        self.session.commit()
