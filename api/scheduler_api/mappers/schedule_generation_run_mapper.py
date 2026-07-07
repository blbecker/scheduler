# scheduler_api/mappers/schedule_generation_run_mapper.py
from scheduler_api.db.models.runs.schedule_generation_run import (
    ScheduleGenerationRunModel)
from scheduler_api.db.models.enums import ScheduleGenerationStatus
from scheduler_api.schemas.schedule_generation_run import (
    ScheduleGenerationRunCreate,
    ScheduleGenerationRunResponse,
    ScheduleGenerationRunUpdate)


def to_response(model: ScheduleGenerationRunModel) -> ScheduleGenerationRunResponse:
    return ScheduleGenerationRunResponse(
        id=model.id,
        schedule_template_id=model.schedule_template_id,
        schedule_id=model.schedule_id,
        status=model.status,
        started_at=model.started_at,
        finished_at=model.finished_at,
        parameters=model.parameters,
        created_at=model.created_at,
        updated_at=model.updated_at)


def from_create(dto: ScheduleGenerationRunCreate) -> ScheduleGenerationRunModel:
    return ScheduleGenerationRunModel(
        schedule_template_id=dto.schedule_template_id,
        parameters=dto.parameters,
        status=ScheduleGenerationStatus.pending,
        started_at=None,
        finished_at=None)


def apply_update(
    model: ScheduleGenerationRunModel, dto: ScheduleGenerationRunUpdate
) -> ScheduleGenerationRunModel:
    data = dto.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(model, k, v)
    return model
