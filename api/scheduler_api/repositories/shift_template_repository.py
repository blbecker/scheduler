# scheduler_api/repositories/shift_template_repository.py
from typing import List, Optional
from uuid import UUID
from sqlmodel import Session, select

from scheduler_api.db.models.templates.shift_template import ShiftTemplateModel


class ShiftTemplateRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_all(self) -> List[ShiftTemplateModel]:
        statement = select(ShiftTemplateModel)
        result = self.session.exec(statement)
        return result.all()

    def get_by_id(self, id: UUID) -> Optional[ShiftTemplateModel]:
        return self.session.get(ShiftTemplateModel, id)

    def add(self, model: ShiftTemplateModel) -> ShiftTemplateModel:
        self.session.add(model)
        self.session.commit()  # Commit transaction
        return model

    def delete(self, model: ShiftTemplateModel) -> None:
        self.session.delete(model)
        self.session.commit()  # Commit transaction
