from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID

from scheduler_api.services.worker_service import WorkerService
from scheduler_api.schemas.worker import (
    Worker,
    WorkerUpdate,
    WorkerResponse,
)

from ..deps import get_unit_of_work_provider
from scheduler_api.uow.unit_of_work import UnitOfWork

router = APIRouter(prefix="/workers", tags=["workers"])


@router.get("/", response_model=list[WorkerResponse], operation_id="list_workers")
def list_workers(uow: UnitOfWork = Depends(get_unit_of_work_provider())):
    service = WorkerService(uow)
    return service.list_workers()


@router.get("/{worker_id}", response_model=WorkerResponse, operation_id="get_worker")
def get_worker(
    worker_id: UUID,
    uow: UnitOfWork = Depends(get_unit_of_work_provider()),
):
    service = WorkerService(uow)
    worker = service.get_worker(worker_id)
    if worker is None:
        raise HTTPException(status_code=404, detail="Worker not found")
    return worker


@router.post(
    "/", response_model=WorkerResponse, status_code=201, operation_id="create_worker"
)
def create_worker(
    worker: Worker,
    uow: UnitOfWork = Depends(get_unit_of_work_provider()),
):
    service = WorkerService(uow)
    return service.create_worker(worker)


@router.put("/{worker_id}", response_model=WorkerResponse, operation_id="update_worker")
def update_worker(
    worker_id: UUID,
    worker: WorkerUpdate,
    uow: UnitOfWork = Depends(get_unit_of_work_provider()),
):
    service = WorkerService(uow)
    updated = service.update_worker(worker_id, worker)
    if updated is None:
        raise HTTPException(status_code=404, detail="Worker not found")
    return updated


@router.delete("/{worker_id}", status_code=204, operation_id="delete_worker")
def delete_worker(
    worker_id: UUID,
    uow: UnitOfWork = Depends(get_unit_of_work_provider()),
):
    service = WorkerService(uow)
    service.delete_worker(worker_id)
