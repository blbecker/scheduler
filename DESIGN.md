# Genetic Algorithm Scheduling Engine — Design Specification

**Status:** Implemented (revision 3 — reflects the engine as built)
**Audience:** AI coding agent / implementation engineer
**Scope:** Implement the first usable genetic-algorithm (GA) scheduling engine in the existing Scheduler application. This document specifies the engine architecture, domain boundary, interface pattern, execution lifecycle, and initial implementation scope.

---

## 0. Changes from revision 1

Revision 2 is not a cosmetic edit. Read this section before anything else.

**Removed**

- **The fixed 15-minute slot grid.** There is no `TimeSlot` model, no `slot_index`, and no slot-alignment in any DTO. Demand is expressed as time windows; the genome is a set of shifts with real `start`/`end` instants. The previous design's discrete slot space multiplied the search space by the horizon-to-resolution ratio for no measurable gain, and produced quantization artifacts in scoring.
- **The separate assignment layer.** Assignments and their coalescing into shifts are gone. A planned shift *is* the genome element.
- **Coverage-requirement identity as a scheduling concept.** Coverage is measured per job per instant; an assignment never records "which demand element" it serves.
- **The word "solve" as a noun.** `SolverState` is now `ExecutionState`, and the result of a run is an `ExecutionResult`. A **solver** is an orchestration object: a description of the GA elements that make up an algorithm. An **execution** is one run of a solver.

**Added**

- Windowed demand (`CoverageRequirement`), interval arithmetic throughout, and an explicit coverage definition in worker-minutes.
- `FitnessConfig`: scorers return 0–100, weights are explicit, fitness is a weighted mean.
- A scorer contract that returns both scores and structured violations, plus a `Violation` model and aggregation rule for surfacing.
- `ExecutionResult` / `CandidateSchedule` so a run returns a list of candidates (initially one).
- **Globally unique component ids.** Because the invocation input union discriminates on `component_id` alone, the selector and culler are `select_top_n` and `cull_top_n` rather than both being `top_n`.
- **Explicit scoring target.** `SCORE` runs twice per generation, so `ExecutionState.scoring_target` records whether the population or the offspring is being evaluated.
- Explicit org-level shift-length policy with per-worker hard overrides and separate soft preferences.
- Deferred-operator design note for the **shift-split mutation** (Appendix A).
- A section listing the persistence changes this design implies (Section 21), which are explicitly *not* part of the engine work.

---

## 1. Goals

Implement a scheduling optimization engine that consumes a schedule problem — staffing demand, workers, jobs, availability, and qualifications — and produces one or more candidate schedules.

The engine must:

1. Use a genetic-algorithm architecture with replaceable components.
2. Represent scheduling decisions as planned shifts: a worker, a job, and a `[start, end)` interval.
3. Keep the engine independent of persistence models, FastAPI, SQLModel, Celery, and other infrastructure.
4. Use Python `Protocol` interfaces for structural typing.
5. Use Pydantic DTOs at engine boundaries so inputs and outputs are explicit, validated, and serializable.
6. Support a synchronous local executor first, while making a distributed Celery executor a straightforward later addition.
7. Keep orchestration and algorithm lifecycle logic separate from the mechanics used to execute component calls.
8. Be testable without a database, message broker, or running API.

The first implementation should favor correctness and clarity over premature performance optimization. Do not introduce distributed execution, persistence optimizations, generic workflow machinery, or elaborate plugin loading in the initial implementation.

## 2. Non-goals

Do not implement these as part of the initial engine work unless explicitly requested:

- Celery tasks or a distributed executor.
- Database persistence for populations or intermediate generations.
- Redis caching, population dehydration, shared-memory optimization, or other performance optimizations.
- Alembic migrations or changes to database schemas (see Section 21 for the changes this design implies but does not deliver).
- API routes, UI work, or frontend integration.
- Employee time-clock/attendance processing.
- Shift swap workflows.
- Candidate acceptance/rejection workflow.
- The **shift-split mutation** (designed for in Appendix A; not implemented initially).
- Crossover as a separate component category. Recombination is a mutation strategy; it is not its own protocol unless implementation proves otherwise.
- A general-purpose workflow engine.
- Dynamic third-party plugin discovery or arbitrary Python class loading.
- A sophisticated GA operator catalogue.

The engine should be designed so these can be added later without changing its core component contracts.

## 3. Existing application context

The application uses:

- FastAPI for the API.
- SQLModel / SQLAlchemy and PostgreSQL for persistence.
- Celery for asynchronous work, with RabbitMQ as broker and Redis available for result storage.
- Pydantic DTOs for API and service boundaries.

The persistence layer is early and will change substantially to support this design. As of this revision it contains exactly five tables:

- `Shift` — `start_time`, `end_time`, optional `location`, optional `notes`. A shift has **many** skills and **many** workers through link tables.
- `Skill` — `name`.
- `Worker` — `name`, `birthdate`, optional `email`, optional `phone`.
- `ShiftSkillLink`, `ShiftWorkerLink`, `WorkerSkillLink` — association rows.

There is no `Schedule`, no schedule template, no job/role entity, no availability data, no labor demand, and no pay data. The engine's vocabulary is therefore **ahead of** the persistence model, deliberately. Do not contort the engine to match today's tables; do not modify the tables as part of this work.

The application/service layer is responsible for loading persisted data, translating it into engine DTOs, invoking the engine, and translating a returned candidate back into persistence entities. That layer is expected to churn; the engine's contracts are what this document pins down.

## 4. Core design decisions

### 4.1 Demand windows and planned shifts

The engine solves exactly two representations:

- **Coverage requirement** — how many workers are required for a job during a time window.
- **Planned shift** — a contiguous interval of work for one worker and one job.

There is no intermediate slot-assignment layer. The genome is the set of planned shifts. There is no coalescing step at the end: what the solver returns is what gets persisted.

**Job semantics (load-bearing invariant).** A job owns exactly one skill set. Demand windows for a job may vary in time and headcount; they may not vary in required skills. If a window needs different skills, it is a different job. This keeps qualification a per-`(worker, job)` fact and keeps coverage a per-instant headcount sum — which is why no coverage-requirement identity is needed anywhere in the engine.

**Overlapping windows.** Multiple windows for the same job may be active simultaneously. Required headcount at an instant is the *sum* of active windows' `required_workers`. Coverage, understaffing, and overstaffing are therefore defined per `(job, instant)`, not per window.

**Shifts vs windows.** A shift need not be contained inside a single window, and may overhang a window's edge. Coverage math is per-instant and handles both. Partial overhang is a soft waste, not a violation (see Section 12). A shift that overlaps demand in *no* minute is a hard violation.

### 4.2 Continuous time at minute resolution

The scheduling horizon is a pair of instants. All time values are timezone-aware `datetime` values representing real instants in the business timezone named by `SchedulingProblem.timezone`.

