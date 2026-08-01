"""Schedule population domain model extending generic population framework."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional, cast, List
from uuid import UUID, uuid4

from .schedule import Schedule
from scheduler_api.engine.population import Candidate, Population as GenericPopulation


@dataclass
class ScheduleCandidate(Candidate[Schedule]):
    """Schedule-specific candidate extending generic candidate."""

    @property
    def schedule(self) -> Schedule:
        """Get schedule genome (backward compatibility)."""
        return self.genome

    @schedule.setter
    def schedule(self, value: Schedule) -> None:
        """Set schedule genome (backward compatibility)."""
        self.genome = value

    def copy(self) -> "ScheduleCandidate":
        """Create a copy of this candidate."""
        return ScheduleCandidate(
            id=self.id,
            generation=self.generation,
            genome=self.genome.copy(),
            fitness=self.fitness,
            score_breakdown=self.score_breakdown.copy(),
            parent_ids=self.parent_ids.copy(),
            metadata=self.metadata.copy(),
            created_at=self.created_at,
        )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ScheduleCandidate":
        """Create candidate from dictionary representation."""
        from scheduler_api.domain.schedule import Schedule

        # Handle genome/schedule conversion
        genome_data = data.get("schedule") or data.get("genome")
        if not genome_data:
            raise ValueError("Missing schedule/genome data")

        # Create schedule from data
        schedule = Schedule.from_dict(genome_data)

        # Parse parent IDs
        parent_ids = [UUID(pid) for pid in data.get("parent_ids", [])]

        # Parse created_at
        created_at_str = data.get("created_at")
        created_at = (
            datetime.fromisoformat(created_at_str)
            if created_at_str
            else datetime.utcnow()
        )

        return cls(
            id=UUID(data["id"]) if "id" in data else uuid4(),
            generation=data.get("generation", 0),
            genome=schedule,
            fitness=data.get("fitness", 0.0),
            score_breakdown=data.get("score_breakdown", {}),
            parent_ids=parent_ids,
            metadata=data.get("metadata", {}),
            created_at=created_at,
        )


class SchedulePopulation(GenericPopulation[Schedule]):
    """Schedule-specific population extending generic population."""

    def __init__(self, generation: int = 0):
        super().__init__(generation)

    @property
    def candidates(self) -> List[Candidate[Schedule]]:
        """Return list of schedule candidates."""
        return super().candidates

    def add_candidate(self, candidate: Candidate[Schedule]) -> None:
        """Add schedule candidate to population."""
        # Type check to ensure it's a ScheduleCandidate
        if not isinstance(candidate, ScheduleCandidate):
            # If it's a generic Candidate[Schedule], convert it
            schedule_candidate = ScheduleCandidate(
                id=candidate.id,
                generation=candidate.generation,
                genome=candidate.genome,
                fitness=candidate.fitness,
                score_breakdown=candidate.score_breakdown.copy(),
                parent_ids=candidate.parent_ids.copy(),
                metadata=candidate.metadata.copy(),
                created_at=candidate.created_at,
            )
            super().add_candidate(schedule_candidate)
        else:
            super().add_candidate(candidate)

    def get_top_n(self, n: int) -> List[Candidate[Schedule]]:
        """Return top N schedule candidates by fitness."""
        return super().get_top_n(n)

    def copy(self) -> "SchedulePopulation":
        """Create a copy of the population."""
        new_population = SchedulePopulation(generation=self.generation)
        for candidate in self.candidates:
            # Create new ScheduleCandidate from existing candidate
            if isinstance(candidate, ScheduleCandidate):
                new_population.add_candidate(candidate.copy())
            else:
                # Convert generic candidate to ScheduleCandidate
                schedule_candidate = ScheduleCandidate(
                    id=candidate.id,
                    generation=candidate.generation,
                    genome=candidate.genome,
                    fitness=candidate.fitness,
                    score_breakdown=candidate.score_breakdown.copy(),
                    parent_ids=candidate.parent_ids.copy(),
                    metadata=candidate.metadata.copy(),
                    created_at=candidate.created_at,
                )
                new_population.add_candidate(schedule_candidate)

        return new_population

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SchedulePopulation":
        """Create population from dictionary representation."""
        population = cls(generation=data.get("generation", 0))

        if "candidates" in data:
            for candidate_data in data["candidates"]:
                candidate = ScheduleCandidate.from_dict(candidate_data)
                population.add_candidate(candidate)

        return population
