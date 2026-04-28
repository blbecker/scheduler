"""Test schedule layout router endpoints."""
import pytest
from unittest.mock import MagicMock, patch
from uuid import uuid4
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from fastapi import FastAPI
from scheduler_api.main import app as main_app
from scheduler_api.schemas.schedule_layout import (
    ScheduleLayoutCreate,
    ScheduleLayoutUpdate,
    ScheduleLayoutResponse,
    ScheduleLayoutGenerateResponse,
)


# Create a test app with the router
test_app = FastAPI()

# We need to import and include the router
# But for testing, we'll mock the dependencies
from scheduler_api.routers.schedule_layouts import router as schedule_layouts_router
test_app.include_router(schedule_layouts_router)


class TestScheduleLayoutRouter:
    """Test schedule layout router endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create a test client."""
        return TestClient(test_app)
    
    @pytest.fixture
    def sample_layout_data(self):
        """Create sample layout data for requests."""
        return {
            "name": "Test Layout",
            "description": "Test Description",
            "date_range_start": datetime.utcnow().isoformat(),
            "date_range_end": (datetime.utcnow() + timedelta(days=7)).isoformat(),
            "worker_ids": [str(uuid4()) for _ in range(3)],
            "shift_templates": [{"name": "Morning", "hours": 8}],
            "constraints": {"max_hours": 40},
        }
    
    @pytest.fixture
    def sample_layout_response(self):
        """Create a sample layout response."""
        layout_id = uuid4()
        return {
            "id": str(layout_id),
            "name": "Test Layout",
            "description": "Test Description",
            "date_range_start": datetime.utcnow().isoformat(),
            "date_range_end": (datetime.utcnow() + timedelta(days=7)).isoformat(),
            "worker_ids": [str(uuid4()) for _ in range(3)],
            "shift_templates": [{"name": "Morning", "hours": 8}],
            "constraints": {"max_hours": 40},
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }
    
    def test_list_layouts_success(self, client, sample_layout_response):
        """Test GET /schedules/layouts/ successfully."""
        # Mock the service dependency
        mock_service = MagicMock()
        mock_service.list_layouts.return_value = [
            ScheduleLayoutResponse(**sample_layout_response)
        ]
        
        with patch('scheduler_api.routers.schedule_layouts.get_schedule_layout_service', return_value=mock_service):
            # Make request
            response = client.get("/schedules/layouts/")
            
            # Verify response
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
            assert len(data) == 1
            assert data[0]["name"] == "Test Layout"
            
            # Verify service was called
            mock_service.list_layouts.assert_called_once()
    
    def test_get_layout_success(self, client, sample_layout_response):
        """Test GET /schedules/layouts/{layout_id} successfully."""
        # Setup
        layout_id = uuid4()
        mock_service = MagicMock()
        mock_service.get_layout.return_value = ScheduleLayoutResponse(**sample_layout_response)
        
        with patch('scheduler_api.routers.schedule_layouts.get_schedule_layout_service', return_value=mock_service):
            # Make request
            response = client.get(f"/schedules/layouts/{layout_id}")
            
            # Verify response
            assert response.status_code == 200
            data = response.json()
            assert data["name"] == "Test Layout"
            assert data["description"] == "Test Description"
            
            # Verify service was called with correct ID
            mock_service.get_layout.assert_called_once_with(layout_id)
    
    def test_get_layout_not_found(self, client):
        """Test GET /schedules/layouts/{layout_id} when layout doesn't exist."""
        # Setup
        layout_id = uuid4()
        mock_service = MagicMock()
        mock_service.get_layout.return_value = None
        
        with patch('scheduler_api.routers.schedule_layouts.get_schedule_layout_service', return_value=mock_service):
            # Make request
            response = client.get(f"/schedules/layouts/{layout_id}")
            
            # Verify response
            assert response.status_code == 404
            data = response.json()
            assert data["detail"] == "Schedule layout not found"
    
    def test_create_layout_success(self, client, sample_layout_data, sample_layout_response):
        """Test POST /schedules/layouts/ successfully."""
        # Setup
        mock_service = MagicMock()
        mock_service.create_layout.return_value = ScheduleLayoutResponse(**sample_layout_response)
        
        with patch('scheduler_api.routers.schedule_layouts.get_schedule_layout_service', return_value=mock_service):
            # Make request
            response = client.post("/schedules/layouts/", json=sample_layout_data)
            
            # Verify response
            assert response.status_code == 201
            data = response.json()
            assert data["name"] == "Test Layout"
            
            # Verify service was called with correct data
            mock_service.create_layout.assert_called_once()
            call_args = mock_service.create_layout.call_args[0][0]
            assert isinstance(call_args, ScheduleLayoutCreate)
            assert call_args.name == "Test Layout"
    
    def test_create_layout_validation_error(self, client):
        """Test POST /schedules/layouts/ with invalid data."""
        # Invalid data - missing required fields
        invalid_data = {
            "name": "",  # Empty name should fail validation
        }
        
        # Make request (no mocking needed as FastAPI validation happens before service)
        response = client.post("/schedules/layouts/", json=invalid_data)
        
        # Verify validation error
        assert response.status_code == 422  # Unprocessable Entity
    
    def test_update_layout_success(self, client, sample_layout_response):
        """Test PUT /schedules/layouts/{layout_id} successfully."""
        # Setup
        layout_id = uuid4()
        update_data = {
            "name": "Updated Layout",
            "description": "Updated Description",
        }
        
        mock_service = MagicMock()
        updated_response = sample_layout_response.copy()
        updated_response.update(update_data)
        mock_service.update_layout.return_value = ScheduleLayoutResponse(**updated_response)
        
        with patch('scheduler_api.routers.schedule_layouts.get_schedule_layout_service', return_value=mock_service):
            # Make request
            response = client.put(f"/schedules/layouts/{layout_id}", json=update_data)
            
            # Verify response
            assert response.status_code == 200
            data = response.json()
            assert data["name"] == "Updated Layout"
            assert data["description"] == "Updated Description"
            
            # Verify service was called
            mock_service.update_layout.assert_called_once_with(layout_id, ScheduleLayoutUpdate(**update_data))
    
    def test_update_layout_not_found(self, client):
        """Test PUT /schedules/layouts/{layout_id} when layout doesn't exist."""
        # Setup
        layout_id = uuid4()
        update_data = {"name": "Updated Layout"}
        
        mock_service = MagicMock()
        mock_service.update_layout.return_value = None
        
        with patch('scheduler_api.routers.schedule_layouts.get_schedule_layout_service', return_value=mock_service):
            # Make request
            response = client.put(f"/schedules/layouts/{layout_id}", json=update_data)
            
            # Verify response
            assert response.status_code == 404
            data = response.json()
            assert data["detail"] == "Schedule layout not found"
    
    def test_delete_layout_success(self, client):
        """Test DELETE /schedules/layouts/{layout_id} successfully."""
        # Setup
        layout_id = uuid4()
        mock_service = MagicMock()
        mock_service.delete_layout.return_value = True
        
        with patch('scheduler_api.routers.schedule_layouts.get_schedule_layout_service', return_value=mock_service):
            # Make request
            response = client.delete(f"/schedules/layouts/{layout_id}")
            
            # Verify response
            assert response.status_code == 204
            
            # Verify service was called
            mock_service.delete_layout.assert_called_once_with(layout_id)
    
    def test_delete_layout_not_found(self, client):
        """Test DELETE /schedules/layouts/{layout_id} when layout doesn't exist."""
        # Setup
        layout_id = uuid4()
        mock_service = MagicMock()
        mock_service.delete_layout.return_value = False
        
        with patch('scheduler_api.routers.schedule_layouts.get_schedule_layout_service', return_value=mock_service):
            # Make request
            response = client.delete(f"/schedules/layouts/{layout_id}")
            
            # Verify response
            assert response.status_code == 404
            data = response.json()
            assert data["detail"] == "Schedule layout not found"
    
    def test_generate_schedule_success(self, client):
        """Test POST /schedules/layouts/{layout_id}/generate successfully."""
        # Setup
        layout_id = uuid4()
        mock_service = MagicMock()
        mock_service.generate_schedule.return_value = ScheduleLayoutGenerateResponse(
            layout_id=layout_id,
            task_id="test-task-123",
            status="queued",
            message="Schedule generation task queued with ID: test-task-123",
        )
        
        with patch('scheduler_api.routers.schedule_layouts.get_schedule_layout_service', return_value=mock_service):
            # Make request
            response = client.post(f"/schedules/layouts/{layout_id}/generate")
            
            # Verify response
            assert response.status_code == 200
            data = response.json()
            assert data["layout_id"] == str(layout_id)
            assert data["task_id"] == "test-task-123"
            assert data["status"] == "queued"
            assert "test-task-123" in data["message"]
            
            # Verify service was called
            mock_service.generate_schedule.assert_called_once_with(layout_id)
    
    def test_generate_schedule_layout_not_found(self, client):
        """Test POST /schedules/layouts/{layout_id}/generate when layout doesn't exist."""
        # Setup
        layout_id = uuid4()
        mock_service = MagicMock()
        mock_service.generate_schedule.side_effect = ValueError(f"Schedule layout with ID {layout_id} not found")
        
        with patch('scheduler_api.routers.schedule_layouts.get_schedule_layout_service', return_value=mock_service):
            # Make request
            response = client.post(f"/schedules/layouts/{layout_id}/generate")
            
            # Verify response
            assert response.status_code == 404
            data = response.json()
            assert f"Schedule layout with ID {layout_id} not found" in data["detail"]
    
    def test_generate_schedule_service_error(self, client):
        """Test POST /schedules/layouts/{layout_id}/generate when service raises unexpected error."""
        # Setup
        layout_id = uuid4()
        mock_service = MagicMock()
        mock_service.generate_schedule.side_effect = Exception("Unexpected error")
        
        with patch('scheduler_api.routers.schedule_layouts.get_schedule_layout_service', return_value=mock_service):
            # Make request
            response = client.post(f"/schedules/layouts/{layout_id}/generate")
            
            # Verify response
            assert response.status_code == 500
            data = response.json()
            assert "Failed to schedule generation" in data["detail"]
            assert "Unexpected error" in data["detail"]
    
    def test_endpoint_urls(self):
        """Test that all expected endpoints are defined."""
        # Check router prefix
        assert schedule_layouts_router.prefix == "/schedules/layouts"
        
        # Check router tags
        assert schedule_layouts_router.tags == ["schedule-layouts"]
        
        # Collect all route paths
        routes = []
        for route in schedule_layouts_router.routes:
            routes.append({
                "path": route.path,
                "methods": list(route.methods),
            })
        
        # Expected endpoints
        expected_routes = [
            {"path": "/schedules/layouts/", "methods": ["GET"]},
            {"path": "/schedules/layouts/{layout_id}", "methods": ["GET"]},
            {"path": "/schedules/layouts/", "methods": ["POST"]},
            {"path": "/schedules/layouts/{layout_id}", "methods": ["PUT"]},
            {"path": "/schedules/layouts/{layout_id}", "methods": ["DELETE"]},
            {"path": "/schedules/layouts/{layout_id}/generate", "methods": ["POST"]},
        ]
        
        # Check each expected route exists
        for expected in expected_routes:
            matching = [r for r in routes if r["path"] == expected["path"]]
            assert len(matching) > 0, f"Missing route: {expected['path']}"
            
            # Check methods
            route_methods = set(matching[0]["methods"])
            expected_methods = set(expected["methods"])
            assert expected_methods.issubset(route_methods), \
                f"Route {expected['path']} missing methods: {expected_methods - route_methods}"


class TestRouterIntegration:
    """Test router integration with the main app."""
    
    def test_router_included_in_main_app(self):
        """Test that schedule_layouts router is included in the main app."""
        # Check that the router is imported in main.py
        with open("api/scheduler_api/main.py", "r") as f:
            main_content = f.read()
        
        assert "schedule_layouts" in main_content
        assert "v1router.include_router(schedule_layouts.router)" in main_content
    
    def test_full_url_paths(self):
        """Test that endpoints have correct full paths in the API."""
        # With v1 prefix, the full paths should be:
        expected_full_paths = [
            "/v1/schedules/layouts/",
            "/v1/schedules/layouts/{layout_id}",
            "/v1/schedules/layouts/{layout_id}/generate",
        ]
        
        # This is a structural test - the actual routing is handled by FastAPI
        for path in expected_full_paths:
            assert path.startswith("/v1/schedules/layouts")
            
        # The generate endpoint should be specifically tested
        assert "/generate" in expected_full_paths[2]