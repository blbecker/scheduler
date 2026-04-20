from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID, uuid4
from .associations import ShiftWorkerLink, ShiftSkillLink

if TYPE_CHECKING:
    from .skill import Skill
    from .worker import Worker


# --- core model ---
class Shift(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    start_time: datetime
    end_time: datetime
    location: Optional[str] = None
    notes: Optional[str] = None

    skills: list["Skill"] = Relationship(
        back_populates="shifts", link_model=ShiftSkillLink
    )
    workers: list["Worker"] = Relationship(
        back_populates="shifts", link_model=ShiftWorkerLink
    )
