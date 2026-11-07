"""Spike 003: is the GA better than a greedy dispatcher, and does seeding help?

Control: greedy least-loaded construction - what a competent human dispatcher does.
Treatment: GA with that solution in generation 0 (memetic seeding).
"""

import statistics

from engine import CellsGenome, WEEK_SEGMENTS, hard_violations, run_ga
from scenario import SEG_HOURS, build

SC = build()
WORKERS = {w.id: w for w in SC.workers}


def used_hours(slots, wid, week):
    return sum(
        SEG_HOURS
        for (r2, w2), segs in slots.items()
        if w2 == wid
        for s in segs
        if s // WEEK_SEGMENTS == week
    )


def greedy(sc):
    """Assign each window's slots to the least-loaded qualified workers, in chunks
    that respect weekly hours. No search, no mutation - just a dispatcher."""
    slots = {}
    for req in sorted(sc.requirements, key=lambda r: sum(1 for w in sc.workers if r.skill in w.skills)):
        qualified = [w.id for w in sc.workers if req.skill in w.skills]
        segs = list(req.segments())
        for _slot in range(req.headcount):
            pos = 0
            while pos < len(segs):
                weeks = {s // WEEK_SEGMENTS for s in segs[pos:]}
                best, best_cap = None, 0.0
                for wid in qualified:
                    cap = min(WORKERS[wid].max_hours_week - used_hours(slots, wid, wk) for wk in weeks)
                    if cap > best_cap:
                        best, best_cap = wid, cap
                if best is None or best_cap <= 0:
                    break
                take = max(1, min(len(segs) - pos, int(best_cap / SEG_HOURS)))
                key = (req.id, best)
                slots.setdefault(key, set()).update(segs[pos : pos + take])
                pos += take
    return CellsGenome(slots)


baseline = greedy(SC)
m = baseline.metrics(SC)
print("=== greedy dispatcher (control) ===")
print(
    {
        "hard": hard_violations(m),
        "uncovered": m["uncovered"],
        "over_hours": m["over_hours"],
        "overlap": m["overlap"],
        "skill": m["skill_violations"],
        "cost": m["cost"],
        "fairness": m["fairness"],
        "assigned_hours": m["assigned_hours"],
        "shift_instances": len(baseline.shifts_out(SC)),
    }
)

CFG = dict(scheme="lexicographic", pop_size=40, generations=60)
print("\n=== plain GA (random seeding) vs memetic (greedy in generation 0) ===")
for label, seeded in (("plain", None), ("greedy-seeded", [baseline])):
    runs = [run_ga(SC, CellsGenome, seed=s, seed_genomes=seeded, **CFG) for s in (1, 2, 3)]
    hards = [hard_violations(r["best"]) for r in runs]
    print(
        f"  {label:14s} hard={hards} median={statistics.median(hards)}"
        f" cost={[r['best']['cost'] for r in runs]}"
        f" fairness={[round(r['best']['fairness'], 2) for r in runs]}"
        f" feasible={sum(1 for h in hards if h == 0)}/3"
    )
    print(f"    hard per gen (seed 1, /10): {[h['hard'] for h in runs[0]['history']][::10]}")
