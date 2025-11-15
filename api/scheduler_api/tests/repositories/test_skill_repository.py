import pytest
import uuid
from unittest.mock import MagicMock
from scheduler_api.repositories.skill_repository import SkillRepository
from scheduler_api.models import Skill


@pytest.fixture
def mock_session_skill():
    session = MagicMock()
    session.__enter__.return_value = session
    session.__exit__.return_value = None
    return session


@pytest.fixture
def repo_skill(mock_session_skill):
    return SkillRepository(session=mock_session_skill)


def test_skill_get_all(repo_skill, mock_session_skill):
    testID1 = uuid.uuid4()
    testID2 = uuid.uuid4()
    fake_skills = [Skill(id=testID1), Skill(id=testID2)]
    mock_session_skill.query.return_value.all.return_value = fake_skills

    result = repo_skill.get_all()

    mock_session_skill.query.assert_called_once_with(Skill)
    mock_session_skill.query.return_value.all.assert_called_once()
    assert result == fake_skills


def test_skill_get_by_id(repo_skill, mock_session_skill):
    testID = uuid.uuid4()
    skill = Skill(id=testID)
    mock_session_skill.get.return_value = skill

    result = repo_skill.get_by_id(testID)

    mock_session_skill.get.assert_called_once_with(Skill, testID)
    assert result == skill


def test_skill_add(repo_skill, mock_session_skill):
    testID = uuid.uuid4()
    skill = Skill(id=testID)

    result = repo_skill.add(skill)

    mock_session_skill.add.assert_called_once_with(skill)
    mock_session_skill.commit.assert_called_once()
    mock_session_skill.refresh.assert_called_once_with(skill)
    assert result == skill


def test_skill_update_existing(repo_skill, mock_session_skill):
    testID = uuid.uuid4()
    existing = Skill(id=testID, name="old")
    mock_session_skill.get.return_value = existing

    updated = Skill(id=testID, name="new")

    result = repo_skill.update(updated)

    mock_session_skill.get.assert_called_once_with(Skill, testID)
    assert existing.name == "new"
    mock_session_skill.add.assert_called_once_with(existing)
    mock_session_skill.commit.assert_called_once()
    mock_session_skill.refresh.assert_called_once_with(existing)
    assert result == existing


def test_skill_update_nonexistent(repo_skill, mock_session_skill):
    testID = uuid.uuid4()
    mock_session_skill.get.return_value = None
    skill = Skill(id=testID)

    result = repo_skill.update(skill)

    mock_session_skill.get.assert_called_once_with(Skill, testID)
    assert result is None
    mock_session_skill.add.assert_not_called()
    mock_session_skill.commit.assert_not_called()
    mock_session_skill.refresh.assert_not_called()


def test_skill_delete_existing(repo_skill, mock_session_skill):
    testID = uuid.uuid4()
    skill = Skill(id=testID)
    mock_session_skill.get.return_value = skill

    result = repo_skill.delete(testID)

    mock_session_skill.get.assert_called_once_with(Skill, testID)
    mock_session_skill.delete.assert_called_once_with(skill)
    mock_session_skill.commit.assert_called_once()
    assert result is True


def test_skill_delete_nonexistent(repo_skill, mock_session_skill):
    testID = uuid.uuid4()
    mock_session_skill.get.return_value = None

    result = repo_skill.delete(testID)

    mock_session_skill.get.assert_called_once_with(Skill, testID)
    mock_session_skill.delete.assert_not_called()
    mock_session_skill.commit.assert_not_called()
    assert result is False
