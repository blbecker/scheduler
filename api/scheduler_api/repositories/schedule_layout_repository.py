from datetime import datetime
from typing import List, Optional
from uuid import UUID
from sqlmodel import Session
from scheduler_api.db.models import ScheduleLayout, ScheduleLayoutUpdate


class ScheduleLayoutRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_all(self) -> List[ScheduleLayout]:
        return self.session.query(ScheduleLayout).all()

    def get_by_id(self, layout_id: UUID) -> Optional[ScheduleLayout]:
        return self.session.get(ScheduleLayout, layout_id)

    def create(self, layout: ScheduleLayout) -> ScheduleLayout:
        self.session.add(layout)
        self.session.commit()
        self.session.refresh(layout)
        return layout

    def update(
        self, layout_id: UUID, layout_update: ScheduleLayoutUpdate
    ) -> Optional[ScheduleLayout]:
        layout = self.session.get(ScheduleLayout, layout_id)
        if not layout:
            return None

        update_data = layout_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(layout, key, value)

        self.session.add(layout)
        self.session.commit()
        self.session.refresh(layout)
        return layout

    def delete(self, layout_id: UUID) -> bool:
        layout = self.session.get(ScheduleLayout, layout_id)
        if not layout:
            return False

        self.session.delete(layout)
        self.session.commit()
        return True

    def get_by_date_range(
        self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None
    ) -> List[ScheduleLayout]:
        query = self.session.query(ScheduleLayout)

        if start_date:
            query = query.filter(ScheduleLayout.date_range_start >= start_date)
        if end_date:
            query = query.filter(ScheduleLayout.date_range_end <= end_date)

        return query.all()
