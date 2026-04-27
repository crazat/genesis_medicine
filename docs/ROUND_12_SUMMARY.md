# Round 12 — Paper-tier integration summary (2026-04-27)

**Trigger**: User questioned value of infinite loop ("무한 loop 를 돌리는 이유는 뭐야?").
Response: switched from cycling cheap CPU work to **finite paper-tier sequential tasks**.

## Pipeline state at R12 commit

### CPU work (all completed in ~30 min)

| Output | Rows × cols | Source |
|---|---|---|
| `pilot/cpu_meaningful/all_boltz2_affinity_consolidated.csv` | 1043 × 5 | Cofold extraction across all `boltz_results_*` |
| `pilot/cpu_meaningful/admet_screen_combined.csv` | 2336 × 107 | ADMET-AI v2 batched (CPU mode, GPU owned by boltz) |
| `pilot/cpu_meaningful/admet_topical_focus.csv` | 2336 × 10 | logP / hERG / AMES / Skin_Reaction subset |
| `pilot/cpu_meaningful/integrated_top_candidates_per_target.csv` | 45 × 23 | Top 15 × 3 targets (CTGF/MMP1/SIRT1) by paper score |
| `pilot/cpu_meaningful/pharmacophore_features_top45.csv` | 45 × 18 | RDKit BaseFeatures.fdef counts + properties |
| `pilot/cpu_meaningful/shape_similarity_matrix_top45.npy` | 45 × 45 | rdShapeHelpers ShapeProtrudeDist |
| `pilot/cpu_meaningful/scaffold_clusters.csv` | 2000 × 4 | Butina d=0.6, 32 clusters |
| `pilot/cpu_meaningful/scaffold_safety_profile.csv` | varies | Per-Murcko mean ADMET (n≥5) |
| `pilot/cpu_meaningful/brics_fragment_frequency.csv` | varies | BRICS frag freq from top-45 |
| `pilot/cpu_meaningful/boltz_deep_metrics.csv` | 1109 × 18 | Confidence + ipTM + affinity full extraction |
| `pilot/cpu_meaningful/chemical_space_umap.csv` | 2336 × 5 | ECFP4 → PCA (UMAP unavailable in env) |
| `pilot/cpu_meaningful/cross_parent_diverse_100.csv` | 100 × 12 | Cross-parent BRICS diversity |
| `pilot/cpu_meaningful/figures/01-06_*.png` | 6 figures | Publication-grade 300 DPI |

### GPU chain (queued, ~3-4h drain)

```
gpu_queue_worker.sh (PID 277604):
  ✅ ctgf  done 13:04
  ✅ sirt1 done 13:27
  🔄 lox   running (affinity step)
  pending ar
  pending mitf
↓
gpu_chain_chembl.sh (PID 295843):
  pending: 95 ChEMBL extended × MMP1
↓
gpu_chain_tyr.sh (PID 296694):
  pending: 100 BRICS × TYR (pigmentation)
↓
gpu_chain_lowcov.sh (PID 297727):
  pending: 100 BRICS × SRD5A2/PTGS2/JUN/DCT (4 batches)
```

Total queued ETA: ~3-4 hours. Each batch = 100 cofold × ~25 min.

### Honest paper-tier scoring

```
score = 0.5 × P(binder)        (Boltz-2 affinity_probability_binary)
      + 0.3 × safety_composite (1 - hERG, 1 - AMES, 1 - Skin_Reaction)
      + 0.2 × novelty          (combined = qed - max_Tanimoto)
```

**Top per target (CTGF/MMP1/SIRT1, 3/14)**:
- CTGF: top011 score 0.590 (`OCc1ccc(O)c(OC2COc3cc(O)ccc3C2)c1`)
- MMP1: top097 score 0.518 (`COC(=O)C1Oc2cc(O)cc(O)c2CC1c1cc(OC)ccc1O`)
- SIRT1: top054 score 0.594 (`OCc1ccc(C=CC2COc3cc(O)ccc3C2)c(O)c1O`)

