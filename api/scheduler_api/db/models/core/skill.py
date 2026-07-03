from sqlalchemy import Column, String
from sqlmodel import Field, Relationship

from scheduler_api.db.models.base import BaseModel
from scheduler_api.db.models.associations.shift_skill_link import ShiftSkillLink


class Skill(BaseModel, table=True):
    __tablename__ = "skills"

    name: str = Field(sa_column=Column(String, unique=True, index=True, nullable=False))
    description: str | None = None

    shifts: list["Shift"] = Relationship(
        back_populates="skills",
        link_model=ShiftSkillLink,
    )
