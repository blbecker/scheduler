from fastapi import APIRouter, Depends
from ..db import get_session
from sqlmodel import Session
from ..services.worker_service import WorkerService

router = APIRouter()


@router.get("/")
def list_workers(session: Session = Depends(get_session)):
    # The workerservice taks a repository, via dependency injection, not a session. AI!
    service = WorkerService(session)
    return service.list_workers()
