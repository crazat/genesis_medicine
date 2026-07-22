# Supplementary Information — README

**Paper:** Cross-Validation of Three Neural Network Potentials for MMP-1 Zn Active-Site Inhibitor Ranking: A Computationally-Driven Repositioning Study of Vorinostat and Indapamide
**Author:** Cheongwoo Han (ORCID 0009-0004-4805-8815), Independent Researcher
**Archive:** `SI.zip` (contents described below)

This README documents the structure of the supplementary data bundle deposited alongside the manuscript on Zenodo.

---

## 1. σ_E sept-matrix CSV sweep (the bulk of the archive)

27,257 files named:

```
xtb_gfn{G}_{calc}_{solvation}_{solvent}_v{cohort}.csv
```

Each file is one cell of the GFN2-xTB conformational-energy (σ_E) reliability sweep:

| Token | Values | Meaning |
|-------|--------|---------|
| `G` (GFN level) | `0`, `1`, `2` | GFN-xTB Hamiltonian order (GFN0 / GFN1 / GFN2) |
| `calc` (calculation mode) | `sp`, `opt`, `ohess` | single-point / geometry optimization / optimization + Hessian (frequencies) |
| `solvation` | `alpb`, `gbsa` | implicit-solvation model (ALPB or GBSA) |
| `solvent` | e.g. `gas`, `water`, `dmf`, `benzene`, `cs2`, `phenol`, `benzaldehyde`, … | solvent environment for the implicit model (`gas` = vacuum) |
| `cohort` | e.g. `v271_v273`, `v304_v305`, `v303` | ligand/compound cohort version range (Boltz cofold batch IDs) |

The matrix spans **3 GFN levels × 3 calc modes × 2 solvation models × N solvents × N cohorts**, yielding the per-conformer relaxation energies (ΔE_relax) and energy-variance (σ_E) statistics reported in the manuscript (e.g. CHEMBL94487 σ 14.27 → 0.007 kcal/mol; indapamide ΔE_relax 6.42 gas / 7.48 water-ALPB).

## 2. Named result tables

| File | Description |
|------|-------------|
| `Table_S3_sigma_signature_mordred_top30.csv` | σ-outlier signature: top-30 Mordred descriptors by \|Spearman ρ\| against ΔE_relax on the n=140 SAR cohort (main text §4.6). Columns: rank, descriptor, family, n (137–140; per-descriptor, after Mordred missing-value exclusion), spearman_rho, spearman_p, rho_no_outliers (ρ recomputed with the three ΔE_relax ≈ 495–600 kcal/mol ligands deleted), pearson_r, pearson_p. Rank statistics are primary: those three ligands sit against a median ΔE_relax of 11.65 (IQR 4.29) and drive Pearson \|r\| > 0.99 for descriptors whose ρ is ≈ 0.26, so `pearson_r` is reported for transparency only and must not be read as an effect size. Regenerate: `scripts/round27_paperA/build_table_s3_sigma_signature.py` |
| `Table_S5_sulfonamide_diuretic_n17_MMP1_audit.csv` | n=17 FDA-approved sulfonamide-diuretic MMP-1 IC50/Ki audit (thiazide, thiazide-like, loop, CA-inhibitor subclasses) |
| `Table_S5_README.md` | column legend for Table S5 |
| `Table_S6_4engine_matrix_v19_vN.csv` | 4-engine consensus matrix (cohort v19 → vN) |
| `admet_baseline_summary_2026_05_22.csv` | ADMET baseline summary |
| `posebusters_v95_v200_extension.csv` | PoseBusters v2 structural-validity audit (cohorts v95–v200) |
| `posebusters_v201_v211.csv` | PoseBusters v2 audit (cohorts v201–v211) |
| `mordred_descriptors_1755.csv` | Mordred 2D molecular descriptors, 1,755 compounds (~40 MB) |
| `mordred_3d_1755.csv` | Mordred 3D molecular descriptors, 1,755 compounds (~40 MB) |

## 3. Cofold pose structures (SDF)

`sdf_*/` directories contain 8,085 Boltz-2 cofold pose structures (`.sdf`), grouped by cohort version range (e.g. `sdf_v201_v211/`, `sdf_v212_v275/`, `sdf_v352_poses/`). These are the 3D ligand poses underlying the PoseBusters audit and the cross-NNP single-point consensus.

---

## Notes
- σ_E and ΔE_relax are in kcal/mol.
- "Cohort version" (`v###`) tags refer to internal Boltz cofold batch identifiers, not manuscript versions.
- The headline consolidated reliability dataset (`sigma_e_v212_v303_unified_consolidated.csv`) and the coverage-calibrated conformal layer (`conformal/`) are deposited as top-level files in the same Zenodo record, outside this archive.
