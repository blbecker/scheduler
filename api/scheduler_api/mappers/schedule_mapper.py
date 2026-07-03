# scheduler_api/mappers/schedule_mapper.py
from scheduler_api.db.models.schedules.schedule import Schedule
from scheduler_api.schemas.schedule_crud import (
    ScheduleCreate,
    ScheduleResponse,
    ScheduleUpdate,
)


def to_response(model: Schedule) -> ScheduleResponse:
    return ScheduleResponse(
        id=model.id,
        schedule_template_id=model.schedule_template_id,
        name=model.name,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def from_create(dto: ScheduleCreate) -> Schedule:
    return Schedule(**dto.model_dump())


def apply_update(model: Schedule, dto: ScheduleUpdate) -> Schedule:
    data = dto.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(model, k, v)
    return model
