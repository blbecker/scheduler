# scheduler_api/repositories/schedule_repository.py
from typing import List, Optional
from uuid import UUID
from sqlmodel import Session, select

from scheduler_api.db.models.schedules.schedule import ScheduleModel


class ScheduleRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_all(self) -> List[ScheduleModel]:
        statement = select(ScheduleModel)
        result = self.session.exec(statement)
        return result.all()

    def get_by_id(self, id: UUID) -> Optional[ScheduleModel]:
        return self.session.get(ScheduleModel, id)

    def add(self, model: ScheduleModel) -> ScheduleModel:
        self.session.add(model)
        return model

    def delete(self, model: ScheduleModel) -> None:
        self.session.delete(model)
