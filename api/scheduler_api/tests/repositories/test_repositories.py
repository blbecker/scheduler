import pytest
from unittest.mock import MagicMock, patch
from uuid import UUID
from datetime import date
from sqlmodel import Session
from scheduler_api.models import Worker, Skill, Shift
from scheduler_api.repositories.worker_repository import WorkerRepository
from scheduler_api.repositories.skill_repository import SkillRepository
from scheduler_api.repositories.shift_repository import ShiftRepository


@pytest.fixture
def mock_session():
    return MagicMock(spec=Session)


@pytest.fixture
def worker_repo(mock_session):
    return WorkerRepository()


@pytest.fixture
def skill_repo(mock_session):
    return SkillRepository()


@pytest.fixture
def shift_repo(mock_session):
    return ShiftRepository()


def test_worker_repository_get_all(worker_repo, mock_session):
    # Setup
    expected_workers = [
        Worker(id=UUID(int=1), name="John Doe", birthdate=date(1990, 1, 1))
    ]
    mock_session.query.return_value.all.return_value = expected_workers

    # Test
    with patch("scheduler_api.db.get_session", return_value=mock_session):
        result = worker_repo.get_all()

    # Verify
    mock_session.query.assert_called_once_with(Worker)
    assert result == expected_workers


def test_worker_repository_get_by_id(worker_repo, mock_session):
    # Setup
    worker_id = UUID(int=1)
    expected_worker = Worker(id=worker_id, name="John Doe", birthdate=date(1990, 1, 1))
    mock_session.get.return_value = expected_worker

    # Test
    with patch("scheduler_api.db.get_session", return_value=mock_session):
        result = worker_repo.get_by_id(worker_id)

    # Verify
    mock_session.get.assert_called_once_with(Worker, worker_id)
    assert result == expected_worker


def test_worker_repository_add(worker_repo, mock_session):
    # Setup
    worker = Worker(name="John Doe", birthdate=date(1990, 1, 1))

    # Test
    with patch("scheduler_api.db.get_session", return_value=mock_session):
        result = worker_repo.add(worker)

    # Verify
    mock_session.add.assert_called_once_with(worker)
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(worker)
    assert result == worker


def test_worker_repository_update(worker_repo, mock_session):
    # Setup
    worker_id = UUID(int=1)
    existing_worker = Worker(id=worker_id, name="John Doe", birthdate=date(1990, 1, 1))
    updated_worker = Worker(id=worker_id, name="Jane Doe", birthdate=date(1990, 1, 1))
    mock_session.get.return_value = existing_worker

    # Test
    with patch("scheduler_api.db.get_session", return_value=mock_session):
        result = worker_repo.update(updated_worker)

    # Verify
    mock_session.get.assert_called_once_with(Worker, worker_id)
    mock_session.add.assert_called_once_with(existing_worker)
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(existing_worker)
    assert result == existing_worker
    assert existing_worker.name == "Jane Doe"


def test_worker_repository_delete(worker_repo, mock_session):
    # Setup
    worker_id = UUID(int=1)
    worker = Worker(id=worker_id, name="John Doe", birthdate=date(1990, 1, 1))
    mock_session.get.return_value = worker

    # Test
    with patch("scheduler_api.db.get_session", return_value=mock_session):
        result = worker_repo.delete(worker_id)

    # Verify
    mock_session.get.assert_called_once_with(Worker, worker_id)
    mock_session.delete.assert_called_once_with(worker)
    mock_session.commit.assert_called_once()
    assert result is True


# Similar tests for SkillRepository and ShiftRepository
def test_skill_repository_get_all(skill_repo, mock_session):
    # Setup
    expected_skills = [Skill(id=UUID(int=1), name="Python")]
    mock_session.exec.return_value.all.return_value = expected_skills

    # Test
    with patch("scheduler_api.db.get_session", return_value=mock_session):
        result = skill_repo.get_all()

    # Verify
    mock_session.exec.assert_called_once()
    assert result == expected_skills


def test_shift_repository_get_all(shift_repo, mock_session):
    # Setup
    expected_shifts = [Shift(id=UUID(int=1), name="Morning Shift")]
    mock_session.exec.return_value.all.return_value = expected_shifts

    # Test
    with patch("scheduler_api.db.get_session", return_value=mock_session):
        result = shift_repo.get_all()

    # Verify
    mock_session.exec.assert_called_once()
    assert result == expected_shifts
