from datetime import date
from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID, uuid4
from scheduler_api.db.models.associations import (
    WorkerSkillLink,
    ShiftSkillLink,
    ShiftWorkerLink,
)
from scheduler_api.db.models.base import BaseModel

if TYPE_CHECKING:
    from .skill import Skill
    from .shift import Shift


# --- core model ---
class Worker(BaseModel, table=True):
    name: str
    birthdate: date
    email: Optional[str] = None
    phone: Optional[str] = None

    # relations
    skills: list["Skill"] = Relationship(
        back_populates="workers", link_model=WorkerSkillLink
    )
    shifts: list["Shift"] = Relationship(
        back_populates="workers", link_model=ShiftWorkerLink
    )
