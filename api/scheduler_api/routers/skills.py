from fastapi import APIRouter, Depends
from ..db import get_session
from sqlmodel import Session

router = APIRouter()


# Add the missing CRUD routes, modeled off of workers.py AI!
@router.get("/")
def list_skills(session: Session = Depends(get_session)):
    return [{"id": 1, "name": "Sample Task"}]
