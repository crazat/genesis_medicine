# Supplementary Information — paper_A v0.3 (core reproduction bundle)

Everything needed to regenerate every number and both figures in the manuscript. 3.6 MB, 12 files.
This is deliberately **not** the full archive: see "What is not here" below.

## Data

| File | Used by | Contents |
|---|---|---|
| `data/paper_a_v3_three_nnp_unified.csv` | §4.1, Figure 1 | 15 ligands × 3 NNP single-point energies + ranks |
| `data/conformal_sigma_e_paperA.csv` | §4.2 | per-cell σ_E conformal intervals, 1,755 (ligand × method × solvent) cells |
| `data/conformal_coverage_validation.txt` | §4.2 | 200-split empirical coverage, σ_E **and** σ_iptm blocks |
| `data/paper_a_sar_dataset.csv` | §4.7, Figure 2 | 140 ligands × (ΔE_relax + 1,615 Mordred descriptors). **`ic50_nm` is present but unused — see manuscript §2.2** |
| `data/Table_S3_sigma_signature_mordred_top30.csv` | §4.7 | top-30 descriptors by \|Spearman ρ\| vs ΔE_relax, with outlier-deleted ρ and Pearson r |
| `data/posebusters_v95_v200_extension.csv` | §5 | PoseBusters v2 mol-mode, 11 checks × 1,590 structures |
| `data/posebusters_v201_v211.csv` | §5 | same, later cycles |
| `data/chembl_mmp1_calibration.csv` | §2.2 | the 15-ligand panel. **Provenance unverified — identifiers and potency annotations are not used anywhere in this work.** Included so the reader can check that claim, not to support it |

## Scripts

| Script | Reproduces |
|---|---|
| `scripts/build_figures_v03.py` | Figures 1–2 |
| `scripts/build_table_s3_sigma_signature.py` | Table S3 |
| `scripts/audit_section46_sigma_signature.py` | the §4.7 rank analysis, and the refutation of the v6 table it replaces |
| `scripts/audit_section45_de_relax.py` | the ΔE_relax trajectory audit behind the §6.1 withdrawals |

Scripts expect the repository layout; adjust the paths at the top of each if run standalone.

## What is not here, and why

- **The σ_E sept-matrix sweep** (29,700 CSVs, 141 MB) underlying §4.3–§4.6. Frozen: last write 2026-06-10.
  Present in the full `SI/` tree and in `SI.zip`; omitted here only for size.
- **17,940 co-fold pose SDFs** (66 MB) underlying the PoseBusters audit of §5. The audit CSVs above summarise
  them per structure and per check, which is sufficient to reproduce every reported number.
- `SI.zip` was rebuilt 2026-07-16 against the frozen tree (the 2026-06-02 build predated 10,153 files added
  between 2026-06-03 and 2026-06-10). It carries the full sept-matrix and pose set; this core bundle is the
  subset a reader needs to reproduce the manuscript.

## Audit record

`AUDIT_2026_07_16_quantitative_claims.md` — the claim-by-claim audit that produced v0.3, including the
verdicts that removed roughly sixty per cent of v6.
