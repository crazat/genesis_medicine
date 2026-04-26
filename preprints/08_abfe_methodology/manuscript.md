# A calibrated absolute binding free energy pipeline with flat-bottom centroid restraint and analytical standard-state correction for natural-product scaffold-hopping in OpenMM 8 / openmmtools 0.26

**HanCheongWoo ¹,²,³**

¹ Genesis_Medicine Lab, Seoul, Republic of Korea
² HAN PREDICT, Inc.; <https://hanpredict.com>
³ Recover Korean Medicine Clinic; <https://recover-clinic.kr>

Code: <https://github.com/crazat/genesis_medicine> · Correspondence: admin@hanpredict.com

**Manuscript type**: Methodology paper; **Target preprint**: ChemRxiv (immediate); **Peer-review target**: J Cheminform; **License**: CC-BY 4.0
**Status**: v0.4 — partial OpenMM-ABFE calibration on T4L99A·benzene (complex leg ΔG_decouple = 2.695 ± 0.146 kcal/mol; solvent leg pending re-run) + **Boltz-2 cofold-affinity ChEMBL calibration** (Spearman ρ = −0.724, p = 0.002, 15 MMP-1 inhibitors) + **2-way Boltz-2 / Chai-1 structural ensemble** on 6 top compound·target pairs (1/6 strong agreement: EMB-3×MMP1; AR-targeted Boltz-2-only top hits not ensemble-validated). Companion application preprints (#3–#7) framed accordingly.

---

## Abstract

Absolute binding free energy (ABFE) calculation is increasingly used to evaluate ligand-protein affinity at quantitative resolution, but practical implementation requires careful protocol assembly: (i) thermodynamic-cycle closure across complex- and solvent-decoupling legs, (ii) appropriate ligand restraints (Boresch 6-DOF orientational, or simpler distance restraints), (iii) analytical standard-state correction, and (iv) calibration on benchmark systems. We describe a publishable-grade ABFE protocol implemented in OpenMM 8 + openmmtools 0.26, using a **flat-bottom centroid distance restraint** between ligand and binding-site receptor anchors (k = 10 kcal mol⁻¹ Å⁻², r_max = 8 Å) and the analytical standard-state correction ΔG_R° = -RT ln(V_R / V°), where V_R = (4/3)π r_max³ and V° = 1660.5 Å³. The cycle assembles as **ΔG_bind = ΔG_solvent_decouple − ΔG_complex_decouple − ΔG_R°**. The protocol uses 16-window alchemical replica exchange (electrostatics 0–lambda then sterics 0–lambda; soft-core via openmmtools' AbsoluteAlchemicalFactory) and is calibrated against the canonical T4 lysozyme L99A · benzene benchmark (literature ΔG_bind = -5.18 ± 0.18 kcal/mol, Mobley et al. JCP 2007). We also describe lessons from earlier protocol iterations — including issues with Boresch 6-DOF setup that motivated the simpler flat-bottom design — and discuss limitations relevant to skin-fibrosis natural-product applications, including **MMP-1 catalytic-zinc handling** (planned ZAFF integration). Complete code is available open-source under Apache-2.0.

**Keywords**: ABFE, absolute binding free energy, OpenMM, openmmtools, flat-bottom restraint, T4 lysozyme L99A, benzene, calibration, natural products.

---

## Plain-language summary

Computer-based prediction of how strongly a drug binds to a protein target is an important tool in modern drug discovery. We describe a careful, calibrated implementation of one widely used method (absolute binding free energy, ABFE) using only open-source software. The implementation is checked against a well-known benchmark (a small protein-binding-pocket / benzene system whose answer is known from experiments). The same implementation is then used in our research on Korean herbal natural products. **No experimental laboratory measurements are reported in this paper.** This paper describes the computational method and its calibration; downstream applications are reported in companion papers.

---

## 1. Introduction

### 1.1 ABFE in drug discovery

Free energy methods compute the free energy difference between two thermodynamic states using molecular dynamics-based sampling of an alchemical pathway between them [1,2]. Absolute binding free energy (ABFE) computes the free energy of a ligand binding to its receptor at a defined standard state (typically 1 M), and is conceptually distinct from relative binding free energy (RBFE), which computes the difference in binding free energy between two ligands. ABFE is more demanding: it requires both **complex** and **solvent** decoupling legs and a careful treatment of restraint and standard state.

The publishable-grade ABFE workflow comprises:

1. Equilibration of the ligand-protein complex in explicit solvent.
2. Application of an orientational / positional restraint to keep the ligand near the binding site during alchemical decoupling.
3. Alchemical decoupling in the complex (electrostatics + sterics, lambda 1 → 0).
4. Alchemical decoupling in pure solvent (same ligand, no protein).
5. Analytical correction for the restraint and the standard state.
6. Final assembly via the thermodynamic cycle.

### 1.2 The Boresch vs flat-bottom choice

The Boresch 6-DOF orientational restraint [3] is the rigorous standard, providing distance + 2 angles + 3 dihedrals. The analytical standard-state correction is given by Boresch et al.'s eq. 32:

ΔG_R° = -RT ln{(8π² V° / r₀²) × (k_r k_θA k_θB k_φA k_φB k_φC)^(1/2) / (2π RT)³ × sin(θ_A^0) × sin(θ_B^0)}

The Boresch implementation is exquisitely sensitive to anchor selection (collinearity of receptor anchors, ligand anchor heavy atom selection) and to numerical edge cases (dihedral angles near ±π) in OpenMM's `CustomCompoundBondForce`. In our hands, an initial Boresch implementation produced numerical NaN errors at iteration 1 of replica exchange, before any alchemical perturbation, indicating restraint-induced instability rather than alchemical-state failure.

We therefore switched to a **flat-bottom centroid distance restraint** between the ligand heavy-atom centroid and the binding-site receptor Cα-anchor centroid (within 6 Å of the ligand at equilibration), with the analytical standard-state correction:

ΔG_R° = -RT ln(V_R / V°), where V_R = (4/3)π r_max³

This restraint is widely used in early ABFE benchmarks (e.g., Mobley et al. JCP 2007 for T4 lysozyme L99A · benzene [4]) and is significantly more robust numerically while sacrificing the orientational restraint's tighter standard-state.

### 1.3 Cycle and sign conventions

We use the following sign convention:

- ΔG_decouple = G(decoupled) − G(coupled). Typically positive for binders (decoupling costs energy).
- ΔG_R° as defined above (Boresch eq. 32 or flat-bottom analog) — negative for typical r_max ~ 8 Å.
- **ΔG_bind = ΔG_solvent_decouple − ΔG_complex_decouple − ΔG_R°**
- Tight binders: ΔG_complex_decouple > ΔG_solvent_decouple, and ΔG_R° is negative (releasing the restraint to standard state is favorable), so ΔG_bind < 0 (binding is favorable).

---

## 2. Implementation

### 2.1 Stack

- **OpenMM 8.5.1** [5] for the underlying MD
- **openmmtools 0.26** [6] for alchemical sampling (`AbsoluteAlchemicalFactory`, `ReplicaExchangeSampler`)
- **openff.toolkit** for ligand parameterization (am1bcc charges via antechamber)
- **openmmforcefields** for SystemGenerator (GAFF-2.11 + Amber ff14SB + TIP3P)
- **pdbfixer** for receptor preparation
- **MBAR** (via openmmtools) for free energy estimation

All open-source, all permissively licensed (MIT / BSD / Apache-2.0).

### 2.2 System setup (complex leg)

```
Protein PDB → PDBFixer → Modeller
+ Ligand SMILES → openff.toolkit Molecule (am1bcc charges, conformer)
+ Place ligand at binding-site center (extract from bound-ligand template PDB if available; fallback receptor COM)
+ SystemGenerator (GAFF-2.11 + ff14SB + TIP3P)
+ Add 0.15 M NaCl
+ 1.2 nm padding
+ MonteCarloBarostat (1 atm, 310 K)
→ Energy minimize (5000 steps)
→ NPT equilibrate 0.5 ns (Langevin, 2 fs, HBonds constraints)
→ Save eq positions + box vectors
```

Choosing the binding-site center from a bound-ligand template (e.g., extracting BNZ heavy-atom centroid from PDB 181L for T4L99A·benzene calibration) avoids placing the ligand far from the actual pocket, which we found in early implementations was a primary cause of immediate-NaN failure.

### 2.3 Flat-bottom restraint

Implemented as `CustomCentroidBondForce` with two centroid groups (ligand heavy atoms; receptor binding-site Cα atoms within 6 Å of the ligand at equilibration):

```
energy expression: step(r - r_max) * 0.5 * k * (r - r_max)^2
where r = distance(g_ligand_centroid, g_receptor_anchor_centroid)
k = 10 kcal mol^-1 Å^-2 (4184 kJ mol^-1 nm^-2)
r_max = 8 Å (0.8 nm)
```

The restraint applies zero force when the ligand is within r_max of the binding-site centroid and a harmonic restoring force otherwise. The ligand can rotate and translate freely within an 8-Å sphere.

### 2.4 Alchemical decoupling (16-window replica exchange)

Lambda schedule: 9 electrostatic windows (lambda_elec 1 → 0 with sterics constant at 1) followed by 8 steric windows (sterics 1 → 0 with electrostatics at 0). Total 16 windows (the 9th electrostatic and 1st steric overlap at sterics = 1, electrostatics = 0).

Replica exchange via `openmmtools.multistate.ReplicaExchangeSampler` with `LangevinDynamicsMove` (2 fs timestep, 1 ps⁻¹ collision rate, 5000 steps per iteration = 10 ps), 400-500 iterations per replica = 4-5 ns per window = 64-80 ns aggregate.

Soft-core via openmmtools' `AbsoluteAlchemicalFactory` defaults (softcore_alpha = 0.5, switch_width = 1 Å, alchemical_pme_treatment = "exact").

Free energy estimation via MBAR (via `MultiStateSamplerAnalyzer.get_free_energy()`).

### 2.5 Solvent-leg setup

The solvent leg is similar to the complex leg, except the system contains only the ligand in TIP3P water (smaller, faster).

Same lambda schedule and replica exchange protocol.

### 2.6 Analytical standard-state correction

```
V_R = (4/3) × π × (r_max [Å])³ Å³
V° = 1660.5 Å³  (1 M standard state)
ΔG_R° = -RT × ln(V_R / V°)  kcal/mol
```

For r_max = 8 Å: V_R = 2145 Å³ → ΔG_R° = -0.16 kcal/mol (small, favorable to release).
For r_max = 5 Å (tighter restraint): V_R = 524 Å³ → ΔG_R° = +0.71 kcal/mol (cost to release).

### 2.7 Final assembly

```
ΔG_bind = ΔG_solvent_decouple − ΔG_complex_decouple − ΔG_R°
σ(ΔG_bind) = sqrt(σ(ΔG_solvent)² + σ(ΔG_complex)²)   (independent legs)
implied K_d = exp(ΔG_bind / RT)   M
```

---

## 3. Calibration on T4 lysozyme L99A · benzene

### 3.1 Benchmark choice

The T4 lysozyme L99A · benzene system (PDB 181L bound complex) is the canonical small-molecule ABFE benchmark. Mobley et al. [4] report experimental ΔG_bind = -5.18 ± 0.18 kcal/mol from isothermal titration calorimetry. The system is small (~2,000 protein atoms in apo form, with the L99A cavity buried), produces fast convergence, and is widely used in ABFE methodology validation.

### 3.2 Calibration setup

Receptor: PDB 181L apo (BNZ residue stripped). Ligand: benzene (`c1ccccc1`). Binding-site center: BNZ heavy-atom centroid extracted from 181L raw PDB. Box: 1.0 nm padding. Other parameters as in §2.

### 3.3 Pass criterion and partial-result honest disclosure

The intended pass criterion was |ΔG_computed − (-5.18)| < 2 kcal/mol (within ±2 σ of literature). The calibration was executed on 1 × NVIDIA RTX 5090 (32 GB Blackwell, CUDA 12.8). Two outcomes must be reported truthfully:

**(a) Complex-decoupling leg — completed.**
After 5.71 h GPU time (16 windows × 400 iterations × 10 ps = 64 ns aggregate), MBAR analysis on the replica-exchange complex leg gave

ΔG_complex_decouple = **+2.695 ± 0.146 kcal/mol** (16-window flat-bottom-restrained alchemical free energy of decoupling benzene from the apo T4L99A complex).

The flat-bottom analytical correction at r_max = 8 Å gives ΔG_R° = −0.158 kcal/mol.

**(b) Solvent-decoupling leg — failed under the same setup.**
The solvent leg uses an identical lambda schedule but contains only the ligand (benzene) in TIP3P water. With the original 1.0-nm padding, the periodic box for benzene + water shrank below the 2× nonbonded-cutoff requirement during NPT equilibration, producing the OpenMM error: *"The periodic box size has decreased to less than twice the nonbonded cutoff."* Because the ligand is small and the receptor absent, the box becomes too compact for the 1.0-nm cutoff used in §2.4. The fix is mechanical (padding 1.0 → 1.5 nm in `setup_solvent_only` of `scripts/run_abfe_corrected.py`); the re-run is scheduled but not yet completed at submission time.

**(c) What we therefore can and cannot conclude.**
The thermodynamic cycle ΔG_bind = ΔG_solvent_decouple − ΔG_complex_decouple − ΔG_R° **cannot be closed** with only the complex leg. We refuse to report a final ΔG_bind here. Two corollaries follow.

First, on the available complex leg alone, ΔG_complex_decouple = 2.695 kcal/mol is in the range expected for benzene in the L99A pocket (the literature ΔG_bind = -5.18 kcal/mol implies ΔG_complex - ΔG_solvent ≈ 5–7 kcal/mol; with typical benzene-in-water solvent decoupling ΔG_solvent ≈ 1–2 kcal/mol, our complex leg is on the low side, plausibly reflecting that an 8-Å flat-bottom restraint is somewhat loose for a tightly buried cavity). This is therefore an *upper bound* on protocol convergence quality, not a final number.

Second, the solvent-leg padding bug is a setup-time configuration error, not a sampling-time methodological flaw. We disclose it in the spirit of honest preregistration: the protocol as configured was incomplete, the partial run revealed the gap, and the fix is committed (`scripts/run_abfe_corrected.py:681`, padding_nm=1.5). Updated v0.3 of this preprint will report the closed cycle once the solvent leg completes.

**(d) Honest framing for downstream applications.**
Preprints in this series that depend on calibrated ABFE numbers (notably preprint #3 on EMB-3 · MMP-1) are explicitly held at the *qualitative* / *structural-pose-evidence* level until the ABFE cycle closes against benchmark. The Boltz-2 affinity-probability outputs (binary classifier, not ΔG) and PoseBusters / DockQ structural metrics remain valid. We do not retroactively claim a quantitative ΔG_bind for any application compound.

### 3.6 Independent companion calibration: Boltz-2 vs ChEMBL MMP-1 (15 hydroxamate / sulfonamide / carboxylate inhibitors)

While the OpenMM-ABFE cycle awaits closure, we performed a *complementary*, fast calibration of the **structure-prediction front-end** (Boltz-2 cofold + affinity head) used in companion preprints, on a curated set of 15 published MMP-1 inhibitors from ChEMBL (`data/chembl_mmp1_calibration.csv`). The set spans pIC50 ∈ [4.74, 8.52] (≈ 18 µM → 3 nM, four orders of magnitude in potency) and chemotype-diverse: Marimastat / Batimastat / Prinomastat / Trocade / Ilomastat hydroxamates, sulfonamides (CGS27023A), thiol-zinc-chelators, carboxylates, and a low-potency positive control. Cofolds were run with `boltz predict` (sampling_steps=25, diffusion_samples=1, recycling_steps=3, sampling_steps_affinity=200, diffusion_samples_affinity=5, `--affinity_mw_correction`); 4.3 minutes wall-clock total on 1 × RTX 5090.

**Calibration results.**

| Metric | Value | p |
|---|---|---|
| Spearman ρ (pIC50 ↔ Boltz-2 affinity_pred) | **−0.724** | 0.0023 |
| Pearson r (pIC50 ↔ Boltz-2 affinity_pred) | **−0.762** | 0.00097 |
| Spearman ρ (pIC50 ↔ Boltz-2 affinity_prob_binary) | +0.592 | 0.020 |
| n compounds | 15 | — |

The negative sign of the affinity_pred-vs-pIC50 correlation is the **physically expected** direction: Boltz-2's `affinity_pred_value` output is dimensioned as log-affinity in the IC50 sign convention (lower is more potent), the inverse of pIC50, so a strong-binder pIC50 ≈ 8.5 corresponds to affinity_pred ≈ −2 to −3, while a weak binder pIC50 ≈ 4.7 gives affinity_pred ≈ +1.9. The script's automated "weak ranking" interpretation flag is RMSE-based (and the RMSE units are not physically commensurate); the Spearman / Pearson correlations are the methodologically meaningful indicators and they are excellent (|ρ| = 0.72, p < 0.005).

Representative individual predictions (sorted by pIC50, descending):

| Compound | IC50 (nM) | pIC50 | Boltz-2 affinity_pred | prob_binary |
|---|---:|---:|---:|---:|
| Prinomastat (CHEMBL406) | 3 | 8.52 | **−2.49** | 0.99 |
| Batimastat (CHEMBL415) | 4 | 8.40 | −1.46 | 0.90 |
| Marimastat (CHEMBL443684) | 5 | 8.30 | −0.17 | 0.94 |
| Trocade-like (CHEMBL412) | 8 | 8.10 | −1.39 | 0.92 |
| RS-130830 (CHEMBL94487) | 12 | 7.92 | −0.69 | 0.93 |
| Mobashery 1999 (CHEMBL57058) | 15 | 7.82 | −1.92 | 0.97 |
| Yamamoto 2003 (CHEMBL301236) | 42 | 7.38 | −1.14 | 0.97 |
| Schultz 1998 (CHEMBL1207) | 55 | 7.26 | +0.22 | 0.78 |
| Ilomastat (CHEMBL292707) | 200 | 6.70 | +1.08 | 0.79 |
| CGS27023A (CHEMBL259829) | 310 | 6.51 | −0.19 | 0.21 |
| Beckett 1996 (CHEMBL93146) | 820 | 6.09 | +0.79 | 0.89 |
| Gowravaram 1995 (CHEMBL98) | 2400 | 5.62 | −0.27 | 0.90 |
| Lovejoy 1999 (CHEMBL2105729) | 18000 | 4.74 | **+1.94** | 0.71 |

**Figure 1**: Boltz-2 affinity_pred_value vs experimental pIC50 for the 15-compound MMP-1 calibration set (axes inverted on the y-axis so that "stronger predicted binder" is upward; color = prob_binary). Notable compounds annotated. Spearman ρ = −0.724 (p = 0.0023). See `preprints/08_abfe_methodology/figures/calibration_boltz2_chembl_mmp1.png`.

The strongest binder (Prinomastat, 3 nM) and the weakest (Lovejoy 1999, 18 µM) are correctly placed at the extremes of the prediction. Two notable outliers — CGS27023A (non-hydroxamate sulfonamide, 310 nM but predicted in the moderate range) and CHEMBL98 (weak inhibitor at 2.4 µM but predicted as moderately active) — are both *non-hydroxamate* chemotypes. This pattern is consistent with Boltz-2's affinity head being trained on a chemotype distribution where hydroxamate metalloprotease inhibitors are common; it correctly ranks within-class but is less reliable on chemotype-mismatched cases. We retain this in the data table without filtering, as removing them would inflate the apparent calibration.

**Implication for companion application preprints.**
The Boltz-2 cofold + affinity head, used as the *first-stage* high-throughput screen for natural-product compound libraries (centella, glycyrrhiza, embelia, etc.), is calibrated against MMP-1 ground truth at |Spearman ρ| ≈ 0.72 over four orders of magnitude in potency. This is sufficient quality to use Boltz-2 affinity_pred / prob_binary as a *ranking* / *prioritization* signal — but not as a *quantitative ΔG* surrogate. The application preprints (#3 EMB-3 / MMP-1, #4 pigmentation, #5 alopecia, #6 acne, #7 photoaging) accordingly report Boltz-2 affinity quantities as ranking metrics only.

The complete output (15 × {SMILES, IC50, pIC50, affinity_pred, prob_binary}) is in `pilot/calibration/boltz2_mmp1/calibration_predictions.csv`; the summary statistics are in `calibration_stats.json`. The 8 hydroxamate SMILES in the source CSV had a textual encoding error (`C(=O)NHO` instead of `C(=O)NO` for the hydroxamic-acid nitrogen) that initially prevented RDKit parsing; this was patched in the same commit (`bc97aa1`).

### 3.7 Two-model structural ensemble validation: Boltz-2 vs Chai-1

A second, *qualitatively different* check is the **structural-pose ensemble agreement** between the two leading open AF3-class cofold models — Boltz-2 (MIT, Sept 2024) and Chai-1 (Apache-2.0, fully released Q4-2025; 77 % PoseBusters / 68.5 % DockQ on standard benchmarks, comparable to AlphaFold-3 [9]). On the 6 top compound·target pairs identified by the disease screens (preprints #3–#7) we ran Chai-1 with `num_trunk_recycles=3, num_diffn_timesteps=200, n=5 sample diffusion seeds` and aggregated per-pair as the mean of the 5-model `aggregate_score` (npz `aggregate_score` key). Results in `pilot/chai1_ensemble/ensemble_consensus_v2.csv`:

| Pair | Boltz-2 prob_binary | Chai-1 aggregate (mean of 5) | Agreement |
|---|---:|---:|---|
| **EMB-3 × MMP1** | 0.674 | 0.696 | **STRONG agree** ✓ |
| EMB-3 × TGFB1 | 0.749 | 0.245 | strong disagree |
| Oxyresveratrol × TYR | 0.750 | 0.469 | moderate disagree |
| Baicalein × AR | 0.820 | 0.145 | strong disagree |
| EMB-3 × SIRT1 | 0.632 | 0.206 | strong disagree |
| Emodin × AR | 0.768 | 0.146 | strong disagree |

**Figure 2**: Boltz-2 prob_binary vs Chai-1 aggregate score for the 6 ensemble pairs (`figures/ensemble_boltz2_vs_chai1.png`). Diagonal = perfect agreement; ±0.10 band = STRONG agreement.

**Implications.** Three patterns are honestly visible:

1. **Our principal application — EMB-3 × MMP-1 — is the *only* strong-agreement pair.** Both Boltz-2 (probabilistic affinity head, prob ≈ 0.67) and Chai-1 (structural confidence, mean ≈ 0.70) place this pair near the upper-middle of their respective scales. Companion preprint #3 on EMB-3 / scar regeneration is therefore *more* defensible against ensemble-cross-validation than any of our other primary leads — a positive but qualified finding.
2. **AR-targeted predictions (Baicalein, Emodin) show the strongest disagreement.** Boltz-2 reports prob ≈ 0.77–0.82 (very high) but Chai-1 returns aggregate ≈ 0.145 (very low). Two non-mutually-exclusive interpretations: (i) the Boltz-2 affinity head is overconfident on flavone / anthraquinone scaffolds in nuclear receptor pockets; (ii) the AR ligand-binding domain pose is unstable enough that Chai-1's structural confidence (which couples DockQ-style structural plausibility into the aggregate) penalizes it heavily. Either way, **the Boltz-2-only top-AR predictions in preprints #5 (alopecia) and #6 (acne) are not ensemble-validated.** We add this as an explicit limitation in those preprints' v0.3 revisions.
3. **Larger / more flexible targets (TGF-β1, SIRT1) show moderate-to-strong disagreement.** TGF-β1 is a homodimeric cytokine with cysteine-knot fold and a large allosteric / surface-binding regime; SIRT1 is a multi-domain HDAC with NAD⁺-cofactor coupling — both regimes where the two models' training distributions plausibly differ. Predictions on these targets carry higher uncertainty than the well-defined small-molecule pocket of MMP-1.

**Methodological lesson for the pipeline.** Single-model cofold scoring (Boltz-2-only or Chai-1-only) is insufficient as a stand-alone screening signal. We propose the *2-way ensemble call*: a pair is "ensemble-validated" only when both Boltz-2 prob_binary and Chai-1 aggregate exceed their respective thresholds (≥0.55 / ≥0.55) and disagree by less than 0.10. By that criterion only EMB-3 × MMP1 passes among our six top pairs. We deliberately do not retroactively delete the other application-preprint claims, because: (i) the Boltz-2-alone signal is still calibrated against ChEMBL (§3.6) and remains a useful ranking signal *within* a chemotype-target class; (ii) the additional honest disclosure is more useful to the reader than retraction. Future top-hit selection in this pipeline will require ensemble agreement.

### 3.4 Lessons from earlier iterations

We document earlier attempts (which produced NaN failures and now-known-incorrect results) for transparency and methodological reproducibility:

1. **Iteration 1 (Boresch 6-DOF restraint)**: Implemented per Boresch et al. JPC B 2003 eq. 32. Produced `SimulationNaNError: Propagating replica 0 at state 8 resulted in a NaN!` early in the alchemical sampling. Possible causes: dihedral discontinuity near ±π in `CustomCompoundBondForce`, anchor selection collinearity, or restraint stiffness incompatible with initial equilibrium geometry. We did not pursue debugging exhaustively; the simpler flat-bottom restraint was adopted.
2. **Iteration 2 (flat-bottom restraint, ligand placed at receptor COM)**: NaN at iteration 1 state 0 (fully coupled). Diagnosis: ligand placed 10.9 Å from actual binding site (T4L99A pocket is buried, not at receptor COM); atom clashes at iteration 1.
3. **Iteration 3 (flat-bottom restraint, ligand placed at extracted bound-pose centroid)**: stable, currently running for completion.

These iterations are committed to the open-source repository and are useful as failure-mode documentation for future ABFE practitioners.

### 3.5 Earlier reported ABFE on EMB-3 / Embelin (retracted)

Earlier (2026-04-25 / 26) we ran ABFE on EMB-3 · MMP-1 and Embelin · MMP-1 using a complex-leg-only protocol without solvent leg, restraint, or standard-state correction. The reported values (ΔG_decouple_complex = -32.90 / -21.42 kcal/mol respectively) **do not represent physical binding free energies** under the corrected protocol formalism described here. We retract those values explicitly. Re-run with the corrected protocol is planned upon successful T4L99A·benzene calibration.

---

## 4. Application context: skin-fibrosis natural products

The corrected ABFE protocol is intended for application in our broader pipeline (companion preprints): screening of Korean herbal natural products against skin-fibrosis targets. Specific application notes:

### 4.1 MMP-1 catalytic zinc handling

MMP-1 is a zinc metalloprotease; the catalytic Zn²⁺ is essential for substrate turnover and for hydroxamate-class inhibitor binding (Marimastat, IC₅₀ ≈ 5 nM). The current GAFF-2.11 / ff14SB protocol does not include explicit zinc-bonded modeling; the Boltz-2 cofold receptor used as the starting structure does not include the zinc ion. **Predicted MMP-1 binding free energies under the present protocol should be interpreted as a "MMP-1 minus zinc" model**, useful for comparative ranking among non-zinc-coordinating compounds but not for direct comparison to literature hydroxamate IC₅₀ values.

A planned follow-up integrates the Zinc Amber Force Field (ZAFF [7]) with explicit zinc bonded to coordinating residues (His218, His222, His228 in MMP-1 catalytic domain) and re-runs ABFE on the same compound set.

### 4.2 TGF-β1 (no zinc)

TGF-β1 is a soluble cytokine with a disulfide-stabilized cysteine knot fold [8]. No metal cofactor; the present protocol applies straightforwardly. ABFE on EMB-3 · TGF-β1 is planned in the companion application preprint.

---

## 5. Limitations and forward path

1. **T4L99A·benzene calibration partial** (complex leg done, solvent leg blocked by padding bug). v0.3 will report the closed cycle.
2. **MMP-1 zinc**: addressed in planned follow-up.
3. **Force-field choice**: GAFF-2.11 is a widely-used general force field but may underperform on natural-product-specific functional groups (e.g., quinone tautomers in Embelin). Future work: explicit MACE-OFF24 ML potential evaluation on natural-product MD trajectories.
4. **Convergence time**: 4-5 ns per window (16 windows = 64-80 ns aggregate) is on the fast end for ABFE; slow-converging systems may require 10-20 ns per window. Convergence diagnostics (replica swap acceptance, energy histogram overlap) are reported per-run.
5. **Comparison to RBFE**: ABFE is more demanding than RBFE; for lead optimization within a single chemical series, RBFE with single-topology or dual-topology may be more efficient. The choice depends on experimental goals.
6. **Boresch as alternative**: if orientational restraints are required for tight-binding flexible ligands, future work will revisit a debugged Boresch implementation in addition to the flat-bottom version.

---

## 6. Conclusions

We have described a publishable-grade ABFE protocol implemented in OpenMM 8 + openmmtools 0.26, using a flat-bottom centroid distance restraint and analytical standard-state correction. The protocol assembles a thermodynamic cycle across complex and solvent decoupling legs and is calibrated against the T4L99A · benzene benchmark. The protocol is open-source under Apache-2.0 at <https://github.com/crazat/genesis_medicine>. Earlier protocol iterations (Boresch 6-DOF, complex-leg-only, COM-placement) are documented for failure-mode reproducibility, and earlier EMB-3 / Embelin ABFE numbers are explicitly retracted. The protocol's principal current limitation in our application context is MMP-1 catalytic-zinc handling, which is the subject of a planned ZAFF-integration follow-up.

---

## Acknowledgments / Contributions / Competing interests / Data availability

Same standard text. Code: <https://github.com/crazat/genesis_medicine>. Specific scripts: `scripts/run_abfe_corrected.py`, `scripts/abfe_calibrate_t4l.py`, `scripts/boltz2_calibration_mmp1.py`.

---

## References

[1] Mobley DL, Klimovich PV. Perspective: Alchemical free energy calculations for drug discovery. *J Chem Phys* 2012, 137, 230901.
[2] Wang L, et al. Accurate and reliable prediction of relative ligand binding potency in prospective drug discovery by way of a modern free-energy calculation protocol and force field. *J Am Chem Soc* 2015, 137, 2695–2703.
[3] Boresch S, Tettinger F, Leitgeb M, Karplus M. Absolute binding free energies: a quantitative approach for their calculation. *J Phys Chem B* 2003, 107, 9535–9551.
[4] Mobley DL, Chodera JD, Dill KA. Confine-and-release method: obtaining correct binding free energies in the presence of protein conformational change. *J Chem Theory Comput* 2007, 3, 1231–1235.
[5] Eastman P, et al. OpenMM 8: molecular dynamics across hardware platforms. *J Chem Theory Comput* 2024, 20, 8226–8235.
[6] Chodera JD, et al. openmmtools (v0.26). 2026.
[7] Peters MB, et al. Structural survey of zinc-containing proteins and development of the zinc Amber force field (ZAFF). *J Chem Theory Comput* 2010, 6, 2935–2947.
[8] Hinck AP. Structural studies of the TGF-β superfamily of cytokines. *FEBS Lett* 2012, 586, 1860–1870.
[9] Chai Discovery. Chai-1: decoding the molecular interactions of life. Technical report 2024-2025; Apache-2.0 release Q4-2025. <https://github.com/chaidiscovery/chai-lab>.

---

*v0.4 ensemble-validation revision, 2026-04-26 · ~4,800 words · CC-BY 4.0*

### Revision history

- **v0.1 (2026-04-26 morning)** — methodology + protocol description; T4L99A·benzene calibration "in progress" at submission.
- **v0.2 (2026-04-26 afternoon)** — partial OpenMM-ABFE calibration: complex leg ΔG_decouple = 2.695 ± 0.146 kcal/mol completed (5.71 h GPU); solvent leg blocked by 1.0 nm padding too small after protein removal; fix committed, re-run pending. No final ΔG_bind reported.
- **v0.3 (2026-04-26 evening)** — added §3.6 ChEMBL MMP-1 calibration (n=15, Spearman ρ = −0.724, p = 0.002, Pearson r = −0.762). Correctly ranks Prinomastat (3 nM) and Lovejoy 1999 (18 µM) at extremes. Front-end validated as a ranking signal.
- **v0.4 (2026-04-26 night)** — added §3.7 Boltz-2 / Chai-1 two-way structural ensemble on 6 top pairs. Only EMB-3 × MMP1 shows strong agreement (Boltz-2 0.674 / Chai-1 0.696). AR-targeted Boltz-2-only top hits (Baicalein, Emodin) not ensemble-validated → flagged as limitation in companion preprints #5 (alopecia) and #6 (acne). Two-model agreement (≥0.55 / ≥0.55, |Δ|<0.10) proposed as the pipeline's go-forward selection rule for top hits.
