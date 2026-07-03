from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID

from scheduler_api.services.skill_service import SkillService
from scheduler_api.schemas.skill import (
    SkillCreate,
    SkillUpdate,
    SkillResponse,
)

from .deps import get_unit_of_work_provider
from scheduler_api.uow.unit_of_work import UnitOfWork

router = APIRouter(prefix="/skills", tags=["skills"])


@router.get("/", response_model=list[SkillResponse])
def list_skills(uow: UnitOfWork = Depends(get_unit_of_work_provider())):
    service = SkillService(uow)
    return service.list_skills()


@router.get("/{skill_id}", response_model=SkillResponse)
def get_skill(
    skill_id: UUID,
    uow: UnitOfWork = Depends(get_unit_of_work_provider()),
):
    service = SkillService(uow)
    skill = service.get_skill(skill_id)
    if skill is None:
        raise HTTPException(status_code=404, detail="Skill not found")
    return skill


@router.post("/", response_model=SkillResponse, status_code=201)
def create_skill(
    skill: SkillCreate,
    uow: UnitOfWork = Depends(get_unit_of_work_provider()),
):
    service = SkillService(uow)
    return service.create_skill(skill)


@router.put("/{skill_id}", response_model=SkillResponse)
def update_skill(
    skill_id: UUID,
    skill: SkillUpdate,
    uow: UnitOfWork = Depends(get_unit_of_work_provider()),
):
    service = SkillService(uow)
    updated = service.update_skill(skill_id, skill)
    if updated is None:
        raise HTTPException(status_code=404, detail="Skill not found")
    return updated


@router.delete("/{skill_id}", status_code=204)
def delete_skill(
    skill_id: UUID,
    uow: UnitOfWork = Depends(get_unit_of_work_provider()),
):
    service = SkillService(uow)
    service.delete_skill(skill_id)
