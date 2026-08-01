"""Generic population model for genetic algorithm evolution."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Generic, TypeVar, Any, Optional, List, Dict
from uuid import UUID, uuid4

# Type variable for genome type
G = TypeVar("G")


@dataclass
class Candidate(Generic[G]):
    """Generic candidate solution with evolution metadata."""

    id: UUID = field(default_factory=uuid4)
    generation: int = 0
    genome: G = field(default_factory=lambda: None)  # type: ignore
    fitness: float = 0.0
    score_breakdown: Dict[str, float] = field(default_factory=dict)
    parent_ids: List[UUID] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def __str__(self) -> str:
        return f"Candidate(id={self.id}, generation={self.generation}, fitness={self.fitness:.3f})"

    def copy(self) -> "Candidate[G]":
        """Create a copy of this candidate."""
        return Candidate(
            id=self.id,
            generation=self.generation,
            genome=self._copy_genome(self.genome),
            fitness=self.fitness,
            score_breakdown=self.score_breakdown.copy(),
            parent_ids=self.parent_ids.copy(),
            metadata=self.metadata.copy(),
            created_at=self.created_at,
        )

    def _copy_genome(self, genome: G) -> G:
        """Create a copy of the genome, handling different genome types."""
        try:
            # Try to use genome's copy method if it exists
            return genome.copy()  # type: ignore
        except AttributeError:
            # Fallback to deepcopy
            import copy

            return copy.deepcopy(genome)

    def to_dict(self) -> Dict[str, Any]:
        """Convert candidate to dictionary representation."""
        return {
            "id": str(self.id),
            "generation": self.generation,
            "genome": self._genome_to_dict(self.genome),
            "fitness": self.fitness,
            "score_breakdown": self.score_breakdown,
            "parent_ids": [str(pid) for pid in self.parent_ids],
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def _genome_to_dict(self, genome: G) -> Any:
        """Convert genome to dictionary representation."""
        try:
            # Try to use genome's to_dict method if it exists
            return genome.to_dict()  # type: ignore
        except AttributeError:
            # Fallback to string representation
            return str(genome)


class Population(Generic[G]):
    """Generic population of candidate solutions."""

    def __init__(self, generation: int = 0):
        self.generation = generation
        self._candidates: List[Candidate[G]] = []

    def add_candidate(self, candidate: Candidate[G]) -> None:
        """Add candidate to population."""
        self._candidates.append(candidate)

    def add_candidates(self, candidates: List[Candidate[G]]) -> None:
        """Add multiple candidates to population."""
        self._candidates.extend(candidates)

    def size(self) -> int:
        """Return number of candidates in population."""
        return len(self._candidates)

    def is_empty(self) -> bool:
        """Return True if population has no candidates."""
        return self.size() == 0

    @property
    def candidates(self) -> List[Candidate[G]]:
        """Return list of candidates."""
        return self._candidates.copy()

    def get_top_n(self, n: int) -> List[Candidate[G]]:
        """Return top N candidates by fitness (descending)."""
        sorted_candidates = sorted(
            self._candidates, key=lambda c: c.fitness, reverse=True
        )
        return sorted_candidates[:n]

    def get_best_fitness(self) -> float:
        """Return highest fitness in population."""
        if self.is_empty():
            return 0.0
        return max(c.fitness for c in self._candidates)

    def get_average_fitness(self) -> float:
        """Return average fitness of population."""
        if self.is_empty():
            return 0.0
        total_fitness = sum(c.fitness for c in self._candidates)
        return total_fitness / self.size()

    def get_worst_fitness(self) -> float:
        """Return lowest fitness in population."""
        if self.is_empty():
            return 0.0
        return min(c.fitness for c in self._candidates)

    def get_fitness_range(self) -> tuple[float, float]:
        """Return min and max fitness values in population."""
        if self.is_empty():
            return (0.0, 0.0)
        fitness_values = [c.fitness for c in self._candidates]
        return (min(fitness_values), max(fitness_values))

    def get_fitness_stats(self) -> Dict[str, float]:
        """Return fitness statistics dictionary."""
        fitness_range = self.get_fitness_range()
        return {
            "best": self.get_best_fitness(),
            "average": self.get_average_fitness(),
            "worst": self.get_worst_fitness(),
            "size": self.size(),
            "generation": self.generation,
            "min": fitness_range[0],
            "max": fitness_range[1],
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert population to dictionary representation."""
        return {
            "generation": self.generation,
            "candidates": [c.to_dict() for c in self._candidates],
            "fitness_stats": self.get_fitness_stats(),
        }

    def __len__(self) -> int:
        """Return number of candidates (allows len(population))."""
        return self.size()

    def __getitem__(self, index: int) -> Candidate[G]:
        """Get candidate by index (allows population[index])."""
        return self._candidates[index]

    def copy(self) -> "Population[G]":
        """Create a copy of the population."""
        new_population = Population(generation=self.generation)
        for candidate in self._candidates:
            new_population.add_candidate(candidate.copy())
        return new_population

    def __str__(self) -> str:
        stats = self.get_fitness_stats()
        return f"Population(generation={self.generation}, size={stats['size']}, best={stats['best']:.3f}, avg={stats['average']:.3f})"
