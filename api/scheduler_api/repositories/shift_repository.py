from typing import List, Optional
from sqlmodel import select
from scheduler_api.models import Shift
from scheduler_api.db import get_session


class ShiftRepository:
    def get_all(self) -> List[Shift]:
        with get_session() as session:
            return session.exec(select(Shift)).all()

    def get_by_id(self, shift_id: int) -> Optional[Shift]:
        with get_session() as session:
            return session.get(Shift, shift_id)

    def add(self, shift: Shift) -> Shift:
        with get_session() as session:
            session.add(shift)
            session.commit()
            session.refresh(shift)
            return shift
