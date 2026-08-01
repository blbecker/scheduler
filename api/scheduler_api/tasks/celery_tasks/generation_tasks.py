"""Generation-level Celery tasks."""

import logging
from typing import Any
from celery import shared_task

from scheduler_api.tasks.celery_tasks.component_tasks import (
    score_population_task,
    select_population_task,
    crossover_population_task,
    mutate_population_task,
)

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=1)
def evolve_generation_task(
    self,
    solve_id: str,
    generation: int,
    population_dto: dict[str, Any],
    component_dtos: dict[str, list[dict]],
    context_dto: dict[str, Any],
    parameters: dict[str, Any],
    component_classes: dict[str, str],
) -> dict[str, Any]:
    """
    Celery chain task for evolving one generation.

    Chains: score → select → crossover → mutate

    Args:
        solve_id: Solve identifier
        generation: Current generation number
        population_dto: Serialized PopulationDTO
        component_dtos: Component DTO dicts by type
        context_dto: Serialized ScheduleSolveContextDTO
        parameters: Evolution parameters
        component_classes: Component type -> class path mapping

    Returns:
        Result of the complete chain execution
    """
    logger.info(
        f"[Solve {solve_id}] Evolve generation task for generation {generation}"
    )

    try:
        # Extract parameters
        elite_size = parameters.get("elite_size", 1)
        crossover_rate = parameters.get("crossover_rate", 0.8)
        mutation_rate = parameters.get("mutation_rate", 0.1)
        target_size = len(population_dto.get("candidates", []))

        # Extract component DTOs
        scorer_dtos = component_dtos.get("scorers", [])
        constraint_dtos = component_dtos.get("constraints", [])
        selector_dto = component_dtos.get("selectors", [{}])[0]
        mutator_dtos = component_dtos.get("mutators", [])

        # For now, execute sequentially instead of using chain
        # This avoids Celery chain complexity

        # Execute tasks sequentially
        result = population_dto

        # Task 1: Score
        score_result = score_population_task.apply(
            kwargs={
                "solve_id": solve_id,
                "generation": generation,
                "population_dto": result,
                "scorer_dtos": scorer_dtos,
                "constraint_dtos": constraint_dtos,
                "context_dto": context_dto,
                "component_classes": component_classes,
            }
        ).get(timeout=300)
        result = score_result.get("population", result)

        # Task 2: Select
        select_result = select_population_task.apply(
            kwargs={
                "solve_id": solve_id,
                "generation": generation,
                "scored_population_dto": result,
                "selector_dto": selector_dto,
                "context_dto": context_dto,
                "component_classes": component_classes,
                "elite_size": elite_size,
                "target_size": target_size,
            }
        ).get(timeout=300)
        result = select_result.get("population", result)

        # Task 3: Crossover
        crossover_result = crossover_population_task.apply(
            kwargs={
                "solve_id": solve_id,
                "generation": generation,
                "population_dto": result,
                "context_dto": context_dto,
                "component_classes": component_classes,
                "crossover_rate": crossover_rate,
            }
        ).get(timeout=300)
        result = crossover_result.get("population", result)

        # Task 4: Mutate
        mutate_result = mutate_population_task.apply(
            kwargs={
                "solve_id": solve_id,
                "generation": generation,
                "population_dto": result,
                "mutator_dtos": mutator_dtos,
                "context_dto": context_dto,
                "component_classes": component_classes,
                "mutation_rate": mutation_rate,
            }
        ).get(timeout=300)
        result = mutate_result.get("population", result)
        final_metrics = mutate_result.get("metrics", {})

        # Update generation number in population
        if "population" in result:
            result["population"]["generation"] = generation + 1

        logger.info(
            f"[Solve {solve_id}] Generation {generation} evolution chain completed"
        )
        return final_metrics

    except Exception as e:
        logger.error(f"[Solve {solve_id}] Evolve generation task failed: {e}")

        # Retry logic
        if self.request.retries < self.max_retries:
            logger.info(f"[Solve {solve_id}] Retrying generation {generation} task")
            raise self.retry(exc=e)
        else:
            raise
