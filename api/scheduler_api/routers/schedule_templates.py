from uuid import UUID
from typing import List
from fastapi import APIRouter
from scheduler_api.schemas.schedule_template import (
    ScheduleTemplateCreateDTO,
    ScheduleTemplateUpdateDTO,
    ScheduleTemplateDTO,
)

router = APIRouter(prefix="/schedule-templates", tags=["schedule-templates"])


@router.post("", response_model=ScheduleTemplateDTO, status_code=201)
async def create_schedule_template(
    payload: ScheduleTemplateCreateDTO,
) -> ScheduleTemplateDTO:
    # TODO: persist template via service layer
    raise NotImplementedError


@router.get("", response_model=List[ScheduleTemplateDTO])
async def list_schedule_templates() -> List[ScheduleTemplateDTO]:
    # TODO: list all templates
    raise NotImplementedError


@router.get("/{template_id}", response_model=ScheduleTemplateDTO)
async def get_schedule_template(template_id: UUID) -> ScheduleTemplateDTO:
    # TODO: fetch template
    raise NotImplementedError


@router.put("/{template_id}", response_model=ScheduleTemplateDTO)
async def update_schedule_template(
    template_id: UUID,
    payload: ScheduleTemplateUpdateDTO,
) -> ScheduleTemplateDTO:
    # TODO: update template
    raise NotImplementedError


@router.patch("/{template_id}", response_model=ScheduleTemplateDTO)
async def patch_schedule_template(
    template_id: UUID,
    payload: ScheduleTemplateUpdateDTO,
) -> ScheduleTemplateDTO:
    # TODO: patch template
    raise NotImplementedError


@router.delete("/{template_id}", status_code=204)
async def delete_schedule_template(template_id: UUID):
    # TODO: delete template
    raise NotImplementedError
