from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID

from scheduler_api.services.worker_service import WorkerService
from scheduler_api.schemas.worker import (
    WorkerCreate,
    WorkerUpdate,
    WorkerResponse,
)

from .deps import get_worker_service

router = APIRouter(prefix="/workers", tags=["workers"])


@router.get("/", response_model=list[WorkerResponse])
def list_workers(service: WorkerService = Depends(get_worker_service)):
    return service.list_workers()


@router.get("/{worker_id}", response_model=WorkerResponse)
def get_worker(
    worker_id: UUID,
    service: WorkerService = Depends(get_worker_service),
):
    worker = service.get_worker(worker_id)
    if worker is None:
        raise HTTPException(status_code=404, detail="Worker not found")
    return worker


@router.post("/", response_model=WorkerResponse, status_code=201)
def create_worker(
    worker: WorkerCreate,
    service: WorkerService = Depends(get_worker_service),
):
    return service.create_worker(worker)


@router.put("/{worker_id}", response_model=WorkerResponse)
def update_worker(
    worker_id: UUID,
    worker: WorkerUpdate,
    service: WorkerService = Depends(get_worker_service),
):
    updated = service.update_worker(worker_id, worker)
    if updated is None:
        raise HTTPException(status_code=404, detail="Worker not found")
    return updated


@router.delete("/{worker_id}", status_code=204)
def delete_worker(
    worker_id: UUID,
    service: WorkerService = Depends(get_worker_service),
):
    ok = service.delete_worker(worker_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Worker not found")
    return None
