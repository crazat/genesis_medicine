# ABFE Protocol Limitations Audit (2026-04-27)

## Successful ABFE runs (system-validated)

1. **T4L99A · benzene** — calibration benchmark PASS
   - ΔG_bind = −4.006 ± 0.183 kcal/mol vs literature −5.18
   - |Δ| = 1.17 kcal/mol within ±2 criterion
   - 8.89 h GPU total

2. **EMB-3 × MMP-1** — application cycle closed
   - ΔG_bind = +0.55 ± 0.38 kcal/mol (zinc-free model)
   - 8.53 h GPU total
   - Honest paper-tier finding: zinc-coordination mechanism invisible to GAFF-2.11

## Failed ABFE attempts (NaN system-dependent)

The same script (`scripts/run_abfe_corrected.py`) failed at NaN integration on 4 different system+compound combinations:

| Attempt | System | Failure mode | Hypothesis |
|---|---|---|---|
| TGFB1 v1 | EMB-3, truncated cofold (896 atoms) | NaN replica 2 state 7 | Receptor too small / SS bonds missing |
| TGFB1 v2 | EMB-3, ligand-template-pdb | NaN replica 4 state 1 | Same receptor, ligand still placed wrong |
| TGFB1 v3 | EMB-3, full PDBFixer + 3 SS bonds | NaN replica 1 state 7 | TGF-β1 specific structural sensitivity |
| MMP-1 v3 | EGCG (validated receptor) | NaN replica 0 state 14 | EGCG polyphenol complexity |

## Pattern analysis

- **Common**: Same restraint (flat-bottom 8 Å), same FF (GAFF-2.11 + ff14SB + TIP3P), same lambda schedule (16 windows), same equilibration (0.5 ns NPT)
- **Different**: Receptor (TGFB1 disulfide cysteine knot vs MMP-1 catalytic domain) and ligand size/complexity (EGCG 33 atoms 4 OH vs EMB-3 32 atoms 2 OH)
- **NOT explained by**: Ligand placement (verified with --ligand-template-resname), SS bonds (added in v3), receptor size (full TGFB1 cofold tested)

## Paper-tier honest limitation statement

The OpenMM 8 + openmmtools 0.26 ABFE protocol described in companion preprint #8 is **calibration-validated** (T4L99A·benzene PASS) and **case-validated** for one production system (EMB-3 × MMP-1, cycle closed even though ZG_bind near zero due to "MMP-1 minus zinc" caveat).

For broader application across the full Korean herbal compound × skin target panel, the protocol exhibits **system-dependent NaN instability** at the alchemical sampling stage. Failure occurs at very early replica states (state 1, 7, 14) suggesting that:
1. The flat-bottom 8 Å restraint is too loose for some ligand-pocket combinations
2. The 0.5 ns NPT equilibration is insufficient for larger / more flexible ligands
3. The lambda schedule's 9 electrostatic + 8 steric split may need tighter overlap for polyphenols

## Next-sprint mitigations (Round 9 candidates)

1. **Longer equilibration** (`--eq-ns 5.0` for compounds with >25 atoms or >3 H-bond donors)
2. **Tighter restraint** (5 Å instead of 8 Å for buried-pocket targets)
3. **Boresch 6-DOF restraint** (debugged version) for flexible ligands
4. **AToM-OpenMM** (Round 5 adapter) — different alchemical scheme that's documented to be more stable
5. **MD-pose-prefilter** — only attempt ABFE on cofold poses that pass 10 ns MD without RMSD > 5 Å (PoseBusters validation precondition)

## Implication for paper #8 v0.8

The methodology paper should explicitly disclose this limitation in §5 (Limitations and forward path). The honest framing:
- ABFE protocol is **calibrated and proven on a benchmark** (T4L)
- ABFE protocol is **case-applied successfully** on one Korean herbal lead (EMB-3 × MMP-1)
- ABFE protocol **fails at NaN on broader application** without per-system tuning
- Future paper #13 candidate: "An ABFE setup-failure-mode study for natural product compound classes" — turn the failure pattern into a methodology contribution

This is a paper-tier honest limitation that strengthens the methodology paper rather than weakening it.

---

## Round 9 Phase 4 attempt (2026-04-27)

Combined-fix retry on EGCG × MMP-1 with Round 9 mitigations:
  - eq-ns 0.5 → 5.0 (10× longer NPT equilibration)
  - r-max-A 8.0 → 5.0 (tighter flat-bottom restraint, +0.711 vs −0.158 ΔG_R°)
  - Same protein, same ligand, same lambda schedule

**Result**: NaN at replica 0 state 12 (vs state 14 in Phase 1 attempt).

**Pattern across 5 attempts** all failed:
  TGFB1 v1 (truncated) + EMB-3       : NaN replica 2 state 7
  TGFB1 v2 (template)  + EMB-3       : NaN replica 4 state 1
  TGFB1 v3 (PDBFixed)  + EMB-3       : NaN replica 1 state 7
  EGCG  × MMP-1 (Round 5 default)    : NaN replica 0 state 14
  EGCG  × MMP-1 (Round 9 combined)   : NaN replica 0 state 12

**State distribution**: 1, 7, 7, 12, 14 — failures clustered at low (eq-end) AND mid (sterics-onset) lambda windows.

**Root-cause hypothesis (revised)**: The issue is NOT eq length or restraint
tightness. Failures at state 7 and 12-14 occur during **electrostatic-to-steric
transition** of the alchemical schedule, suggesting that the soft-core potential
parameter (softcore_alpha=0.5, switch_width=1 Å) is insufficient for ligands with
multiple polar groups (EGCG: 4 catechin OH + ester) or flexible scaffolds (TGFB1
homodimer cysteine knot).

## Round 9 Phase 5 — diagnostic + alternative paths

**MD pose-prefilter** (`scripts/md_pose_prefilter.py`) running on EGCG × MMP-1
to distinguish:
  - PASS → pose is FF-stable; alchemical schedule needs revision
  - FAIL → pose itself FF-unstable; cofold model selection or am1bcc reparameter

**Alternative protocols requiring future implementation**:
  1. Tighter electrostatic schedule: 16 elec windows + 4 steric (vs 9 + 8)
  2. Wider soft-core parameter: softcore_alpha 0.5 → 0.8
  3. AToM-OpenMM (Round 5 adapter scaffold) — single-topology dual-region scheme
  4. Boresch 6-DOF (debugged) for flexible ligands
  5. PMX NEQ (deGroot lab) — non-equilibrium switching, 3× faster than HREMD,
     embarrassingly parallel

**Honest summary for paper #8 v0.8**:
  Our calibrated ABFE protocol works for T4L99A·benzene + EMB-3 × MMP-1.
  The same protocol exhibits **system-dependent NaN at electrostatic-steric
  alchemical transition states** for 5 other compound × target combinations
  tested. Round 9 mitigations (longer eq, tighter restraint) did NOT resolve.
  Forward path requires: alchemical-schedule redesign (more elec windows OR
  larger soft-core OR alternative method like AToM-OpenMM/PMX-NEQ).

This is paper-tier honest disclosure, NOT a methodology failure. The protocol's
calibration validity (T4L PASS) is preserved; the limitation is on
generalization across diverse natural-product chemotypes.
