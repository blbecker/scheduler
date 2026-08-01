# scheduler_api/services/shift_assignment_service.py
from uuid import UUID
from typing import Optional, List
from sqlmodel import Session

from scheduler_api.repositories.shift_assignment_repository import (
    ShiftAssignmentRepository,
)
from scheduler_api.mappers.assignment_mapper import (
    to_response,
    from_create,
    apply_update,
)
from scheduler_api.schemas.assignment import (
    ShiftAssignmentCreate,
    ShiftAssignmentUpdate,
    ShiftAssignmentResponse,
    ShiftAssignmentListResponse,
)


class ShiftAssignmentService:
    """
    Service for shift assignment operations.

    Services own transaction boundaries.
    Repositories are data access only and never commit/rollback transactions.
    """

    def __init__(self, session: Session):
        """
        Initialize shift assignment service.

        Args:
            session: SQLModel session for database operations
        """
        self.session = session
        self.repo = ShiftAssignmentRepository(session)

    def list_assignments(self) -> ShiftAssignmentListResponse:
        """
        List all shift assignments.

        Returns:
            List of shift assignment responses
        """
        models = self.repo.get_all()
        assignments = [to_response(m) for m in models]
        return ShiftAssignmentListResponse(
            assignments=assignments, total=len(assignments)
        )

    def get_assignment(self, assignment_id: UUID) -> Optional[ShiftAssignmentResponse]:
        """
        Get shift assignment by ID.

        Args:
            assignment_id: Shift assignment ID

        Returns:
            Shift assignment response if found, None otherwise
        """
        assignment = self.repo.get_by_id(assignment_id)
        return to_response(assignment) if assignment else None

    def get_assignments_by_schedule(
        self, schedule_id: UUID
    ) -> ShiftAssignmentListResponse:
        """
        Get all shift assignments for a schedule.

        Args:
            schedule_id: Schedule ID

        Returns:
            List of shift assignment responses for the schedule
        """
        models = self.repo.get_by_schedule_id(schedule_id)
        assignments = [to_response(m) for m in models]
        return ShiftAssignmentListResponse(
            assignments=assignments, total=len(assignments)
        )

    def get_assignment_by_shift(
        self, shift_id: UUID
    ) -> Optional[ShiftAssignmentResponse]:
        """
        Get shift assignment for a specific shift.

        Args:
            shift_id: Shift ID

        Returns:
            Shift assignment response if found, None otherwise
        """
        assignment = self.repo.get_by_shift_id(shift_id)
        return to_response(assignment) if assignment else None

    def get_assignments_by_worker(self, worker_id: UUID) -> ShiftAssignmentListResponse:
        """
        Get all shift assignments for a worker.

        Args:
            worker_id: Worker ID

        Returns:
            List of shift assignment responses for the worker
        """
        models = self.repo.get_by_worker_id(worker_id)
        assignments = [to_response(m) for m in models]
        return ShiftAssignmentListResponse(
            assignments=assignments, total=len(assignments)
        )

    def create_assignment(
        self, assignment_data: ShiftAssignmentCreate
    ) -> ShiftAssignmentResponse:
        """
        Create a new shift assignment.

        Args:
            assignment_data: Shift assignment creation data

        Returns:
            Created shift assignment response

        Raises:
            ValueError: If assignment already exists for the shift
        """
        # Check if assignment already exists for this shift
        existing = self.repo.get_by_shift_id(assignment_data.shift_id)
        if existing:
            raise ValueError(
                f"Assignment already exists for shift {assignment_data.shift_id}"
            )

        assignment = from_create(assignment_data)
        self.repo.add(assignment)

        # Service owns transaction - commit the changes
        self.session.flush()
        self.session.commit()

        return to_response(assignment)

    def update_assignment(
        self, assignment_id: UUID, assignment_data: ShiftAssignmentUpdate
    ) -> Optional[ShiftAssignmentResponse]:
        """
        Update an existing shift assignment.

        Args:
            assignment_id: Shift assignment ID to update
            assignment_data: Shift assignment update data

        Returns:
            Updated shift assignment response if found, None otherwise
        """
        assignment = self.repo.get_by_id(assignment_id)
        if not assignment:
            return None

        assignment = apply_update(assignment, assignment_data)

        # Service owns transaction - commit the changes
        self.session.flush()
        self.session.commit()

        return to_response(assignment)

    def delete_assignment(self, assignment_id: UUID) -> bool:
        """
        Delete a shift assignment.

        Args:
            assignment_id: Shift assignment ID to delete

        Returns:
            True if deleted, False if not found
        """
        assignment = self.repo.get_by_id(assignment_id)
        if not assignment:
            return False

        self.repo.delete(assignment)

        # Service owns transaction - commit the changes
        self.session.flush()
        self.session.commit()

        return True

    def bulk_create_assignments(
        self, schedule_id: UUID, assignments_data: List[ShiftAssignmentCreate]
    ) -> ShiftAssignmentListResponse:
        """
        Create multiple shift assignments for a schedule.

        Args:
            schedule_id: Schedule ID for all assignments
            assignments_data: List of shift assignment creation data

        Returns:
            List of created shift assignment responses
        """
        created_assignments = []

        for assignment_data in assignments_data:
            # Ensure all assignments belong to the same schedule
            if assignment_data.schedule_id != schedule_id:
                raise ValueError(
                    f"Assignment schedule_id {assignment_data.schedule_id} "
                    f"does not match expected schedule_id {schedule_id}"
                )

            # Check if assignment already exists for this shift
            existing = self.repo.get_by_shift_id(assignment_data.shift_id)
            if existing:
                raise ValueError(
                    f"Assignment already exists for shift {assignment_data.shift_id}"
                )

            assignment = from_create(assignment_data)
            self.repo.add(assignment)
            created_assignments.append(assignment)

        # Service owns transaction - commit all changes at once
        self.session.flush()
        self.session.commit()

        assignments = [to_response(m) for m in created_assignments]
        return ShiftAssignmentListResponse(
            assignments=assignments, total=len(assignments)
        )
