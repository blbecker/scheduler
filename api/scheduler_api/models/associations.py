from sqlmodel import SQLModel, Field, ForeignKey
from typing import Optional
from uuid import UUID
from typing import List, Optional, TYPE_CHECKING


class WorkerSkillLink(SQLModel, table=True):
    worker_id: UUID = Field(foreign_key="worker.id", primary_key=True)
    skill_id: UUID = Field(foreign_key="skill.id", primary_key=True)


class ShiftSkillLink(SQLModel, table=True):
    shift_id: UUID = Field(foreign_key="shift.id", primary_key=True)
    skill_id: UUID = Field(foreign_key="skill.id", primary_key=True)


class ShiftWorkerLink(SQLModel, table=True):
    shift_id: UUID = Field(foreign_key="shift.id", primary_key=True)
    worker_id: UUID = Field(foreign_key="worker.id", primary_key=True)
