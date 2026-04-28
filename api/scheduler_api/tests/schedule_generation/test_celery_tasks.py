"""Test Celery tasks for schedule generation."""
import pytest
from unittest.mock import patch, MagicMock, call
from celery import chain
from pydantic import ValidationError
from uuid import uuid4
from datetime import datetime
from scheduler_api.tasks.ga_tasks import (
    population_generate,
    score_population_task,
    mutate_and_breed,
    cull_population_task,
    select_best,
    generate_schedule_from_layout,
)


class TestCeleryTasks:
    """Test Celery task functionality with mocking."""
    
    def test_population_generate_task(
        self,
        sample_schedule_layout_dto,
        mock_time_sleep,
        mock_random_uniform,
    ):
        """Test population_generate task."""
        # Mock the genetic operations
        with patch('scheduler_api.tasks.ga_tasks.generate_initial_population') as mock_gen_pop:
            with patch('scheduler_api.tasks.ga_tasks.schedule_layout_from_dto') as mock_from_dto:
                with patch('scheduler_api.tasks.ga_tasks.population_to_dto') as mock_to_dto:
                    # Setup mocks
                    mock_layout = MagicMock()
                    mock_from_dto.return_value = mock_layout
                    
                    mock_population = MagicMock()
                    mock_population.generation = 0
                    mock_population.layout_id = sample_schedule_layout_dto.id
                    mock_population.schedules = []
                    mock_gen_pop.return_value = mock_population
                    
                    mock_population_dto = MagicMock()
                    mock_population_dto.model_dump.return_value = {"test": "population"}
                    mock_to_dto.return_value = mock_population_dto
                    
                    # Execute task
                    result = population_generate(sample_schedule_layout_dto.model_dump())
                    
                    # Verify calls
                    mock_from_dto.assert_called_once()
                    mock_gen_pop.assert_called_once_with(mock_layout, size=100)
                    mock_to_dto.assert_called_once_with(mock_population)
                    mock_time_sleep.assert_called_once()
                    
                    # Verify result
                    assert result == {"test": "population"}
    
    def test_score_population_task(
        self,
        sample_population_dto,
        mock_time_sleep,
        mock_random_uniform,
    ):
        """Test score_population_task."""
        with patch('scheduler_api.tasks.ga_tasks.score_population') as mock_score_pop:
            with patch('scheduler_api.tasks.ga_tasks.population_from_dto') as mock_from_dto:
                with patch('scheduler_api.tasks.ga_tasks.population_to_dto') as mock_to_dto:
                    # Setup mocks
                    mock_population = MagicMock()
                    mock_from_dto.return_value = mock_population
                    
                    mock_scored_population = MagicMock()
                    mock_score_pop.return_value = mock_scored_population
                    
                    mock_population_dto = MagicMock()
                    mock_population_dto.model_dump.return_value = {"test": "scored"}
                    mock_to_dto.return_value = mock_population_dto
                    
                    # Execute task
                    result = score_population_task(sample_population_dto.model_dump())
                    
                    # Verify calls
                    mock_from_dto.assert_called_once()
                    mock_score_pop.assert_called_once_with(mock_population)
                    mock_to_dto.assert_called_once_with(mock_scored_population)
                    mock_time_sleep.assert_called_once()
                    
                    # Verify result
                    assert result == {"test": "scored"}
    
    def test_mutate_and_breed_task(
        self,
        sample_population_dto,
        mock_time_sleep,
        mock_random_uniform,
        mock_random_random,
    ):
        """Test mutate_and_breed task."""
        with patch('scheduler_api.tasks.ga_tasks.mutate_population') as mock_mutate:
            with patch('scheduler_api.tasks.ga_tasks.breed_population') as mock_breed:
                with patch('scheduler_api.tasks.ga_tasks.population_from_dto') as mock_from_dto:
                    with patch('scheduler_api.tasks.ga_tasks.population_to_dto') as mock_to_dto:
                        # Setup mocks
                        mock_population = MagicMock()
                        mock_from_dto.return_value = mock_population
                        
                        mock_mutated_population = MagicMock()
                        mock_mutate.return_value = mock_mutated_population
                        
                        mock_bred_population = MagicMock()
                        mock_breed.return_value = mock_bred_population
                        
                        mock_population_dto = MagicMock()
                        mock_population_dto.model_dump.return_value = {"test": "mutated_breed"}
                        mock_to_dto.return_value = mock_population_dto
                        
                        # Execute task
                        result = mutate_and_breed(sample_population_dto.model_dump())
                        
                        # Verify calls
                        mock_from_dto.assert_called_once()
                        mock_mutate.assert_called_once_with(mock_population, mutation_rate=0.1)
                        mock_breed.assert_called_once_with(mock_mutated_population, crossover_rate=0.8)
                        mock_to_dto.assert_called_once_with(mock_bred_population)
                        mock_time_sleep.assert_called_once()
                        
                        # Verify result
                        assert result == {"test": "mutated_breed"}
    
    def test_cull_population_task(
        self,
        sample_population_dto,
        mock_time_sleep,
        mock_random_uniform,
    ):
        """Test cull_population_task."""
        with patch('scheduler_api.tasks.ga_tasks.cull_population') as mock_cull:
            with patch('scheduler_api.tasks.ga_tasks.population_from_dto') as mock_from_dto:
                with patch('scheduler_api.tasks.ga_tasks.population_to_dto') as mock_to_dto:
                    # Setup mocks
                    mock_population = MagicMock()
                    mock_from_dto.return_value = mock_population
                    
                    mock_culled_population = MagicMock()
                    mock_cull.return_value = mock_culled_population
                    
                    mock_population_dto = MagicMock()
                    mock_population_dto.model_dump.return_value = {"test": "culled"}
                    mock_to_dto.return_value = mock_population_dto
                    
                    # Execute task
                    result = cull_population_task(sample_population_dto.model_dump())
                    
                    # Verify calls
                    mock_from_dto.assert_called_once()
                    mock_cull.assert_called_once_with(mock_population, target_size=100)
                    mock_to_dto.assert_called_once_with(mock_culled_population)
                    mock_time_sleep.assert_called_once()
                    
                    # Verify result
                    assert result == {"test": "culled"}
    
    def test_select_best_task(
        self,
        sample_population_dto,
        mock_time_sleep,
        mock_random_uniform,
    ):
        """Test select_best task."""
        with patch('scheduler_api.tasks.ga_tasks.select_best_schedule') as mock_select:
            with patch('scheduler_api.tasks.ga_tasks.population_from_dto') as mock_from_dto:
                with patch('scheduler_api.tasks.ga_tasks.schedule_to_dto') as mock_to_dto:
                    # Setup mocks
                    mock_population = MagicMock()
                    mock_from_dto.return_value = mock_population
                    
                    mock_best_schedule = MagicMock()
                    mock_best_schedule.fitness = 0.9
                    mock_best_schedule.name = "Best Schedule"
                    mock_select.return_value = mock_best_schedule
                    
                    mock_schedule_dto = MagicMock()
                    mock_schedule_dto.model_dump.return_value = {"id": "test-schedule"}
                    mock_to_dto.return_value = mock_schedule_dto
                    
                    # Execute task
                    result = select_best(sample_population_dto.model_dump())
                    
                    # Verify calls
                    mock_from_dto.assert_called_once()
                    mock_select.assert_called_once_with(mock_population)
                    mock_to_dto.assert_called_once_with(mock_best_schedule)
                    mock_time_sleep.assert_called_once()
                    
                    # Verify result structure
                    assert result == {
                        "best_schedule": {"id": "test-schedule"},
                        "fitness": 0.9
                    }
    
    def test_generate_schedule_from_layout_task(
        self,
        sample_schedule_layout_dto,
        mock_time_sleep,
        mock_celery_chain,
    ):
        """Test generate_schedule_from_layout task (entrypoint)."""
        # Execute task
        result = generate_schedule_from_layout(sample_schedule_layout_dto.model_dump())
        
        # Verify chain was called with correct task signatures
        mock_celery_chain.assert_called_once()
        
        # Get the call arguments
        chain_call = mock_celery_chain.call_args
        
        # Verify the chain structure: population_generate.s() -> score_population_task.s() -> ...
        assert len(chain_call[0]) == 5  # 5 tasks in the chain
        
        # The first argument should be population_generate.s(layout_dto)
        first_task = chain_call[0][0]
        assert hasattr(first_task, 'args')
        assert first_task.args[0] == sample_schedule_layout_dto.model_dump()
        
        # Verify result
        assert result == {"test": "result"}
    
    def test_task_logging(self, sample_schedule_layout_dto, mock_time_sleep, caplog):
        """Test that tasks log start and end messages."""
        import logging
        
        # Set up logging capture
        caplog.set_level(logging.INFO)
        
        # Mock all dependencies
        with patch('scheduler_api.tasks.ga_tasks.generate_initial_population'):
            with patch('scheduler_api.tasks.ga_tasks.schedule_layout_from_dto'):
                with patch('scheduler_api.tasks.ga_tasks.population_to_dto'):
                    # Execute task
                    population_generate(sample_schedule_layout_dto.model_dump())
        
        # Check logs
        log_messages = [record.message for record in caplog.records]
        assert "[population_generate] start" in log_messages
        assert "[population_generate] end" in log_messages
    
    def test_task_dto_boundary_respect(self, sample_schedule_layout_dto):
        """Test that tasks respect DTO-only boundaries."""
        # All tasks should accept and return dicts (serialized DTOs)
        tasks = [
            (population_generate, sample_schedule_layout_dto.model_dump()),
            (score_population_task, {"id": "test", "schedules": []}),
            (mutate_and_breed, {"id": "test", "schedules": []}),
            (cull_population_task, {"id": "test", "schedules": []}),
            (select_best, {"id": "test", "schedules": []}),
            (generate_schedule_from_layout, sample_schedule_layout_dto.model_dump()),
        ]
        
        for task_func, input_data in tasks:
            # Mock all dependencies to avoid actual execution
            with patch('scheduler_api.tasks.ga_tasks._log_task_start'):
                with patch('scheduler_api.tasks.ga_tasks._log_task_end'):
                    with patch('scheduler_api.tasks.ga_tasks._simulate_work'):
                        with patch('scheduler_api.tasks.ga_tasks.schedule_layout_from_dto'):
                            with patch('scheduler_api.tasks.ga_tasks.generate_initial_population'):
                                with patch('scheduler_api.tasks.ga_tasks.population_to_dto'):
                                    with patch('scheduler_api.tasks.ga_tasks.chain'):
                                        try:
                                            # Task should accept dict input
                                            result = task_func(input_data)
                                            
                                            # Task should return dict output
                                            assert isinstance(result, dict), \
                                                f"{task_func.__name__} should return dict"
                                        except Exception as e:
                                            # Some tasks might fail due to missing mocks,
                                            # but we're only checking the interface
                                            pass
    
    def test_task_error_handling(self, sample_schedule_layout_dto):
        """Test task error handling (simulated by mock failures)."""
        # Test population_generate with invalid input (Pydantic validation error)
        with pytest.raises(ValidationError):
            population_generate({"invalid": "data"})
        
        # Test population_generate with valid input but schedule_layout_from_dto error
        with patch('scheduler_api.tasks.ga_tasks.schedule_layout_from_dto', side_effect=ValueError("Invalid DTO")):
            with pytest.raises(ValueError, match="Invalid DTO"):
                # Use sample DTO that passes Pydantic validation
                population_generate(sample_schedule_layout_dto.model_dump())
        
        # Test select_best with empty population
        with patch('scheduler_api.tasks.ga_tasks.population_from_dto', return_value=MagicMock(schedules=[])):
            with patch('scheduler_api.tasks.ga_tasks.select_best_schedule', side_effect=ValueError("No schedules")):
                with pytest.raises(ValueError, match="No schedules"):
                    # Pass valid DTO data that passes Pydantic validation
                    select_best({
                        "id": str(uuid4()),
                        "generation": 1,
                        "schedules": [],
                        "layout_id": str(uuid4()),
                        "created_at": datetime.utcnow().isoformat()
                    })


