from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID, uuid4
from scheduler_api.db.models.associations import ShiftWorkerLink, ShiftSkillLink
from scheduler_api.db.models.base import BaseModel

if TYPE_CHECKING:
    from .skill import Skill
    from .worker import Worker


# --- core model ---
class Shift(BaseModel, table=True):
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
