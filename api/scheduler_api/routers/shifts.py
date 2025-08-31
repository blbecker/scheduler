from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID
from ..services.shift_service import ShiftService
from ..repositories.shift_repository import ShiftRepository
from ..models.shift import Shift

router = APIRouter()


def get_shift_repo() -> ShiftRepository:
    return ShiftRepository()


@router.get("/")
def list_shifts(repo: ShiftRepository = Depends(get_shift_repo)):
    service = ShiftService(repo)
    return service.list_shifts()


@router.get("/{shift_id}")
def get_shift(shift_id: UUID, repo: ShiftRepository = Depends(get_shift_repo)):
    service = ShiftService(repo)
    return service.get_shift(shift_id)


@router.post("/", status_code=201)
def create_shift(shift: Shift, repo: ShiftRepository = Depends(get_shift_repo)):
    service = ShiftService(repo)
    return service.create_shift(shift)


@router.put("/{shift_id}")
def update_shift(
    shift_id: UUID, shift: Shift, repo: ShiftRepository = Depends(get_shift_repo)
):
    shift.id = shift_id
    service = ShiftService(repo)
    updated_shift = service.update_shift(shift)
    if updated_shift is None:
        raise HTTPException(status_code=404, detail="Shift not found")
    return updated_shift


@router.delete("/{shift_id}", status_code=204)
def delete_shift(shift_id: UUID, repo: ShiftRepository = Depends(get_shift_repo)):
    service = ShiftService(repo)
    if not service.delete_shift(shift_id):
        raise HTTPException(status_code=404, detail="Shift not found")
    return None
