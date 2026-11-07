"""Spike 004: determinism (REQ-SOL-004) and runtime scaling with range length."""

import time

from engine import ShiftsGenome, hard_violations, run_ga
from scenario import build

print("=== determinism: same seed twice ===")
SC = build()
a = run_ga(SC, ShiftsGenome, seed=42, pop_size=30, generations=30)
b = run_ga(SC, ShiftsGenome, seed=42, pop_size=30, generations=30)
same_metrics = a["best"]["cost"] == b["best"]["cost"] and a["best"]["fairness"] == b["best"]["fairness"]
same_shifts = a["final_pop"][0].shifts_out(SC) == b["final_pop"][0].shifts_out(SC)
print(f"  identical metrics: {same_metrics} | identical shift list: {same_shifts}")
print(f"  cost {a['best']['cost']} vs {b['best']['cost']}, hard {hard_violations(a['best'])} vs {hard_violations(b['best'])}")

c = run_ga(SC, ShiftsGenome, seed=43, pop_size=30, generations=30)
print(f"  different seed (43): cost {c['best']['cost']} fairness {c['best']['fairness']} "
      f"(seed 42 gave {a['best']['cost']} / {a['best']['fairness']})")

print("\n=== scaling: range length vs wall clock (pop 30 x 30 generations) ===")
print(f"{'days':>5} {'segments':>9} {'reqs':>5} {'seconds':>8} {'ms/eval':>8} {'hard':>5} {'cost':>10}")
for days in (7, 14, 28):
    sc = build(days=days)
    t0 = time.perf_counter()
    r = run_ga(sc, ShiftsGenome, seed=1, pop_size=30, generations=30)
    wall = time.perf_counter() - t0
    print(
        f"{days:>5} {sc.segments:>9} {len(sc.requirements):>5} {wall:>8.2f} "
        f"{1000 * wall / (30 * 30):>8.2f} {hard_violations(r['best']):>5} {r['best']['cost']:>10.2f}"
    )

print("\n(naive pure-Python implementation, single process, no caching, no numpy)")
