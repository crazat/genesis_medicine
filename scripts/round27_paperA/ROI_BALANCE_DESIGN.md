# ROI / Exploit–Explore Balance — Design for a World-Class Autonomous Discovery Allocator

*Round-27 paper-A pipeline. Synthesized from a 2023–2026 frontier literature sweep
(bandits/BO, self-driving labs, multi-fidelity budgeting, novelty pricing). This doc is the
spec; `phase3_acquisition_select.py` is the first implementation.*

---

## 0. The one equation everything reduces to

Every sub-problem below — splitting CPU/GPU between arms, escalating SP→OPT→Hessian, deciding
when to stop scoring a pool, deciding which molecule to cofold next — is the **same Lagrangian**
seen from a different angle. Rank every unit of work by a single **cost-aware ROI index**:

```
ROI(job) = E[(value − g)+] / cost_in_core_hours       # expected marginal insight above
                                                        # the shadow price g, per core-hour
```

- `g` = the current "good enough" threshold = the shadow price λ of a scarce core-hour
  (Pandora's-box / Gittins reservation value; solves `E[(V−g)+] = cost`).
- **Water-filling:** at the optimum, every *active* arm has equal marginal value `V' = λ`.
  Pour compute into an arm until its marginal return falls to λ; then move.
- **Stop rule:** when `ROI ≤ 1` (i.e. `E[improvement] ≤ cost`) for all remaining work on an
  arm, the arm has saturated — reallocate.
- **Anti-idle:** never leave a slot empty while *any* job has `ROI > 1`.

This single index gives (i) reallocation, (ii) escalation order, (iii) stopping, (iv) anti-idle,
and (v) saturation detection. Build it once.

---

## 1. Diagnosis — where we already lead, where we are blindly greedy

We operate at **two levels**. They are in very different states.

### Level A — Resource allocation (CPU cores / GPU slots): **already near world-class.**
- Never-idle invariant, never-explore-zero floor, partitioned core-sets (exploit 0-18 / explore
  19-23), reactive refill on drain, OOM-safe GPU saturation. This is a hand-tuned water-filler and
  it works. The recent "stable-then-OOM" pain was a *VRAM fragmentation bug* (fixed with
  `expandable_segments`), **not** an allocation-logic flaw.
- Gap (minor, deferred): the reallocation is reactive/heuristic, not driven by a measured
  marginal-value signal. Upgrade = a discounted-UCB meta-arm allocator (§4-R5).

### Level B — Scientific decision (which molecules to spend the oracle on): **pure greed, zero loop.**
This is the gap between us and a state-of-the-art self-driving lab. Ground-truth (verified in code):
- Candidates ranked **once** by `composite_score = 0.40·QED + 0.35·ADMET_safety +
  0.15·ADMET_perm + 0.10·novelty`; then tiers are **strict rank-order slices** `rows[start:end]`
  processed in fixed order 1→2→3→4→5.
- **Zero feedback loop.** σ_iptm and σ_E are computed but *never read back* to re-select or
  re-rank. No bandit / UCB / Thompson / acquisition / active-learning anywhere.
- **No batch diversity.** `max_tanimoto_seed` is a static scoring feature, never an active
  selection constraint. Adjacent ranks are often near-duplicate scaffolds → the parallel GPU
  slots can cofold redundant molecules.
- **One-shot generation.** REINVENT mol2mol samples 120 once; no regenerate-on-success loop.

**Why this is wrong for *our* regime (the key insight):** the literature splits cleanly.
Pure greedy *wins* on frozen mega-libraries (MolPAL: 97.6 % of top-1000 at 2.4 % cost) because
you just want the top-k of a fixed list. But we are the **opposite regime** — a *small*,
*generative*, *multi-objective* loop — where greedy provably **collapses onto one scaffold** and
the winning policy is **diversity-clustered greedy + mild uncertainty + retrain each round**
(the REINVENT+ABFE "cluster-greedy" recipe, which converges in 3–4 rounds at ~250–500/round).
We currently implement none of the loop.

---

## 2. Pricing exploration on the exploit scale (so one index can compare them)

Exploration's payoff is heavy-tailed (most new molecules are mediocre; a rare one opens a new
chemical class / a new paper). A greedy ROI built on observed means is **structurally blind to
the tail**, so it under-explores. Fixes (all label-free, robust):

