import pytest
from unittest.mock import MagicMock
from uuid import UUID
from datetime import date
from scheduler_api.models import Skill
from scheduler_api.services.skill_service import SkillService


@pytest.fixture
def mock_skill_repo():
    return MagicMock()


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


def test_skill_service_get_by_id(mock_skill_repo):
    # Setup
    skill_id = UUID(int=1)
    expected_skill = Skill(id=skill_id, name="John Doe")
    mock_skill_repo.get_by_id.return_value = expected_skill
    service = SkillService(mock_skill_repo)

    # Test
    result = service.get_skill(skill_id)

    # Verify
    mock_skill_repo.get_by_id.assert_called_once_with(skill_id)
    assert result == expected_skill


def test_add_skill(mock_skill_repo):

    # Setup
    skill_id = UUID(int=1)
    expected_skill = Skill(id=skill_id, name="John Doe", birthdate=date(1990, 1, 1))
    mock_skill_repo.add.return_value = expected_skill
    service = SkillService(mock_skill_repo)

    # Test
    service.create_skill(expected_skill)

    # Verify
    mock_skill_repo.add.assert_called_once_with(expected_skill)


# def test_update_skill(mock_skill_repo):
#
#     # Setup
#     skill_id = UUID(int=1)
#     expected_skill = Skill(id=skill_id, name="John Doe", birthdate=date(1990, 1, 1))
#     mock_skill_repo.update.return_value = expected_skill
#     service = SkillService(mock_skill_repo)
#
#     # Test
#     service.update_skill(expected_skill)
#
#     # Verify
#     mock_skill_repo.update.assert_called_once_with(expected_skill)
