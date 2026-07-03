# scheduler_api/repositories/schedule_template_repository.py
from typing import List, Optional
from uuid import UUID
from sqlmodel import Session, select

from scheduler_api.db.models.templates.schedule_template import ScheduleTemplate


class ScheduleTemplateRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_all(self) -> List[ScheduleTemplate]:
        statement = select(ScheduleTemplate)
        result = self.session.exec(statement)
        return result.all()

    def get_by_id(self, id: UUID) -> Optional[ScheduleTemplate]:
        return self.session.get(ScheduleTemplate, id)

    def add(self, model: ScheduleTemplate) -> ScheduleTemplate:
        self.session.add(model)
        return model

    def delete(self, model: ScheduleTemplate) -> None:
        self.session.delete(model)
