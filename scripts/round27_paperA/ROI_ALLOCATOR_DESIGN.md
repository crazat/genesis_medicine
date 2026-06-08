# ROI Allocator — exploit/explore compute-allocation engine (design synthesis)

**Date:** 2026-06-08. **Trigger:** user request to make the autonomous compute orchestrator a
"world-best" ROI/balance system, grounded in broad literature. Four independent parallel surveys
(bandits/RL · Bayesian-opt/VoI · self-driving labs · portfolio/scheduling) **converged on one design.**

## The problem
One box (24-core CPU + 1 GPU) split each moment between two arms:
- **A = EXPLOIT** — extend reliability statistics (σ_iptm, σ_E) on KNOWN binders. Low variance,
  **value KNOWN and decaying** (publication-closest, paper_A/B).
- **B = EXPLORE** — de novo molecule discovery + structure-reliability gating. High variance,
  **rare large payoff** (a novel reliable binder = a 4th paper). Option value.

Old policy was heuristic ("exploit primary, explore≠0, fill idle GPU, eyeball diminishing returns").
New policy is a **quantitative cost-aware index allocator**.

## Convergent result from the 4 surveys
1. **Model A analytically** (its value is known): marginal value of cycle *n* = per-cycle shrinkage of
   the standard error of a σ estimate, SE(σ̂)=σ/√(2(n−1)) ⇒ marginal ≈ **s/(2√2·(n−1)^{3/2})**, decaying
   as **n^(−3/2)**. (Bandit survey's discounted-value, BO survey's SE-decay, portfolio's 1/√n all agree.)
2. **Model B with option value / posterior sampling** (its value is unknown & high-variance): value ≈
   **P(hit)·payoff** with a Beta posterior on P(hit); high variance keeps B's share strictly positive
   (Kelly puts σ² in the *denominator*, not zero). Add a novelty bonus inside B (MAP-Elites / RND) so it
   doesn't re-mine one scaffold.
3. **Decide by marginal value PER GPU-HOUR** (cost-aware acquisition = Gittins/Knowledge-Gradient index):
   fund argmax(MV/GPU-hr). Stop an arm when its marginal value < its GPU cost (Xie 2025: EI ≤ cost).
4. **Hard floor on B** (March 1991: greedy feedback over-refines exploit and lets exploration atrophy →
   "effective short-run, self-destructive long-run"). Floor = our standing "explore=0 방치 금지" rule.
5. **Deadline anneal** (DQN/BAVT/SDL): shrink B near a submission deadline. Currently mild (A is also past
   its plateau, so the binding consideration is option value, not deadline).
6. **Value-density backfill** for idle slots: ρ = value/(resource-hours); never idle (DRF + SLURM backfill).

## Why this beats the old heuristic (measured)
At n=33: **MV_A = 6.98e-5 vs MV_B = 1.11** → EXPLORE by 4 orders of magnitude. The reliability cascade was
being run on momentum despite near-zero marginal value (σ_iptm inter-cycle <0.003 plateau at n≈28). The
allocator makes this quantitative and reallocates the GPU to the high-option-value de novo track.

## Implementation (files in scripts/round27_paperA/ + explore_denovo_mmp1/)
- **roi_allocator.py** — the decision engine. `--decide` prints `ARM|KIND|CYCLE|SEED`; `--json` full state;
  `--log ARM KIND` appends to roi_allocation_log.csv (for the March-floor recent-fraction check).
  Subjective inputs (the ONLY knobs, documented in-file): LAMBDA_A, LAMBDA_B, P_HIT_B, S_SIGMA, KELLY_LAMBDA=0.4, B_FLOOR=0.15.
- **gpu_roi_supervisor.sh** — value-density backfill daemon (poll 45s). Keeps the GPU saturated with the
  highest-ROI Boltz job, one at a time. Priority ladder: finish triage → deep-σ on survivors (GPU-dense,
  directory-batched) → backfill with exploit cycle. No-kill, setsid-robust, boltz pinned 19-23.
- **explore_denovo_mmp1/phase2b_deep_sigma.sh** — GPU-DENSE de novo deep-σ: ONE boltz invocation over a
  directory of top-20 survivors × 100 poses (fixes the per-molecule triage's GPU-idle gaps = the "GPU 최대화" fix).

## GPU-utilization lesson (from the "GPU 최대화" request)
Per-molecule cofold (1 boltz call/molecule) wastes GPU on repeated model-load/MSA init → low duty cycle.
**Directory-batched cofold** (1 call over many YAMLs, like the reliability cascade's 15-ligand dir) keeps the
GPU saturated. All future de novo GPU work uses directory-batching; the supervisor serializes one GPU-dense
job at a time and backfills instantly on completion.

## Adopt next (from self-driving-lab survey, not yet implemented)
- MAP-Elites archive for B (bin by scaffold/QED/MW, keep best-per-bin) — fixes the top-60 single-scaffold
  (indolinone-sulfonamide) convergence already visible.
- Pareto gating for B on (σ_iptm, σ_E, ADMET, novelty) instead of one composite score.
- Productivity-weighted supervisor: track realized value/GPU-hr per arm and update LAMBDA_* online.

## Key citations
Auer 2002 (UCB); Russo TS tutorial; Gittins 1979 / Whittle; Frazier-Powell Knowledge Gradient;
Garivier-Moulines 2011 (discounted UCB); Srinivas 2010 (GP-UCB); Xie 2025 (cost-aware stopping);
Kelly 1956 / MacLean-Thorp-Ziemba (fractional Kelly); Weitzman 1979 (Pandora reservation value);
March 1991 (exploration/exploitation); Ghodsi 2011 (DRF); A-Lab (Nature 2023); Google AI co-scientist
(arXiv:2502.18864); SDL benchmarking (arXiv:2508.06642); MAP-Elites (Mouret-Clune 2015).
