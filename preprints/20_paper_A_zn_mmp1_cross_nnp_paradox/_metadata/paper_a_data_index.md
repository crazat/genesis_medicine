# paper_A Data and Figure Index

**Manuscript:** `/home/crazat/genesis_medicine/preprints/20_paper_A_zn_mmp1_cross_nnp_paradox/manuscript.md`
**Draft version:** 0.1 (2026-05-12)
**Author:** Han, Cheongwoo (crazat7@gmail.com)
**Companion preprints:** paper_B (Boltz-2x `--use_potentials` protocol, dir 21), paper_C (Zn metallohydrolase de-novo, dir 22).

---

## 1. Primary data files (NNP single-point CSVs)

All under `/home/crazat/genesis_medicine/pilot/round27_paperA/`.

### 1.1 xTB single points
- `xtb_v18_sp/xtb_v18_sp_results.csv` — GFN2-xTB SP on v18 (~1244 valid poses).
- `xtb_gfn2_ligand_v<NN>_sp/` — per-replicate GFN2-xTB SP on ligand-only extract. v<NN> ∈ {11..23}.
- `xtb_gfn1_ligand_v<NN>_sp/` — per-replicate GFN1-xTB SP. v<NN> ∈ {11..23}.
- `xtb_gfnff_complex_v<NN>_sp/` — per-replicate GFN-FF SP on full complex (Zn included). v<NN> ∈ {11..23}.

### 1.2 Orb-v3 single points (NNP)
- `orb_v3_extended/orb_v3_v<NN>_sp.csv` — Orb-v3 OMat SP per replicate. v<NN> ∈ {11..23}.
- `orb_v3_extended/orb_v3_omol25_v<NN>_sp.csv` — Orb-v3 OMol25 SP per replicate. v<NN> ∈ {11..23}.
- `orb_v3_extended/orb_v3_retro_sp.csv` — retro 100 PDBs for cross-check.
- `orb_v3_extended/orb_v3_fork_pot_sp.csv` — fork+pot 100 PDBs for cross-check (paper_B Boltz-community fork variant).

### 1.3 SevenNet single points (paper_A v4 expansion)
- `sevennet_extended/sn_omat24_v18_sp.csv`
- `sevennet_extended/sn_mpa_v18_sp.csv`
- `sevennet_extended/sn_matpes_pbe_v18_sp.csv`
- `sevennet_extended/sn_omol25_high_v18_sp.csv`

### 1.4 MatterSim, AIMNet2, ANI-2x, AceFF
- `mattersim_5M/mattersim_v<NN>_sp.csv` — v<NN> ∈ {11..23} + v24 partial.
- `aimnet2_extended/aimnet2_v<NN>_sp.csv` — v<NN> ∈ {11..23} (v11 partial).
- `ani2x_ligand/ani2x_v<NN>_sp.csv` — v<NN> ∈ {20, 22, 23} (partial set).
- `aceff_extended/aceff_v<NN>_sp.csv` — v<NN> ∈ {11..23}.

### 1.5 Classical force fields
- `mmff94_ligand_baseline_v2/mmff94_v<NN>_sp.csv` — v<NN> ∈ {11..23}.
- `uff_ligand_baseline/uff_v<NN>_sp.csv` — v<NN> ∈ {11..23}.

### 1.6 FeNNix-Bio1S (10th NNP, paper_A v4)
- `fennix_extended/fennix_v18_sp.csv` — sign convention is positive; flip required for cluster comparison.

---

## 2. DFT reference CSVs

All B3LYP/def2-SVP via PySCF 2.13.0.

- `dft_reference_chembl406_v22.csv` — CHEMBL406 5 conformers, B3LYP/def2-SVP, no D3 (initial verdict).
- `dft_reference_4ligand_extension.csv` — 4 ligands × 5 conformers = 20 conformers, B3LYP/def2-SVP, no D3.
- `dft_b3lyp_d3_verdict.csv` — combined 5 ligands × 5 conformers = 25 conformers, B3LYP and B3LYP-D3(BJ) where applicable.

---

## 3. Cross-correlation outputs

- `cluster_AB_analysis/cross_correlation_v5.csv` — initial 7-axis cluster analysis (paper_A v5).
- `cluster_AB_analysis/matrix_v5.npz` — 7-axis correlation matrix.
- `cluster_AB_analysis/v5g_13rep_table.csv` — 13-replicate × 5-pair cross-validation table (Table 1 source).
- `cluster_AB_analysis/v5g_13rep_full.npz` — 10 × 10 × 13-replicate correlation tensor.
- `cluster_AB_analysis/mattersim_cross_v13rep.csv` — MatterSim addition × 13 replicates.

---

## 4. Analysis scripts

All under `/home/crazat/genesis_medicine/scripts/round27_paperA/`.

- `analyze_cluster_AB_v5b.py` — original 7-axis analysis (paper_A v5).
- `analyze_cluster_AB_v5g.py` — 13-replicate × 11-axis cross-replicate analysis (current paper_A v5g).
- `nnp_sp_orb_v3.py` — Orb-v3 OMat / OMol25 single-point batch driver.
- `nnp_sp_mattersim.py` — MatterSim-5M batch driver.
- `nnp_sp_aimnet2.py` — AIMNet2-NSE batch driver.
- `nnp_sp_ani2x.py` — ANI-2x batch driver.
- `nnp_sp_aceff.py` — AceFF-2 batch driver.
- `nnp_sp_sevennet.py` — SevenNet variant batch driver (4 weights).
- `dft_pyscf_b3lyp_subset.py` — B3LYP/def2-SVP DFT reference driver.
- `dft_pyscf_b3lyp_d3_subset.py` — B3LYP-D3(BJ)/def2-SVP DFT reference driver.

