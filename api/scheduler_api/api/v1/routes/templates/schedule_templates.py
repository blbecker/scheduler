# scheduler_api/routers/schedule_templates.py
from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID
from sqlmodel import Session

from scheduler_api.services.schedule_template_service import ScheduleTemplateService
from scheduler_api.repositories.schedule_template_repository import ScheduleTemplateRepository
from scheduler_api.schemas.schedule_template import (
    ScheduleTemplate,
    ScheduleTemplateUpdate,
    ScheduleTemplateResponse,
)

from ..deps import get_db_session

router = APIRouter(prefix="/schedule-templates", tags=["schedule-templates"])


@router.get(
    "/",
    response_model=list[ScheduleTemplateResponse],
    operation_id="list_schedule_templates",
)
def list_schedule_templates(
    session: Session = Depends(get_db_session),
):
    repo = ScheduleTemplateRepository(session)
    service = ScheduleTemplateService(repo)
    return service.list_schedule_templates()


@router.get(
    "/{schedule_template_id}",
    response_model=ScheduleTemplateResponse,
    operation_id="get_schedule_template",
)
def get_schedule_template(
    schedule_template_id: UUID,
    session: Session = Depends(get_db_session),
):
    repo = ScheduleTemplateRepository(session)
    service = ScheduleTemplateService(repo)
    try:
        return service.get_schedule_template(schedule_template_id)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=404, detail="Schedule template not found")


@router.post(
    "/",
    response_model=ScheduleTemplateResponse,
    operation_id="create_schedule_template",
    status_code=201,
)
def create_schedule_template(
    schedule_template: ScheduleTemplate,
    session: Session = Depends(get_db_session),
):
    repo = ScheduleTemplateRepository(session)
    service = ScheduleTemplateService(repo)
    return service.create_schedule_template(schedule_template)


@router.put(
    "/{schedule_template_id}",
    response_model=ScheduleTemplateResponse,
    operation_id="update_schedule_template",
)
def update_schedule_template(
    schedule_template_id: UUID,
    schedule_template: ScheduleTemplateUpdate,
    session: Session = Depends(get_db_session),
):
    repo = ScheduleTemplateRepository(session)
    service = ScheduleTemplateService(repo)
    try:
        return service.update_schedule_template(schedule_template_id, schedule_template)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=404, detail="Schedule template not found")


@router.delete(
    "/{schedule_template_id}", operation_id="delete_schedule_template", status_code=204
)
def delete_schedule_template(
    schedule_template_id: UUID,
    session: Session = Depends(get_db_session),
):
    repo = ScheduleTemplateRepository(session)
    service = ScheduleTemplateService(repo)
    try:
        service.delete_schedule_template(schedule_template_id)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=404, detail="Schedule template not found")
    return None
