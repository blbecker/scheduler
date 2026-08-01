from typing import Optional, List
from uuid import UUID
from sqlmodel import Session, select
from scheduler_api.db.models.assignments.shift_assignment import ShiftAssignmentModel


class ShiftAssignmentRepository:
    """
    Repository for shift assignment data access.

    Repositories are responsible for data access only.
    They never commit or rollback transactions - services own transaction boundaries.
    """

    def __init__(self, session: Session):
        self.session = session

    def get_all(self) -> List[ShiftAssignmentModel]:
        """Get all shift assignments."""
        statement = select(ShiftAssignmentModel)
        result = self.session.exec(statement)
        return list(result.all())

    def get_by_id(self, assignment_id: UUID) -> Optional[ShiftAssignmentModel]:
        """Get shift assignment by ID."""
        return self.session.get(ShiftAssignmentModel, assignment_id)

    def get_by_schedule_id(self, schedule_id: UUID) -> List[ShiftAssignmentModel]:
        """Get all shift assignments for a schedule."""
        statement = select(ShiftAssignmentModel).where(
            ShiftAssignmentModel.schedule_id == schedule_id
        )
        result = self.session.exec(statement)
        return list(result.all())

    def get_by_shift_id(self, shift_id: UUID) -> Optional[ShiftAssignmentModel]:
        """Get shift assignment for a specific shift (one-to-one relationship)."""
        statement = select(ShiftAssignmentModel).where(
            ShiftAssignmentModel.shift_id == shift_id
        )
        result = self.session.exec(statement)
        return result.first()

    def get_by_worker_id(self, worker_id: UUID) -> List[ShiftAssignmentModel]:
        """Get all shift assignments for a worker."""
        statement = select(ShiftAssignmentModel).where(
            ShiftAssignmentModel.worker_id == worker_id
        )
        result = self.session.exec(statement)
        return list(result.all())

    def add(self, assignment: ShiftAssignmentModel) -> ShiftAssignmentModel:
        """
        Add a shift assignment to the session.

        Note: Does not commit - service owns transaction boundaries.
        """
        self.session.add(assignment)
        # No commit - service owns transaction
        return assignment

    def delete(self, assignment: ShiftAssignmentModel) -> None:
        """
        Delete a shift assignment from the session.

        Note: Does not commit - service owns transaction boundaries.
        """
        self.session.delete(assignment)
        # No commit - service owns transaction

    def get_assignments_for_schedule_and_worker(
        self, schedule_id: UUID, worker_id: UUID
    ) -> List[ShiftAssignmentModel]:
        """Get all assignments for a specific worker in a specific schedule."""
        statement = select(ShiftAssignmentModel).where(
            (ShiftAssignmentModel.schedule_id == schedule_id)
            & (ShiftAssignmentModel.worker_id == worker_id)
        )
        result = self.session.exec(statement)
        return list(result.all())
