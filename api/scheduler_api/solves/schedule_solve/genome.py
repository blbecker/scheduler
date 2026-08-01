"""Genome DTO and domain models for schedule solves."""

from typing import Dict, List
from uuid import UUID
from dataclasses import dataclass, field, asdict


@dataclass
class ScheduleGenome:
    """Domain model for schedule genome."""

    assignments: Dict[UUID, List[UUID]] = field(default_factory=dict)

    def copy(self) -> "ScheduleGenome":
        """Create a copy of the genome."""
        return ScheduleGenome(assignments=self.assignments.copy())


@dataclass
class ScheduleGenomeDTO:
    """DTO for schedule genome serialization."""

    assignments: Dict[str, List[str]] = field(default_factory=dict)

    @classmethod
    def from_domain(cls, genome: ScheduleGenome) -> "ScheduleGenomeDTO":
        """Convert domain genome to DTO."""
        assignments = {
            str(shift_id): [str(worker_id) for worker_id in worker_ids]
            for shift_id, worker_ids in genome.assignments.items()
        }
        return cls(assignments=assignments)

    def to_domain(self) -> ScheduleGenome:
        """Convert DTO to domain genome."""
        assignments = {
            UUID(shift_id): [UUID(worker_id) for worker_id in worker_ids]
            for shift_id, worker_ids in self.assignments.items()
        }
        return ScheduleGenome(assignments=assignments)

    def model_dump(self) -> dict:
        """Convert to dictionary."""
        return asdict(self)
