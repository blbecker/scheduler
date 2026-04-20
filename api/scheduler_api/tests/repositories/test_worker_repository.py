import pytest
import uuid
from unittest.mock import MagicMock
from scheduler_api.repositories.worker_repository import WorkerRepository
from scheduler_api.models import Worker


@pytest.fixture
def mock_session_worker():
    session = MagicMock()
    session.__enter__.return_value = session
    session.__exit__.return_value = None
    return session


@pytest.fixture
def repo_worker(mock_session_worker):
    return WorkerRepository(session=mock_session_worker)


def test_worker_get_all(repo_worker, mock_session_worker):
    testID1 = uuid.uuid4()
    testID2 = uuid.uuid4()
    fake_workers = [Worker(id=testID1), Worker(id=testID2)]
    mock_session_worker.query.return_value.all.return_value = fake_workers

    result = repo_worker.get_all()

    mock_session_worker.query.assert_called_once_with(Worker)
    mock_session_worker.query.return_value.all.assert_called_once()
    assert result == fake_workers


def test_worker_get_by_id(repo_worker, mock_session_worker):
    testID = uuid.uuid4()
    worker = Worker(id=testID)
    mock_session_worker.get.return_value = worker

    result = repo_worker.get_by_id(testID)

    mock_session_worker.get.assert_called_once_with(Worker, testID)
    assert result == worker


def test_worker_add(repo_worker, mock_session_worker):
    testID = uuid.uuid4()
    worker = Worker(id=testID)

    result = repo_worker.add(worker)

    mock_session_worker.add.assert_called_once_with(worker)
    mock_session_worker.commit.assert_called_once()
    mock_session_worker.refresh.assert_called_once_with(worker)
    assert result == worker


def test_worker_update_existing(repo_worker, mock_session_worker):
    testID = uuid.uuid4()
    existing = Worker(id=testID, name="old")
    mock_session_worker.get.return_value = existing

    updated = Worker(id=testID, name="new")

    result = repo_worker.update(updated)

    mock_session_worker.get.assert_called_once_with(Worker, testID)
    assert existing.name == "new"
    mock_session_worker.add.assert_called_once_with(existing)
    mock_session_worker.commit.assert_called_once()
    mock_session_worker.refresh.assert_called_once_with(existing)
    assert result == existing


def test_worker_update_nonexistent(repo_worker, mock_session_worker):
    testID = uuid.uuid4()
    mock_session_worker.get.return_value = None
    worker = Worker(id=testID)

    result = repo_worker.update(worker)

    mock_session_worker.get.assert_called_once_with(Worker, testID)
    assert result is None
    mock_session_worker.add.assert_not_called()
    mock_session_worker.commit.assert_not_called()
    mock_session_worker.refresh.assert_not_called()


def test_worker_delete_existing(repo_worker, mock_session_worker):
    testID = uuid.uuid4()
    worker = Worker(id=testID)
    mock_session_worker.get.return_value = worker

    result = repo_worker.delete(testID)

    mock_session_worker.get.assert_called_once_with(Worker, testID)
    mock_session_worker.delete.assert_called_once_with(worker)
    mock_session_worker.commit.assert_called_once()
    assert result is True


def test_worker_delete_nonexistent(repo_worker, mock_session_worker):
    testID = uuid.uuid4()
    mock_session_worker.get.return_value = None

    result = repo_worker.delete(testID)

    mock_session_worker.get.assert_called_once_with(Worker, testID)
    mock_session_worker.delete.assert_not_called()
    mock_session_worker.commit.assert_not_called()
    assert result is False
