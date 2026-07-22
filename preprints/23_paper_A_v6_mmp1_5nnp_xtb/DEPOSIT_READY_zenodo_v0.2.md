# Zenodo Deposit — paper_A v6 (DEPOSIT-READY, single-author)

> Prepared 2026-06-02. Single-author self-submission per user decision (no co-authors).
> **The actual upload + "Publish" is done by you** (your Zenodo account, ORCID 0009-0004-4805-8815).
> This file is the exact field-by-field checklist. Nothing here is auto-published.

---

## 1. Upload type
- **Publication** → Publication type: **Preprint**

## 2. Title (paste verbatim)
```
Cross-Validation of Three Neural Network Potentials for MMP-1 Zn Active-Site Inhibitor Ranking: A Computationally-Driven Repositioning Study of Vorinostat and Indapamide
```

## 3. Creators (SINGLE author)
| Name | Affiliation | ORCID |
|------|-------------|-------|
| Han, Cheongwoo | Independent Researcher | 0009-0004-4805-8815 |

(Remove any prior co-author rows — this deposit is sole-author.)

## 4. Description (paste the Abstract — manuscript_v0.2.md lines 14-20)
Use the 250-word Abstract block from `manuscript_v0.2.md`. It already reflects the single-author scope and the v6 results (r=0.9146 cross-NNP, CHEMBL94487 σ 14.27→0.007 = 2068×, PoseBusters 94.5%, indapamide ΔE_relax within predictable regime, n=17 sulfonamide-diuretic audit).

## 5. License
- **Creative Commons Attribution 4.0 International (CC-BY-4.0)**

## 6. Keywords
`Boltz-2; neural network potentials; GFN2-xTB; MMP-1; matrix metalloproteinase-1; zinc metalloprotease; drug repositioning; vorinostat; indapamide; sulfonamide diuretic; PoseBusters; cross-validation; reliability; conformal prediction`

## 7. Files to upload (manifest)
| File | Path | Note |
|------|------|------|
| Manuscript | `manuscript_v0.2.md` (+ PDF export) | sole-author, 9 sections + abstract + refs |
| References | `references.md` | 239 refs (full comprehensive set — Zenodo allows over-scope) |
| Figure 1 | `figures/figure1_boltz_25cycle_convergence.png/.pdf` | Boltz 25-cycle convergence |
| Figure 2 | `figures/figure2_5nnp_bootstrap_ci.png/.pdf` | cross-NNP bootstrap CI |
| Figure 3 | `figures/figure3_xtb_3mode_outlier.png/.pdf` | xtb 3-mode σ outlier |
| Figure 4 | `figures/figure4_shap_top20_dual.png/.pdf` | SHAP top-20 feature importance |
| Figure 5 | `figures/figure5_7organ_pleiotropy.png/.pdf` | 7-organ pleiotropy |
| SI data bundle | `SI/` (zip) | σ_E sept-matrix CSVs + PoseBusters JSON + SAR/Mordred — **zip before upload** (27k files; consider a curated subset + a README) |
| Conformal layer | `conformal/*.csv` + `conformal_reliability_layer.py` | coverage-calibrated intervals |
| Consolidated σ_E | `sigma_e_v212_v303_unified_consolidated.csv` | headline reliability dataset |

> ⚠️ SI is 27,260 CSVs (~1.7 GB). Zenodo per-record limit is 50 GB but huge file counts are unwieldy — **recommended**: upload a single `SI.zip` + an `SI_README.md` describing the sept-matrix schema, rather than 27k loose files.

## 8. Related/alternate identifiers (optional but recommended)
- Relation: *is supplemented by* → (the SI Zenodo record if split out)
- Relation: *is part of* → Part I of the planned 3-paper trajectory (paper_B reliability protocol, paper_19 Korean herbal)

## 9. Pre-publish final checks (done ✓ / verify)
- [x] Author block = single author (Cheongwoo Han)
- [x] CRediT = sole author, all roles
- [x] No "co-author / pending confirmation / co-PI" claims in body (neutralized 2026-06-02)
- [x] PDF export `manuscript_v0.2.pdf` generated (pandoc 3.9 + weasyprint, NanumGothic+DejaVu fonts) — **reviewed all 50 pp, 0 breakage** (Korean/σ/Zn²⁺/superscripts/tables/code all render; single-author header confirmed p1)
- [ ] SI zipped + README written
- [ ] You click **Publish** (assigns DOI = priority date)

## 10. After publish
- Record the DOI here and in `references.md` self-citation.
- The same cleaned manuscript feeds the JCIM track (see `JCIM_submission_prep_plan.md`) — Zenodo priority is already secured, so JCIM review risk carries no priority-date downside.
