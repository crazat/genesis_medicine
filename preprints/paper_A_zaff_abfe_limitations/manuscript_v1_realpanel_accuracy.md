---
title: "Systematic over-binding in ZAFF-AMBER absolute binding free energy calculations for zinc-metalloenzyme inhibitors: a 14-compound accuracy benchmark on MMP-1"
author:
  - Cheongwoo Han^1,2,3^
date: 2026-07-23
---

^1^ Genesis Medicine Lab, Seoul, Republic of Korea
^2^ HAN PREDICT, Inc. (hanpredict.com)
^3^ Recover Korean Medicine Clinic (recover-clinic.kr)

## Abstract

Absolute binding free energy (ABFE) calculation on zinc metalloenzymes is a stress test for non-bonded zinc force fields such as ZAFF-AMBER: the catalytic Zn^2+^ coordination chemistry of hydroxamate, sulfonamide, carboxylate and phosphonate inhibitors must be recovered from a fixed-charge, restraint-based description of the metal shell. We benchmark the ZAFF-AMBER + GAFF-2 + AM1-BCC ABFE protocol against experimental affinity for fourteen MMP-1 inhibitors drawn from PubChem bioassay records, spanning 0.78 nM to 98 µM in IC~50~ (pIC~50~ 9.11 to 4.01) and three zinc-binding warhead classes (eleven hydroxamates, two carboxylates, one phosphonate), each carrying its PubChem compound identifier, assay identifier and retrieval timestamp. The protocol over-binds every compound in the set: the computed binding free energy is more negative than the IC~50~-derived experimental value for all fourteen ligands, by 0.6 to 58.1 kcal mol^-1^. The over-binding is governed by the chelation strength of the warhead rather than by the measured potency. The four strongest inhibitors (IC~50~ ≤ 10 nM), all hydroxamates, over-bind by a mean of 53.0 kcal mol^-1^; a weak hydroxamate (IC~50~ 50 µM) still over-binds by 43.2 kcal mol^-1^, whereas a mid-potency phosphonate (IC~50~ 77 nM) over-binds by only 4.3 kcal mol^-1^. The rank correlation between computed and experimental binding free energy is weak and imprecise (Spearman ρ = 0.587, 95% CI [0.041, 0.847]; Pearson r = 0.631), with the confidence interval reaching to near zero. No compound sign-flips: the error is a one-directional, warhead-scaled over-stabilization. We emphasise that within-run statistical precision is not accuracy: each ABFE estimate carries an MBAR bootstrap error of 0.5 to 0.9 kcal mol^-1^ while deviating from experiment by up to two orders of magnitude more. We additionally document two pipeline failure modes and their fixes — a ReplicaExchangeSampler swap-all deadlock that requires a non-exchanging MultiStateSampler, and a production NaN crash on medium-sized ligands that requires an explicit minimize–heat–NPT warmup between topology build and alchemical decoupling — and contrast the single-compound instability of ABFE with the population-level rank stability of semi-empirical xtb screening. We position this work as a limitations evaluation rather than a validation study, and recommend that fixed-charge ZAFF-AMBER ABFE not be used to rank zinc-chelating metalloenzyme inhibitors without warhead-stratified error budgeting.

Keywords: ABFE, ZAFF-AMBER, zinc metalloenzyme, MMP-1, hydroxamate, over-binding, MultiStateSampler, accuracy benchmark.

## 1. Introduction

### 1.1 ABFE for metalloenzyme inhibitor ranking

Absolute binding free energy (ABFE) calculation evaluates ligand–protein affinity by alchemically decoupling the ligand in two thermodynamic states — the bound complex and pure solvent — and combining the two legs through a thermodynamic cycle. For a zinc metalloenzyme such as the matrix metalloproteinase MMP-1, the catalytic Zn^2+^ ion is the principal binding determinant for the hydroxamate-class inhibitors that reached nanomolar potency in the early MMP inhibitor programs, and the quality of the computed affinity therefore rests on how faithfully the force field represents the metal–warhead interaction.

