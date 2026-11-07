"""Spike 001: cells genome vs shift-instance genome - same problem, same budget."""

import json
import statistics

from engine import CellsGenome, ShiftsGenome, hard_violations, run_ga
from scenario import build, capacity_report

SC = build()
CFG = dict(scheme="lexicographic", pop_size=40, generations=60)


def fragmentation(genome, sc):
    shifts = genome.shifts_out(sc)
    lens = [e - s for (_r, s, e, _w) in shifts]
    if not lens:
        return None
    return {
        "instances": len(shifts),
        "median_len": statistics.median(lens),
        "min_len": min(lens),
        "under_1h": sum(1 for n in lens if n < 4),
    }


print("scenario:", json.dumps(capacity_report(SC)))
print()

for label, cls in (("cells", CellsGenome), ("shifts", ShiftsGenome)):
    runs = [run_ga(SC, cls, seed=s, **CFG) for s in (1, 2, 3)]
    print(f"=== {label} ===")
    for r in runs:
        b = r["best"]
        print(
            f"  seed {r['seed']}: hard={hard_violations(b):4d}"
            f" (uncov={b['uncovered']} over={b['over_hours']} ovl={b['overlap']} skill={b['skill_violations']})"
            f" cost={b['cost']:9.2f} fair={b['fairness']:6.2f}"
            f" {r['seconds']}s {round(1000 * r['seconds'] / r['evals'], 2)}ms/eval"
        )
    hards = [hard_violations(r["best"]) for r in runs]
    print(
        f"  hard: {hards} median={statistics.median(hards)}"
        f" feasible={sum(1 for h in hards if h == 0)}/3"
        f" costs={[r['best']['cost'] for r in runs]}"
    )
    print(f"  hard per gen (seed 1, /10): {[h['hard'] for h in runs[0]['history']][::10]}")
    print(f"  structure: {fragmentation(runs[0]['final_pop'][0], SC)}")
    print()
