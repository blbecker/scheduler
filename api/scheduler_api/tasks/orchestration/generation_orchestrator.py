"""Generation orchestrator for evolutionary operations."""

import logging
from typing import Any
import time

from scheduler_api.dto.population import PopulationDTO
from scheduler_api.dto.solve_context import ScheduleSolveContextDTO
from scheduler_api.tasks.core.evolutionary import (
    score_population,
    select_population,
    crossover_population,
    mutate_population,
)

logger = logging.getLogger(__name__)


class GenerationOrchestrator:
    """Orchestrates one generation of evolution using pure functions."""

    def __init__(
        self,
        component_classes: dict[str, Any],
        logger_instance: logging.Logger | None = None,
    ):
        self.component_classes = component_classes
        self.logger = logger_instance or logger

    def evolve_generation(
        self,
        solve_id: str,
        generation: int,
        population_dto: PopulationDTO,
        component_dtos: dict[str, list[dict]],  # Serialized DTO dicts
        context_dto: ScheduleSolveContextDTO,
        parameters: dict[str, Any],
    ) -> tuple[PopulationDTO, dict[str, Any]]:
        """
        Execute one generation evolution: Score → Select → Crossover → Mutate.

        Args:
            solve_id: Solve identifier for logging
            generation: Current generation number
            population_dto: Population to evolve
            component_dtos: Component DTO dicts by type
            context_dto: Solve context
            parameters: Evolution parameters

        Returns:
            Tuple of (evolved PopulationDTO, generation metrics)

        Raises:
            Exception: If any evolutionary operation fails
        """
        start_time = time.time()
        self.logger.info(f"[Solve {solve_id}] Generation {generation} starting")

        try:
            # Deserialize DTOs
            from scheduler_api.dto.solve_components import (
                ScorerDTO,
                ConstraintDTO,
                SelectorDTO,
                MutatorDTO,
            )

            scorer_dtos = [ScorerDTO(**d) for d in component_dtos.get("scorers", [])]
            constraint_dtos = [
                ConstraintDTO(**d) for d in component_dtos.get("constraints", [])
            ]
            selector_dto = (
                SelectorDTO(**component_dtos["selectors"][0])
                if component_dtos.get("selectors")
                else None
            )
            mutator_dtos = [MutatorDTO(**d) for d in component_dtos.get("mutators", [])]

            if not scorer_dtos:
                raise ValueError("No scorers configured")
            if not selector_dto:
                raise ValueError("No selector configured")

            # 1. Score population
            scored_population, scoring_metrics = score_population(
                population_dto=population_dto,
                scorer_dtos=scorer_dtos,
                constraint_dtos=constraint_dtos,
                context_dto=context_dto,
                component_classes=self.component_classes,
            )

            # 2. Select population
            target_size = len(population_dto.candidates)
            elite_size = parameters.get("elite_size", 1)

            selected_population, selection_metrics = select_population(
                scored_population_dto=scored_population,
                selector_dto=selector_dto,
                context_dto=context_dto,
                component_classes=self.component_classes,
                elite_size=elite_size,
                target_size=target_size,
            )

            # 3. Apply crossover
            crossover_rate = parameters.get("crossover_rate", 0.8)
            crossed_population, crossover_metrics = crossover_population(
                population_dto=selected_population,
                context_dto=context_dto,
                component_classes=self.component_classes,
                crossover_rate=crossover_rate,
            )

            # 4. Apply mutation
            mutation_rate = parameters.get("mutation_rate", 0.1)
            mutated_population, mutation_metrics = mutate_population(
                population_dto=crossed_population,
                mutator_dtos=mutator_dtos,
                context_dto=context_dto,
                component_classes=self.component_classes,
                mutation_rate=mutation_rate,
            )

            # Update generation number
            evolved_population = PopulationDTO(
                generation=generation + 1, candidates=mutated_population.candidates
            )

            # Calculate generation metrics
            elapsed_time = time.time() - start_time
            best_fitness = evolved_population.get_best_fitness()
            avg_fitness = evolved_population.get_average_fitness()

            generation_metrics = {
                "generation": generation,
                "elapsed_time": elapsed_time,
                "best_fitness": best_fitness,
                "average_fitness": avg_fitness,
                "population_size": len(evolved_population.candidates),
                "scoring": scoring_metrics,
                "selection": selection_metrics,
                "crossover": crossover_metrics,
                "mutation": mutation_metrics,
            }

            self.logger.info(
                f"[Solve {solve_id}] Generation {generation} completed: "
                f"best={best_fitness:.3f}, avg={avg_fitness:.3f}, "
                f"elapsed={elapsed_time:.2f}s"
            )

            return evolved_population, generation_metrics

        except Exception as e:
            self.logger.error(f"[Solve {solve_id}] Generation {generation} failed: {e}")
            raise
