"""Test service implementations with UnitOfWork."""

import pytest
from unittest.mock import MagicMock, patch
from uuid import UUID, uuid4
from datetime import datetime, time
from fastapi import HTTPException, status

from scheduler_api.uow.unit_of_work import UnitOfWork
from scheduler_api.services.schedule_template_service import ScheduleTemplateService
from scheduler_api.services.shift_template_service import ShiftTemplateService
from scheduler_api.services.schedule_service import ScheduleService
from scheduler_api.services.schedule_generation_run_service import (
    ScheduleGenerationRunService,
)
from scheduler_api.services.shift_service import ShiftService
from scheduler_api.services.skill_service import SkillService
from scheduler_api.services.worker_service import WorkerService

from scheduler_api.schemas.schedule_template import (
    ScheduleTemplate,
    ScheduleTemplateUpdate,
    ScheduleTemplateResponse,
)
from scheduler_api.schemas.shift_template import (
    ShiftTemplate,
    ShiftTemplateUpdate,
    ShiftTemplateResponse,
)
from scheduler_api.schemas.schedule_crud import (
    Schedule,
    ScheduleUpdate,
    ScheduleResponse,
)
from scheduler_api.schemas.schedule_generation_run import (
    ScheduleGenerationRun,
    ScheduleGenerationRunUpdate,
    ScheduleGenerationRunResponse,
)
from scheduler_api.schemas.shift import Shift, ShiftUpdate, ShiftResponse
from scheduler_api.schemas.skill import Skill, SkillUpdate, SkillResponse
from scheduler_api.schemas.worker import Worker, WorkerUpdate, WorkerResponse

from scheduler_api.db.models.templates.schedule_template import ScheduleTemplateModel
from scheduler_api.db.models.templates.shift_template import ShiftTemplateModel
from scheduler_api.db.models.schedules.schedule import ScheduleModel
from scheduler_api.db.models.schedules.shift import ShiftModel
from scheduler_api.db.models.core.skill import SkillModel
from scheduler_api.db.models.core.worker import WorkerModel
from scheduler_api.db.models.runs.schedule_generation_run import (
    ScheduleGenerationRunModel,
)
from scheduler_api.db.models.enums import ScheduleGenerationStatus


