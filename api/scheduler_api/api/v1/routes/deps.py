from typing import Generator
from fastapi import Depends
from sqlmodel import Session

from scheduler_api.db.session import SessionLocal
from scheduler_api.services.shift_service import ShiftService
from scheduler_api.services.skill_service import SkillService
from scheduler_api.services.worker_service import WorkerService
from scheduler_api.services.schedule_template_service import ScheduleTemplateService
from scheduler_api.services.shift_template_service import ShiftTemplateService
from scheduler_api.services.schedule_service import ScheduleService
from scheduler_api.services.schedule_solve_service import ScheduleSolveService


# -----------------------------
# DB Session Dependency
# -----------------------------
def get_db_session() -> Generator[Session, None, None]:
    """
    Provides a SQLModel session per request.

    FastAPI will use this generator to get a session for each request.
    The session is automatically closed after the request finishes.
    """
    with SessionLocal() as session:
        yield session


# -----------------------------
# Service Dependencies
# -----------------------------
def get_shift_service(session: Session = Depends(get_db_session)) -> ShiftService:
    """
    Shift service (application/business boundary).
    """
    return ShiftService(session)


def get_skill_service(session: Session = Depends(get_db_session)) -> SkillService:
    """
    Skill service (application/business boundary).
    """
    return SkillService(session)


def get_worker_service(session: Session = Depends(get_db_session)) -> WorkerService:
    """
    Worker service (application/business boundary).
    """
    return WorkerService(session)


def get_schedule_template_service(
    session: Session = Depends(get_db_session),
) -> ScheduleTemplateService:
    """
    Schedule template service (application/business boundary).
    """
    return ScheduleTemplateService(session)


def get_shift_template_service(
    session: Session = Depends(get_db_session),
) -> ShiftTemplateService:
    """
    Shift template service (application/business boundary).
    """
    return ShiftTemplateService(session)


def get_schedule_service(session: Session = Depends(get_db_session)) -> ScheduleService:
    """
    Schedule service (application/business boundary).
    """
    return ScheduleService(session)


def get_schedule_solve_service(
    session: Session = Depends(get_db_session),
) -> ScheduleSolveService:
    """
    Schedule solve service (application/business boundary).
    """
    return ScheduleSolveService(session)
