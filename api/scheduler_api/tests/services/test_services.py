import pytest
from unittest.mock import MagicMock
from uuid import UUID
from datetime import date, datetime
from scheduler_api.db.models import Worker, Skill, Shift
from scheduler_api.services.worker_service import WorkerService
from scheduler_api.services.skill_service import SkillService
from scheduler_api.services.shift_service import ShiftService
from scheduler_api.schemas.worker import WorkerResponse
from scheduler_api.schemas.skill import SkillResponse
from scheduler_api.schemas.shift import ShiftResponse


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
    worker_model = Worker(id=UUID(int=1), name="John Doe", birthdate=date(1990, 1, 1))
    expected_response = WorkerResponse(
        id=UUID(int=1),
        name="John Doe",
        birthdate=date(1990, 1, 1),
        email=None,
        phone=None,
    )
    mock_worker_repo.get_all.return_value = [worker_model]
    service = WorkerService(mock_worker_repo)

    # Test
    result = service.list_workers()

    # Verify
    mock_worker_repo.get_all.assert_called_once()
    assert len(result) == 1
    assert result[0].id == expected_response.id
    assert result[0].name == expected_response.name
    assert result[0].birthdate == expected_response.birthdate


def test_worker_service_get_by_id(mock_worker_repo):
    # Setup
    worker_id = UUID(int=1)
    worker_model = Worker(id=worker_id, name="John Doe", birthdate=date(1990, 1, 1))
    expected_response = WorkerResponse(
        id=worker_id,
        name="John Doe",
        birthdate=date(1990, 1, 1),
        email=None,
        phone=None,
    )
    mock_worker_repo.get_by_id.return_value = worker_model
    service = WorkerService(mock_worker_repo)

    # Test
    result = service.get_worker(worker_id)

    # Verify
    mock_worker_repo.get_by_id.assert_called_once_with(worker_id)
    assert result.id == expected_response.id
    assert result.name == expected_response.name
    assert result.birthdate == expected_response.birthdate


def test_skill_service_get_all(mock_skill_repo):
    # Setup
    skill_model = Skill(id=UUID(int=1), name="Python")
    expected_response = SkillResponse(id=UUID(int=1), name="Python")
    mock_skill_repo.get_all.return_value = [skill_model]
    service = SkillService(mock_skill_repo)

    # Test
    result = service.list_skills()

    # Verify
    mock_skill_repo.get_all.assert_called_once()
    assert len(result) == 1
    assert result[0].id == expected_response.id
    assert result[0].name == expected_response.name


def test_shift_service_get_all(mock_shift_repo):
    # Setup
    shift_model = Shift(
        id=UUID(int=1),
        start_time=datetime(2024, 1, 1, 9, 0, 0),
        end_time=datetime(2024, 1, 1, 17, 0, 0),
        location="Office",
        notes="Test shift",
    )
    expected_response = ShiftResponse(
        id=UUID(int=1),
        start_time=datetime(2024, 1, 1, 9, 0, 0),
        end_time=datetime(2024, 1, 1, 17, 0, 0),
        location="Office",
        notes="Test shift",
    )
    mock_shift_repo.get_all.return_value = [shift_model]
    service = ShiftService(mock_shift_repo)

    # Test
    result = service.list_shifts()

    # Verify
    mock_shift_repo.get_all.assert_called_once()
    assert len(result) == 1
    assert result[0].id == expected_response.id
    assert result[0].start_time == expected_response.start_time
    assert result[0].end_time == expected_response.end_time
