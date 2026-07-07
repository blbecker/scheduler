# scheduler_api/mappers/skill_mapper.py
from scheduler_api.db.models.core.skill import SkillModel
from scheduler_api.schemas.skill import SkillCreate, SkillResponse, SkillUpdate


def to_response(model: SkillModel) -> SkillResponse:
    return SkillResponse(
        id=model.id,
        name=model.name,
        description=model.description,
        created_at=model.created_at,
        updated_at=model.updated_at)


def from_create(dto: SkillCreate) -> SkillModel:
    return SkillModel(**dto.model_dump())


def apply_update(model: SkillModel, dto: SkillUpdate) -> SkillModel:
    data = dto.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(model, k, v)
    return model
