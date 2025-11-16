from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID
from ..services.shift_service import ShiftService
from ..repositories.shift_repository import ShiftRepository
from ..db import get_session
from typing import List
from scheduler_api.schemas.shift import ShiftCreate, ShiftUpdate, ShiftRead
from sqlmodel import Session
from scheduler_api.mappers.shift_mapper import shift_to_read, list_shifts_to_read

router = APIRouter(prefix="/shifts", tags=["shifts"])


@router.get("/", response_model=List[ShiftRead])
def list_shifts(session: Session = Depends(get_session)):
    repo = ShiftRepository(session)
    service = ShiftService(repo)
    return list_shifts_to_read(service.list_shifts())


@router.get("/{shift_id}", response_model=ShiftRead)
def get_shift(shift_id: UUID, session: Session = Depends(get_session)):
    repo = ShiftRepository(session)
    service = ShiftService(repo)
    return shift_to_read(service.get_shift(shift_id))


@router.post("/", status_code=201, response_model=ShiftRead)
def create_shift(shift: ShiftCreate, session: Session = Depends(get_session)):
    repo = ShiftRepository(session)
    service = ShiftService(repo)
    return shift_to_read(service.create_shift(shift))


@router.put("/{shift_id}", response_model=ShiftRead)
def update_shift(
    shift_id: UUID, shift: ShiftUpdate, session: Session = Depends(get_session)
):
    repo = ShiftRepository(session)
    shift.id = shift_id
    service = ShiftService(repo)
    updated_shift = service.update_shift(shift)
    if updated_shift is None:
        raise HTTPException(status_code=404, detail="Shift not found")
    return shift_to_read(updated_shift)


@router.delete("/{shift_id}", status_code=204)
def delete_shift(shift_id: UUID, session: Session = Depends(get_session)):
    repo = ShiftRepository(session)
    service = ShiftService(repo)
    if not service.delete_shift(shift_id):
        raise HTTPException(status_code=404, detail="Shift not found")
    return None
