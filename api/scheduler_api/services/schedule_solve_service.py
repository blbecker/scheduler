# scheduler_api/services/schedule_solve_service.py
from uuid import UUID
from typing import Optional
from sqlmodel import Session

from scheduler_api.repositories.schedule_solve_repository import (
    ScheduleSolveRepository,
)
from scheduler_api.mappers.schedule_solve_mapper import (
    to_response,
    from_create,
    apply_update,
)
from scheduler_api.schemas.schedule_solve import (
    ScheduleSolveCreate,
    ScheduleSolveResponse,
    ScheduleSolveUpdate,
)
from scheduler_api.db.models.enums import ScheduleSolveStatus


class ScheduleSolveService:
    """
    Service for schedule solve operations.

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
        self.repo = ScheduleSolveRepository(session)

    def list_schedule_solves(self) -> list[ScheduleSolveResponse]:
        """List all schedule solves."""
        models = self.repo.get_all()
        return [to_response(model) for model in models]

    def get_schedule_solve(self, id: UUID) -> Optional[ScheduleSolveResponse]:
        """Get schedule solve by ID."""
        model = self.repo.get_by_id(id)
        return to_response(model) if model else None

    def create_schedule_solve(self, dto: ScheduleSolveCreate) -> ScheduleSolveResponse:
        """
        Create a new schedule solve.
        """
        model = from_create(dto)
        saved_model = self.repo.add(model)
        self.session.flush()
        self.session.commit()
        return to_response(saved_model)

    def update_schedule_solve(
        self, id: UUID, dto: ScheduleSolveUpdate
    ) -> Optional[ScheduleSolveResponse]:
        """
        Update an existing schedule solve.

        Returns None if schedule solve not found.
        """
        model = self.repo.get_by_id(id)
        if not model:
            return None

        updated_model = apply_update(model, dto)
        self.session.flush()
        self.session.commit()
        return to_response(updated_model)

    def delete_schedule_solve(self, id: UUID) -> None:
        """
        Delete a schedule solve.

        Raises ValueError if schedule solve not found.
        """
        model = self.repo.get_by_id(id)
        if not model:
            raise ValueError(f"Schedule solve with id {id} not found")

        self.repo.delete(model)
        self.session.flush()
        self.session.commit()

    # -----------------------------------------------------------------
    # Enhanced methods for solve framework integration
    # -----------------------------------------------------------------

    def update_schedule_solve_status(
        self, solve_id: UUID, status: ScheduleSolveStatus, **kwargs
    ) -> None:
        """Update schedule solve status with optional additional fields."""
        from scheduler_api.db.models.enums import ScheduleSolveStatus

        model = self.repo.get_by_id(solve_id)
        if not model:
            raise ValueError(f"Schedule solve with id {solve_id} not found")

        model.status = status

        # Update timestamps based on status
        if status == ScheduleSolveStatus.running and not model.started_at:
            from datetime import datetime, timezone

            model.started_at = datetime.now(timezone.utc)
        elif (
            status
            in [
                ScheduleSolveStatus.completed,
                ScheduleSolveStatus.failed,
                ScheduleSolveStatus.cancelled,
            ]
            and not model.finished_at
        ):
            from datetime import datetime, timezone

            model.finished_at = datetime.now(timezone.utc)

        # Update any additional fields from kwargs
        for key, value in kwargs.items():
            if hasattr(model, key):
                setattr(model, key, value)

        self.repo.update(model)
        self.session.flush()
        self.session.commit()

    def update_schedule_solve_progress(self, solve_id: UUID, **kwargs) -> None:
        """Update schedule solve progress metrics."""
        model = self.repo.get_by_id(solve_id)
        if not model:
            raise ValueError(f"Schedule solve with id {solve_id} not found")

        # Update fields from kwargs
        for key, value in kwargs.items():
            if hasattr(model, key):
                setattr(model, key, value)

        self.repo.update(model)
        self.session.flush()
        self.session.commit()

    def complete_schedule_solve(self, solve_id: UUID, schedule_id: UUID) -> None:
        """Mark schedule solve as completed with schedule reference."""
        from scheduler_api.db.models.enums import ScheduleSolveStatus

        self.update_schedule_solve_status(
            solve_id,
            ScheduleSolveStatus.completed,
            schedule_id=schedule_id,
            progress=1.0,
        )

    def fail_schedule_solve(self, solve_id: UUID, error_details: str) -> None:
        """Mark schedule solve as failed with error details."""
        from scheduler_api.db.models.enums import ScheduleSolveStatus

        self.update_schedule_solve_status(
            solve_id, ScheduleSolveStatus.failed, error_details=error_details
        )

    def create_schedule_from_solve(self, solve_id: UUID, name: str) -> "ScheduleModel":
        """
        Create a schedule linked to a solve.

        Note: This is a simplified implementation. In production,
        you would use the ScheduleService to create the schedule.
        """
        from scheduler_api.db.models.schedules.schedule import ScheduleModel

        model = self.repo.get_by_id(solve_id)
        if not model:
            raise ValueError(f"Schedule solve with id {solve_id} not found")

        # Create schedule
        schedule = ScheduleModel(
            name=name,
            schedule_template_id=model.schedule_template_id,
            schedule_solve_id=model.id,
        )

        self.session.add(schedule)
        self.session.flush()
        self.session.commit()

        return schedule
