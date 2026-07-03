# scheduler_api/mappers/schedule_template_mapper.py
from scheduler_api.db.models.templates.schedule_template import ScheduleTemplate
from scheduler_api.schemas.schedule_template import (
    ScheduleTemplateCreate,
    ScheduleTemplateResponse,
    ScheduleTemplateUpdate,
)


def to_response(model: ScheduleTemplate) -> ScheduleTemplateResponse:
    return ScheduleTemplateResponse(
        id=model.id,
        name=model.name,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def from_create(dto: ScheduleTemplateCreate) -> ScheduleTemplate:
    return ScheduleTemplate(**dto.model_dump())


def apply_update(
    model: ScheduleTemplate, dto: ScheduleTemplateUpdate
) -> ScheduleTemplate:
    data = dto.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(model, k, v)
    return model
