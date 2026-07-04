"""Generation limit stop condition."""

from dataclasses import dataclass
from ...interfaces import Stoppable


@dataclass
class GenerationLimitStopCondition(Stoppable[list, object]):
    """Stop after reaching max generations."""

    max_generations: int
    name: str = "generation_limit"

    def should_stop(
        self, population: list, generation: int, start_time: float, context: object
    ) -> bool:
        """Return True if generation limit reached."""
        return generation >= self.max_generations