1. **Novelty vs a FIXED reference, never vs our own noisy scorer.**
   `nov_seed(m) = 1 − max_{s∈seeds} Tanimoto(ECFP4 m, s)` and
   `unc(m) = 1 − max_{c∈cofolded} Tanimoto(m, c)` (distance from the *visited* set).
   Pricing against fixed sets avoids the ICM "noisy-TV" trap = rewarding Boltz/xtb FP-noise as if
   it were discovery (cf. our R55 "σ is an upper bound / FP-noise floor" finding).
2. **Decaying scaffold-rarity bonus** `β / √(N(cell)+1)`, cell = Bemis-Murcko generic scaffold.
   Auto-decays as a chemotype fills → MAP-Elites-style spread, prevents scaffold collapse.
3. **Hard explore floor (barbell), heavy-tail-correct.** Reserve **≥15–20 %** of every batch for
   pure-novelty picks regardless of their exploit score; size the band with fractional-Kelly and
   estimate explore value with **median-of-means** (one jackpot/dud must not whipsaw the split).
   This is the principled form of our standing "explore must never hit 0" rule.

Mild weights matter: MolPAL shows over-trusting uncertainty *hurts*. Keep explore weights small
and constant (do not hand-cool a schedule; let the shrinking `unc`/filling `N(cell)` decay it).

---

## 3. The acquisition selector (THIS build) — closing the Level-B loop

`phase3_acquisition_select.py` replaces `rows[start:end]` with, per un-cofolded candidate:

```
acq(m) = z(composite_score)            # EXPLOIT (cheap reliable proxy)
       + w_nov · z(nov_seed)           # EXPLORE: into new chemotype space (fixed seeds)
       + w_unc · z(unc_cofolded)       # EXPLORE: into unvisited space (closes the loop)
       + w_scaf · β/√(N(cell)+1)       # EXPLORE: decaying anti-collapse rarity bonus
```

Batch of `N` assembled by **greedy local penalization** (the cheap discrete k-DPP / cluster-greedy):
`pick = argmax [ acq(m) − δ · max_{j∈picked} Tanimoto(m, j) ]`, updating scaffold counts as we go,
and the **last ⌈f·N⌉ slots reserved for pure-novelty** (the barbell floor). Output =
`phase3_next_batch.csv`, consumed by `phase2_build_inputs_tier6.py`. It reports the **distinct-
scaffold count of the acquisition batch vs the naive rank-order batch** — the quantified
exploit/explore gain at equal GPU cost.

Defaults: `N=80, w_nov=0.4, w_unc=0.4, w_scaf=0.4, β=1.0, δ=1.0, f_explore=0.2`. Forward hook:
`--use-surrogate` adds a kNN-predicted realized-binding term once the σ tables are clean (today
σ_iptm table is empty and gfn0 σ_E fails, so it stays off — garbage-in guard).

---

## 4. Roadmap — STATUS (2026-06-09, all R1–R7 implemented & verified)

- **R1 ✅ — acquisition selector** `phase3_acquisition_select.py`. Diversity+novelty acquisition,
  greedy local penalization, barbell explore floor. Result: distinct scaffolds 45→61 (+36%),
  seed-novelty +23%, exploit −8%. Output `phase3_next_batch.csv` → `phase2_build_inputs_tier6.py`.
- **R2 ✅ — feedback substrate fixed.** (a) Rewrote `phase2_score_sigma.py` to scan ALL tier
  outputs (was globbing the empty legacy dir) → `phase2_reliability_ranked.csv` now has **318
  candidates** with σ_iptm. (b) `phase3_build_labels.py` unifies σ_iptm+σ_E, **excludes the failing
  gfn0 family** → `phase3_labels.csv` (298 dual-labeled). gfn0 stays out of future COMBOS.
- **R3 ✅ — surrogate** `phase3_surrogate.py` (Tanimoto-kNN, k=7). **LOO-CV calibrated**:
  iptm_mean ρ=0.56, gate ρ=0.42, σ_E ρ=0.35 (weak → weight σ_E lightly). Wired into the selector
  via `--use-surrogate` (EXPLOIT predicted gate `w_surr=0.5` + EXPLORE QbC disagreement `w_qbc=0.3`).
  Surrogate-on batch: scaffolds +44%, novelty +21%, **predicted-binding +5%**, exploit −7% — better
  on 3/4 axes. The selector now distinguishes truly-cofolded (`visited`, from labels) from staged
  inputs → idempotent.
