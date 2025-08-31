from typing import List, Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy.orm import Mapped
from uuid import UUID, uuid4

from .associations import WorkerSkillLink, ShiftSkillLink

if TYPE_CHECKING:
    from .worker import Worker
    from .shift import Shift


# --- core model ---
class Skill(SQLModel, table=True):
    id: Optional[UUID] = Field(default=uuid4(), primary_key=True)
    name: str

    # Relations
    workers: list["Worker"] = Relationship(
        back_populates="skills", link_model=WorkerSkillLink
    )
    shifts: list["Shift"] = Relationship(
        back_populates="skills", link_model=ShiftSkillLink
    )
