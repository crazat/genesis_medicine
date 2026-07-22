# paper_A v6 — audit of load-bearing quantitative claims (2026-07-16)

Triggered because three unreproducible numbers surfaced in one day. Every verdict below is reproducible
from the scripts named; nothing is asserted from prose. **Do not submit until the CONTRADICTED rows are
resolved.**

Root cause is structural: **paper_A's 541-line manuscript contains 2 mentions of `.csv`.** It has no
provenance layer. paper_B, by contrast, closes each subsection with `Source: <file>.csv; analysis script
<path>`. Where nothing points at a file, nothing can be checked — which is how the §4.5 and §4.6 errors
survived to a submission-ready draft.

## Verified — reproduces from source

| Claim | Manuscript | Recomputed | Source |
|---|---|---|---|
| cross-NNP Pearson r | 0.9146 | **0.9142** | `pilot/paper_a_v3_three_nnp_unified.csv` (Orb-v2 vs Orb-v3, n=15) |
| 1000-bootstrap 95% CI | [0.817, 0.973] | **[0.826, 0.971]** | same (resampling variance) |
| leave-one-out r | 0.9146 ± 0.0115 | **0.9141 ± 0.0104** | same |
| conformal coverage (σ_iptm) | 79.88±2.15 / 89.93±1.72 / 95.11±1.19 | **exact match** | `conformal/conformal_coverage_validation.txt` |
| PoseBusters perfect-pass fraction | 33 % | **33 %** (5/15) | `SI/posebusters_v95_v200_extension.csv` |
| PoseBusters n | 45 | **45** = cycles v95+v96+v97 × 15 ligands | same |
| §4.6 "size/flexibility not significant" | MW, RotBonds, NumRings n.s. | **MW p=0.485, nRot p=0.139, nRing p=0.118** | `audit_section46_sigma_signature.py` |
| Vorinostat ΔE_relax | 3.89 | **3.91** | `audit_section45_de_relax.py` (May-16 trajectory) |

Conformal numbers are **not** mixed between papers: the validation file holds both σ_iptm (ligand-level,
n=15) and σ_E (cell-level, n=1755) blocks; paper_A §4.10 quotes only q̂, paper_B §3.7 correctly quotes the
σ_iptm block.

## Contradicted — the source data says otherwise

| Claim | Manuscript | Data | Status |
|---|---|---|---|
| §4.6 σ-signature top-10 | BCUT/ETA/spectral, all \|r\|>0.97, p≈0, negative | all ten at **r≈0** (p up to 0.91) | **rewritten 2026-07-16** → rank correlations (ATS6s +0.640, TopoPSA(NO) +0.598, nHetero +0.578); direction, family and strength all inverted |
| §4.5 ΔE_relax ordering — **in both abstracts** | Indapamide 7.48 **<** CHEMBL94487 9.36 ⇒ "indapamide is NOT a σ outlier, supporting its repositioning candidacy" | Indapamide **12.27** **>** CHEMBL94487 **5.69** | **UNRESOLVED — the argument inverts** |
| PoseBusters quality floor | "all structures ≥ 11/12 checks" | **10 of 15** v95 structures pass only **10/11**; minimum is 10, not 11 | **UNRESOLVED** |

§4.5 detail: no xtb JSON holds a `dE_relax` for CHEMBL98 / CHEMBL406 / CHEMBL94487 / CHEMBL57058 (a 9.36
exists but belongs to CHEMBL294088 — coincidence). The only surviving artifact is the 2026-05-16 xtb
trajectory in `pilot/round28_retroval/top_hit_work/<cmpd>/xtbopt.log`, one day before manuscript v0.1.
Two independent checks confirm the reading: re-running `xtb --sp --alpb h2o` on `in.xyz` reproduces each
trajectory's first-frame energy to 8–9 decimals (so the stored runs were ALPB/water and `in.xyz` was their
input), and Vorinostat comes out at 3.91 against the claimed 3.89 — the method reproduces the value that is
right. **Honest limit:** ΔE_relax is the strain of one starting pose, and the scratch directory holds a
single run while §4.5 claims three solvent modes, so it was overwritten ≥2×; the original pose may be gone.
We cannot prove the numbers were never computed. We can only state that nothing holds them and the one
artifact that survives inverts the comparison. Either way they must be recomputed from a recorded, named
pose before submission.

## Minor — presentational, not fabrication

| Claim | Issue |
|---|---|
| σ 14.27 → 0.007 = "2,068× reduction" | A reader computes **2,039×**. 2,068 is right only for the unrounded 0.0069. Print 0.0069, or state 2,039×. |
| PoseBusters "12 checks", "≥11/12", "perfect 12/12" | The data has **11** boolean checks (PoseBusters *mol* mode; no protein-distance checks anywhere, so it was never *dock* mode). Denominator is wrong throughout. |
| PoseBusters mean pass 94.5 % | Actual **93.9 %** on the same rows. |
| "cross-NNP correlation **reaches** r=0.9146" | 0.9146 is the **lowest** of the three pairwise correlations, not a high-water mark. "reaches" misreads. |

## Unverifiable — no source exists

- **Figure 4 panel A (SHAP top-20 hydroxamate strata)** — no generating script, no source data; only the
  output PNG/PDF. It cannot be regenerated, and its numbers cannot be checked. Panel B is now contradicted
  by the rewritten §4.6, so the composite figure needs rebuilding — which panel A blocks.

## Undisclosed weakness — true but not stated

**The "three-engine cross-validation" carries ~2 independent signals, not 3.** MACE-OMol25 and Orb-v3
correlate at **r = 0.9992** — both are trained on OMol25, so their agreement is redundancy, not
cross-validation. Pairwise: Orb-v2↔MACE +0.9175, Orb-v2↔Orb-v3 +0.9142, MACE↔Orb-v3 +0.9992. The paper
should say this; it is the same illusory-diversification failure that `phase10_portfolio_risk.py` measures
elsewhere in this project (N_eff 1.68 of 7).

## Reproduce this audit

```
python scripts/round27_paperA/audit_section46_sigma_signature.py   # §4.6
python scripts/round27_paperA/audit_section45_de_relax.py          # §4.5
python scripts/round27_paperA/build_table_s3_sigma_signature.py    # regenerates Table S3
```

## Not yet audited

R²=0.4353 (140-ligand SAR leakage-fix), the 37,500-structure cofold count, the n=17 sulfonamide audit,
ChEMBL332 record counts (vorinostat 0 of 8,274; indapamide 2 placeholders), the patent-landscape audit,
and every §5–§8 literature-derived figure.