- **R4 ✅ — Pareto/EHVI** `phase4_pareto.py`. Realized non-dominated front over (iptm↑, σ_E↓) =
  **7 dual-reliable hits** (`phase4_pareto_front.csv`), hypervolume 11.99 (`phase4_hypervolume.txt`,
  the stagnation-alarm scalar), EHVI for 1466 un-cofolded (`phase4_ehvi.csv`, light-weight selection
  input given weak σ_E surrogate). QED/ADMET remain the upstream hard gate, not Pareto axes.
- **R5 ✅ — multi-fidelity ASHA** `phase5_asha_select.py` (η=3) + `CANDS_FILE` subset filter and
  `MODE=ohess`→`--ohess` added to `phase2_xtb_sigma.py`. OHESS targets **40/318 (12%) = 8× heavy
  compute saved**, focused on top-gate ∪ Pareto-front. This is the next σ_E refill mode (non-disruptive).
- **R6 ✅ — generative loop** `phase6_reseed.py` + `sample_mol2mol_r3.toml` + `run_phase6_reseed.sh`.
  Reseeds mol2mol from **39 seeds = 7 Pareto-front + 17 top-gate + 15 original anchors** (≈70/30
  exploit/explore). CPU-only, CUDA hidden, cores 19-23 nice15 (no GPU/exploit-core disruption).
  Output `generated_raw_r3.csv`; merge into the pool is a separate reviewed step (filter_and_rank).
- **R7 ✅ (advisory) — discounted-UCB meta-allocator** `phase7_roi_ledger.py`. Snapshots each arm's
  cumulative output, computes the within-arm-normalized value rate, discounted-UCB index
  (γ=0.9, C=0.5), logs the recommended next-resource arm. Observe-and-recommend only (does NOT yet
  reallocate — the working supervisor stays). CUSUM change-detection + auto-act = the next step.

**What's left (next ticks):** act on R7 (auto-shift cores when an arm's index drops), wire EHVI as a
light selector term, run the ASHA OHESS rung when OPT drains, and review-merge R6's `generated_raw_r3`.

---

## 5. Self-monitored "you're over-exploiting" alarms (wire into the cron tick)

