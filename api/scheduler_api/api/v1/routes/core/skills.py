from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID

from scheduler_api.services.skill_service import SkillService
from scheduler_api.schemas.skill import SkillCreate, SkillUpdate, SkillResponse

from ..deps import get_skill_service

router = APIRouter(prefix="/skills", tags=["skills"])


@router.get("/", response_model=list[SkillResponse], operation_id="list_skills")
def list_skills(service: SkillService = Depends(get_skill_service)):
    return service.list_skills()


@router.get("/{skill_id}", response_model=SkillResponse, operation_id="get_skill")
def get_skill(skill_id: UUID, service: SkillService = Depends(get_skill_service)):
    skill = service.get_skill(skill_id)
    if skill is None:
        raise HTTPException(status_code=404, detail="Skill not found")
    return skill


@router.post(
    "/", response_model=SkillResponse, operation_id="create_skill", status_code=201
)
def create_skill(
    skill: SkillCreate, service: SkillService = Depends(get_skill_service)
):
    return service.create_skill(skill)


@router.put("/{skill_id}", response_model=SkillResponse, operation_id="update_skill")
def update_skill(
    skill_id: UUID,
    skill: SkillUpdate,
    service: SkillService = Depends(get_skill_service),
):
    updated = service.update_skill(skill_id, skill)
    if updated is None:
        raise HTTPException(status_code=404, detail="Skill not found")
    return updated


@router.delete("/{skill_id}", operation_id="delete_skill", status_code=204)
def delete_skill(skill_id: UUID, service: SkillService = Depends(get_skill_service)):
    try:
        service.delete_skill(skill_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Skill not found")
