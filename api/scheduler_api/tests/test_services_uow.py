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
from scheduler_api.services.schedule_generation_run_service import ScheduleGenerationRunService

from scheduler_api.schemas.schedule_template import ScheduleTemplateCreate, ScheduleTemplateUpdate, ScheduleTemplateResponse
from scheduler_api.schemas.shift_template import ShiftTemplateCreate, ShiftTemplateUpdate, ShiftTemplateResponse
from scheduler_api.schemas.schedule_crud import ScheduleCreate, ScheduleUpdate, ScheduleResponse
from scheduler_api.schemas.schedule_generation_run import ScheduleGenerationRunCreate, ScheduleGenerationRunUpdate, ScheduleGenerationRunResponse

from scheduler_api.db.models.templates.schedule_template import ScheduleTemplate
from scheduler_api.db.models.templates.shift_template import ShiftTemplate
from scheduler_api.db.models.schedules.schedule import Schedule
from scheduler_api.db.models.runs.schedule_generation_run import ScheduleGenerationRun
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
            updated_at=sample_template_model.updated_at
        )
    
    def test_list_schedule_templates(self, service, mock_uow, mock_repo, sample_template_model, sample_template_response):
        # Setup
        with patch('scheduler_api.services.schedule_template_service.ScheduleTemplateRepository', return_value=mock_repo):
            mock_repo.get_all.return_value = [sample_template_model]
            
            # Test
            result = service.list_schedule_templates()
            
            # Verify
            mock_repo.get_all.assert_called_once()
            assert len(result) == 1
            assert result[0].id == sample_template_response.id
            assert result[0].name == sample_template_response.name
    
    def test_get_schedule_template(self, service, mock_uow, mock_repo, sample_template_model, sample_template_response):
        # Setup
        with patch('scheduler_api.services.schedule_template_service.ScheduleTemplateRepository', return_value=mock_repo):
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
        with patch('scheduler_api.services.schedule_template_service.ScheduleTemplateRepository', return_value=mock_repo):
            template_id = uuid4()
            mock_repo.get_by_id.return_value = None
            
            # Test & Verify
            with pytest.raises(HTTPException) as exc_info:
                service.get_schedule_template(template_id)
            
            assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
            mock_repo.get_by_id.assert_called_once_with(template_id)
    
    def test_create_schedule_template(self, service, mock_uow, mock_repo, sample_template_model, sample_template_response):
        # Setup
        with patch('scheduler_api.services.schedule_template_service.ScheduleTemplateRepository', return_value=mock_repo):
            create_dto = ScheduleTemplateCreate(name="Weekly Schedule")
            mock_repo.add.return_value = sample_template_model
            
            # Test
            result = service.create_schedule_template(create_dto)
            
            # Verify
            mock_repo.add.assert_called_once()
            mock_uow.flush.assert_called_once()
            assert result.id == sample_template_response.id
            assert result.name == sample_template_response.name
    
    def test_update_schedule_template(self, service, mock_uow, mock_repo, sample_template_model, sample_template_response):
        # Setup
        with patch('scheduler_api.services.schedule_template_service.ScheduleTemplateRepository', return_value=mock_repo):
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
        with patch('scheduler_api.services.schedule_template_service.ScheduleTemplateRepository', return_value=mock_repo):
            template_id = uuid4()
            update_dto = ScheduleTemplateUpdate(name="Updated Schedule")
            mock_repo.get_by_id.return_value = None
            
            # Test & Verify
            with pytest.raises(HTTPException) as exc_info:
                service.update_schedule_template(template_id, update_dto)
            
            assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
            mock_repo.get_by_id.assert_called_once_with(template_id)
    
    def test_delete_schedule_template(self, service, mock_uow, mock_repo, sample_template_model):
        # Setup
        with patch('scheduler_api.services.schedule_template_service.ScheduleTemplateRepository', return_value=mock_repo):
            template_id = sample_template_model.id
            mock_repo.get_by_id.return_value = sample_template_model
            
            # Test
            service.delete_schedule_template(template_id)
            
            # Verify
            mock_repo.get_by_id.assert_called_once_with(template_id)
            mock_repo.delete.assert_called_once_with(sample_template_model)
    
    def test_delete_schedule_template_not_found(self, service, mock_uow, mock_repo):
        # Setup
        with patch('scheduler_api.services.schedule_template_service.ScheduleTemplateRepository', return_value=mock_repo):
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
            updated_at=datetime.now()
        )
    
    def test_get_shift_template_not_found(self, service, mock_uow, mock_repo):
        # Setup
        with patch('scheduler_api.services.shift_template_service.ShiftTemplateRepository', return_value=mock_repo):
            template_id = uuid4()
            mock_repo.get_by_id.return_value = None
            
            # Test & Verify
            with pytest.raises(HTTPException) as exc_info:
                service.get_shift_template(template_id)
            
            assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
            mock_repo.get_by_id.assert_called_once_with(template_id)
    
    def test_update_shift_template_not_found(self, service, mock_uow, mock_repo):
        # Setup
        with patch('scheduler_api.services.shift_template_service.ShiftTemplateRepository', return_value=mock_repo):
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
        with patch('scheduler_api.services.shift_template_service.ShiftTemplateRepository', return_value=mock_repo):
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
        with patch('scheduler_api.services.schedule_service.ScheduleRepository', return_value=mock_repo):
            schedule_id = uuid4()
            mock_repo.get_by_id.return_value = None
            
            # Test & Verify
            with pytest.raises(HTTPException) as exc_info:
                service.get_schedule(schedule_id)
            
            assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
            mock_repo.get_by_id.assert_called_once_with(schedule_id)
    
    def test_update_schedule_not_found(self, service, mock_uow, mock_repo):
        # Setup
        with patch('scheduler_api.services.schedule_service.ScheduleRepository', return_value=mock_repo):
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
        with patch('scheduler_api.services.schedule_service.ScheduleRepository', return_value=mock_repo):
            schedule_id = uuid4()
            mock_repo.get_by_id.return_value = None
            
            # Test & Verify
            with pytest.raises(HTTPException) as exc_info:
                service.delete_schedule(schedule_id)
            
            assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
            mock_repo.get_by_id.assert_called_once_with(schedule_id)


