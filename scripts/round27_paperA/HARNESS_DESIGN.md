# R15 — the Opportunity Harness (2026-08-08)

Explore in hypothesis space, commit to one pursuit at a time, and finish it. This is the layer that R8-R14
does not contain, plus the two liveness holes that made the existing stack fail silently.

## 1. Diagnosis

R8-R14 built a genuinely strong advisory brain: phase8 (marginal VOI per core, VOC-stop, over-greed),
paper_claim_ledger R12/R14 (V = sum P(published) x impact, COMPUTE/WRITEUP on one scale), phase10
(portfolio/correlated failure), phase11-14 (applicability domain, LF-HF gate, information-directed
top-two, replicate CI stop), phase15 (core actuator, shadow-by-default), and tier_planner as the one place
theory reaches the GPU.

Measured against the three properties this system is supposed to have, it scored two out of three badly.

**Exploration was confined to molecule space.** phase13/IDS answers "which candidate to cofold next".
Nothing answers "what else is in the data". The claim set is a hardcoded Python literal in
`paper_claim_ledger.build_claims()`, and the A4 entry says so in its own comment: "NEW claim, spawned by a
result (the evidence->claim loop the static list lacked)". That loop was a human in a conversation. With
nobody attached, the rate of new hypotheses was exactly zero regardless of how much compute burned, while
12,207 labelled rows sat unexamined.

**Greed had no object to attach to.** Every layer re-decides from scratch on a timer: tier_planner every
600s, the ledger loop every 1500s. There is no representation of "a line of inquiry currently being
pursued", so a signal noticed at 03:00 is simply gone at 03:10. The one place depth existed (REPLICATE) was
bounded by a sample cap, not by information.

**Two daemons had no liveness trip, and one of the gaps was self-concealing.** Of six daemons, the watcher
covered four. `tier_autopilot` and `sweetspot_ledger_loop` had none. Worse, the EVIDENCE-STALE trip was
gated on `sweet_running`, so the death of the aggregator loop also switched off the detector for the
staleness that its death causes. Every resume note since 2026-07-15 compensated for this by hand
("verify by mtime, not by liveness").

## 2. What was built

    harness/harness_scan.py     probes -> Observations (effect + 95% CI + n + provenance + recompute cmd)
    harness/harness_ledger.py   registry, triage to OV, arbiter, commitment lock, pursuit stepping, findings
    harness_loop.sh             daemon: scan hourly, one pursuit step per 15 min, heartbeat
    autonomous_watcher.sh       + aggregator/autopilot liveness, harness heartbeat, promotion trip
    roi_report.sh               + OPPORTUNITY HARNESS section

State lives under `tier_state/harness/`: `scan_latest.json`, `registry.json`, `allocation.json`,
`harness_state.json`, `PURSUIT.active`, `PROMOTION_PENDING`, `findings/finding_<key>.md`, `heartbeat`.

### The loop it closes

    evidence -> observation -> triaged opportunity -> committed pursuit -> confirmed finding
             -> LLM promotion -> claim ledger -> tier_planner -> GPU

Only the promotion arrow is human. Everything else runs unattended.

## 3. One value scale

An opportunity's value is expressed in the same units as a claim's MV, so explore-vs-exploit is a
comparison rather than a preference:

    OV = impact_prior(probe) x headroom_prior x P_real x novelty

`P_real` is an explicit product of visible discounts (FDR q, effect size, cross-scan stability, mechanism
flags), documented as a prior and not as a calibrated probability. `novelty` discounts territory an
existing claim already owns. `COMMIT_FLOOR` is set to the claim ledger's own `VOC_FLOOR = 0.12` — the same
number, deliberately, so the two layers cannot drift apart.

The arbiter reads `best_compute_mv` straight from `paper_claim_ledger_state.json` and sets

    explore_share = clamp(V_explore / (V_explore + V_exploit), 0.10, 0.40)

Both clamps are load-bearing. The floor is insurance against the 2026-07-15 collapse, when 685 of 733
tiers went to a settled claim because nothing forced a minimum of exploration. The ceiling guarantees the
exploit floor keeps the majority of the machine no matter how exciting a scan looks.

## 4. Greed, and its four stopping rules

At most one opportunity is COMMITTED at a time. A committed pursuit writes `PURSUIT.active` and runs an
ordered plan of confirmation steps, one step per daemon tick, until it concludes. Routine rotation cannot
preempt it; that is the mechanism that makes follow-through structural rather than a matter of attention.

It ends when, and only when, one of these fires:

    PRECISION  the CI half-width reaches the target -> the question is answered, either way
    FUTILITY   the permuted null is not excluded -> refuted, recorded with its empirical p
    BUDGET     spend exceeds 4 core-hours -> stop, record what that budget bought
    VOC        expected remaining gain per core-hour falls below the shared VOC_FLOOR

