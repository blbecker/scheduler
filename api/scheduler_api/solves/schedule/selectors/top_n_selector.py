"""Top N selector for population selection."""

from dataclasses import dataclass
from typing import List, Tuple
from ...interfaces import Selector
from ..genome import ScheduleGenome
from ..context import ScheduleSolveContext


@dataclass
class TopNSelector(Selector[ScheduleGenome, ScheduleSolveContext]):
    """Selector that chooses top N genomes by score."""

    name: str = "top_n_selector"

    def select(
        self,
        population: List[Tuple[ScheduleGenome, float]],
        context: ScheduleSolveContext,
        count: int,
    ) -> List[ScheduleGenome]:
        """Select top N genomes by score."""
        if not population:
            return []

        # Sort by score descending
        sorted_population = sorted(population, key=lambda x: x[1], reverse=True)

        # Select top N
        selected_count = min(count, len(sorted_population))
        selected_genomes = [genome for genome, _ in sorted_population[:selected_count]]

        return selected_genomes
