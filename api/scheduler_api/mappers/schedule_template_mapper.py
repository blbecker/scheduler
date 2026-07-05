# scheduler_api/mappers/schedule_template_mapper.py
from scheduler_api.db.models.templates.schedule_template import ScheduleTemplateModel
from scheduler_api.schemas.schedule_template import (
    ScheduleTemplate,
    ScheduleTemplateResponse,
    ScheduleTemplateUpdate,
)


def to_response(model: ScheduleTemplateModel) -> ScheduleTemplateResponse:
    return ScheduleTemplateResponse(
        id=model.id,
        name=model.name,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def from_create(dto: ScheduleTemplate) -> ScheduleTemplateModel:
    return ScheduleTemplateModel(**dto.model_dump())


def apply_update(
    model: ScheduleTemplateModel, dto: ScheduleTemplateUpdate
) -> ScheduleTemplateModel:
    data = dto.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(model, k, v)
    return model
