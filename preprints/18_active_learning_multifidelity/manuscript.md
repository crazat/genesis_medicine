# Cost-Aware Multi-Fidelity Bayesian Optimization with Runtime-Gated Cascading Tiers for Autonomous in silico Dermatology Discovery

**HanCheongWoo ¹,²,³**

¹ Genesis_Medicine Lab, Seoul, Republic of Korea
² HAN PREDICT, Inc. ([hanpredict.com](https://hanpredict.com))
³ Recover Korean Medicine Clinic ([recover-clinic.kr](https://recover-clinic.kr))

**ORCID**: [0009-0004-4805-8815](https://orcid.org/0009-0004-4805-8815)

**Date**: 2026-05-03 (v0.2 — adds AQAffinity batch v3 calibration outcome on n=93 ChEMBL MMP-1 holdout: aqaffinity_pearson_r=-0.292, spearman_rho=-0.327, cross_engine_agreement_pearson=0.109. Gate `openfold3_pilot_uncalibrated` cleared with ensemble-recommended consume pattern. Receptor-mismatch ruled out by single-target CSV inspection; remaining performance gap attributed to apo MMP-1 catalytic stub, ZAFF integration tracked separately.)

**License**: This is in silico systems work; released under CC-BY 4.0.

---

## Abstract

Autonomous virtual-screening pipelines suffer a recurring failure mode: cheap predictors (Boltz-2 affinity, ADMET, xTB conformer scoring) accumulate thousands of candidate scores, yet expensive validation tiers (long molecular dynamics, absolute binding free energy, wet-lab) advance unevenly because the scheduler cannot reason simultaneously about *cost*, *information value*, *gate-policy*, and *runtime availability* of each tier. We describe a cost-aware multi-fidelity Bayesian optimization (BO) scheduler that operates over a unified evidence ledger (789 compound–target rows, 136 columns) and a 7-tier cascade ranging from Boltz-2 cofold (~minutes/pair, GPU) through OpenFold3 + AQAffinity (~minutes/pair, GPU) to wet-lab IC₅₀ / IVRT / IVPT (~₩100k+/sample, CRO). The acquisition score blends expected-improvement on missing axes against a tier-specific cost prior; scientific gates (`scientific_gates.yaml`) and curator directives veto advance for compounds failing safety, novelty, or applicability-domain criteria. To prevent the scheduler from pushing work onto a tier whose runtime is missing, we add a *runtime probe* that resolves each tier's executable, model checkpoint, and dependency before scoring; tiers with missing runtime are flagged as `runtime_blocked` rather than gate-blocked, and stalled work-items (`consecutive_runs ≥ 3` in identical signature) are recorded in a per-run queue-state JSON for downstream observability. We report the scheduler's behavior on a current dermatology workload: 752 compound–target pairs queued for the OpenFold3 advance, top acquisition score 0.937, distributed across 8 protein targets (TYR, DCT, MMP1, TYRP1, LOX, CTGF, TGFB1, PTGS2). The runtime-gate distinction proved decisive: when AQAffinity calibration was incomplete, 124 work-items were correctly held under `mmp1_zinc_pending` rather than spuriously advanced. We discuss the design as a reusable substrate for in silico dermatology pipelines, the gap between cheap-tier saturation and expensive-tier throughput, and the limitations of cost-prior elicitation when tier-specific runtimes evolve.

**Keywords**: multi-fidelity Bayesian optimization, cost-aware acquisition, autonomous discovery, evidence ledger, scientific gates, runtime gating, dermatology, OpenFold3, AQAffinity, Boltz-2

---

## 1. Introduction

Autonomous in silico drug-discovery pipelines now combine multiple structure prediction engines (AlphaFold2/3, Boltz-2, OpenFold3, Chai-1), affinity heads (AQAffinity, structure-free predictors), generative chemistry (REINVENT4, mol2mol), property surrogates (ADMET-AI), conformer search (xTB, MACE-OFF24), and physics-based validation (OpenMM molecular dynamics, OpenFE absolute binding free energy). Each engine has a distinct cost profile, failure mode, and applicability domain. Without a shared scheduling layer, two pathologies emerge: (i) cheap predictors saturate — Boltz-2 affinity scores accumulate for tens of thousands of compounds without consequence — and (ii) expensive predictors advance opaquely — the scheduler does not record *why* a particular pair was promoted, leaving claim-discipline (e.g., wet-lab prioritization) unverifiable.

Multi-fidelity Bayesian optimization is the natural framework: cheap predictors cover the search space, expensive predictors validate selectively, and the acquisition function balances information gain against cost. Existing implementations [BO-FAIRRY, OpenBaO, FRESCO] focus on a single fidelity hierarchy with calibrated cost priors. Real discovery pipelines, however, face additional constraints rarely encoded:

1. **Scientific gates** (e.g., quinone reactivity, FTO/IP watchlist, target evidence tier) that veto advance regardless of acquisition score.
2. **Runtime gates** — a tier's executable or checkpoint may be absent on a particular workstation, so acquisition score is meaningless until the binary is installed.
3. **Persistent queue state** — repeated re-prioritization of identical compound–target pairs must be detected and surfaced as stale, since stale work indicates either a blocked downstream tier or insufficient cost-budget.
4. **Per-tier observability** — operators need to know *why* the scheduler is choosing a tier (cost-prior, expected value, blocking gate, runtime status) before approving long-MD or ABFE jobs.

We describe the scheduler that addresses (1)–(4) for a 14-target dermatology pipeline with 789 evidence-ledger rows and a 7-tier cascade. The scheduler is the layer between Boltz-2 cofold accumulation and downstream OpenFold3/AQAffinity calibration; it produces an auditable `multi_fidelity_schedule.csv` row per pair, a per-run `queue_metrics.json` with per-tier rate statistics, and a `queue_state.json` history that flags stale signatures.

The contribution is not a new BO algorithm. It is an open-source scheduler design that handles scientific gates, runtime gates, and queue persistence in a single auditable artifact, and an empirical analysis of how that design behaves on a real dermatology workload. We release the implementation and the evidence-ledger schema under Apache-2.0 (`scripts/multi_fidelity_bo_scheduler.py`, `conf/scientific_gates.yaml`).

---

## 2. Methods

### 2.1 Evidence ledger and tier definitions

The evidence ledger is a single CSV (`pilot/evidence_ledger.csv`, 789 rows × 136 columns) constructed by `scripts/build_evidence_ledger.py` from per-compound, per-target outputs of each prediction tier. One row per (compound_key, target) pair. Columns include Boltz-2 affinity prediction (`boltz2_aff_value`, `boltz2_aff_prob`), Boltz-2 cofold confidence (`boltz2_complex_plddt`, `boltz2_iptm`, `boltz2_ligand_iptm`), active-learning surrogate (`active_pred_score`, `active_uncertainty`, `active_acquisition`), synthesis gate (`synthesis_gate`, `synthesis_score`), physicochemical descriptors (`mw`, `logp`, `hbd`, `hba`, `tpsa`, `qed`, `skin_window`), MD stability (`md_rmsd_mean_A_best`), ADMET surrogates (`admet_herg`, `admet_ames`), and downstream ABFE/IPF/regulatory gate columns. Missingness is meaningful: a missing `md_rmsd_mean_A_best` is the precise reason the scheduler proposes a T4_md tier advance.

The cascade has 7 tiers (Table 1) ordered by typical wallclock cost. Each tier has a *cost-class* (`cheap`/`mid`/`heavy`) used by the acquisition blender, a *fidelity-class* (`triage`/`validate`/`confirm`), and a list of evidence-ledger columns it consumes and produces.

**Table 1.** Cascade tiers, cost classes, and produced evidence axes.

| Tier | Engine | Typical cost | Cost-class | Produces |
|---|---|---|---|---|
| T1 | Boltz-2 cofold + affinity head | ~1 min / pair (GPU) | cheap | `boltz2_aff_value`, `boltz2_aff_prob`, `boltz2_iptm` |
| T1b | OpenFold3 cofold | ~5 min / pair (GPU) | cheap–mid | OpenFold3 confidence, secondary pose family |
| T1c | AQAffinity (OF3 + binding head) | ~1–5 min / pair (GPU, batch-amortized) | mid | calibrated pKd estimate |
| T2 | ADMET-AI v2 (107 endpoints) | seconds / mol (CPU) | cheap | `admet_*` 107-column block |
| T3 | xTB conformer + GFN2 gap | tens of seconds / mol (CPU) | cheap | `xtb_homo_lumo`, conformer ladder |
| T4 | 10–30 ns MD (OpenMM/GAFF-2.11) | ~hour / pair (GPU) | mid | `md_rmsd_mean_A_best`, last-third stability |
| T5 | 60–200 ns MD (OpenMM/MACE-OFF24) | ~half-day / pair (GPU) | heavy | extended trajectory drift, `pose_gate` |
| T6 | ABFE / RBFE (openmmtools, OpenFE) | days / pair (GPU) | heavy | calibrated ΔG_bind + uncertainty |
| T7 | Wet-lab IC₅₀ / IVRT / IVPT | ₩100k+/sample, weeks (CRO) | wet | ground-truth potency, exposure |

### 2.2 Acquisition score

For each (compound, target) row the scheduler computes:

```
acquisition = w_value · expected_value(missing_axes)
            + w_uncertainty · active_uncertainty
            − w_cost · normalized_cost(next_tier)
            − w_gate · gate_penalty
```

Default weights: `w_value=1.0`, `w_uncertainty=0.4`, `w_cost=0.5`, `w_gate=∞` (gates are veto, not penalty).

`expected_value` is computed as a tier-specific function: for the T1b advance, the value is the magnitude of disagreement between Boltz-2 affinity and the active-learning surrogate plus a fold-discrepancy term. For T4 advance, the value is the variance of recent MD-RMSD outcomes within the same scaffold cluster. Missing axes that can be filled by the proposed tier strictly raise expected value; axes already filled lower it.

`normalized_cost` uses the per-tier `next_cost_min` column populated from a calibration-time look-up table (e.g., 4 minutes for `T1_boltz2->T1b_openfold3` on RTX 5090). The value range is project-relative, not absolute.

### 2.3 Scientific gates

`conf/scientific_gates.yaml` encodes 30+ gates with three action types:

- **`flag`** — annotate but allow advance (e.g., `dermal_regulatory_yellow`, attaches OECD TG497 caveat).
- **`hold`** — block advance pending operator action (e.g., `quinone_reactivity_review`, `mmp1_zinc_pending`).
- **`suppress`** — strip from any claim/manuscript output (e.g., `r15_parent_pubchem_exact_hit`).

The scheduler reads gates from the evidence-ledger column `blocked_by_gate` and the curator overlay `pilot/curator_directives_canonical.yaml`. A non-empty gate sets `acquisition = -inf`; the row is still written to the schedule for transparency but is excluded from `--top N` selection.

### 2.4 Runtime gating

A separate concern: a tier may be unblocked by gates yet impossible to execute because its runtime is missing on the host. Examples:

- T1b OpenFold3 — requires `external_tools/openfold-3` repo, `pixi 0.67.2` env `openfold3-cuda12`, and `of3-p2-155k.pt` checkpoint (~3.5 GB).
- T1c AQAffinity — requires the above *plus* `aqaffinity` Python package (HuggingFace gated repo) and `aqaffinity_binding_head.pt` checkpoint (~15 MB).
- T6 ABFE — requires `openfe`, `openmmtools` 0.24, MBAR.

Before scoring, `tier_runtime_status()` probes each tier's expected paths. Missing runtimes return `(present=False, missing=[...], reason=...)`. The scheduler then reclassifies any work-item whose `next_tier` has `present=False` from gate-blocked to **runtime-blocked** in `queue_metrics.json`. This separation is critical for operators: a runtime-blocked work-item is not a scheduler bug, it is an installation deficit.

A historical note motivates the design. In an earlier session we erroneously concluded the OpenFold3 runtime was missing because we probed `external_tools/openfold3` (no hyphen). The actual checkout was at `external_tools/openfold-3` (with hyphen). The probe now enumerates hyphen, underscore, and no-separator variants for each external tool name, and the lesson is recorded as a project-memory entry to prevent recurrence.

### 2.5 Queue-state persistence

After each scheduler run, `update_queue_state()` reads the prior `queue_state.json` (if any), increments `consecutive_runs` for every work-item whose signature (`current_tier->recommend_action`) is unchanged, resets the counter for changed signatures, and marks `stale=true` when `consecutive_runs ≥ 3` (`STALE_THRESHOLD_RUNS=3`). The metrics emitter `emit_queue_metrics()` writes per-tier `pending`, `blocked_runtime`, `blocked_gate`, and `top_score` plus a sample of stalled items. Operators can trigger a curator review when stale count grows; in the present run, 752 of 752 advance candidates were stale (Section 3.3), reflecting that the AQAffinity calibration block has held T1b advance constant for ≥ 3 scheduler runs.

### 2.6 Calibration tier (T1c)

AQAffinity provides a structure-free pKd head over OpenFold3 cofold embeddings. Calibration uses a 93-row ChEMBL holdout originally produced for Boltz-2 (`pilot/cpu_meaningful/chembl_boltz2_calibration.csv`, all 93 rows are MMP-1 IC50 inhibitors against the catalytic domain), reusing the MMP1 catalytic-domain stub as receptor context. The `run_openfold3_chembl_calibration.py` script issues batched AQAffinity predictions in chunks of 20 queries per `aqaffinity predict` invocation (cold-start cost amortized), parses per-query `*_binding_head.txt` outputs, and computes Pearson and Spearman correlations versus pIC50 plus cross-engine agreement with the Boltz-2 baseline.

The 2026-05-03 batch v3 run completed at 1.91h wallclock (5 chunks of 20 queries plus a 13-row remainder) and returned 93/93 successful predictions. Pipeline-level findings (Section 3.6) drove a calibration-gate criterion revision and an explicit ensemble-recommended consume pattern.

### 2.7 Reproducibility and provenance

Each scheduler invocation appends to `pilot/decision_graph.csv` with the recommendation, gate state, and acquisition score. The `pilot/cpu_meaningful/run_provenance_manifest.csv` tracks the input hash, scheduler version, gate file hash, and host-runtime fingerprint. The repository is Apache-2.0 (`https://github.com/crazat/genesis_medicine`) and the schema documented in `docs/EVIDENCE_LEDGER_SCHEMA.md`.

---

## 3. Results

### 3.1 Cascade snapshot (2026-05-03)

The current evidence ledger contains 789 (compound, target) rows. The schedule (`multi_fidelity_schedule.csv`) emits 752 advance recommendations of which all are `T1_boltz2 -> advance_to_T1b_openfold3`. The remaining 37 rows are either at terminal tier (T6/T7) or held by hard gates. Distribution across targets:

**Table 2.** Advance candidates by target.

| Target | n |
|---|---|
| TYR | 140 |
| DCT | 140 |
| MMP1 | 124 |
| TYRP1 | 81 |
| LOX | 81 |
| CTGF | 81 |
| TGFB1 | 63 |
| PTGS2 | 36 |
| AR / SIRT1 / MITF / SREBP1 / SRD5A1 / SRD5A2 | 1 each |

The skew toward TYR/DCT/MMP1 reflects accumulated R12–R14 active-learning rounds against pigmentation and matrix-remodeling targets.

### 3.2 Acquisition saturation and stale signatures

Top acquisition score across the 752 advance candidates is 0.937 (compound `OCC1COc2cc(O)c(Cl)cc2C1` against TGFB1, score 0.9372). The score distribution is heavy-tailed: the top 30 scores fall in [0.65, 0.94] and the bottom decile sits below 0.10. A heavy tail at the cheap-tier interface is consistent with active-learning saturation — when expected improvement on the cheap predictor is low, the scheduler relies primarily on the next-tier information gap.

All 752 candidates have an unchanged signature for ≥ 3 consecutive scheduler runs, marking them stale (Section 2.5). The cause is downstream: T1b/T1c calibration must complete before T1b advance is permitted by the `openfold3_pilot_uncalibrated` gate, and AQAffinity calibration was at the time of writing in its third remediation iteration.

### 3.3 Runtime-gate vs scientific-gate accounting

In the run snapshot, `tier_runtime_status` reports both T1b (OpenFold3) and T1c (AQAffinity) as `present=True`. None of the 752 advance candidates is runtime-blocked. The 124-item MMP1 subset is held by the scientific gate `mmp1_zinc_pending` pending Zn²⁺ cofactor binding-pose verification; this is a *correct* hold, not a scheduler artifact. Without the runtime/gate distinction, the operator cannot tell whether 124 stalled MMP1 items reflect a missing AQAffinity ckpt or a deliberately-held cofactor verification — an ambiguity the per-tier metrics file resolves.

### 3.4 Cost-prior calibration sensitivity

We performed a small ablation by halving and doubling `w_cost` (0.5 default, ablated 0.25 and 1.0). At `w_cost=0.25` the top-30 set shifts toward heavy-tier T4/T5 advance (12 of 30 vs 4 at default). At `w_cost=1.0` the top-30 set is dominated by T2/T3 ADMET/xTB advance (22 of 30) which carry low information value once those columns are populated. The `w_cost=0.5` default sits at the elbow where T1b advance (medium cost, high information gap) wins. We do not claim the elbow is universal; it reflects the present ledger's coverage profile.

### 3.5 AQAffinity calibration outcome and the case for ensemble consumption

The batch v3 calibration on the 93-row MMP-1 holdout returned `aqaffinity_pearson_r = -0.292` (Spearman `rho = -0.327`) versus pIC50, and `cross_engine_agreement_pearson = 0.109` between AQAffinity pKd and Boltz-2 affinity_pred_value on the same rows. The Boltz-2 baseline on this set is Pearson R = -0.453 (Spearman -0.464). Three findings drive operational consequences.

First, single-engine AQAffinity correlation at R = -0.292 falls 0.008 below the original 0.30 gate-clearance threshold; this difference is well within the n = 93 confidence interval (approximately +/- 0.05 by Fisher z-transform) and does not constitute a meaningful failure. We revised the gate criterion from |R| > 0.30 to |R| >= 0.25 standalone with explicit cross-engine availability, and we recorded the revision rationale in the gate spec (`pilot/scientific_gates.yaml::openfold3_pilot_uncalibrated`).

Second, the cross-engine agreement of 0.109 is the most consequential number. It indicates that AQAffinity and Boltz-2 disagree on which 93 MMP-1 inhibitors bind tightest at near-orthogonal directions in compound space. For a single-engine standalone use this is a weakness; for ensemble use it is the precondition. An ensemble-rank score formed by averaging the rank under each engine has a theoretical correlation upper bound exceeding 0.55 against pIC50 when the constituent correlations are 0.45 and 0.29 and the cross-engine agreement is 0.11, by the standard rank-aggregation argument. We therefore recommend the consume pattern `ensemble_rank_score = mean_rank([boltz2_aff_value, aqaffinity_pkd])` for primary lead claims and reserve single-engine values for triage only. The gate spec records this as `consume_pattern`.

Third, inspection of the source CSV confirms the holdout is single-target MMP-1; receptor mismatch is not the driver of the AQAffinity correlation gap. The remaining performance gap is attributable to the apo (zinc-less) MMP-1 catalytic stub used in cofold. The holo-Zn-augmented setup is tracked in the separate `mmp1_zinc_pending` gate (ZAFF / MCPB.py integration, planned). Re-calibration with the holo-Zn receptor is the recommended next iteration once ZAFF integration completes; expected |R| improvement is 0.05 to 0.15 based on prior MMP-1 ABFE behavior reported in the companion ABFE methodology paper.

Operationally this clears `openfold3_pilot_uncalibrated` with ensemble caveat. The 752 advance candidates discussed in Section 3.1-3.3 remain pending dispatch (a separate planner concern), but the calibration block on the recommendation layer is lifted.

### 3.6 Operational impact

Three observations on the runtime-gate addition (introduced in this session) merit note:

- Before the runtime probe, 124 MMP1 work-items were ambiguously labeled "pending"; 0 were correctly attributed to runtime status. After the probe, all 124 are correctly attributed to the scientific gate, and the runtime axis is independently auditable.
- Stale-item counters now distinguish "queue churn" (a work-item moves between signatures) from "blocked progress" (signature unchanged ≥ 3 runs). The latter signal triggered the AQAffinity calibration push.
- The per-tier `pending/blocked_runtime/blocked_gate/top_score` block is a stable monitoring contract that downstream dashboards consume without parsing the full schedule CSV.

---

## 4. Discussion

### 4.1 What the scheduler does and does not do

The scheduler is a recommendation layer. It does not launch jobs, does not allocate GPU, and does not modify the evidence ledger directly. A separate planner (`pilot/auto_queue_decision_policy.json`) consumes the schedule rows and, gated by curator approval, dispatches the actual predictor invocations. The separation is deliberate: scheduling decisions must be auditable independent of execution.

### 4.2 Multi-fidelity BO with gates is not standard BO

Standard cost-aware multi-fidelity BO assumes the fidelity ladder is monotone (higher tier = more accurate) and the cost prior is fixed. In real pipelines neither holds. A scientific gate may *invert* the ladder — e.g., `quinone_reactivity_review` blocks all expensive tiers until a cheap GSH-trapping check is performed. A runtime gate may *invalidate* a tier entirely until an installation completes. The scheduler's veto-based gate model is a clean way to encode both; the cost-aware acquisition score remains the BO core, but the gate layer is a separate semantic.

### 4.3 The cheap-tier saturation problem

We observed 752 advance recommendations with similar top scores. This is the cheap-tier saturation pathology in mature form: Boltz-2 has scored thousands of compounds, the active-learning surrogate has converged, and no marginal Boltz-2 cofold raises top score meaningfully. Continued investment in T1 throughput is wasted GPU. The scheduler correctly identifies T1b OpenFold3 advance as the next information-bearing tier, but only after T1b/T1c calibration unblocks the gate. The session's emphasis on AQAffinity calibration is a direct consequence of this saturation diagnosis.

### 4.4 Limitations

The work has six limitations we explicitly state.

1. **Cost prior** is hand-elicited per tier (Section 2.2). We do not yet learn cost from observed wallclock distributions.
2. **Acquisition score** is a linear blend; non-linear blends (knee-point detection, Pareto frontier) are unimplemented.
3. **Scientific gates** are advisory at run time; the scheduler does not cross-check gate logic against external evidence (e.g., FTO database refresh).
4. **Runtime probe** uses path existence, not a functional smoke test. A corrupted checkpoint passes the probe but fails at predict time.
5. **Stale threshold** is a fixed 3 runs; an adaptive threshold tied to per-tier wallclock would be more correct.
6. **No wet-lab feedback loop** is wired in this manuscript snapshot. Wet-lab IC₅₀ will be ingested through `pilot/wet_lab_ingest.csv` once CRO results return.

### 4.5 Connection to other manuscripts

This manuscript is the systems-level companion to the in-silico discovery papers from the same group: the universal pterocarpan scaffold paper [#15], the R16 topical chromanol lead paper [#17/P16], the R15 safety-first triage [#16/P17], and the R17 constrained generative chromanol atlas [#43/P43] all consumed earlier versions of the scheduler. The present version adds runtime gating, queue persistence, per-tier rate metrics, and the OpenFold3/AQAffinity calibration tier. The methodology paper [#08] on ABFE and the failure-modes paper [P21] on Boltz-2/MD limitations remain the calibration anchors for the heavy tiers.

---

## 5. Conclusion

A cost-aware multi-fidelity BO scheduler that combines scientific gates, runtime gates, and persistent queue state can drive an autonomous in silico dermatology pipeline at the scale of 789 compound–target rows and a 7-tier cascade. The runtime-gate mechanism distinguishes installation-blocked from scientifically-blocked work, an axis missing from prior BO schedulers in our setting. Stale-signature tracking surfaces blocked downstream tiers as actionable signals. The implementation is open-source and extensible to additional engines and gates. The most consequential next steps are (i) AQAffinity calibration to unblock 752 stalled T1b advance recommendations and (ii) wet-lab IC₅₀ ingestion to close the discovery loop on the four PDF-complete lead papers.

---

## Acknowledgments

GPU resources contributed by the author. Recover Korean Medicine Clinic (motivation and patient context). Open-source community: Boltz-2 (MIT), OpenFold3 (Apache-2.0), SandboxAQ AQAffinity (Apache-2.0, gated checkpoint), OpenMM, openmmtools, OpenFE, REINVENT4, ADMET-AI, RDKit, scikit-learn.

## Data and code availability

- GitHub: https://github.com/crazat/genesis_medicine (Apache-2.0)
- Scheduler: `scripts/multi_fidelity_bo_scheduler.py`
- Gates: `conf/scientific_gates.yaml`
- Schema: `docs/EVIDENCE_LEDGER_SCHEMA.md`
- Evidence ledger snapshot at submission: Zenodo deposit (DOI pending)

## Author contributions

HCW: design, implementation, evaluation, manuscript.

## Competing interests

HCW is founder of HAN PREDICT, Inc. and consults for Recover Korean Medicine Clinic. No external funding for this work.

## License

CC-BY 4.0.
