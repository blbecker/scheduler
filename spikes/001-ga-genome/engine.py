"""Shared GA engine for the scheduler spike.

Two genome representations of the SAME problem (Model B: coverage requirements;
shifts are decision variables):

  CellsGenome  - (requirement, worker) -> arbitrary set of 15-min segments.
                 No shift objects exist. Coverage may fragment freely.
  ShiftsGenome - explicit shift instances (requirement, start, end, worker).
                 Every assignment is contiguous by construction.

A third thing this file learned the hard way: assignment must be attributed to a
*requirement*, not just to a segment. With overlapping demand windows (a 07-19 day
shift and a 15-23 evening shift on the same day) a bare worker->segments genome
cannot express which requirement the worker is covering, so skill validity becomes
undecidable. Both representations here carry the requirement id.

Everything is throwaway: hardcoded, no config, no persistence.
"""

import math
import random
import statistics
import time
from collections import defaultdict

from scenario import SEGMENTS_PER_DAY, SEG_HOURS, req_by_id

WEEK_SEGMENTS = 7 * SEGMENTS_PER_DAY


# --------------------------------------------------------------------------- #
# scoring
# --------------------------------------------------------------------------- #
def evaluate(sc, slots):
    """slots: iterable of (req_id, worker_id, segments). O(assigned segments)."""
    workers_by_id = {w.id: w for w in sc.workers}
    covered = defaultdict(int)  # (req_id, seg) -> workers covering it
    worker_seg = defaultdict(int)  # (worker_id, seg) -> times assigned
    week_hours = defaultdict(float)
    hours = defaultdict(float)
    skill_violations = 0
    missing_by_skill = defaultdict(int)

    for rid, wid, segs in slots:
        req = req_by_id(sc, rid)
        qualified = req.skill in workers_by_id[wid].skills
        if not qualified:
            missing_by_skill[req.skill] += 1
        for seg in segs:
            hours[wid] += SEG_HOURS
            week_hours[(wid, seg // WEEK_SEGMENTS)] += SEG_HOURS
            worker_seg[(wid, seg)] += 1
            covered[(rid, seg)] += 1
            if not qualified:
                skill_violations += 1

    uncovered = 0
    for req in sc.requirements:
        for seg in sc.req_segments[req.id]:
            short = req.headcount - covered.get((req.id, seg), 0)
            if short > 0:
                uncovered += short

    overlap = sum(count - 1 for count in worker_seg.values() if count > 1)
    over_hours = sum(
        1
        for (wid, _week), h in week_hours.items()
        if h > workers_by_id[wid].max_hours_week + 1e-9
    )
    cost = sum(hours[wid] * workers_by_id[wid].rate for wid in hours)
    all_hours = [hours.get(w.id, 0.0) for w in sc.workers]
    fairness = statistics.pstdev(all_hours) if len(all_hours) > 1 else 0.0

    return {
        "uncovered": uncovered,
        "skill_violations": skill_violations,
        "over_hours": over_hours,
        "overlap": overlap,
        "cost": round(cost, 2),
        "fairness": round(fairness, 4),
        "assigned_hours": round(sum(hours.values()), 2),
        "missing_by_skill": dict(missing_by_skill),
    }


def hard_violations(m):
    return m["uncovered"] + m["skill_violations"] + m["over_hours"] + m["overlap"]


# --------------------------------------------------------------------------- #
# aggregation schemes  (spike 002)
# --------------------------------------------------------------------------- #
def _norm(values):
    lo, hi = min(values), max(values)
    if math.isclose(lo, hi):
        return [0.5 for _ in values]
    return [(v - lo) / (hi - lo) for v in values]


def rank_population(metrics, scheme):
    """Fitness per candidate; higher is better. Lexicographic returns tuples."""
    if scheme == "raw":
        # Sum the scores as they come. Currency is thousands, fairness is a
        # handful of hours: one objective silently wins by magnitude.
        return [-(hard_violations(m) * 1000 + m["cost"] + m["fairness"]) for m in metrics]

    cost = _norm([m["cost"] for m in metrics])
    fair = _norm([m["fairness"] for m in metrics])

    if scheme == "normalized":
        return [
            -(hard_violations(m) * 1000 + (0.5 * cost[i] + 0.5 * fair[i]) * 100)
            for i, m in enumerate(metrics)
        ]
    if scheme == "lexicographic":
        return [
            (-hard_violations(m), -(0.5 * cost[i] + 0.5 * fair[i]))
            for i, m in enumerate(metrics)
        ]
    raise ValueError(scheme)


def key_of(fitness):
    return fitness if isinstance(fitness, tuple) else (fitness,)


# --------------------------------------------------------------------------- #
# genomes
# --------------------------------------------------------------------------- #
class CellsGenome:
    """(requirement, worker) -> set(segments). Shifts do not exist as objects."""

    kind = "cells"

    def __init__(self, slots):
        self.slots = slots

    @classmethod
    def seed(cls, sc, rng):
        slots = {}
        for req in sc.requirements:
            qualified = [w.id for w in sc.workers if req.skill in w.skills]
            for wid in rng.sample(qualified, min(req.headcount, len(qualified))):
                slots[(req.id, wid)] = set(req.segments())
        return cls(slots)

    def clone(self):
        return CellsGenome({k: set(v) for k, v in self.slots.items()})

    def mutate(self, sc, rng):
        g = self.clone()
        keys = list(g.slots)
        if not keys:
            return g
        for _ in range(rng.choice([1, 1, 2])):
            op = rng.random()
            rid, wid = rng.choice(keys)
            segs = g.slots.get((rid, wid)) or set()
            if not segs:
                continue
            req = req_by_id(sc, rid)
            qualified = [w.id for w in sc.workers if req.skill in w.skills and w.id != wid]

            if op < 0.35 and qualified:
                other = rng.choice(qualified)
                g.slots.pop((rid, wid), None)
                g.slots[(rid, other)] = g.slots.setdefault((rid, other), set()) | segs

            elif op < 0.60 and qualified and len(segs) > 1:
                # Fragment: hand part of the coverage to another worker. Cells
                # allow this; a shift-instance genome would have to split.
                ordered = sorted(segs)
                cut = rng.randrange(1, len(ordered))
                part = set(ordered[cut:]) if rng.random() < 0.5 else set(ordered[:cut])
                other = rng.choice(qualified)
                g.slots[(rid, wid)] = segs - part
                g.slots[(rid, other)] = g.slots.setdefault((rid, other), set()) | part

            elif op < 0.80:
                worst = self._most_overloaded(sc)
                if worst is None:
                    continue
                w_rid, w_wid, week = worst
                movable = {s for s in g.slots.get((w_rid, w_wid), set()) if s // WEEK_SEGMENTS == week}
                cands = [w.id for w in sc.workers if req_by_id(sc, w_rid).skill in w.skills and w.id != w_wid]
                if movable and cands:
                    other = rng.choice(cands)
                    g.slots[(w_rid, w_wid)] = g.slots.get((w_rid, w_wid), set()) - movable
                    g.slots[(w_rid, other)] = g.slots.setdefault((w_rid, other), set()) | movable

            else:
                if len(segs) > 1:
                    ordered = sorted(segs)
                    cut = rng.randrange(1, len(ordered))
                    g.slots[(rid, wid)] = set(ordered[:cut])
        return CellsGenome({k: v for k, v in g.slots.items() if v})

    def _most_overloaded(self, sc):
        per = defaultdict(float)
        holder = {}
        for (rid, wid), segs in self.slots.items():
            for seg in segs:
                week = seg // WEEK_SEGMENTS
                per[(wid, week)] += SEG_HOURS
                holder[(wid, week)] = (rid, wid, week)
        limit = {w.id: w.max_hours_week for w in sc.workers}
        worst = None
        for (wid, week), h in per.items():
            over = h - limit[wid]
            if over > 0 and (worst is None or over > worst[0]):
                worst = (over, holder[(wid, week)])
        return worst[1] if worst else None

    def to_slots(self, sc):
        return [(rid, wid, segs) for (rid, wid), segs in self.slots.items()]

    def metrics(self, sc):
        return evaluate(sc, self.to_slots(sc))

    def shifts_out(self, sc):
        """Shifts are *derived* after the fact, by contiguity."""
        out = []
        for (rid, wid), segs in self.slots.items():
            ordered = sorted(segs)
            if not ordered:
                continue
            start = prev = ordered[0]
            for seg in ordered[1:]:
                if seg == prev + 1:
                    prev = seg
                    continue
                out.append((rid, start, prev + 1, wid))
                start = prev = seg
            out.append((rid, start, prev + 1, wid))
        return out


class ShiftsGenome:
    """Explicit shift instances: (requirement, start, end, worker)."""

    kind = "shifts"

    def __init__(self, shifts):
        self.shifts = shifts

    @classmethod
    def seed(cls, sc, rng):
        shifts = []
        for req in sc.requirements:
            qualified = [w.id for w in sc.workers if req.skill in w.skills]
            for wid in rng.sample(qualified, min(req.headcount, len(qualified))):
                shifts.append((req.id, req.start, req.end, wid))
        return cls(shifts)

    @classmethod
    def from_cells(cls, sc, cells):
        return cls(cells.shifts_out(sc))

    def clone(self):
        return ShiftsGenome(list(self.shifts))

    def _most_overloaded(self, sc):
        limit = {w.id: w.max_hours_week for w in sc.workers}
        per = defaultdict(float)
        idx = {}
        for i, (_rid, start, end, wid) in enumerate(self.shifts):
            week = start // WEEK_SEGMENTS
            per[(wid, week)] += (end - start) * SEG_HOURS
            idx[(wid, week)] = i
        worst = None
        for (wid, week), h in per.items():
            over = h - limit[wid]
            if over > 0 and (worst is None or over > worst[0]):
                worst = (over, idx[(wid, week)])
        return worst[1] if worst else None

    def mutate(self, sc, rng):
        g = self.clone()
        for _ in range(rng.choice([1, 1, 2])):
            if not g.shifts:
                g.shifts.append(self._random_shift(sc, rng))
                continue
            op = rng.random()
            i = rng.randrange(len(g.shifts))
            rid, start, end, wid = g.shifts[i]
            req = req_by_id(sc, rid)
            qualified = [w.id for w in sc.workers if req.skill in w.skills]

            if op < 0.20:
                worst = self._most_overloaded(sc)
                if worst is None:
                    continue
                w_rid, w_start, w_end, w_wid = g.shifts[worst]
                cands = [w.id for w in sc.workers if req_by_id(sc, w_rid).skill in w.skills and w.id != w_wid]
                if cands:
                    g.shifts[worst] = (w_rid, w_start, w_end, rng.choice(cands))

            elif op < 0.40:
                g.shifts[i] = (rid, start, end, rng.choice(qualified))

            elif op < 0.58:
                # Move a boundary: the engine's freedom (ADR 0004).
                delta = rng.choice([-8, -4, -1, 1, 4, 8])
                if rng.random() < 0.5:
                    start = max(req.start, min(end - 1, start + delta))
                else:
                    end = min(req.end, max(start + 1, end + delta))
                g.shifts[i] = (rid, start, end, wid)

            elif op < 0.72:
                if end - start > 2:
                    cut = rng.randrange(start + 1, end)
                    g.shifts[i] = (rid, start, cut, wid)
                    g.shifts.append((rid, cut, end, rng.choice(qualified)))

            elif op < 0.84:
                same = [(j, s) for j, s in enumerate(g.shifts) if j != i and s[0] == rid and s[3] == wid]
                if same:
                    j, (_r, s2, e2, _w) = same[0]
                    g.shifts[i] = (rid, min(start, s2), max(end, e2), wid)
                    del g.shifts[j]

            elif op < 0.94:
                del g.shifts[i]

            else:
                g.shifts.append(self._random_shift(sc, rng))

        g._repair(sc)
        return g

    def _random_shift(self, sc, rng):
        req = rng.choice(sc.requirements)
        qualified = [w.id for w in sc.workers if req.skill in w.skills]
        start = rng.randrange(req.start, max(req.start + 1, req.end - 1))
        end = rng.randrange(start + 1, req.end + 1)
        return (req.id, start, end, rng.choice(qualified))

    def _repair(self, sc):
        """Remove worker-overlapping shifts: non-duplication is structural here."""
        by_worker = defaultdict(list)
        for s in self.shifts:
            by_worker[s[3]].append(s)
        kept = []
        for wid, group in by_worker.items():
            group.sort(key=lambda s: (s[1], s[2]))
            cursor = -1
            for rid, start, end, _w in group:
                if start < cursor:
                    continue
                kept.append((rid, start, end, wid))
                cursor = end
        self.shifts = kept
        return self

    def to_slots(self, sc):
        return [(rid, wid, range(start, end)) for rid, start, end, wid in self.shifts]

    def metrics(self, sc):
        return evaluate(sc, self.to_slots(sc))

    def shifts_out(self, sc):
        return list(self.shifts)


# --------------------------------------------------------------------------- #
# GA driver
# --------------------------------------------------------------------------- #
def run_ga(sc, genome_cls, scheme="lexicographic", pop_size=40, generations=60, seed=1, seed_genomes=None):
    rng = random.Random(seed)
    pop = [g.clone() for g in (seed_genomes or [])]
    pop += [genome_cls.seed(sc, rng) for _ in range(max(0, pop_size - len(pop)))]
    history = []
    t0 = time.perf_counter()

    for _gen in range(generations):
        metrics = [g.metrics(sc) for g in pop]
        fitness = rank_population(metrics, scheme)
        order = sorted(range(len(pop)), key=lambda i: key_of(fitness[i]), reverse=True)
        pop = [pop[i] for i in order]
        metrics = [metrics[i] for i in order]
        best = metrics[0]
        history.append(
            {
                "hard": hard_violations(best),
                "uncovered": best["uncovered"],
                "over_hours": best["over_hours"],
                "overlap": best["overlap"],
                "cost": best["cost"],
                "fairness": best["fairness"],
            }
        )
        elite = max(2, pop_size // 4)
        survivors = pop[:elite]
        children = []
        while len(children) < pop_size - elite:
            parent = survivors[rng.randrange(elite)]
            children.append(parent.clone().mutate(sc, rng))
        pop = survivors + children

    elapsed = time.perf_counter() - t0
    metrics = [g.metrics(sc) for g in pop]
    fitness = rank_population(metrics, scheme)
    order = sorted(range(len(pop)), key=lambda i: key_of(fitness[i]), reverse=True)
    return {
        "scheme": scheme,
        "kind": genome_cls.kind,
        "seed": seed,
        "pop_size": pop_size,
        "generations": generations,
        "seconds": round(elapsed, 2),
        "evals": pop_size * generations,
        "history": history,
        "final_metrics": [metrics[i] for i in order],
        "final_pop": [pop[i] for i in order],
        "best": metrics[order[0]],
        "feasible": hard_violations(metrics[order[0]]) == 0,
    }
