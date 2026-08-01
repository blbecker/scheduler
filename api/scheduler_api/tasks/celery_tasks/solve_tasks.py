"""Solve-level Celery tasks."""

import logging
from typing import Any
from uuid import uuid4
from celery import shared_task

from scheduler_api.tasks.orchestration.solve_orchestrator import (
    ConcreteSolveOrchestrator,
)
from scheduler_api.tasks.orchestration.generation_orchestrator import (
    GenerationOrchestrator,
)

logger = logging.getLogger(__name__)


def _get_default_component_classes() -> dict[str, str]:
    """Get default component class mappings."""
    return {
        "SkillsMatchScorer": "scheduler_api.solves.scorers.skills_match_scorer.SkillsMatchScorer",
        "NoDoubleBookingConstraint": "scheduler_api.solves.constraints.no_double_booking_constraint.NoDoubleBookingConstraint",
        "TournamentSelector": "scheduler_api.solves.selectors.tournament_selector.TournamentSelector",
        "RandomAssignmentMutator": "scheduler_api.solves.mutators.random_assignment_mutator.RandomAssignmentMutator",
        "RandomSeeder": "scheduler_api.solves.seeders.random_seeder.RandomSeeder",
    }


def _get_default_component_dtos() -> dict[str, list[dict]]:
    """Get default component DTOs matching the old pipeline."""
    # This is a placeholder - in production, DTOs would be created properly
    return {
        "seeders": [{"component_type": "RandomSeeder", "parameters": {}}],
        "scorers": [{"component_type": "SkillsMatchScorer", "parameters": {}}],
        "constraints": [
            {"component_type": "NoDoubleBookingConstraint", "parameters": {}}
        ],
        "selectors": [
            {
                "component_type": "TournamentSelector",
                "parameters": {"tournament_size": 3},
            }
        ],
        "mutators": [{"component_type": "RandomAssignmentMutator", "parameters": {}}],
        "crossovers": [{"component_type": "UniformCrossover", "parameters": {}}],
    }


def _get_default_parameters() -> dict[str, Any]:
    """Get default evolution parameters."""
    return {
        "population_size": 50,
        "max_generations": 100,
        "elite_size": 1,
        "crossover_rate": 0.8,
        "mutation_rate": 0.1,
    }


def _resolve_component_classes(class_mapping: dict[str, str]) -> dict[str, Any]:
    """Resolve component class paths to actual classes."""
    resolved = {}

    for component_type, class_path in class_mapping.items():
        try:
            # Import module and get class
            module_path, class_name = class_path.rsplit(".", 1)
            module = __import__(module_path, fromlist=[class_name])
            component_class = getattr(module, class_name)
            resolved[component_type] = component_class
        except Exception as e:
            logger.warning(f"Failed to resolve component class {class_path}: {e}")
            # Keep string for now - will be handled differently

    return resolved


@shared_task(bind=True, max_retries=1)
def schedule_solve_task(
    self, schedule_solve_id: str, preset: str = "default"
) -> dict[str, Any]:
    """
    Main Celery task for scheduling solve.

    This task orchestrates the complete solve process using the ConcreteSolveOrchestrator.

    Args:
        schedule_solve_id: ID of the ScheduleSolveModel
        preset: Preset configuration name ("default" or custom)

    Returns:
        Dictionary with solve results
    """
    logger.info(
        f"[Solve {schedule_solve_id}] Starting solve task with preset '{preset}'"
    )

    try:
        # Get component DTOs and parameters for the preset
        component_dtos = _get_default_component_dtos()
        parameters = _get_default_parameters()

        # Component class mappings
        component_classes_mapping = _get_default_component_classes()
        resolved_classes = _resolve_component_classes(component_classes_mapping)

        # Create solve orchestrator
        orchestrator = ConcreteSolveOrchestrator(
            component_classes=resolved_classes, logger_instance=logger
        )

        # Create a template ID for now (in production, this would come from the solve)
        template_id = uuid4()

        # Execute solve using orchestrator
        result = orchestrator.solve(
            solve_id=schedule_solve_id,
            template_id=template_id,
            parameters=parameters,
            component_dtos=component_dtos,
        )

        logger.info(f"[Solve {schedule_solve_id}] Solve completed successfully")

        # In production, this would update the database
        return {
            "status": "completed",
            "solve_id": schedule_solve_id,
            "best_candidate": result.get("best_candidate"),
            "best_fitness": result.get("best_fitness"),
            "final_generation": result.get("generation"),
            "elapsed_time": result.get("elapsed_time"),
        }

    except Exception as e:
        logger.error(f"[Solve {schedule_solve_id}] Solve task failed: {e}")

        # Retry logic
        if self.request.retries < self.max_retries:
            logger.info(f"[Solve {schedule_solve_id}] Retrying solve task")
            raise self.retry(exc=e)
        else:
            # In production, update database with failure status
            return {"status": "failed", "solve_id": schedule_solve_id, "error": str(e)}
