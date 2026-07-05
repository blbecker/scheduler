from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import Depends
from sqlmodel import Session

from scheduler_api.db.session import engine
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


# -----------------------------
# DB Session Dependency
# -----------------------------
def get_db_session():
    """
    Provides a SQLModel session per request.
    """
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()


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



