# scheduler_api/services/schedule_service.py
from uuid import UUID
from typing import Optional
from sqlmodel import Session

from scheduler_api.repositories.schedule_repository import ScheduleRepository
from scheduler_api.repositories.schedule_template_repository import (
    ScheduleTemplateRepository,
)
from scheduler_api.repositories.shift_template_repository import ShiftTemplateRepository
from scheduler_api.repositories.shift_repository import ShiftRepository
from scheduler_api.repositories.shift_assignment_repository import (
    ShiftAssignmentRepository,
)
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
        self.schedule_template_repo = ScheduleTemplateRepository(session)
        self.shift_template_repo = ShiftTemplateRepository(session)
        self.shift_repo = ShiftRepository(session)
        self.shift_assignment_repo = ShiftAssignmentRepository(session)

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
        Create a new schedule from template.

        Steps:
        1. Create schedule model
        2. Get schedule template with its shift templates (SQLModel hydrates relationships)
        3. Create shifts from shift templates
        4. Create shift assignments linking shifts to schedule
        """
        from datetime import datetime, date
        from scheduler_api.domain.schedule import ShiftAssignmentStatus

        # 1. Create schedule model
        model = from_create(dto)

        # 2. Get schedule template - SQLModel will hydrate shift_templates relationship
        from scheduler_api.db.models.templates.schedule_template import (
            ScheduleTemplateModel,
        )

        schedule_template = self.session.get(
            ScheduleTemplateModel, dto.schedule_template_id
        )

        if not schedule_template:
            raise ValueError(
                f"Schedule template with id {dto.schedule_template_id} not found"
            )

        # Save schedule first to get its ID
        saved_schedule = self.repo.add(model)
        self.session.flush()  # Get schedule ID

        try:
            # 3. Create shifts from shift templates
            # SQLModel hydrates shift_templates relationship automatically
            shift_templates = schedule_template.shift_templates

            # Use today's date for time-to-datetime conversion
            today = date.today()

            for shift_template in shift_templates:
                # Create shift from template
                from scheduler_api.db.models.schedules.shift import ShiftModel

                # Convert time to datetime using today's date
                start_datetime = datetime.combine(today, shift_template.start_time)
                end_datetime = datetime.combine(today, shift_template.end_time)

                shift = ShiftModel(
                    shift_template_id=shift_template.id,
                    name=shift_template.name,
                    start_time=start_datetime,
                    end_time=end_datetime,
                )
                self.shift_repo.add(shift)

                # 4. Create shift assignment (no worker assigned initially)
                from scheduler_api.db.models.assignments.shift_assignment import (
                    ShiftAssignmentModel,
                )

                assignment = ShiftAssignmentModel(
                    schedule_id=saved_schedule.id,
                    shift_id=shift.id,
                    worker_id=None,  # No worker assigned initially
                    status=ShiftAssignmentStatus.ASSIGNED,  # Use enum
                )
                self.shift_assignment_repo.add(assignment)
                # Add assignment to schedule's shift_assignments
                saved_schedule.shift_assignments.append(assignment)

            # Commit all changes
            self.session.flush()
            self.session.commit()

        except Exception as e:
            # Rollback on error
            self.session.rollback()
            raise ValueError(f"Failed to create schedule from template: {str(e)}")

        return to_response(saved_schedule)

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
