from typing import List, Optional
from uuid import UUID
from sqlmodel import Session, select
from scheduler_api.db.models.schedules.shift import Shift


class ShiftRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_all(self) -> List[Shift]:
        statement = select(Shift)
        result = self.session.exec(statement)
        return result.all()

    def get_by_id(self, shift_id: UUID) -> Optional[Shift]:
        return self.session.get(Shift, shift_id)

    def add(self, shift: Shift) -> Shift:
        self.session.add(shift)
        return shift

    def delete(self, shift: Shift) -> None:
        self.session.delete(shift)
