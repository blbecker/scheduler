import pytest
from unittest.mock import MagicMock, patch
from uuid import UUID
from datetime import date
from scheduler_api.models import Worker, Skill, Shift
from scheduler_api.services.worker_service import WorkerService
from scheduler_api.services.skill_service import SkillService
from scheduler_api.services.shift_service import ShiftService


@pytest.fixture
def mock_worker_repo():
    return MagicMock()


@pytest.fixture
def mock_skill_repo():
    return MagicMock()


@pytest.fixture
def mock_shift_repo():
    return MagicMock()


def test_worker_service_get_all(mock_worker_repo):
    # Setup
    expected_workers = [
        Worker(id=UUID(int=1), name="John Doe", birthdate=date(1990, 1, 1))
    ]
    mock_worker_repo.get_all.return_value = expected_workers
    service = WorkerService(mock_worker_repo)

    # Test
    result = service.list_workers()

    # Verify
    mock_worker_repo.get_all.assert_called_once()
    assert result == expected_workers


def test_worker_service_get_by_id(mock_worker_repo):
    # Setup
    worker_id = UUID(int=1)
    expected_worker = Worker(id=worker_id, name="John Doe", birthdate=date(1990, 1, 1))
    mock_worker_repo.get_by_id.return_value = expected_worker
    service = WorkerService(mock_worker_repo)

    # Test
    result = service.get_worker(worker_id)

    # Verify
    mock_worker_repo.get_by_id.assert_called_once_with(worker_id)
    assert result == expected_worker


def test_skill_service_get_all(mock_skill_repo):
    # Setup
    expected_skills = [Skill(id=UUID(int=1), name="Python")]
    mock_skill_repo.get_all.return_value = expected_skills
    service = SkillService(mock_skill_repo)

    # Test
    result = service.list_skills()

    # Verify
    mock_skill_repo.get_all.assert_called_once()
    assert result == expected_skills


def test_shift_service_get_all(mock_shift_repo):
    # Setup
    expected_shifts = [Shift(id=UUID(int=1), name="Morning Shift")]
    mock_shift_repo.get_all.return_value = expected_shifts
    service = ShiftService(mock_shift_repo)

    # Test
    result = service.list_shifts()

    # Verify
    mock_shift_repo.get_all.assert_called_once()
    assert result == expected_shifts
