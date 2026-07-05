# scheduler_api/routers/shift_templates.py
from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID
from sqlmodel import Session

from scheduler_api.services.shift_template_service import ShiftTemplateService
from scheduler_api.repositories.shift_template_repository import ShiftTemplateRepository
from scheduler_api.schemas.shift_template import (
    ShiftTemplate,
    ShiftTemplateUpdate,
    ShiftTemplateResponse,
)

from ..deps import get_db_session

router = APIRouter(prefix="/shift-templates", tags=["shift-templates"])


@router.get(
    "/", response_model=list[ShiftTemplateResponse], operation_id="list_shift_templates"
)
def list_shift_templates(
    session: Session = Depends(get_db_session),
):
    repo = ShiftTemplateRepository(session)
    service = ShiftTemplateService(repo)
    return service.list_shift_templates()


@router.get(
    "/{shift_template_id}",
    response_model=ShiftTemplateResponse,
    operation_id="get_shift_template",
)
def get_shift_template(
    shift_template_id: UUID,
    session: Session = Depends(get_db_session),
):
    repo = ShiftTemplateRepository(session)
    service = ShiftTemplateService(repo)
    try:
        return service.get_shift_template(shift_template_id)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=404, detail="Shift template not found")


@router.post(
    "/",
    response_model=ShiftTemplateResponse,
    operation_id="create_shift_template",
    status_code=201,
)
def create_shift_template(
    shift_template: ShiftTemplate,
    session: Session = Depends(get_db_session),
):
    repo = ShiftTemplateRepository(session)
    service = ShiftTemplateService(repo)
    return service.create_shift_template(shift_template)


@router.put(
    "/{shift_template_id}",
    response_model=ShiftTemplateResponse,
    operation_id="update_shift_template",
)
def update_shift_template(
    shift_template_id: UUID,
    shift_template: ShiftTemplateUpdate,
    session: Session = Depends(get_db_session),
):
    repo = ShiftTemplateRepository(session)
    service = ShiftTemplateService(repo)
    try:
        return service.update_shift_template(shift_template_id, shift_template)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=404, detail="Shift template not found")


@router.delete(
    "/{shift_template_id}", operation_id="delete_shift_template", status_code=204
)
def delete_shift_template(
    shift_template_id: UUID,
    session: Session = Depends(get_db_session),
):
    repo = ShiftTemplateRepository(session)
    service = ShiftTemplateService(repo)
    try:
        service.delete_shift_template(shift_template_id)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=404, detail="Shift template not found")
    return None