- **Intervals are half-open:** `[start, end)`. A shift ending at 12:00 does not overlap one starting at 12:00.
- **Internal resolution is one minute.** All duration and coverage measures are integer minutes. Never use floats for time measures: coverage is a ratio of two measures and float accumulation makes scoring order-dependent.
- **Input timestamps must be minute-aligned.** Validate this at the boundary and raise; do not silently truncate.
- **Boundary granularity.** `SchedulingProblem.boundary_granularity_minutes` (default 15) is the grid that *mutators* snap new boundaries to. The model stays continuous — nothing in a scorer or in coverage math may assume boundaries fall on this grid. The granularity exists so generated schedules are human-legible (nobody schedules 08:07–12:23) and so mutation does not drift into meaningless minute-level jitter.
- **Daylight saving.** Do not assume every local calendar day has a fixed number of minutes. DST transitions make local days 23 or 25 hours long. Work with absolute instants and convert to local time only when a rule is *about* local days (day attribution, weekly aggregation, reporting).
- **Day attribution.** A rule expressed per day (e.g. maximum shifts per day, hours per day) attributes a shift to the **local date on which the shift starts**. Hours are measured by overlapped minutes, so a 22:00–06:00 shift contributes minutes to both dates while counting as one shift on the start date.
- **Bootstrap.** `horizon_start` / `horizon_end` bound the execution's scope and seed generation. They are supplied by the caller; do not infer them inside components.

### 4.3 Structural interfaces with `Protocol`

Use `typing.Protocol` for component, solver, controller, and executor contracts.

Implementations do not need to inherit from the protocol. A class satisfies a protocol structurally by providing the required methods and attributes. Use static type checking (mypy) to validate implementations.

Do not use abstract base classes merely to force inheritance. An ABC is appropriate only if shared implementation or enforced inheritance becomes necessary.

Do not add `@runtime_checkable` unless runtime `isinstance()` checks are genuinely required. Runtime protocol checks do not validate method signatures; static checking remains the primary contract validation.

A static type checker is the only mechanism that makes these Protocol contracts real. Add mypy to the API development dependencies and run it in CI; without it the Protocol layer is decoration.

### 4.4 Pydantic DTOs at boundaries

All inputs and outputs crossing an engine component, executor, controller, or future Celery boundary must be Pydantic models.

- Do not pass SQLModel/ORM instances into the engine.
- Do not pass database sessions, repositories, service objects, or arbitrary callables in DTOs.
- Use UUIDs and primitive values to identify domain entities.
- Keep DTOs JSON-serializable.
- Use `model_dump(mode="json")` and `model_validate()` for serialization boundaries.
- Prefer explicit, typed models and discriminated unions over `dict[str, Any]`.
- Avoid serializing arbitrary component instances. Refer to components by stable string identifiers and resolve them from a registry.

Pydantic models should be immutable (`frozen=True`), especially problem context, component configuration, and component results. Mutable algorithm state is owned explicitly by the controller/execution state, not hidden in component instances.

Components are stateless. A component receives its configuration inside the invocation input DTO (Section 9.5), never from constructor state.

### 4.5 Determinism

An execution is reproducible: the same problem, request, and seed produce a byte-identical `ExecutionResult` except for the execution id.

- Never use module-global random state. Randomness comes from an injected `random.Random` instance seeded per invocation.
- Seeds are derived deterministically from the execution seed plus stable coordinates: `blake2b(f"{master_seed}:{component_id}:{generation}:{invocation_ordinal}")`. Do not derive seeds from UUIDs generated at runtime.
- All UUIDs created by the engine are derived with `uuid5` from stable coordinates (execution id, generation, component id, ordinal, and a role-specific namespace). No `uuid4()` inside the engine.
- Any ordering used for ranking has a total deterministic tie-break (Section 12.4).

## 5. Suggested package structure

Place the engine under `api/scheduler_api/engine/`. Match the repository's existing layout conventions (`db/models`, `schemas`, `services`, `mappers`, `repositories`, `routers`, `views`, `tasks`), and keep the engine's models isolated from API schemas and database models.

```text
api/
  scheduler_api/
    engine/
      __init__.py

      protocols/
        __init__.py
        solver.py
        controller.py
        executor.py
        seeder.py
        scorer.py
        selector.py
        mutator.py
        culler.py
        stopper.py

      models/
        __init__.py
        time.py            # TimeWindow, minute validation helpers
        problem.py         # SchedulingProblem, CoverageRequirement, WorkerInfo, JobInfo, policies
        genome.py          # PlannedShift, Individual, Population
        scores.py          # Violation, violation codes
        fitness.py         # FitnessConfig and fitness computation
        config.py          # per-component config DTOs
        component_io.py    # per-component input/result DTOs + discriminated unions
        phase.py           # PhaseType, PhasePlan, ComponentInvocation, PhaseResult
        execution.py       # ExecutionRequest, ExecutionState, ExecutionStatus, ExecutionResult
        results.py         # CandidateSchedule

      components/
        __init__.py
        seeders/
          __init__.py
          random_shifts.py
        scorers/
          __init__.py
          coverage.py
          overstaffing.py
          skills_match.py
          shift_length.py
          availability.py
          double_booking.py
          schedule_limits.py
        selectors/
          __init__.py
          top_n.py
        mutators/
          __init__.py
          random_shift.py
        cullers/
          __init__.py
          top_n.py
        stoppers/
          __init__.py
          generation_count.py

      execution/
        __init__.py
        registry.py
        runner.py
        local.py
        store.py           # ExecutionStore protocol + in-memory implementation

      solver.py
      controller.py
      intervals.py         # sweep-line, overlap, containment, per-day grouping
      policies.py          # effective shift-length bounds (shared by mutators and scorers)
```

### Directory responsibilities

- `protocols/` — structural interfaces only, no concrete behavior.
- `models/` — Pydantic DTOs shared across components and execution infrastructure.
- `components/` — concrete, replaceable GA operators. Components must not know about Celery, persistence, the controller, or the executor.
- `intervals.py` / `policies.py` — pure functions for interval math and effective bound resolution. Scorers and mutators must share these; duplicated bound logic is how a mutator ends up producing shifts a scorer marks infeasible.
- `execution/registry.py` — maps stable component ids to implementations, per category.
- `execution/runner.py` — validates and dispatches one invocation to the right component method.
- `execution/local.py` — runs planned phases synchronously through the controller and runner.
- `execution/store.py` — holds execution state and results; in-memory for the MVP.
- `solver.py` — concrete GA solver definition and component registrations.
- `controller.py` — lifecycle state machine: plans phases, aggregates results, updates state, decides what happens next.

Avoid circular imports. Protocol modules depend on model modules; concrete components may depend on protocols and models; execution may depend on both. Components must not import the controller or executor.

---

## 6. Engine data model

### 6.1 Problem context

