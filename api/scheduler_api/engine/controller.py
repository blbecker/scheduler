"""The GA lifecycle state machine.

The controller plans phases, aggregates phase results, and decides what happens
next. It holds no per-execution state of its own: everything needed to resume or
replay an execution lives in :class:`ExecutionState`.
"""

from __future__ import annotations

from typing import Sequence, cast
from uuid import UUID

from scheduler_api.engine.determinism import derive_seed, derive_uuid
from scheduler_api.engine.errors import (
    ComponentResultError,
    ExecutionNotFoundError,
    ExecutionStateError,
    PhaseResultError,
    UnknownComponentError,
)
from scheduler_api.engine.execution.runner import ComponentRunner
from scheduler_api.engine.execution.store import ExecutionStore
from scheduler_api.engine.models.component_io import (
    AvailabilityScoreInput,
    ComponentInputUnion,
    ComponentOutput,
    CoverageScoreInput,
    CullResult,
    DoubleBookingScoreInput,
    GenerationCountStopInput,
    MutateResult,
    OverstaffingScoreInput,
    RandomShiftMutateInput,
    ScheduleLimitsScoreInput,
    ScoreInput,
    ScoreResult,
    SeedRandomShiftsInput,
    SeedResult,
    SelectResult,
    ShiftLengthScoreInput,
    SkillsMatchScoreInput,
    StopResult,
    TopNCullInput,
    TopNSelectInput,
)
from scheduler_api.engine.models.config import (
    AvailabilityScorerConfig,
    CoverageScorerConfig,
    DoubleBookingScorerConfig,
    OverstaffingScorerConfig,
    ScheduleLimitsScorerConfig,
    ScorerConfig,
    ShiftLengthScorerConfig,
    SkillsMatchScorerConfig,
)
from scheduler_api.engine.models.execution import (
    ExecutionRequest,
    ExecutionState,
    ExecutionStatus,
    ScoringTarget,
)
from scheduler_api.engine.models.fitness import compute_fitness
from scheduler_api.engine.models.genome import Individual, Population
from scheduler_api.engine.models.phase import (
    ComponentCategory,
    ComponentInvocation,
    PhasePlan,
    PhaseResult,
    PhaseType,
)
from scheduler_api.engine.models.problem import (
    SchedulingProblem,
    validate_problem_context,
)
from scheduler_api.engine.models.results import CandidateSchedule, ExecutionResult
from scheduler_api.engine.models.scores import Violation
from scheduler_api.engine.ordering import better_of, best_of, rank_individuals
from scheduler_api.engine.protocols.solver import Solver


def score_input_for(
    config: ScorerConfig,
    problem: SchedulingProblem,
    individuals: Sequence[Individual],
) -> ComponentInputUnion:
    """Build the typed input DTO for one scorer.

    Explicit per-component dispatch: no instance checks on untyped dicts, and a new
    scorer has to be added here, which keeps serialization honest.
    """
    people = tuple(individuals)
    if isinstance(config, CoverageScorerConfig):
        return CoverageScoreInput(problem=problem, individuals=people, config=config)
    if isinstance(config, OverstaffingScorerConfig):
        return OverstaffingScoreInput(
            problem=problem, individuals=people, config=config
        )
    if isinstance(config, SkillsMatchScorerConfig):
        return SkillsMatchScoreInput(problem=problem, individuals=people, config=config)
    if isinstance(config, ShiftLengthScorerConfig):
        return ShiftLengthScoreInput(problem=problem, individuals=people, config=config)
    if isinstance(config, AvailabilityScorerConfig):
        return AvailabilityScoreInput(
            problem=problem, individuals=people, config=config
        )
    if isinstance(config, DoubleBookingScorerConfig):
        return DoubleBookingScoreInput(
            problem=problem, individuals=people, config=config
        )
    if isinstance(config, ScheduleLimitsScorerConfig):
        return ScheduleLimitsScoreInput(
            problem=problem, individuals=people, config=config
        )
    raise UnknownComponentError(
        f"no score input DTO for scorer {config.component_id!r}"
    )


