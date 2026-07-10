"""Main solve orchestrator."""

import time
from typing import Any, Optional
from uuid import UUID, uuid4
from dataclasses import dataclass, field
from .evolution import EvolutionEngine
from .population import Population, Candidate
from ..interfaces import Solvable, Stoppable


@dataclass
class SolveResult:
    """Result of a solve execution."""

    id: UUID = field(default_factory=uuid4)
    status: str = "completed"
    best_genome: Any = None
    best_fitness: float = 0.0
    generations: int = 0
    elapsed_time: float = 0.0
    metrics: dict[str, Any] = field(default_factory=dict)
    population: Optional[Population] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert result to dictionary for serialization."""
        return {
            "id": str(self.id),
            "status": self.status,
            "best_fitness": self.best_fitness,
            "generations": self.generations,
            "elapsed_time": self.elapsed_time,
            "metrics": self.metrics,
        }


class SolveOrchestrator:
    """Orchestrates solve execution with evolution engine."""

    def __init__(self, evolution_engine: Optional[EvolutionEngine] = None):
        self.evolution_engine = evolution_engine or EvolutionEngine()

    def solve(
        self, solvable: Solvable, template_id: UUID, parameters: dict[str, Any]
    ) -> SolveResult:
        """Execute solve using genetic algorithm."""
        start_time = time.time()

        # Create context
        context = solvable.create_context(template_id, parameters)

        # Get pipeline configuration
        pipeline = solvable.create_pipeline()

        # Create initial population
        population_size = parameters.get("population_size", 10)
        initial_genomes = solvable.create_initial_population(context, population_size)

        # Convert genomes to initial population
        initial_population = Population(generation=0)
        for genome in initial_genomes:
            candidate = Candidate(
                generation=0,
                genome=genome,
                fitness=0.0,  # Will be scored in first evolution cycle
                metadata={"type": "initial"},
            )
            initial_population.add_candidate(candidate)

        # Score initial population
        current_population = initial_population

        # Evolution loop
        generation = 0
        best_fitness_history = []

        while True:
            # Evolve population
            current_population = self.evolution_engine.evolve_population(
                population=current_population,
                genome_operators=pipeline.genome_operators,
                scorers=pipeline.scorers,
                constraints=pipeline.constraints,
                selector=pipeline.selector,
                context=context,
            )

            generation += 1

            # Track best fitness
            best_fitness = current_population.get_best_fitness()
            best_fitness_history.append(best_fitness)

            # Log progress
            self._log_progress(generation, best_fitness, current_population)

            # Check stop conditions
            should_stop = False
            for stop_condition in pipeline.stop_conditions:
                if stop_condition.should_stop(
                    population=current_population.candidates,
                    generation=generation,
                    start_time=start_time,
                    context=context,
                ):
                    should_stop = True
                    break

            if should_stop:
                break

        # Get best candidate
        best_candidate = current_population.get_best()

        # Calculate metrics
        elapsed_time = time.time() - start_time
        metrics = self._calculate_metrics(
            generation, best_fitness_history, current_population, elapsed_time
        )

        # Create result
        result = SolveResult(
            status="completed",
            best_genome=best_candidate.genome if best_candidate else None,
            best_fitness=best_candidate.fitness if best_candidate else 0.0,
            generations=generation,
            elapsed_time=elapsed_time,
            metrics=metrics,
            population=current_population,
        )

        return result

    def _log_progress(
        self, generation: int, best_fitness: float, population: Population
    ) -> None:
        """Log evolution progress."""
        avg_fitness = population.get_average_fitness()
        worst_fitness = population.get_worst_fitness()

        print(
            f"Generation {generation}: "
            f"Best={best_fitness:.3f}, "
            f"Avg={avg_fitness:.3f}, "
            f"Worst={worst_fitness:.3f}, "
            f"Size={population.size()}"
        )

    def _calculate_metrics(
        self,
        generations: int,
        best_fitness_history: list[float],
        final_population: Population,
        elapsed_time: float,
    ) -> dict[str, Any]:
        """Calculate solve metrics."""
        if not best_fitness_history:
            return {}

        # Fitness improvement metrics
        initial_fitness = best_fitness_history[0] if best_fitness_history else 0.0
        final_fitness = best_fitness_history[-1] if best_fitness_history else 0.0
        fitness_improvement = final_fitness - initial_fitness

        # Population diversity metrics
        fitness_range = final_population.get_fitness_range()

        return {
            "initial_fitness": initial_fitness,
            "final_fitness": final_fitness,
            "fitness_improvement": fitness_improvement,
            "fitness_range_min": fitness_range[0],
            "fitness_range_max": fitness_range[1],
            "fitness_history": best_fitness_history,
            "generations_per_second": (
                generations / elapsed_time if elapsed_time > 0 else 0
            ),
            "candidates_evaluated": generations * final_population.size(),
        }
