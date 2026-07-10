from sqlalchemy import Column, String
from sqlmodel import Field, Relationship

from scheduler_api.db.models.base import BaseModel
from scheduler_api.db.models.associations.shift_worker_link import ShiftWorkerLinkModel


class WorkerModel(BaseModel, table=True):
    __tablename__ = "workers"

    name: str = Field(sa_column=Column(String, nullable=False))

    shifts: list["ShiftModel"] = Relationship(
        back_populates="workers", link_model=ShiftWorkerLinkModel
    )