A negative outcome is an output. CONCLUDED_BOUND and CONCLUDED_REFUTED are written up with numbers, never
as "nothing found", following the standing rule that negative results are reported as bounds.

Three consecutive step errors ABORT the pursuit and release the lock, so a broken pursuit cannot wedge the
harness.

### The confirmation plan is this project's own evidence standard

The steps are not generic statistics. They are the checks the 2026-07-17/18 discrimination result had to
pass before it was believed: held-out replication, a permuted null, a partial correlation against the
size/allocation confound, and leave-one-era-out stability. Encoding the standard in code is what stops it
from being lowered at 04:00 when nobody is watching.

## 5. Honesty guards (the hard part, not the statistics)

At n=12,207 a Spearman rho of 0.03 has p<0.001, so significance carries almost no information and an
unfiltered sweep is a fabrication machine. Four guards:

1. **Effect floor, not p.** `|rho| >= 0.15` is the admission test; the p-value only breaks ties.
2. **One FDR pass over the whole family**, with `n_tests` recorded on every observation so the
   multiplicity travels downstream instead of being laundered away.
3. **Derived-pair mask.** `gate_score = iptm_mean * (1 - min(sigma_iptm/0.10, 1)) * qed` is an identity,
   not a finding. Same for `composite_score` vs `qed`.
4. **Coverage and cohort tagging.** `qed` / `composite_score` / `zbg` exist for 1,784 of 12,207 rows, so
   any pair involving them is a library result and is tagged `library_only`; below 5% joint coverage the
   test is not run at all. This is the "a join silently collapsing to an empty intersection" rule enforced
   in code rather than remembered.

Statements are descriptive only. The scanner never writes an interpretation or a causal reading; that is
the promotion step's job.

## 6. Two defects found while building it, both kept as comments in the code

**The scanner discovered its own scheduler.** The first ledger run ranked six allocation-variable relations
at the top, headed by "Spearman(iptm_mean, n_iptm) is heterogeneous across 23 generation eras, I^2=0.94".
That is not chemistry. `n_iptm` is assigned by `tier_planner.replicate_priority()` ordering on gate_score,
and `n_sigmaE_cells` by the floor's score-based survivor screen, so both are functions of the very
variables they were being correlated against, and the 23-era heterogeneity is our own policy changing
(phase14's gate began binding 2026-07-26, the 64-sample cap landed 07-27). Fix: a variable the system sets
by policy can never be an endpoint. `NEVER_ENDPOINT` removes them from every probe family; they remain as
covariates in the confound step, which is the only role they can honestly play.

**A confirmation step must test the statistic, not the variables.** The first plan was generic
(split-half / permutation / partial / jackknife) and produced a wrong verdict on its first pursuit: for a
drift observation ("the relation is heterogeneous across eras"), leave-one-era-out returned PASS meaning
"stable" — evidence against the observation — and the generic logic counted it as support. The same run
printed "retains 115% of the raw |rho|" because it compared a partial correlation against a heterogeneity
span. Fix: each probe declares its own statistic and its own null-defining label, and holdout /
permutation / confound are written in terms of those. Drift permutes era labels, hetero permutes cohort
labels, pair permutes the second variable.

A third, smaller one: re-ingesting the same scan extended each key's effect history, so running the ledger
five times against one scan drove stability from the 0.7 prior to a fully-earned 1.0 — confidence
manufactured by looping. Ingest is now idempotent per scan timestamp, not per call.

**A mask that keys on a name cannot see an alias** (found the same day, by the harness's own first
CONCLUDED_POSITIVE — see section 7b). Every guard above matches literal column names, so a variable that is
a deterministic function of other columns walks straight past all of them. `step_mediation` closes this
generally: before any pair-family observation can conclude, both sides are residualized on the ingredients
and co-moments of whichever side has them, and the plan runs it FIRST so an alias is caught before the
budget is spent. Two declarations drive it, and adding a column means adding it here:

    DERIVED_OF    = {"gate_score": ("iptm_mean", "sigma_iptm", "qed")}   # deterministic parentage
    MOMENT_FAMILY = [("iptm_mean", "sigma_iptm", "kurt_iptm")]           # moments of one sample

`novelty_of` uses the same parentage: a pair inherits the coverage discount of any (parent, other) pair a
claim already owns, so an alias can no longer collect full novelty under a different name.

The conclusion splits on the admission floor rather than collapsing to one verdict. Below `RHO_MIN` the
observation is `CONCLUDED_ALIAS` — real, but belonging to the parents. Above it, most of the effect is
carried by the ingredients and what remains is written as a numeric bound on the variable's own
contribution, because "adds nothing" would overclaim the negative exactly as badly as the original
overclaimed the positive.

## 7. First live result

The corrected harness immediately did the thing it exists for, unattended. Observation: the
iptm_mean/sigma_E_med relation is heterogeneous across 23 generation eras (I^2 = 0.857). It passed the
held-out split (0.851 / 0.851) and passed the permuted-era null (p = 0.0025), then collapsed to I^2 =
0.000 once n_iptm and n_sigmaE_cells were residualized out. Conclusion: CONCLUDED_BOUND, "the effect
attributable to chemistry rather than to sampling policy is bounded at 0.000", written to
`findings/finding_fee8d64a3f7e6a28.md` with its recompute command. Total spend: 0.1 core-minutes.

That is the same class of trap a human caught by hand earlier the same day. The mechanism now catches it
without one.

## 7b. The first CONCLUDED_POSITIVE was wrong, and that is what the promotion gate is for

Hours after deployment the new PROMOTION_PENDING trip fired on its first candidate: "Spearman(gate_score,
sigma_E_med) = -0.537 [-0.552, -0.522], n=10300", passing all four confirmation steps including the
allocation control (73% retained) and leave-one-era-out.

