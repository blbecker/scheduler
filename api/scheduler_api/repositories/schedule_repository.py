# scheduler_api/repositories/schedule_repository.py
from typing import Optional
from uuid import UUID
from sqlmodel import Session, select

from scheduler_api.db.models.schedules.schedule import ScheduleModel


class ScheduleRepository:
    """
    Repository for schedule data access.

    Repositories are responsible for data access only.
    They never commit or rollback transactions - services own transaction boundaries.
    """

    def __init__(self, session: Session):
        self.session = session

    def get_all(self) -> list[ScheduleModel]:
        """Get all schedules."""
        statement = select(ScheduleModel)
        result = self.session.exec(statement)
        return list(result.all())

    def get_by_id(self, id: UUID) -> Optional[ScheduleModel]:
        """Get schedule by ID."""
        return self.session.get(ScheduleModel, id)

    def add(self, model: ScheduleModel) -> ScheduleModel:
        """
        Add a schedule to the session.

        Note: Does not commit - service owns transaction boundaries.
        """
        self.session.add(model)
        # No commit - service owns transaction
        return model

    def delete(self, model: ScheduleModel) -> None:
        """
        Delete a schedule from the session.

        Note: Does not commit - service owns transaction boundaries.
        """
        self.session.delete(model)
        # No commit - service owns transaction