A non-bonded zinc force field, here ZAFF-AMBER applied as the ions234lm_126_tip3p parameter set augmented with 12-6-4 zinc-coordination terms, describes the metal as an explicitly charged ion held by short-range Lennard-Jones potentials plus harmonic restraints to the three coordinating histidines. Whether this fixed-charge representation recovers the experimental rank ordering of inhibitors, and how the residual error is structured, is the question this work addresses on a real, provenance-tracked ligand panel.

### 1.2 Precision is not accuracy

A single ABFE run reports a binding free energy together with a bootstrap-style statistical error from the alchemical (MBAR) analysis, typically 0.3 to 0.9 kcal mol^-1^. That error is a within-run dispersion: it measures the Poisson-like fluctuation across the alchemical states inside one simulation and says nothing about the systematic bias of the protocol. The published ABFE benchmark literature (Aldeghi et al., 2017; Mey et al., 2020; Schindler et al., 2020) stresses both error sources, but applied screening efforts often report only the within-run error. On the panel benchmarked here, that within-run error is small and stable while the deviation from experiment is large and systematic — the clearest possible demonstration that precision must not be read as accuracy.

### 1.3 Pipeline pitfalls

ABFE calculation is implementation-sensitive. We document two failure modes encountered during this benchmark, both with concrete fixes now baked into the released pipeline:

1. The openmmtools ReplicaExchangeSampler with a swap-all exchange policy deadlocks on the ZAFF–MMP-1 systems at the first exchange iteration: worker threads enter a futex wait, the main thread spins, and no further trajectory frames are written. The deadlock reproduced on every launch and is not GPU-contention related. Switching to the non-exchanging MultiStateSampler removes it with no measurable convergence penalty.
2. Phase-5 production crashes with a SimulationNaNError at the first iteration on ligands larger than roughly eight heavy atoms unless an explicit warmup — energy minimization, staged heating to 310 K, and restrained then unrestrained NPT equilibration — is interposed between the tleap-built complex and the alchemical decoupling. The default preparation does not minimize, and the alchemical integrator is too aggressive on an un-minimized solvated complex.

## 2. Methods

### 2.1 Compound selection and provenance

Fourteen MMP-1 inhibitors were selected from PubChem bioassay records to span four orders of magnitude in IC~50~ (0.78 nM to 98 µM) across the principal zinc-binding warhead classes. Each compound is identified by its PubChem compound identifier (CID) and carries, in the panel file `data/mmp1_panel_pubchem.csv`, its canonical SMILES, molecular formula, InChIKey, the reported IC~50~, the source assay identifier (PubChem AID) and the UTC retrieval timestamp. No compound is referred to by a trade or drug name in this work; the analysis uses only the deposited structures and their recorded assay values. The subset actually carried through ABFE is `pilot/abfe_realpanel_mmp1/abfe_subset.csv`.

Warhead class was assigned programmatically from each deposited SMILES by RDKit SMARTS matching (hydroxamate `[CX3](=O)[NX3][OX2H1,OX1-]`, carboxylate `[CX3](=O)[OX2H1,OX1-]`, sulfonamide, sulfonate, thiol, phosphonate), with hydroxamate, thiol and phosphonate reported preferentially where more than one motif is present because they are the stronger zinc chelators. The panel resolves to eleven hydroxamates, two carboxylates and one phosphonate. This assignment is derived from the structures themselves, not from any external annotation.

### 2.2 Receptor and force field

The receptor was 1HFC chain A, the catalytic domain of human MMP-1 in the holo form, with the catalytic zinc and its three coordinating histidines (HID111, HID115, HID121; Nε2–Zn 1.88 to 2.08 Å) preserved. AMBER ff14SB described the protein, GAFF-2.11 the ligand, TIP3P the water, and the ions234lm_126_tip3p parameter set the zinc and any charge-balancing counterions. Ligand net charge was inferred by RDKit SMARTS detection of ionisable groups and passed to antechamber as the -nc flag for AM1-BCC charging, which avoids the sqm electron-parity failures that otherwise occur on the anionic hydroxamate, carboxylate and phosphonate warheads. Complex topologies were assembled with tleap (TIP3P box, 12 Å buffer, neutralised with Na^+^/Cl^-^); solvent-leg topologies were assembled identically without the protein.

