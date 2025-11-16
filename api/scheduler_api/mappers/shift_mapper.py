from scheduler_api.models import Shift
from scheduler_api.schemas.shift import ShiftRead
from typing import List
import logging

logger = logging.getLogger(__name__)


def shift_to_read(shift: Shift) -> ShiftRead:
    return ShiftRead(
        id=shift.id,
        start_time=shift.start_time,
        end_time=shift.end_time,
        workers=[w.id for w in shift.workers],
        skills=[s.id for s in shift.skills],
    )


def list_shifts_to_read(shifts: List[Shift]) -> List[ShiftRead]:
    return [shift_to_read(w) for w in shifts]
