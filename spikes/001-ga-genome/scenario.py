"""Synthetic scenario for the scheduler GA spike.

Model B shapes it: demand is coverage requirements (window + skill + headcount),
not pre-made shifts. Times are 15-minute segments, as specified in REQ-SCH-003.

Deliberately hand-tuned to be *feasible but tight*: enough total capacity, but
unevenly distributed, so a solver has to think.
"""

from dataclasses import dataclass, field

SEG_MINUTES = 15
SEG_HOURS = 0.25
SEGMENTS_PER_DAY = 24 * 60 // SEG_MINUTES  # 96


@dataclass(frozen=True)
class Requirement:
    """A coverage requirement: this window needs this many people with this skill."""

    id: int
    day: int
    start: int  # inclusive segment index
    end: int  # exclusive
    skill: str
    headcount: int

    def segments(self):
        return range(self.start, self.end)


@dataclass
class Worker:
    id: int
    name: str
    skills: frozenset
    rate: float  # currency per hour
    max_hours_week: float = 40.0


@dataclass
class Scenario:
    days: int
    requirements: list = field(default_factory=list)
    workers: list = field(default_factory=list)
    # derived
    req_segments: dict = field(default_factory=dict)  # req_id -> list[segment]
    segment_reqs: dict = field(default_factory=dict)  # segment -> list[req_id]
    qualified_reqs: dict = field(default_factory=dict)  # worker_id -> set[req_id]

    @property
    def segments(self):
        return self.days * SEGMENTS_PER_DAY

    def total_required_segments(self):
        return sum(len(r.segments()) * r.headcount for r in self.requirements)


def build(days=14, seed=7):
    """Two weeks, three shift-shaped demand windows per day."""
    import random

    rng = random.Random(seed)
    reqs = []
    rid = 0
    for day in range(days):
        base = day * SEGMENTS_PER_DAY
        # Day shift: 07:00-19:00, two RNs
        reqs.append(Requirement(rid, day, base + 28, base + 76, "rn", 2))
        rid += 1
        # Evening: 15:00-23:00, one aide
        reqs.append(Requirement(rid, day, base + 60, base + 92, "aide", 1))
        rid += 1
        # Night: 23:00-07:00 (crosses midnight), one aide
        reqs.append(Requirement(rid, day, base + 92, base + SEGMENTS_PER_DAY + 28, "aide", 1))
        rid += 1

    workers = []
    wid = 0
    for name, skills, rate in [
        ("rn", ["rn", "aide"], (42, 48)),
        ("aide", ["aide"], (22, 30)),
        ("tech", ["tech", "aide"], (28, 34)),
    ]:
        count = {"rn": 8, "aide": 12, "tech": 4}[name]
        for i in range(count):
            workers.append(
                Worker(wid, f"{name}-{i}", frozenset(skills), round(rng.uniform(*rate), 2))
            )
            wid += 1

    sc = Scenario(days=days, requirements=reqs, workers=workers)
    _derive(sc)
    return sc


def _derive(sc):
    for r in sc.requirements:
        sc.req_segments[r.id] = list(r.segments())
        for seg in r.segments():
            sc.segment_reqs.setdefault(seg, []).append(r.id)
    req_by_id = {r.id: r for r in sc.requirements}
    for w in sc.workers:
        sc.qualified_reqs[w.id] = {
            r.id for r in sc.requirements if r.skill in w.skills
        }
    sc._req_by_id = req_by_id
    return sc


def req_by_id(sc, rid):
    return sc._req_by_id[rid]


def capacity_report(sc):
    """Sanity-check the scenario: demand vs qualified, availability-adjusted capacity."""
    by_skill = {}
    for r in sc.requirements:
        by_skill.setdefault(r.skill, 0)
        by_skill[r.skill] += len(sc.req_segments[r.id]) * r.headcount * SEG_HOURS
    weeks = sc.days / 7
    supply = {}
    for w in sc.workers:
        for s in w.skills:
            supply.setdefault(s, 0)
            supply[s] += w.max_hours_week * weeks
    return {
        "demand_hours": {k: round(v, 1) for k, v in by_skill.items()},
        "supply_hours": {k: round(v, 1) for k, v in supply.items()},
        "required_segments": sc.total_required_segments(),
        "total_segments": sc.segments,
    }


if __name__ == "__main__":
    sc = build()
    print("segments:", sc.segments)
    print("requirements:", len(sc.requirements))
    print("workers:", len(sc.workers))
    for k, v in capacity_report(sc).items():
        print(f"{k}: {v}")
