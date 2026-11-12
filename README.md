# scheduler

Scheduling application: a FastAPI backend (`api/`), a Vue frontend (`ui/`), and a
genetic-algorithm scheduling engine.

## Scheduling engine

The GA engine lives in `api/scheduler_api/engine/` and is deliberately independent of
FastAPI, SQLModel, and Celery: it consumes plain Pydantic DTOs and returns candidate
schedules as DTOs. The full design — domain boundary, component protocols, phase
lifecycle, coverage semantics, and the deferred shift-split operator — is in
[`DESIGN.md`](DESIGN.md).

```text
engine/
  models/        Pydantic DTOs (problem context, genome, phases, results)
  protocols/     structural interfaces for components, solver, controller, executor
  components/    concrete seeders, scorers, selectors, mutators, cullers, stoppers
  execution/     registry, runner, in-memory store, local executor
  controller.py  GA lifecycle state machine
  solver.py      the concrete algorithm definition and registrations
```

An execution can be run entirely in memory, with no database, broker, or API:

```python
from uuid import uuid4

from scheduler_api.engine.controller import GAController
from scheduler_api.engine.execution.local import LocalExecutor
from scheduler_api.engine.execution.registry import ComponentRegistry
from scheduler_api.engine.execution.runner import ComponentRunner
from scheduler_api.engine.execution.store import InMemoryExecutionStore
from scheduler_api.engine.solver import GeneticAlgorithmSolver, build_default_registry

registry = build_default_registry()
runner = ComponentRunner(registry)
store = InMemoryExecutionStore()
solver = GeneticAlgorithmSolver(registry=registry)
controller = GAController(solver, runner, store)
executor = LocalExecutor(controller, runner)

execution_id = uuid4()
store.save_request(
    solver.build_request(execution_id=execution_id, problem=problem, random_seed=42)
)
executor.execute(execution_id)
result = store.load_result(execution_id)
```

`problem` is a `SchedulingProblem` (horizon, coverage requirements, workers, jobs). One run
returns an `ExecutionResult` carrying ranked `CandidateSchedule` objects — initially one.
Candidates may be infeasible when no feasible schedule exists, in which case they carry
their violations and `feasible = false`.

`api/scheduler_api/mappers/candidate_schedule_mapper.py` converts a candidate into
persistence-ready drafts. Persisting it needs the `Schedule`, `Job`, demand, and
availability tables described in section 21 of `DESIGN.md`; the engine change does not
include that schema work.

## Development

```bash
# API checks (from api/)
black --check .
flake8 .
pytest

# Type checking (from the repository root)
mypy
```
