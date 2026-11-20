from __future__ import annotations

from uuid import UUID, uuid4

from scheduler_api.engine.aggregation import (
    aggregate_cull,
    aggregate_mutate,
    aggregate_scores,
    aggregate_seed,
    aggregate_select,
    aggregate_stop,
)
from scheduler_api.engine.exceptions import (
    DuplicateInvocationError,
    InvalidPhaseResultError,
    StalePhaseResultError,
    UnknownExecutionError,
)
from scheduler_api.engine.models.assignment import Individual
from scheduler_api.engine.models.component_io import (
    ComponentInputPayload,
    CullInput,
    MutateInput,
    ScoreInput,
    SeedInput,
    SelectInput,
    StopInput,
)
from scheduler_api.engine.models.execution import (
    ExecutionState,
    ExecutionStatus,
    FailureInfo,
    ScoreTarget,
)
from scheduler_api.engine.models.phase import (
    ComponentCategory,
    ComponentInvocation,
    PhasePlan,
    PhaseResult,
    PhaseType,
)
from scheduler_api.engine.models.population import Population
from scheduler_api.engine.models.problem import SchedulingProblem
from scheduler_api.engine.models.results import ExecutionResult
from scheduler_api.engine.models.solver_spec import SolverSpec
from scheduler_api.engine.ranking import rank_individuals, total_score
from scheduler_api.engine.randomness import derive_seed