```python
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class TimeWindow(BaseModel):
    model_config = ConfigDict(frozen=True)

    start: datetime
    end: datetime

    @model_validator(mode="after")
    def _validate(self) -> "TimeWindow":
        if self.end <= self.start:
            raise ValueError("window end must be strictly after start")
        return self


class ShiftLengthPolicy(BaseModel):
    """Organization-level hard limits, in minutes."""

    model_config = ConfigDict(frozen=True)

    minimum_minutes: int = 120
    maximum_minutes: int = 720


class ScheduleLimits(BaseModel):
    """Organization-level hard caps. None means 'no limit configured'."""

    model_config = ConfigDict(frozen=True)

    maximum_hours_per_week: int | None = None
    maximum_shifts_per_day: int | None = None


class CoverageRequirement(BaseModel):
    """Required headcount for one job during one window.

    Has no identity field on purpose: coverage is measured per (job, instant)
    as a sum over active windows. Nothing in the engine records which
    requirement a shift serves.
    """

    model_config = ConfigDict(frozen=True)

    job_id: UUID
    start: datetime
    end: datetime
    required_workers: int  # >= 1


class WorkerInfo(BaseModel):
    model_config = ConfigDict(frozen=True)

    worker_id: UUID
    qualified_job_ids: frozenset[UUID]
    available_windows: tuple[TimeWindow, ...]

    # Hard overrides of the org policy. None = use ShiftLengthPolicy.
    minimum_shift_minutes: int | None = None
    maximum_shift_minutes: int | None = None

    # Soft preferences, scored not enforced.
    preferred_minimum_shift_minutes: int | None = None
    preferred_maximum_shift_minutes: int | None = None


class JobInfo(BaseModel):
    model_config = ConfigDict(frozen=True)

    job_id: UUID
    name: str


class SchedulingProblem(BaseModel):
    model_config = ConfigDict(frozen=True)

    timezone: str
    horizon_start: datetime
    horizon_end: datetime
    boundary_granularity_minutes: int = 15
    shifts: ShiftLengthPolicy
    limits: ScheduleLimits
    requirements: tuple[CoverageRequirement, ...]
    workers: tuple[WorkerInfo, ...]
    jobs: tuple[JobInfo, ...]
```

Notes:

- Qualification is precomputed per worker as `qualified_job_ids`. The application layer derives it from `WorkerSkillLink` and the job's skill set. Do not pass skill sets, skill names, or skill comparison logic into the engine.
- `JobInfo.name` exists only so violations and results are readable to a human; no component may branch on it.
- Add fields only when a component needs them. Pay rates, fairness tallies, and preferences beyond shift length are deliberately absent: no component in the MVP consumes them.
- The problem context must be sufficient for every component to evaluate candidate shifts without touching the database.

### 6.2 Genome: planned shifts and individuals

```python
class PlannedShift(BaseModel):
    model_config = ConfigDict(frozen=True)

    shift_id: UUID
    worker_id: UUID
    job_id: UUID
    start: datetime
    end: datetime


class Individual(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: UUID
    shifts: tuple[PlannedShift, ...]
    scores: dict[str, float] = Field(default_factory=dict)   # component_id -> 0..100
    violations: tuple[Violation, ...] = ()
    fitness: float | None = None

    @property
    def feasible(self) -> bool:
        return not self.violations
```

- Name the engine's shift model `PlannedShift`, never `Shift`, to avoid shadowing the ORM entity.
- Canonicalize order in a model validator: sort shifts by `(worker_id, start, job_id, shift_id)`. Two structurally identical individuals must compare equal and serialize identically.
- An `Individual` is the unit that gets scored, selected, mutated, culled, and returned as a candidate.
- `fitness` is filled by the controller after score aggregation, not by a component.
- Do not store derived data redundantly (per-worker hour totals, per-job coverage) on the individual in the MVP. Compute it in the scorer that needs it. Add cached summaries only after profiling.
- Workers may hold shifts for different jobs; whether a same-worker back-to-back job change is acceptable is a scorer/constraint question, not a data-structure one.

### 6.3 Population

```python
class Population(BaseModel):
    model_config = ConfigDict(frozen=True)

    individuals: tuple[Individual, ...]
```

Populations are immutable. Components return new individuals or populations; they never mutate their inputs. Individual ids must be unique within a population; the controller validates this.

### 6.4 Scores, violations, and feasibility

Two separate channels, never mixed:

- **Scores** — one value per `(individual, scorer component)`, always in `[0, 100]`. Higher is better. The score channel is fitness only.
- **Violations** — structured statements that the candidate breaks a rule. Violations, not low scores, determine feasibility.

A scorer may emit both. A scorer that only detects violations (availability, double-booking, caps) is given a fitness weight of `0`, which excludes it from fitness aggregation while keeping its violations.

```python
class Violation(BaseModel):
    model_config = ConfigDict(frozen=True)

    code: str                     # from the ViolationCode table in Section 12.3
    job_id: UUID | None = None
    worker_id: UUID | None = None
    start: datetime | None = None
    end: datetime | None = None
    shift_id: UUID | None = None
    detail: str = ""
```

Violations are emitted per occurrence. A single infeasible schedule can carry thousands; the app layer aggregates by `code` before showing anything to a person (Section 16.3). Do not attempt to pre-aggregate inside components — the raw list is evidence.

Scoring conventions, all mandatory:

- A scorer returns `actual_points / maximum_possible_points * 100` for its own criterion, or another documented 0–100 mapping. The engine does not constrain *how* a scorer reaches its number, but every scorer must document what 0 and 100 mean.
- Score fields carry Pydantic constraints (`ge=0`, `le=100`) so a faulty scorer fails loudly at the runner boundary instead of silently skewing fitness.
- Do not round scores. Rounding manufactures ties.
- Score computation must be deterministic for a fixed input. If a scorer is intentionally stochastic it must be documented and seeded.

### 6.5 Fitness

```python
class FitnessConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    weights: dict[str, float] = Field(default_factory=dict)  # component_id -> weight
```

- Missing weight means `1.0`. Weight `0.0` means "collect violations, ignore the score". Negative weights are invalid.
- Default configuration uses equal weights for all scoring components, excluding constraint-only components.
- **fitness = Σ(wᵢ · scoreᵢ) / Σ(wᵢ)** over components with `wᵢ > 0` and a score present for that individual.
- A weighted mean is used rather than a raw sum so fitness stays on the same 0–100 scale regardless of how many scorers are configured. Ranking is identical either way; the scale is not, and fitness is recorded across runs (REQ-SOL-003).
- If an individual has no scored components at all, that is a validation error, not a default of zero.

---

## 7. Component protocols

Each operator has a narrow typed contract. Components are stateless: configuration arrives in the input DTO; per-execution data arrives as method arguments.

Every invocation input DTO carries `component_id` as a `Literal`, which is what makes the invocation unions discriminating (Section 10.2).

### 7.1 Seeder

```python
class Seeder(Protocol):
    def seed(self, input: SeedInput) -> SeedResult: ...
```

- Input: problem, `population_size` contribution, `random_seed`, typed config.
- Result: a population, fully formed planned shifts, unique ids.
- A solver may register several seeders. Each seeder config declares a `contribution` (number of individuals); the controller concatenates. Contributions must sum to `population_size` — validate, do not pad silently.
- Seeders must produce structurally valid shifts: known worker/job ids, `end > start`, minute-aligned, boundaries on the granularity grid, and (in the MVP) drawn from within demand windows. Business-rule compliance beyond that is scorers' work, not seeders'.
- Seeders should respect effective hard shift-length bounds. A seeder that emits infeasible-length shifts wastes a generation of scoring.
- Initial implementation: `RandomShiftSeeder`.

### 7.2 Scorer

```python
class Scorer(Protocol):
    def score(self, input: ScoreInput) -> ScoreResult: ...
```

