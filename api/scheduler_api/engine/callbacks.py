"""Generic callback protocol for evolution progress tracking."""

import logging
from typing import Protocol, Any, TypeVar, Generic
from .population import Population

logger = logging.getLogger(__name__)

# Type variable for population type
P = TypeVar("P", bound=Population)


class EvolutionCallback(Protocol[P]):
    """Protocol for evolution progress callbacks."""

    def on_generation_start(self, generation: int, population: P) -> None:
        """Called at start of each generation."""
        ...

    def on_generation_complete(self, generation: int, population: P) -> None:
        """Called at end of each generation."""
        ...

    def on_scoring_complete(self, population: P) -> None:
        """Called after population scoring."""
        ...

    def on_selection_complete(self, selected: list[Any], context: Any) -> None:
        """Called after parent selection."""
        ...

    def on_offspring_created(self, offspring: list[Any]) -> None:
        """Called after offspring creation."""
        ...


class LoggingCallback:
    """Simple callback that logs evolution progress."""

    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)

    def on_generation_start(self, generation: int, population: Population) -> None:
        if self.logger:
            self.logger.info(f"Starting generation {generation}")

    def on_generation_complete(self, generation: int, population: Population) -> None:
        best_fitness = population.get_best_fitness()
        avg_fitness = population.get_average_fitness()
        if self.logger:
            self.logger.info(
                f"Generation {generation} complete: "
                f"Best={best_fitness:.3f}, Avg={avg_fitness:.3f}, "
                f"Size={population.size()}"
            )

    def on_scoring_complete(self, population: Population) -> None:
        pass

    def on_selection_complete(self, selected: list[Any], context: Any) -> None:
        pass

    def on_offspring_created(self, offspring: list[Any]) -> None:
        pass
