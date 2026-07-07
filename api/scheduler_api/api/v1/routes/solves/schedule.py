"""API router for solve framework."""

from fastapi import APIRouter, HTTPException, status
from uuid import UUID
from datetime import datetime
from celery.result import AsyncResult

from scheduler_api.schemas.solve import (
    ScheduleSolveParameters,
    ScheduleSolveRequest,
    ScheduleSolveCreateResponse,
    ScheduleSolveStatus,
    ScheduleSolveResult,
)
from scheduler_api.tasks.solve_tasks import schedule_solve_task
from scheduler_api.celery import app

router = APIRouter(prefix="/solves", tags=["schedule-solves"])


@router.post(
    "/schedule",
    response_model=ScheduleSolveCreateResponse,
    operation_id="create_schedule_solve",
    status_code=status.HTTP_202_ACCEPTED,
)
def create_schedule_solve(request: ScheduleSolveRequest):
    """
    Create a new schedule solve.

    This starts a background task that runs the genetic algorithm
    to optimize worker-shift assignments for the given template.
    """
    # Start the Celery task
    task = schedule_solve_task.delay(
        str(request.template_id), request.parameters.model_dump()
    )

    return ScheduleSolveCreateResponse(
        id=UUID(task.id),
        status="pending",
        template_id=request.template_id,
        parameters=request.parameters,
    )


@router.get(
    "/schedule/{solve_id}",
    response_model=ScheduleSolveStatus,
    operation_id="get_schedule_solve_status",
)
def get_schedule_solve_status(solve_id: UUID):
    """
    Get the status of a schedule solve.

    Returns current progress, generation count, best fitness, etc.
    """
    result = AsyncResult(str(solve_id), app=app)

    # Celery task states
    celery_state_to_status = {
        "PENDING": "pending",
        "STARTED": "running",
        "SUCCESS": "completed",
        "FAILURE": "failed",
        "RETRY": "running",
        "REVOKED": "failed",
    }

    status_str = celery_state_to_status.get(result.state, "unknown")

    # Build base response
    response = ScheduleSolveStatus(
        id=solve_id,
        status=status_str,
        template_id=UUID(),  # TODO: Store template_id with task
        parameters=ScheduleSolveParameters(),  # TODO: Store parameters
        created_at=datetime.now(),  # TODO: Get actual creation time
    )

    # Add result data if task completed successfully
    if result.ready() and result.successful():
        result_data = result.result
        if isinstance(result_data, dict):
            response.result = result_data
            response.best_fitness = result_data.get("best_fitness")
            response.current_generation = result_data.get("generations")
            response.progress = 1.0  # Completed

    # Add error if task failed
    elif result.failed():
        response.status = "failed"
        try:
            result.get(propagate=False)  # Get result without raising
        except Exception as e:
            response.error_message = str(e)

    # Estimate progress if running
    elif result.state == "STARTED":
        # TODO: Implement progress tracking
        # For now, we can estimate or return None
        response.progress = None

    return response


@router.get(
    "/schedule/{solve_id}/result",
    response_model=ScheduleSolveResult,
    operation_id="get_schedule_solve_result",
)
def get_schedule_solve_result(solve_id: UUID):
    """
    Get the final result of a completed schedule solve.

    Only returns results for completed solves.
    """
    result = AsyncResult(str(solve_id), app=app)

    if not result.ready():
        raise HTTPException(
            status_code=status.HTTP_202_ACCEPTED, detail="Solve is still running"
        )

    if result.failed():
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Solve failed: {getattr(result, 'traceback', 'Unknown error')}",
        )

    result_data = result.result
    if not isinstance(result_data, dict):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Invalid result format",
        )

    return ScheduleSolveResult(
        id=solve_id,
        status="completed",
        best_genome=result_data.get("best_genome"),
        best_fitness=result_data.get("best_fitness", 0.0),
        generations=result_data.get("generations", 0),
        elapsed_time=result_data.get("elapsed_time", 0.0),
        metrics=result_data.get("metrics", {}),
        created_at=datetime.now(),  # TODO: Get actual creation time
    )
