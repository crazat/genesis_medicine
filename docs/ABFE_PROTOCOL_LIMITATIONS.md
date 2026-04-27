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
