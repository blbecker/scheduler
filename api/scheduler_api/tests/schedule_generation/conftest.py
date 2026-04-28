import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from uuid import uuid4


from scheduler_api.schemas.ga_dtos import (
    ScheduleLayoutDTO,
    ScheduleDTO,
    PopulationDTO,
    ShiftAssignmentDTO,
)
from scheduler_api.domain.schedule import Schedule, ShiftAssignment
from scheduler_api.domain.population import Population
from scheduler_api.domain.schedule_layout import ScheduleLayout


@pytest.fixture
def mock_time_sleep():
    """Mock time.sleep to speed up tests."""
    with patch("time.sleep") as mock_sleep:
        yield mock_sleep


@pytest.fixture
def mock_random_uniform():
    """Mock random.uniform for deterministic tests."""
    with patch("random.uniform") as mock_uniform:
        mock_uniform.return_value = 0.5
        yield mock_uniform


@pytest.fixture
def mock_random_random():
    """Mock random.random for deterministic tests."""
    with patch("random.random") as mock_random:
        mock_random.return_value = 0.5
        yield mock_random


@pytest.fixture
def sample_shift_assignment_dto():
    """Create a sample ShiftAssignmentDTO for testing."""
    return ShiftAssignmentDTO(
        worker_id=uuid4(),
        shift_id=uuid4(),
        start_time=datetime.utcnow(),
        end_time=datetime.utcnow() + timedelta(hours=8),
    )


@pytest.fixture
def sample_schedule_dto(sample_shift_assignment_dto):
    """Create a sample ScheduleDTO for testing."""
    return ScheduleDTO(
        id=uuid4(),
        name="Test Schedule",
        assignments=[sample_shift_assignment_dto],
        fitness=0.8,
        created_at=datetime.utcnow(),
    )


@pytest.fixture
def sample_schedule_layout_dto():
    """Create a sample ScheduleLayoutDTO for testing."""
    return ScheduleLayoutDTO(
        id=uuid4(),
        name="Test Layout",
        date_range_start=datetime.utcnow(),
        date_range_end=datetime.utcnow() + timedelta(days=7),
        worker_ids=[uuid4() for _ in range(5)],
        shift_templates=[
            {"id": str(uuid4()), "name": "Morning", "start_hour": 8, "end_hour": 16},
            {"id": str(uuid4()), "name": "Evening", "start_hour": 16, "end_hour": 24},
        ],
        constraints={"max_hours_per_week": 40, "min_rest_hours": 12},
        created_at=datetime.utcnow(),
    )


@pytest.fixture
def sample_population_dto(sample_schedule_dto, sample_schedule_layout_dto):
    """Create a sample PopulationDTO for testing."""
    return PopulationDTO(
        id=uuid4(),
        generation=1,
        schedules=[sample_schedule_dto],
        layout_id=sample_schedule_layout_dto.id,
        created_at=datetime.utcnow(),
    )


@pytest.fixture
def sample_shift_assignment():
    """Create a sample ShiftAssignment domain object for testing."""
    return ShiftAssignment(
        worker_id=uuid4(),
        shift_id=uuid4(),
        start_time=datetime.utcnow(),
        end_time=datetime.utcnow() + timedelta(hours=8),
    )


@pytest.fixture
def sample_schedule(sample_shift_assignment):
    """Create a sample Schedule domain object for testing."""
    return Schedule(
        id=uuid4(),
        name="Test Schedule",
        assignments=[sample_shift_assignment],
        fitness=0.8,
    )


@pytest.fixture
def sample_schedule_layout():
    """Create a sample ScheduleLayout domain object for testing."""
    return ScheduleLayout(
        id=uuid4(),
        name="Test Layout",
        date_range_start=datetime.utcnow(),
        date_range_end=datetime.utcnow() + timedelta(days=7),
        worker_ids=[uuid4() for _ in range(5)],
        shift_templates=[
            {"id": str(uuid4()), "name": "Morning", "start_hour": 8, "end_hour": 16},
            {"id": str(uuid4()), "name": "Evening", "start_hour": 16, "end_hour": 24},
        ],
        constraints={"max_hours_per_week": 40, "min_rest_hours": 12},
    )


@pytest.fixture
def sample_population(sample_schedule, sample_schedule_layout):
    """Create a sample Population domain object for testing."""
    return Population(
        id=uuid4(),
        generation=1,
        schedules=[sample_schedule],
        layout_id=sample_schedule_layout.id,
    )


@pytest.fixture
def celery_app():
    """Create a test Celery app."""
    from celery import Celery

    # Use the test configuration
    app = Celery("test_scheduler_api")
    app.conf.update(
        task_always_eager=True,  # Run tasks synchronously for testing
        task_eager_propagates=True,  # Propagate exceptions
        broker_url="memory://",  # In-memory broker for testing
        result_backend="cache+memory://",  # In-memory result backend
    )

    # Autodiscover tasks
    app.autodiscover_tasks(packages=["scheduler_api"])

    return app


@pytest.fixture
def mock_celery_chain():
    """Mock celery.chain for testing orchestration."""
    with patch("scheduler_api.tasks.ga_tasks.chain") as mock_chain:
        mock_chain_instance = Mock()
        mock_chain.return_value = mock_chain_instance
        mock_chain_instance.return_value = Mock(get=lambda: {"test": "result"})
        yield mock_chain