It does not survive contact with `phase2_score_sigma.py:76`, `qed = float(m.get("qed", 0.5) or 0.5)`. In
`generated_auto`, qed coverage is exactly 0.0000, so every row takes the constant and `gate_score` reduces
to a function of two other columns in the same table — reconstructible from them at Spearman +0.999995,
max abs difference 0.00031. Held against both parents the statistic goes -0.537 -> +0.064: below the
admission floor and sign-flipped. What the harness had found was
`Spearman(sigma_iptm, sigma_E_med) = +0.531`, which is claimed territory (A4/P1) carrying a novelty
discount the alias had walked around.

The same reading killed the sibling queued behind it. `iptm_mean x sigma_E_med = -0.502` is not derived
from anything, but mean and standard deviation of one bounded sample are mechanically coupled: holding
sigma_iptm drops it to -0.130. Hence `MOMENT_FAMILY` alongside `DERIVED_OF` — parentage alone would have
caught the first and passed the second.

Re-adjudicating the whole pair family under the guard turned 1 POSITIVE and 2 BOUND into 0 POSITIVE, 8
CONCLUDED_ALIAS and 10 CONCLUDED_BOUND. Nothing in the fixed registry currently clears the bar.

Two things this cost, both worth stating plainly. The harness spent four confirmation steps on a
restatement, which is exactly the waste `NEVER_ENDPOINT` was supposed to have ended one defect earlier. And
the promotion gate is load-bearing rather than ceremonial: had CONCLUDED_POSITIVE auto-promoted into
`paper_claim_ledger.py`, a renamed copy of an existing claim would now be sitting in the ledger inflating
its own portfolio value. Promotion stays a read-the-note decision.

One robustness bug surfaced while repairing the registry by hand: a pursuit entry missing `steps` or
`spend_s` raised a KeyError inside the step driver, and because the daemon redirects to /dev/null the
registry then never persisted and the same pursuit was re-committed every tick without ever stepping.
Both accesses are `setdefault` now. A daemon that swallows its own stack trace needs its state reads to be
total.

## 8. Actuation scope, and how to stop it

Narrow, and it follows the R11 precedent approved 2026-06-13: raise the ceiling, never move the floor.

The harness writes state files, runs its own analysis on the EXPLORE cores (read from
`tier_state/core_split.active`, so it composes with phase15 rather than fighting it), and sets
`PROMOTION_PENDING` to wake the LLM when a pursuit concludes positive. It never kills a process, never
queues GPU work, never touches the exploit floor, and never writes to an existing CSV.

    touch tier_state/harness/HARNESS_OFF     # stop all harness action; the watcher trip is gated on this
    bash harness_loop.sh                     # relaunch; MUST be `bash <name>.sh`, never ./ or a full path

`explore_share` in `allocation.json` is currently a published recommendation, not an enforced split. Making
it enforced would mean moving cores, which is phase15's job and a separate, reviewed step.

## 9. New watcher trips

    sweetspot_ledger_loop count != 1   the aggregators are down; every ROI layer freezes on a stale snapshot
    tier_autopilot count != 1          no queue refill; both slots drain at the end of their current tiers
    harness heartbeat > 45 min         the explore arm stopped or a pursuit is frozen mid-plan
    PROMOTION_PENDING present          a pursuit passed every step and is waiting to become a claim

EVIDENCE-STALE is no longer gated on the aggregator being alive. Staleness is excused only during a full
stop, meaning `GPU_PAUSED` is set and the loop is deliberately down.
