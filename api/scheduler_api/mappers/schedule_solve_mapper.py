# scheduler_api/mappers/schedule_solve_mapper.py
from scheduler_api.db.models.solves.schedule_solve import ScheduleSolveModel
from scheduler_api.db.models.enums import ScheduleSolveStatus
from scheduler_api.schemas.schedule_solve import (
    ScheduleSolveCreate,
    ScheduleSolveResponse,
    ScheduleSolveUpdate,
)


def to_response(model: ScheduleSolveModel) -> ScheduleSolveResponse:
    return ScheduleSolveResponse(
        id=model.id,
        schedule_template_id=model.schedule_template_id,
        schedule_id=model.schedule_id,
        status=model.status,
        started_at=model.started_at,
        finished_at=model.finished_at,
        parameters=model.parameters,
        celery_task_id=model.celery_task_id,
        current_generation=model.current_generation,
        best_fitness=model.best_fitness,
        progress=model.progress,
        error_details=model.error_details,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def from_create(dto: ScheduleSolveCreate) -> ScheduleSolveModel:
    return ScheduleSolveModel(
        schedule_template_id=dto.schedule_template_id,
        parameters=dto.parameters,
        status=ScheduleSolveStatus.pending,
        started_at=None,
        finished_at=None,
        celery_task_id=None,
        current_generation=None,
        best_fitness=None,
        progress=0.0,
        error_details=None,
    )


def apply_update(
    model: ScheduleSolveModel, dto: ScheduleSolveUpdate
) -> ScheduleSolveModel:
    data = dto.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(model, k, v)
    return model
