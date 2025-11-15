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

    # start_time: datetime
    # end_time: datetime
    # location: Optional[str] = None
    # notes: Optional[str] = None

    def create_shift(self, shift: Shift) -> Shift:
        return self.repo.add(shift)
