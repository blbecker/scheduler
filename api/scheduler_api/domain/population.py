from dataclasses import dataclass, field
from datetime import datetime
from typing import List
from uuid import UUID, uuid4
from .schedule import Schedule


@dataclass
class Population:
    id: UUID = field(default_factory=uuid4)
    generation: int = 0
    schedules: List[Schedule] = field(default_factory=list)
    layout_id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def get_best_schedule(self) -> Schedule:
        if not self.schedules:
            raise ValueError("Population has no schedules")
        return max(self.schedules, key=lambda s: s.calculate_fitness())

    def size(self) -> int:
        return len(self.schedules)