from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import Depends

from scheduler_api.db.session import get_session
from scheduler_api.repositories.shift_repository import ShiftRepository
from scheduler_api.repositories.skill_repository import SkillRepository
from scheduler_api.repositories.worker_repository import WorkerRepository
from scheduler_api.repositories.schedule_template_repository import (
    ScheduleTemplateRepository,
)
from scheduler_api.repositories.shift_template_repository import ShiftTemplateRepository
from scheduler_api.repositories.schedule_repository import ScheduleRepository
from scheduler_api.repositories.schedule_generation_run_repository import (
    ScheduleGenerationRunRepository,
)
from scheduler_api.services.shift_service import ShiftService
from scheduler_api.services.skill_service import SkillService
from scheduler_api.services.worker_service import WorkerService
from scheduler_api.services.schedule_template_service import ScheduleTemplateService
from scheduler_api.services.shift_template_service import ShiftTemplateService
from scheduler_api.services.schedule_service import ScheduleService
from scheduler_api.services.schedule_generation_run_service import (
    ScheduleGenerationRunService,
)
from scheduler_api.uow.unit_of_work import UnitOfWork


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


def get_schedule_template_repository(
    session=Depends(get_db_session),
) -> ScheduleTemplateRepository:
    """
    Schedule template repository bound to request-scoped DB session.
    """
    return ScheduleTemplateRepository(session)


def get_shift_template_repository(
    session=Depends(get_db_session),
) -> ShiftTemplateRepository:
    """
    Shift template repository bound to request-scoped DB session.
    """
    return ShiftTemplateRepository(session)


def get_schedule_repository(session=Depends(get_db_session)) -> ScheduleRepository:
    """
    Schedule repository bound to request-scoped DB session.
    """
    return ScheduleRepository(session)


def get_schedule_generation_run_repository(
    session=Depends(get_db_session),
) -> ScheduleGenerationRunRepository:
    """
    Schedule generation run repository bound to request-scoped DB session.
    """
    return ScheduleGenerationRunRepository(session)


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


def get_schedule_template_service(
    repo: ScheduleTemplateRepository = Depends(get_schedule_template_repository),
) -> ScheduleTemplateService:
    """
    Schedule template service (application/business boundary).
    """
    return ScheduleTemplateService(repo)


def get_shift_template_service(
    repo: ShiftTemplateRepository = Depends(get_shift_template_repository),
) -> ShiftTemplateService:
    """
    Shift template service (application/business boundary).
    """
    return ShiftTemplateService(repo)


def get_schedule_service(
    repo: ScheduleRepository = Depends(get_schedule_repository),
) -> ScheduleService:
    """
    Schedule service (application/business boundary).
    """
    return ScheduleService(repo)


def get_schedule_generation_run_service(
    repo: ScheduleGenerationRunRepository = Depends(
        get_schedule_generation_run_repository
    ),
) -> ScheduleGenerationRunService:
    """
    Schedule generation run service (application/business boundary).
    """
    return ScheduleGenerationRunService(repo)


# -----------------------------
# Unit of Work Dependencies
# -----------------------------
def get_unit_of_work(session=Depends(get_db_session)) -> UnitOfWork:
    """
    Provides a UnitOfWork instance for manual transaction management.
    
    The caller is responsible for calling commit() or rollback().
    For automatic transaction management, use get_unit_of_work_provider().
    """
    return UnitOfWork(session)


def get_unit_of_work_provider():
    """
    Provides UnitOfWork via async context manager for automatic transaction management.
    
    The context manager automatically commits on success or rolls back on exception.
    Usage: uow: UnitOfWork = Depends(get_unit_of_work_provider())
    """
    @asynccontextmanager
    async def _provider(session=Depends(get_db_session)) -> AsyncGenerator[UnitOfWork, None]:
        """
        Context manager that yields a UnitOfWork for the request.
        Transaction is committed on success, rolled back on exception.
        """
        with UnitOfWork(session) as uow:
            yield uow
    
    return _provider
