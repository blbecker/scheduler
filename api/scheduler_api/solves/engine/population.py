"""Enhanced population model for evolution."""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from uuid import UUID, uuid4
from datetime import datetime


@dataclass
class Candidate:
    """A candidate solution with metadata."""

    id: UUID = field(default_factory=uuid4)
    generation: int = 0
    genome: Any = None
    fitness: float = 0.0
    score_breakdown: Dict[str, float] = field(default_factory=dict)
    parent_ids: List[UUID] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def __str__(self) -> str:
        return f"Candidate(id={self.id}, generation={self.generation}, fitness={self.fitness:.3f})"


@dataclass
class Population:
    """Enhanced population with candidate tracking."""

    generation: int = 0
    candidates: List[Candidate] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def size(self) -> int:
        """Return number of candidates."""
        return len(self.candidates)

    def is_empty(self) -> bool:
        """Return True if population is empty."""
        return self.size() == 0

    def get_best(self) -> Optional[Candidate]:
        """Return candidate with highest fitness."""
        if self.is_empty():
            return None
        return max(self.candidates, key=lambda c: c.fitness)

    def get_best_fitness(self) -> float:
        """Return fitness of best candidate."""
        best = self.get_best()
        return best.fitness if best else 0.0

    def get_average_fitness(self) -> float:
        """Return average fitness of population."""
        if self.is_empty():
            return 0.0
        total = sum(c.fitness for c in self.candidates)
        return total / self.size()

    def get_worst_fitness(self) -> float:
        """Return fitness of worst candidate."""
        if self.is_empty():
            return 0.0
        return min(c.fitness for c in self.candidates)

    def add_candidate(self, candidate: Candidate) -> None:
        """Add candidate to population."""
        self.candidates.append(candidate)

    def clear(self) -> None:
        """Clear all candidates."""
        self.candidates.clear()

    def sort_by_fitness(self, descending: bool = True) -> None:
        """Sort candidates by fitness."""
        self.candidates.sort(key=lambda c: c.fitness, reverse=descending)

    def get_top_n(self, n: int) -> List[Candidate]:
        """Return top N candidates by fitness."""
        sorted_candidates = sorted(
            self.candidates, key=lambda c: c.fitness, reverse=True
        )
        return sorted_candidates[:n]

    def get_fitness_range(self) -> tuple[float, float]:
        """Return (min_fitness, max_fitness) range."""
        if self.is_empty():
            return (0.0, 0.0)
        fitness_values = [c.fitness for c in self.candidates]
        return (min(fitness_values), max(fitness_values))
