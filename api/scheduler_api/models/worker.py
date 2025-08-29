from datetime import date
from typing import List, Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
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
    skills: List["Skill"] = Relationship(back_populates="workers", link_model=WorkerSkillLink)
    shifts: List["Shift"] = Relationship(back_populates="workers", link_model=ShiftWorkerLink)
