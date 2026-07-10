import uuid
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID


class ShiftSkillLinkModel(SQLModel, table=True):
    __tablename__ = "shift_skill_links"

    shift_id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("shifts.id", ondelete="CASCADE"),
            primary_key=True,
        )
    )

    skill_id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("skills.id", ondelete="CASCADE"),
            primary_key=True,
        )
    )
