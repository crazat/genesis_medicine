# Chromanol Pose Sanity Gate

- scope: R15 chromanol 14-target cofold + R16 topical chromanol 18-pair cofold
- method: OpenMM PDBxFile CIF split, RDKit SMILES template bond-order assignment, PoseBusters `dock` checks
- caveat: this is a physical pose sanity gate, not wet-lab evidence and not a binding free-energy calculation.

## Overall

- rows: `32`
- ok_rows: `32`
- full_pass_rows: `20`
- full_pass_rate: `0.625`
- gate_counts: `{'pass': 20, 'review': 12}`

## By Source

| Source | ok rows | pass | review | fail | full-pass rate | mean check pass-rate |
|---|---:|---:|---:|---:|---:|---:|
| r15_chromanol | 14 | 9 | 5 | 0 | 0.643 | 0.977 |
| r16_chromanol_topical | 18 | 11 | 7 | 0 | 0.611 | 0.972 |

## By Target

| Target | ok rows | pass | review | fail | full-pass rate | mean check pass-rate |
|---|---:|---:|---:|---:|---:|---:|
| ar | 1 | 1 | 0 | 0 | 1.000 | 1.000 |
| ctgf | 1 | 1 | 0 | 0 | 1.000 | 1.000 |
| dct | 7 | 4 | 3 | 0 | 0.571 | 0.981 |
| lox | 1 | 1 | 0 | 0 | 1.000 | 1.000 |
| mitf | 1 | 0 | 1 | 0 | 0.000 | 0.955 |
| mmp1 | 1 | 0 | 1 | 0 | 0.000 | 0.955 |
| ptgs2 | 1 | 1 | 0 | 0 | 1.000 | 1.000 |
| sirt1 | 1 | 0 | 1 | 0 | 0.000 | 0.909 |
| srd5a1 | 1 | 1 | 0 | 0 | 1.000 | 1.000 |
| srd5a2 | 1 | 1 | 0 | 0 | 1.000 | 1.000 |
| srebp1 | 1 | 1 | 0 | 0 | 1.000 | 1.000 |
| tgfb1 | 7 | 2 | 5 | 0 | 0.286 | 0.935 |
| tyr | 7 | 6 | 1 | 0 | 0.857 | 0.994 |
| tyrp1 | 1 | 1 | 0 | 0 | 1.000 | 1.000 |

## Outputs

- `pilot/cpu_meaningful/chromanol_pose_sanity_gate.csv`
- `pilot/cpu_meaningful/chromanol_pose_sanity_gate_summary.json`
