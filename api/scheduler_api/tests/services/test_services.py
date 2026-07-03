"""Test Worker, Skill, and Shift services with UnitOfWork pattern."""

import pytest
from unittest.mock import MagicMock, patch
from uuid import UUID
from datetime import date, datetime
from scheduler_api.db.models.core.worker import Worker
from scheduler_api.db.models.core.skill import Skill
from scheduler_api.db.models.schedules.shift import Shift
from scheduler_api.services.worker_service import WorkerService
from scheduler_api.services.skill_service import SkillService
from scheduler_api.services.shift_service import ShiftService
from scheduler_api.uow.unit_of_work import UnitOfWork
from scheduler_api.schemas.worker import WorkerResponse
from scheduler_api.schemas.skill import SkillResponse
from scheduler_api.schemas.shift import ShiftResponse


@pytest.fixture
def mock_uow():
    uow = MagicMock(spec=UnitOfWork)
    uow.session = MagicMock()
    uow.flush = MagicMock()
    return uow


def test_worker_service_get_all(mock_uow):
    # Setup
    worker_model = Worker(id=UUID(int=1), name="John Doe")
    expected_response = WorkerResponse(
        id=UUID(int=1),
        name="John Doe",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    mock_repo = MagicMock()
    mock_repo.get_all.return_value = [worker_model]
    
    # Patch the repository constructor to return our mock
    with patch('scheduler_api.services.worker_service.WorkerRepository', return_value=mock_repo):
        service = WorkerService(mock_uow)
        
        # Test
        result = service.list_workers()
    
    # Verify
    mock_repo.get_all.assert_called_once()
    assert len(result) == 1
    assert result[0].id == expected_response.id
    assert result[0].name == expected_response.name


def test_worker_service_get_by_id(mock_uow):
    # Setup
    worker_id = UUID(int=1)
    worker_model = Worker(id=worker_id, name="John Doe")
    expected_response = WorkerResponse(
        id=worker_id,
        name="John Doe",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    mock_repo = MagicMock()
    mock_repo.get_by_id.return_value = worker_model
    
    # Patch the repository constructor to return our mock
    with patch('scheduler_api.services.worker_service.WorkerRepository', return_value=mock_repo):
        service = WorkerService(mock_uow)
        
        # Test
        result = service.get_worker(worker_id)
    
    # Verify
    mock_repo.get_by_id.assert_called_once_with(worker_id)
    assert result.id == expected_response.id
    assert result.name == expected_response.name


def test_skill_service_get_all(mock_uow):
    # Setup
    skill_model = Skill(id=UUID(int=1), name="Python", description="Python programming")
    expected_response = SkillResponse(
        id=UUID(int=1),
        name="Python",
        description="Python programming",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    mock_repo = MagicMock()
    mock_repo.get_all.return_value = [skill_model]
    
    # Patch the repository constructor to return our mock
    with patch('scheduler_api.services.skill_service.SkillRepository', return_value=mock_repo):
        service = SkillService(mock_uow)
        
        # Test
        result = service.list_skills()
    
    # Verify
    mock_repo.get_all.assert_called_once()
    assert len(result) == 1
    assert result[0].id == expected_response.id
    assert result[0].name == expected_response.name


def test_shift_service_get_all(mock_uow):
    # Setup
    shift_model = Shift(
        id=UUID(int=1),
        name="Morning Shift",
        start_time=datetime(2024, 1, 1, 9, 0, 0),
        end_time=datetime(2024, 1, 1, 17, 0, 0),
        schedule_id=UUID(int=2),
        shift_template_id=UUID(int=3),
    )
    expected_response = ShiftResponse(
        id=UUID(int=1),
        name="Morning Shift",
        start_time=datetime(2024, 1, 1, 9, 0, 0),
        end_time=datetime(2024, 1, 1, 17, 0, 0),
        schedule_id=UUID(int=2),
        shift_template_id=UUID(int=3),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    mock_repo = MagicMock()
    mock_repo.get_all.return_value = [shift_model]
    
    # Patch the repository constructor to return our mock
    with patch('scheduler_api.services.shift_service.ShiftRepository', return_value=mock_repo):
        service = ShiftService(mock_uow)
        
        # Test
        result = service.list_shifts()
    
    # Verify
    mock_repo.get_all.assert_called_once()
    assert len(result) == 1
    assert result[0].id == expected_response.id
    assert result[0].name == expected_response.name
    assert result[0].start_time == expected_response.start_time
    assert result[0].end_time == expected_response.end_time
