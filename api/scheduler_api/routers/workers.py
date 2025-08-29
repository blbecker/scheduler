from fastapi import APIRouter, Depends
from ..db import get_session
from sqlmodel import Session
from ..services.worker_service import WorkerService
from ..repositories.worker_repository import WorkerRepository

router = APIRouter()


def get_worker_repo(session: Session = Depends(get_session)) -> WorkerRepository:
    return WorkerRepository(session)


@router.get("/")
def list_workers(repo: WorkerRepository = Depends(get_worker_repo)):
    service = WorkerService(repo)
    return service.list_workers()
