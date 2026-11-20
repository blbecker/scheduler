from __future__ import annotations

from uuid import UUID

from scheduler_api.engine.components.stoppers.generations import (
    GenerationCountStopper,
)
from scheduler_api.engine.models.component_config import (
    GenerationCountStopperConfig,
)
from scheduler_api.engine.models.component_io import StopInput


def make_input(generation: int) -> StopInput:
    return StopInput(
        category="stopper",
        execution_id=UUID(int=1),
        generation=generation,
        population_size=10,
    )


def test_does_not_stop_below_limit():
    result = GenerationCountStopper(
        GenerationCountStopperConfig(max_generations=3)
    ).should_stop(make_input(2))

    assert result.should_stop is False
    assert result.reason is None


def test_stops_at_limit():
    result = GenerationCountStopper(
        GenerationCountStopperConfig(max_generations=3)
    ).should_stop(make_input(3))

    assert result.should_stop is True
    assert result.reason == "generation_limit:3"


def test_stops_above_limit():
    result = GenerationCountStopper(
        GenerationCountStopperConfig(max_generations=3)
    ).should_stop(make_input(4))

    assert result.should_stop is True


def test_stopper_does_not_mutate_input():
    stop_input = make_input(1)
    before = stop_input.model_dump(mode="json")

    GenerationCountStopper().should_stop(stop_input)

    assert stop_input.model_dump(mode="json") == before
