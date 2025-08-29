from fastapi import APIRouter, Depends
from ..db import get_session
from sqlmodel import Session
from ..services.worker_service import WorkerService
from ..repositories.worker_repository import WorkerRepository

router = APIRouter()


def get_worker_repo() -> WorkerRepository:
    return WorkerRepository()


@router.get("/")
def list_workers(repo: WorkerRepository = Depends(get_worker_repo)):
    service = WorkerService(repo)
    return service.list_workers()
