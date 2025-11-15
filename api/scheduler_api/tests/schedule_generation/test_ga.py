import pytest
import asyncio

from scheduler_api.genetic.ga import run_genetic_algorithm, GAConfig
from scheduler_api.genetic.scoring import ScoreResult


@pytest.mark.asyncio
async def test_ga_runs(simple_schedule_template):
    def trivial_scorer(schedule):
        return ScoreResult(score=1.0)

    result = await run_genetic_algorithm(
        schedule_template=simple_schedule_template,
        scorers=[trivial_scorer],
        config=GAConfig(population_size=5, generations=3),
    )

    assert result is not None
