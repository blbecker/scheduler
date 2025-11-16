from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from uuid import UUID
from ..services.worker_service import WorkerService
from ..repositories.worker_repository import WorkerRepository
from ..db import get_session
from scheduler_api.schemas.worker import WorkerCreate, WorkerRead, WorkerUpdate
from scheduler_api.mappers.worker_mapper import worker_to_read, list_workers_to_read
from typing import List
import logging

router = APIRouter(prefix="/workers", tags=["workers"])
logger = logging.getLogger(__name__)


@router.get("/", response_model=List[WorkerRead])
def list_workers(session: Session = Depends(get_session)):
    repo = WorkerRepository(session)
    service = WorkerService(repo)
    workers = service.list_workers()
    return list_workers_to_read(workers)


@router.get("/{worker_id}", response_model=WorkerRead)
def get_worker(worker_id: UUID, session: Session = Depends(get_session)):
    repo = WorkerRepository(session)
    service = WorkerService(repo)
    worker = service.get_worker(worker_id)
    return worker_to_read(worker)


@router.post("/", status_code=201, response_model=WorkerRead)
def create_worker(worker: WorkerCreate, session: Session = Depends(get_session)):
    repo = WorkerRepository(session)
    service = WorkerService(repo)
    return worker_to_read(service.create_worker(worker))


@router.put("/{worker_id}", response_model=WorkerRead)
def update_worker(
    worker_id: UUID,
    worker: WorkerUpdate,
    session: Session = Depends(get_session),
):
    repo = WorkerRepository(session)
    service = WorkerService(repo)
    updated_worker = service.update_worker(id, worker)
    if updated_worker is None:
        raise HTTPException(status_code=404, detail="Worker not found")
    return worker_to_read(updated_worker)


@router.delete("/{worker_id}", status_code=204)
def delete_worker(worker_id: UUID, session: Session = Depends(get_session)):
    repo = WorkerRepository(session)
    service = WorkerService(repo)
    if not service.delete_worker(worker_id):
        raise HTTPException(status_code=404, detail="Worker not found")
    return None
