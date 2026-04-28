"""Test schedule layout service and repository."""
import pytest
from unittest.mock import MagicMock, patch
from uuid import uuid4
from datetime import datetime, timedelta
from scheduler_api.services.schedule_layout_service import ScheduleLayoutService
from scheduler_api.repositories.schedule_layout_repository import ScheduleLayoutRepository
from scheduler_api.schemas.schedule_layout import (
    ScheduleLayoutCreate,
    ScheduleLayoutUpdate,
    ScheduleLayoutResponse,
)


class TestScheduleLayoutRepository:
    """Test schedule layout repository."""
    
    @pytest.fixture
    def mock_session(self):
        """Create a mock SQLAlchemy session."""
        return MagicMock()
    
    @pytest.fixture
    def repository(self, mock_session):
        """Create a repository with mocked session."""
        return ScheduleLayoutRepository(mock_session)
    
    def test_get_all(self, repository, mock_session):
        """Test get_all method."""
        # Setup
        mock_layouts = [MagicMock(), MagicMock()]
        mock_session.query.return_value.all.return_value = mock_layouts
        
        # Execute
        result = repository.get_all()
        
        # Verify
        mock_session.query.assert_called_once()
        assert result == mock_layouts
    
    def test_get_by_id_found(self, repository, mock_session):
        """Test get_by_id when layout exists."""
        # Setup
        layout_id = uuid4()
        mock_layout = MagicMock()
        mock_session.get.return_value = mock_layout
        
        # Execute
        result = repository.get_by_id(layout_id)
        
        # Verify
        mock_session.get.assert_called_once_with(repository.__class__.__annotations__['ScheduleLayout'], layout_id)
        assert result == mock_layout
    
    def test_get_by_id_not_found(self, repository, mock_session):
        """Test get_by_id when layout doesn't exist."""
        # Setup
        layout_id = uuid4()
        mock_session.get.return_value = None
        
        # Execute
        result = repository.get_by_id(layout_id)
        
        # Verify
        assert result is None
    
    def test_create(self, repository, mock_session):
        """Test create method."""
        # Setup
        mock_layout = MagicMock()
        
        # Execute
        result = repository.create(mock_layout)
        
        # Verify
        mock_session.add.assert_called_once_with(mock_layout)
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once_with(mock_layout)
        assert result == mock_layout
    
    def test_update_found(self, repository, mock_session):
        """Test update when layout exists."""
        # Setup
        layout_id = uuid4()
        mock_layout = MagicMock()
        mock_layout.id = layout_id
        
        update_data = MagicMock()
        update_data.model_dump.return_value = {
            "name": "Updated Name",
            "description": "Updated Description",
        }
        
        mock_session.get.return_value = mock_layout
        
        # Execute
        result = repository.update(layout_id, update_data)
        
        # Verify
        mock_session.get.assert_called_once_with(repository.__class__.__annotations__['ScheduleLayout'], layout_id)
        update_data.model_dump.assert_called_once_with(exclude_unset=True)
        assert mock_layout.name == "Updated Name"
        assert mock_layout.description == "Updated Description"
        mock_session.add.assert_called_once_with(mock_layout)
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once_with(mock_layout)
        assert result == mock_layout
    
    def test_update_not_found(self, repository, mock_session):
        """Test update when layout doesn't exist."""
        # Setup
        layout_id = uuid4()
        update_data = MagicMock()
        mock_session.get.return_value = None
        
        # Execute
        result = repository.update(layout_id, update_data)
        
        # Verify
        assert result is None
    
    def test_delete_found(self, repository, mock_session):
        """Test delete when layout exists."""
        # Setup
        layout_id = uuid4()
        mock_layout = MagicMock()
        mock_session.get.return_value = mock_layout
        
        # Execute
        result = repository.delete(layout_id)
        
        # Verify
        mock_session.get.assert_called_once_with(repository.__class__.__annotations__['ScheduleLayout'], layout_id)
        mock_session.delete.assert_called_once_with(mock_layout)
        mock_session.commit.assert_called_once()
        assert result is True
    
    def test_delete_not_found(self, repository, mock_session):
        """Test delete when layout doesn't exist."""
        # Setup
        layout_id = uuid4()
        mock_session.get.return_value = None
        
        # Execute
        result = repository.delete(layout_id)
        
        # Verify
        assert result is False


