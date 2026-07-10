# scheduler_api/repositories/schedule_solve_repository.py
from typing import Optional
from uuid import UUID
from sqlmodel import Session, select

from scheduler_api.db.models.solves.schedule_solve import ScheduleSolveModel


class ScheduleSolveRepository:
    """
    Repository for schedule solve data access.

    Repositories are responsible for data access only.
    They never commit or rollback transactions - services own transaction boundaries.
    """

    def __init__(self, session: Session):
        self.session = session

    def get_all(self) -> list[ScheduleSolveModel]:
        """Get all schedule solves."""
        statement = select(ScheduleSolveModel)
        result = self.session.exec(statement)
        return list(result.all())

    def get_by_id(self, id: UUID) -> Optional[ScheduleSolveModel]:
        """Get schedule solve by ID."""
        return self.session.get(ScheduleSolveModel, id)

    def add(self, model: ScheduleSolveModel) -> ScheduleSolveModel:
        """
        Add a schedule solve to the session.

        Note: Does not commit - service owns transaction boundaries.
        """
        self.session.add(model)
        # No commit - service owns transaction
        return model

    def update(self, model: ScheduleSolveModel) -> ScheduleSolveModel:
        """
        Update a schedule solve in the session.

        Note: Does not commit - service owns transaction boundaries.
        """
        # SQLModel/SQLAlchemy tracks changes automatically
        # We just need to ensure the model is in the session
        self.session.add(model)
        return model

    def delete(self, model: ScheduleSolveModel) -> None:
        """
        Delete a schedule solve from the session.

        Note: Does not commit - service owns transaction boundaries.
        """
        self.session.delete(model)
        # No commit - service owns transaction
