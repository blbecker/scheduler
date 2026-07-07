# scheduler_api/mappers/shift_mapper.py
from scheduler_api.db.models.schedules.shift import ShiftModel
from scheduler_api.schemas.shift import ShiftCreate, ShiftResponse, ShiftUpdate


def to_response(model: ShiftModel) -> ShiftResponse:
    return ShiftResponse(
        id=model.id,
        schedule_id=model.schedule_id,
        shift_template_id=model.shift_template_id,
        name=model.name,
        start_time=model.start_time,
        end_time=model.end_time,
        created_at=model.created_at,
        updated_at=model.updated_at)


def from_create(dto: ShiftCreate) -> ShiftModel:
    return ShiftModel(**dto.model_dump())


def apply_update(model: ShiftModel, dto: ShiftUpdate) -> ShiftModel:
    data = dto.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(model, k, v)
    return model
