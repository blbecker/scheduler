# scheduler_api/repositories/schedule_generation_run_repository.py
from typing import Optional
from uuid import UUID
from sqlmodel import Session, select

from scheduler_api.db.models.runs.schedule_generation_run import (
    ScheduleGenerationRunModel)


class ScheduleGenerationRunRepository:
    """
    Repository for schedule generation run data access.
    
    Repositories are responsible for data access only.
    They never commit or rollback transactions - services own transaction boundaries.
    """
    
    def __init__(self, session: Session):
        self.session = session

    def get_all(self) -> list[ScheduleGenerationRunModel]:
        """Get all schedule generation runs."""
        statement = select(ScheduleGenerationRunModel)
        result = self.session.exec(statement)
        return list(result.all())

    def get_by_id(self, id: UUID) -> Optional[ScheduleGenerationRunModel]:
        """Get schedule generation run by ID."""
        return self.session.get(ScheduleGenerationRunModel, id)

    def add(self, model: ScheduleGenerationRunModel) -> ScheduleGenerationRunModel:
        """
        Add a schedule generation run to the session.
        
        Note: Does not commit - service owns transaction boundaries.
        """
        self.session.add(model)
        # No commit - service owns transaction
        return model

    def delete(self, model: ScheduleGenerationRunModel) -> None:
        """
        Delete a schedule generation run from the session.
        
        Note: Does not commit - service owns transaction boundaries.
        """
        self.session.delete(model)
        # No commit - service owns transaction
