"""Main solve orchestrator."""

import logging
import time
from typing import Any
from uuid import UUID

from scheduler_api.dto.population import PopulationDTO
from scheduler_api.dto.solve_context import ScheduleSolveContextDTO
from scheduler_api.tasks.core.initialization import (
    initialize_context,
    create_initial_population,
)
from scheduler_api.tasks.orchestration.generation_orchestrator import (
    GenerationOrchestrator,
)

logger = logging.getLogger(__name__)


class ConcreteSolveOrchestrator:
    """
    Orchestrates entire solve execution across multiple generations.

    Replaces the old ParallelSolveOrchestrator with pure DTO functions.
    """

    def __init__(
        self,
        component_classes: dict[str, Any],
        logger_instance: logging.Logger | None = None,
    ):
        """
        Args:
            component_classes: Mapping of component type to class
            logger_instance: Optional logger instance
        """
        self.component_classes = component_classes
        self.logger = logger_instance or logger
        self.generation_orchestrator = GenerationOrchestrator(
            component_classes=component_classes, logger_instance=self.logger
        )

    def solve(
        self,
        solve_id: str,
        template_id: UUID,
        parameters: dict[str, Any],
        component_dtos: dict[str, list[dict]],
    ) -> dict[str, Any]:
        """
        Execute complete solve across multiple generations.

        Args:
            solve_id: Unique solve identifier
            template_id: Schedule template ID
            parameters: Solve parameters
            component_dtos: Component DTO dicts by type

        Returns:
            Solve result dictionary with best genome and metrics
        """
        start_time = time.time()
        self.logger.info(f"[Solve {solve_id}] Starting solve execution")

        try:
            # 1. Initialize context
            # TODO: Fetch actual shift/worker data from database
            context_dto = initialize_context(
                template_id=template_id,
                parameters=parameters,
                # These would come from database in production
                shift_ids=[],
                worker_ids=[],
                skill_requirements={},
                worker_skills={},
            )

            # 2. Create initial population
            population_size = parameters.get("population_size", 50)
            population_dto = create_initial_population(
                context_dto=context_dto,
                population_size=population_size,
                seeder_dtos=component_dtos.get("seeders", []),
                component_classes=self.component_classes,
            )

            # 3. Execute generation loop
            max_generations = parameters.get("max_generations", 100)
            all_metrics = []
            best_fitness_history = []

            for generation in range(max_generations):
                try:
                    (
                        population_dto,
                        generation_metrics,
                    ) = self.generation_orchestrator.evolve_generation(
                        solve_id=solve_id,
                        generation=generation,
                        population_dto=population_dto,
                        component_dtos=component_dtos,
                        context_dto=context_dto,
                        parameters=parameters,
                    )

                    all_metrics.append(generation_metrics)
                    best_fitness_history.append(generation_metrics["best_fitness"])

                    # Log progress every 10 generations
                    if generation % 10 == 0 or generation == max_generations - 1:
                        self.logger.info(
                            f"[Solve {solve_id}] Progress: {generation + 1}/{max_generations} "
                            f"generations, best fitness: {generation_metrics['best_fitness']:.3f}"
                        )

                except Exception as e:
                    self.logger.error(
                        f"[Solve {solve_id}] Generation {generation} failed: {e}"
                    )
                    # Fail entire solve if any generation fails
                    raise

            # 4. Compile final result
            elapsed_time = time.time() - start_time
            best_fitness = best_fitness_history[-1] if best_fitness_history else 0.0

            # Get best candidate
            best_candidate = None
            if population_dto.candidates:
                sorted_candidates = sorted(
                    population_dto.candidates, key=lambda c: c.fitness, reverse=True
                )
                best_candidate = sorted_candidates[0]

            result = {
                "solve_id": solve_id,
                "status": "completed",
                "elapsed_time": elapsed_time,
                "generations_completed": max_generations,
                "best_fitness": best_fitness,
                "best_genome": best_candidate.genome_data if best_candidate else {},
                "final_population_size": len(population_dto.candidates),
                "fitness_history": best_fitness_history,
                "generation_metrics": all_metrics,
                "component_configuration": {
                    "scorers": len(component_dtos.get("scorers", [])),
                    "mutators": len(component_dtos.get("mutators", [])),
                    "constraints": len(component_dtos.get("constraints", [])),
                    "selectors": len(component_dtos.get("selectors", [])),
                    "seeders": len(component_dtos.get("seeders", [])),
                },
            }

            self.logger.info(
                f"[Solve {solve_id}] Solve completed: "
                f"{max_generations} generations, "
                f"best fitness: {best_fitness:.3f}, "
                f"elapsed time: {elapsed_time:.1f}s"
            )

            return result

        except Exception as e:
            elapsed_time = time.time() - start_time
            self.logger.error(
                f"[Solve {solve_id}] Solve failed after {elapsed_time:.1f}s: {e}"
            )

            return {
                "solve_id": solve_id,
                "status": "failed",
                "elapsed_time": elapsed_time,
                "error": str(e),
                "generations_completed": 0,
                "best_fitness": 0.0,
            }

    def get_default_component_dtos(self) -> dict[str, list[dict]]:
        """Get default component DTOs matching the old pipeline composition."""
        return {
            "seeders": [
                {
                    "component_type": "random_seeder",
                    "name": "Random Seeder",
                    "config": {},
                }
            ],
            "scorers": [
                {
                    "component_type": "skills_match_scorer",
                    "name": "Skills Match Scorer",
                    "config": {},
                }
            ],
            "mutators": [
                {
                    "component_type": "random_assignment_mutator",
                    "name": "Random Assignment Mutator",
                    "config": {},
                },
                {
                    "component_type": "swap_assignment_mutator",
                    "name": "Swap Assignment Mutator",
                    "config": {},
                },
            ],
            "constraints": [
                {
                    "component_type": "no_double_booking_constraint",
                    "name": "No Double Booking Constraint",
                    "config": {},
                }
            ],
            "selectors": [
                {
                    "component_type": "tournament_selector",
                    "name": "Tournament Selector",
                    "config": {"tournament_size": 3},
                }
            ],
        }
