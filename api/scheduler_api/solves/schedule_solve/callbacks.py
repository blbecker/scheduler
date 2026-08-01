"""Schedule-specific callback implementations."""

import logging
from typing import Optional
from uuid import UUID

from scheduler_api.engine.callbacks import EvolutionCallback
from scheduler_api.engine.population import Population
from scheduler_api.services.schedule_solve_service import ScheduleSolveService
from scheduler_api.db.models.enums import ScheduleSolveStatus

logger = logging.getLogger(__name__)


class DatabaseCallback(EvolutionCallback):
    """Callback that updates ScheduleSolveModel progress in database."""

    def __init__(self, solve_id: UUID, service: ScheduleSolveService):
        self.solve_id = solve_id
        self.service = service
        self.max_generations: Optional[int] = None

    def on_generation_start(self, generation: int, population: Population) -> None:
        """Called at start of each generation."""
        # Nothing to do at generation start
        pass

    def on_generation_complete(self, generation: int, population: Population) -> None:
        """Called at end of each generation."""
        try:
            best_fitness = population.get_best_fitness()

            # Calculate progress if we know max generations
            progress = None
            if self.max_generations:
                progress = min(1.0, generation / self.max_generations)

            self.service.update_schedule_solve_progress(
                self.solve_id,
                current_generation=generation,
                best_fitness=best_fitness,
                progress=progress,
            )

            logger.debug(
                f"Updated progress for solve {self.solve_id}: "
                f"generation={generation}, fitness={best_fitness:.3f}"
            )

        except Exception as e:
            logger.error(f"Failed to update progress for solve {self.solve_id}: {e}")

    def on_scoring_complete(self, population: Population) -> None:
        """Called after population scoring."""
        pass

    def on_selection_complete(self, selected: list, context) -> None:
        """Called after parent selection."""
        pass

    def on_offspring_created(self, offspring: list) -> None:
        """Called after offspring creation."""
        pass
