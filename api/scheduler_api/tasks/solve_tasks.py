"""Celery tasks for solve framework."""

import time
import logging
from celery import shared_task
from uuid import UUID
from scheduler_api.schemas.solve import ScheduleSolveParameters
from scheduler_api.solves.schedule.solver import ScheduleSolver
from scheduler_api.solves.engine.orchestrator import SolveOrchestrator
from scheduler_api.solves.schedule.genome import ScheduleGenomeDTO

logger = logging.getLogger(__name__)


@shared_task
def schedule_solve_task(template_id: str, parameters_dict: dict) -> dict:
    """
    Celery task for schedule solve execution.

    Args:
        template_id: UUID string of schedule template
        parameters_dict: Dictionary of solve parameters

    Returns:
        Dictionary with solve results
    """
    logger.info(f"Starting schedule solve for template {template_id}")

    try:
        # Parse inputs
        template_uuid = UUID(template_id)
        parameters = ScheduleSolveParameters(**parameters_dict)

        # Create solver and orchestrator
        solver = ScheduleSolver()
        orchestrator = SolveOrchestrator()

        # Run solve
        result = orchestrator.solve(solver, template_uuid, parameters.model_dump())

        # Convert result to serializable format
        response = {
            "id": str(result.id),
            "status": result.status,
            "best_fitness": result.best_fitness,
            "generations": result.generations,
            "elapsed_time": result.elapsed_time,
            "metrics": result.metrics,
        }

        # Include best genome if available
        if result.best_genome:
            genome_dto = ScheduleGenomeDTO.from_domain(result.best_genome)
            response["best_genome"] = genome_dto.model_dump()

        logger.info(
            f"Schedule solve completed for template {template_id}: "
            f"fitness={result.best_fitness:.3f}, generations={result.generations}"
        )

        return response

    except Exception as e:
        logger.error(
            f"Schedule solve failed for template {template_id}: {str(e)}", exc_info=True
        )
        return {
            "status": "failed",
            "error_message": str(e),
            "template_id": template_id,
        }


@shared_task
def debug_schedule_solve_task(template_id: str) -> dict:
    """
    Debug task for quick testing with small parameters.
    """
    logger.info(f"Starting debug schedule solve for template {template_id}")

    # Use debug parameters (very small for quick testing)
    debug_parameters = {
        "population_size": 5,
        "max_generations": 10,
        "mutation_rate": 0.2,
        "selection_top_n": 3,
        "elite_size": 1,
    }

    return schedule_solve_task(template_id, debug_parameters)
