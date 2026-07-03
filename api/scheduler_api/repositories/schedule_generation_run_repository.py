# scheduler_api/repositories/schedule_generation_run_repository.py
from typing import List, Optional
from uuid import UUID
from sqlmodel import Session, select

from scheduler_api.db.models.runs.schedule_generation_run import ScheduleGenerationRun


class ScheduleGenerationRunRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_all(self) -> List[ScheduleGenerationRun]:
        statement = select(ScheduleGenerationRun)
        result = self.session.exec(statement)
        return result.all()

    def get_by_id(self, id: UUID) -> Optional[ScheduleGenerationRun]:
        return self.session.get(ScheduleGenerationRun, id)

    def add(self, model: ScheduleGenerationRun) -> ScheduleGenerationRun:
        self.session.add(model)
        return model

    def delete(self, model: ScheduleGenerationRun) -> None:
        self.session.delete(model)
