from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID
from ..services.skill_service import SkillService
from ..repositories.skill_repository import SkillRepository
from ..db import get_session
from scheduler_api.schemas.skill import SkillCreate, SkillRead, SkillUpdate
from typing import List
from sqlmodel import Session
from scheduler_api.mappers.skill_mapper import list_skills_to_read, skill_to_read

router = APIRouter(prefix="/skills", tags=["skills"])


@router.get("/", response_model=List[SkillRead])
def list_skills(session: Session = Depends(get_session)):
    repo = SkillRepository(session)
    service = SkillService(repo)
    return list_skills_to_read(service.list_skills())


@router.get("/{skill_id}", response_model=SkillRead)
def get_skill(skill_id: UUID, session: Session = Depends(get_session)):
    repo = SkillRepository(session)
    service = SkillService(repo)
    return skill_to_read(service.get_skill(skill_id))


@router.post("/", status_code=201, response_model=SkillRead)
def create_skill(skill: SkillCreate, session: Session = Depends(get_session)):
    repo = SkillRepository(session)
    service = SkillService(repo)
    return skill_to_read(service.create_skill(skill))


@router.put("/{skill_id}", response_model=SkillRead)
def update_skill(
    skill_id: UUID, skill: SkillUpdate, session: Session = Depends(get_session)
):
    repo = SkillRepository(session)
    service = SkillService(repo)
    updated_skill = service.update_skill(skill_id, skill)
    if updated_skill is None:
        raise HTTPException(status_code=404, detail="Skill not found")
    return skill_to_read(updated_skill)


@router.delete("/{skill_id}", status_code=204)
def delete_skill(skill_id: UUID, session: Session = Depends(get_session)):
    repo = SkillRepository(session)
    service = SkillService(repo)
    if not service.delete_skill(skill_id):
        raise HTTPException(status_code=404, detail="Skill not found")
    return None
