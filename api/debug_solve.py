"""Debug test for solve framework."""

from uuid import uuid4
from scheduler_api.solves.schedule.solver import ScheduleSolver
from scheduler_api.solves.engine.orchestrator import SolveOrchestrator


def debug_solve():
    """Debug the solve framework."""
    print("=== Debug Solve Framework ===\n")

    # Create solver
    solver = ScheduleSolver()

    # Create template ID
    template_id = uuid4()

    # Very small parameters for debugging
    parameters = {
        "population_size": 5,
        "max_generations": 3,  # Just 3 generations
        "mutation_rate": 0.3,  # High mutation
        "selection_top_n": 3,  # Keep more
        "elite_size": 1,
    }

    # Create orchestrator
    orchestrator = SolveOrchestrator()

    # Manually step through to debug
    print("1. Creating context...")
    context = solver.create_context(template_id, parameters)
    print(f"   Workers: {len(context.worker_ids)}, Shifts: {len(context.shift_ids)}")

    print("\n2. Creating initial population...")
    initial_genomes = solver.create_initial_population(
        context, parameters["population_size"]
    )
    print(f"   Created {len(initial_genomes)} initial genomes")

    # Show first genome
    if initial_genomes:
        first_genome = initial_genomes[0]
        print(f"   First genome has {len(first_genome.assignments)} shift assignments")
        for shift_id, workers in first_genome.assignments.items():
            print(f"     Shift {str(shift_id)[:8]}... -> {len(workers)} workers")

    print("\n3. Testing scorer...")
    from scheduler_api.solves.schedule.scorers.skills_match_scorer import (
        SkillsMatchScorer,
    )

    scorer = SkillsMatchScorer()
    if initial_genomes:
        score = scorer.score(initial_genomes[0], context)
        print(f"   Score for first genome: {score:.3f}")

    print("\n4. Testing pipeline creation...")
    pipeline = solver.create_pipeline()
    print(f"   Seeders: {len(pipeline.seeders)}")
    print(f"   Genome operators: {len(pipeline.genome_operators)}")
    print(f"   Scorers: {len(pipeline.scorers)}")
    print(f"   Constraints: {len(pipeline.constraints)}")
    print(f"   Stop conditions: {len(pipeline.stop_conditions)}")

    print("\n5. Running full solve (will be quick)...")
    result = orchestrator.solve(solver, template_id, parameters)

    print(f"\nResult: {result.status}, Fitness: {result.best_fitness:.3f}")
    print(
        f"Population size in final result: {result.population.size() if result.population else 0}"
    )


if __name__ == "__main__":
    debug_solve()
