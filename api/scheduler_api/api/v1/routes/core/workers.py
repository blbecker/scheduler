from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID
from sqlmodel import Session

from scheduler_api.services.worker_service import WorkerService
from scheduler_api.repositories.worker_repository import WorkerRepository
from scheduler_api.schemas.worker import (
    Worker,
    WorkerUpdate,
    WorkerResponse,
)

from ..deps import get_db_session

router = APIRouter(prefix="/workers", tags=["workers"])


@router.get("/", response_model=list[WorkerResponse], operation_id="list_workers")
def list_workers(session: Session = Depends(get_db_session)):
    repo = WorkerRepository(session)
    service = WorkerService(repo)
    return service.list_workers()


@router.get("/{worker_id}", response_model=WorkerResponse, operation_id="get_worker")
def get_worker(
    worker_id: UUID,
    session: Session = Depends(get_db_session),
):
    repo = WorkerRepository(session)
    service = WorkerService(repo)
    worker = service.get_worker(worker_id)
    if worker is None:
        raise HTTPException(status_code=404, detail="Worker not found")
    return worker


@router.post(
    "/", response_model=WorkerResponse, status_code=201, operation_id="create_worker"
)
def create_worker(
    worker: Worker,
    session: Session = Depends(get_db_session),
):
    repo = WorkerRepository(session)
    service = WorkerService(repo)
    return service.create_worker(worker)


@router.put("/{worker_id}", response_model=WorkerResponse, operation_id="update_worker")
def update_worker(
    worker_id: UUID,
    worker: WorkerUpdate,
    session: Session = Depends(get_db_session),
):
    repo = WorkerRepository(session)
    service = WorkerService(repo)
    updated = service.update_worker(worker_id, worker)
    if updated is None:
        raise HTTPException(status_code=404, detail="Worker not found")
    return updated


@router.delete("/{worker_id}", status_code=204, operation_id="delete_worker")
def delete_worker(
    worker_id: UUID,
    session: Session = Depends(get_db_session),
):
    repo = WorkerRepository(session)
    service = WorkerService(repo)
    service.delete_worker(worker_id)