- Input: problem, the individuals to score, typed config.
- Result: `scores: dict[UUID, float]` keyed by individual id, and `violations: dict[UUID, tuple[Violation, ...]]`.
- Both maps must be keyed by ids present in the input; unknown ids and duplicates are errors.
- Scorers must be independently executable over the same population so they can later run in parallel. A scorer must not require another scorer's output.
- Scorers must not mutate input individuals or the problem.
- Predicted cost should be linear in the total shift count. Use `intervals.py`; do not build per-minute arrays.

The scorer is responsible for *its own* criterion only. Do not write a "master" scorer that computes everything.

### 7.3 Selector

```python
class Selector(Protocol):
    def select(self, input: SelectInput) -> SelectResult: ...
```

- Input: population, `count`.
- Result: exactly `count` individuals drawn from the input population (in the MVP).
- Must use the solver's documented ordering (Section 11.4).
- Initial implementation: `TopNSelector`.

### 7.4 Mutator

```python
class Mutator(Protocol):
    def mutate(self, input: MutateInput) -> MutateResult: ...
```

- Input: problem, selected parents, `offspring_count`, `random_seed`, typed config, plus the effective shift-length bounds helper already resolved.
- Result: new individuals with new ids, `scores` empty, `violations` empty, `fitness = None`.
- Never mutate source individuals in place.
- Mutation must preserve structural validity (known ids, `end > start`, minute-aligned, on-grid boundaries) and **must respect effective hard shift-length bounds**. This is not optional: free boundary mutation produces fragmented shifts (see Appendix A), and once those are hard-violations the population collapses back toward the seed.
- Mutation does not need to preserve feasibility. It should avoid accidentally destroying it, but business-rule evaluation belongs to scorers.
- Initial implementation: `RandomShiftMutator` — a weighted mix of reassigning a shift's worker, nudging a boundary (snapped to grid, clamped to bounds), deleting a shift, and inserting a shift for uncovered demand.
- Recombination/crossover, when added, is a strategy inside a mutator component. Do not introduce a `Crossover` protocol preemptively.

### 7.5 Culler

```python
class Culler(Protocol):
    def cull(self, input: CullInput) -> CullResult: ...
```

- Input: combined candidate population, `target_size`, `preserve_best` count.
- Result: the retained population of exactly `target_size`.
- Must use the same ordering as selection (Section 11.4).
- Initial implementation: `TopNCuller`.

### 7.6 Stopper

```python
class Stopper(Protocol):
    def should_stop(self, input: StopInput) -> StopResult: ...
```

- Input: execution metadata, current generation, best-so-far fitness, population summary.
- Result: `should_stop: bool` and a required `reason: str`.
- Multiple stoppers may be registered; aggregation is "stop if any stopper says stop". The reason from the first stopper (in registration order) that says stop is recorded.
- Stoppers run through the same component execution mechanism as everything else. Do not invoke them as a hidden callback inside the controller.
- Initial implementation: `GenerationCountStopper` (configured `maximum_generations`).

---

## 8. Component configuration and registration

Each component registration includes:

- A stable string component id.
- The concrete implementation.
- The component category.
- Its typed config DTO, supplied per execution in the `ExecutionRequest` (not on the instance).

Component ids are **globally unique across categories**, not per category. This is what allows a single discriminated union over `component_id` for invocation inputs. The registry rejects duplicates anywhere.

```python
class ComponentRegistry:
    def register_seeder(self, component_id: str, component: Seeder) -> None: ...
    def register_scorer(self, component_id: str, component: Scorer) -> None: ...
    def register_selector(self, component_id: str, component: Selector) -> None: ...
    def register_mutator(self, component_id: str, component: Mutator) -> None: ...
    def register_culler(self, component_id: str, component: Culler) -> None: ...
    def register_stopper(self, component_id: str, component: Stopper) -> None: ...
```

- Registration is explicit. No entry-point discovery, no dynamic imports.
- The registry provides a clear error for unknown ids and category mismatches.
- A phase plan carries only the component id and a JSON-compatible input DTO. It never carries implementation instances or Python objects.
- Config lives in the input DTO, so an invocation is self-describing and replayable from the plan alone. Do not let a component read configuration from its own constructor — that would make the plan's meaning depend on which process ran it.

---

## 9. Solver, controller, runner, and executor responsibilities

These are four separate abstractions. Do not collapse them.

### 9.1 Solver

The solver is the algorithm definition — an orchestration object describing the GA elements that make up an algorithm:

- seeders (with contributions)
- scorers
- one selector
- mutators (with probabilities)
- one culler
- stoppers
- population size, `max_candidates`, `preserve_best`
- the component registry it registers into

The solver contains no execution logic, no Celery, no database access, and no phase-resumption logic. It must not know whether execution is local or distributed.

### 9.2 Controller

The controller owns the lifecycle state machine. It:

1. Accepts an `ExecutionRequest` and starts an execution.
2. Determines the next phase and constructs a `PhasePlan`.
3. Accepts a completed `PhaseResult`.
4. Validates and aggregates results (scores, violations, offspring, retained population).
5. Updates `ExecutionState` (immutably — returns new state).
6. Decides the next phase, or finalizes.
7. On finalization, builds the `ExecutionResult` with ranked candidates.

The controller is deterministic for a given state and phase result. All mutable state lives in `ExecutionState`; nothing important is held in controller instance attributes. A controller instance may be reused across executions only if it holds no per-execution state.

`phase_execution_id` idempotency: the controller records completed phase execution ids and rejects a duplicate `PhaseResult` for an already-completed phase (returning the same next plan rather than double-applying).

### 9.3 Component runner

The runner invokes exactly one component by id:

- Resolve the component from the registry.
- Validate the invocation input against the concrete DTO type expected for that component and category.
- Call the correct protocol method.
- Validate and normalize the result (score range, known individual ids, uniqueness).
- Return a typed, serializable result envelope.
- Produce errors that name the execution, phase, component, and invocation.

Use an explicit dispatcher keyed on `ComponentCategory` (and the discriminated input union). Never dispatch on `getattr(component, untrusted_string)`. The runner is shared by the local executor and any future distributed executor, and knows nothing about Celery.

### 9.4 Executor

```python
class SolverExecutor(Protocol):
    def execute(self, execution_id: UUID) -> None: ...
```

- `LocalExecutor.execute()` runs the whole execution synchronously and returns when terminal. It returns `None` by contract; the result is read from the execution store (Section 9.6).
- A future `DistributedExecutor.execute()` dispatches initial work and returns; persisted execution status becomes the source of truth.
- The executor does not decide phase ordering. It asks the controller for a plan, runs the plan, submits results, repeats.

### 9.5 Configuration is per-invocation

Every component input DTO has this shape:

```python
class CoverageScoreInput(BaseModel):
    model_config = ConfigDict(frozen=True)

    component_id: Literal["coverage"] = "coverage"
    problem: SchedulingProblem
    individuals: tuple[Individual, ...]
    config: CoverageScorerConfig
```

The controller copies the config out of the `ExecutionRequest` into each invocation input. Consequences: an invocation is complete on its own, a plan can be serialized and replayed, and a component never depends on ambient process state.

### 9.6 Execution store and result access

The MVP has no persistence, but it still needs a single read path for results that a
distributed executor will share later.

