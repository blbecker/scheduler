import pytest
from unittest.mock import MagicMock
from uuid import UUID
from datetime import date
from scheduler_api.models import Shift
from scheduler_api.services.shift_service import ShiftService


@pytest.fixture
def mock_shift_repo():
    return MagicMock()


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


def test_shift_service_get_by_id(mock_shift_repo):
    # Setup
    shift_id = UUID(int=1)
    expected_shift = Shift(id=shift_id, name="John Doe")
    mock_shift_repo.get_by_id.return_value = expected_shift
    service = ShiftService(mock_shift_repo)

    # Test
    result = service.get_shift(shift_id)

    # Verify
    mock_shift_repo.get_by_id.assert_called_once_with(shift_id)
    assert result == expected_shift


def test_add_shift(mock_shift_repo):

    # Setup
    shift_id = UUID(int=1)
    expected_shift = Shift(id=shift_id, name="John Doe", birthdate=date(1990, 1, 1))
    mock_shift_repo.add.return_value = expected_shift
    service = ShiftService(mock_shift_repo)

    # Test
    service.create_shift(expected_shift)

    # Verify
    mock_shift_repo.add.assert_called_once_with(expected_shift)


# def test_update_shift(mock_shift_repo):
#
#     # Setup
#     shift_id = UUID(int=1)
#     expected_shift = Shift(id=shift_id, name="John Doe", birthdate=date(1990, 1, 1))
#     mock_shift_repo.update.return_value = expected_shift
#     service = ShiftService(mock_shift_repo)
#
#     # Test
#     service.update_shift(expected_shift)
#
#     # Verify
#     mock_shift_repo.update.assert_called_once_with(expected_shift)
