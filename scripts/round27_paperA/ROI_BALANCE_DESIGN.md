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

## R11 — Sweet-Spot Controller v2 (2026-06-13, THIRD frontier survey)

Trigger: a live read of `phase8_sweetspot.log` showed the R8 controller **frozen for ~75 min**, every tick
identical (`EXPLOIT 0.500 next=gfn1_acetonitrile | ACQ 0.131 | GEN 0.094`). A four-axis 2024-2026 survey
(bandits/BO · active-learning-for-discovery · compute/budget metareasoning · LLM-agent ROI) independently
converged on **five named defects** of R8 — each maps to something we could SEE in that frozen log — plus
the actuation gap. Fixes shipped in `phase8_sweetspot_controller.py` (still ADVISORY = 0 compute risk):

1. **Cheap-arm cost-normalization degeneracy** (Lee/CArBO 2020, arXiv:2003.10870). R8 divided VOI by
   `cost^alpha`; the cheapest arm has `cost=1` so `1^alpha=1` for *every* alpha — cost-cooling **never
   touches the cheap SP σ_E grind**, which is therefore structurally over-funded and wins permanently
   (exactly the frozen `EXPLOIT 0.500`). **FIX:** shift the cost, `(cost+C0)^alpha`, C0=1 → SP cost 1→2 so
   `2^0.29=1.23` now penalises it (live: SP cell 0.500→0.409). Modern standard is log-cost
   `value − α·ln(cost+c0)` (BoTorch LogEIPC); the shift is its first-order, unit-preserving form.
2. **Pandora-Box-Gittins reservation index** (Xie/Astudillo/Frazier/Bindel, NeurIPS 2024, arXiv:2406.20062).
   A cost-aware index where cost enters as the **RHS of an EI equation** `E[(g−res)+] = λ·cost`, NOT as a
   divisor → a cheap low-value arm gets a *low* index (cannot be inflated by small cost; the EIpu failure
   mode). Computed for the GPU/ACQ arm by bisection on the batch extreme belief `N(g_max, sd_ext)`. **Units
   matter**: g is in gate-score units, cost is wall-time — so `res` is only meaningful when cost is first
   converted to value units by the shadow price, `λ_value·cost(cofold)`. With `λ` from the CPU water-line,
   live PBGI res = 0.78 (> incumbent → GPU box worth opening). `λ` IS our KKT shadow price — PBGI slots
   directly into the water-filling layer (R8 §4 had this DEFERRED; now implemented).
3. **Non-stationary forgetting / saturation decay** (Garivier-Moulines D-UCB / SW-UCB 2011, arXiv:0805.3415).
   R8 had no memory — a drained track kept its index forever (the other half of the frozen log). **FIX:** a
   rolling `phase8_history.json`; if a track's **underlying progress counter** (done σ_E cells / labels /
   distinct scaffolds) is flat across recent ticks, discount its forward VOI by `γ^stall`, γ=0.97 (memory
   ~1/(1−γ)=33 ticks ≈ 14 h). A saturated track now automatically loses the water-line instead of squatting
   on it. (Counter-based, so it forgets *real* stalls, not noise.)
4. **Two-sided hysteresis + dwell** (Balseiro/Lu/Mirrokni dual mirror descent, ICML 2020 / Oper. Res. 2023;
   switched-systems deadband). R8 used a single water-line (`λ_high=λ_low`) → flaps. **FIX:** a deadband
   `λ_high/λ_low = HYST = 1.4` and a dwell rule — the CPU winner only switches when the challenger beats the
   incumbent by `> HYST`. This is not cosmetic: our own logs measured a **~2× floor slowdown** when CREST
   backfill churned the cache ([[feedback_backfill_belongs_on_explore_cores_2026_06_11]]) and a +52% chain
   regression from nice-churn — switching IS costly, so the literature's 1.3-1.5× deadband matches our scar
   tissue exactly.
