import uuid
from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlmodel import Field, Relationship

from scheduler_api.db.models.base import BaseModel
from scheduler_api.db.models.associations.shift_skill_link import ShiftSkillLinkModel

if TYPE_CHECKING:
    from scheduler_api.db.models.templates.shift_template import ShiftTemplateModel
    from scheduler_api.db.models.assignments.shift_assignment import (
        ShiftAssignmentModel,
    )
    from scheduler_api.db.models.core.skill import SkillModel


class ShiftModel(BaseModel, table=True):
    __tablename__ = "shifts"

    shift_template_id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("shift_templates.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        )
    )

    name: str = Field(sa_column=Column(String, nullable=False))

    start_time: datetime
    end_time: datetime

    shift_template: "ShiftTemplateModel" = Relationship(back_populates="shifts")

    skills: list["SkillModel"] = Relationship(
        back_populates="shifts", link_model=ShiftSkillLinkModel
    )

    assignment: "ShiftAssignmentModel" = Relationship(back_populates="shift")