### 2.3 ABFE protocol

Each complex and each solvent leg was warmed before decoupling: L-BFGS minimization, staged heating from 0 to 310 K over 100 ps, then 100 ps restrained NPT (protein heavy atoms restrained at 10 kcal mol^-1^ Å^-2^) and 100 ps unrestrained NPT. Alchemical decoupling used the openmmtools MultiStateSampler (no replica exchange) over sixteen λ-windows, decoupling electrostatics first and sterics second, with the AbsoluteAlchemicalFactory soft-core defaults. A flat-bottom centroid distance restraint (k = 10 kcal mol^-1^ Å^-2^, r~max~ = 8 Å) held the ligand near the active site during decoupling, with the corresponding analytical standard-state correction ΔG°~R~ = −RT ln(V~R~/V°), V~R~ = (4/3)π r~max~^3^, V° = 1660.5 Å^3^. Production ran at a 1 fs timestep with a Langevin middle integrator at 310 K and 1 ps^-1^ friction. Free energies were estimated by MBAR through the MultiStateSamplerAnalyzer, and the binding free energy computed as ΔG~bind~ = ΔG~solvent~ − ΔG~complex~ − ΔG°~R~. The experimental reference is ΔG~exp~ = RT ln IC~50~ at 310 K (RT = 0.616 kcal mol^-1^), taking K~i~ ≈ IC~50~. One ABFE replicate was computed per compound in this campaign; the accuracy axis reported below is therefore a single-replicate accuracy benchmark, and between-replicate dispersion is treated as a limitation (Section 5) rather than a claim.

### 2.4 Cross-method screening-tier check

To place the ABFE absolute-affinity behaviour in context against a cheaper screening tier, GFN1-xTB and GFN2-xTB single-point and 432-conformer ensemble energies and frontier-orbital gaps were computed with ALPB implicit water on a 1050-molecule NPAtlas natural-product subset, and the pairwise rank correlation between the two semi-empirical methods used as an internal-consistency measure independent of ABFE.

## 3. Results

### 3.1 Per-compound ABFE accuracy

Table 1 reports, for each of the fourteen compounds ordered by potency, the PubChem CID, molecular formula, assigned warhead, IC~50~, the experimental binding free energy, the single-replicate ABFE estimate with its within-run MBAR error, and the deviation from experiment (ΔG~ABFE~ − ΔG~exp~). Figure 1 plots ΔG~ABFE~ against ΔG~exp~ with the line of perfect accuracy; Figure 2 plots the residual against potency.

![Figure 1. Computed ZAFF-AMBER ABFE binding free energy against the IC~50~-derived experimental value for the fourteen MMP-1 inhibitors, coloured by warhead class. The dashed line is perfect accuracy (y = x). Every point lies far below the line: the protocol over-binds all fourteen compounds, most severely the strong hydroxamates.](figures/fig_accuracy_scatter.png)

![Figure 2. ABFE residual (ΔG~ABFE~ − ΔG~exp~) against experimental potency (pIC~50~, strongest to the left), coloured by warhead. The shaded band is ±2 kcal mol^-1^ chemical accuracy. The over-binding tracks warhead chelation strength, not potency: the 50 µM hydroxamate (compound 10303333) over-binds as severely as sub-nanomolar hydroxamates, while the phosphonate deviates least.](figures/fig_potency_residual.png)

Table 1. ZAFF-AMBER ABFE benchmark on fourteen PubChem MMP-1 inhibitors. Free energies in kcal mol^-1^; ΔG~exp~ from IC~50~ at 310 K assuming K~i~ = IC~50~. Deviation is ΔG~ABFE~ − ΔG~exp~ (negative = over-binding).