class TestScheduleTemplateServiceUOW:
    """Test ScheduleTemplateService with UnitOfWork."""

    @pytest.fixture
    def mock_uow(self):
        uow = MagicMock(spec=UnitOfWork)
        uow.session = MagicMock()
        uow.flush = MagicMock()
        return uow

    @pytest.fixture
    def mock_repo(self):
        repo = MagicMock()
        repo.get_all = MagicMock()
        repo.get_by_id = MagicMock()
        repo.add = MagicMock()
        repo.delete = MagicMock()
        return repo

    @pytest.fixture
    def service(self, mock_uow):
        return ScheduleTemplateService(mock_uow)

    @pytest.fixture
    def sample_template_model(self):
        template = MagicMock()
        template.id = uuid4()
        template.name = "Weekly Schedule"
        template.created_at = datetime.now()
        template.updated_at = datetime.now()
        return template

    @pytest.fixture
    def sample_template_response(self, sample_template_model):
        return ScheduleTemplateResponse(
            id=sample_template_model.id,
            name=sample_template_model.name,
            created_at=sample_template_model.created_at,
            updated_at=sample_template_model.updated_at,
        )

    def test_list_schedule_templates(
        self,
        service,
        mock_uow,
        mock_repo,
        sample_template_model,
        sample_template_response,
    ):
        # Setup
        with patch(
            "scheduler_api.services.schedule_template_service.ScheduleTemplateRepository",
            return_value=mock_repo,
        ):
            mock_repo.get_all.return_value = [sample_template_model]

            # Test
            result = service.list_schedule_templates()

            # Verify
            mock_repo.get_all.assert_called_once()
            assert len(result) == 1
            assert result[0].id == sample_template_response.id
            assert result[0].name == sample_template_response.name

    def test_get_schedule_template(
        self,
        service,
        mock_uow,
        mock_repo,
        sample_template_model,
        sample_template_response,
    ):
        # Setup
        with patch(
            "scheduler_api.services.schedule_template_service.ScheduleTemplateRepository",
            return_value=mock_repo,
        ):
            template_id = sample_template_model.id
            mock_repo.get_by_id.return_value = sample_template_model

            # Test
            result = service.get_schedule_template(template_id)

            # Verify
            mock_repo.get_by_id.assert_called_once_with(template_id)
            assert result.id == sample_template_response.id
            assert result.name == sample_template_response.name

    def test_get_schedule_template_not_found(self, service, mock_uow, mock_repo):
        # Setup
        with patch(
            "scheduler_api.services.schedule_template_service.ScheduleTemplateRepository",
            return_value=mock_repo,
        ):
            template_id = uuid4()
            mock_repo.get_by_id.return_value = None

            # Test & Verify
            with pytest.raises(HTTPException) as exc_info:
                service.get_schedule_template(template_id)

            assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
            mock_repo.get_by_id.assert_called_once_with(template_id)

    def test_create_schedule_template(
        self,
        service,
        mock_uow,
        mock_repo,
        sample_template_model,
        sample_template_response,
    ):
        # Setup
        with patch(
            "scheduler_api.services.schedule_template_service.ScheduleTemplateRepository",
            return_value=mock_repo,
        ):
            create_dto = ScheduleTemplate(name="Weekly Schedule")
            mock_repo.add.return_value = sample_template_model

            # Test
            result = service.create_schedule_template(create_dto)

            # Verify
            mock_repo.add.assert_called_once()
            mock_uow.flush.assert_called_once()
            assert result.id == sample_template_response.id
            assert result.name == sample_template_response.name

    def test_update_schedule_template(
        self,
        service,
        mock_uow,
        mock_repo,
        sample_template_model,
        sample_template_response,
    ):
        # Setup
        with patch(
            "scheduler_api.services.schedule_template_service.ScheduleTemplateRepository",
            return_value=mock_repo,
        ):
            template_id = sample_template_model.id
            update_dto = ScheduleTemplateUpdate(name="Updated Schedule")
            mock_repo.get_by_id.return_value = sample_template_model
            mock_repo.add.return_value = sample_template_model

            # Test
            result = service.update_schedule_template(template_id, update_dto)

            # Verify
            mock_repo.get_by_id.assert_called_once_with(template_id)
            mock_repo.add.assert_called_once()
            mock_uow.flush.assert_called_once()
            assert result.id == sample_template_response.id

    def test_update_schedule_template_not_found(self, service, mock_uow, mock_repo):
        # Setup
        with patch(
            "scheduler_api.services.schedule_template_service.ScheduleTemplateRepository",
            return_value=mock_repo,
        ):
            template_id = uuid4()
            update_dto = ScheduleTemplateUpdate(name="Updated Schedule")
            mock_repo.get_by_id.return_value = None

            # Test & Verify
            with pytest.raises(HTTPException) as exc_info:
                service.update_schedule_template(template_id, update_dto)

            assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
            mock_repo.get_by_id.assert_called_once_with(template_id)

    def test_delete_schedule_template(
        self, service, mock_uow, mock_repo, sample_template_model
    ):
        # Setup
        with patch(
            "scheduler_api.services.schedule_template_service.ScheduleTemplateRepository",
            return_value=mock_repo,
        ):
            template_id = sample_template_model.id
            mock_repo.get_by_id.return_value = sample_template_model

            # Test
            service.delete_schedule_template(template_id)

            # Verify
            mock_repo.get_by_id.assert_called_once_with(template_id)
            mock_repo.delete.assert_called_once_with(sample_template_model)

    def test_delete_schedule_template_not_found(self, service, mock_uow, mock_repo):
        # Setup
        with patch(
            "scheduler_api.services.schedule_template_service.ScheduleTemplateRepository",
            return_value=mock_repo,
        ):
            template_id = uuid4()
            mock_repo.get_by_id.return_value = None

            # Test & Verify
            with pytest.raises(HTTPException) as exc_info:
                service.delete_schedule_template(template_id)

            assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
            mock_repo.get_by_id.assert_called_once_with(template_id)


