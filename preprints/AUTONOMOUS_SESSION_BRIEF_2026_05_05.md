# 12h Autonomous Session Brief — for user review on wake

**Session window:** 2026-05-04 22:34 KST → 2026-05-05 ~10:34 KST
**User delegation:** "12시간 동안 네가 알아서 판단해서 최적화된 방향으로 나아가도록 해보자"

---

## TL;DR

System stable. apo MD progressing (~30+ ns / 100 ns at first quarter). 7 paper deliverables produced + 2 paper drafts written. 3 deadlock incidents diagnosed and resolved. Memory rules for safe concurrency now documented.

---

## What was produced

### Paper #A (methodology)
- **F3 DUD-E enrichment**: AUC=0.846 (gap, mass-independent), 0.884 (energy, mass-bias). EF5%=5.48 / EF10%=4.11 / BEDROC=0.277. Cheap QM (xtb single-point) is meaningful for hydroxamate inhibitor screening.
- **DUD-E v2 refine 432-conf** running (~11 min wall, output: pilot/dude_benchmark_mmp1/scored_all_432conf.csv) — strengthens F3 with converged ensemble.
- Pre-registration template updated: Tier-1 6 actual compounds (CHEMBL415-2105729), 8/5ns production protocol, deadlock scheduling rules, embelin exclusion rationale.
- Methods/results draft saved at preprints/paper_A_methods_results_draft.md (§2-§5).

### Paper #B (cross-engine multi-fidelity)
- **Headline**: Boltz-2 affinity_pred is dominated by MW (Spearman -0.645) and logP (-0.541) → mass/lipophilicity bias. Methods orthogonal at top-K (top-10 IoU ≈ 0).
- **xtb refine ladder convergence**: 432 conformers per molecule = converged threshold. Pairwise rank Spearman 432-vs-528 = 0.9999.
- **OF3 + AQAffinity Tier-1**: Pearson(pKd, pIC50) = -0.592, Spearman = -0.886 (sign-flipped, paper-grade ranking).
- **Active learning round 2 v3**: held-out Spearman 0.850 on 9728-mol master corpus. Surrogate ready.
- Headline draft saved at preprints/paper_B_headline_draft.md.

### Visualizations (publication-ready)
- pilot/paper_figures/fig1_dude_enrichment_roc.png
- pilot/paper_figures/fig2_boltz_vs_xtb_features.png
- pilot/paper_figures/fig3_of3_tier1_pIC50.png
- pilot/paper_figures/fig4_xtb_ladder_convergence.png
- pilot/paper_figures/fig5_al_round2_ranking.png
- pilot/paper_figures/fig6_master_deliverables.png (4-panel comprehensive)

### Memory rules saved (for next sessions)
- feedback_destructive_action_recommendation.md — when evidence is overwhelming, state recommended kill explicitly, don't hedge
- feedback_openmm_cuda_multiprocess_deadlock.md — 24-core ceiling rule, subprocess vs in-process pool difference, multi-OpenMM deadlock pattern

### Project memory
- project_autonomous_12h_session_2026_05_04.md (this session activity log)

---

## What's deferred / blocked

| Item | Why deferred |
|---|---|
| ABFE benchmark Tier-1 (8 days wall) | Must run sole-tenant; apo MD finishes ~10:30 AM tomorrow first |
| 9997 mol single-point xtb (full corpus) | In-process pool deadlocked apo MD; rewrote in subprocess pattern but ROI marginal vs existing master n_confs=2 data |
| KIPRIS patent novelty (paper #A F2) | Needs `KIPRIS_API_KEY` env var |
| OSF pre-reg filing | User action required; template ready |

---

## What requires user attention

1. **ABFE benchmark launch decision.** When apo MD finishes (~10:30 AM tomorrow), Tier-1 6-compound ABFE benchmark can launch sole-tenant. ~8 days wall. Confirms paper #A H1 hypothesis.
2. **Pre-registration filing.** Template ready at `preprints/PRE_REGISTRATION_TEMPLATE.md`. File at https://osf.io/registries/osfregistries/new/preregistration BEFORE launching ABFE benchmark.
3. **Embelin re-attempt decision.** Embelin Phase 5 deadlocked under multi-process GPU contention. Re-run sole-tenant requires apo MD finish. Or accept primary H3 evidence from EMB-3 (+0.38 ± 0.29 INCONCLUSIVE).
4. **Paper draft review.** Two drafts in `preprints/`: paper_A_methods_results_draft.md, paper_B_headline_draft.md. ABFE §3.4 in paper #A is placeholder.

---

## Operational lessons (for future sessions)

1. **Single OpenMM CUDA process at a time.** Multiple alchemical replica exchange jobs deadlock via CUDA context contention. Sequence them, never parallelize.
2. **Subprocess-blocking xtb pools (refine pattern) are safe alongside OpenMM CUDA.** In-process Python xtb interface pools at same worker count starve OpenMM dispatch.
3. **24-core ceiling**: 1 OpenMM + 22 subprocess workers = safe. Cumulative oversubscription with even 8 extra workers degrades apo MD.
4. **CPU and GPU "both at full power" historically**: this was sequential overlap (one ramping while other ramping), not sustained co-occupancy at 22+1 ceiling. Sustained co-occupancy requires care.

---

## System state at brief (2026-05-04 23:08 KST → updated 2026-05-05 03:06 KST)

- ~~apo MD: PID 3674029, ~30 ns / 100 ns, GPU 200W healthy, ETA ~10-12h~~ **COMPLETE 03:03 KST 100 ns / 100 ns. final.pdb + traj.dcd + APO_MD_OK + summary.json all written. ETA was actually ~5 hours not 12 (speed 17 ns/h ≈ 400 ns/day, much faster than initial 87 ns/day estimate).**
- ~~DUD-E 432-conf refine: 22 worker subprocess pool, ETA ~10 min more~~ **COMPLETE 23:32 KST. F3 enrichment with 432-conf: gap_eV_min AUC=0.874 (best mass-independent variant), gap_eV_mean=0.859. Paper #A §3.2 updated.**
- 25-min monitoring loop active. **GPU now idle (56W, 30GB free) — system has zero active jobs as of 03:06 KST.**

## Critical state change at 03:03 KST: apo MD finished

This unblocks the ABFE benchmark Tier-1 launch (sole-tenant available). However, two user-action prerequisites remain:
1. **Pre-registration filing** at OSF (template ready at `preprints/PRE_REGISTRATION_TEMPLATE.md`)
2. **Embelin re-attempt decision** (could run sole-tenant now; or accept INCONCLUSIVE evidence)

I did not autonomously launch the 8-day benchmark orchestrator because:
- 8-day commitment is significant
- Pre-reg filing is a research integrity safeguard the user should review first
- CHEMBL415 has partial deadlocked state from yesterday — restart strategy needs user awareness
- The /loop prompt's launch chain was set up before all the deadlock incidents and may need adjustment

When you wake up, the next-step decision is yours: file pre-reg + launch orchestrator, or revise plan first. apo MD output is in `pilot/mmp1_apo_zn_md_100ns/`.

---

*Generated autonomously by Claude during 12h delegation. All numbers derived from local files in pilot/. Verify before paper inclusion.*
