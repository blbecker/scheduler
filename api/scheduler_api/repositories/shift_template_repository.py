# scheduler_api/repositories/shift_template_repository.py
from typing import Optional
from uuid import UUID
from sqlmodel import Session, select

from scheduler_api.db.models.templates.shift_template import ShiftTemplateModel


class ShiftTemplateRepository:
    """
    Repository for shift template data access.
    
    Repositories are responsible for data access only.
    They never commit or rollback transactions - services own transaction boundaries.
    """
    
    def __init__(self, session: Session):
        self.session = session

    def get_all(self) -> list[ShiftTemplateModel]:
        """Get all shift templates."""
        statement = select(ShiftTemplateModel)
        result = self.session.exec(statement)
        return list(result.all())

    def get_by_id(self, id: UUID) -> Optional[ShiftTemplateModel]:
        """Get shift template by ID."""
        return self.session.get(ShiftTemplateModel, id)

    def add(self, model: ShiftTemplateModel) -> ShiftTemplateModel:
        """
        Add a shift template to the session.
        
        Note: Does not commit - service owns transaction boundaries.
        """
        self.session.add(model)
        # No commit - service owns transaction
        return model

    def delete(self, model: ShiftTemplateModel) -> None:
        """
        Delete a shift template from the session.
        
        Note: Does not commit - service owns transaction boundaries.
        """
        self.session.delete(model)
        # No commit - service owns transaction
