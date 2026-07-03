"""Test ScheduleService with UnitOfWork pattern."""

import pytest
from unittest.mock import MagicMock, patch
from uuid import UUID, uuid4
from datetime import datetime
from fastapi import HTTPException, status

from scheduler_api.uow.unit_of_work import UnitOfWork
from scheduler_api.services.schedule_service import ScheduleService
from scheduler_api.schemas.schedule_crud import ScheduleCreate, ScheduleUpdate, ScheduleResponse


class TestScheduleService:
    """Test ScheduleService."""
    
    @pytest.fixture
    def mock_uow(self):
        uow = MagicMock(spec=UnitOfWork)
        uow.session = MagicMock()
        uow.flush = MagicMock()
        return uow
    
    @pytest.fixture
    def sample_schedule_model(self):
        schedule = MagicMock()
        schedule.id = uuid4()
        schedule.name = "January 2024 Schedule"
        schedule.schedule_template_id = uuid4()
        schedule.created_at = datetime.utcnow()
        schedule.updated_at = datetime.utcnow()
        return schedule
    
    @pytest.fixture
    def sample_schedule_response(self, sample_schedule_model):
        return ScheduleResponse(
            id=sample_schedule_model.id,
            name=sample_schedule_model.name,
            schedule_template_id=sample_schedule_model.schedule_template_id,
            created_at=sample_schedule_model.created_at,
            updated_at=sample_schedule_model.updated_at
        )
    
    def test_list_schedules(self, mock_uow, sample_schedule_model, sample_schedule_response):
        # Setup
        mock_repo = MagicMock()
        mock_repo.get_all.return_value = [sample_schedule_model]
        
        # Patch the repository constructor to return our mock
        with patch('scheduler_api.services.schedule_service.ScheduleRepository', return_value=mock_repo):
            service = ScheduleService(mock_uow)
            
            # Test
            result = service.list_schedules()
        
        # Verify
        mock_repo.get_all.assert_called_once()
        assert len(result) == 1
        assert result[0].id == sample_schedule_response.id
        assert result[0].name == sample_schedule_response.name
    
    def test_get_schedule(self, mock_uow, sample_schedule_model, sample_schedule_response):
        # Setup
        schedule_id = sample_schedule_model.id
        mock_repo = MagicMock()
        mock_repo.get_by_id.return_value = sample_schedule_model
        
        # Patch the repository constructor to return our mock
        with patch('scheduler_api.services.schedule_service.ScheduleRepository', return_value=mock_repo):
            service = ScheduleService(mock_uow)
            
            # Test
            result = service.get_schedule(schedule_id)
        
        # Verify
        mock_repo.get_by_id.assert_called_once_with(schedule_id)
        assert result.id == sample_schedule_response.id
        assert result.name == sample_schedule_response.name
    
    def test_get_schedule_not_found(self, mock_uow):
        # Setup
        schedule_id = uuid4()
        mock_repo = MagicMock()
        mock_repo.get_by_id.return_value = None
        
        # Patch the repository constructor to return our mock
        with patch('scheduler_api.services.schedule_service.ScheduleRepository', return_value=mock_repo):
            service = ScheduleService(mock_uow)
            
            # Test & Verify
            with pytest.raises(HTTPException) as exc_info:
                service.get_schedule(schedule_id)
        
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        mock_repo.get_by_id.assert_called_once_with(schedule_id)
    
    def test_create_schedule(self, mock_uow, sample_schedule_model, sample_schedule_response):
        # Setup
        create_dto = ScheduleCreate(
            name="January 2024 Schedule",
            schedule_template_id=sample_schedule_model.schedule_template_id
        )
        mock_repo = MagicMock()
        mock_repo.add.return_value = sample_schedule_model
        
        # Patch the repository constructor to return our mock
        with patch('scheduler_api.services.schedule_service.ScheduleRepository', return_value=mock_repo):
            service = ScheduleService(mock_uow)
            
            # Test
            result = service.create_schedule(create_dto)
        
        # Verify
        mock_repo.add.assert_called_once()
        mock_uow.flush.assert_called_once()
        assert result.id == sample_schedule_response.id
        assert result.name == sample_schedule_response.name
    
    def test_update_schedule(self, mock_uow, sample_schedule_model, sample_schedule_response):
        # Setup
        schedule_id = sample_schedule_model.id
        update_dto = ScheduleUpdate(name="Updated Schedule")
        mock_repo = MagicMock()
        mock_repo.get_by_id.return_value = sample_schedule_model
        mock_repo.add.return_value = sample_schedule_model
        
        # Patch the repository constructor to return our mock
        with patch('scheduler_api.services.schedule_service.ScheduleRepository', return_value=mock_repo):
            service = ScheduleService(mock_uow)
            
            # Test
            result = service.update_schedule(schedule_id, update_dto)
        
        # Verify
        mock_repo.get_by_id.assert_called_once_with(schedule_id)
        mock_repo.add.assert_called_once()
        mock_uow.flush.assert_called_once()
        assert result.id == sample_schedule_response.id
    
    def test_update_schedule_not_found(self, mock_uow):
        # Setup
        schedule_id = uuid4()
        update_dto = ScheduleUpdate(name="Updated Schedule")
        mock_repo = MagicMock()
        mock_repo.get_by_id.return_value = None
        
        # Patch the repository constructor to return our mock
        with patch('scheduler_api.services.schedule_service.ScheduleRepository', return_value=mock_repo):
            service = ScheduleService(mock_uow)
            
            # Test & Verify
            with pytest.raises(HTTPException) as exc_info:
                service.update_schedule(schedule_id, update_dto)
        
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        mock_repo.get_by_id.assert_called_once_with(schedule_id)
    
    def test_delete_schedule(self, mock_uow, sample_schedule_model):
        # Setup
        schedule_id = sample_schedule_model.id
        mock_repo = MagicMock()
        mock_repo.get_by_id.return_value = sample_schedule_model
        
        # Patch the repository constructor to return our mock
        with patch('scheduler_api.services.schedule_service.ScheduleRepository', return_value=mock_repo):
            service = ScheduleService(mock_uow)
            
            # Test
            service.delete_schedule(schedule_id)
        
        # Verify
        mock_repo.get_by_id.assert_called_once_with(schedule_id)
        mock_repo.delete.assert_called_once_with(sample_schedule_model)
    
    def test_delete_schedule_not_found(self, mock_uow):
        # Setup
        schedule_id = uuid4()
        mock_repo = MagicMock()
        mock_repo.get_by_id.return_value = None
        
        # Patch the repository constructor to return our mock
        with patch('scheduler_api.services.schedule_service.ScheduleRepository', return_value=mock_repo):
            service = ScheduleService(mock_uow)
            
            # Test & Verify
            with pytest.raises(HTTPException) as exc_info:
                service.delete_schedule(schedule_id)
        
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        mock_repo.get_by_id.assert_called_once_with(schedule_id)