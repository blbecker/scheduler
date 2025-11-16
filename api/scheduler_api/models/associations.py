from sqlmodel import SQLModel, Field
from uuid import UUID


class WorkerSkillLink(SQLModel, table=True):
    worker_id: UUID = Field(foreign_key="worker.id", primary_key=True)
    skill_id: UUID = Field(foreign_key="skill.id", primary_key=True)


class ShiftSkillLink(SQLModel, table=True):
    shift_id: UUID = Field(foreign_key="shift.id", primary_key=True)
    skill_id: UUID = Field(foreign_key="skill.id", primary_key=True)


class ShiftWorkerLink(SQLModel, table=True):
    shift_id: UUID = Field(foreign_key="shift.id", primary_key=True)
    worker_id: UUID = Field(foreign_key="worker.id", primary_key=True)


class ScheduleTemplateShiftLink(SQLModel, table=True):
    schedule_template_id: UUID = Field(
        foreign_key="scheduletemplate.id", primary_key=True
    )
    shift_template_id: UUID = Field(foreign_key="shifttemplate.id", primary_key=True)
