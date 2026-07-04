from typing import List, Optional
from uuid import UUID
from sqlmodel import Session, select
from scheduler_api.db.models.schedules.shift import ShiftModel


class ShiftRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_all(self) -> List[ShiftModel]:
        statement = select(ShiftModel)
        result = self.session.exec(statement)
        return result.all()

    def get_by_id(self, shift_id: UUID) -> Optional[ShiftModel]:
        return self.session.get(ShiftModel, shift_id)

    def add(self, shift: ShiftModel) -> ShiftModel:
        self.session.add(shift)
        return shift

    def delete(self, shift: ShiftModel) -> None:
        self.session.delete(shift)
