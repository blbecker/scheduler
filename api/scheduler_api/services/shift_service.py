# scheduler_api/services/shift_service.py
from typing import List, Optional
from scheduler_api.models import Shift
from scheduler_api.repositories.shift_repository import ShiftRepository


class ShiftService:
    def __init__(self, repo: ShiftRepository):
        self.repo = repo

    def list_shifts(self) -> List[Shift]:
        return self.repo.get_all()

    def get_shift(self, shift_id: int) -> Optional[Shift]:
        return self.repo.get_by_id(shift_id)

    def create_shift(self, name: str, birthdate, email: str = None) -> Shift:
        shift = Shift(name=name, birthdate=birthdate, email=email)
        return self.repo.add(shift)
