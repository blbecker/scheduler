from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID

from scheduler_api.services.skill_service import SkillService
from scheduler_api.schemas.skill import (
    SkillCreate,
    SkillUpdate,
    SkillResponse,
)

from .deps import get_skill_service

router = APIRouter(prefix="/skills", tags=["skills"])


@router.get("/", response_model=list[SkillResponse])
def list_skills(service: SkillService = Depends(get_skill_service)):
    return service.list_skills()


@router.get("/{skill_id}", response_model=SkillResponse)
def get_skill(
    skill_id: UUID,
    service: SkillService = Depends(get_skill_service),
):
    skill = service.get_skill(skill_id)
    if skill is None:
        raise HTTPException(status_code=404, detail="Skill not found")
    return skill


@router.post("/", response_model=SkillResponse, status_code=201)
def create_skill(
    skill: SkillCreate,
    service: SkillService = Depends(get_skill_service),
):
    return service.create_skill(skill)


@router.put("/{skill_id}", response_model=SkillResponse)
def update_skill(
    skill_id: UUID,
    skill: SkillUpdate,
    service: SkillService = Depends(get_skill_service),
):
    updated = service.update_skill(skill_id, skill)
    if updated is None:
        raise HTTPException(status_code=404, detail="Skill not found")
    return updated


@router.delete("/{skill_id}", status_code=204)
def delete_skill(
    skill_id: UUID,
    service: SkillService = Depends(get_skill_service),
):
    ok = service.delete_skill(skill_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Skill not found")
    return None
