from typing import List, Optional
from scheduler_api.db.models import Shift
from sqlmodel import Session


class ShiftRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_all(self) -> list[Shift]:
        return self.session.query(Shift).all()

    def get_by_id(self, shift_id: int) -> Shift | None:
        return self.session.get(Shift, shift_id)

    def add(self, shift: Shift) -> Shift:
        self.session.add(shift)
        self.session.commit()
        self.session.refresh(shift)
        return shift

    def delete(self, shift_id: int) -> bool:
        obj = self.session.get(Shift, shift_id)
        if not obj:
            return False
        self.session.delete(obj)
        self.session.commit()
        return True