class GeneticAlgorithmController:
    """Drive a single GA execution through deterministic phase plans."""

    def __init__(
        self,
        spec: SolverSpec,
        problem: SchedulingProblem,
    ) -> None:
        self._spec = spec
        self._problem = problem
        self._state: ExecutionState | None = None
        self._pending_plan: PhasePlan | None = None
        self._decisions: dict[UUID, PhasePlan | None] = {}

    @property
    def spec(self) -> SolverSpec:
        return self._spec

    @property
    def problem(self) -> SchedulingProblem:
        return self._problem

    def start(self, execution_id: UUID) -> PhasePlan | None:
        if self._state is None:
            self._state = ExecutionState(
                execution_id=execution_id,
                problem=self._problem,
                population=Population(individuals=()),
            )
            plan = self._seed_plan()
            self._pending_plan = plan
            return plan

        if self._state.status is ExecutionStatus.RUNNING:
            return self._pending_plan
        return None

    def complete_phase(self, plan: PhasePlan, result: PhaseResult) -> PhasePlan | None:
        if self._state is None:
            raise UnknownExecutionError(plan.execution_id)

        if plan.phase_execution_id in self._decisions:
            if result.execution_id != self._state.execution_id:
                raise InvalidPhaseResultError(
                    "phase result execution ID does not match controller state"
                )
            return self._decisions[plan.phase_execution_id]

        if (
            self._pending_plan is None
            or plan.phase_execution_id != self._pending_plan.phase_execution_id
        ):
            raise StalePhaseResultError(result.phase_execution_id)

        self._validate_result(plan, result)
        next_plan = self._apply(plan, result)
        self._decisions[plan.phase_execution_id] = next_plan
        self._pending_plan = next_plan
        return next_plan

    def fail(self, execution_id: UUID, failure: FailureInfo) -> None:
        if self._state is None:
            return
        if self._state.execution_id != execution_id:
            return
        if self._state.status is not ExecutionStatus.RUNNING:
            return
        self._transition(status=ExecutionStatus.FAILED, failure=failure)
        self._pending_plan = None

    def get_state(self, execution_id: UUID) -> ExecutionState:
        state = self._state
        if state is None or state.execution_id != execution_id:
            raise UnknownExecutionError(execution_id)
        return state

    def get_result(self, execution_id: UUID) -> ExecutionResult:
        state = self.get_state(execution_id)
        best = state.best_individual
        return ExecutionResult(
            execution_id=state.execution_id,
            status=state.status,
            generation=state.generation,
            best_individual=best,
            best_total_score=state.best_total_score,
            best_feasible=best is not None and best.feasible,
            termination_reason=state.termination_reason,
            failure=state.failure,
        )

    def _validate_result(self, plan: PhasePlan, result: PhaseResult) -> None:
        if result.execution_id != plan.execution_id:
            raise InvalidPhaseResultError(
                "phase result execution ID does not match plan"
            )
        if result.phase_execution_id != plan.phase_execution_id:
            raise InvalidPhaseResultError(
                "phase result phase execution ID does not match plan"
            )

        invocations = {
            invocation.invocation_id: invocation for invocation in plan.invocations
        }
        seen: set[UUID] = set()
        for entry in result.results:
            if entry.invocation_id in seen:
                raise DuplicateInvocationError(entry.invocation_id)
            invocation = invocations.get(entry.invocation_id)
            if invocation is None:
                raise InvalidPhaseResultError(
                    f"unknown invocation {entry.invocation_id}"
                )
            if (
                entry.component_id != invocation.component_id
                or entry.category != invocation.category
            ):
                raise InvalidPhaseResultError(
                    f"result for invocation {entry.invocation_id} does not "
                    "match the planned component"
                )
            seen.add(entry.invocation_id)

        if len(seen) != len(invocations):
            raise InvalidPhaseResultError("phase result is missing invocation results")

    def _apply(self, plan: PhasePlan, result: PhaseResult) -> PhasePlan | None:
        if plan.phase is PhaseType.SEED:
            population = aggregate_seed(
                plan,
                result,
                self._spec.population_size,
                self._problem,
            )
            self._transition(
                population=population,
                score_target=ScoreTarget.POPULATION,
            )
            return self._score_plan(population)

        if plan.phase is PhaseType.SCORE:
            return self._apply_score(plan, result)

        if plan.phase is PhaseType.SELECT:
            selected = aggregate_select(plan, result, self._state.population)
            self._transition(selected_parents=selected)
            return self._mutate_plan(selected)

        if plan.phase is PhaseType.MUTATE:
            parents = self._state.selected_parents
            if parents is None:
                raise InvalidPhaseResultError("cannot mutate without selected parents")
            offspring = aggregate_mutate(plan, result, parents, self._problem)
            self._transition(
                offspring=offspring,
                score_target=ScoreTarget.OFFSPRING,
            )
            return self._score_plan(offspring)

        if plan.phase is PhaseType.CULL:
            return self._apply_cull(plan, result)

        if plan.phase is PhaseType.CHECK_STOP:
            should_stop, reason = aggregate_stop(plan, result)
            if should_stop:
                self._transition(
                    status=ExecutionStatus.COMPLETED,
                    termination_reason=reason,
                )
                return None
            return self._select_plan()

        raise InvalidPhaseResultError(f"unknown phase {plan.phase}")

    def _apply_score(self, plan: PhasePlan, result: PhaseResult) -> PhasePlan | None:
        state = self._state
        if state.score_target is ScoreTarget.POPULATION:
            target = state.population
        elif state.score_target is ScoreTarget.OFFSPRING:
            target = state.offspring
        else:
            raise InvalidPhaseResultError("cannot score without a score target")
        if target is None:
            raise InvalidPhaseResultError("score target population is missing")

        scored = aggregate_scores(plan, result, target)
        best, best_total, elites = self._select_best(scored)

        update: dict[str, object] = {
            "best_individual": best,
            "best_total_score": best_total,
            "elite_individuals": elites,
            "score_target": None,
        }
        if state.score_target is ScoreTarget.POPULATION:
            update["population"] = scored
        else:
            update["offspring"] = scored

        self._transition(**update)
        if state.score_target is ScoreTarget.POPULATION:
            return self._select_plan()
        return self._cull_plan()

    def _apply_cull(self, plan: PhasePlan, result: PhaseResult) -> PhasePlan:
        state = self._state
        offspring = state.offspring
        if offspring is None:
            raise InvalidPhaseResultError("cannot cull without offspring")

        candidates = Population(
            individuals=state.population.individuals + offspring.individuals
        )
        retained = aggregate_cull(
            plan,
            result,
            candidates,
            self._spec.population_size,
            state.elite_individuals,
        )
        self._transition(
            population=retained,
            selected_parents=None,
            offspring=None,
            score_target=None,
            generation=state.generation + 1,
        )
        return self._check_stop_plan()

    def _transition(self, **updates: object) -> None:
        state = self._state
        assert state is not None
        candidate = state.model_copy(update=updates)
        self._state = ExecutionState.model_validate(candidate.model_dump())

    def _select_best(
        self, newly_scored: Population
    ) -> tuple[Individual | None, float | None, tuple[Individual, ...]]:
        assert self._state is not None
        ordered: list[Individual] = []
        previous_best = self._state.best_individual
        if previous_best is not None:
            ordered.append(previous_best)
        ordered.extend(self._state.elite_individuals)
        ordered.extend(newly_scored.individuals)
        deduped: dict[UUID, Individual] = {}
        for individual in ordered:
            deduped.setdefault(individual.id, individual)

        ranked = rank_individuals(tuple(deduped.values()), self._spec.scoring_policy)
        best = ranked[0] if ranked else None
        best_total = (
            total_score(best, self._spec.scoring_policy) if best is not None else None
        )
        elites = ranked[: self._spec.elitism_count]
        return best, best_total, elites

    def _build_plan(
        self,
        phase: PhaseType,
        payloads: list[tuple[str, ComponentCategory, ComponentInputPayload]],
    ) -> PhasePlan:
        assert self._state is not None
        invocations = tuple(
            ComponentInvocation(
                invocation_id=uuid4(),
                component_id=component_id,
                category=category,
                input=payload,
            )
            for component_id, category, payload in payloads
        )
        return PhasePlan(
            execution_id=self._state.execution_id,
            phase_execution_id=uuid4(),
            generation=self._state.generation,
            phase=phase,
            invocations=invocations,
        )

    def _seed_plan(self) -> PhasePlan:
        assert self._state is not None
        payloads: list[tuple[str, ComponentCategory, ComponentInputPayload]] = []
        for index, seeder in enumerate(self._spec.seeders):
            payloads.append(
                (
                    seeder.component_id,
                    ComponentCategory.SEEDER,
                    SeedInput(
                        category="seeder",
                        problem=self._problem,
                        population_size=seeder.contribution,
                        rng_seed=derive_seed(
                            self._spec.random_seed,
                            0,
                            PhaseType.SEED,
                            seeder.component_id,
                            index,
                        ),
                    ),
                )
            )
        return self._build_plan(PhaseType.SEED, payloads)

    def _score_plan(self, target: Population) -> PhasePlan:
        assert self._state is not None
        payloads: list[tuple[str, ComponentCategory, ComponentInputPayload]] = [
            (
                scorer_id,
                ComponentCategory.SCORER,
                ScoreInput(
                    category="scorer",
                    problem=self._problem,
                    population=target,
                ),
            )
            for scorer_id in self._spec.scorer_ids
        ]
        return self._build_plan(PhaseType.SCORE, payloads)

    def _select_plan(self) -> PhasePlan:
        assert self._state is not None
        payload = SelectInput(
            category="selector",
            population=self._state.population,
            count=self._spec.population_size,
            scoring_policy=self._spec.scoring_policy,
        )
        return self._build_plan(
            PhaseType.SELECT,
            [
                (
                    self._spec.selector_id,
                    ComponentCategory.SELECTOR,
                    payload,
                )
            ],
        )

    def _mutate_plan(self, parents: Population) -> PhasePlan:
        assert self._state is not None
        payloads: list[tuple[str, ComponentCategory, ComponentInputPayload]] = []
        for index, mutator in enumerate(self._spec.mutators):
            payloads.append(
                (
                    mutator.component_id,
                    ComponentCategory.MUTATOR,
                    MutateInput(
                        category="mutator",
                        problem=self._problem,
                        parents=parents,
                        offspring_count=len(parents.individuals)
                        * mutator.offspring_per_parent,
                        rng_seed=derive_seed(
                            self._spec.random_seed,
                            self._state.generation,
                            PhaseType.MUTATE,
                            mutator.component_id,
                            index,
                        ),
                    ),
                )
            )
        return self._build_plan(PhaseType.MUTATE, payloads)

    def _cull_plan(self) -> PhasePlan:
        assert self._state is not None
        offspring = self._state.offspring
        if offspring is None:
            raise InvalidPhaseResultError("cannot cull without offspring")
        candidates = Population(
            individuals=self._state.population.individuals + offspring.individuals
        )
        payload = CullInput(
            category="culler",
            population=candidates,
            target_size=self._spec.population_size,
            scoring_policy=self._spec.scoring_policy,
            elite_individuals=self._state.elite_individuals,
        )
        return self._build_plan(
            PhaseType.CULL,
            [
                (
                    self._spec.culler_id,
                    ComponentCategory.CULLER,
                    payload,
                )
            ],
        )

    def _check_stop_plan(self) -> PhasePlan:
        assert self._state is not None
        state = self._state
        best = state.best_individual
        payloads: list[tuple[str, ComponentCategory, ComponentInputPayload]] = [
            (
                stopper_id,
                ComponentCategory.STOPPER,
                StopInput(
                    category="stopper",
                    execution_id=state.execution_id,
                    generation=state.generation,
                    population_size=len(state.population.individuals),
                    best_individual_id=best.id if best is not None else None,
                    best_total_score=state.best_total_score,
                    best_feasible=best is not None and best.feasible,
                ),
            )
            for stopper_id in self._spec.stopper_ids
        ]
        return self._build_plan(PhaseType.CHECK_STOP, payloads)


__all__ = ["GeneticAlgorithmController"]