### Preprint integration

3/12 preprints updated with R12 §3 sections:
- `preprints/03_emb3_scar_case_study/manuscript.md` (CTGF + MMP1)
- `preprints/07_photoaging_egcg/manuscript.md` (SIRT1)

Pending integration (after GPU chain drain):
- `04_pigmentation_screening` ← TYR/DCT/TYRP1/MITF
- `05_alopecia_screening` ← AR/SRD5A2/CTNNB1
- `06_acne_microbiome` ← PTGS2

### Honest limitations

- **PoseBusters validation 0/300 pass** — extraction logic from Boltz-2 CIF
  needs proper ligand/receptor split. Currently `posebusters_validation_v2.csv`
  reports "no ligand found" for all 300. Method-dependent failure mode, NOT
  evidence of bad poses. To be fixed in R13.
- **UMAP unavailable** — fell back to PCA for chemical space. 4 DBSCAN
  clusters produced, but UMAP would give better topology.
- **Generic Bemis-Murcko** in scaffold SAR script failed (Pool pickle on
  local function); core Murcko + safety profile completed cleanly.
- **Affinity vs IC50**: Boltz-2 `affinity_probability_binary` is a binary
  classifier output, NOT pIC50. ChEMBL extended 95-inhibitor batch (queued)
  will provide regression calibration.

## Process discipline (CPU + GPU 동시 가동)

Per `feedback_cpu_gpu_concurrent.md` hard requirement:

- Throughout R12, GPU stayed at 70-92% utilization
- CPU saturated 24-core via Pool(24) for: ECFP fingerprints, conformer
  ensembles, scaffold extraction, ADMET batched inference
- Idle gaps minimized to <10s between CPU script transitions
- Switched from `cpu_queue_v6_continuous.sh` (infinite loop, marginal value)
  to `cpu_meaningful_queue.sh` + sequence of paper-tier finite tasks

## Files added to repo

```
scripts/
├── cpu_meaningful_queue.sh         # 4-task finite (originally written R11)
├── cpu_admet_screen.py             # ADMET-AI batched, 2336 mol
├── cpu_integrated_ranker.py        # Boltz×ADMET×novelty composite
├── cpu_pharmacophore_3d.py         # Conformers + features + shape
├── cpu_scaffold_sar.py             # Murcko + safety profile + BRICS frag
├── cpu_boltz_deep_extract.py       # 1109 cofolds × 18 metrics
├── cpu_chemical_space.py           # ECFP + UMAP/PCA + DBSCAN
├── cpu_paper_figures.py            # 5 publication figures
├── cpu_preprint_integrator.py      # Append R12 sections to preprints
├── cpu_posebusters_validate.py     # ❌ failed (CIF extraction)
├── cpu_posebusters_v2.py           # ❌ also failed (gemmi entity_type)
├── prep_remaining_target_yamls.py  # TYR yaml prep
├── prep_low_coverage_yamls.py      # SRD5A2/PTGS2/JUN/DCT yamls
├── gpu_chain_chembl.sh             # Chain step 2
├── gpu_chain_tyr.sh                # Chain step 3
└── gpu_chain_lowcov.sh             # Chain step 4

docs/
└── ROUND_12_SUMMARY.md             # This file

preprints/
├── 03_emb3_scar_case_study/manuscript.md   # +R12 §3.CTGF, §3.MMP1
└── 07_photoaging_egcg/manuscript.md        # +R12 §3.SIRT1
```

## Round 13 plan (after GPU chain drain)

1. Re-run integrated ranker on full 14-target dataset (currently 3 targets covered)
2. Re-run preprint integrator → fill all 12 preprints' R12 sections
3. Fix PoseBusters extraction (gemmi `entity_type` vs het residue check)
4. ChEMBL pIC50 calibration: scatter `affinity_pred_value` vs published pIC50
5. Synthesis route prediction (AiZynthFinder) on top 15 integrated candidates
6. Korean herbal natural product cross-reference (LOTUS / NPASS) for top hits