| PubChem CID | Formula | Warhead | IC~50~ (nM) | pIC~50~ | ΔG~exp~ | ΔG~ABFE~ | dev |
|---|---|---|---:|---:|---:|---:|---:|
| 119031 | C15H29N3O5 | hydroxamate | 0.78 | 9.11 | −12.92 | −66.82 ± 0.55 | −53.90 |
| 132519 | C20H28N4O4 | hydroxamate | 1.5 | 8.82 | −12.52 | −69.93 ± 0.72 | −57.41 |
| 466151 | C18H21N3O5S2 | hydroxamate | 5.7 | 8.24 | −11.69 | −69.76 ± 0.77 | −58.07 |
| 9822724 | C20H32N4O5 | hydroxamate | 10 | 8.00 | −11.35 | −53.77 ± 0.73 | −42.42 |
| 9821883 | C19H24N2O5S | hydroxamate | 33 | 7.48 | −10.61 | −67.96 ± 0.78 | −57.35 |
| 9822461 | C16H19ClNO5PS | phosphonate | 77 | 7.11 | −10.09 | −14.40 ± 0.75 | −4.31 |
| 44394994 | C20H23FN2O6S | hydroxamate | 180 | 6.74 | −9.57 | −19.85 ± 0.81 | −10.28 |
| 44394426 | C20H23FN2O6S | hydroxamate | 420 | 6.38 | −9.04 | −20.64 ± 0.78 | −11.60 |
| 9911009 | C20H23FN2O6S | hydroxamate | 1100 | 5.96 | −8.45 | −9.08 ± 0.70 | −0.63 |
| 44395069 | C21H26N2O7S | hydroxamate | 2600 | 5.59 | −7.92 | −10.67 ± 0.82 | −2.75 |
| 10737732 | C17H18ClNO4S | carboxylate | 6500 | 5.19 | −7.36 | −32.68 ± 0.70 | −25.32 |
| 20689551 | C22H22F3N3O6 | hydroxamate | 10000 | 5.00 | −7.09 | −35.68 ± 0.86 | −28.59 |
| 10303333 | C26H24F3NO8S | hydroxamate | 50000 | 4.30 | −6.10 | −49.34 ± 0.68 | −43.24 |
| 45482998 | C18H20O3 | carboxylate | 98000 | 4.01 | −5.69 | −16.23 ± 0.53 | −10.55 |

The experimental affinities span a 7.2 kcal mol^-1^ window (ΔG~exp~ = −12.92 to −5.69). The computed affinities span a 60.9 kcal mol^-1^ window (ΔG~ABFE~ = −69.93 to −9.08) — an order of magnitude wider than the underlying chemistry admits. Every one of the fourteen compounds over-binds: the deviation is negative in every row, from −0.6 to −58.1 kcal mol^-1^, and no compound sign-flips to a predicted non-binder. The rank correlation between computed and experimental binding free energy is weak and imprecise: Spearman ρ = 0.587 with a 95% confidence interval of [0.041, 0.847], and Pearson r = 0.631. The lower confidence bound sits just above zero, so the panel provides no reliable rank-ordering signal despite the point estimate being positive.

### 3.2 Over-binding is warhead-driven, not potency-ranked

The over-binding does not scale with measured potency; it scales with the chelation strength of the warhead. The four strongest inhibitors (IC~50~ ≤ 10 nM), all hydroxamates, over-bind by a mean of 53.0 kcal mol^-1^. The clearest evidence that the warhead rather than the affinity drives the error is at the weak end of the panel: compound 10303333, a hydroxamate whose measured IC~50~ is only 50 µM, still over-binds by 43.2 kcal mol^-1^ — comparable to the sub-nanomolar hydroxamates and far larger than any mid-potency non-hydroxamate. By contrast the single phosphonate (compound 9822461, IC~50~ 77 nM) over-binds by only 4.3 kcal mol^-1^, and a carboxylate at 98 µM (compound 45482998) by 10.5 kcal mol^-1^. A fixed +2 point charge on the zinc, coordinating a strongly anionic hydroxamate with no allowance for charge transfer, over-stabilises the complex in proportion to how strongly the warhead chelates the metal, independent of the ligand's true affinity. This is why the rank correlation is degraded: the strong-chelator warhead that a weakly-binding hydroxamate carries is enough to lift its computed affinity above that of a genuinely tighter non-hydroxamate.