5. **Value-of-Computation stop** (Russell & Wefald, *Principles of Metareasoning*, AIJ 1991). "busy ≠
   valuable": maximising utilization is a vanity metric; compute more iff `V′(b) > λ`. **FIX:** a `voc_stop`
   verdict — when even the best CPU track and the GPU cofold are both below an absolute floor, the right move
   is **RAISE THE CEILING** (trigger a generation round / open a new MAP-Elites niche), NOT grind a saturated
   σ_E cell to keep cores warm. This is the formal statement of the user's "exploit AND explore, never
   explore=0" mandate ([[feedback_exploit_explore_balance_2026_06_08]]): never-idle means *always on the
   highest-VOC work*, and when all tracks saturate the highest-VOC work is generating new molecules, not
   re-filling cells. Reconciles the never-idle doctrine with the VOC anti-busywork guardrail.

Plus **online cost calibration** (EWMA of measured combo wall-times from the σ_E matrix logs) — but **sanity-
gated**: accepted only if the read is physically monotone `sp ≤ opt ≤ ohess` within bounds, else physics
defaults. (Live: a mixed-run read gave `opt 54 > ohess 40`, correctly rejected — xtb fidelity cost is
intrinsic, not machine-drift, so an unsanitised measurement is worse than the default.)

**State schema** kept backward-compatible (`tracks` still drives `tier_planner`); new fields `tracks_raw`,
`acq_pbgi`, `voc_stop`, `over_greedy`, `all_dead`, `cpu_water_high`, `stalls`, `costs`, `gpu_paused`.

**Convergent frontier ideas NOT yet shipped (DEFERRED, ranked) — paper4 SI roadmap:**
- **Actuation (the real gap).** All four briefs agree R8/R11 is a strong *advisory* but the value is in
  closing advisory→action. The principled actuator = **drift-plus-penalty virtual queues** (Neely 2010) to
  encode the hard rules ("GPU idle < 10 min", "explore ≠ 0") as queue-stability + **dual-mirror-descent λ**
  updated online from realized consumption `μ←max(0, μ−η(ρ−consumed))`, applied through the R11 hysteresis
  band so cores move EXPLOIT↔GENERATION automatically without thrash. **Held for explicit user sign-off**
  (moving running compute = high blast radius; our backfill scar proves wrong moves are costly).
- **Restless-bandit / Whittle index** with sliding-window estimation (SW-Whittle 2025) as the rigorous
  cross-track index (tracks evolve whether funded or not — xtb/Boltz are checkpoint-resumable = textbook
  restless arms).
- **Discounted-Thompson-Sampling master allocator** (Qi 2023) — q posterior samples → argmax-count = the
  box split, no explore knob; supersedes the deterministic water-line.
- **ASHA η=3 async promotion** over σ_E sub-jobs / **weighted facility-location** GPU batches / **DPP**
  diversity (replace greedy local-penalization) — Li MLSys 2020; Kulesza-Taskar 2012.
- **Counterfactual policy audit** (DR/IPS/SNIPS off-policy eval, Dudík 2011) — nightly replay of the ledger
  to check the controller beats greedy & uniform; the empirical self-diagnostic that allocation is good.
- **Elo tournament over heterogeneous work-items** (Google AI co-scientist 2025, arXiv:2502.18864) — a
  single comparable currency across exploit/explore/new-paper bets, seed 1200, cheap single-turn ranking +
  expensive debate only near the decision boundary.

Full four-agent survey (formulas, regret bounds, ~40 citations) in the 2026-06-13 session transcript.

## R12 — Deliverable-value layer + risk/calibration/EIG roadmap (2026-06-13, FOURTH frontier survey)