Trip → divert the next batch to explore:
1. **Novelty-coverage stall:** Δ(#distinct scaffolds in the cofolded archive) over 24 h < 1 while
   exploit > 80 % of compute → grinding buys ~zero new chemical space.
2. **Scaffold-entropy decay:** Shannon entropy of the recent-top-50 scaffold distribution drops
   > 15 % over a rolling window → incipient mode collapse.
3. **Marginal-gain < best-unexplored-cell bonus:** median σ-improvement per exploit cycle
   (median-of-means) falls below `β/√(N(best empty cell)+1)` → the cheapest unexplored cell now
   out-values continued grinding (the regret estimate, on the σ scale).

---

## R8 — Sweet-Spot Controller (2026-06-10, second frontier survey)

A 4-axis frontier survey (cost-aware/MF BO · bandit-portfolio · self-driving-lab discovery · VOI/optimal-
stopping) **independently converged on the same diagnosis** of phase7's discounted-UCB advisory:

1. **Wrong objective.** Discounted-UCB minimizes *cumulative regret*; our goal is *top-k identification*.
   These have opposite optima — a regret-minimizer re-samples the confirmed leader Θ(t) times to exploit
   it; a top-k identifier samples it O(log 1/δ) and pours the rest into the contested k/k+1 boundary.
   Estimate: ~30-40 % of compute wasted re-confirming settled tracks. (Successive-Rejects / Sequential-
   Halving / Track-and-Stop are the right family; our ASHA η=3 is the SH special case.)
2. **Cost frozen.** `ROI=E[(V−g)+]/cost` is EI-per-unit-cost with the cost exponent **α≡1** — the exact
   config that *provably fails to beat plain EI when the winners are expensive* (Lee/CArBO 2020). With a
   ~100-1000× cost spread across tracks this **structurally over-funds the cheap σ_E grind and starves the
   expensive Boltz cofold** — the only track that can confirm a best-arm. This is the mechanism behind
   every "explore=0 / GPU idle" incident.
3. **No common currency / no cross-track marginal comparison.** ROI is computed *within* a track; the
   sweet spot is *defined* by equalizing **marginal-VOI-per-cost across tracks** (KKT / water-filling),
   whose common level is the shadow price λ. We never computed λ — "keep cores 80 % busy" targets
   *occupancy*, not value.
4. **No stopping rule.** σ_E grinds to floor. The Weitzman/Pandora reservation value `E[(X−g)+]=c`
   (= Pandora's-Box-Gittins, Xie NeurIPS 2024) gives the exact $-optimal cutoff to hand cores to explore.

**`phase8_sweetspot_controller.py`** implements the fix with quantities we already log:
- **A EXPLOIT** = submodular marginal *coverage* gain of the best remaining (mode,gfn,solvent) σ_E cell /
  cost(mode). `gain = W_mode · 1/(1+n_redundant_in_same(mode,gfn,solvent-class))` → diminishing returns
  are automatic, the track self-throttles (Nemhauser-Wolsey-Fisher 1−1/e greedy on submodular coverage).
- **B ACQUISITION** = batch reservation value `E[(g_max − incumbent)+]`, g_max = extreme value of an N=80
  tier `≈ μ + sd·√(2 ln N)` / cost(cofold). (One-average-draw EI mis-priced this near-zero; the tier finds
  the *best of 80*.)
- **C GENERATION** = IDS-style `novelty_coverage · P(gate_pass) · H(A*)` / cost(gen), H(A*) = normalized
  top-k scaffold entropy → generate iff the winner is still uncertain (Russo-Van Roy IDS; Neu OIDS 2024).
- **cost-cooling α(t)** = clip((TARGET_LABELS − n_lab)/TARGET_LABELS, 0, 1), TARGET=800: α high early (build
  the surrogate cheaply on exploit), α→0 near the decision (fund the expensive cofold). De-starves Boltz.
- **resource-aware water-filling:** GPU is ACQ-exclusive (verdict vs an idle floor); CPU cores split
  EXPLOIT(0-18) | GENERATION(19-23) at the water-line λ = the lower of the two CPU marginal-VOI/cost.
  **over-greed flag** fires when EXPLOIT > (1+tol)·GENERATION-per-core (EXPLOIT hoarding cores).

**First live read (2026-06-10, n_lab=567, α=0.29):** EXPLOIT 0.500 (next cell gfn1_acetonitrile) | ACQ
0.131 (EI 0.18, pool 1217) | GEN 0.094 (H*=0.739, pass 1.0) | GPU→ACQUISITION | CPU water-line 0.094,
co-active [EXPLOIT, GENERATION], no over-greed. → The frontier-correct controller **independently
reproduces the hand-tuned live split** (2-explore GPU + σ_E on 0-18 + generation on 19-23), but now as a
*computed* λ with an α that will auto-tilt toward cofold as labels→800 and an over-greed detector on
EXPLOIT's submodular decay. Advisory daemon `sweetspot_ledger_loop.sh` (cores 19-23, nice 15, 25-min loop,
log `phase8_sweetspot.log`) accumulates the λ/α time series; logs only, never moves cores → 0 compute risk.

## R9 — MAP-Elites illumination archive (optimizer → illuminator)

The survey's **#1 discovery blind spot**: our loop maximizes one scalar (gate_score) and reseeds REINVENT
70/30 from the *global* winners = an OPTIMIZER. For DISCOVERY the object is a MAP-Elites **archive** (each
behavior niche keeps its own champion → a winning chemotype can't empty the other niches). We didn't even
keep the instrument to *detect* collapse. **`phase9_mapelites_archive.py`** builds it:
- niche = (Bemis-Murcko *generic* scaffold, primary ZBG class, MW bucket); elite = max gate_score.
- **First run (567 labels): 174 niches illuminated, top-50 scaffold entropy 0.725 = HEALTHY** (resource-
  level diversity is genuinely good). **But the best-20 niches are 20/20 pool-owned, 0/20 generated** —
  the r3/r4 generated winners are high-scoring yet land in *already-occupied* niches. Concrete proof of the
  "optimizer not illuminator" diagnosis on our own data: generation improves scores *within known
  scaffolds* instead of opening new niche space.
- **Fix = illuminated reseed `seeds_illuminated.smi`** = one elite per niche (174) ∪ Pareto front (5) ∪
  anchors (15) = 194 seeds → the next mol2mol round reseeds from *all niche champions*, pushing the
  generator into unoccupied niche space rather than the single global mode. Replaces phase6's global-top-K.
  **Next generation round (r5+) consumes seeds_illuminated.smi, not phase6 global-winner seeds.**

**Adopted now (pure-CPU, explore cores only):** phase8 controller + advisory daemon; phase9 archive +
collapse instrument + illuminated reseed. **Deferred (needs surrogate/NN):** PBGI reservation-stop as the
cross-track index; DPP batch selection (replace greedy distance penalty); decision-EIG for acquisition;
GFlowNet (A-GFN finetune + ACE) for built-in reward-proportional diversity. Survey full reports in the
2026-06-10 session transcript.

## R10 — Autonomous tier rotation (queue-driven supervisor + phase8-planner; no per-transition human)

The remaining autonomy gap: every resume-skip trap (a tier hits 80/80 → boltz self-exits "all processed"
→ GPU drops to 1-explore) required a human/LLM to EDIT gpu_roi_supervisor.sh and restart it. Closed with
a two-layer design so the exploit/explore sweet spot is allocated continuously WITHOUT my intervention:

* **Mechanical layer — `gpu_roi_supervisor.sh` v4 (queue-driven).** Each slot has `tier_state/slot_{E,F}.
  {current,queue}`. A tier is *trapped* when N_done has stalled at ≥ N_inputs−SKIP_TOL(2) for STALL_POLLS(8)
  ≈ 4 min (distinguishes "finished/self-exiting" from "still computing the last few"). On trap: SIGKILL the
  trapped boltz (no 3-context), pop the next tier off the queue, rotate. Convention tN ↔ denovo_cofold_
  input_tN / denovo_tN_output. SLOT-E 19-23/seed7041, SLOT-F 14-18/seed8107. Deterministic, runs blind,
  guarantees never-idle as long as the queue is non-empty. v3 backed up as gpu_roi_supervisor_v3_backup_*.
* **Intelligent layer — `tier_planner.py` via `tier_autopilot.sh` (10-min loop).** When a slot's queue
  drops below MIN_QUEUE(1) and its current tier is ≥ LEAD_FRAC(0.70) done, build & queue the next tier.
  TYPE chosen by phase8's marginal-VOI/cost: GENERATION if GEN mVOI > ACQ mVOI and an illuminated batch is
  ready (else trigger `run_generation_round.sh` to prepare one, queue ACQ this round to stay busy);
  otherwise ACQUISITION (built instantly from the un-cofolded pool via phase3_acquisition_select +
  phase2_build_inputs_generic = always-available never-idle floor). Lock-guarded, pure CPU 19-23.
* **Generation injection — `run_generation_round.sh` + `filter_and_rank_generic.py`.** The sweet-spot's
  exploration arm, triggered autonomously when phase8 favors GEN: phase9 illuminated reseed (one elite per
  niche, not global winners) → REINVENT mol2mol (CPU, CUDA hidden) → filter/ADMET → pending_gen_manifest.csv
  → planner turns it into a cofold tier. Closes the generative loop with NO human step.
* **LLM layer — the autonomous-loop cron (`<<autonomous-loop>>`, ~25-min).** With routine rotation now
  mechanical, the LLM tick's job narrows to STRATEGY + EXCEPTIONS: verify the stack, score new cofolds
  (phase2→phase3→surrogate retrain), review the phase8 ledger / phase9 collapse metric, force exploration
  if collapse detected, handle OOM/novel situations. "Advanced reasoning without user intervention."

Live since 2026-06-10 10:0x: v4 supervisor (1 instance), tier_autopilot, sweetspot_ledger all running;
seed queues slot_E=[t11] slot_F=[t12] (prebuilt acquisition, scaffold +104%/+126% vs naive); 2-explore
t9+t10 intact, GPU free ~14.8G. First autonomous rotation will be t9→t12 / t10→t11 at their traps.
