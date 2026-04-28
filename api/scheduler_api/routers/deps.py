from fastapi import Depends

from scheduler_api.db.session import get_session
from scheduler_api.repositories.shift_repository import ShiftRepository
from scheduler_api.repositories.skill_repository import SkillRepository
from scheduler_api.repositories.worker_repository import WorkerRepository
from scheduler_api.repositories.schedule_layout_repository import ScheduleLayoutRepository
from scheduler_api.services.shift_service import ShiftService
from scheduler_api.services.skill_service import SkillService
from scheduler_api.services.worker_service import WorkerService
from scheduler_api.services.schedule_layout_service import ScheduleLayoutService


# -----------------------------
# DB Session Dependency
# -----------------------------
def get_db_session():
    """
    Provides a SQLAlchemy session per request.
    """
    return get_session()


# -----------------------------
# Repository Dependencies
# -----------------------------
def get_shift_repository(session=Depends(get_db_session)) -> ShiftRepository:
    """
    Shift repository bound to request-scoped DB session.
    """
    return ShiftRepository(session)


def get_skill_repository(session=Depends(get_db_session)) -> SkillRepository:
    """
    Skill repository bound to request-scoped DB session.
    """
    return SkillRepository(session)


def get_worker_repository(session=Depends(get_db_session)) -> WorkerRepository:
    """
    Worker repository bound to request-scoped DB session.
    """
    return WorkerRepository(session)


# -----------------------------
# Service Dependencies
# -----------------------------
def get_shift_service(
    repo: ShiftRepository = Depends(get_shift_repository),
) -> ShiftService:
    """
    Shift service (application/business boundary).
    """
    return ShiftService(repo)


def get_skill_service(
    repo: SkillRepository = Depends(get_skill_repository),
) -> SkillService:
    """
    Skill service (application/business boundary).
    """
    return SkillService(repo)


def get_worker_service(
    repo: WorkerRepository = Depends(get_worker_repository),
) -> WorkerService:
    """
    Worker service (application/business boundary).
    """
    return WorkerService(repo)


def get_schedule_layout_repository(session=Depends(get_db_session)) -> ScheduleLayoutRepository:
    """
    Schedule layout repository bound to request-scoped DB session.
    """
    return ScheduleLayoutRepository(session)


def get_schedule_layout_service(
    repo: ScheduleLayoutRepository = Depends(get_schedule_layout_repository),
) -> ScheduleLayoutService:
    """
    Schedule layout service (application/business boundary).
    """
    return ScheduleLayoutService(repo)
