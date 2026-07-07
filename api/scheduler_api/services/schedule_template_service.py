# scheduler_api/services/schedule_template_service.py
from uuid import UUID
from typing import Optional
from sqlmodel import Session

from scheduler_api.repositories.schedule_template_repository import (
    ScheduleTemplateRepository,
)
from scheduler_api.mappers.schedule_template_mapper import (
    to_response,
    from_create,
    apply_update,
)
from scheduler_api.schemas.schedule_template import (
    ScheduleTemplateCreate,
    ScheduleTemplateResponse,
    ScheduleTemplateUpdate,
)


class ScheduleTemplateService:
    """
    Service for schedule template operations.

    Services own transaction boundaries.
    Repositories are data access only and never commit/rollback transactions.
    """

    def __init__(self, session: Session):
        """
        Initialize schedule template service.

        Args:
            session: SQLModel database session
        """
        self.session = session
        self.repo = ScheduleTemplateRepository(session)

    def list_schedule_templates(self) -> list[ScheduleTemplateResponse]:
        """List all schedule templates."""
        models = self.repo.get_all()
        return [to_response(model) for model in models]

    def get_schedule_template(self, id: UUID) -> Optional[ScheduleTemplateResponse]:
        """Get schedule template by ID."""
        model = self.repo.get_by_id(id)
        return to_response(model) if model else None

    def create_schedule_template(
        self, dto: ScheduleTemplateCreate
    ) -> ScheduleTemplateResponse:
        """
        Create a new schedule template.
        """
        model = from_create(dto)
        saved_model = self.repo.add(model)
        self.session.flush()
        self.session.commit()
        return to_response(saved_model)

    def update_schedule_template(
        self, id: UUID, dto: ScheduleTemplateUpdate
    ) -> Optional[ScheduleTemplateResponse]:
        """
        Update an existing schedule template.

        Returns None if schedule template not found.
        """
        model = self.repo.get_by_id(id)
        if not model:
            return None

        updated_model = apply_update(model, dto)
        self.session.flush()
        self.session.commit()
        return to_response(updated_model)

    def delete_schedule_template(self, id: UUID) -> None:
        """
        Delete a schedule template.

        Raises:
            ValueError: If schedule template not found
        """
        model = self.repo.get_by_id(id)
        if not model:
            raise ValueError(f"Schedule template with id {id} not found")
        self.repo.delete(model)
        self.session.flush()
        self.session.commit()
