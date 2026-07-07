# scheduler_api/services/schedule_service.py
from uuid import UUID
from typing import Optional
from sqlmodel import Session

from scheduler_api.repositories.schedule_repository import ScheduleRepository
from scheduler_api.mappers.schedule_mapper import to_response, from_create, apply_update
from scheduler_api.schemas.schedule_crud import (
    ScheduleCreate,
    ScheduleResponse,
    ScheduleUpdate,
)


class ScheduleService:
    """
    Service for schedule operations.

    Services own transaction boundaries.
    Repositories are data access only and never commit/rollback transactions.
    """

    def __init__(self, session: Session):
        """
        Initialize schedule service.

        Args:
            session: SQLModel database session
        """
        self.session = session
        self.repo = ScheduleRepository(session)

    def list_schedules(self) -> list[ScheduleResponse]:
        """List all schedules."""
        models = self.repo.get_all()
        return [to_response(model) for model in models]

    def get_schedule(self, id: UUID) -> Optional[ScheduleResponse]:
        """Get schedule by ID."""
        model = self.repo.get_by_id(id)
        return to_response(model) if model else None

    def create_schedule(self, dto: ScheduleCreate) -> ScheduleResponse:
        """
        Create a new schedule.
        """
        model = from_create(dto)
        saved_model = self.repo.add(model)
        self.session.flush()
        self.session.commit()
        return to_response(saved_model)

    def update_schedule(
        self, id: UUID, dto: ScheduleUpdate
    ) -> Optional[ScheduleResponse]:
        """
        Update an existing schedule.

        Returns None if schedule not found.
        """
        model = self.repo.get_by_id(id)
        if not model:
            return None

        updated_model = apply_update(model, dto)
        self.session.flush()
        self.session.commit()
        return to_response(updated_model)

    def delete_schedule(self, id: UUID) -> None:
        """
        Delete a schedule.

        Raises:
            ValueError: If schedule not found
        """
        model = self.repo.get_by_id(id)
        if not model:
            raise ValueError(f"Schedule with id {id} not found")
        self.repo.delete(model)
        self.session.flush()
        self.session.commit()
