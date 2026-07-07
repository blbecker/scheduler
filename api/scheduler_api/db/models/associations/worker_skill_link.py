import uuid
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID


class WorkerSkillLinkModel(SQLModel, table=True):
    __tablename__ = "worker_skill_links"

    worker_id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("workers.id", ondelete="CASCADE"),
            primary_key=True)
    )

    skill_id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("skills.id", ondelete="CASCADE"),
            primary_key=True)
    )
