"""Test GA DTOs and domain models."""
import pytest
from datetime import datetime, timedelta
from uuid import uuid4


class TestGADTOs:
    """Test GA DTO validation and serialization."""
    
    def test_schedule_layout_dto_creation(self, sample_schedule_layout_dto):
        """Test ScheduleLayoutDTO creation and validation."""
        assert sample_schedule_layout_dto.name == "Test Layout"
        assert isinstance(sample_schedule_layout_dto.date_range_start, datetime)
        assert isinstance(sample_schedule_layout_dto.date_range_end, datetime)
        assert len(sample_schedule_layout_dto.worker_ids) == 5
        assert len(sample_schedule_layout_dto.shift_templates) == 2
        assert sample_schedule_layout_dto.constraints["max_hours_per_week"] == 40
    
    def test_schedule_layout_dto_serialization(self, sample_schedule_layout_dto):
        """Test ScheduleLayoutDTO serialization to dict."""
        dto_dict = sample_schedule_layout_dto.model_dump()
        
        assert "id" in dto_dict
        assert "name" in dto_dict
        assert "date_range_start" in dto_dict
        assert "date_range_end" in dto_dict
        assert "worker_ids" in dto_dict
        assert "shift_templates" in dto_dict
        assert "constraints" in dto_dict
        assert "created_at" in dto_dict
        
        # Ensure datetime fields are ISO format strings
        assert isinstance(dto_dict["date_range_start"], str)
        assert isinstance(dto_dict["date_range_end"], str)
        assert isinstance(dto_dict["created_at"], str)
    
    def test_schedule_dto_creation(self, sample_schedule_dto):
        """Test ScheduleDTO creation and validation."""
        assert sample_schedule_dto.name == "Test Schedule"
        assert sample_schedule_dto.fitness == 0.8
        assert len(sample_schedule_dto.assignments) == 1
        assert isinstance(sample_schedule_dto.created_at, datetime)
    
    def test_schedule_dto_serialization(self, sample_schedule_dto):
        """Test ScheduleDTO serialization to dict."""
        dto_dict = sample_schedule_dto.model_dump()
        
        assert "id" in dto_dict
        assert "name" in dto_dict
        assert "assignments" in dto_dict
        assert "fitness" in dto_dict
        assert "created_at" in dto_dict
        assert isinstance(dto_dict["assignments"], list)
        assert len(dto_dict["assignments"]) == 1
    
    def test_population_dto_creation(self, sample_population_dto):
        """Test PopulationDTO creation and validation."""
        assert sample_population_dto.generation == 1
        assert len(sample_population_dto.schedules) == 1
        assert isinstance(sample_population_dto.layout_id, type(uuid4()))
        assert isinstance(sample_population_dto.created_at, datetime)
    
    def test_population_dto_serialization(self, sample_population_dto):
        """Test PopulationDTO serialization to dict."""
        dto_dict = sample_population_dto.model_dump()
        
        assert "id" in dto_dict
        assert "generation" in dto_dict
        assert "schedules" in dto_dict
        assert "layout_id" in dto_dict
        assert "created_at" in dto_dict
        assert isinstance(dto_dict["schedules"], list)
        assert len(dto_dict["schedules"]) == 1
    
    def test_shift_assignment_dto_validation(self):
        """Test ShiftAssignmentDTO validation with invalid data."""
        from pydantic import ValidationError
        
        # Test with invalid UUID
        with pytest.raises(ValidationError):
            ShiftAssignmentDTO(
                worker_id="not-a-uuid",
                shift_id=uuid4(),
                start_time=datetime.utcnow(),
                end_time=datetime.utcnow() + timedelta(hours=8),
            )
        
        # Test with end_time before start_time
        with pytest.raises(ValidationError):
            ShiftAssignmentDTO(
                worker_id=uuid4(),
                shift_id=uuid4(),
                start_time=datetime.utcnow() + timedelta(hours=8),
                end_time=datetime.utcnow(),
            )


