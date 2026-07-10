from typing import TYPE_CHECKING
from sqlalchemy import Column, String
from sqlmodel import Field, Relationship

from scheduler_api.db.models.base import BaseModel
from scheduler_api.db.models.associations.shift_skill_link import ShiftSkillLinkModel
from scheduler_api.db.models.associations.shift_template_skill import ShiftTemplateSkillModel

if TYPE_CHECKING:
    from scheduler_api.db.models.schedules.shift import ShiftModel
    from scheduler_api.db.models.templates.shift_template import ShiftTemplateModel


class SkillModel(BaseModel, table=True):
    __tablename__ = "skills"

    name: str = Field(sa_column=Column(String, unique=True, index=True, nullable=False))
    description: str | None = None

    shifts: list["ShiftModel"] = Relationship(
        back_populates="skills", link_model=ShiftSkillLinkModel
    )

    shift_templates: list["ShiftTemplateModel"] = Relationship(
        back_populates="skills", link_model=ShiftTemplateSkillModel
    )
