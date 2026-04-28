from scheduler_api.db.models import ScheduleLayout
from scheduler_api.schemas.schedule_layout import (
    ScheduleLayoutCreate,
    ScheduleLayoutUpdate,
    ScheduleLayoutResponse,
)


def to_response(model: ScheduleLayout) -> ScheduleLayoutResponse:
    return ScheduleLayoutResponse(
        id=model.id,
        name=model.name,
        description=model.description,
        date_range_start=model.date_range_start,
        date_range_end=model.date_range_end,
        worker_ids=model.worker_ids,
        shift_templates=model.shift_templates,
        constraints=model.constraints,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def from_create(dto: ScheduleLayoutCreate) -> ScheduleLayout:
    return ScheduleLayout(
        name=dto.name,
        description=dto.description,
        date_range_start=dto.date_range_start,
        date_range_end=dto.date_range_end,
        worker_ids=dto.worker_ids,
        shift_templates=dto.shift_templates,
        constraints=dto.constraints,
    )


def apply_update(model: ScheduleLayout, dto: ScheduleLayoutUpdate) -> ScheduleLayout:
    data = dto.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(model, key, value)
    return model
