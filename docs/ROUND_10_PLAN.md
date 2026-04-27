# Round 10 Sprint Plan (post Round 9 NaN-cluster diagnosis)

**Date**: 2026-04-27 (after Round 9 phases 1-5)
**Trigger**: 5/5 ABFE NaN failures at electrostatic-steric transition states (1, 7, 7, 12, 14)

## Confirmed via Round 9 phase 5 diagnostic (post-box-fix)

- MD prefilter PC: EMB-3 × MMP-1 PASS (max RMSD 1.75 Å) — known-working ABFE system
- MD prefilter target: EGCG × MMP-1 — diagnosing now
- Implication: alchemical schedule (9 elec + 8 steric, softcore_alpha=0.5) is the bottleneck

## Round 10 priority queue (sequential, GPU-blocking)

### 1. AToM-OpenMM external clone + production run (8 GPU-h)

```bash
git clone https://github.com/Gallicchio-Lab/AToM-OpenMM $HOME/AToM-OpenMM
cd $HOME/AToM-OpenMM && pip install -e . --no-deps
# Then run via existing src/genesis_medicine/md/atom_openmm_adapter.py
python scripts/run_atom_openmm.py \
  --receptor pilot/scaffold_hop/abfe_egcg_mmp1/receptor.pdb \
  --ligand-smiles "OC1=CC(=CC(=C1O)O)..." \
  --name egcg_mmp1_atom \
  --out pilot/scaffold_hop/abfe_egcg_mmp1_atom/
```

**Why**: ATM single-topology dual-region scheme avoids the elec-to-steric
transition entirely. Different sampling — different failure mode.

### 2. PMX NEQ (deGroot lab, GROMACS) — 3× faster than HREMD

```bash
git clone https://github.com/deGrootLab/pmx $HOME/pmx
# Convert OpenMM PDB → GROMACS topology via parmed
# Run NEQ switching trajectories
```

**Why**: embarrassingly parallel; multiple short trajectories instead of
16-window REMD. NaN-resistant by design.

### 3. Denser electrostatic alchemical schedule (16 elec + 4 steric)

Modify `scripts/run_abfe_corrected.py`:
```python
# Current: 9 elec + 8 steric = 16 windows total
# Round 10: 16 elec + 4 steric = 20 windows total
N_LAMBDA_WINDOWS_DEFAULT = 20
ELEC_LAMBDA_SCHEDULE = np.linspace(1.0, 0.0, 16)  # finer
STERIC_LAMBDA_SCHEDULE = np.linspace(1.0, 0.0, 4)  # coarser
```

**Why**: failures at states 7, 12, 14 cluster around current elec-steric
transition. More elec windows → smoother transition → fewer NaN.

### 4. Wider soft-core potential (softcore_alpha 0.5 → 0.8)

```python
# In setup_alchemical_factory()
softcore_alpha = 0.8  # Round 10: was 0.5
```

**Why**: standard openmmtools softcore_alpha=0.5 is tuned for benzene-class
ligands. Polyphenols (EGCG 4 OH) and quinones (EMB-3) need wider softcore
to avoid potential singularities at λ→0.

### 5. Boresch 6-DOF restraint (debugged version)

Earlier preprint #8 §1.2 documented Boresch NaN issues from anchor selection.
Round 10 implementation:
- Auto-select non-collinear anchor triple (3 receptor Cα + 3 ligand heavy)
- Avoid dihedral ±π edge cases via cosine clipping
- Validate on T4L99A·benzene first; if T4L still passes, deploy on EGCG/TGFB1

**Why**: tight orientational restraint may stabilize sampling at edge λ values
where flat-bottom permits ligand drift → NaN.

## Round 10 quick-win targets

| Target | Effort | Expected outcome |
|---|---|---|
| AToM-OpenMM EGCG × MMP-1 | 2 days install + 1 day run | First non-zero EGCG ΔG_bind |
| Denser elec schedule retry | 1 day script + 1 day run | Diagnose if elec-transition is bottleneck |
| Softcore α 0.8 retry | 1 hour edit + 1 day run | Cheap experiment |
| Boresch debug | 3 days implement + verify | Long-term ABFE robustness |
| PMX NEQ pipeline | 1 week setup | Alternative full pipeline |

## Round 10 success criteria

- 1 non-EMB-3 ABFE cycle closes successfully (not NaN)
- AToM-OpenMM benchmark passes T4L99A·benzene (validates the alternative path)
- Preprint #8 v0.8 with documented "alchemical-schedule sensitivity" Limitations §

## What Round 10 will NOT achieve (out of scope)

- ZAFF zinc force field for MMP-1 (still task #182, separate sprint)
- Wet-lab CRO Tier 1 (task pending budget allocation)
- Recover D-110 photo cube hardware purchase (tasks pending Recover finance)

## Round 10 dependencies

- External repo cloning (no pip install — torch downgrade risk learned in Round 7)
- ~5 GPU-days total for sequential ABFE retries
- Documentation discipline maintained — every fail mode added to ABFE_PROTOCOL_LIMITATIONS.md
