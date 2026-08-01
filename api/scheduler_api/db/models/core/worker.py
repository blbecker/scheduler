from typing import TYPE_CHECKING
from sqlalchemy import Column, String
from sqlmodel import Field, Relationship

from scheduler_api.db.models.base import BaseModel
from scheduler_api.db.models.associations.worker_skill_link import WorkerSkillLinkModel

if TYPE_CHECKING:
    from scheduler_api.db.models.core.skill import SkillModel
    from scheduler_api.db.models.assignments.shift_assignment import (
        ShiftAssignmentModel,
    )


class WorkerModel(BaseModel, table=True):
    __tablename__ = "workers"

    name: str = Field(sa_column=Column(String, nullable=False))

    shift_assignments: list["ShiftAssignmentModel"] = Relationship(
        back_populates="worker",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )

    skills: list["SkillModel"] = Relationship(
        back_populates="workers", link_model=WorkerSkillLinkModel
    )