---

## 5. Figures

Currently in `/home/crazat/genesis_medicine/manuscripts/paper_A_v4/figures/` (paper_A v4 versions):

- `fig_4nnp_paradox.png` / `fig_4nnp_paradox.pdf` — 4-NNP paradox figure (paper_A v4, initial discovery).
- `fig_9nnp_paradox_final.png` / `fig_9nnp_paradox_final.pdf` — 9-NNP cluster paradox final figure (paper_A v4).

Target figures for paper_A v5g (to be generated in `figures/` subdir of this preprint):

- `figures/fig1_omol25_paradox_13rep.png` — 13-replicate cross-validation stability plot, 5 method-pair lines, ±1 SD shaded bands. Source data: `cluster_AB_analysis/v5g_13rep_table.csv`.
- `figures/fig2_10axis_heatmap_v22.png` — 10×10 Pearson heatmap on v22 with cluster annotations (Cluster I QM-like blue, Cluster II FF orange, Isolated OMol25 red, Borderline ANI-2x/GFN-FF light).
- `figures/fig3_omat_vs_omol25_scatter_15panel.png` — 15-panel scatter, one per ligand, 100 conformers each, x = Orb-v3 OMat energy (kcal/mol per atom), y = Orb-v3 OMol25 energy. Shows ligand-by-ligand the paradox.
- `figures/fig4_training_data_lineage.png` — diagram: training-data lineage tree (Materials Project → OrbOMat/MatterSim → tight QM cluster; Meta OMol25 → OrbOMol25/SevenNet-OMol25 → isolated cluster).
- `figures/fig5_per_ligand_sigma_E.png` — bar chart of per-ligand σ_E across methods (Section 3.9 data).

Figure-generation scripts to be added under `scripts/round27_paperA/figures/`.

---

## 6. Cross-references in memory

For reviewer-defense and revision tracking:

- `project_paper_a_v5g_HEADLINE_13rep_validated_2026_05_10.md` — main 68σ finding.
- `project_paper_a_v5g_FINAL_v22_10axis_omol25_paradox_2026_05_10.md` — 10-axis heatmap source.
- `project_paper_a_v5g_OMol25_paper_admits_longrange_weakness_2026_05_10.md` — mechanism citation.
- `project_paper_a_v5g_DFT_VERDICT_2026_05_10.md` — DFT N=5 verdict (cluster I anti-correlates with cheap-DFT).
- `project_paper_a_v5g_DFT_caveats_bursch_2022.md` — DFT methodology limitations.
- `project_paper_a_v5g_SMOKING_GUN_biology_2026_05_10.md` — biology validation attempt (subsequently retracted).
- `project_paper_a_v5g_RETRACTION_size_confound_2026_05_10.md` — RETRACTION audit (size confound).
- `project_paper_a_v5g_MatterSim_materials_subcluster_2026_05_10.md` — 2nd materials NN confirmation.
- `project_paper_a_v5g_cluster_validation_2026_05_10.md` — 11-replicate prior validation.
- `project_paper_a_v4_orb_xtb_cross_nnp_2026_05_09.md` — paper_A v4 9-NNP matrix (Section 3.7 Table 4 source).
- `project_paper_a_v5_3cluster_paradox.md` — 3-cluster topology context (extension to MMFF/UFF antiCorr).

---

## 7. 15-ligand ChEMBL panel (manifest)

| ChEMBL ID | Heavy atoms | Charge | IC50 (nM) reported | Warhead |
|---|---:|---:|---:|---|
| CHEMBL406 (Prinomastat) | ~43 | 0 | 3 | sulfonamide-hydroxamate |
| CHEMBL415 | ~37 | 0 | 4 | hydroxamate |
| CHEMBL443684 (Marimastat) | ~27 | 0 | 5 | hydroxamate (peptidic) |
| CHEMBL94487 | ~32 | 0 | 12 | hydroxamate |
| CHEMBL257077 | — | 0 | 15 | hydroxamate |
| CHEMBL301236 | — | 0 | 42 | hydroxamate |
| CHEMBL57058 | ~30 | 0 | — | hydroxamate |
| CHEMBL259829 (CGS27023A) | ~28 | 0 | 310 | non-hydroxamate sulfonamide |
| CHEMBL292707 | — | 0 | 200 | hydroxamate |
| CHEMBL98 | ~32 | 0 | 2400 | aryl-sulfone hydroxamate (weak) |
| CHEMBL2105729 | ~22 | 0 | 18,000 | hydroxamate (very weak) |
| CHEMBL3036 | — | 0 | — | macrocyclic hydroxamate |
| CHEMBL_supp_1 | — | varied | — | supplemental |
| CHEMBL_supp_2 | — | varied | — | supplemental |
| CHEMBL_supp_3 | — | varied | — | supplemental |

(Heavy-atom counts are approximate; refer to `pilot/round27_paperA/ligand_manifest.csv` for canonical values.)

---

## 8. Reproducibility hash and pinned versions

- Boltz-2x: v0.6.x cofold checkpoint (Mar 2026 community release).
- xtb: 6.7.0 (conda-forge).
- orb-models: 0.5.x, torch 2.8 cu128 (RTX 5090 sm_120 compatible).
- mattersim: 1.1.x, torch 2.8 cu128.
- aimnet2: 2024.x.
- torchani: 2.2.
- PySCF: 2.13.0.
- RDKit: 2024.09.x.
- Python: 3.11.x.
- CUDA: 12.8.

---

*Last updated 2026-05-12 to reflect manuscript draft v0.1.*
