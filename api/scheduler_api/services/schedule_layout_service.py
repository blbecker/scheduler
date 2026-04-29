from typing import List, Optional
from uuid import UUID
from scheduler_api.repositories.schedule_layout_repository import (
    ScheduleLayoutRepository,
)
from scheduler_api.mappers.schedule_layout_mapper import (
    to_response,
    from_create,
)
from scheduler_api.schemas.schedule_layout import (
    ScheduleLayoutCreate,
    ScheduleLayoutUpdate,
    ScheduleLayoutResponse,
    ScheduleLayoutGenerateResponse,
)
from scheduler_api.tasks.ga_tasks import generate_schedule_from_layout
from scheduler_api.mappers.ga_mapper import schedule_layout_to_dto
from scheduler_api.domain.schedule_layout import ScheduleLayout as DomainScheduleLayout


class ScheduleLayoutService:
    def __init__(self, repo: ScheduleLayoutRepository):
        self.repo = repo

    def list_layouts(self) -> List[ScheduleLayoutResponse]:
        layouts = self.repo.get_all()
        return [to_response(layout) for layout in layouts]

    def get_layout(self, layout_id: UUID) -> Optional[ScheduleLayoutResponse]:
        layout = self.repo.get_by_id(layout_id)
        return to_response(layout) if layout else None

    def create_layout(self, dto: ScheduleLayoutCreate) -> ScheduleLayoutResponse:
        model = from_create(dto)
        saved = self.repo.create(model)
        return to_response(saved)

    def update_layout(
        self, layout_id: UUID, dto: ScheduleLayoutUpdate
    ) -> Optional[ScheduleLayoutResponse]:
        from scheduler_api.db.models import (
            ScheduleLayoutUpdate as DBScheduleLayoutUpdate,
        )

        existing = self.repo.get_by_id(layout_id)
        if not existing:
            return None

        # Convert Pydantic update DTO to SQLModel update model
        update_data = dto.model_dump(exclude_unset=True)
        db_update = DBScheduleLayoutUpdate(**update_data)

        saved = self.repo.update(layout_id, db_update)
        return to_response(saved) if saved else None

    def delete_layout(self, layout_id: UUID) -> bool:
        return self.repo.delete(layout_id)

    def generate_schedule(self, layout_id: UUID) -> ScheduleLayoutGenerateResponse:
        layout = self.repo.get_by_id(layout_id)
        if not layout:
            raise ValueError(f"Schedule layout with ID {layout_id} not found")

        # Convert database model to domain model
        domain_layout = DomainScheduleLayout(
            id=layout.id,
            name=layout.name,
            date_range_start=layout.date_range_start,
            date_range_end=layout.date_range_end,
            shift_templates=layout.shift_templates,
            worker_ids=layout.worker_ids,
            constraints=layout.constraints,
            created_at=layout.created_at,
        )

        # Convert domain model to DTO
        layout_dto = schedule_layout_to_dto(domain_layout)

        # Trigger the Celery task
        task_result = generate_schedule_from_layout.delay(layout_dto.model_dump())

        return ScheduleLayoutGenerateResponse(
            layout_id=layout_id,
            task_id=task_result.id,
            status="queued",
            message=f"Schedule generation task queued with ID: {task_result.id}",
        )
