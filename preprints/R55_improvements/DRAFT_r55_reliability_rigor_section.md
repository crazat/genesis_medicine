# DRAFT — R55 reliability-rigor additions (manuscript-ready, English)

Live numbers from r55_*.py (outputs in this dir). NOT yet inserted into manuscripts.
Three compute-now results that close the "is σ real, and is it trustworthy?" gap.

## A. The numerical floor is zero — σ_E is genuine signal (paper_A)
To exclude the possibility that the reported reseed dispersion σ_E reflects floating-point /
thread-reduction-order non-determinism rather than genuine conformer/seed variation, we ran a
controlled numerical-floor experiment: GFN2-xTB single-point on a *fixed* conformer
(CHEMBL259829) repeated 12× at OMP_NUM_THREADS = 1 and 12× at = 8. The total energy was
**bitwise identical across all 24 runs (σ = 0.000 Eh at both thread counts; −71.1141816431 Eh)**,
i.e. the numerical/threading floor is below the SCF convergence threshold (~1×10⁻⁷ Eh =
6.3×10⁻⁵ kcal·mol⁻¹). Since the per-cell reseed σ_E we report spans 15–100 kcal·mol⁻¹ — six to
seven orders of magnitude above this floor — **100 % of σ_E is genuine conformer/seed signal**,
not numerical artifact. This pre-empts the reviewer objection that semiempirical reproducibility
spread could be a hardware/FP non-determinism floor.

## B. The σ_iptm reseed ensemble is well-calibrated (paper_B)
We applied forecast-verification scoring rules (weather-ensemble methodology; Gneiting & Raftery
2007; Hamill 2001) to the 161-cycle σ_iptm reseed ensembles, treating raw σ — which is not a
proper score — as only a starting point. A pooled leave-one-out **rank (Talagrand) histogram is
flat** (bins 240–256 over n = 2,415), and the **spread–skill ratio = 0.997** (1.0 = ideally
dispersed), establishing that the reseed dispersion is neither over- nor under-confident: the
ensemble spread is the statistically correct size to serve as an error bar, and the reseed
cycles are exchangeable with no infrastructure drift. The strictly-proper **CRPS** preserves the
per-ligand reliability ordering (CHEMBL259829 worst, 0.0032; CHEMBL57058 best, 0.00012),
upgrading the bare-σ ranking to a proper-scoring-rule footing.

## C. Structure partially predicts reliability — toward a predictive σ (both papers)
A proof-of-concept structure→σ correlation (RDKit descriptors vs measured σ, n = 15 ligands)
shows σ_E is moderately predicted by H-bonding / polarity / flexibility descriptors —
**H-bond donors ρ = 0.61, H-bond acceptors 0.55, TPSA 0.49, rotatable bonds 0.46** (Spearman) —
while σ_iptm is only weakly structure-predictable at this sample size (max |ρ| = 0.33). This
motivates a full "Error Model" meta-regressor (cf. *J Chem Inf Model* 2026, PMC12848971) trained
on the 140-ligand SAR set (or the carbonic-anhydrase 2nd-target extension), which would convert
descriptive reseed σ into a one-shot *predicted* reliability score and, via SHAP/counterfactual
attribution, name the substructures that drive unreliability — a prospective third contribution.

## Placement
- A → paper_A Methods/SI ("numerical-floor control") + one sentence in §4.10/§4.11 reliability discussion.
- B → paper_B §3.7/§3.8 neighbourhood (calibration certificate for the reseed σ).
- C → paper_B/§paper_A future-work + the platform/CA generalization narrative.
Deferred GPU/MD extensions (Boltz FP32 arm; AFsample2/PLACER/Open-BPMD metastability) in PLAN_deferred_gpu_md.md.
