from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID

from scheduler_api.services.shift_service import ShiftService
from scheduler_api.schemas.shift import (
    ShiftCreate,
    ShiftUpdate,
    ShiftResponse,
)

from .deps import get_shift_service

router = APIRouter(prefix="/shifts", tags=["shifts"])


@router.get("/", response_model=list[ShiftResponse])
def list_shifts(service: ShiftService = Depends(get_shift_service)):
    return service.list_shifts()


@router.get("/{shift_id}", response_model=ShiftResponse)
def get_shift(
    shift_id: UUID,
    service: ShiftService = Depends(get_shift_service),
):
    shift = service.get_shift(shift_id)
    if shift is None:
        raise HTTPException(status_code=404, detail="Shift not found")
    return shift


@router.post("/", response_model=ShiftResponse, status_code=201)
def create_shift(
    shift: ShiftCreate,
    service: ShiftService = Depends(get_shift_service),
):
    return service.create_shift(shift)


@router.put("/{shift_id}", response_model=ShiftResponse)
def update_shift(
    shift_id: UUID,
    shift: ShiftUpdate,
    service: ShiftService = Depends(get_shift_service),
):
    updated = service.update_shift(shift_id, shift)
    if updated is None:
        raise HTTPException(status_code=404, detail="Shift not found")
    return updated


@router.delete("/{shift_id}", status_code=204)
def delete_shift(
    shift_id: UUID,
    service: ShiftService = Depends(get_shift_service),
):
    ok = service.delete_shift(shift_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Shift not found")
    return None
