# scheduler_api/mappers/shift_template_mapper.py
from scheduler_api.db.models.templates.shift_template import ShiftTemplateModel
from scheduler_api.schemas.shift_template import (
    ShiftTemplateCreate,
    ShiftTemplateResponse,
    ShiftTemplateUpdate,
)


def to_response(model: ShiftTemplateModel) -> ShiftTemplateResponse:
    # Extract skill IDs from the hydrated relationship
    skill_ids = [skill.id for skill in model.skills] if model.skills else []

    return ShiftTemplateResponse(
        id=model.id,
        schedule_template_id=model.schedule_template_id,
        name=model.name,
        start_time=model.start_time,
        end_time=model.end_time,
        skill_ids=skill_ids,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def from_create(dto: ShiftTemplateCreate) -> ShiftTemplateModel:
    # Create model without skills - skills will be handled by service
    data = dto.model_dump(exclude={"skill_ids"})
    return ShiftTemplateModel(**data)


def apply_update(
    model: ShiftTemplateModel, dto: ShiftTemplateUpdate
) -> ShiftTemplateModel:
    # Update only basic fields, skills will be handled by service
    data = dto.model_dump(exclude_unset=True, exclude={"skill_ids"})
    for k, v in data.items():
        setattr(model, k, v)
    return model
