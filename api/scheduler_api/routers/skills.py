from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID
from ..services.skill_service import SkillService
from ..repositories.skill_repository import SkillRepository
from ..models.skill import Skill
from ..db import get_session

router = APIRouter(prefix="/skills", tags=["skills"])


def get_skill_repo() -> SkillRepository:
    return SkillRepository(get_session())


@router.get("/")
def list_skills(repo: SkillRepository = Depends(get_skill_repo)):
    service = SkillService(repo)
    return service.list_skills()


@router.get("/{skill_id}")
def get_skill(skill_id: UUID, repo: SkillRepository = Depends(get_skill_repo)):
    service = SkillService(repo)
    return service.get_skill(skill_id)


@router.post("/", status_code=201)
def create_skill(skill: Skill, repo: SkillRepository = Depends(get_skill_repo)):
    service = SkillService(repo)
    return service.create_skill(skill)


@router.put("/{skill_id}")
def update_skill(
    skill_id: UUID, skill: Skill, repo: SkillRepository = Depends(get_skill_repo)
):
    skill.id = skill_id
    service = SkillService(repo)
    updated_skill = service.update_skill(skill)
    if updated_skill is None:
        raise HTTPException(status_code=404, detail="Skill not found")
    return updated_skill


@router.delete("/{skill_id}", status_code=204)
def delete_skill(skill_id: UUID, repo: SkillRepository = Depends(get_skill_repo)):
    service = SkillService(repo)
    if not service.delete_skill(skill_id):
        raise HTTPException(status_code=404, detail="Skill not found")
    return None
