# scheduler_api/repositories/shift_template_repository.py
from typing import List, Optional
from uuid import UUID
from sqlmodel import Session, select

from scheduler_api.db.models.templates.shift_template import ShiftTemplate


class ShiftTemplateRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_all(self) -> List[ShiftTemplate]:
        statement = select(ShiftTemplate)
        result = self.session.exec(statement)
        return result.all()

    def get_by_id(self, id: UUID) -> Optional[ShiftTemplate]:
        return self.session.get(ShiftTemplate, id)

    def add(self, model: ShiftTemplate) -> ShiftTemplate:
        self.session.add(model)
        return model

    def delete(self, model: ShiftTemplate) -> None:
        self.session.delete(model)
