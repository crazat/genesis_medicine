# DRAFT — Multiverse / Generalizability-Theory reframe (manuscript-ready, English)

R54 #1. Live numbers from `scripts/round27_paperA/multiverse_gtheory_analysis.py`
(outputs in `preprints/23_paper_A_v6.../conformal/`). NOT yet inserted into manuscripts.

## Methods

We frame the sept-matrix — every compound evaluated under three semiempirical Hamiltonians
(GFN0/1/2) × {single-point, optimization, Hessian-thermo} × two implicit-solvation models
(GBSA/ALPB), repeated over independent reseed cycles — as a formal **multiverse / specification
curve** (Steegen et al., *Perspect. Psychol. Sci.* 2016; Simonsohn et al., *Nat. Hum. Behav.*
2020; ML analogue Bell et al., NeurIPS 2022). Each axis is an analytical degree of freedom; the
full grid is the specification space and the per-cell reseed standard deviation σ is the
within-specification noise. To our knowledge this is the **first transfer of multiverse analysis
into computational chemistry**, importing a methodology matured in psychology and neuroimaging.

We decompose the variance of the computed quantity with first-order functional-ANOVA indices
(Generalizability-Theory variance components; Cronbach; bootstrap CIs per Li, *PLoS One* 2023),
distinguishing repeatability (reseed) from reproducibility (method facets) in the metrological
sense (ASTM E691 / Gauge R&R).

## Results — paper_A (semiempirical free energy)

The Hamiltonian is the dominant analytical degree of freedom: GFN0/1/2 are distinct methods whose
**absolute total energies are not on a common scale**, so they must never be mixed (≈97 % of the
raw within-compound variance is the inter-Hamiltonian offset). The informative decomposition is
therefore *within a fixed Hamiltonian*, where all choices are commensurate. There, of the residual
free-energy variance (pooled SD ≈ 37 kcal·mol⁻¹):

| Facet (within fixed Hamiltonian) | Variance share |
|---|---:|
| reseed / conformer stochasticity | **84.0 %** |
| solvent (23 choices)             | 1.2 % |
| solvation model (GBSA/ALPB)      | 0.4 % |
| interactions + higher order      | 14.5 % |

**The reseed/conformer term is the overwhelming residual uncertainty once a Hamiltonian is fixed,
while solvent and solvation-model choice are minor (<2 % combined).** This is the quantitative
justification for treating σ_E (reseed reproducibility) as *the* per-method reliability metric:
the dominant irreducible noise is stochastic sampling, not the solvent-model degree of freedom.
The specification curve (117 cells) ranks reliability from most reliable
(GFN0/ALPB/nitromethane, mean σ_E = 15.3 kcal·mol⁻¹) to least
(GFN1/ALPB/methanol, mean σ_E = 40.3 kcal·mol⁻¹).

## Results — paper_B (co-folding confidence)

Treating ligand × reseed as a one-way random-effects design, the between-ligand signal vastly
exceeds reseed noise: σ²(ligand) = 1.39×10⁻³ vs σ²(reseed) = 2.79×10⁻⁶, giving a single-reseed
intraclass reliability **ICC = 0.998** and a generalizability coefficient G ≈ 1.000 over the
realized 161 reseeds; the D-study shows **a single Boltz reseed already attains G ≥ 0.99** for the
*aggregate ligand ranking*. The decisive point: precisely *because* the aggregate ranking is
near-perfectly reproducible, the scientifically meaningful signal is the **per-ligand
heterogeneity of σ_iptm** — a small subset of ligands (e.g. CHEMBL259829) carries 8–25× the
reproducibility noise of the most stable ligands and is invisible at the aggregate level. This
mirrors and sharpens the Wan/Coveney "aggregate-reliable but individually variable" finding:
generalizability theory shows the aggregate is essentially perfect, so a per-ligand variance
audit is the only place reliability information remains.

## Positioning
- First multiverse-analysis framing in comp-chem (novelty hook, intro + discussion).
- G-theory gives a single citable reliability coefficient + a D-study answering "how many reseeds."
- Defends every multiplicity/dependence/optional-stopping objection when combined with the
  SDMA dependence adjustment (Lefort-Besnard 2025), minP/e-value multiplicity control
  (Hoffmann 2024), and anytime-valid confidence sequences (Ramdas/Grünwald) for adaptive reseed stopping.
- Pairs with the conformal layer: conformal gives coverage-calibrated intervals; G-theory gives
  variance attribution + the D-study reseed budget.
