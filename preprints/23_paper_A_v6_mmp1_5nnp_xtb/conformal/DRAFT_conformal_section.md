# Conformal reliability layer — manuscript-ready draft (English)

Generated 2026-05-29 (R53 priority #1). Shared text for paper_A (σ_E) and paper_B (σ_iptm).
Numbers are live from `conformal_reliability_layer.py` on the unified v143–v303 (paper_B) /
v212–v303 (paper_A) reseed datasets. NOT yet inserted into manuscripts — review first.

---

## Methods — Conformal reliability intervals

For each prediction unit *u* (paper_B: a ligand; paper_A: a (ligand × GFN-Hamiltonian ×
solvation-model × solvent) cell) we treat the *m_u* independent reseed cycles as exchangeable
draws and construct a distribution-free prediction interval using **normalized split-conformal
prediction** (Lei et al., *JASA* 2018; locally-adaptive variant). Each unit's cycles are
randomly partitioned into training, calibration, and test folds (40/40/20). The unit mean
μ_u and standard deviation s_u are estimated on the training fold; the studentized
nonconformity score r = |x − μ_u| / s_u is evaluated on the calibration fold and pooled across
all units. The conformal threshold q̂ is the ⌈(n_cal+1)(1−α)⌉ / n_cal empirical quantile of
the pooled scores, giving the interval [μ_u − q̂ s_u, μ_u + q̂ s_u] with a finite-sample
marginal coverage guarantee of 1−α. Coverage was validated by 200 independent random
splits; final per-unit intervals use all available cycles. The procedure requires no
distributional assumption and adds no new computation — it reuses the existing reseed cascade.

## Results — the σ-axis becomes a coverage-calibrated reliability interval

The conformal layer converts the raw reseed standard deviation σ into a prediction interval
whose empirical coverage matches its nominal level almost exactly across both modalities
(200-split validation):

| Nominal | paper_B σ_iptm (15 ligands) | paper_A σ_E (1,755 cells, kcal·mol⁻¹) |
|--------:|:---------------------------:|:-------------------------------------:|
| 80 %    | 79.88 % ± 2.15 %            | 79.97 % ± 0.22 %                      |
| 90 %    | 89.93 % ± 1.72 %            | 89.98 % ± 0.16 %                      |
| 95 %    | 95.11 % ± 1.19 %            | 95.01 % ± 0.11 %                      |

The conformal threshold is q̂ = 1.52 (σ_iptm) and q̂ = 1.50 (σ_E) at 90 % — *below* the
Gaussian 1.645·σ — indicating the reseed distributions are light-tailed and that the interval
is, if anything, tighter than a normality assumption would yield while retaining valid
coverage. The interval half-width q̂·s_u inherits the per-unit reliability ordering established
by σ: for σ_iptm the least-reliable ligand is CHEMBL259829 (half-width 0.0086 at 90 %) and the
most reliable is CHEMBL57058 (0.00034), a 25× spread; for σ_E the widest cell is
CHEMBL257077 (GFN1/ALPB/phenol, ±149 kcal·mol⁻¹). Crucially, an outlier is now defined not by
an arbitrary σ cut-off but by whether its calibrated interval crosses a decision-relevant
threshold at a stated confidence — a reproducible, defensible reliability criterion.

## Positioning / impact framing

These two analyses are the empirical, statistically-powered extension of the
"ensembles-not-single-shots / actionable reproducibility" doctrine (Coveney & Wan, OUP 2025)
into two prediction modalities that have not previously been treated this way: semiempirical-QM
free energies (paper_A) and deep-learning co-folding confidence (paper_B). By delivering
*guaranteed-coverage* reliability intervals rather than point estimates or uncalibrated
variances, the framework supplies precisely the uncertainty quantification required by the
emerging regulatory credibility frameworks for in-silico evidence — the FDA draft guidance
"Considerations for the Use of AI to Support Regulatory Decision-Making for Drug and Biological
Products" (Jan 2025; risk-based context-of-use + model-credibility + UQ) and the EMA reflection
paper on AI in the medicinal-product lifecycle (Sep 2024) — expressed in the verification,
validation and uncertainty-quantification (VVUQ / ASME V&V-40) vocabulary those frameworks use.
In this framing σ_E and σ_iptm are *aleatoric* (seed/conformer-sampling) reproducibility axes,
distinct from the *epistemic* (out-of-distribution-compound) axis, and the dual-axis outlier
set becomes the high-aleatoric subset flagged for physics-based rescue.

## Suggested placement
- paper_A: new SI subsection + one Results paragraph; cite Lei 2018, FDA-2025, EMA-2024, ASME V&V-40.
- paper_B: §4.3 / Discussion; same citations + Coveney-Wan 2025 book as the doctrinal anchor.
- Optional venue lane this opens: COPA-2026 (Conformal Prediction conf.) / JCIM UQ cluster.

## Reproducibility
`scripts/round27_paperA/conformal_reliability_layer.py` (seed 20260529, 200 splits).
Outputs: `conformal_sigma_iptm_paperB.csv`, `conformal_sigma_e_paperA.csv`,
`conformal_coverage_validation.txt`. No GPU; reads existing reseed CSVs only.
