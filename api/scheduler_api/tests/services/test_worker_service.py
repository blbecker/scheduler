import pytest
from unittest.mock import MagicMock
from uuid import UUID
from datetime import date
from scheduler_api.models import Worker
from scheduler_api.services.worker_service import WorkerService


@pytest.fixture
def mock_worker_repo():
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


def test_delete_worker(mock_worker_repo):

    # Setup
    worker_id = UUID(int=1)
    mock_worker_repo.delete.return_value = True
    service = WorkerService(mock_worker_repo)

    # Test
    service.delete_worker(worker_id)

    # Verify
    mock_worker_repo.delete.assert_called_once_with(worker_id)


def test_add_worker(mock_worker_repo):

    # Setup
    worker_id = UUID(int=1)
    expected_worker = Worker(id=worker_id, name="John Doe", birthdate=date(1990, 1, 1))
    mock_worker_repo.add.return_value = expected_worker
    service = WorkerService(mock_worker_repo)

    # Test
    service.create_worker(expected_worker)

    # Verify
    mock_worker_repo.add.assert_called_once_with(expected_worker)


def test_update_worker(mock_worker_repo):

    # Setup
    worker_id = UUID(int=1)
    expected_worker = Worker(id=worker_id, name="John Doe", birthdate=date(1990, 1, 1))
    mock_worker_repo.update.return_value = expected_worker
    service = WorkerService(mock_worker_repo)

    # Test
    service.update_worker(expected_worker)

    # Verify
    mock_worker_repo.update.assert_called_once_with(expected_worker)