```python
class ExecutionStore(Protocol):
    def save_request(self, request: ExecutionRequest) -> None: ...
    def load_request(self, execution_id: UUID) -> ExecutionRequest: ...
    def save_state(self, state: ExecutionState) -> None: ...
    def load_state(self, execution_id: UUID) -> ExecutionState: ...
    def save_result(self, result: ExecutionResult) -> None: ...
    def load_result(self, execution_id: UUID) -> ExecutionResult | None: ...
```

`InMemoryExecutionStore` fulfils it for now. The controller writes state; the executor
drives; callers read `load_result(execution_id)`. Do not hold the result on the executor
or controller — the executor returns `None` per its protocol, and the store is what makes
"the test receives the best candidate" work without special-casing the local executor.

---

## 10. Phase planning and execution DTOs

### 10.1 Envelope

```python
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel


class PhaseType(StrEnum):
    SEED = "seed"
    SCORE = "score"
    SELECT = "select"
    MUTATE = "mutate"
    CULL = "cull"
    CHECK_STOP = "check_stop"


class ComponentCategory(StrEnum):
    SEEDER = "seeder"
    SCORER = "scorer"
    SELECTOR = "selector"
    MUTATOR = "mutator"
    CULLER = "culler"
    STOPPER = "stopper"


class ComponentInvocation(BaseModel):
    model_config = ConfigDict(frozen=True)

    invocation_id: UUID
    category: ComponentCategory
    input: ComponentInput        # discriminated union over component_id


class PhasePlan(BaseModel):
    model_config = ConfigDict(frozen=True)

    execution_id: UUID
    phase_execution_id: UUID
    generation: int
    phase: PhaseType
    invocations: tuple[ComponentInvocation, ...]


class ComponentResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    invocation_id: UUID
    category: ComponentCategory
    result: ComponentOutput      # discriminated union over component_id


class PhaseResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    execution_id: UUID
    phase_execution_id: UUID
    results: tuple[ComponentResult, ...]
```

### 10.2 No untyped dictionaries

`ComponentInput` and `ComponentOutput` are discriminated unions of the concrete input/result DTOs, discriminated on `component_id`. Each concrete input DTO declares its id as a `Literal`.

```python
ComponentInput = Annotated[
    SeedRandomShiftsInput
    | CoverageScoreInput
    | OverstaffingScoreInput
    | SkillsMatchScoreInput
    | ShiftLengthScoreInput
    | AvailabilityScoreInput
    | DoubleBookingScoreInput
    | ScheduleLimitsScoreInput
    | TopNSelectInput
    | RandomShiftMutateInput
    | TopNCullInput
    | GenerationCountStopInput,
    Field(discriminator="component_id"),
]
```

Practical consequences:

- Adding a component means adding its DTOs to the union. That is deliberate friction, not a wart: it keeps serialization explicit.
- Because the union is global, a new component id must be unique across all categories.
- Do not leave `dict` payloads in the plan. If a payload genuinely varies (e.g. a config block), the variation belongs in a typed config model attached to a concrete input DTO.

### 10.3 Idempotency

`phase_execution_id` identifies one execution of one phase. A retried callback or a duplicate result must not complete the same phase twice. The controller rejects duplicates by `phase_execution_id` and returns the already-planned next step.

A plan must contain everything needed to execute its invocations, including the working population. Plans are immutable DTOs; treat serialized size as a known non-problem until profiling says otherwise.

---

## 11. GA lifecycle

### 11.1 Generation zero

1. `SEED` — invoke every configured seeder; verify contributions sum to `population_size`; concatenate; validate unique ids.
2. `SCORE` — score the whole seeded population.

### 11.2 Generation n ≥ 1

3. `SELECT` — pick `parent_count` individuals from the current population using the canonical ordering.
4. `MUTATE` — invoke mutators over the selected parents to produce `offspring_count` new individuals.
5. `SCORE` — score **offspring only**, with `ExecutionState.scoring_target = offspring`. Survivors keep the scores and violations they already have.
6. `CULL` — combine current population and offspring; retain `population_size` using the canonical ordering; honor `preserve_best`.
7. `CHECK_STOP` — invoke all stoppers.
   - If stopping: finalize (Section 11.5).
   - If continuing: increment generation, return to `SELECT`.

Rationale for scoring offspring only: re-scoring survivors is wasted work (cost is linear in shift count per individual, and survivors can be the whole population), and scoring is deterministic, so a survivor's score cannot have changed. If a future component makes scores time- or population-dependent, this rule must be revisited explicitly rather than accidentally.

### 11.3 Policies that must be explicit

- **Elitism:** `preserve_best` (default 1). The best individual found so far is not culled regardless of generation population. Best-so-far is tracked in `ExecutionState`, not inferred from the current population.
- **Offspring count** is configured, not implied by parent count.
- **Parents are eligible for survival** through the cull phase; reproduction does not discard them implicitly.
- **Mutation rate** is a mutator-config value with a documented default, not a magic constant in code.

### 11.4 Canonical ordering

One ordering, used by `SELECT`, `CULL`, best-candidate tracking, and candidate ranking:

1. **Feasible before infeasible** — always, regardless of fitness. (REQ-CON-003.)
2. Higher `fitness` first.
3. Tie-break deterministically on a stable structural key: the individual's canonical shift tuple as serialized, then `individual_id`. Both are total and reproducible.

Do not rely on tuple ordering from dict insertion or generation order for tie-breaks. Early generations are full of exact ties, and unstable tie-breaks make seeded runs non-reproducible.

### 11.5 Finalization

- Determine candidates from best-so-far plus the final population, ranked by Section 11.4.
- Take up to `max_candidates`, preferring feasible individuals. If `max_candidates > 1`, drop structurally identical genomes before selecting (a converged population is full of clones; three identical schedules is a worse answer than one).
- If **no feasible individual exists**, return the top-ranked infeasible individuals with `feasible: false` and their violations. Do not fail the execution: reporting shortfalls is more useful than an error (REQ-COV-003).
- Record `termination_reason` from the stopper that fired.
- Persist `ExecutionState` as terminal and `ExecutionResult` in the store.

### 11.6 Variance

The MVP uses mutation only, no crossover, and no diversity preservation. Expect convergence and clone-heavy final populations; that is acceptable for a first engine, and `max_candidates` dedupe is what keeps it from surfacing as a product problem.

---

## 12. Fitness, feasibility, and constraints

### 12.1 Hard constraints

Represented as **violations**, never as very negative scores. A very negative score can be outbid by a sufficiently large soft gain; feasibility must be categorical.

- A worker must not be assigned to overlapping shifts.
- A worker must be available for every minute of an assigned shift.
- A worker must be qualified for the assigned job.
- A shift must respect the effective hard minimum and maximum length.
- A shift must overlap demand in at least one minute.
- Configured org caps must hold: maximum hours per week, maximum shifts per day.
- All worker/job references must exist in the problem context.

Selection and culling rank every feasible individual ahead of every infeasible one.

### 12.2 Soft objectives

Competing on the 0–100 scale:

- Coverage of required demand.
- Overstaffing / wasted labor minutes.
- Qualification mix (when not already infeasible).
- Shift length near a worker's preferred bounds.
- (Later: fairness, payroll cost, preference satisfaction, travel/back-to-back job changes.)

