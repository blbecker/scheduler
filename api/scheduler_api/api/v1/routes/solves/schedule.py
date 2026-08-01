"""API router for solve framework with persistence."""

from fastapi import APIRouter, HTTPException, status, Depends
from uuid import UUID
from celery.result import AsyncResult

from scheduler_api.schemas.solve import (
    ScheduleSolveParameters,
    ScheduleSolveRequest,
    ScheduleSolveCreateResponse,
    ScheduleSolveStatus,
    ScheduleSolveResult,
)
from scheduler_api.schemas.schedule_solve import (
    ScheduleSolveCreate,
    ScheduleSolveResponse,
)
from scheduler_api.tasks.celery_tasks.solve_tasks import schedule_solve_task

# Use the imported schedule_solve_task directly
# Since it's decorated with @shared_task, it should have .delay() method
from scheduler_api.celery import app
from scheduler_api.api.v1.routes.deps import get_schedule_solve_service
from scheduler_api.services.schedule_solve_service import ScheduleSolveService
from scheduler_api.db.models.enums import ScheduleSolveStatus as StatusEnum

router = APIRouter(prefix="/solves/schedule", tags=["schedule-solves"])


@router.get(
    "/", response_model=list[ScheduleSolveResponse], operation_id="list_schedule_solves"
)
def list_schedule_solves(
    service: ScheduleSolveService = Depends(get_schedule_solve_service),
):
    return service.list_schedule_solves()


@router.post(
    "/",
    response_model=ScheduleSolveCreateResponse,
    operation_id="create_schedule_solve",
    status_code=status.HTTP_202_ACCEPTED,
)
def create_schedule_solve(
    request: ScheduleSolveRequest,
    service: ScheduleSolveService = Depends(get_schedule_solve_service),
):
    """
    Create a new schedule solve with persistence.

    This creates a ScheduleSolveModel record and starts a background task
    that runs the genetic algorithm to optimize worker-shift assignments.
    """
    # Create ScheduleSolveModel record
    solve_create = ScheduleSolveCreate(
        schedule_template_id=request.template_id,
        parameters=request.parameters.model_dump(),
    )

    schedule_solve = service.create_schedule_solve(solve_create)

    # Start the Celery task with the schedule solve ID
    celery_task = schedule_solve_task.apply_async(
        args=[str(schedule_solve.id), "default"]
    )
    task_id = celery_task.id

    # Update the schedule solve with the celery task ID
    service.update_schedule_solve_status(
        schedule_solve.id, StatusEnum.queued, celery_task_id=task_id
    )

    return ScheduleSolveCreateResponse(
        id=schedule_solve.id,
        status="queued",
        template_id=request.template_id,
        parameters=request.parameters,
        schedule_solve_id=schedule_solve.id,
    )


@router.get(
    "/{solve_id}",
    response_model=ScheduleSolveStatus,
    operation_id="get_schedule_solve_status",
)
def get_schedule_solve_status(
    solve_id: UUID,
    service: ScheduleSolveService = Depends(get_schedule_solve_service),
):
    """
    Get the status of a schedule solve from persistence.

    Returns current progress, generation count, best fitness, etc.
    """
    # First try to get from database
    schedule_solve = service.get_schedule_solve(solve_id)
    if not schedule_solve:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Schedule solve {solve_id} not found",
        )

    # Build response from persisted data
    response = ScheduleSolveStatus(
        id=solve_id,
        status=schedule_solve.status,
        template_id=schedule_solve.schedule_template_id,
        parameters=ScheduleSolveParameters(**schedule_solve.parameters),
        created_at=schedule_solve.created_at,
        best_fitness=schedule_solve.best_fitness,
        current_generation=schedule_solve.current_generation,
        progress=schedule_solve.progress,
        error_message=schedule_solve.error_details,
    )

    # If solve has a celery task ID, we can check Celery for additional info
    if schedule_solve.celery_task_id:
        celery_result = AsyncResult(schedule_solve.celery_task_id, app=app)

        # If task is still running and we don't have current generation data,
        # we can get it from Celery's result metadata
        if celery_result.state == "STARTED" and celery_result.info:
            info = celery_result.info
            if isinstance(info, dict):
                response.current_generation = (
                    info.get("current_generation") or response.current_generation
                )
                response.best_fitness = (
                    info.get("best_fitness") or response.best_fitness
                )
                response.progress = info.get("progress") or response.progress

    return response


@router.get(
    "/{solve_id}/result",
    response_model=ScheduleSolveResult,
    operation_id="get_schedule_solve_result",
)
def get_schedule_solve_result(
    solve_id: UUID,
    service: ScheduleSolveService = Depends(get_schedule_solve_service),
):
    """
    Get the final result of a completed schedule solve.

    Only returns results for completed solves.
    """
    schedule_solve = service.get_schedule_solve(solve_id)
    if not schedule_solve:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Schedule solve {solve_id} not found",
        )

    if schedule_solve.status != "completed":
        raise HTTPException(
            status_code=status.HTTP_202_ACCEPTED,
            detail=f"Solve is {schedule_solve.status}, not completed",
        )

    # Calculate elapsed time
    elapsed_time = 0.0
    if schedule_solve.started_at and schedule_solve.finished_at:
        elapsed_time = (
            schedule_solve.finished_at - schedule_solve.started_at
        ).total_seconds()

    return ScheduleSolveResult(
        id=solve_id,
        status=schedule_solve.status,
        best_fitness=schedule_solve.best_fitness or 0.0,
        generations=schedule_solve.current_generation or 0,
        elapsed_time=elapsed_time,
        metrics={
            "population_size": schedule_solve.parameters.get("population_size", 0),
            "max_generations": schedule_solve.parameters.get("max_generations", 0),
            "schedule_solve_id": str(schedule_solve.id),
        },
        created_at=schedule_solve.created_at,
    )
