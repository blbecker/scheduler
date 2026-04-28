from scheduler_api.domain.schedule import Schedule, ShiftAssignment
from scheduler_api.domain.population import Population
from scheduler_api.domain.schedule_layout import ScheduleLayout
from scheduler_api.schemas.ga_dtos import (
    ScheduleDTO,
    ShiftAssignmentDTO,
    PopulationDTO,
    ScheduleLayoutDTO,
)
from uuid import UUID


def schedule_to_dto(schedule: Schedule) -> ScheduleDTO:
    assignment_dtos = [
        ShiftAssignmentDTO(
            worker_id=assignment.worker_id,
            shift_id=assignment.shift_id,
            start_time=assignment.start_time,
            end_time=assignment.end_time,
        )
        for assignment in schedule.assignments
    ]

    return ScheduleDTO(
        id=schedule.id,
        name=schedule.name,
        assignments=assignment_dtos,
        fitness=schedule.fitness,
        created_at=schedule.created_at,
    )


def schedule_from_dto(dto: ScheduleDTO) -> Schedule:
    assignments = [
        ShiftAssignment(
            worker_id=assignment.worker_id,
            shift_id=assignment.shift_id,
            start_time=assignment.start_time,
            end_time=assignment.end_time,
        )
        for assignment in dto.assignments
    ]

    return Schedule(
        id=dto.id,
        name=dto.name,
        assignments=assignments,
        fitness=dto.fitness,
        created_at=dto.created_at,
    )


def population_to_dto(population: Population) -> PopulationDTO:
    schedule_dtos = [schedule_to_dto(schedule) for schedule in population.schedules]

    return PopulationDTO(
        id=population.id,
        generation=population.generation,
        schedules=schedule_dtos,
        layout_id=population.layout_id,
        created_at=population.created_at,
    )


def population_from_dto(dto: PopulationDTO) -> Population:
    schedules = [schedule_from_dto(schedule_dto) for schedule_dto in dto.schedules]

    return Population(
        id=dto.id,
        generation=dto.generation,
        schedules=schedules,
        layout_id=dto.layout_id,
        created_at=dto.created_at,
    )


def schedule_layout_to_dto(layout: ScheduleLayout) -> ScheduleLayoutDTO:
    return ScheduleLayoutDTO(
        id=layout.id,
        name=layout.name,
        date_range_start=layout.date_range_start,
        date_range_end=layout.date_range_end,
        shift_templates=layout.shift_templates,
        worker_ids=layout.worker_ids,
        constraints=layout.constraints,
        created_at=layout.created_at,
    )


def schedule_layout_from_dto(dto: ScheduleLayoutDTO) -> ScheduleLayout:
    return ScheduleLayout(
        id=dto.id,
        name=dto.name,
        date_range_start=dto.date_range_start,
        date_range_end=dto.date_range_end,
        shift_templates=dto.shift_templates,
        worker_ids=dto.worker_ids,
        constraints=dto.constraints,
        created_at=dto.created_at,
    )