Soft objectives contribute through `FitnessConfig` weights.

### 12.3 Violation codes

Stable string constants, defined once in `models/scores.py`. Treat them as an API: the UI and the app layer aggregate on them.

- `worker_unavailable` — assigned minutes fall outside the worker's available windows.
- `worker_unqualified` — worker is not qualified for the shift's job.
- `worker_double_booked` — two shifts for the same worker overlap.
- `shift_too_short` / `shift_too_long` — outside effective hard bounds.
- `shift_outside_demand` — shift overlaps no demand window for its job.
- `weekly_hours_exceeded` — worker exceeds `maximum_hours_per_week`.
- `shifts_per_day_exceeded` — worker exceeds `maximum_shifts_per_day` on a local day.
- `unknown_reference` — shift names a worker or job absent from the problem.

Each violation carries enough context to be legible (`worker_id`, `job_id`, `start`, `end`, `shift_id`, `detail`) and to be aggregated.

### 12.4 Coverage, defined exactly

For each job *j*, using integer minutes:

- `required_j(t)` = Σ `required_workers` over *j*'s active requirement windows at *t*.
- `assigned_j(t)` = count of *j*'s planned shifts containing *t*.
- `covered_j = ∫ min(assigned_j(t), required_j(t)) dt`
- `over_j = ∫ max(0, assigned_j(t) − required_j(t)) dt`
- `required_total_j = ∫ required_j(t) dt`
- `assigned_total_j = ∫ assigned_j(t) dt`

Then:

- **Coverage score** = `100 · Σ covered_j / Σ required_total_j`. Higher is better; 100 means demand fully covered at every instant.
- **Overstaffing score** = `100 · (1 − Σ over_j / max(Σ required_total_j, 1))`, clamped to `[0, 100]`. 100 means no excess minutes.
- When `required_total_j == 0`, the job contributes nothing to coverage (no demand to cover) and its assigned minutes show up as excess. A whole problem with zero demand is a validation error, not a 100% score.

Implement this as a sweep over sorted interval endpoints per job — O(n log n) in that job's shifts and windows. Never build a per-minute array; a 28-day horizon at one-minute resolution is 40,320 entries per job, and the sweep is both faster and exact.

### 12.5 Shift length

Effective hard bounds resolve as:

```python
def effective_bounds(worker: WorkerInfo, policy: ShiftLengthPolicy) -> tuple[int, int]:
    minimum = worker.minimum_shift_minutes if worker.minimum_shift_minutes is not None else policy.minimum_minutes
    maximum = worker.maximum_shift_minutes if worker.maximum_shift_minutes is not None else policy.maximum_minutes
    return minimum, maximum
```

- Org defaults: minimum 120 minutes, maximum 720 minutes.
- Per-worker overrides are **hard**; they exist for contractual differences (part-time vs full-time).
- `preferred_*` fields are **soft** and scored, never enforced.
- Mutators use `policies.effective_bounds` to bound every boundary move, insert, and split. Scorers use the same function to emit `shift_too_short` / `shift_too_long`. One implementation, two consumers.

---

## 13. Initial concrete component set

Component ids are **globally unique across categories**, because the invocation input
union discriminates on `component_id` alone. The selector and culler are therefore
`select_top_n` and `cull_top_n` rather than both being `top_n`.

- **Seeder** — `random_shifts` — samples shifts inside demand windows for qualified,
  available workers, respecting hard bounds and the boundary grid.
- **Scorer** — `coverage` — covered requirement-minutes over total requirement-minutes;
  emits `shift_outside_demand` and `unknown_reference`. Weight 1.
- **Scorer** — `overstaffing` — assigned minutes beyond demand; weight 1.
- **Scorer** — `skills_match` — share of assigned minutes on qualified workers; emits
  `worker_unqualified`. Weight 1.
- **Scorer** — `shift_length` — hard bounds as violations, preferences as score; weight 1.
- **Scorer** — `availability` — emits `worker_unavailable`. Weight 0.
- **Scorer** — `double_booking` — emits `worker_double_booked`. Weight 0.
- **Scorer** — `schedule_limits` — emits `weekly_hours_exceeded` and
  `shifts_per_day_exceeded`. Weight 0.
- **Selector** — `select_top_n` — top `count` by the canonical ordering.
- **Mutator** — `random_shift` — weighted mix of worker reassignment, boundary nudge,
  deletion, and insertion for uncovered demand.
- **Culler** — `cull_top_n` — retains `target_size` best, honouring `preserve_best`.
- **Stopper** — `generation_count` — stops after `maximum_generations`, counting the
  seeded generation as generation 1.

Keep implementations simple. The goal is to prove the architecture and produce valid
candidate schedules, not to optimize quality immediately. Every component receives an
injected `random.Random`.

Optional pre-implementation sanity check: a greedy dispatch (sweep demand, assign the
least-loaded qualified available worker) is known to produce a feasible schedule quickly
and score well. Consider implementing it as a second seeder later — it is cheap and gives
the GA a feasible starting point, which is the biggest quality lever observed in
prototype work.

## 14. Local executor

```python
class LocalExecutor:
    def __init__(self, controller: SolverController, runner: ComponentRunner) -> None:
        self._controller = controller
        self._runner = runner

    def execute(self, execution_id: UUID) -> None:
        try:
            plan = self._controller.start(execution_id)
            while plan is not None:
                results = tuple(
                    self._runner.run(invocation) for invocation in plan.invocations
                )
                phase_result = PhaseResult(
                    execution_id=plan.execution_id,
                    phase_execution_id=plan.phase_execution_id,
                    results=results,
                )
                plan = self._controller.complete_phase(plan, phase_result)
        except Exception as exc:
            self._controller.fail(execution_id, f"{type(exc).__name__}: {exc}")
            raise
```

Requirements:

- Execute invocations in a deterministic order.
- Keep invocation execution independent of phase planning.
- Propagate component failures with execution, phase, component, and invocation context.
- Do not continue with partial results unless the phase explicitly defines partial-result semantics (none do in the MVP).
- Mark the execution `FAILED` through the controller on error, and re-raise.
- Hold no database session. The MVP in-memory implementation needs no persistence at all.

## 15. Future distributed executor considerations

Do not implement this now, but do not preclude it.

A future Celery executor can reuse `PhasePlan`, `ComponentInvocation`, `ComponentResult`, `PhaseResult`, `ComponentRunner`, `ExecutionStore`, and the controller unchanged. Likely flow: start/resume an execution → ask the controller for the next plan → dispatch one task per invocation → chord/aggregate → callback calls `complete_phase()` → dispatch next plan or leave the execution terminal.

Constraints to preserve now:

- Do not call `.get()` on Celery results from inside worker tasks.
- Chord header tasks must store results; do not set `ignore_result=True`.
- Make phase completion idempotent via `phase_execution_id`.
- Handle failed header tasks and callback retries explicitly.
- Consider a transactional outbox if committing phase state and dispatching the next group must be atomic.
- Configure JSON serialization; never rely on pickle.
- Every task must reconstruct its inputs from the serialized plan alone — which is why configuration lives in the input DTO.
- The controller must not know whether phase results came from a local loop or a chord.

