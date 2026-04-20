from datetime import date
from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID, uuid4
from decimal import Decimal
from .associations import WorkerSkillLink, ShiftWorkerLink

if TYPE_CHECKING:
    from .skill import Skill
    from .shift import Shift


# --- core model ---
class Worker(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str
    birthdate: date
    # hourly_rate: Decimal
    email: Optional[str] = None
    phone: Optional[str] = None

    # relations
    skills: list["Skill"] = Relationship(
        back_populates="workers", link_model=WorkerSkillLink
    )
    shifts: list["Shift"] = Relationship(
        back_populates="workers", link_model=ShiftWorkerLink
    )
