from typing import List, Optional
from scheduler_api.models import Shift
from sqlmodel import Session


class ShiftRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_all(self) -> List[Shift]:
        with self.session as session:
            return session.query(Shift).all()

    def get_by_id(self, shift_id: int) -> Optional[Shift]:
        with self.session as session:
            return session.get(Shift, shift_id)

    def add(self, shift: Shift) -> Shift:
        with self.session as session:
            session.add(shift)
            session.commit()
            session.refresh(shift)
            return shift

    def update(self, shift: Shift) -> Optional[Shift]:
        with self.session as session:
            existing_shift = session.get(Shift, shift.id)
            if existing_shift is None:
                return None
            shift_data = shift.model_dump(exclude_unset=True)
            for key, value in shift_data.items():
                setattr(existing_shift, key, value)
            session.add(existing_shift)
            session.commit()
            session.refresh(existing_shift)
            return existing_shift

    def delete(self, shift_id: int) -> bool:
        with self.session as session:
            shift = session.get(Shift, shift_id)
            if shift is None:
                return False
            session.delete(shift)
            session.commit()
            return True
