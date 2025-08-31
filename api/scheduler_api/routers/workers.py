from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID
from sqlmodel import Session
from ..services.worker_service import WorkerService
from ..repositories.worker_repository import WorkerRepository
from ..models.worker import Worker

router = APIRouter()


def get_worker_repo() -> WorkerRepository:
    return WorkerRepository()


@router.get("/")
def list_workers(repo: WorkerRepository = Depends(get_worker_repo)):
    service = WorkerService(repo)
    return service.list_workers()


@router.get("/{worker_id}")
def get_worker(worker_id: UUID, repo: WorkerRepository = Depends(get_worker_repo)):
    service = WorkerService(repo)
    return service.get_worker(worker_id)


@router.post("/", status_code=201)
def create_worker(worker: Worker, repo: WorkerRepository = Depends(get_worker_repo)):
    service = WorkerService(repo)
    return service.create_worker(worker)


@router.put("/{worker_id}")
def update_worker(
    worker_id: UUID, worker: Worker, repo: WorkerRepository = Depends(get_worker_repo)
):
    worker.id = worker_id
    service = WorkerService(repo)
    updated_worker = service.update_worker(worker)
    if updated_worker is None:
        raise HTTPException(status_code=404, detail="Worker not found")
    return updated_worker


@router.delete("/{worker_id}", status_code=204)
def delete_worker(worker_id: UUID, repo: WorkerRepository = Depends(get_worker_repo)):
    service = WorkerService(repo)
    # TODO: Implement delete logic
    raise HTTPException(status_code=501, detail="Not implemented")