class GAController:
    """Plans and aggregates generation phases for a GA solver."""

    def __init__(
        self,
        solver: Solver,
        runner: ComponentRunner,
        store: ExecutionStore,
    ) -> None:
        self._solver = solver
        self._runner = runner
        self._store = store

    # -- public API ---------------------------------------------------------

    def start(self, execution_id: UUID) -> PhasePlan | None:
        request = self._store.load_request(execution_id)
        try:
            existing = self._store.load_state(execution_id)
        except ExecutionNotFoundError:
            existing = None
        if existing is not None:
            if existing.status is ExecutionStatus.COMPLETED:
                raise ExecutionStateError(
                    f"execution {execution_id} is already complete"
                )
            return existing.next_plan
        validate_problem_context(request.problem)
        state = ExecutionState(
            execution_id=execution_id, status=ExecutionStatus.RUNNING
        )
        self._store.save_state(state)
        return self._issue(state, self._plan_seed(state, request))

    def complete_phase(self, plan: PhasePlan, result: PhaseResult) -> PhasePlan | None:
        self._validate_phase_result(plan, result)
        request = self._store.load_request(plan.execution_id)
        state = self._store.load_state(plan.execution_id)
        if state.completed(plan.phase_execution_id):
            # Idempotent replay: hand back the plan already issued, never re-apply.
            return state.next_plan
        if state.status is not ExecutionStatus.RUNNING:
            raise ExecutionStateError(
                f"execution {plan.execution_id} is {state.status.value}, not running"
            )
        state = state.with_phase_completed(plan.phase_execution_id)
        handler = {
            PhaseType.SEED: self._after_seed,
            PhaseType.SCORE: self._after_score,
            PhaseType.SELECT: self._after_select,
            PhaseType.MUTATE: self._after_mutate,
            PhaseType.CULL: self._after_cull,
            PhaseType.CHECK_STOP: self._after_check_stop,
        }[plan.phase]
        state, next_plan = handler(plan, result, state, request)
        return self._issue(state, next_plan)

    def result(self, execution_id: UUID) -> ExecutionResult:
        result = self._store.load_result(execution_id)
        if result is None:
            raise ExecutionStateError(f"execution {execution_id} has no result yet")
        return result

    def fail(self, execution_id: UUID, reason: str) -> None:
        try:
            state = self._store.load_state(execution_id)
        except ExecutionNotFoundError:
            return
        self._store.save_state(
            state.model_copy(
                update={
                    "status": ExecutionStatus.FAILED,
                    "failure_reason": reason,
                    "next_plan": None,
                }
            )
        )

    # -- phase handlers -----------------------------------------------------

    def _after_seed(
        self,
        plan: PhasePlan,
        result: PhaseResult,
        state: ExecutionState,
        request: ExecutionRequest,
    ) -> tuple[ExecutionState, PhasePlan]:
        individuals: list[Individual] = []
        for component_result in result.results:
            seeded = cast(SeedResult, self._expect(component_result.result, SeedResult))
            individuals.extend(seeded.population.individuals)
        expected = request.settings.population_size
        if len(individuals) != expected:
            raise ComponentResultError(
                f"seeders produced {len(individuals)} individuals, expected {expected}"
            )
        population = Population(individuals=tuple(individuals))
        state = state.model_copy(
            update={
                "population": population,
                "generation": 0,
                "scoring_target": ScoringTarget.POPULATION,
            }
        )
        return state, self._plan_score(state, request, target=ScoringTarget.POPULATION)

    def _after_score(
        self,
        plan: PhasePlan,
        result: PhaseResult,
        state: ExecutionState,
        request: ExecutionRequest,
    ) -> tuple[ExecutionState, PhasePlan]:
        individuals = self._scored_individuals(plan)
        scores: dict[UUID, dict[str, float]] = {
            individual.id: {} for individual in individuals
        }
        violations: dict[UUID, list[Violation]] = {
            individual.id: [] for individual in individuals
        }
        for component_result in result.results:
            scored = cast(
                ScoreResult, self._expect(component_result.result, ScoreResult)
            )
            for individual_id, value in scored.scores.items():
                scores[individual_id][scored.component_id] = value
            for individual_id, found in scored.violations.items():
                violations[individual_id].extend(found)

        evaluated: list[Individual] = []
        for individual in individuals:
            component_scores = scores[individual.id]
            for scorer in request.settings.scorers:
                if request.settings.weight_for(scorer.component_id) <= 0:
                    continue
                if scorer.component_id not in component_scores:
                    raise ComponentResultError(
                        f"scorer {scorer.component_id!r} produced no score for individual "
                        f"{individual.id}"
                    )
            fitness = compute_fitness(component_scores, request.settings.fitness)
            evaluated.append(
                individual.with_evaluation(
                    scores=component_scores,
                    violations=tuple(violations[individual.id]),
                    fitness=fitness,
                )
            )
        frozen = tuple(evaluated)
        if state.scoring_target is ScoringTarget.OFFSPRING:
            state = state.model_copy(
                update={"offspring": frozen, "scoring_target": None}
            )
            return state, self._plan_cull(state, request)
        population = Population(individuals=frozen)
        state = state.model_copy(
            update={
                "population": population,
                "scoring_target": None,
                "best_so_far": better_of(state.best_so_far, best_of(frozen)),
            }
        )
        return state, self._plan_select(state, request)

    def _after_select(
        self,
        plan: PhasePlan,
        result: PhaseResult,
        state: ExecutionState,
        request: ExecutionRequest,
    ) -> tuple[ExecutionState, PhasePlan]:
        selected = cast(
            SelectResult, self._expect(result.results[0].result, SelectResult)
        )
        if len(selected.individuals) != request.settings.parent_count:
            raise ComponentResultError(
                f"selector returned {len(selected.individuals)} individuals, expected "
                f"{request.settings.parent_count}"
            )
        population_ids = {individual.id for individual in state.population.individuals}
        stray = [
            individual.id
            for individual in selected.individuals
            if individual.id not in population_ids
        ]
        if stray:
            raise ComponentResultError(
                f"selector returned individuals outside the population: {stray}"
            )
        state = state.model_copy(update={"selected": selected.individuals})
        return state, self._plan_mutate(state, request)

    def _after_mutate(
        self,
        plan: PhasePlan,
        result: PhaseResult,
        state: ExecutionState,
        request: ExecutionRequest,
    ) -> tuple[ExecutionState, PhasePlan]:
        offspring: list[Individual] = []
        for component_result in result.results:
            mutated = cast(
                MutateResult, self._expect(component_result.result, MutateResult)
            )
            offspring.extend(mutated.individuals)
        expected = request.settings.offspring_count
        if len(offspring) != expected:
            raise ComponentResultError(
                f"mutators produced {len(offspring)} individuals, expected {expected}"
            )
        ids = [individual.id for individual in offspring]
        if len(set(ids)) != len(ids):
            raise ComponentResultError("mutators produced duplicate individual ids")
        state = state.model_copy(
            update={
                "offspring": tuple(offspring),
                "scoring_target": ScoringTarget.OFFSPRING,
            }
        )
        return state, self._plan_score(state, request, target=ScoringTarget.OFFSPRING)

    def _after_cull(
        self,
        plan: PhasePlan,
        result: PhaseResult,
        state: ExecutionState,
        request: ExecutionRequest,
    ) -> tuple[ExecutionState, PhasePlan]:
        population = cast(
            CullResult, self._expect(result.results[0].result, CullResult)
        ).population
        if len(population) != request.settings.population_size:
            raise ComponentResultError(
                f"culler retained {len(population)} individuals, expected "
                f"{request.settings.population_size}"
            )
        state = state.model_copy(
            update={
                "population": population,
                "selected": (),
                "offspring": (),
                "scoring_target": None,
                "best_so_far": better_of(
                    state.best_so_far, best_of(population.individuals)
                ),
            }
        )
        return state, self._plan_check_stop(state, request)

    def _after_check_stop(
        self,
        plan: PhasePlan,
        result: PhaseResult,
        state: ExecutionState,
        request: ExecutionRequest,
    ) -> tuple[ExecutionState, PhasePlan | None]:
        reasons: list[str] = []
        for component_result in result.results:
            stop = cast(StopResult, self._expect(component_result.result, StopResult))
            if stop.should_stop:
                reasons.append(stop.reason)
        if reasons:
            state = state.model_copy(
                update={
                    "status": ExecutionStatus.COMPLETED,
                    "termination_reason": reasons[0],
                    "next_plan": None,
                }
            )
            self._store.save_result(self._finalize(state, request))
            return state, None
        state = state.model_copy(update={"generation": state.generation + 1})
        return state, self._plan_select(state, request)

    # -- planning -----------------------------------------------------------

    def _plan_seed(self, state: ExecutionState, request: ExecutionRequest) -> PhasePlan:
        invocations = tuple(
            self._invocation(
                request.execution_id,
                PhaseType.SEED,
                state.generation,
                ComponentCategory.SEEDER,
                SeedRandomShiftsInput(
                    problem=request.problem,
                    population_size=config.contribution,
                    random_seed=derive_seed(
                        request.random_seed,
                        config.component_id,
                        state.generation,
                        "seed",
                    ),
                    config=config,
                ),
            )
            for config in request.settings.seeders
        )
        return self._plan(request, state, PhaseType.SEED, "seed", invocations)

    def _plan_score(
        self,
        state: ExecutionState,
        request: ExecutionRequest,
        *,
        target: ScoringTarget,
    ) -> PhasePlan:
        individuals = (
            state.population.individuals
            if target is ScoringTarget.POPULATION
            else state.offspring
        )
        invocations = tuple(
            self._invocation(
                request.execution_id,
                PhaseType.SCORE,
                state.generation,
                ComponentCategory.SCORER,
                score_input_for(config, request.problem, individuals),
            )
            for config in request.settings.scorers
        )
        return self._plan(request, state, PhaseType.SCORE, target.value, invocations)

    def _plan_select(
        self, state: ExecutionState, request: ExecutionRequest
    ) -> PhasePlan:
        invocation = self._invocation(
            request.execution_id,
            PhaseType.SELECT,
            state.generation,
            ComponentCategory.SELECTOR,
            TopNSelectInput(
                individuals=state.population.individuals,
                count=request.settings.parent_count,
                config=request.settings.selector,
            ),
        )
        return self._plan(request, state, PhaseType.SELECT, "select", (invocation,))

    def _plan_mutate(
        self, state: ExecutionState, request: ExecutionRequest
    ) -> PhasePlan:
        invocations = tuple(
            self._invocation(
                request.execution_id,
                PhaseType.MUTATE,
                state.generation,
                ComponentCategory.MUTATOR,
                RandomShiftMutateInput(
                    problem=request.problem,
                    parents=state.selected,
                    offspring_count=config.share,
                    random_seed=derive_seed(
                        request.random_seed,
                        config.component_id,
                        state.generation,
                        "mutate",
                    ),
                    config=config,
                ),
            )
            for config in request.settings.mutators
        )
        return self._plan(request, state, PhaseType.MUTATE, "mutate", invocations)

    def _plan_cull(self, state: ExecutionState, request: ExecutionRequest) -> PhasePlan:
        invocation = self._invocation(
            request.execution_id,
            PhaseType.CULL,
            state.generation,
            ComponentCategory.CULLER,
            TopNCullInput(
                candidates=(*state.population.individuals, *state.offspring),
                target_size=request.settings.population_size,
                preserve_best=request.settings.preserve_best,
                config=request.settings.culler,
            ),
        )
        return self._plan(request, state, PhaseType.CULL, "cull", (invocation,))

    def _plan_check_stop(
        self, state: ExecutionState, request: ExecutionRequest
    ) -> PhasePlan:
        best = state.best_so_far
        invocations = tuple(
            self._invocation(
                request.execution_id,
                PhaseType.CHECK_STOP,
                state.generation,
                ComponentCategory.STOPPER,
                GenerationCountStopInput(
                    generation=state.generation,
                    best_fitness=best.fitness if best is not None else None,
                    best_feasible=best.feasible if best is not None else False,
                    population_size=len(state.population),
                    config=config,
                ),
            )
            for config in request.settings.stoppers
        )
        return self._plan(request, state, PhaseType.CHECK_STOP, "stop", invocations)

    # -- helpers ------------------------------------------------------------

    @staticmethod
    def _plan(
        request: ExecutionRequest,
        state: ExecutionState,
        phase: PhaseType,
        label: str,
        invocations: tuple[ComponentInvocation, ...],
    ) -> PhasePlan:
        return PhasePlan(
            execution_id=request.execution_id,
            phase_execution_id=derive_uuid(
                request.execution_id, phase.value, label, state.generation
            ),
            generation=state.generation,
            phase=phase,
            invocations=invocations,
        )

    @staticmethod
    def _invocation(
        execution_id: UUID,
        phase: PhaseType,
        generation: int,
        category: ComponentCategory,
        payload: ComponentInputUnion,
    ) -> ComponentInvocation:
        return ComponentInvocation(
            invocation_id=derive_uuid(
                execution_id,
                phase.value,
                generation,
                category.value,
                payload.component_id,
            ),
            category=category,
            input=payload,
        )

    def _issue(self, state: ExecutionState, plan: PhasePlan | None) -> PhasePlan | None:
        self._store.save_state(state.model_copy(update={"next_plan": plan}))
        return plan

    @staticmethod
    def _expect(result: ComponentOutput, expected: type) -> ComponentOutput:
        if not isinstance(result, expected):
            raise ComponentResultError(
                f"expected a {expected.__name__}, received {type(result).__name__}"
            )
        return result

    @staticmethod
    def _scored_individuals(plan: PhasePlan) -> tuple[Individual, ...]:
        if not plan.invocations:
            raise PhaseResultError("score phase has no invocations")
        payload = plan.invocations[0].input
        if not isinstance(payload, ScoreInput):
            raise PhaseResultError("score phase invocation is not a score input")
        return payload.individuals

    @staticmethod
    def _validate_phase_result(plan: PhasePlan, result: PhaseResult) -> None:
        if result.execution_id != plan.execution_id:
            raise PhaseResultError("phase result names a different execution")
        if result.phase_execution_id != plan.phase_execution_id:
            raise PhaseResultError("phase result names a different phase execution")
        planned = {invocation.invocation_id for invocation in plan.invocations}
        completed = [
            component_result.invocation_id for component_result in result.results
        ]
        if len(set(completed)) != len(completed):
            raise PhaseResultError("phase result contains duplicate invocation ids")
        unknown = set(completed) - planned
        if unknown:
            raise PhaseResultError(
                f"phase result contains unknown invocations {sorted(map(str, unknown))}"
            )
        missing = planned - set(completed)
        if missing:
            raise PhaseResultError(
                f"phase result is missing invocations {sorted(map(str, missing))}"
            )

    def _finalize(
        self, state: ExecutionState, request: ExecutionRequest
    ) -> ExecutionResult:
        unique: dict[tuple, Individual] = {}
        pool: list[Individual] = list(state.population.individuals)
        if state.best_so_far is not None:
            pool.append(state.best_so_far)
        for individual in pool:
            unique.setdefault(individual.structural_key, individual)
        ranked = rank_individuals(tuple(unique.values()))
        feasible = tuple(individual for individual in ranked if individual.feasible)
        chosen = (feasible or ranked)[: request.settings.max_candidates]
        candidates = tuple(
            CandidateSchedule(
                candidate_id=derive_uuid(request.execution_id, "candidate", rank),
                rank=rank,
                shifts=individual.shifts,
                fitness=individual.fitness or 0.0,
                scores=dict(individual.scores),
                violations=individual.violations,
                feasible=individual.feasible,
            )
            for rank, individual in enumerate(chosen, start=1)
        )
        return ExecutionResult(
            execution_id=request.execution_id,
            candidates=candidates,
            generation=state.generation,
            termination_reason=state.termination_reason or "stopped",
            random_seed=request.random_seed,
        )
