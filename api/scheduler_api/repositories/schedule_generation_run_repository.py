# scheduler_api/repositories/schedule_generation_run_repository.py
from typing import List, Optional
from uuid import UUID
from sqlmodel import Session, select

from scheduler_api.db.models.runs.schedule_generation_run import (
    ScheduleGenerationRunModel,
)


class ScheduleGenerationRunRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_all(self) -> List[ScheduleGenerationRunModel]:
        statement = select(ScheduleGenerationRunModel)
        result = self.session.exec(statement)
        return result.all()

    def get_by_id(self, id: UUID) -> Optional[ScheduleGenerationRunModel]:
        return self.session.get(ScheduleGenerationRunModel, id)

    def add(self, model: ScheduleGenerationRunModel) -> ScheduleGenerationRunModel:
        self.session.add(model)
        self.session.commit()  # Commit transaction
        return model

    def delete(self, model: ScheduleGenerationRunModel) -> None:
        self.session.delete(model)
        self.session.commit()  # Commit transaction