---

## 16. Mapping candidates to persisted schedules

### 16.1 What the engine returns

An `ExecutionResult`:

```python
class CandidateSchedule(BaseModel):
    model_config = ConfigDict(frozen=True)

    candidate_id: UUID
    rank: int                      # 1 = best
    shifts: tuple[PlannedShift, ...]
    fitness: float
    scores: dict[str, float]       # component_id -> 0..100
    violations: tuple[Violation, ...]
    feasible: bool


class ExecutionResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    execution_id: UUID
    candidates: tuple[CandidateSchedule, ...]   # MVP: exactly one
    generation: int
    termination_reason: str
    random_seed: int
```

`candidate_id` is deterministic and stable, so a reviewer can reference a specific candidate when acceptance workflow exists later.

### 16.2 Persisting a candidate

The application/service layer converts a candidate into persistence entities:

1. Create a `Schedule` for the run: horizon, timezone, source template/context, execution id, candidate id and rank, seed, fitness, per-scorer scores, aggregated violations, termination reason.
2. Create one `Shift` per `PlannedShift` — no coalescing is required; the genome *is* the shift list.
3. Preserve the references required by the existing domain model (job, worker, required skills).

Do not put SQLModel construction or database writes in the engine. The converter lives in `services/` or `mappers/`, outside `engine/`.

Timestamps come from the slot-free genome directly and are already absolute instants; there is no index arithmetic to get wrong around DST. Store them timezone-aware.

### 16.3 Surfacing violations

A candidate can carry thousands of raw violations. The app layer aggregates them before display: group by `code`, count occurrences, collect affected workers/jobs and a handful of representative intervals. The raw list stays available on the result/artifact; the aggregated view is what a human reviews. REQ-SCHED-003 wants a reviewer to have a basis for accepting a schedule, and an unaggregated violation dump is not a basis.

---

## 17. Error handling and invariants

Use explicit engine/domain exceptions for:

- Unknown component id, category mismatch.
- Component input/result validation failure (including out-of-range scores, unknown individual ids, duplicate ids).
- Invalid phase result; unknown or already-completed phase.
- Population size mismatch; seeder contributions not summing to population size.
- Shift with non-existent worker/job reference.
- Non-minute-aligned or inverted time values.
- Missing scorer output for a scored individual.
- Component execution failure.

Do not use assertions for user- or data-driven validation. Assertions are for internal invariants that cannot be true simultaneously with correct validation.

Validate at boundaries. Do not re-validate entire populations inside inner loops; establish boundary validation first, then profile.

Invariants worth testing directly:

- `feasible == (len(violations) == 0)`, always.
- Every score in `[0, 100]`; every fitness in `[0, 100]`.
- Population always holds exactly `population_size` individuals after `SEED` and after every `CULL`.
- Individual ids unique within a population; shifts canonicalized.
- Same seed + same request ⇒ identical result.

---

## 18. Testing strategy

Tests must not require PostgreSQL, Redis, RabbitMQ, Celery, or FastAPI.

### Protocol and component tests

- Static type checking (mypy) proves each component satisfies its protocol.
- Each component tested with small hand-constructed DTO inputs.
- Deterministic behavior verified with fixed seeds.
- Invalid references, inverted intervals, non-minute-aligned times, and empty inputs.
- Components do not mutate their inputs.
- Scorers tested for score range, id coverage, and that no scorer reads another's output.

### Interval math tests

`intervals.py` deserves direct tests, because everything depends on it:

- Overlap detection at half-open boundaries (touching intervals do not overlap).
- Sweep-line coverage with adjacent, overlapping, and nested windows.
- Sum of required headcount across simultaneously active windows.
- Overhang: shift wider than the window on one side; zero-overlap shift.
- Containment of a shift in the union of available windows, including gaps.
- Minutes-per-local-day across a DST spring-forward (23h) and fall-back (25h) day.
- Grid snapping idempotence; bounds clamping at exactly minimum and maximum.

### Runner and registry tests

- Resolve every component in every category.
- Reject duplicate ids across categories, unknown ids, category mismatches.
- Validate invocation input/result types; reject `dict` payloads.
- Errors carry execution, phase, component, and invocation context.

### Controller tests

- Generation-zero seed/score flow.
- Phase ordering for a full generation; that offspring are the only scored set in later generations.
- Score aggregation across multiple scorers, weighted mean, weight-0 exclusion.
- Feasibility-first ordering, including "infeasible with huge fitness loses to feasible".
- Deterministic tie-break at identical fitness.
- `preserve_best` survives culling.
- Stopper aggregation and termination reason.
- Duplicate `phase_execution_id` rejected; idempotent replay.
- Zero-feasible finalization returns infeasible candidates with `feasible: false`.
- `max_candidates` dedupe of identical genomes.

### Executor tests

- Full execution through `LocalExecutor`, result read from the store.
- Component error fails the execution rather than producing a partial schedule.
- Same request + seed twice ⇒ byte-identical `ExecutionResult`.

### Scheduling behavior tests

Tiny problems over a two-day horizon with a few workers and jobs:

- Fully covered schedule.
- Unavailable worker; partially available window.
- Unqualified worker.
- Overlapping shifts for one worker.
- Under- and overstaffing, measured in minutes.
- Two overlapping windows for one job summing headcount.
- Shift overhanging a window edge (soft) vs a shift with no demand at all (hard).
- Shift exactly at minimum and maximum length; one minute under and over.
- Weekly hours cap and shifts-per-day cap, including a shift crossing midnight.
- Zero-demand problem rejected at validation.

Prefer small deterministic fixtures over large random scenarios.

---

## 19. Implementation order

1. **Time and intervals:** `models/time.py`, `intervals.py`, `policies.py`, with tests. Everything else depends on this and it is the cheapest place to be wrong.
2. **Models:** problem, genome, violations, fitness, `ExecutionRequest`/`ExecutionState`/`ExecutionResult`, `CandidateSchedule`.
3. **Protocols:** component protocols plus solver/controller/executor.
4. **Registry:** explicit registration, global id uniqueness, category checks.
5. **Runner:** typed dispatch, input/result validation, contextual errors.
6. **Components:** seeder, seven scorers, selector, mutator, culler, stopper.
7. **Solver definition:** register components, wire `FitnessConfig` defaults.
8. **Controller:** state machine, aggregation, idempotency, finalization.
9. **Local executor and in-memory store.**
10. **Mapper:** candidate → `Schedule`/`Shift` construction, outside `engine/` (see Section 21 for the schema work this depends on).
11. **Tests throughout** each layer; do not defer them.

Acceptance for the initial implementation: a test constructs a `SchedulingProblem` in memory, runs a complete execution through `LocalExecutor`, and reads a single feasible `CandidateSchedule` from the store — with no database, broker, or API.

---

## 20. Guidance to the coding agent

