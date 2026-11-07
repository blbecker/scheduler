"""Spike 002: does the aggregation scheme change the answer?

Takes a real candidate pool from a run, restricts to the feasible tier (equal hard
violations), and ranks that same pool under three schemes.
"""

import itertools
import statistics

from engine import (
    CellsGenome,
    ShiftsGenome,
    _norm,
    hard_violations,
    rank_population,
    run_ga,
)
from scenario import build

SC = build()


def kendall_tau(xs, ys):
    n = len(xs)
    conc = disc = 0
    for i, j in itertools.combinations(range(n), 2):
        a = (xs[i] - xs[j])
        b = (ys[i] - ys[j])
        if a * b > 0:
            conc += 1
        elif a * b < 0:
            disc += 1
    total = conc + disc
    return round((conc - disc) / total, 3) if total else None


def pool_from(kind, seed=1):
    cls = CellsGenome if kind == "cells" else ShiftsGenome
    run = run_ga(SC, cls, scheme="lexicographic", pop_size=40, generations=60, seed=seed)
    metrics = run["final_metrics"]
    floor = min(hard_violations(m) for m in metrics)
    tier = [m for m in metrics if hard_violations(m) == floor]
    return floor, tier


for kind in ("cells", "shifts"):
    floor, tier = pool_from(kind)
    print(f"=== {kind}: feasible tier = {len(tier)} candidates at hard={floor} ===")
    if len(tier) < 3:
        print("  (too few candidates in the tier to rank)\n")
        continue

    costs = [m["cost"] for m in tier]
    fairs = [m["fairness"] for m in tier]
    print(f"  raw units -> cost range {min(costs):.0f}..{max(costs):.0f} "
          f"(spread {max(costs) - min(costs):.0f}); fairness range "
          f"{min(fairs):.2f}..{max(fairs):.2f} (spread {max(fairs) - min(fairs):.2f})")
    print(f"  => in a raw sum, 1 unit of cost is worth {1:.0f} and 1 unit of fairness "
          f"{1:.0f}; cost spread is {round((max(costs) - min(costs)) / max(1e-9, max(fairs) - min(fairs)), 1)}x "
          f"the fairness spread, so cost decides the ranking by arithmetic accident.")

    schemes = ("raw", "normalized", "lexicographic")
    scores = {s: rank_population(tier, s) for s in schemes}
    picks = {}
    for s in schemes:
        order = sorted(range(len(tier)), key=lambda i: scores[s][i], reverse=True)
        top = tier[order[0]]
        picks[s] = order[0]
        print(f"  {s:14s} top-1: cost={top['cost']:9.2f} fairness={top['fairness']:6.2f}")

    for a, b in itertools.combinations(schemes, 2):
        va = [scores[a][i] if not isinstance(scores[a][i], tuple) else scores[a][i][1] for i in range(len(tier))]
        vb = [scores[b][i] if not isinstance(scores[b][i], tuple) else scores[b][i][1] for i in range(len(tier))]
        print(f"  rank agreement {a} vs {b}: tau={kendall_tau(va, vb)}")

    best = picks["lexicographic"]
    print(f"  lexical pick vs raw pick identical: {picks['raw'] == best}")
    print()

# How much does the scheme steer the search itself (not just the ranking)?
print("=== same run, different scheme driving selection ===")
for scheme in ("raw", "normalized", "lexicographic"):
    runs = [run_ga(SC, ShiftsGenome, scheme=scheme, pop_size=40, generations=60, seed=s) for s in (1, 2, 3)]
    print(
        f"  {scheme:14s} hard={[hard_violations(r['best']) for r in runs]}"
        f" cost={[r['best']['cost'] for r in runs]}"
        f" fairness={[round(r['best']['fairness'], 2) for r in runs]}"
    )
