from fastapi import APIRouter, Depends
from ..db import get_session
from sqlmodel import Session

router = APIRouter()


# Update the get method to consume a WorkerService, from ../services/ to retrieve a list of workers. Return it. AI!
@router.get("/")
def list_workers(session: Session = Depends(get_session)):
    return [{"id": 1, "name": "Sample Task"}]