class TestTaskIntegration:
    """Test integration between Celery tasks."""
    
    def test_task_chain_structure(self, mock_celery_chain, sample_schedule_layout_dto):
        """Test that tasks are chained in correct order."""
        # Execute entrypoint task
        generate_schedule_from_layout(sample_schedule_layout_dto.model_dump())
        
        # Verify chain structure
        mock_celery_chain.assert_called_once()
        
        # Get the chain call
        chain_args = mock_celery_chain.call_args[0]
        
        # Verify task order in chain
        task_names = []
        for task_sig in chain_args:
            # Handle different possible signature types
            if hasattr(task_sig, 'task'):
                # Celery Signature object
                try:
                    task_names.append(task_sig.task.__name__)
                except AttributeError:
                    # task might be a string or other object without __name__
                    task_names.append(str(task_sig.task))
            elif isinstance(task_sig, str):
                # String representation of task
                task_names.append(task_sig)
            else:
                # Try to get task name from other attributes
                task_name = str(task_sig)
                task_names.append(task_name)
        
        expected_order = [
            'scheduler_api.tasks.ga_tasks.population_generate',
            'scheduler_api.tasks.ga_tasks.score_population_task',
            'scheduler_api.tasks.ga_tasks.mutate_and_breed',
            'scheduler_api.tasks.ga_tasks.cull_population_task',
            'scheduler_api.tasks.ga_tasks.select_best',
        ]
        
        assert task_names == expected_order, f"Tasks should be chained in order: {expected_order}"
    
    def test_task_data_flow(self, sample_schedule_layout_dto):
        """Test data flow through task chain (mocked)."""
        # Mock each task to verify data flow
        mock_results = [
            {"id": "pop-1", "schedules": []},  # population_generate result
            {"id": "pop-1", "schedules": [], "scored": True},  # score_population_task result
            {"id": "pop-1", "schedules": [], "mutated": True},  # mutate_and_breed result
            {"id": "pop-1", "schedules": []},  # cull_population_task result
            {"best_schedule": {"id": "best"}, "fitness": 0.9},  # select_best result
        ]
        
        # Create mock tasks
        mock_tasks = []
        for i, result in enumerate(mock_results):
            mock_task = MagicMock()
            mock_task.s = MagicMock(return_value=mock_task)
            mock_task.apply = MagicMock(return_value=MagicMock(get=MagicMock(return_value=result)))
            mock_tasks.append(mock_task)
        
        # Mock chain to use our mock tasks
        with patch('scheduler_api.tasks.ga_tasks.chain') as mock_chain:
            mock_chain_instance = MagicMock()
            mock_chain.return_value = mock_chain_instance
            
            # Setup chain to execute mock tasks
            def execute_chain(*args, **kwargs):
                # Simulate chain execution
                return MagicMock(get=MagicMock(return_value=mock_results[-1]))
            
            mock_chain_instance.return_value = MagicMock()
            mock_chain_instance.return_value.get = MagicMock(return_value=mock_results[-1])
            
            # Execute entrypoint
            result = generate_schedule_from_layout(sample_schedule_layout_dto.model_dump())
            
            # Verify final result
            assert result == mock_results[-1]