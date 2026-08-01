"""Component-level Celery tasks for evolutionary operations."""

import logging
from typing import Any
from celery import shared_task

from scheduler_api.dto.population import PopulationDTO
from scheduler_api.dto.solve_context import ScheduleSolveContextDTO
from scheduler_api.dto.solve_components import (
    ScorerDTO,
    MutatorDTO,
    ConstraintDTO,
    SelectorDTO,
)
from scheduler_api.tasks.core.evolutionary import (
    score_population,
    select_population,
    crossover_population,
    mutate_population,
)

logger = logging.getLogger(__name__)


def _deserialize_dto_dicts(dto_dicts: list[dict], dto_class: type) -> list:
    """Deserialize list of dicts to DTO objects."""
    return [dto_class(**d) for d in dto_dicts]


@shared_task(bind=True, max_retries=0)
def score_population_task(
    self,
    solve_id: str,
    generation: int,
    population_dto: dict[str, Any],  # Serialized PopulationDTO
    scorer_dtos: list[dict],
    constraint_dtos: list[dict],
    context_dto: dict[str, Any],
    component_classes: dict[str, str],  # Component type -> class path
) -> dict[str, Any]:
    """
    Celery task wrapper for score_population pure function.

    Args:
        solve_id: Solve identifier
        generation: Current generation number
        population_dto: Serialized PopulationDTO
        scorer_dtos: List of serialized ScorerDTOs
        constraint_dtos: List of serialized ConstraintDTOs
        context_dto: Serialized ScheduleSolveContextDTO
        component_classes: Component type -> class path mapping

    Returns:
        Serialized result: {"population": ..., "metrics": ...}
    """
    logger.info(f"[Solve {solve_id}] Score population task for generation {generation}")

    try:
        # Deserialize DTOs
        population = PopulationDTO(**population_dto)
        context = ScheduleSolveContextDTO(**context_dto)
        scorers = _deserialize_dto_dicts(scorer_dtos, ScorerDTO)
        constraints = _deserialize_dto_dicts(constraint_dtos, ConstraintDTO)

        # Resolve component classes from string paths
        # For now, we need to import them dynamically
        resolved_classes = _resolve_component_classes(component_classes)

        # Call pure function
        scored_population, metrics = score_population(
            population_dto=population,
            scorer_dtos=scorers,
            constraint_dtos=constraints,
            context_dto=context,
            component_classes=resolved_classes,
        )

        result = {
            "population": scored_population.model_dump(),
            "metrics": metrics,
            "status": "completed",
        }

        return result

    except Exception as e:
        logger.error(f"[Solve {solve_id}] Score population task failed: {e}")
        raise


@shared_task(bind=True, max_retries=0)
def select_population_task(
    self,
    solve_id: str,
    generation: int,
    scored_population_dto: dict[str, Any],
    selector_dto: dict[str, Any],
    context_dto: dict[str, Any],
    component_classes: dict[str, str],
    elite_size: int,
    target_size: int,
) -> dict[str, Any]:
    """
    Celery task wrapper for select_population pure function.
    """
    logger.info(
        f"[Solve {solve_id}] Select population task for generation {generation}"
    )

    try:
        # Deserialize DTOs
        population = PopulationDTO(**scored_population_dto)
        context = ScheduleSolveContextDTO(**context_dto)
        selector = SelectorDTO(**selector_dto)

        # Resolve component classes
        resolved_classes = _resolve_component_classes(component_classes)

        # Call pure function
        selected_population, metrics = select_population(
            scored_population_dto=population,
            selector_dto=selector,
            context_dto=context,
            component_classes=resolved_classes,
            elite_size=elite_size,
            target_size=target_size,
        )

        result = {
            "population": selected_population.model_dump(),
            "metrics": metrics,
            "status": "completed",
        }

        return result

    except Exception as e:
        logger.error(f"[Solve {solve_id}] Select population task failed: {e}")
        raise


@shared_task(bind=True, max_retries=0)
def crossover_population_task(
    self,
    solve_id: str,
    generation: int,
    population_dto: dict[str, Any],
    context_dto: dict[str, Any],
    component_classes: dict[str, str],
    crossover_rate: float,
) -> dict[str, Any]:
    """
    Celery task wrapper for crossover_population pure function.
    """
    logger.info(
        f"[Solve {solve_id}] Crossover population task for generation {generation}"
    )

    try:
        # Deserialize DTOs
        population = PopulationDTO(**population_dto)
        context = ScheduleSolveContextDTO(**context_dto)

        # Resolve component classes
        resolved_classes = _resolve_component_classes(component_classes)

        # Call pure function
        crossed_population, metrics = crossover_population(
            population_dto=population,
            context_dto=context,
            component_classes=resolved_classes,
            crossover_rate=crossover_rate,
        )

        result = {
            "population": crossed_population.model_dump(),
            "metrics": metrics,
            "status": "completed",
        }

        return result

    except Exception as e:
        logger.error(f"[Solve {solve_id}] Crossover population task failed: {e}")
        raise


@shared_task(bind=True, max_retries=0)
def mutate_population_task(
    self,
    solve_id: str,
    generation: int,
    population_dto: dict[str, Any],
    mutator_dtos: list[dict],
    context_dto: dict[str, Any],
    component_classes: dict[str, str],
    mutation_rate: float,
) -> dict[str, Any]:
    """
    Celery task wrapper for mutate_population pure function.
    """
    logger.info(
        f"[Solve {solve_id}] Mutate population task for generation {generation}"
    )

    try:
        # Deserialize DTOs
        population = PopulationDTO(**population_dto)
        context = ScheduleSolveContextDTO(**context_dto)
        mutators = _deserialize_dto_dicts(mutator_dtos, MutatorDTO)

        # Resolve component classes
        resolved_classes = _resolve_component_classes(component_classes)

        # Call pure function
        mutated_population, metrics = mutate_population(
            population_dto=population,
            mutator_dtos=mutators,
            context_dto=context,
            component_classes=resolved_classes,
            mutation_rate=mutation_rate,
        )

        result = {
            "population": mutated_population.model_dump(),
            "metrics": metrics,
            "status": "completed",
        }

        return result

    except Exception as e:
        logger.error(f"[Solve {solve_id}] Mutate population task failed: {e}")
        raise


def _resolve_component_classes(component_classes: dict[str, str]) -> dict[str, Any]:
    """
    Resolve component class paths to actual classes.

    Args:
        component_classes: Mapping of component type -> fully qualified class path

    Returns:
        Mapping of component type -> class
    """
    resolved = {}

    for component_type, class_path in component_classes.items():
        try:
            # Import module and get class
            module_path, class_name = class_path.rsplit(".", 1)
            module = __import__(module_path, fromlist=[class_name])
            component_class = getattr(module, class_name)
            resolved[component_type] = component_class
        except Exception as e:
            logger.warning(f"Failed to resolve component class {class_path}: {e}")
            # Keep string for now - will be handled in instantiate_component

    return resolved
