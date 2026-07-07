# scheduler_api/services/schedule_generation_run_service.py
from uuid import UUID
from typing import Optional
from sqlmodel import Session

from scheduler_api.repositories.schedule_generation_run_repository import (
    ScheduleGenerationRunRepository,
)
from scheduler_api.mappers.schedule_generation_run_mapper import (
    to_response,
    from_create,
    apply_update,
)
from scheduler_api.schemas.schedule_generation_run import (
    ScheduleGenerationRunCreate,
    ScheduleGenerationRunResponse,
    ScheduleGenerationRunUpdate,
)


class ScheduleGenerationRunService:
    """
    Service for schedule generation run operations.

    Services own transaction boundaries.
    Repositories are data access only and never commit/rollback transactions.
    """

    def __init__(self, session: Session):
        """
        Initialize schedule generation run service.

        Args:
            session: SQLModel database session
        """
        self.session = session
        self.repo = ScheduleGenerationRunRepository(session)

    def list_schedule_generation_runs(self) -> list[ScheduleGenerationRunResponse]:
        """List all schedule generation runs."""
        models = self.repo.get_all()
        return [to_response(model) for model in models]

    def get_schedule_generation_run(
        self, id: UUID
    ) -> Optional[ScheduleGenerationRunResponse]:
        """Get schedule generation run by ID."""
        model = self.repo.get_by_id(id)
        return to_response(model) if model else None

    def create_schedule_generation_run(
        self, dto: ScheduleGenerationRunCreate
    ) -> ScheduleGenerationRunResponse:
        """
        Create a new schedule generation run.
        """
        model = from_create(dto)
        saved_model = self.repo.add(model)
        self.session.flush()
        self.session.commit()
        return to_response(saved_model)

    def update_schedule_generation_run(
        self, id: UUID, dto: ScheduleGenerationRunUpdate
    ) -> Optional[ScheduleGenerationRunResponse]:
        """
        Update an existing schedule generation run.

        Returns None if schedule generation run not found.
        """
        model = self.repo.get_by_id(id)
        if not model:
            return None

        updated_model = apply_update(model, dto)
        self.session.flush()
        self.session.commit()
        return to_response(updated_model)

    def delete_schedule_generation_run(self, id: UUID) -> None:
        """
        Delete a schedule generation run.

        Raises:
            ValueError: If schedule generation run not found
        """
        model = self.repo.get_by_id(id)
        if not model:
            raise ValueError(f"Schedule generation run with id {id} not found")
        self.repo.delete(model)
        self.session.flush()
        self.session.commit()
