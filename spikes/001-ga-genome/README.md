# GA solver spike — genome representation, aggregation, seeding

Throwaway experiment answering the questions the `specify-ga-solver` design left open.
Scenario: 2 weeks = 1344 fifteen-minute segments, 42 coverage requirements (day/evening/
night with skill + headcount), 24 workers with skills, pay rates and a 40h/week cap.
GA: tournament-free elitist hill climbing (top 25% survive, offspring = mutated elite),
pop 40, 60 generations, 3 seeds per configuration. Pure Python, no numpy, no caching.

Run: `python3 exp1_genome.py`, `exp2_aggregation.py`, `exp3_greedy.py`, `exp4_scaling.py`.

## Verdict: PARTIAL — the approach works, one representation choice and one spec gap are decisive

### What worked

1. **Both genomes reach feasibility.** With the fix below, every seed of both
   representations ends at hard violations 0 (coverage complete, no double-booking,
   no weekly-hour breach, no skill mismatch), typically by generation 10.
2. **Runtime is a non-issue at MVP scale.** Naive pure Python: 1.07 ms/eval at 7 days,
   2.19 at 14 days, 4.80 at 28 days — linear in demand, not quadratic. A 14-day run
   of 2,400 evaluations costs ~5 s single-threaded.
3. **Determinism is cheap.** Same seed → identical metrics *and* identical shift list.
   Different seed → ~1.2% cost difference (20,889.88 vs 21,141.65), i.e. seed variance
   is real but small.
4. **Repair beats penalty for non-duplication.** The shift-instance genome repairs
   worker overlaps on every mutation, so the search never wastes generations on
   structurally invalid members.

### What didn't (and the one thing that was actually broken)

**Attribution to a requirement is mandatory in the genome.** The first version modelled
a genome as `worker -> set(segments)`. With overlapping demand windows (a 07:00-19:00 day
requirement and a 15:00-23:00 evening requirement on the same day) that genome cannot
express *which* requirement a worker is covering, so skill validity is undecidable: a
correct greedy solution scored **224 phantom skill violations**. Changing the genome to
`(requirement, worker) -> segments` made every run feasible. This is not a solver detail;
it is a data-model requirement — an assignment must record the coverage requirement it
serves.

### Surprises

1. **A greedy dispatcher is nearly as good as the GA.** Least-loaded greedy construction
   is feasible at generation 0 with cost 20,667 / fairness 14.95. The 60-generation GA
   gets cost ~20,614 (0.3% better) and fairness 13.57-13.87 (8% better). For this
   scenario the genetic algorithm's value is **soft-objective optimization, not
   feasibility** — feasibility is a dispatching problem.
2. **Greedy seeding is free quality.** With the greedy solution in generation 0, the best
   candidate is feasible from the first generation and final results are equal or better
   (cost 20,593 best, fairness 13.46). Every run should therefore always have a feasible
   fallback candidate.
3. **The aggregation scheme changes the answer, not just the ordering.** In a pool of
   feasible candidates, cost spread is 174-198× the fairness spread, so a raw sum makes
   cost win by arithmetic accident: Kendall τ = 0.54 (cells) / 0.77 (shifts) against a
   normalized scheme, and a different winner. Driving the *search* with raw sum gives
   cost 20,082-20,231 with fairness 20.9-22.6, versus 20,502-20,728 with fairness 14.0-15.0
   for the normalized scheme: ~3% cheaper schedules for ~50% worse fairness.
4. **Normalized and lexicographic agree perfectly on feasible pools** (τ = 1.0): tiering
   only matters when infeasible candidates coexist with feasible ones. The ×1000-style
   hard penalty held in practice because soft spreads were ~200-300 ≪ 1000 — a
   tuning-dependent guarantee, not a structural one.
5. **Both representations produce absurd micro-shifts.** Min shift length 1-2 segments
   (15-30 minutes), 2-5 shifts under an hour per candidate. Mutating boundaries freely
   (a deliberate ADR 0004 freedom) fragments coverage unless a minimum shift length is
   enforced. Review screens full of 15-minute shifts are the obvious consequence.

### Recommendation for the real build

- **Genome: explicit shift instances keyed by requirement** — `(requirement, start, end,
  worker)`. Cells showed no quality advantage, fragments coverage, and cannot present the
  object the reviewer actually reviews.
- **Non-duplication by repair** (structural), skill match by construction; hard
  constraints must not rely on penalty magnitude.
- **Seed generation 0 with a greedy construction** and keep that candidate as the
  guaranteed-feasible fallback.
- **Specify before implementing:** minimum (and maximum) shift length, max shifts per day,
  and the aggregation formula with configurable weights. All three are product behavior
  that emerged as missing here.
- **Termination:** generation cap plus time budget; runtime is cheap enough that time is
  a UX choice, not a necessity.

### Follow-ups this spike does not answer

- Parallel evaluation across Celery workers (would break the determinism proven here
  unless each individual gets its own seeded stream).
- Whether the GA still beats greedy on harder scenarios (scarce skills, many
  incompatible constraints) — this scenario had ~50% slack on the tight skill.
- Crossover. The driver here uses mutation only; recombination is unproven.
