# scheduler_api/mappers/schedule_mapper.py
from scheduler_api.db.models.schedules.schedule import ScheduleModel
from scheduler_api.schemas.schedule_crud import (
    ScheduleCreate,
    ScheduleResponse,
    ScheduleUpdate)


def to_response(model: ScheduleModel) -> ScheduleResponse:
    return ScheduleResponse(
        id=model.id,
        schedule_template_id=model.schedule_template_id,
        name=model.name,
        created_at=model.created_at,
        updated_at=model.updated_at)


def from_create(dto: ScheduleCreate) -> ScheduleModel:
    return ScheduleModel(**dto.model_dump())


def apply_update(model: ScheduleModel, dto: ScheduleUpdate) -> ScheduleModel:
    data = dto.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(model, k, v)
    return model
