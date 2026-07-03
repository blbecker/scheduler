from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID, uuid4

from scheduler_api.db.models.associations import WorkerSkillLink, ShiftSkillLink
from scheduler_api.db.models.base import BaseModel

if TYPE_CHECKING:
    from .worker import Worker
    from .shift import Shift


# --- core model ---
class Skill(BaseModel, table=True):
    name: str

    # Relations
    workers: list["Worker"] = Relationship(
        back_populates="skills", link_model=WorkerSkillLink
    )
    shifts: list["Shift"] = Relationship(
        back_populates="skills", link_model=ShiftSkillLink
    )
