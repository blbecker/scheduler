# scheduler_api/routers/shift_templates.py
from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID

from scheduler_api.services.shift_template_service import ShiftTemplateService
from scheduler_api.schemas.shift_template import (
    ShiftTemplateCreate,
    ShiftTemplateUpdate,
    ShiftTemplateResponse,
)

from ..deps import get_shift_template_service

router = APIRouter(prefix="/shift-templates", tags=["shift-templates"])


@router.get(
    "/", response_model=list[ShiftTemplateResponse], operation_id="list_shift_templates"
)
def list_shift_templates(
    service: ShiftTemplateService = Depends(get_shift_template_service),
):
    return service.list_shift_templates()


@router.get(
    "/{shift_template_id}",
    response_model=ShiftTemplateResponse,
    operation_id="get_shift_template",
)
def get_shift_template(
    shift_template_id: UUID,
    service: ShiftTemplateService = Depends(get_shift_template_service),
):
    shift_template = service.get_shift_template(shift_template_id)
    if shift_template is None:
        raise HTTPException(status_code=404, detail="Shift template not found")
    return shift_template


@router.post(
    "/",
    response_model=ShiftTemplateResponse,
    operation_id="create_shift_template",
    status_code=201,
)
def create_shift_template(
    shift_template: ShiftTemplateCreate,
    service: ShiftTemplateService = Depends(get_shift_template_service),
):
    return service.create_shift_template(shift_template)


@router.put(
    "/{shift_template_id}",
    response_model=ShiftTemplateResponse,
    operation_id="update_shift_template",
)
def update_shift_template(
    shift_template_id: UUID,
    shift_template: ShiftTemplateUpdate,
    service: ShiftTemplateService = Depends(get_shift_template_service),
):
    updated = service.update_shift_template(shift_template_id, shift_template)
    if updated is None:
        raise HTTPException(status_code=404, detail="Shift template not found")
    return updated


@router.delete(
    "/{shift_template_id}", operation_id="delete_shift_template", status_code=204
)
def delete_shift_template(
    shift_template_id: UUID,
    service: ShiftTemplateService = Depends(get_shift_template_service),
):
    try:
        service.delete_shift_template(shift_template_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Shift template not found")
