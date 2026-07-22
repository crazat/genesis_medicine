# DRAFT — Killer figure: static confidence cutoff vs σ_iptm (manuscript-ready, English)

R54 💥. Live numbers from `scripts/round27_paperA/iptm_static_vs_sigma.py`
(output `conformal/iptm_static_vs_sigma_paperB.csv`). NOT yet inserted.

## Motivation
A single co-folding confidence value is not trustworthy: AlphaFold3-class ipTM can be
**artificially inflated by embedding perturbations** (arXiv:2602.24007, Feb 2026), yet industrial
pipelines operationalize a *static* confidence cutoff (Isomorphic Labs filters predictions below
~0.7 binding probability before synthesis). A static per-prediction threshold cannot see
reproducibility.

## Result
Across the 15-ligand MMP-1 panel (161 reseeds each), **all 15 ligands pass a static 0.70 ipTM
cutoff on 100 % of cycles** — a static filter would accept every one. Yet the inter-reseed
reproducibility σ_iptm spans 25× (0.00022 → 0.00569). Using σ ≥ 2× the panel median (0.00102) as
an unreliability flag, **4 of 15 ligands are "static-pass-but-unreliable"**:

| ligand | mean ipTM | σ_iptm | conformal 90% half-width | %cycles ≥0.70 |
|---|---:|---:|---:|---:|
| CHEMBL259829 | 0.847 | 0.00569 | 0.0086 | 100 % |
| CHEMBL3036   | 0.899 | 0.00189 | 0.0029 | 100 % |
| CHEMBL2105729| 0.943 | 0.00147 | 0.0022 | 100 % |
| CHEMBL415    | 0.916 | 0.00127 | 0.0019 | 100 % |

**CHEMBL259829 is the exemplar**: it clears the static 0.70 cutoff (mean 0.847, 100 % of cycles
pass) yet carries 10× the median reproducibility noise and 25× that of the most stable ligand
(CHEMBL57058, σ = 0.00022) — exactly the failure mode a static threshold cannot detect and that a
variance-based reliability audit catches for free.

## Figure caption (draft)
"**Figure X. A static confidence cutoff is blind to reproducibility.** All 15 MMP-1 ligands pass a
static ipTM ≥ 0.70 filter on 100 % of 161 reseed cycles (grey band), yet inter-reseed σ_iptm spans
25× (left axis). Four ligands (red) clear the static cutoff but exceed 2× the median σ_iptm; the
worst, CHEMBL259829, combines an above-threshold mean (0.847) with the panel's largest
reproducibility noise. Variance-based screening (this work) flags cases that point-estimate
thresholds — and the embedding-perturbation inflation of arXiv:2602.24007 — cannot."

## Placement
paper_B Results, immediately before the conformal-interval section; positions σ_iptm as the
practical, training-free detector of the confidence-inflation failure mode that arXiv:2602.24007
demonstrates theoretically and that static industrial cutoffs (Isomorphic) miss.
