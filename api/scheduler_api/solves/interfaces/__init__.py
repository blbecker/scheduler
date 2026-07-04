"""Core protocol interfaces for the extensible solve framework."""

from typing import Protocol, Any, TypeVar, Generic
from uuid import UUID

# Type variables for generic protocols
T = TypeVar("T")  # Context type
G = TypeVar("G")  # Genome type
P = TypeVar("P")  # Population type
R = TypeVar("R")  # Pipeline result type


class Solvable(Protocol[T, G, P, R]):
    """Protocol for solve types (e.g., schedule-solve, route-solve)."""

    name: str

    def create_context(self, template_id: UUID, parameters: dict) -> T:
        """Create solve context from template and parameters."""
        ...

    def create_initial_population(self, context: T, size: int) -> list[G]:
        """Generate initial population of genomes."""
        ...

    def create_pipeline(self) -> R:
        """Return pipeline configuration."""
        ...


class GenomeOperator(Protocol[G, T]):
    """Protocol for genome transformation operators (mutators, crossover)."""

    name: str

    def apply(self, genome: G, context: T) -> G:
        """Transform genome and return new genome."""
        ...


class Scorable(Protocol[G, T]):
    """Protocol for scoring genomes."""

    name: str

    def score(self, genome: G, context: T) -> float:
        """Calculate and return score for genome."""
        ...


class Constraint(Protocol[G, T]):
    """Protocol for constraint validation."""

    name: str

    def validate(self, genome: G, context: T) -> bool:
        """Return True if genome satisfies constraint."""
        ...

    def penalty(self, genome: G, context: T) -> float:
        """Return penalty score for constraint violation (0.0 = no violation)."""
        ...


class Selector(Protocol[G, T]):
    """Protocol for population selection."""

    name: str

    def select(
        self, population: list[tuple[G, float]], context: T, count: int
    ) -> list[G]:
        """Select genomes from scored population."""
        ...


class Seeder(Protocol[G, T]):
    """Protocol for initial population generation."""

    name: str

    def seed(self, context: T, count: int) -> list[G]:
        """Generate initial genomes."""
        ...


class Stoppable(Protocol[P, T]):
    """Protocol for stop conditions."""

    name: str

    def should_stop(
        self, population: P, generation: int, start_time: float, context: T
    ) -> bool:
        """Return True if evolution should stop."""
        ...
