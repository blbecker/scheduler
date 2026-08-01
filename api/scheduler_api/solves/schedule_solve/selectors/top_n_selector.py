"""Top N selector for population selection."""

from dataclasses import dataclass
from scheduler_api.engine.interfaces import Selector
from scheduler_api.domain.schedule import Schedule
from ..context import ScheduleSolveContext


@dataclass
class TopNSelector(Selector[Schedule, ScheduleSolveContext]):
    """Selector that chooses top N schedules by score."""

    name: str = "top_n_selector"

    def select(
        self,
        population: list[tuple[Schedule, float]],
        context: ScheduleSolveContext,
        count: int,
    ) -> list[Schedule]:
        """Select top N schedules by score."""
        if not population:
            return []

        # Sort by score descending
        sorted_population = sorted(population, key=lambda x: x[1], reverse=True)

        # Select top N
        selected_count = min(count, len(sorted_population))
        selected_schedules = [
            schedule for schedule, _ in sorted_population[:selected_count]
        ]

        return selected_schedules