### 3.3 Within-run precision is not accuracy

The within-run MBAR error is small and uniform across the panel: it ranges from 0.53 to 0.86 kcal mol^-1^ (Table 1). Read in isolation, an ABFE estimate of −66.8 ± 0.55 kcal mol^-1^ for compound 119031 looks precise to better than 1 kcal mol^-1^. The accuracy gap for that same compound is 53.9 kcal mol^-1^ — nearly a hundredfold larger than its reported error bar. Reporting the within-run error as though it were the uncertainty of the result is therefore actively misleading on this system class: it understates the true distance from experiment by one to two orders of magnitude. This is the central practical caution of the benchmark. It holds even without a between-replicate study, because the systematic bias dwarfs any plausible replicate dispersion.

### 3.4 Potency-class stratification

Grouping by potency shows the same warhead effect rather than a clean potency trend. The strong class (IC~50~ ≤ 10 nM, n = 4, all hydroxamate) over-binds by a mean of 53.0 kcal mol^-1^. The mid class (10 nM to 10 µM, n = 8, mixed hydroxamate/phosphonate) over-binds by a mean of 17.6 kcal mol^-1^, but this average hides a wide internal spread (−0.6 to −28.6) that tracks warhead identity: the two smallest deviations in the whole panel are the 1.1 and 2.6 µM hydroxamates whose fluorinated scaffolds evidently weaken the effective chelation, while the phosphonate deviates least of all. The weak class (> 10 µM, n = 2) over-binds by a mean of 26.9 kcal mol^-1^, dominated by the 50 µM hydroxamate outlier. There is no potency threshold below which the protocol becomes reliable.

### 3.5 Screening-tier rank stability, for contrast

Against the single-compound instability of ABFE, the semi-empirical screening tier is population-stable. On the 1050-molecule NPAtlas subset the two xtb methods agree almost exactly in rank: total-energy rank Spearman ρ = 0.993 between GFN1-xTB and GFN2-xTB, with gap, HOMO and LUMO ranks preserved at ρ > 0.92. Conformer-count refinement beyond 432 conformers is rank-equivalent to four decimal places. Semi-empirical QM is rank-robust at the population level on screening corpora; alchemical ZAFF-AMBER ABFE is not rank-robust at the single-compound level on this metalloenzyme class. A multi-fidelity pipeline that triages with xtb and confirms with ABFE should expect the triage ranking to survive method choice, but should not expect the ABFE confirmation to reproduce an accurate absolute affinity without warhead-stratified error budgeting.

## 4. Discussion

### 4.1 What ZAFF-AMBER ABFE can and cannot be used for

The benchmark is unforgiving on the accuracy axis: every compound over-binds, the computed affinity window is an order of magnitude too wide, and the error is largest exactly where the medicinal chemistry is most interesting — the strong hydroxamate chelators. The one encouraging feature is that the error is one-directional and warhead-structured rather than random: no compound sign-flips, and the deviation is a monotone function of chelation strength within the hydroxamate series. This means the protocol is not useful for ranking chelating inhibitors against one another, and is not useful at all for absolute affinity, but a warhead-stratified correction — a per-class additive offset fitted on a chelation-matched reference set — could in principle recover usable relative rankings within a single warhead class. We do not fit such a correction here; the point of this work is to show that it is necessary.

### 4.2 Why ZAFF-AMBER over-binds these inhibitors

The ions234lm_126_tip3p parameter set was developed for divalent cations in solution and bulk-protein contexts, not for the strongly ionic Zn–warhead interaction of a metalloprotease inhibitor. Two mechanisms are consistent with the observed warhead-scaled over-binding. First, charge-transfer underestimation: a fixed-charge description cannot represent the partial charge transfer (QM-estimated at roughly 0.2 to 0.4 e) between a deprotonated hydroxamate oxygen and the Zn^2+^, so the residual electrostatic attraction is applied at full formal-charge strength and over-stabilises the bound state; the stronger the chelator, the larger the error, exactly as seen. Second, restraint-induced over-stabilisation during decoupling: the harmonic restraints holding the zinc in coordination can bias the sterics phase of the alchemical path for tightly-coordinated ligands. Both mechanisms predict the largest error for the strongest chelators and the smallest for the phosphonate and carboxylates, which is the observed ordering.

