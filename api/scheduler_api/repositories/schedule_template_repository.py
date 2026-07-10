# scheduler_api/repositories/schedule_template_repository.py
from typing import Optional
from uuid import UUID
from sqlmodel import Session, select

from scheduler_api.db.models.templates.schedule_template import ScheduleTemplateModel


class ScheduleTemplateRepository:
    """
    Repository for schedule template data access.

    Repositories are responsible for data access only.
    They never commit or rollback transactions - services own transaction boundaries.
    """

    def __init__(self, session: Session):
        self.session = session

    def get_all(self) -> list[ScheduleTemplateModel]:
        """Get all schedule templates."""
        statement = select(ScheduleTemplateModel)
        result = self.session.exec(statement)
        return list(result.all())

    def get_by_id(self, id: UUID) -> Optional[ScheduleTemplateModel]:
        """Get schedule template by ID."""
        return self.session.get(ScheduleTemplateModel, id)

    def add(self, model: ScheduleTemplateModel) -> ScheduleTemplateModel:
        """
        Add a schedule template to the session.

        Note: Does not commit - service owns transaction boundaries.
        """
        self.session.add(model)
        # No commit - service owns transaction
        return model

    def delete(self, model: ScheduleTemplateModel) -> None:
        """
        Delete a schedule template from the session.

        Note: Does not commit - service owns transaction boundaries.
        """
        self.session.delete(model)
        # No commit - service owns transaction
