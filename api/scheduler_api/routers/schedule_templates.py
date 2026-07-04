# scheduler_api/routers/schedule_templates.py
from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID

from scheduler_api.services.schedule_template_service import ScheduleTemplateService
from scheduler_api.schemas.schedule_template import (
    ScheduleTemplate,
    ScheduleTemplateUpdate,
    ScheduleTemplateResponse,
)
from scheduler_api.uow.unit_of_work import UnitOfWork

from .deps import get_unit_of_work_provider

router = APIRouter(prefix="/schedule-templates", tags=["schedule-templates"])


@router.get("/", response_model=list[ScheduleTemplateResponse])
def list_schedule_templates(
    uow: UnitOfWork = Depends(get_unit_of_work_provider()),
):
    service = ScheduleTemplateService(uow)
    return service.list_schedule_templates()


@router.get("/{schedule_template_id}", response_model=ScheduleTemplateResponse)
def get_schedule_template(
    schedule_template_id: UUID,
    uow: UnitOfWork = Depends(get_unit_of_work_provider()),
):
    service = ScheduleTemplateService(uow)
    try:
        return service.get_schedule_template(schedule_template_id)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=404, detail="Schedule template not found")


@router.post("/", response_model=ScheduleTemplateResponse, status_code=201)
def create_schedule_template(
    schedule_template: ScheduleTemplate,
    uow: UnitOfWork = Depends(get_unit_of_work_provider()),
):
    service = ScheduleTemplateService(uow)
    return service.create_schedule_template(schedule_template)


@router.put("/{schedule_template_id}", response_model=ScheduleTemplateResponse)
def update_schedule_template(
    schedule_template_id: UUID,
    schedule_template: ScheduleTemplateUpdate,
    uow: UnitOfWork = Depends(get_unit_of_work_provider()),
):
    service = ScheduleTemplateService(uow)
    try:
        return service.update_schedule_template(schedule_template_id, schedule_template)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=404, detail="Schedule template not found")


@router.delete("/{schedule_template_id}", status_code=204)
def delete_schedule_template(
    schedule_template_id: UUID,
    uow: UnitOfWork = Depends(get_unit_of_work_provider()),
):
    service = ScheduleTemplateService(uow)
    try:
        service.delete_schedule_template(schedule_template_id)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=404, detail="Schedule template not found")
    return None
