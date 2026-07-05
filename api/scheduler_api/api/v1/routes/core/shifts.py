from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID
from sqlmodel import Session

from scheduler_api.services.shift_service import ShiftService
from scheduler_api.repositories.shift_repository import ShiftRepository
from scheduler_api.schemas.shift import (
    Shift,
    ShiftUpdate,
    ShiftResponse,
)

from ..deps import get_db_session

router = APIRouter(prefix="/shifts", tags=["shifts"])


@router.get("/", response_model=list[ShiftResponse], operation_id="list_shifts")
def list_shifts(session: Session = Depends(get_db_session)):
    repo = ShiftRepository(session)
    service = ShiftService(repo)
    return service.list_shifts()


@router.get("/{shift_id}", response_model=ShiftResponse, operation_id="get_shift")
def get_shift(
    shift_id: UUID,
    session: Session = Depends(get_db_session),
):
    repo = ShiftRepository(session)
    service = ShiftService(repo)
    shift = service.get_shift(shift_id)
    if shift is None:
        raise HTTPException(status_code=404, detail="Shift not found")
    return shift


@router.post(
    "/", response_model=ShiftResponse, operation_id="create_shift", status_code=201
)
def create_shift(
    shift: Shift,
    session: Session = Depends(get_db_session),
):
    repo = ShiftRepository(session)
    service = ShiftService(repo)
    return service.create_shift(shift)


@router.put("/{shift_id}", response_model=ShiftResponse, operation_id="update_shift")
def update_shift(
    shift_id: UUID,
    shift: ShiftUpdate,
    session: Session = Depends(get_db_session),
):
    repo = ShiftRepository(session)
    service = ShiftService(repo)
    updated = service.update_shift(shift_id, shift)
    if updated is None:
        raise HTTPException(status_code=404, detail="Shift not found")
    return updated


@router.delete("/{shift_id}", operation_id="delete_shift", status_code=204)
def delete_shift(
    shift_id: UUID,
    session: Session = Depends(get_db_session),
):
    repo = ShiftRepository(session)
    service = ShiftService(repo)
    service.delete_shift(shift_id)
