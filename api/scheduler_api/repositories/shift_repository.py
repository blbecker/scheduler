from typing import List, Optional
from scheduler_api.models import Shift
from sqlmodel import Session


class ShiftRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_all(self) -> List[Shift]:
        return self.session.query(Shift).all()

    def get_by_id(self, shift_id: int) -> Optional[Shift]:
        return self.session.get(Shift, shift_id)

    def add(self, shift: Shift) -> Shift:
        self.session.add(shift)
        self.session.commit()
        self.session.refresh(shift)
        return shift

    def update(self, shift: Shift) -> Optional[Shift]:
        existing_shift = self.session.get(Shift, shift.id)
        if existing_shift is None:
            return None
        shift_data = shift.model_dump(exclude_unset=True)
        for key, value in shift_data.items():
            setattr(existing_shift, key, value)
        self.session.add(existing_shift)
        self.session.commit()
        self.session.refresh(existing_shift)
        return existing_shift

    def delete(self, shift_id: int) -> bool:
        shift = self.session.get(Shift, shift_id)
        if shift is None:
            return False
        self.session.delete(shift)
        self.session.commit()
        return True
