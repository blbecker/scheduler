from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID

from scheduler_api.services.schedule_layout_service import ScheduleLayoutService
from scheduler_api.schemas.schedule_layout import (
    ScheduleLayoutCreate,
    ScheduleLayoutUpdate,
    ScheduleLayoutResponse,
    ScheduleLayoutGenerateResponse,
)

from .deps import get_schedule_layout_service


router = APIRouter(prefix="/schedules/layouts", tags=["schedule-layouts"])


@router.get("/", response_model=list[ScheduleLayoutResponse])
def list_layouts(service: ScheduleLayoutService = Depends(get_schedule_layout_service)):
    return service.list_layouts()


@router.get("/{layout_id}", response_model=ScheduleLayoutResponse)
def get_layout(
    layout_id: UUID,
    service: ScheduleLayoutService = Depends(get_schedule_layout_service),
):
    layout = service.get_layout(layout_id)
    if layout is None:
        raise HTTPException(status_code=404, detail="Schedule layout not found")
    return layout


@router.post("/", response_model=ScheduleLayoutResponse, status_code=201)
def create_layout(
    layout: ScheduleLayoutCreate,
    service: ScheduleLayoutService = Depends(get_schedule_layout_service),
):
    return service.create_layout(layout)


@router.put("/{layout_id}", response_model=ScheduleLayoutResponse)
def update_layout(
    layout_id: UUID,
    layout: ScheduleLayoutUpdate,
    service: ScheduleLayoutService = Depends(get_schedule_layout_service),
):
    updated = service.update_layout(layout_id, layout)
    if updated is None:
        raise HTTPException(status_code=404, detail="Schedule layout not found")
    return updated


@router.delete("/{layout_id}", status_code=204)
def delete_layout(
    layout_id: UUID,
    service: ScheduleLayoutService = Depends(get_schedule_layout_service),
):
    ok = service.delete_layout(layout_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Schedule layout not found")
    return None


@router.post("/{layout_id}/generate", response_model=ScheduleLayoutGenerateResponse)
def generate_schedule(
    layout_id: UUID,
    service: ScheduleLayoutService = Depends(get_schedule_layout_service),
):
    try:
        return service.generate_schedule(layout_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to schedule generation: {str(e)}"
        )