class TestShiftTemplateServiceUOW:
    """Test ShiftTemplateService with UnitOfWork."""

    @pytest.fixture
    def mock_uow(self):
        uow = MagicMock(spec=UnitOfWork)
        uow.session = MagicMock()
        uow.flush = MagicMock()
        return uow

    @pytest.fixture
    def mock_repo(self):
        repo = MagicMock()
        repo.get_all = MagicMock()
        repo.get_by_id = MagicMock()
        repo.add = MagicMock()
        repo.delete = MagicMock()
        return repo

    @pytest.fixture
    def service(self, mock_uow):
        return ShiftTemplateService(mock_uow)

    @pytest.fixture
    def sample_shift_template_response(self):
        return ShiftTemplateResponse(
            id=uuid4(),
            name="Morning Shift",
            schedule_template_id=uuid4(),
            start_time=time(9, 0, 0),
            end_time=time(17, 0, 0),
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

    def test_get_shift_template_not_found(self, service, mock_uow, mock_repo):
        # Setup
        with patch(
            "scheduler_api.services.shift_template_service.ShiftTemplateRepository",
            return_value=mock_repo,
        ):
            template_id = uuid4()
            mock_repo.get_by_id.return_value = None

            # Test & Verify
            with pytest.raises(HTTPException) as exc_info:
                service.get_shift_template(template_id)

            assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
            mock_repo.get_by_id.assert_called_once_with(template_id)

    def test_update_shift_template_not_found(self, service, mock_uow, mock_repo):
        # Setup
        with patch(
            "scheduler_api.services.shift_template_service.ShiftTemplateRepository",
            return_value=mock_repo,
        ):
            template_id = uuid4()
            update_dto = ShiftTemplateUpdate(name="Updated Shift")
            mock_repo.get_by_id.return_value = None

            # Test & Verify
            with pytest.raises(HTTPException) as exc_info:
                service.update_shift_template(template_id, update_dto)

            assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
            mock_repo.get_by_id.assert_called_once_with(template_id)

    def test_delete_shift_template_not_found(self, service, mock_uow, mock_repo):
        # Setup
        with patch(
            "scheduler_api.services.shift_template_service.ShiftTemplateRepository",
            return_value=mock_repo,
        ):
            template_id = uuid4()
            mock_repo.get_by_id.return_value = None

            # Test & Verify
            with pytest.raises(HTTPException) as exc_info:
                service.delete_shift_template(template_id)

            assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
            mock_repo.get_by_id.assert_called_once_with(template_id)


class TestScheduleServiceUOW:
    """Test ScheduleService with UnitOfWork."""

    @pytest.fixture
    def mock_uow(self):
        uow = MagicMock(spec=UnitOfWork)
        uow.session = MagicMock()
        uow.flush = MagicMock()
        return uow

    @pytest.fixture
    def mock_repo(self):
        repo = MagicMock()
        repo.get_all = MagicMock()
        repo.get_by_id = MagicMock()
        repo.add = MagicMock()
        repo.delete = MagicMock()
        return repo

    @pytest.fixture
    def service(self, mock_uow):
        return ScheduleService(mock_uow)

    def test_get_schedule_not_found(self, service, mock_uow, mock_repo):
        # Setup
        with patch(
            "scheduler_api.services.schedule_service.ScheduleRepository",
            return_value=mock_repo,
        ):
            schedule_id = uuid4()
            mock_repo.get_by_id.return_value = None

            # Test & Verify
            with pytest.raises(HTTPException) as exc_info:
                service.get_schedule(schedule_id)

            assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
            mock_repo.get_by_id.assert_called_once_with(schedule_id)

    def test_update_schedule_not_found(self, service, mock_uow, mock_repo):
        # Setup
        with patch(
            "scheduler_api.services.schedule_service.ScheduleRepository",
            return_value=mock_repo,
        ):
            schedule_id = uuid4()
            update_dto = ScheduleUpdate(name="Updated Schedule")
            mock_repo.get_by_id.return_value = None

            # Test & Verify
            with pytest.raises(HTTPException) as exc_info:
                service.update_schedule(schedule_id, update_dto)

            assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
            mock_repo.get_by_id.assert_called_once_with(schedule_id)

    def test_delete_schedule_not_found(self, service, mock_uow, mock_repo):
        # Setup
        with patch(
            "scheduler_api.services.schedule_service.ScheduleRepository",
            return_value=mock_repo,
        ):
            schedule_id = uuid4()
            mock_repo.get_by_id.return_value = None

            # Test & Verify
            with pytest.raises(HTTPException) as exc_info:
                service.delete_schedule(schedule_id)

            assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
            mock_repo.get_by_id.assert_called_once_with(schedule_id)


class TestShiftServiceUOW:
    """Test ShiftService with UnitOfWork."""

    @pytest.fixture
    def mock_uow(self):
        uow = MagicMock(spec=UnitOfWork)
        uow.session = MagicMock()
        uow.flush = MagicMock()
        return uow

    @pytest.fixture
    def mock_repo(self):
        repo = MagicMock()
        repo.get_all = MagicMock()
        repo.get_by_id = MagicMock()
        repo.add = MagicMock()
        repo.delete = MagicMock()
        return repo

    @pytest.fixture
    def service(self, mock_uow):
        return ShiftService(mock_uow)

    def test_list_shifts(self, service, mock_uow, mock_repo):
        # Setup
        with patch(
            "scheduler_api.services.shift_service.ShiftRepository",
            return_value=mock_repo,
        ):
            shift1 = ShiftModel(
                id=uuid4(),
                name="Morning Shift",
                start_time=datetime(2024, 1, 1, 9, 0, 0),
                end_time=datetime(2024, 1, 1, 17, 0, 0),
                schedule_id=uuid4(),
                shift_template_id=uuid4(),
            )
            shift2 = ShiftModel(
                id=uuid4(),
                name="Evening Shift",
                start_time=datetime(2024, 1, 1, 17, 0, 0),
                end_time=datetime(2024, 1, 1, 1, 0, 0),
                schedule_id=uuid4(),
                shift_template_id=uuid4(),
            )
            mock_repo.get_all.return_value = [shift1, shift2]

            # Test
            result = service.list_shifts()

            # Verify
            assert len(result) == 2
            assert result[0].name == "Morning Shift"
            assert result[1].name == "Evening Shift"
            mock_repo.get_all.assert_called_once()

    def test_get_shift(self, service, mock_uow, mock_repo):
        # Setup
        with patch(
            "scheduler_api.services.shift_service.ShiftRepository",
            return_value=mock_repo,
        ):
            shift_id = uuid4()
            shift_model = ShiftModel(
                id=shift_id,
                name="Morning Shift",
                start_time=datetime(2024, 1, 1, 9, 0, 0),
                end_time=datetime(2024, 1, 1, 17, 0, 0),
                schedule_id=uuid4(),
                shift_template_id=uuid4(),
            )
            mock_repo.get_by_id.return_value = shift_model

            # Test
            result = service.get_shift(shift_id)

            # Verify
            assert result is not None
            assert result.id == shift_id
            assert result.name == "Morning Shift"
            mock_repo.get_by_id.assert_called_once_with(shift_id)

    def test_get_shift_not_found(self, service, mock_uow, mock_repo):
        # Setup
        with patch(
            "scheduler_api.services.shift_service.ShiftRepository",
            return_value=mock_repo,
        ):
            shift_id = uuid4()
            mock_repo.get_by_id.return_value = None

            # Test
            result = service.get_shift(shift_id)

            # Verify
            assert result is None
            mock_repo.get_by_id.assert_called_once_with(shift_id)

    def test_create_shift(self, service, mock_uow, mock_repo):
        # Setup
        with patch(
            "scheduler_api.services.shift_service.ShiftRepository",
            return_value=mock_repo,
        ):
            shift_id = uuid4()
            create_dto = Shift(
                name="Morning Shift",
                start_time=datetime(2024, 1, 1, 9, 0, 0),
                end_time=datetime(2024, 1, 1, 17, 0, 0),
                schedule_id=uuid4(),
                shift_template_id=uuid4(),
            )
            saved_model = ShiftModel(
                id=shift_id,
                name="Morning Shift",
                start_time=datetime(2024, 1, 1, 9, 0, 0),
                end_time=datetime(2024, 1, 1, 17, 0, 0),
                schedule_id=uuid4(),
                shift_template_id=uuid4(),
            )
            mock_repo.add.return_value = saved_model

            # Test
            result = service.create_shift(create_dto)

            # Verify
            assert result is not None
            assert result.id == shift_id
            assert result.name == "Morning Shift"
            mock_repo.add.assert_called_once()
            mock_uow.flush.assert_called_once()

    def test_update_shift(self, service, mock_uow, mock_repo):
        # Setup
        with patch(
            "scheduler_api.services.shift_service.ShiftRepository",
            return_value=mock_repo,
        ):
            shift_id = uuid4()
            existing_model = ShiftModel(
                id=shift_id,
                name="Morning Shift",
                start_time=datetime(2024, 1, 1, 9, 0, 0),
                end_time=datetime(2024, 1, 1, 17, 0, 0),
                schedule_id=uuid4(),
                shift_template_id=uuid4(),
            )
            update_dto = ShiftUpdate(name="Updated Shift Name")
            updated_model = ShiftModel(
                id=shift_id,
                name="Updated Shift Name",
                start_time=datetime(2024, 1, 1, 9, 0, 0),
                end_time=datetime(2024, 1, 1, 17, 0, 0),
                schedule_id=uuid4(),
                shift_template_id=uuid4(),
            )
            mock_repo.get_by_id.return_value = existing_model
            mock_repo.add.return_value = updated_model

            # Test
            result = service.update_shift(shift_id, update_dto)

            # Verify
            assert result is not None
            assert result.name == "Updated Shift Name"
            mock_repo.get_by_id.assert_called_once_with(shift_id)
            mock_repo.add.assert_called_once()
            mock_uow.flush.assert_called_once()

    def test_update_shift_not_found(self, service, mock_uow, mock_repo):
        # Setup
        with patch(
            "scheduler_api.services.shift_service.ShiftRepository",
            return_value=mock_repo,
        ):
            shift_id = uuid4()
            update_dto = ShiftUpdate(name="Updated Shift Name")
            mock_repo.get_by_id.return_value = None

            # Test
            result = service.update_shift(shift_id, update_dto)

            # Verify
            assert result is None
            mock_repo.get_by_id.assert_called_once_with(shift_id)

    def test_delete_shift(self, service, mock_uow, mock_repo):
        # Setup
        with patch(
            "scheduler_api.services.shift_service.ShiftRepository",
            return_value=mock_repo,
        ):
            shift_id = uuid4()
            shift_model = ShiftModel(
                id=shift_id,
                name="Morning Shift",
                start_time=datetime(2024, 1, 1, 9, 0, 0),
                end_time=datetime(2024, 1, 1, 17, 0, 0),
                schedule_id=uuid4(),
                shift_template_id=uuid4(),
            )
            mock_repo.get_by_id.return_value = shift_model

            # Test
            service.delete_shift(shift_id)

            # Verify
            mock_repo.get_by_id.assert_called_once_with(shift_id)
            mock_repo.delete.assert_called_once_with(shift_model)

    def test_delete_shift_not_found(self, service, mock_uow, mock_repo):
        # Setup
        with patch(
            "scheduler_api.services.shift_service.ShiftRepository",
            return_value=mock_repo,
        ):
            shift_id = uuid4()
            mock_repo.get_by_id.return_value = None

            # Test & Verify
            with pytest.raises(HTTPException) as exc_info:
                service.delete_shift(shift_id)

            assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
            mock_repo.get_by_id.assert_called_once_with(shift_id)


class TestSkillServiceUOW:
    """Test SkillService with UnitOfWork."""

    @pytest.fixture
    def mock_uow(self):
        uow = MagicMock(spec=UnitOfWork)
        uow.session = MagicMock()
        uow.flush = MagicMock()
        return uow

    @pytest.fixture
    def mock_repo(self):
        repo = MagicMock()
        repo.get_all = MagicMock()
        repo.get_by_id = MagicMock()
        repo.add = MagicMock()
        repo.delete = MagicMock()
        return repo

    @pytest.fixture
    def service(self, mock_uow):
        return SkillService(mock_uow)

    def test_list_skills(self, service, mock_uow, mock_repo):
        # Setup
        with patch(
            "scheduler_api.services.skill_service.SkillRepository",
            return_value=mock_repo,
        ):
            skill1 = SkillModel(id=uuid4(), name="Python", description="Python programming")
            skill2 = SkillModel(id=uuid4(), name="JavaScript", description="JavaScript programming")
            mock_repo.get_all.return_value = [skill1, skill2]

            # Test
            result = service.list_skills()

            # Verify
            assert len(result) == 2
            assert result[0].name == "Python"
            assert result[1].name == "JavaScript"
            mock_repo.get_all.assert_called_once()

    def test_get_skill(self, service, mock_uow, mock_repo):
        # Setup
        with patch(
            "scheduler_api.services.skill_service.SkillRepository",
            return_value=mock_repo,
        ):
            skill_id = uuid4()
            skill_model = SkillModel(id=skill_id, name="Python", description="Python programming")
            mock_repo.get_by_id.return_value = skill_model

            # Test
            result = service.get_skill(skill_id)

            # Verify
            assert result is not None
            assert result.id == skill_id
            assert result.name == "Python"
            mock_repo.get_by_id.assert_called_once_with(skill_id)

    def test_get_skill_not_found(self, service, mock_uow, mock_repo):
        # Setup
        with patch(
            "scheduler_api.services.skill_service.SkillRepository",
            return_value=mock_repo,
        ):
            skill_id = uuid4()
            mock_repo.get_by_id.return_value = None

            # Test
            result = service.get_skill(skill_id)

            # Verify
            assert result is None
            mock_repo.get_by_id.assert_called_once_with(skill_id)

    def test_create_skill(self, service, mock_uow, mock_repo):
        # Setup
        with patch(
            "scheduler_api.services.skill_service.SkillRepository",
            return_value=mock_repo,
        ):
            skill_id = uuid4()
            create_dto = Skill(name="Python", description="Python programming")
            saved_model = SkillModel(id=skill_id, name="Python", description="Python programming")
            mock_repo.add.return_value = saved_model

            # Test
            result = service.create_skill(create_dto)

            # Verify
            assert result is not None
            assert result.id == skill_id
            assert result.name == "Python"
            mock_repo.add.assert_called_once()
            mock_uow.flush.assert_called_once()

    def test_update_skill(self, service, mock_uow, mock_repo):
        # Setup
        with patch(
            "scheduler_api.services.skill_service.SkillRepository",
            return_value=mock_repo,
        ):
            skill_id = uuid4()
            existing_model = SkillModel(id=skill_id, name="Python", description="Python programming")
            update_dto = SkillUpdate(name="Python 3", description="Python 3 programming")
            updated_model = SkillModel(id=skill_id, name="Python 3", description="Python 3 programming")
            mock_repo.get_by_id.return_value = existing_model
            mock_repo.add.return_value = updated_model

            # Test
            result = service.update_skill(skill_id, update_dto)

            # Verify
            assert result is not None
            assert result.name == "Python 3"
            assert result.description == "Python 3 programming"
            mock_repo.get_by_id.assert_called_once_with(skill_id)
            mock_repo.add.assert_called_once()
            mock_uow.flush.assert_called_once()

    def test_update_skill_not_found(self, service, mock_uow, mock_repo):
        # Setup
        with patch(
            "scheduler_api.services.skill_service.SkillRepository",
            return_value=mock_repo,
        ):
            skill_id = uuid4()
            update_dto = SkillUpdate(name="Python 3", description="Python 3 programming")
            mock_repo.get_by_id.return_value = None

            # Test
            result = service.update_skill(skill_id, update_dto)

            # Verify
            assert result is None
            mock_repo.get_by_id.assert_called_once_with(skill_id)

    def test_delete_skill(self, service, mock_uow, mock_repo):
        # Setup
        with patch(
            "scheduler_api.services.skill_service.SkillRepository",
            return_value=mock_repo,
        ):
            skill_id = uuid4()
            skill_model = SkillModel(id=skill_id, name="Python", description="Python programming")
            mock_repo.get_by_id.return_value = skill_model

            # Test
            service.delete_skill(skill_id)

            # Verify
            mock_repo.get_by_id.assert_called_once_with(skill_id)
            mock_repo.delete.assert_called_once_with(skill_model)

    def test_delete_skill_not_found(self, service, mock_uow, mock_repo):
        # Setup
        with patch(
            "scheduler_api.services.skill_service.SkillRepository",
            return_value=mock_repo,
        ):
            skill_id = uuid4()
            mock_repo.get_by_id.return_value = None

            # Test & Verify
            with pytest.raises(HTTPException) as exc_info:
                service.delete_skill(skill_id)

            assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
            mock_repo.get_by_id.assert_called_once_with(skill_id)


class TestWorkerServiceUOW:
    """Test WorkerService with UnitOfWork."""

    @pytest.fixture
    def mock_uow(self):
        uow = MagicMock(spec=UnitOfWork)
        uow.session = MagicMock()
        uow.flush = MagicMock()
        return uow

    @pytest.fixture
    def mock_repo(self):
        repo = MagicMock()
        repo.get_all = MagicMock()
        repo.get_by_id = MagicMock()
        repo.add = MagicMock()
        repo.delete = MagicMock()
        return repo

    @pytest.fixture
    def service(self, mock_uow):
        return WorkerService(mock_uow)

    def test_list_workers(self, service, mock_uow, mock_repo):
        # Setup
        with patch(
            "scheduler_api.services.worker_service.WorkerRepository",
            return_value=mock_repo,
        ):
            worker1 = WorkerModel(id=uuid4(), name="John Doe")
            worker2 = WorkerModel(id=uuid4(), name="Jane Smith")
            mock_repo.get_all.return_value = [worker1, worker2]

            # Test
            result = service.list_workers()

            # Verify
            assert len(result) == 2
            assert result[0].name == "John Doe"
            assert result[1].name == "Jane Smith"
            mock_repo.get_all.assert_called_once()

    def test_get_worker(self, service, mock_uow, mock_repo):
        # Setup
        with patch(
            "scheduler_api.services.worker_service.WorkerRepository",
            return_value=mock_repo,
        ):
            worker_id = uuid4()
            worker_model = WorkerModel(id=worker_id, name="John Doe")
            mock_repo.get_by_id.return_value = worker_model

            # Test
            result = service.get_worker(worker_id)

            # Verify
            assert result is not None
            assert result.id == worker_id
            assert result.name == "John Doe"
            mock_repo.get_by_id.assert_called_once_with(worker_id)

    def test_get_worker_not_found(self, service, mock_uow, mock_repo):
        # Setup
        with patch(
            "scheduler_api.services.worker_service.WorkerRepository",
            return_value=mock_repo,
        ):
            worker_id = uuid4()
            mock_repo.get_by_id.return_value = None

            # Test
            result = service.get_worker(worker_id)

            # Verify
            assert result is None
            mock_repo.get_by_id.assert_called_once_with(worker_id)

    def test_create_worker(self, service, mock_uow, mock_repo):
        # Setup
        with patch(
            "scheduler_api.services.worker_service.WorkerRepository",
            return_value=mock_repo,
        ):
            worker_id = uuid4()
            create_dto = Worker(name="John Doe")
            saved_model = WorkerModel(id=worker_id, name="John Doe")
            mock_repo.add.return_value = saved_model

            # Test
            result = service.create_worker(create_dto)

            # Verify
            assert result is not None
            assert result.id == worker_id
            assert result.name == "John Doe"
            mock_repo.add.assert_called_once()
            mock_uow.flush.assert_called_once()

    def test_update_worker(self, service, mock_uow, mock_repo):
        # Setup
        with patch(
            "scheduler_api.services.worker_service.WorkerRepository",
            return_value=mock_repo,
        ):
            worker_id = uuid4()
            existing_model = WorkerModel(id=worker_id, name="John Doe")
            update_dto = WorkerUpdate(name="Johnathan Doe")
            updated_model = WorkerModel(id=worker_id, name="Johnathan Doe")
            mock_repo.get_by_id.return_value = existing_model
            mock_repo.add.return_value = updated_model

            # Test
            result = service.update_worker(worker_id, update_dto)

            # Verify
            assert result is not None
            assert result.name == "Johnathan Doe"
            mock_repo.get_by_id.assert_called_once_with(worker_id)
            mock_repo.add.assert_called_once()
            mock_uow.flush.assert_called_once()

    def test_update_worker_not_found(self, service, mock_uow, mock_repo):
        # Setup
        with patch(
            "scheduler_api.services.worker_service.WorkerRepository",
            return_value=mock_repo,
        ):
            worker_id = uuid4()
            update_dto = WorkerUpdate(name="Johnathan Doe")
            mock_repo.get_by_id.return_value = None

            # Test
            result = service.update_worker(worker_id, update_dto)

            # Verify
            assert result is None
            mock_repo.get_by_id.assert_called_once_with(worker_id)

    def test_delete_worker(self, service, mock_uow, mock_repo):
        # Setup
        with patch(
            "scheduler_api.services.worker_service.WorkerRepository",
            return_value=mock_repo,
        ):
            worker_id = uuid4()
            worker_model = WorkerModel(id=worker_id, name="John Doe")
            mock_repo.get_by_id.return_value = worker_model

            # Test
            service.delete_worker(worker_id)

            # Verify
            mock_repo.get_by_id.assert_called_once_with(worker_id)
            mock_repo.delete.assert_called_once_with(worker_model)

    def test_delete_worker_not_found(self, service, mock_uow, mock_repo):
        # Setup
        with patch(
            "scheduler_api.services.worker_service.WorkerRepository",
            return_value=mock_repo,
        ):
            worker_id = uuid4()
            mock_repo.get_by_id.return_value = None

            # Test & Verify
            with pytest.raises(HTTPException) as exc_info:
                service.delete_worker(worker_id)

            assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
            mock_repo.get_by_id.assert_called_once_with(worker_id)
