# NPASS xTB refinement ladder summary

- timestamp_basis: completed CSV mtimes through `2026-05-01T17:43+09:00`
- ladder_files: `51`
- combined_ok_rows: `83939`
- unique_np_ids: `5724`
- caveat: 이 표는 Potts-Guy logKp proxy, RDKit descriptors, GFN2-xTB conformer summaries만 통합한 in silico triage이다. 생물활성, 피부투과, hERG/AMES/DILI 안전성은 별도 검증 전 claim으로 쓰지 않는다.

## Best Candidates

| rank | np_id | source | logKp | logP | MW | gap_mean_eV | skin_window_like |
|---:|---|---|---:|---:|---:|---:|---|
| 1 | NPC42783 | xtb_npass_top500_hetero2_refine_120conf.csv | -2.087 | 2.48 | 188.3 | 11.98 | True |
| 2 | NPC213764 | xtb_npass_top500_hetero2_refine_120conf.csv | -3.044 | 0.53 | 118.2 | 11.96 | False |
| 3 | NPC474914 | xtb_npass_top500_hetero2_refine_120conf.csv | -0.939 | 4.82 | 272.5 | 11.65 | False |
| 4 | NPC236761 | xtb_npass_top500_hetero2_refine_120conf.csv | -3.618 | -0.64 | 76.1 | 11.89 | False |
| 5 | NPC88887 | xtb_npass_top500_hetero2_refine_120conf.csv | -3.428 | -0.25 | 90.1 | 11.64 | False |
| 6 | NPC149567 | xtb_npass_top500_hetero2_refine_120conf.csv | -3.809 | -1.03 | 62.1 | 11.49 | False |
| 7 | NPC323980 | xtb_npass_top500_hetero2_refine_120conf.csv | -2.280 | 2.09 | 174.3 | 11.01 | True |
| 8 | NPC283633 | xtb_npass_top500_hetero2_refine_120conf.csv | -3.428 | -0.25 | 90.1 | 11.27 | False |
| 9 | NPC324003 | xtb_npass_top500_hetero2_refine_120conf.csv | -0.749 | 5.21 | 286.5 | 10.98 | False |
| 10 | NPC184593 | xtb_npass_top500_hetero2_refine_120conf.csv | -2.423 | 1.41 | 118.2 | 10.76 | False |
| 11 | NPC479534 | xtb_npass_top1000_hetero3_refine_120conf.csv | -1.385 | 4.57 | 316.5 | 10.83 | False |
| 12 | NPC249078 | xtb_npass_top500_hetero2_refine_120conf.csv | -2.220 | 2.72 | 238.4 | 10.71 | True |

## Outputs

- `pilot/cpu_meaningful/npass_xtb_refine_ladder_summary.csv`
- `pilot/cpu_meaningful/npass_xtb_refine_best_candidates.csv`
