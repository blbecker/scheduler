# scheduler_api/mappers/skill_mapper.py
from scheduler_api.db.models import Skill
from scheduler_api.schemas.skill import SkillCreate, SkillResponse, SkillUpdate


def to_response(model: Skill) -> SkillResponse:
    return SkillResponse(
        id=model.id,
        name=model.name,
    )


def from_create(dto: SkillCreate) -> Skill:
    return Skill(**dto.model_dump())


def apply_update(model: Skill, dto: SkillUpdate) -> Skill:
    data = dto.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(model, k, v)
    return model