# scheduler_api/repositories/schedule_repository.py
from typing import List, Optional
from uuid import UUID
from sqlmodel import Session, select

from scheduler_api.db.models.schedules.schedule import Schedule


class ScheduleRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_all(self) -> List[Schedule]:
        statement = select(Schedule)
        result = self.session.exec(statement)
        return result.all()

    def get_by_id(self, id: UUID) -> Optional[Schedule]:
        return self.session.get(Schedule, id)

    def add(self, model: Schedule) -> Schedule:
        self.session.add(model)
        return model

    def delete(self, model: Schedule) -> None:
        self.session.delete(model)
