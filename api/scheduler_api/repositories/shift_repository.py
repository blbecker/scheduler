from typing import Optional
from uuid import UUID
from sqlmodel import Session, select
from scheduler_api.db.models.schedules.shift import ShiftModel


class ShiftRepository:
    """
    Repository for shift data access.

    Repositories are responsible for data access only.
    They never commit or rollback transactions - services own transaction boundaries.
    """

    def __init__(self, session: Session):
        self.session = session

    def get_all(self) -> list[ShiftModel]:
        """Get all shifts."""
        statement = select(ShiftModel)
        result = self.session.exec(statement)
        return list(result.all())

    def get_by_id(self, shift_id: UUID) -> Optional[ShiftModel]:
        """Get shift by ID."""
        return self.session.get(ShiftModel, shift_id)

    def add(self, shift: ShiftModel) -> ShiftModel:
        """
        Add a shift to the session.

        Note: Does not commit - service owns transaction boundaries.
        """
        self.session.add(shift)
        # No commit - service owns transaction
        return shift

    def delete(self, shift: ShiftModel) -> None:
        """
        Delete a shift from the session.

        Note: Does not commit - service owns transaction boundaries.
        """
        self.session.delete(shift)
        # No commit - service owns transaction
