# scheduler_api/mappers/shift_template_mapper.py
from scheduler_api.db.models.templates.shift_template import ShiftTemplateModel
from scheduler_api.schemas.shift_template import (
    ShiftTemplate,
    ShiftTemplateResponse,
    ShiftTemplateUpdate,
)


def to_response(model: ShiftTemplateModel) -> ShiftTemplateResponse:
    return ShiftTemplateResponse(
        id=model.id,
        schedule_template_id=model.schedule_template_id,
        name=model.name,
        start_time=model.start_time,
        end_time=model.end_time,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def from_create(dto: ShiftTemplate) -> ShiftTemplateModel:
    return ShiftTemplate(**dto.model_dump())


def apply_update(model: ShiftTemplateModel, dto: ShiftTemplateUpdate) -> ShiftTemplate:
    data = dto.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(model, k, v)
    return model
