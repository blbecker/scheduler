from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4


@dataclass
class ShiftAssignment:
    worker_id: UUID
    shift_id: UUID
    start_time: datetime
    end_time: datetime


@dataclass
class Schedule:
    id: UUID = field(default_factory=uuid4)
    name: str = ""
    assignments: List[ShiftAssignment] = field(default_factory=list)
    fitness: Optional[float] = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    def calculate_fitness(self) -> float:
        if self.fitness is not None:
            return self.fitness
        return 0.0
