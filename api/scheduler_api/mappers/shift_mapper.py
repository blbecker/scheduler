# scheduler_api/mappers/shift_mapper.py
from scheduler_api.db.models import Shift
from scheduler_api.schemas.shift import ShiftCreate, ShiftResponse, ShiftUpdate


def to_response(model: Shift) -> ShiftResponse:
    return ShiftResponse(
        id=model.id,
        start_time=model.start_time,
        end_time=model.end_time,
        location=model.location,
        notes=model.notes,
    )


def from_create(dto: ShiftCreate) -> Shift:
    return Shift(**dto.model_dump())


def apply_update(model: Shift, dto: ShiftUpdate) -> Shift:
    data = dto.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(model, k, v)
    return model
