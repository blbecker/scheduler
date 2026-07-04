"""Schedule genome domain model and DTO."""

from dataclasses import dataclass, field
from typing import Dict, List
from uuid import UUID
from copy import deepcopy
from pydantic import BaseModel, Field


@dataclass
class ScheduleGenome:
    """Domain genome representation for schedule solves (immutable)."""

    assignments: Dict[UUID, List[UUID]] = field(default_factory=dict)
    """Mapping of shift_id -> list of assigned worker_ids"""

    def copy(self) -> "ScheduleGenome":
        """Return deep copy (immutable pattern)."""
        return ScheduleGenome(assignments=deepcopy(self.assignments))

    def is_empty(self) -> bool:
        """Return True if genome has no assignments."""
        return len(self.assignments) == 0

    def get_assigned_workers(self) -> List[UUID]:
        """Get all unique worker IDs assigned across all shifts."""
        workers = set()
        for worker_list in self.assignments.values():
            workers.update(worker_list)
        return list(workers)

    def get_shifts_for_worker(self, worker_id: UUID) -> List[UUID]:
        """Get all shift IDs where a worker is assigned."""
        shifts = []
        for shift_id, worker_list in self.assignments.items():
            if worker_id in worker_list:
                shifts.append(shift_id)
        return shifts


class ScheduleGenomeDTO(BaseModel):
    """Pydantic DTO for schedule genome serialization."""

    assignments: Dict[str, List[str]] = Field(
        default_factory=dict,
        description="Mapping of shift_id -> list of assigned worker_ids",
    )

    def to_domain(self) -> ScheduleGenome:
        """Convert to domain genome object."""
        # Convert string UUIDs back to UUID objects
        domain_assignments = {}
        for shift_str, worker_strs in self.assignments.items():
            domain_assignments[UUID(shift_str)] = [
                UUID(worker_str) for worker_str in worker_strs
            ]
        return ScheduleGenome(assignments=domain_assignments)

    @classmethod
    def from_domain(cls, genome: ScheduleGenome) -> "ScheduleGenomeDTO":
        """Create DTO from domain genome."""
        # Convert UUIDs to strings for serialization
        dto_assignments = {}
        for shift_id, worker_list in genome.assignments.items():
            dto_assignments[str(shift_id)] = [
                str(worker_id) for worker_id in worker_list
            ]
        return cls(assignments=dto_assignments)