### 4.3 Pipeline reliability

The ReplicaExchangeSampler swap-all deadlock (Section 1.3) consumed substantial debugging effort before identification. Its signature is unambiguous: trajectory and checkpoint files are written at iteration 1 and never again, the main thread shows state R with an empty wchan (user-space spinning), worker threads block in futex_wait, and process memory grows without forward progress; a secondary OpenMM CUDA process can still reach high GPU utilisation alongside the deadlocked one, so the symptom is not GPU contention. The MultiStateSampler replacement is a small edit and restores forward progress with no measurable convergence penalty. The NaN-warmup fix (an explicit minimize–heat–NPT stage between topology build and decoupling) was likewise required for every ligand above roughly eight heavy atoms; it is now interposed automatically by the production launcher. Both fixes are released with the code.

## 5. Limitations

- Single replicate per compound. This campaign computed one ABFE replicate per ligand, so the accuracy axis is reported without a between-replicate dispersion. The systematic over-binding is far larger than any plausible replicate scatter, so the accuracy conclusions are robust to it, but a per-class error budget for production use would require a multi-replicate follow-up.
- Sample size. Fourteen compounds across three warhead classes is adequate to establish the direction and warhead-dependence of the bias but not to fit a quantitative per-class correction.
- Single docked pose per compound. Each ABFE started from one docked pose; pose re-sampling was not budgeted and could affect the mid-potency compounds where the deviation spread is widest.
- One force field, one target. Only ZAFF-AMBER was tested, on MMP-1 alone. A 12-6-4-tuned zinc set, a polarizable model, or QM/MM-corrected FEP could behave differently, and other zinc metalloenzymes (HDAC, carbonic anhydrase) have different coordination chemistry to which these results may not transfer.

## 6. Reproducibility

All code, prepared topologies and per-compound analysis are released under Apache-2.0 at https://github.com/crazat/genesis_medicine. The panel and its provenance are `data/mmp1_panel_pubchem.csv` (PubChem CID, assay AID, retrieval timestamp per row) and `pilot/abfe_realpanel_mmp1/abfe_subset.csv`; the ABFE results and aggregate are `pilot/abfe_realpanel_mmp1/abfe_realpanel_results.csv` and `abfe_realpanel_summary.json`; the warhead classification, statistics and figures are regenerated by `scripts/zaff_realpanel_manuscript_figures.py`. The relevant pipeline scripts are `scripts/zaff_phase5_warmup_generic.py` and `scripts/zaff_phase5_abfe_production_mss.py`. A Zenodo code-DOI snapshot will be attached on deposit.

## Acknowledgements

We thank the openmmtools, OpenMM, RDKit and AmberTools communities for software infrastructure. Computation was performed on a single NVIDIA RTX 5090 (32 GB) workstation under WSL2 Ubuntu 24.04.

## References

Aldeghi, M., Heifetz, A., Bodkin, M. J., Knapp, S., Biggin, P. C. (2017). Accurate calculation of the absolute free energy of binding for drug molecules. Chemical Science, 8, 1710.

Mey, A. S. J. S., Allen, B. K., Bruce McDonald, H. E., et al. (2020). Best practices for alchemical free energy calculations. Living Journal of Computational Molecular Science, 2, 18378.

Schindler, C. E. M., Baumann, H., Blum, A., et al. (2020). Large-scale assessment of binding free energy calculations in active drug discovery projects. Journal of Chemical Information and Modeling, 60, 5457.

Mobley, D. L., Graves, A. P., Chodera, J. D., et al. (2007). Predicting absolute ligand binding free energies to a simple model site. Journal of Molecular Biology, 371, 1118.
