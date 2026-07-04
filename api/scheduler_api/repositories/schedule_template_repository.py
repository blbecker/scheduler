# scheduler_api/repositories/schedule_template_repository.py
from typing import List, Optional
from uuid import UUID
from sqlmodel import Session, select

from scheduler_api.db.models.templates.schedule_template import ScheduleTemplateModel


class ScheduleTemplateRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_all(self) -> List[ScheduleTemplateModel]:
        statement = select(ScheduleTemplateModel)
        result = self.session.exec(statement)
        return result.all()

    def get_by_id(self, id: UUID) -> Optional[ScheduleTemplateModel]:
        return self.session.get(ScheduleTemplateModel, id)

    def add(self, model: ScheduleTemplateModel) -> ScheduleTemplateModel:
        self.session.add(model)
        return model

    def delete(self, model: ScheduleTemplateModel) -> None:
        self.session.delete(model)
