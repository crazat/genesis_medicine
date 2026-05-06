# Pre-Registration Template — Genesis_Medicine ABFE Methodology Paper

**Status**: TEMPLATE  /  to be filed at OSF (https://osf.io/) BEFORE running benchmark Phase 5 ABFE on the 5-compound ChEMBL panel.

**Why pre-register**: bioRxiv/ChemRxiv editor flagged "in silico screening of N compounds" papers. Pre-registration converts our work from screening report to confirmatory hypothesis-test, much harder to dismiss.

---

## 1. Title

**Tentative**: "Validation of ZAFF-AMBER absolute binding free energy protocol against ChEMBL MMP-1 inhibitors: an open benchmark for natural-product drug discovery"

## 2. Authors

Han, Cheongwoo (HAN PREDICT, Inc.; Recover Korean Medicine Clinic)
ORCID: 0009-0004-4805-8815
Email: crazat7@gmail.com

## 3. Hypothesis

**H1 (predictive)**: Our ZAFF-AMBER + alchemical replica exchange ABFE protocol (16 λ × 3 replicas × 5 ns production) recovers experimental MMP-1 IC50 ranking with Spearman ρ ≥ 0.6 on a 5-compound benchmark spanning 4 orders of magnitude in IC50 (3 nM to 18,000 nM).

**H2 (mechanistic)**: For sub-100 nM hydroxamate inhibitors, the dominant binding contribution comes from the Zn-coordinating hydroxamate moiety (predicted dG decomposition: dG_Zn-coord ≥ -3 kcal/mol per bond).

**H3 (negative result)**: 1,4-benzoquinone-2,5-diol natural products (EMB-3, embelin) do NOT bind MMP-1 with measurable affinity (predicted dG_bind > -2 kcal/mol with uncertainty includes 0).

## 4. Compounds (locked in advance — Tier-1, post Phase-4 prep validation 2026-05-04)

Original Tier-1 (Marimastat, Prinomastat, CGS27023A, aryl sulfone) excluded after Phase-4 antechamber failure ("sqm odd electrons" for hydroxamate protonation forms). Substituted with 6 PASSED compounds spanning IC50 4 nM → 18 μM, 4500-fold range:

| ChEMBL ID | Compound | IC50 (nM) | Class |
|---|---|---|---|
| CHEMBL415 | Batimastat | 4.0 | hydroxamate |
| CHEMBL94487 | RS-130830 | 12.0 | carboxylate |
| CHEMBL257077 | prinomastat-like | 15.0 | hydroxamate analog |
| CHEMBL301236 | fluoro-aryl HX | 42.0 | fluorohydroxamate |
| CHEMBL292707 | Ilomastat | 200.0 | zinc-chelating |
| CHEMBL2105729 | weak hydroxamate | 18000 | very weak (negative control) |

Independent points: EMB-3 (already done, +0.38±0.29 kcal/mol INCONCLUSIVE) + embelin (Phase 5 attempted 2026-05-04 — see exclusion rationale §7).

## 5. Protocol (locked)

- **Receptor**: 1HFC chain A holo, with catalytic Zn (3-His coordination: HID111, HID115, HID121)
- **Force field**: AMBER ff14SB protein + GAFF-2.11 ligand + ZAFF (Zn nonbonded ions234lm_126_tip3p) + TIP3P water
- **Charge model**: AM1-BCC for ligand
- **Initial pose**: AutoDock Vina rigid docking, grid centered on Zn (40.32, 27.89, 36.94), exhaustiveness=16
- **Warmup**: 10000-step minimization + 0K→310K heating (100 ps NVT) + 100 ps NPT restrained + 100 ps NPT unrestrained
- **Production**: openmmtools alchemical replica exchange, 16 λ windows, 3 replicas, **8 ns/window complex + 5 ns/window solvent** (upgraded from 5/3 ns 2026-05-04 17:14 KST for Spearman ρ uplift +0.05–0.15 per Aldeghi 2017 / Mey 2020)
- **Standard state correction**: ΔG_R = -RT ln(V_R / V₀), V₀ = 1660.5 Å³, V_R = (4/3)π(8 Å)³

## 6. Statistical analysis

**Primary outcome**: Spearman ρ between predicted dG_bind and experimental dG_exp = RT ln(IC50 in M) at T=310 K.

**Pre-specified threshold**: ρ ≥ 0.6 supports H1.

**Secondary**: MAE, RMSE between predicted and experimental dG.

**Negative control**: weakest compound (CHEMBL2105729, 18 μM) should have highest predicted dG (least negative).

**Effect size**: each ABFE result reported with uncertainty σ = sqrt(σ_complex² + σ_solvent²).

## 7. Pre-defined exclusion criteria

- Compound excluded if Phase 4 build (antechamber/parmchk2/tleap) fails after 2 retries (documented in §4).
- Compound excluded if Phase 5 production NaN's after warmup (replica integrator divergence) — documented as "failed to converge in this protocol", NOT silently dropped.
- Compound excluded if Phase 5 deadlocks due to concurrent OpenMM CUDA contention (system-level scheduling failure, not method failure) — re-run sole-tenant.
- All exclusions reported with reason.

### Embelin exclusion rationale (2026-05-04)

Embelin (1,4-benzoquinone-2,5-diol natural product, EMB-3 analog) Phase 5 launched 2026-05-04 16:09 KST under multi-process GPU contention with concurrent Boltz inference. After 6h+ runtime, trajectory.nc remained frozen at initial state (R(running) state with 0 progress). Process killed 2026-05-04 22:02 KST. Diagnosis: GPU dispatch starvation deadlock from concurrent OpenMM CUDA + short-task multiprocessing. To be re-attempted as sole-tenant. **Result for H3 deferred to re-run; EMB-3 +0.38±0.29 INCONCLUSIVE result stands as primary H3 evidence.**

## 8. Interpretation

**If ρ ≥ 0.7 + MAE < 2 kcal/mol**: validated protocol; can claim quantitative ranking ability.

**If 0.4 ≤ ρ < 0.7**: qualitative ranking only; ranking actives vs inactives works but quantitative IC50 prediction unreliable.

**If ρ < 0.4**: protocol fails on this benchmark; pivot to relative FEP or refine force field.

**For embelin/EMB-3 (independent of H1 outcome)**: report INCONCLUSIVE result ((+0.38 ± 0.29) kcal/mol for EMB-3) honestly with mechanistic interpretation.

## 9. Computational resources

- 1× NVIDIA RTX 5090 (32 GB VRAM)
- 24-core CPU
- Wallclock budget: ~8 days for 6 compounds × 19-29 h ABFE each (8/5 ns production)
- **Critical scheduling rule (added 2026-05-04 after deadlock incidents)**: ABFE Phase 5 must run as sole GPU process. Concurrent OpenMM CUDA jobs deadlock; concurrent multiprocessing.Pool with sub-second tasks also induce GPU dispatch starvation deadlock. Long-task (>5s/task) CPU pools may run alongside.

## 10. Code & data deposition

- All code: github.com/crazat/genesis_medicine (Apache-2.0)
- Code DOI: Zenodo deposit on commit corresponding to results
- Trajectories + analysis: deposit on Zenodo (separate DOI)
- Results table: pilot/abfe_benchmark_chembl/benchmark_summary.json

## 11. Conflicts of interest

HCW is founder of HAN PREDICT, Inc. and consults for Recover Korean Medicine Clinic. No external funding.

## 12. Pre-registration date

**Drafted**: 2026-05-04 KST
**Locked on**: [Lock when apo MD finishes + Tier-1 ABFE benchmark sole-tenant launched]
**OSF DOI**: [TO BE ASSIGNED at OSF filing]

---

## Filing checklist

- [ ] Read manuscript outline; ensure all H1-H3 are answerable from planned experiments
- [ ] Confirm protocol parameters match scripts (zaff_phase5_warmup_*.py, zaff_phase5_abfe_production_*.py)
- [ ] Lock compound list; no post-hoc additions
- [ ] Submit to OSF Pre-Registration form (https://osf.io/registries/osfregistries/new/preregistration)
- [ ] Get OSF DOI; cite in paper #A submission
- [ ] Tag git commit `prereg-v1` to anchor code state
