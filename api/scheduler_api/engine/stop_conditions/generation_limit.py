"""Generation limit stop condition."""

from dataclasses import dataclass
from typing import TypeVar
from ..interfaces import Stoppable

# Type variables for generics
P = TypeVar("P")  # Population type
T = TypeVar("T")  # Context type


@dataclass
class GenerationLimitStopCondition(Stoppable[P, T]):
    """Stop after reaching max generations."""

    max_generations: int
    name: str = "generation_limit"

    def should_stop(
        self, population: P, generation: int, start_time: float, context: T
    ) -> bool:
        """Return True if generation limit reached."""
        return generation >= self.max_generations
