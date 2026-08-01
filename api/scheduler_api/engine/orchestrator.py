"""Main solve orchestrator."""

import time
from typing import Any, Generic, TypeVar, Optional
from uuid import UUID, uuid4
from dataclasses import dataclass, field
from .evolution import EvolutionEngine
from .population import Population, Candidate
from .interfaces import Solvable, Stoppable

G = TypeVar("G")  # Genome type
T = TypeVar("T")  # Context type
P = TypeVar("P")  # Population type
R = TypeVar("R")  # Pipeline result type


@dataclass
class SolveResult(Generic[G]):
    """Result of a solve execution."""

    id: UUID = field(default_factory=uuid4)
    status: str = "completed"
    best_genome: Optional[G] = None
    best_fitness: float = 0.0
    generations: int = 0
    elapsed_time: float = 0.0
    metrics: dict[str, Any] = field(default_factory=dict)
    population: Optional[Population[G]] = None

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


class SolveOrchestrator(Generic[G, T, P, R]):
    """Generic orchestrates solve execution with evolution engine."""

    def __init__(self, evolution_engine: Optional[EvolutionEngine[G, T]] = None):
        self.evolution_engine = evolution_engine or EvolutionEngine[G, T]()

    def solve(
        self,
        solvable: Solvable[T, G, P, R],
        template_id: UUID,
        parameters: dict[str, Any],
    ) -> SolveResult[G]:
        """Execute solve using genetic algorithm."""
        start_time = time.time()

        # Create context
        context = solvable.create_context(template_id, parameters)

        # Get pipeline configuration
        pipeline = solvable.create_pipeline()

        # Create initial population
        population_size = parameters.get("population_size", 10)
        initial_population = solvable.create_initial_population(
            context, population_size
        )

        # Convert initial population to Population[G] type if needed
        if not isinstance(initial_population, Population):
            # Handle case where solvable returns a different population type
            current_population = Population[G](generation=0)
            # Implementation would need to convert here
            # For now, assume it's already a Population[G]
            current_population = initial_population  # type: ignore
        else:
            current_population = initial_population

        # Evolution loop
        generation = 0
        best_fitness_history = []

        while True:
            # Evolve population
            try:
                current_population = self.evolution_engine.evolve_population(
                    population=current_population,
                    genome_operators=getattr(pipeline, "genome_operators", []),
                    scorers=getattr(pipeline, "scorers", []),
                    constraints=getattr(pipeline, "constraints", []),
                    selector=getattr(pipeline, "selector"),
                    context=context,
                )
            except Exception as e:
                print(f"Evolution error: {e}")
                break

            generation += 1

            # Track best fitness
            best_fitness = current_population.get_best_fitness()
            best_fitness_history.append(best_fitness)

            # Log progress
            self._log_progress(generation, best_fitness, current_population)

            # Check stop conditions
            should_stop = False
            stop_conditions = getattr(pipeline, "stop_conditions", [])
            for stop_condition in stop_conditions:
                try:
                    if stop_condition.should_stop(
                        population=current_population,
                        generation=generation,
                        start_time=start_time,
                        context=context,
                    ):
                        should_stop = True
                        break
                except Exception as e:
                    print(f"Stop condition error: {e}")
                    continue

            if should_stop:
                break

        # Get best candidate
        try:
            best_candidates = current_population.get_top_n(1)
            best_candidate = best_candidates[0] if best_candidates else None
        except Exception:
            best_candidate = None

        # Calculate metrics
        elapsed_time = time.time() - start_time
        metrics = self._calculate_metrics(
            generation, best_fitness_history, current_population, elapsed_time
        )

        # Get best fitness from history if available
        best_fitness = best_fitness_history[-1] if best_fitness_history else 0.0

        # Create result
        result = SolveResult[G](
            status="completed",
            best_genome=best_candidate.genome if best_candidate else None,
            best_fitness=best_fitness,
            generations=generation,
            elapsed_time=elapsed_time,
            metrics=metrics,
            population=current_population,
        )

        return result

    def _log_progress(
        self, generation: int, best_fitness: float, population: Population[G]
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
        final_population: Population[G],
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
