import pytest
import uuid
from unittest.mock import MagicMock
from scheduler_api.repositories.shift_repository import ShiftRepository
from scheduler_api.models import Shift


@pytest.fixture
def mock_session():
    # Create a MagicMock that acts as a Session
    session = MagicMock()
    # Context manager support for `with`
    session.__enter__.return_value = session
    session.__exit__.return_value = None
    return session


@pytest.fixture
def repo(mock_session):
    return ShiftRepository(session=mock_session)


def test_get_all(repo, mock_session):
    testID1 = uuid.uuid4()
    testID2 = uuid.uuid4()

    fake_shifts = [Shift(id=testID1), Shift(id=testID2)]
    mock_session.query.return_value.all.return_value = fake_shifts

    result = repo.get_all()

    mock_session.query.assert_called_once_with(Shift)
    mock_session.query.return_value.all.assert_called_once()
    assert result == fake_shifts


def test_get_by_id(repo, mock_session):
    testID = uuid.uuid4()

    shift = Shift(id=testID)
    mock_session.get.return_value = shift

    result = repo.get_by_id(testID)

    mock_session.get.assert_called_once_with(Shift, testID)
    assert result == shift


def test_add(repo, mock_session):
    testID = uuid.uuid4()

    shift = Shift(id=testID)
    mock_session.add.return_value = None
    mock_session.commit.return_value = None
    mock_session.refresh.return_value = None

    result = repo.add(shift)

    mock_session.add.assert_called_once_with(shift)
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(shift)
    assert result == shift


def test_update_existing_shift(repo, mock_session):
    # Existing shift in "DB"
    testID = uuid.uuid4()
    existing = Shift(id=testID, location="here")
    mock_session.get.return_value = existing

    # Shift to update
    updated = Shift(
        id=testID, location="there"
    )  # just set the new values on the test object

    result = repo.update(updated)

    mock_session.get.assert_called_once_with(Shift, testID)
    assert existing.location == "there"  # updated in-place
    mock_session.add.assert_called_once_with(existing)
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(existing)
    assert result == existing


def test_update_nonexistent_shift(repo, mock_session):
    mock_session.get.return_value = None
    testID = uuid.uuid4()

    shift = Shift(id=testID)

    result = repo.update(shift)

    mock_session.get.assert_called_once_with(Shift, testID)
    assert result is None
    mock_session.add.assert_not_called()
    mock_session.commit.assert_not_called()
    mock_session.refresh.assert_not_called()


def test_delete_existing_shift(repo, mock_session):
    testID = uuid.uuid4()
    shift = Shift(id=testID)
    mock_session.get.return_value = shift

    result = repo.delete(testID)

    mock_session.get.assert_called_once_with(Shift, testID)
    mock_session.delete.assert_called_once_with(shift)
    mock_session.commit.assert_called_once()
    assert result is True


def test_delete_nonexistent_shift(repo, mock_session):
    testID = uuid.uuid4()

    mock_session.get.return_value = None

    result = repo.delete(testID)

    mock_session.get.assert_called_once_with(Shift, testID)
    mock_session.delete.assert_not_called()
    mock_session.commit.assert_not_called()
    assert result is False
