from datetime import date
from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy.orm import Mapped
from uuid import UUID, uuid4
from .associations import WorkerSkillLink, ShiftWorkerLink

if TYPE_CHECKING:
    from .skill import Skill
    from .shift import Shift


# --- core model ---
class Worker(SQLModel, table=True):
    id: Optional[UUID] = Field(default=uuid4(), primary_key=True)
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
