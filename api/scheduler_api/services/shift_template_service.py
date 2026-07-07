# scheduler_api/services/shift_template_service.py
from uuid import UUID
from typing import Optional
from sqlmodel import Session

from scheduler_api.repositories.shift_template_repository import ShiftTemplateRepository
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
        self.repo = ShiftTemplateRepository(session)

    def list_shift_templates(self) -> list[ShiftTemplateResponse]:
        """
        List all shift templates.

        Returns:
            List of shift template responses
        """
        models = self.repo.get_all()
        return [to_response(model) for model in models]

    def get_shift_template(self, id: UUID) -> Optional[ShiftTemplateResponse]:
        """
        Get shift template by ID.

        Args:
            id: Shift template ID

        Returns:
            Shift template response if found, None otherwise
        """
        model = self.repo.get_by_id(id)
        return to_response(model) if model else None

    def create_shift_template(self, dto: ShiftTemplateCreate) -> ShiftTemplateResponse:
        """
        Create a new shift template.

        Args:
            dto: Shift template creation data

        Returns:
            Created shift template response
        """
        model = from_create(dto)
        saved_model = self.repo.add(model)
        self.session.flush()
        self.session.commit()
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
        """
        model = self.repo.get_by_id(id)
        if not model:
            return None

        updated_model = apply_update(model, dto)
        self.repo.add(updated_model)
        self.session.flush()
        self.session.commit()
        return to_response(updated_model)

    def delete_shift_template(self, id: UUID) -> None:
        """
        Delete a shift template.

        Args:
            id: Shift template ID to delete

        Raises:
            ValueError: If shift template not found
        """
        model = self.repo.get_by_id(id)
        if not model:
            raise ValueError(f"Shift template with id {id} not found")
        self.repo.delete(model)
        self.session.flush()
        self.session.commit()