class TestScheduleLayoutService:
    """Test schedule layout service."""
    
    @pytest.fixture
    def mock_repository(self):
        """Create a mock repository."""
        return MagicMock(spec=ScheduleLayoutRepository)
    
    @pytest.fixture
    def service(self, mock_repository):
        """Create a service with mocked repository."""
        return ScheduleLayoutService(mock_repository)
    
    @pytest.fixture
    def sample_create_dto(self):
        """Create a sample ScheduleLayoutCreate DTO."""
        return ScheduleLayoutCreate(
            name="Test Layout",
            description="Test Description",
            date_range_start=datetime.utcnow(),
            date_range_end=datetime.utcnow() + timedelta(days=7),
            worker_ids=[uuid4() for _ in range(3)],
            shift_templates=[{"name": "Morning", "hours": 8}],
            constraints={"max_hours": 40},
        )
    
    @pytest.fixture
    def sample_update_dto(self):
        """Create a sample ScheduleLayoutUpdate DTO."""
        return ScheduleLayoutUpdate(
            name="Updated Layout",
            description="Updated Description",
        )
    
    def test_list_layouts(self, service, mock_repository):
        """Test list_layouts method."""
        # Setup
        mock_layout = MagicMock()
        mock_layout.id = uuid4()
        mock_layout.name = "Test Layout"
        mock_layout.description = "Test Description"
        mock_layout.date_range_start = datetime.utcnow()
        mock_layout.date_range_end = datetime.utcnow() + timedelta(days=7)
        mock_layout.worker_ids = []
        mock_layout.shift_templates = []
        mock_layout.constraints = {}
        mock_layout.created_at = datetime.utcnow()
        mock_layout.updated_at = datetime.utcnow()
        
        mock_repository.get_all.return_value = [mock_layout]
        
        # Execute
        result = service.list_layouts()
        
        # Verify
        mock_repository.get_all.assert_called_once()
        assert len(result) == 1
        assert isinstance(result[0], ScheduleLayoutResponse)
        assert result[0].name == "Test Layout"
    
    def test_get_layout_found(self, service, mock_repository):
        """Test get_layout when layout exists."""
        # Setup
        layout_id = uuid4()
        mock_layout = MagicMock()
        mock_layout.id = layout_id
        mock_layout.name = "Test Layout"
        mock_layout.description = "Test Description"
        mock_layout.date_range_start = datetime.utcnow()
        mock_layout.date_range_end = datetime.utcnow() + timedelta(days=7)
        mock_layout.worker_ids = []
        mock_layout.shift_templates = []
        mock_layout.constraints = {}
        mock_layout.created_at = datetime.utcnow()
        mock_layout.updated_at = datetime.utcnow()
        
        mock_repository.get_by_id.return_value = mock_layout
        
        # Execute
        result = service.get_layout(layout_id)
        
        # Verify
        mock_repository.get_by_id.assert_called_once_with(layout_id)
        assert isinstance(result, ScheduleLayoutResponse)
        assert result.name == "Test Layout"
    
    def test_get_layout_not_found(self, service, mock_repository):
        """Test get_layout when layout doesn't exist."""
        # Setup
        layout_id = uuid4()
        mock_repository.get_by_id.return_value = None
        
        # Execute
        result = service.get_layout(layout_id)
        
        # Verify
        assert result is None
    
    def test_create_layout(self, service, mock_repository, sample_create_dto):
        """Test create_layout method."""
        # Setup
        mock_layout = MagicMock()
        mock_layout.id = uuid4()
        mock_layout.name = sample_create_dto.name
        mock_layout.description = sample_create_dto.description
        mock_layout.date_range_start = sample_create_dto.date_range_start
        mock_layout.date_range_end = sample_create_dto.date_range_end
        mock_layout.worker_ids = sample_create_dto.worker_ids
        mock_layout.shift_templates = sample_create_dto.shift_templates
        mock_layout.constraints = sample_create_dto.constraints
        mock_layout.created_at = datetime.utcnow()
        mock_layout.updated_at = datetime.utcnow()
        
        mock_repository.create.return_value = mock_layout
        
        # Execute
        result = service.create_layout(sample_create_dto)
        
        # Verify
        mock_repository.create.assert_called_once()
        assert isinstance(result, ScheduleLayoutResponse)
        assert result.name == sample_create_dto.name
        assert result.description == sample_create_dto.description
    
    def test_update_layout_found(self, service, mock_repository, sample_update_dto):
        """Test update_layout when layout exists."""
        # Setup
        layout_id = uuid4()
        
        # Mock the db model import
        with patch('scheduler_api.services.schedule_layout_service.ScheduleLayoutUpdate') as mock_db_update:
            mock_db_update_instance = MagicMock()
            mock_db_update.return_value = mock_db_update_instance
            
            mock_updated_layout = MagicMock()
            mock_updated_layout.id = layout_id
            mock_updated_layout.name = sample_update_dto.name
            mock_updated_layout.description = sample_update_dto.description
            mock_updated_layout.date_range_start = datetime.utcnow()
            mock_updated_layout.date_range_end = datetime.utcnow() + timedelta(days=7)
            mock_updated_layout.worker_ids = []
            mock_updated_layout.shift_templates = []
            mock_updated_layout.constraints = {}
            mock_updated_layout.created_at = datetime.utcnow()
            mock_updated_layout.updated_at = datetime.utcnow()
            
            mock_repository.update.return_value = mock_updated_layout
            
            # Execute
            result = service.update_layout(layout_id, sample_update_dto)
            
            # Verify
            mock_repository.update.assert_called_once_with(layout_id, mock_db_update_instance)
            assert isinstance(result, ScheduleLayoutResponse)
            assert result.name == sample_update_dto.name
            assert result.description == sample_update_dto.description
    
    def test_update_layout_not_found(self, service, mock_repository, sample_update_dto):
        """Test update_layout when layout doesn't exist."""
        # Setup
        layout_id = uuid4()
        
        with patch('scheduler_api.services.schedule_layout_service.ScheduleLayoutUpdate'):
            mock_repository.update.return_value = None
            
            # Execute
            result = service.update_layout(layout_id, sample_update_dto)
            
            # Verify
            assert result is None
    
    def test_delete_layout(self, service, mock_repository):
        """Test delete_layout method."""
        # Setup
        layout_id = uuid4()
        mock_repository.delete.return_value = True
        
        # Execute
        result = service.delete_layout(layout_id)
        
        # Verify
        mock_repository.delete.assert_called_once_with(layout_id)
        assert result is True
    
    def test_generate_schedule_success(self, service, mock_repository):
        """Test generate_schedule method successfully."""
        # Setup
        layout_id = uuid4()
        
        mock_layout = MagicMock()
        mock_layout.id = layout_id
        mock_layout.name = "Test Layout"
        mock_layout.date_range_start = datetime.utcnow()
        mock_layout.date_range_end = datetime.utcnow() + timedelta(days=7)
        mock_layout.shift_templates = [{"name": "Morning", "hours": 8}]
        mock_layout.worker_ids = [uuid4()]
        mock_layout.constraints = {"max_hours": 40}
        mock_layout.created_at = datetime.utcnow()
        
        mock_repository.get_by_id.return_value = mock_layout
        
        # Mock the Celery task
        with patch('scheduler_api.services.schedule_layout_service.generate_schedule_from_layout') as mock_task:
            mock_task_result = MagicMock()
            mock_task_result.id = "test-task-id"
            mock_task.delay.return_value = mock_task_result
            
            # Execute
            result = service.generate_schedule(layout_id)
            
            # Verify
            mock_repository.get_by_id.assert_called_once_with(layout_id)
            mock_task.delay.assert_called_once()
            
            assert result.layout_id == layout_id
            assert result.task_id == "test-task-id"
            assert result.status == "queued"
            assert "test-task-id" in result.message
    
    def test_generate_schedule_layout_not_found(self, service, mock_repository):
        """Test generate_schedule when layout doesn't exist."""
        # Setup
        layout_id = uuid4()
        mock_repository.get_by_id.return_value = None
        
        # Execute & Verify
        with pytest.raises(ValueError, match=f"Schedule layout with ID {layout_id} not found"):
            service.generate_schedule(layout_id)
    
    def test_generate_schedule_celery_error(self, service, mock_repository):
        """Test generate_schedule when Celery task fails."""
        # Setup
        layout_id = uuid4()
        
        mock_layout = MagicMock()
        mock_layout.id = layout_id
        mock_layout.name = "Test Layout"
        mock_layout.date_range_start = datetime.utcnow()
        mock_layout.date_range_end = datetime.utcnow() + timedelta(days=7)
        mock_layout.shift_templates = []
        mock_layout.worker_ids = []
        mock_layout.constraints = {}
        mock_layout.created_at = datetime.utcnow()
        
        mock_repository.get_by_id.return_value = mock_layout
        
        # Mock the Celery task to raise an exception
        with patch('scheduler_api.services.schedule_layout_service.generate_schedule_from_layout') as mock_task:
            mock_task.delay.side_effect = Exception("Celery error")
            
            # Execute & Verify
            with pytest.raises(Exception, match="Celery error"):
                service.generate_schedule(layout_id)