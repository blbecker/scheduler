from typing import List, Optional
from sqlmodel import select
from scheduler_api.models import Shift
from scheduler_api.db import get_session


class ShiftRepository:
    def _get_session(self):
        return get_session()

    def get_all(self) -> List[Shift]:
        with self._get_session() as session:
            stmt = select(Shift)
            return session.exec(stmt).all()

    def get_by_id(self, shift_id: int) -> Optional[Shift]:
        with self._get_session() as session:
            return session.get(Shift, shift_id)

    def add(self, shift: Shift) -> Shift:
        with self._get_session() as session:
            session.add(shift)
            session.commit()
            session.refresh(shift)
            return shift

    def update(self, shift: Shift) -> Optional[Shift]:
        with self._get_session() as session:
            existing_shift = session.get(Shift, shift.id)
            if existing_shift is None:
                return None
            shift_data = shift.dict(exclude_unset=True)
            for key, value in shift_data.items():
                setattr(existing_shift, key, value)
            session.add(existing_shift)
            session.commit()
            session.refresh(existing_shift)
            return existing_shift

    def delete(self, shift_id: int) -> bool:
        with self._get_session() as session:
            shift = session.get(Shift, shift_id)
            if shift is None:
                return False
            session.delete(shift)
            session.commit()
            return True