- Inspect the existing repository before creating files. Match its Python version (3.12), formatting (black), lint (flake8, max line length 180), and test (pytest) conventions.
- Do not modify API routes, database models, migrations, or frontend code as part of the engine work.
- Additional third-party dependencies are permitted. This is a substantial change to the application, and the right library is better than a hand-rolled approximation. When you add one: pin the exact version in `api/requirements.txt` (the file already pins everything), prefer a maintained library over an abandoned one, and record in your implementation note what it replaced and why it earned its place.
- A dependency still has to justify itself. Do not add one for something the standard library already does well — interval math over sorted endpoints, `datetime`/`zoneinfo` arithmetic, and `random.Random` all stay stdlib. Do not use this latitude to introduce a numerical/optimization framework, a workflow engine, or a GA library that would replace the architecture described here.
- Keep protocols in dedicated modules and concrete implementations in `components/`.
- Use Pydantic DTOs for all component and execution boundaries, `frozen=True` wherever possible.
- Keep the engine free of ORM models, sessions, Celery imports, and infrastructure dependencies.
- Components are stateless; configuration arrives in the input DTO; randomness is injected.
- Never represent time as slots, indices, or floats. Integer minutes, aware datetimes, half-open intervals.
- Share `intervals.py` and `policies.py`. Do not reimplement bound or overlap logic inside a component.
- Keep the canonical ordering in one place; selection, culling, and ranking must not each have their own comparator.
- Do not leave `dict[str, Any]` placeholders in component or phase contracts.
- Do not implement a plugin framework, a workflow engine, or the shift-split mutation.
- If a detail is underspecified, choose the simplest design consistent with this document and record the decision in a short implementation note. Do not expand scope into unrelated scheduling-domain problems.

The primary architectural test: the same solver definition, controller, registry, runner, and execution store work with both a synchronous local executor and a future asynchronous distributed executor, with no execution-specific behavior inside components or algorithm logic.

---

## 21. Persistence changes this design implies (not part of the engine work)

Listed so the follow-on work is not rediscovered late. None of this belongs in the engine change.

1. **`Schedule`** — the artifact: horizon, timezone, status (`generated` / `under_review` / `accepted`), execution id, candidate id and rank, seed, fitness, per-scorer score breakdown, aggregated violations, termination reason.
2. **`Job`** (role) — name, required skill set. Replaces "a shift carries an arbitrary skill list" with "a job owns one skill set" (Section 4.1).
3. **`CoverageRequirement`** — job, window, required headcount. The demand input.
4. **`WorkerAvailability`** — windows per worker; needed by nearly every constraint.
5. **`Shift` reshape** — add `job_id`, make the worker a single FK rather than a many-to-many link, add `schedule_id`. A planned shift is one worker on one job.
6. **`Worker` additions** — shift-length overrides, preferences, employment classification for caps.
7. **Pay rate and fairness accumulators** — only when payroll/fairness scorers exist; deliberately out of scope now.
8. **Transactional generation** — persisting a candidate and its shifts atomically, and (later) accepting a candidate.

---

## Appendix A. Deferred operator: shift-split mutation

Designed for now, implemented later, so the current operator set does not block it.

**Purpose.** Address fragmentation without the cost of a discrete slot grid. Splitting lets the search subdivide an over-long shift into two viable shifts that can then serve different workers, jobs, or demand windows.

**Contract.**

- Input: one parent individual, one target `shift_id`, and a split boundary drawn from `[start + min, end − min]` where `min` is the effective hard minimum for the shift's worker (and for whatever worker receives the new half).
- The boundary is snapped to `boundary_granularity_minutes` and must leave both halves within effective hard bounds. Reject the move otherwise; do not clamp into an invalid shape.
- Output: the original shift replaced by two shifts with fresh ids, same `worker_id` and `job_id`, contiguous at the boundary.

**Why it must be paired.** A split on its own is fitness-neutral: same worker, same job, same covered minutes. It changes only shift-length preference and per-day shift counts. So the operator is designed as a **compound mutation**: split, then reassign the worker on one of the halves. Split-alone, as a pure mutation, would just be neutral drift in the population.

**Why it matters.** Free boundary mutation at slot resolution is what produced 15-minute fragments in prototype work (minimum observed length 1 segment; 2–5 sub-hour shifts per candidate). Bounded, grid-snapped, min-length-respecting splits give the same expressive freedom with none of the degenerate results.

**Related knobs to keep in view** (not implemented now): a maximum-shifts-per-day cap (already in `ScheduleLimits`) and a soft preference for contiguous work.

---

## Appendix B. Open questions

None blocking. These are recorded so they are decided deliberately rather than by accident:

- Whether `max_candidates > 1` should use diversity selection rather than pure ranking.
- Whether a greedy dispatch seeder is worth adding (evidence suggests it is).
- Whether parallelism across scorers is worth it before profiling.
- Whether fairness and payroll scorers require additional problem context (pay rates, accumulated undesirable shifts) — they will.

---

## Appendix C. Implementation notes

Decisions taken where this document was underspecified, recorded as Section 20 requires.

1. **Component ids are globally unique.** The invocation union discriminates on `component_id`, so the selector and culler are `select_top_n` and `cull_top_n`. The registry enforces uniqueness across all categories, not within one.
2. **Phase execution ids** are derived from `(execution_id, phase, label, generation)`. `SCORE` runs twice per generation, so the label is `population` or `offspring`; the label also feeds the derived component seeds, so the two scoring passes never share random state.
3. **Idempotent replay** hands back the plan the controller last issued for that execution rather than re-deriving it, so a duplicate callback cannot advance the state machine.
4. **Constraint-only scorers still return a score** (share of minutes inside availability, share of minutes not double-booked, share of limit checks passed). Their influence on fitness is denied purely by `weight = 0`, which keeps every scorer's contract uniform: score every individual, report violations where rules break.
5. **`preserve_best` is validated but structurally guaranteed.** Rank-based retention keeps the best candidates by construction; the controller additionally tracks `best_so_far` across generations so a converged population cannot lose the best candidate ever seen.
6. **The seeder refuses placements it cannot satisfy completely.** If no worker is available and conflict-free for a candidate shift, it places nothing rather than emitting an invalid shift. Coverage shortfalls therefore surface as score rather than as availability violations, and the seed population is mostly feasible — which matters, because infeasible length mutations are what collapsed the population in prototype work.
7. **Mutator shares are explicit.** Each mutator config declares a `share`, validated to sum to `offspring_count`, so offspring counts are exact and plans are deterministic. Probabilistic shares were rejected for that reason.
8. **`maximum_generations` counts the seeded generation.** A value of 1 evaluates the seed population and stops.
9. **A result may contain infeasible candidates.** When nothing feasible exists, the best-ranked infeasible individuals are returned with `feasible = false` and their violations. Callers must not assume a candidate is feasible.
10. **Boundary validation lives in the controller**, not in the Pydantic models. Model validators enforce per-value invariants (aware, minute-aligned, ordered, in-range); `validate_problem_context` cross-checks entities and runs once at `start`.
11. **Time arithmetic is done in UTC.** Adding a `timedelta` to an aware datetime is wall-clock arithmetic and silently produces wrong instants across DST transitions; `to_utc` is applied before every measurement, and local time is used only for day attribution and grid snapping.
12. **`E203` is ignored in the flake8 config** because it conflicts with black's slice formatting; black owns whitespace.

### Running the checks

From `api/`: `black --check .`, `flake8 .`, `pytest`. From the repository root: `mypy` (configured in `pyproject.toml`, scoped to `engine/` and the candidate mapper).
