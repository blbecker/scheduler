from fastapi import APIRouter, Depends
from ..db import get_session
from sqlmodel import Session

router = APIRouter()


@router.get("/")
def list_skills(session: Session = Depends(get_session)):
    return [{"id": 1, "name": "Sample Task"}]
