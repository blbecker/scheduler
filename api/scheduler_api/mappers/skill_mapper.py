from scheduler_api.models import Skill
from scheduler_api.schemas.skill import SkillRead, SkillCreate, SkillUpdate
from typing import List
import logging

logger = logging.getLogger(__name__)


def skill_create_to_model(dto: SkillCreate) -> Skill:
    skill_model = Skill(name=dto.name)
    logger.debug(f"Mapped SkillCreate DTO {dto} to Skill model: {skill_model}")
    return skill_model


def skill_update_to_model(dto: SkillUpdate) -> Skill:
    return Skill(name=dto.name)


def skill_to_read(skill: Skill) -> SkillRead:
    return SkillRead(
        id=skill.id,
        name=skill.name,
    )


def list_skills_to_read(skills: List[Skill]) -> List[SkillRead]:
    return [skill_to_read(w) for w in skills]
