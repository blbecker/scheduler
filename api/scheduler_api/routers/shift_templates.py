# scheduler_api/routers/shift_templates.py
from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID

from scheduler_api.services.shift_template_service import ShiftTemplateService
from scheduler_api.schemas.shift_template import (
    ShiftTemplateCreate,
    ShiftTemplateUpdate,
    ShiftTemplateResponse,
)
from scheduler_api.uow.unit_of_work import UnitOfWork

from .deps import get_unit_of_work_provider

router = APIRouter(prefix="/shift-templates", tags=["shift-templates"])


@router.get("/", response_model=list[ShiftTemplateResponse])
def list_shift_templates(
    uow: UnitOfWork = Depends(get_unit_of_work_provider()),
):
    service = ShiftTemplateService(uow)
    return service.list_shift_templates()


@router.get("/{shift_template_id}", response_model=ShiftTemplateResponse)
def get_shift_template(
    shift_template_id: UUID,
    uow: UnitOfWork = Depends(get_unit_of_work_provider()),
):
    service = ShiftTemplateService(uow)
    try:
        return service.get_shift_template(shift_template_id)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=404, detail="Shift template not found")


@router.post("/", response_model=ShiftTemplateResponse, status_code=201)
def create_shift_template(
    shift_template: ShiftTemplateCreate,
    uow: UnitOfWork = Depends(get_unit_of_work_provider()),
):
    service = ShiftTemplateService(uow)
    return service.create_shift_template(shift_template)


@router.put("/{shift_template_id}", response_model=ShiftTemplateResponse)
def update_shift_template(
    shift_template_id: UUID,
    shift_template: ShiftTemplateUpdate,
    uow: UnitOfWork = Depends(get_unit_of_work_provider()),
):
    service = ShiftTemplateService(uow)
    try:
        return service.update_shift_template(shift_template_id, shift_template)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=404, detail="Shift template not found")


@router.delete("/{shift_template_id}", status_code=204)
def delete_shift_template(
    shift_template_id: UUID,
    uow: UnitOfWork = Depends(get_unit_of_work_provider()),
):
    service = ShiftTemplateService(uow)
    try:
        service.delete_shift_template(shift_template_id)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=404, detail="Shift template not found")
    return None
