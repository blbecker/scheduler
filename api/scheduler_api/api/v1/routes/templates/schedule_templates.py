# scheduler_api/routers/schedule_templates.py
from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID

from scheduler_api.services.schedule_template_service import ScheduleTemplateService
from scheduler_api.schemas.schedule_template import (
    ScheduleTemplateCreate,
    ScheduleTemplateUpdate,
    ScheduleTemplateResponse,
)

from ..deps import get_schedule_template_service

router = APIRouter(prefix="/schedule-templates", tags=["schedule-templates"])


@router.get(
    "/",
    response_model=list[ScheduleTemplateResponse],
    operation_id="list_schedule_templates",
)
def list_schedule_templates(
    service: ScheduleTemplateService = Depends(get_schedule_template_service),
):
    return service.list_schedule_templates()


@router.get(
    "/{schedule_template_id}",
    response_model=ScheduleTemplateResponse,
    operation_id="get_schedule_template",
)
def get_schedule_template(
    schedule_template_id: UUID,
    service: ScheduleTemplateService = Depends(get_schedule_template_service),
):
    schedule_template = service.get_schedule_template(schedule_template_id)
    if schedule_template is None:
        raise HTTPException(status_code=404, detail="Schedule template not found")
    return schedule_template


@router.post(
    "/",
    response_model=ScheduleTemplateResponse,
    operation_id="create_schedule_template",
    status_code=201,
)
def create_schedule_template(
    schedule_template: ScheduleTemplateCreate,
    service: ScheduleTemplateService = Depends(get_schedule_template_service),
):
    return service.create_schedule_template(schedule_template)


@router.put(
    "/{schedule_template_id}",
    response_model=ScheduleTemplateResponse,
    operation_id="update_schedule_template",
)
def update_schedule_template(
    schedule_template_id: UUID,
    schedule_template: ScheduleTemplateUpdate,
    service: ScheduleTemplateService = Depends(get_schedule_template_service),
):
    updated = service.update_schedule_template(schedule_template_id, schedule_template)
    if updated is None:
        raise HTTPException(status_code=404, detail="Schedule template not found")
    return updated


@router.delete(
    "/{schedule_template_id}", operation_id="delete_schedule_template", status_code=204
)
def delete_schedule_template(
    schedule_template_id: UUID,
    service: ScheduleTemplateService = Depends(get_schedule_template_service),
):
    try:
        service.delete_schedule_template(schedule_template_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Schedule template not found")
