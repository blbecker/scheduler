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
    LEGACY: Celery task for schedule solve execution.

    This is kept for backward compatibility during transition.
    New code should use schedule_solve_pseudo_task().

    Args:
        template_id: UUID string of schedule template
        parameters_dict: Dictionary of solve parameters

    Returns:
        Dictionary with solve results
    """
    logger.warning(f"Using legacy schedule_solve_task for template {template_id}")
    logger.warning("This will be deprecated. Use schedule_solve_pseudo_task instead.")

    # For now, call the new pseudo-task with a dummy solve ID
    # In production, this would need to create a ScheduleSolve record first
    from uuid import uuid4

    dummy_solve_id = str(uuid4())
    return schedule_solve_pseudo_task(dummy_solve_id)


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


@shared_task(bind=True)
def schedule_solve_pseudo_task(self, schedule_solve_id: str) -> dict:
    """
    Pseudo-implementation of schedule solve task.

    Simulates genetic algorithm execution with sleeps and logging.
    Updates ScheduleSolveModel status throughout.

    Args:
        schedule_solve_id: UUID string of ScheduleSolveModel

    Returns:
        Dictionary with solve results
    """
    from uuid import UUID
    from datetime import datetime, timezone
    from scheduler_api.tasks.session import get_task_session
    from scheduler_api.services.schedule_solve_service import ScheduleSolveService
    from scheduler_api.db.models.enums import ScheduleSolveStatus

    logger.info(f"Starting pseudo-solve for schedule solve {schedule_solve_id}")

    # Initialize variables
    session = None
    service = None
    best_fitness = 0.0

    try:
        # Create session for this task
        session = get_task_session()

        # Create service with session
        service = ScheduleSolveService(session)

        # Load schedule solve
        solve_response = service.get_schedule_solve(UUID(schedule_solve_id))
        if not solve_response:
            logger.error(f"Schedule solve {schedule_solve_id} not found")
            return {"status": "failed", "error": "Schedule solve not found"}

        # Need to get the model to access parameters
        solve_model = service.repo.get_by_id(UUID(schedule_solve_id))
        if not solve_model:
            logger.error(f"Schedule solve model {schedule_solve_id} not found")
            return {"status": "failed", "error": "Schedule solve model not found"}

        # Update status to running with celery task ID
        service.update_schedule_solve_status(
            UUID(schedule_solve_id),
            ScheduleSolveStatus.running,
            celery_task_id=self.request.id,
        )

        # Extract parameters
        from scheduler_api.schemas.solve import ScheduleSolveParameters

        parameters = ScheduleSolveParameters(**solve_model.parameters)

        logger.info(
            f"Starting pseudo-solve with population={parameters.population_size}, "
            f"generations={parameters.max_generations}"
        )

        # Pseudo-evolution loop
        last_progress_update = 0
        for generation in range(1, parameters.max_generations + 1):
            # Calculate mock progress and fitness
            progress = generation / parameters.max_generations
            best_fitness = 0.1 + progress * 0.8  # Linear improvement from 0.1 to 0.9

            # Update progress periodically: every 5 generations OR every 10% progress
            should_update = (
                generation % 5 == 0
                or int(progress * 10) > int(last_progress_update * 10)
                or generation == parameters.max_generations
            )

            if should_update:
                service.update_schedule_solve_progress(
                    UUID(schedule_solve_id),
                    current_generation=generation,
                    best_fitness=best_fitness,
                    progress=progress,
                )
                last_progress_update = progress

            logger.info(
                f"Generation {generation}/{parameters.max_generations}: "
                f"fitness={best_fitness:.3f}, progress={progress:.1%}"
            )

            # Sleep to simulate computation (1 second per generation)
            time.sleep(1)

        # Create mock schedule
        schedule = service.create_schedule_from_solve(
            UUID(schedule_solve_id), name=f"Schedule from Solve {schedule_solve_id[:8]}"
        )

        # Mark solve as completed
        service.complete_schedule_solve(
            UUID(schedule_solve_id), schedule_id=schedule.id
        )

        # Calculate elapsed time
        solve_model = service.repo.get_by_id(UUID(schedule_solve_id))
        elapsed_time = 0.0
        if solve_model and solve_model.started_at and solve_model.finished_at:
            elapsed_time = (
                solve_model.finished_at - solve_model.started_at
            ).total_seconds()

        logger.info(
            f"Pseudo-solve completed for {schedule_solve_id}: "
            f"created schedule {schedule.id}, elapsed={elapsed_time:.1f}s"
        )

        return {
            "status": "completed",
            "schedule_solve_id": schedule_solve_id,
            "schedule_id": str(schedule.id),
            "best_fitness": best_fitness,
            "generations": parameters.max_generations,
            "elapsed_time": elapsed_time,
            "metrics": {
                "simulation": True,
                "population_size": parameters.population_size,
                "max_generations": parameters.max_generations,
            },
        }

    except Exception as e:
        logger.error(
            f"Pseudo-solve failed for {schedule_solve_id}: {str(e)}", exc_info=True
        )

        # Record failure if service is available
        if service:
            try:
                service.fail_schedule_solve(
                    UUID(schedule_solve_id), error_details=str(e)
                )
            except Exception as inner_e:
                logger.error(
                    f"Failed to record solve failure: {str(inner_e)}", exc_info=True
                )

        raise  # Re-raise for Celery error handling

    finally:
        # Always close the session
        if session:
            session.close()
