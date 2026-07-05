from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID
from sqlmodel import Session

from scheduler_api.services.skill_service import SkillService
from scheduler_api.repositories.skill_repository import SkillRepository
from scheduler_api.schemas.skill import (
    Skill,
    SkillUpdate,
    SkillResponse,
)

from ..deps import get_db_session

router = APIRouter(prefix="/skills", tags=["skills"])


@router.get("/", response_model=list[SkillResponse], operation_id="list_skills")
def list_skills(session: Session = Depends(get_db_session)):
    repo = SkillRepository(session)
    service = SkillService(repo)
    return service.list_skills()


@router.get("/{skill_id}", response_model=SkillResponse, operation_id="get_skill")
def get_skill(
    skill_id: UUID,
    session: Session = Depends(get_db_session),
):
    repo = SkillRepository(session)
    service = SkillService(repo)
    skill = service.get_skill(skill_id)
    if skill is None:
        raise HTTPException(status_code=404, detail="Skill not found")
    return skill


@router.post(
    "/", response_model=SkillResponse, operation_id="create_skill", status_code=201
)
def create_skill(
    skill: Skill,
    session: Session = Depends(get_db_session),
):
    repo = SkillRepository(session)
    service = SkillService(repo)
    return service.create_skill(skill)


@router.put("/{skill_id}", response_model=SkillResponse, operation_id="update_skill")
def update_skill(
    skill_id: UUID,
    skill: SkillUpdate,
    session: Session = Depends(get_db_session),
):
    repo = SkillRepository(session)
    service = SkillService(repo)
    updated = service.update_skill(skill_id, skill)
    if updated is None:
        raise HTTPException(status_code=404, detail="Skill not found")
    return updated


@router.delete("/{skill_id}", operation_id="delete_skill", status_code=204)
def delete_skill(
    skill_id: UUID,
    session: Session = Depends(get_db_session),
):
    repo = SkillRepository(session)
    service = SkillService(repo)
    service.delete_skill(skill_id)