class TestDomainModels:
    """Test domain model functionality."""
    
    def test_schedule_domain_creation(self, sample_schedule):
        """Test Schedule domain model creation."""
        assert sample_schedule.name == "Test Schedule"
        assert sample_schedule.fitness == 0.8
        assert len(sample_schedule.assignments) == 1
        assert isinstance(sample_schedule.created_at, datetime)
    
    def test_schedule_calculate_fitness(self, sample_schedule):
        """Test Schedule.calculate_fitness method."""
        # With fitness already set
        assert sample_schedule.calculate_fitness() == 0.8
        
        # Without fitness set
        schedule = Schedule(name="Test")
        assert schedule.calculate_fitness() == 0.0
    
    def test_population_domain_creation(self, sample_population):
        """Test Population domain model creation."""
        assert sample_population.generation == 1
        assert len(sample_population.schedules) == 1
        assert isinstance(sample_population.layout_id, type(uuid4()))
        assert isinstance(sample_population.created_at, datetime)
    
    def test_population_size(self, sample_population):
        """Test Population.size() method."""
        assert sample_population.size() == 1
        
        # Test with empty population
        empty_population = Population()
        assert empty_population.size() == 0
    
    def test_population_get_best_schedule(self, sample_population):
        """Test Population.get_best_schedule() method."""
        best = sample_population.get_best_schedule()
        assert best.name == "Test Schedule"
        assert best.fitness == 0.8
    
    def test_population_get_best_schedule_empty(self):
        """Test Population.get_best_schedule() with empty population raises error."""
        empty_population = Population()
        
        with pytest.raises(ValueError, match="Population has no schedules"):
            empty_population.get_best_schedule()
    
    def test_schedule_layout_domain_creation(self, sample_schedule_layout):
        """Test ScheduleLayout domain model creation."""
        assert sample_schedule_layout.name == "Test Layout"
        assert isinstance(sample_schedule_layout.date_range_start, datetime)
        assert isinstance(sample_schedule_layout.date_range_end, datetime)
        assert len(sample_schedule_layout.worker_ids) == 5
        assert len(sample_schedule_layout.shift_templates) == 2
        assert sample_schedule_layout.constraints["max_hours_per_week"] == 40
        assert isinstance(sample_schedule_layout.created_at, datetime)


class TestDTOToDomainConversion:
    """Test conversion between DTOs and domain models."""
    
    def test_mapper_schedule_conversion(self, sample_schedule_dto):
        """Test ScheduleDTO <-> Schedule conversion."""
        from scheduler_api.mappers.ga_mapper import schedule_from_dto, schedule_to_dto
        
        # DTO -> Domain
        domain_schedule = schedule_from_dto(sample_schedule_dto)
        assert domain_schedule.name == sample_schedule_dto.name
        assert domain_schedule.fitness == sample_schedule_dto.fitness
        assert len(domain_schedule.assignments) == len(sample_schedule_dto.assignments)
        
        # Domain -> DTO
        back_to_dto = schedule_to_dto(domain_schedule)
        assert back_to_dto.name == sample_schedule_dto.name
        assert back_to_dto.fitness == sample_schedule_dto.fitness
        assert len(back_to_dto.assignments) == len(sample_schedule_dto.assignments)
    
    def test_mapper_population_conversion(self, sample_population_dto):
        """Test PopulationDTO <-> Population conversion."""
        from scheduler_api.mappers.ga_mapper import population_from_dto, population_to_dto
        
        # DTO -> Domain
        domain_population = population_from_dto(sample_population_dto)
        assert domain_population.generation == sample_population_dto.generation
        assert domain_population.layout_id == sample_population_dto.layout_id
        assert len(domain_population.schedules) == len(sample_population_dto.schedules)
        
        # Domain -> DTO
        back_to_dto = population_to_dto(domain_population)
        assert back_to_dto.generation == sample_population_dto.generation
        assert back_to_dto.layout_id == sample_population_dto.layout_id
        assert len(back_to_dto.schedules) == len(sample_population_dto.schedules)
    
    def test_mapper_schedule_layout_conversion(self, sample_schedule_layout_dto):
        """Test ScheduleLayoutDTO <-> ScheduleLayout conversion."""
        from scheduler_api.mappers.ga_mapper import (
            schedule_layout_from_dto,
            schedule_layout_to_dto,
        )
        
        # DTO -> Domain
        domain_layout = schedule_layout_from_dto(sample_schedule_layout_dto)
        assert domain_layout.name == sample_schedule_layout_dto.name
        assert domain_layout.date_range_start == sample_schedule_layout_dto.date_range_start
        assert domain_layout.date_range_end == sample_schedule_layout_dto.date_range_end
        assert len(domain_layout.worker_ids) == len(sample_schedule_layout_dto.worker_ids)
        
        # Domain -> DTO
        back_to_dto = schedule_layout_to_dto(domain_layout)
        assert back_to_dto.name == sample_schedule_layout_dto.name
        assert back_to_dto.date_range_start == sample_schedule_layout_dto.date_range_start
        assert back_to_dto.date_range_end == sample_schedule_layout_dto.date_range_end
        assert len(back_to_dto.worker_ids) == len(sample_schedule_layout_dto.worker_ids)