class TestScheduleGenerationRunServiceUOW:
    """Test ScheduleGenerationRunService with UnitOfWork."""
    
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
        return ScheduleGenerationRunService(mock_uow)
    
    def test_get_schedule_generation_run_not_found(self, service, mock_uow, mock_repo):
        # Setup
        with patch('scheduler_api.services.schedule_generation_run_service.ScheduleGenerationRunRepository', return_value=mock_repo):
            run_id = uuid4()
            mock_repo.get_by_id.return_value = None
            
            # Test & Verify
            with pytest.raises(HTTPException) as exc_info:
                service.get_schedule_generation_run(run_id)
            
            assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
            mock_repo.get_by_id.assert_called_once_with(run_id)
    
    def test_update_schedule_generation_run_not_found(self, service, mock_uow, mock_repo):
        # Setup
        with patch('scheduler_api.services.schedule_generation_run_service.ScheduleGenerationRunRepository', return_value=mock_repo):
            run_id = uuid4()
            update_dto = ScheduleGenerationRunUpdate(status=ScheduleGenerationStatus.running)
            mock_repo.get_by_id.return_value = None
            
            # Test & Verify
            with pytest.raises(HTTPException) as exc_info:
                service.update_schedule_generation_run(run_id, update_dto)
            
            assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
            mock_repo.get_by_id.assert_called_once_with(run_id)
    
    def test_delete_schedule_generation_run_not_found(self, service, mock_uow, mock_repo):
        # Setup
        with patch('scheduler_api.services.schedule_generation_run_service.ScheduleGenerationRunRepository', return_value=mock_repo):
            run_id = uuid4()
            mock_repo.get_by_id.return_value = None
            
            # Test & Verify
            with pytest.raises(HTTPException) as exc_info:
                service.delete_schedule_generation_run(run_id)
            
            assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
            mock_repo.get_by_id.assert_called_once_with(run_id)