R11 made the *resource allocator* world-class but a FOURTH survey from four ORTHOGONAL angles (risk-sensitive/safe
allocation · optimizer's-curse/calibration · objective-design/Goodhart · BOED-EIG + attention economics) exposed a
deeper class of defects R8-R11 never touched. Each converged independently; flagship fix shipped, rest is roadmap.

**THE FLAGSHIP DEFECT — we optimize PROXIES, not the deliverable.** R8-R11 all maximize sigma_E cells / CPU% /
gate_score / coverage. But the true objective is `V = sum_papers P(accept) * impact`. Zhuang & Hadfield-Menell
(NeurIPS 2020) PROVE that indefinitely optimizing an incomplete proxy under (i) incomplete incentives (ii) shared
finite resource (iii) diminishing returns drives true value arbitrarily DOWN — **all three hold for us**. Gao-
Schulman-Hilton 2022: the gold-value-vs-proxy curve PEAKS then FALLS. Manheim-Garrabrant 2018: grinding a full
matrix to stay "busy" is textbook extremal+causal Goodhart; CPU% is the canonical causal-Goodhart proxy (high util
correlates with progress only via the confounder "useful jobs running" — our own backfill scar proved raising util
while slowing the primary 2x).

**SHIPPED: `paper_claim_ledger.py`** — the deliverable-value layer ABOVE phase8. Maintains the load-bearing claims of
paper_A/B/4, each with its reviewer KILL-SHOT (from R53-R55 scans), the cheapest DECISIVE artifact that defuses it
(Platt 1964 strong-inference: the experiment that could EXCLUDE the claim, not more confirming volume), evidence-state
derived LIVE from the data, and `MV = impact * p_gain * deadline_mult * cost_mult`, `p_gain = base_headroom*(1-suff)`.
**First live run (2026-06-13) is decisive**: A1 "sigma_E is signal not FP/SCF noise" MV=5.61 (the R55 #1 kill-shot,
near-submission, cheap CPU, decisive 2-arm control NOT YET RUN) vs A2 "ranking survives GBSA->ALPB" MV=0.18 — and
**A2 is exactly what the exploit floor is grinding**. The ledger raises a MISALLOCATION flag: the floor is 30x
below the highest-MV move. This reframes "keep cores busy on sigma_E" into "run the one control that defuses the
paper-killing objection." Allocate next compute to the highest-MV NOT-yet-sufficient load-bearing claim; when a
claim reaches sufficiency (EVPPI~0, ISPOR VOI 2020), set its weight to ~0 and re-solve the portfolio. Advisory; pairs
with phase8 (phase8 picks the RESOURCE, the ledger picks the CLAIM the resource should serve).

**ROADMAP (convergent, ranked; each closes a defect class R8-R11 ignored):**
- **#1 NOW — the 2-arm sigma_E numeric-floor control** (paper_A A1, the ledger's MV-leader, also R55 #1 "compute-now"):
  re-run xtb SP on IDENTICAL pose geometries under varied OMP threads/seeds to bound the FP/SCF numeric floor, then
  report sigma_E MINUS floor. Defuses the single biggest reviewer kill-shot. CPU-only, runs on 19-23 without touching
  the floor. (Regressional-Goodhart fix = the control group; Platt decisive experiment.)
- **RISK/SAFETY (OOM = hard rule #1): a chance-constrained VRAM gate.** `free_safe = torch_free - Delta_bias -
  kappa*sd_peak - margin` with Cantelli `kappa=sqrt((1-delta)/delta)` (distribution-free) and `Delta_bias` = the
  measured nvidia-smi-vs-torch gap (our WSL2 artifact, budgeted explicitly). Safe-SET filter: 2-explore drops off the
  action menu when its empirical-Bernstein UCB-peak crosses `free_safe` -> formal trigger for 1-explore retreat. A
  Neely drift-plus-penalty SAFETY QUEUE replaces the static VRAM multiplier (self-tunes, O(1/V) optimality). A pre-
  decision SHIELD vetoes any launch whose worst-case peak breaches the ceiling; a residual check refuses to act on
  nvidia-smi alone. (Nemirovski-Shapiro 2006; SafeOpt Sui 2015; Neely 2010; Alshiekh 2018.)
- **OPTIMIZER'S CURSE / pessimism (our argmax-of-noisy gate_score is upward-biased; R55 "sigma is an UPPER BOUND"
  MAXIMIZES the curse):** rank candidates by the CONFORMAL LOWER bound (we already have a split-conformal layer), not
  the point estimate (Rashidinejad 2021 pessimism is minimax-optimal when you ACT on the selection). Tweedie/James-
  Stein shrinkage `mu_hat = mu + tau^2/(tau^2+sigma_i^2)(v_i-mu)` debiases before promotion (Smith-Winkler 2006,
  Efron 2011). Data-SPLIT replicate seeds (select on half, confirm on the other) for an assumption-free unbiased
  value. Conformal selection (Jin-Candes 2023) to size the promoted top-k at a target FDR. CRPS+PIT monitoring: when
  surrogate CRPS ~ prior CRPS / PIT flat -> sigma is pure noise -> shrink fully to prior, halt differential spend.
- **EIG REFRAME (value = bits toward a CLAIM, not generic samples):** score a cofold by EPIG toward a ranking-claim
  (Bickford-Smith 2023) or Box-Hill discrimination for the signal-vs-noise hypothesis; EVPI ceiling per claim; cheap
  PCE/ACE lower bounds, not nested-MC (Foster 2019/2020). Composite priority `EIG_claim * v(deadline) / cost` = WSPT
  (Smith 1956) with EDD override for hard deadlines (Moore-Hodgson) — this unifies the ledger MV with scheduling.
- **ATTENTION ECONOMICS (the user's attention is the scarcest resource):** ping iff `VOI_alert = P(action changes
  outcome)*dU - Cost_interrupt(state) - P(false)*Cost_credibility > tau(state)`, with bounded deferral to breakpoints
  and tau raised overnight/focus (Horvitz 1999 attention-sensitive alerting; bounded deferral) — formalizes "one ping
  per state, not per tick" and the HEALTHY/INCIDENT/OVERNIGHT regimes the watcher already uses.

Full four-agent survey (formulas, ~50 citations) in the 2026-06-13 session transcript (second batch).

### R12 EXECUTED (2026-06-13, GPU-paused window)

Two ledger-driven decisive artifacts shipped on CPU while GPU is paused (video work):

1. **A1 — sigma_E noise-floor control, CLOSED at full library.** `explore_denovo_mmp1/phase_sigmaE_noisefloor_control.py`
   (2-arm: OMP=1 det repeats + OMP{2,4,8} thread-floor vs cross-pose signal), extended to the entire
   eligible de novo library **n=244** (NSHARD sharding on cores 19-23, floor 0-18 untouched). Result:
   signal/floor ratio **median 69.8M×, min 2.6M×, 0/244 below threshold** -> "sigma_E is FP noise" AND
   "n=15 cherry-pick" both dead. Ledger probe `noise_floor_control_present()` fixed to match the real
   filename + require an "is DEFUSED" verdict; A1 suff 0.12->0.90.

2. **B1 — optimizer's-curse / selection-bias defense.** `phase_optimizers_curse_lcb.py` on the EXISTING
   sigma_iptm replicate data (15 ligands x n=161 cofold cycles; no GPU). Three independent tests:
   (1) LCB ranking — CHEMBL259829 stays #1 by its 95% LOWER bound, strict (outlier.lcb 0.0543 >
   runner-up.ucb 0.0183, margin +0.036); (2) James-Stein EB shrinkage — survives, still #1; (3) data-split
   cross-fit (Smith-Winkler 2006) — selected==held-out argmax in all 3 splits, realized curse bias ~1% of
   the held-out lead. **VERDICT: DEFUSED.** Whole 15-ligand ranking is identical under naive/LCB/JS.
   Refs: Smith & Winkler 2006; Efron-Morris 1977 (James-Stein); Efron 2011 (Tweedie).

Post-R12 ledger ranking: #1 P1 de novo dual-gating MV 0.943 (GPU, PARKED by user video-work pause),
A1 0.637 (closed), B1 0.420 (now CPU-defended), A2 0.184 (saturated, do-not-grind). With GPU parked and
A2 saturated, no multi-hour high-MV CPU work remains; remaining CPU items are fast analyses (P2 coverage).
Still DEFERRED (need sign-off): risk chance-constrained VRAM gate, EIG reframe, attention-ping policy,
full auto-actuator (drift-plus-penalty + dual-mirror lambda for 0-18<->GEN core moves).

## R13 — Portfolio / correlated-failure layer (2026-06-19, FIFTH frontier survey)

Five orthogonal 2024-2026 scouts (bandits/pure-exploration · autonomous-labs/AI-scientist · molecular
active-learning/QD · portfolio/risk/decision-theory · compute-scheduling) **independently converged on one
defect R8-R12 never touched**: `paper_claim_ledger.py` ranks each claim by its MARGINAL, INDEPENDENT MV and
SUMS them — there is **no bet×bet COVARIANCE / co-adoption model**. But the entire diversify-vs-concentrate
decision (the greed/explore sweet spot at the DELIVERABLE level) is a function of the CORRELATION structure,
not the marginal values (Markowitz 1952; CVaR coherence Rockafellar-Uryasev 2000; risk-parity 2010;
Wasserstein-DRO≡shrinkage Blanchet-Chen-Zhou MgmtSci 2022; megafund needs ~independence Fagnan-Lo AER 2013).

Our bets are heavily correlated and the ledger was blind to it: **A1,A2,B1,B2,P1 all rest on the shared
premise "σ (xtb/Boltz) is a meaningful reliability signal"** — one reviewer kill-shot on σ-credibility fails
~5 claims at once; de novo P1,P2 share the indolinone-sulfonamide scaffold + the single MMP-1 target.

**SHIPPED: `phase10_portfolio_risk.py`** (R13, advisory, pure-CPU, reads `paper_claim_ledger_state.json`):
- structural factor-loading model (8 factors: sigma_infra, forcefield_xtb, boltz_cofold, mmp1_target,
  scaffold_indolinone, solvation_model, lit_audit, mapelites_diversity), editable literal like CLAIMS.
- C = cosine-correlation of loading vectors, light-shrunk toward I (SHRINK=0.15; N tiny).
- **N_eff = (ΣMV)² / (MVᵀ C MV)** = effective number of INDEPENDENT bets (diversification ratio;
  =Herfindahl when C=I, →1 when all correlated). PRIMARY concentration trigger (the theoretically-correct
  scalar); per-factor MV-share only EXPLAINS where the concentration comes from.
- per-factor systemic-risk share, risk-adjusted V_adj = ΣMV − γ·√(MVᵀCMV), and a diversify-vs-concentrate
  verdict with the highest-MV ORTHOGONAL hedge (advance top-MV AND an off-cluster bet, don't pile on).
- lightweight discovery-EFFICIENCY meter (AF/EF spirit, MADE arXiv:2601.20996): dual-reliable Pareto hits
  per cofold = paper4 autonomous-efficiency number (currently unmeasured).

**First live read (2026-06-19, 7 bets):** **N_eff=1.68 of 7** (uncorrelated-Herfindahl 3.89 → correlated
drag −2.2 effective bets = "illusory diversification"); systemic shares sigma_infra 35% + boltz_cofold 18%
+ forcefield_xtb 17% = **70% σ-machinery**; V_naive 2.444 → V_risk_adj 1.502. **Verdict HEDGE**: top-MV P1
loads 58% on sigma_infra → risk-adjusted best move = advance P1 AND the orthogonal P2 (off the σ cluster) to
cut correlated-failure risk. Wired into `sweetspot_ledger_loop.sh` (phase8 → claim_ledger → phase10 each
25-min tick; advisory, 0 compute risk).

**Actionable implication for the papers:** the single highest-leverage RISK reduction is an **orthogonal,
non-σ-dependent claim** — the R53/R54 CA-selectivity axis (sulfamoyl=ZBG; CA sub-nM precedent) is the
natural hedge: it does NOT load on sigma_infra, so it raises N_eff materially.

**Convergent frontier ideas NOT yet shipped (DEFERRED, ranked) — R13 addendum:**
- **DyRAMO applicability-domain reward gate on REINVENT** (Hirono Nat Commun 2025, s41467-025-57582-3):
  reward=0 if a generated mol's max-Tanimoto-similarity to the ADMET/σ surrogate training set < ρ
  (BO-tuned). Stops surrogate-Goodharting via extrapolation — THE pure-in-silico failure mode. Explore-side,
  CPU, safe to add as a generation filter. **Highest-leverage explore-side upgrade.**
- **Validated LF↔HF correlation gate before cascade promotion** (Sabanza-Gil Nat Comput Sci 2025,
  s43588-025-00822-9): measure Spearman(cheap ADMET/σ-surrogate, Boltz σ_iptm) on a held-out set; promote
  to Boltz only if correlation high AND Boltz ≥10× costlier — else multi-fidelity HURTS. Currently we
  promote by cascade order, never validated. CPU diagnostic, safe.
- **Information-Directed Top-Two as the EXPLORE selector** (Qin-You arXiv:2310.19319; fluid-β Bandyopadhyay
  NeurIPS 2024): identification-optimal "which to probe next" — PBGI is reservation/exploit-side, we lack an
  identification-optimal explorer. Closes the β-optimality constant-factor gap to exact, no hyperparameter.
- **σ-CI relative-precision stop for the REPLICATE tier** (heavy-tail-robust bootstrap, not chi-square):
  replace the fixed 20-candidate cursor slice with a per-cell sequential stop when the σ confidence-interval
  relative half-width ≤ target (~30 reps for ±25%). Directly publishable reproducibility-budget methodology;
  OCBA selects means, it does NOT size σ. CPU, safe.
- **ACTUATION (the standing deferred gap, needs user sign-off):** PID-Lagrange drift-plus-penalty + a VRAM
  VIRTUAL QUEUE (An IET GTD 2025) replacing the static VRAM multiplier and the static 0-18/19-23 split;
  driven by a learned restless/Whittle index (GINO-Q arXiv:2408.09882 / SW-Whittle arXiv:2506.18186) that
  captures EXPLOIT's value-decay-on-exhaustion vs EXPLORE's value-rise-on-idle. Literature is unanimous that
  a static split is provably suboptimal (non-convex, condition-dependent Pareto front, Shukor 2024/Lu 2025),
  but re-partition ONLY at job boundaries, ONE core at a time, with dwell — our measured 1.3-2× cache-churn
  penalty bounds the gain. **HELD for explicit sign-off (moving running compute = high blast radius).**

Full five-agent survey (formulas, ~60 citations) in the 2026-06-19 session transcript.

### R13-⑤ ACTUATION SHIPPED + ARMED (SAFE tier) — 2026-06-19

The standing deferred actuation gap is closed with `phase15_actuator.py` (the only piece that moves running
compute -> built SHADOW-by-default, two risk tiers, hard guards). User sign-off 2026-06-19 ("남은 것 진행").

- **Formalism:** PID-Lagrange λ (Kp/Ki/Kd) + idle-core & VRAM virtual queues (Neely 2010; An IET GTD 2025).
- **SAFE tier (ARMED):** GPU PAUSED + explore-idle (boltz=0, no gen round, no pending manifest) => the σ FLOOR
  reclaims the otherwise-idle cores 19-23 (FLOOR=0-23); ANY explore activity or GPU-active => instant yield
  back to FLOOR=0-18. CPU-only (cannot OOM), cannot starve explore (it isn't running), resumable, and never
  migrates a running process — only NEW xtb cells pick up the range at a job boundary. This is the never-idle
  reclaim of wasted pause-time cores, the OPPOSITE of the risky floor-shrink direction.
- **AGGRESSIVE tier (SHADOW unless `ACTUATION_ARMED_AGGRESSIVE`):** continuous floor<->explore shrink during
  GPU-active driven by the phase8-VOI PID λ — the cache-churn-scar direction; recommendation logged only.
- **Guards:** floor ≥ 12 cores; dwell 1800s; step ±1 (full jump only on a pause<->active regime change);
  VRAM<6GB (driver-confirmed) never shrinks floor below 0-18.
- **Mechanism:** writes `tier_state/core_split.active` (FLOOR=0-N EXPLORE=…); `floor_sigma_feeder.sh`
  `floor_cores()` reads it per cell (job boundary), default 0-18 (fully backward-compatible). **Consumer-side
  belt-and-suspenders:** when GPU is NOT paused and AGGRESSIVE is not armed, `floor_cores()` forces 0-18
  regardless of the file -> on GPU resume the floor reverts to 0-18 with zero actuator-lag race (no manual rm).
- **Live (2026-06-19, GPU paused, a generation round running on 19-23):** active=FLOOR=0-18 = current default
  = safe no-op; the floor will auto-reclaim 0-23 the moment that gen round finishes while still paused. Wired
  into `sweetspot_ledger_loop.sh` as the 8th advisory layer (phase8→ledger→10→11→12→13→14→15).
- **Still deferred:** arming the AGGRESSIVE tier (dynamic shrink during GPU-active, after more shadow
  observation) + a learned restless/Whittle index (GINO-Q arXiv:2408.09882 / SW-Whittle arXiv:2506.18186)
  to generalize the 2-state regime to a continuous VOI-driven split.

## R14 — Deliverable axis (objective fix) + first SAFE compute actuation (2026-07-18, brain-vs-body audit)

Trigger: a user request to make the exploit/explore balance world-class. A three-agent line-level audit of
the RUNNING system found the failure is **not the theory** (R1-R13 is frontier-grade) but a **brain-vs-body
split**: the whole advisory stack (ledger + phase8 λ/PBGI/cost-cooling/hysteresis + phase10 N_eff + phase15
PID + roi_allocator) computes every tick and writes logs, yet the *actual* allocation is a **static** hand-tuned
0-18/19-23 partition + queue rotation. The entire live influence of the stack on what runs is `tier_planner`'s
narrow GEN-vs-ACQ tie-break. `roi_allocator.py` is orphaned (log froze 2026-06-09); `phase10_state` has zero
readers; `core_split.recommended` has zero readers; phase15 AGGRESSIVE is unarmed; the floor grinds the σ_E
grid **unconditionally, reading no value signal** (confirmed: `floor_sigma_feeder.sh` while-true, MISALLOC_ACK
accepting a floor on MV 0.049 while A1 leads at 0.637). *Five frontier surveys of allocation theory that never
reached the wheel* — itself the Goodhart failure the ledger was built to prevent (optimize the machinery proxy,
not the deliverable).

**THE ROOT DEFECT (deeper than any R8-R13 touched): the objective was wrong.** The ledger equated
*compute-artifact-computed* with *value-realized* and had NO manuscript/publication term, so it forever
recommended MORE COMPUTE for results that are compute-done and stuck in write-up — exactly the standing
bottleneck (memory: 병목=원고, 컴퓨트 아님). The true objective is `V = Σ P(**published**)·impact`, and value is
realized only when a result is (i) COMPUTED **and** (ii) WRITTEN **and** (iii) SUBMITTED.

**SHIPPED (`paper_claim_ledger.py` R14, advisory):** a DELIVERABLE axis. Only three actions raise V —
COMPUTE (iff the decisive artifact has NOT run; sufficiency≥0.80 ⇒ artifact ran ⇒ COMPUTE MV=0, killing the
stale "grind a settled claim" recommendation), WRITEUP (iff computed but not in its manuscript — trapped value,
`× WRITEUP_PREMIUM`; written-fraction probed by signature-grep of the actual .md files), SUBMIT (author). All
actions rank on one MV scale; a `floor_should_idle` verdict fires when the best COMPUTE action < the Russell-
Wefald value-of-computation floor (VOC_FLOOR=0.12). New claim A4 registers this session's real-panel σ_E result
(the evidence→claim loop the static CLAIMS list lacked). **First live read: every decisive artifact has run
(all COMPUTE MV=0) → NEXT ACTION = WRITEUP, [VOC-STOP] "the floor is grinding make-work; idle it; the binding
constraint is WRITE-UP/SUBMISSION" — matching phase8's own all-arms-saturated read.**

**SHIPPED + LIVE (`floor_sigma_feeder.sh`, user-approved SAFE actuation 2026-07-18):** the floor now reads
`floor_should_idle` at its job boundary and, when compute is saturated **and** the GPU is truly idle (boltz=0,
so no new cofolds to SP-gate), **idles instead of grinding make-work**; auto-resumes the instant real work
appears. This is the first advisory→actuation closure beyond phase15-SAFE. It only STOPS compute (never moves a
core ⇒ cannot OOM or cache-thrash — the scarred direction stays deferred), fail-safes to GRIND on any ambiguity
(stale/missing ledger, any boltz alive), and is reversible instantly with `touch tier_state/FLOOR_VOC_STOP_DISABLED`.
Watcher-compatible with no change: the feeder-dead trip keys on the floor PROCESS being alive (`fd`), not on
xtb worker count, so an intentionally-idle-but-alive floor never false-trips.

**Still deferred (unchanged, needs sign-off):** the AGGRESSIVE dynamic core-split (moves running cores; 1.3-2×
cache-churn scar). **Next R14 ticks (advisory→wire):** (a) auto-retire ledger claims from the voided narrative
(A3 surfaced as top-WRITEUP is a stale remnant of the void repositioning story — the claim SET needs the same
evidence-coupling the values now have); (b) tune WRITEUP deadline-weighting (a low-impact near-deadline claim
can out-rank a higher-impact one); (c) let the LLM tick consume `best_action`/`floor_should_idle` directly so
the highest-value move (currently WRITEUP paper_C) is surfaced every cycle, not just logged.
