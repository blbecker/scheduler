from sqlmodel import SQLModel, Field, ForeignKey
from typing import Optional

class WorkerSkillLink(SQLModel, table=True):
    worker_id: int = Field(foreign_key="worker.id", primary_key=True)
    skill_id: int = Field(foreign_key="skill.id", primary_key=True)

class ShiftSkillLink(SQLModel, table=True):
    shift_id: int = Field(foreign_key="shift.id", primary_key=True)
    skill_id: int = Field(foreign_key="skill.id", primary_key=True)

class ShiftWorkerLink(SQLModel, table=True):
    shift_id: int = Field(foreign_key="shift.id", primary_key=True)
    worker_id: int = Field(foreign_key="worker.id", primary_key=True)
