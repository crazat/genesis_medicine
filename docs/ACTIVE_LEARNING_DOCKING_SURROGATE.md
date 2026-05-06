# Active-learning Docking Surrogate

- timestamp: `2026-05-06T12:46:06+09:00`
- training_rows: `32`
- candidate_rows: `672`
- leave-one-out MAE: `0.0765`
- purpose: 이미 계산한 Boltz/MD 결과에서 다음 cofold 후보를 능동 선택한다.

## Top Recommendations

| rank | candidate | target | source | predicted | uncertainty | acquisition | next |
|---:|---|---|---|---:|---:|---:|---|
| 1 | R15_chromanol_Cl_pos9 | tgfb1 | r16_chromanol_topical_cofold | 0.7344 | 0.0298 | 0.7848 | skip_or_MD_if_unvalidated |
| 2 | R15_chromanol_Cl_pos6 | tgfb1 | r16_chromanol_topical_cofold | 0.7344 | 0.0298 | 0.7848 | skip_or_MD_if_unvalidated |
| 3 | R15_chromanol_Cl_pos10 | tgfb1 | r16_chromanol_topical_cofold | 0.7344 | 0.0298 | 0.7848 | skip_or_MD_if_unvalidated |
| 4 | R15_chromanol | tgfb1 | r15_chromanol_cofold | 0.6812 | 0.1004 | 0.7515 | skip_or_MD_if_unvalidated |
| 5 | R15_chromanol_Me6_Me9 | tgfb1 | r16_chromanol_topical_cofold | 0.6883 | 0.082 | 0.7514 | skip_or_MD_if_unvalidated |
| 6 | R15_chromanol_Me6_Me10 | tgfb1 | r16_chromanol_topical_cofold | 0.6883 | 0.082 | 0.7514 | skip_or_MD_if_unvalidated |
| 7 | R15_chromanol_Me9_Me10 | tgfb1 | r16_chromanol_topical_cofold | 0.6883 | 0.082 | 0.7514 | skip_or_MD_if_unvalidated |
| 8 | NPC243469 | dct | npass_xtb_best_cross_target | 0.5925 | 0.0482 | 0.6534 | Boltz-2 cofold |
| 9 | NPC194985 | dct | npass_xtb_best_cross_target | 0.5925 | 0.0482 | 0.6534 | Boltz-2 cofold |
| 10 | NPC196715 | dct | npass_xtb_best_cross_target | 0.5925 | 0.0482 | 0.6534 | Boltz-2 cofold |
| 11 | NPC261839 | dct | npass_xtb_best_cross_target | 0.5925 | 0.0482 | 0.6534 | Boltz-2 cofold |
| 12 | NPC469970 | dct | npass_xtb_best_cross_target | 0.5925 | 0.0482 | 0.6534 | Boltz-2 cofold |
| 13 | R15_chromanol_Cl_pos9 | dct | r16_chromanol_topical_cofold | 0.5925 | 0.0482 | 0.6494 | skip_or_MD_if_unvalidated |
| 14 | R15_chromanol_Cl_pos6 | dct | r16_chromanol_topical_cofold | 0.5925 | 0.0482 | 0.6494 | skip_or_MD_if_unvalidated |
| 15 | R15_chromanol_Cl_pos10 | dct | r16_chromanol_topical_cofold | 0.5925 | 0.0482 | 0.6494 | skip_or_MD_if_unvalidated |
| 16 | NPC243469 | ctgf | npass_xtb_best_cross_target | 0.5713 | 0.0641 | 0.6378 | Boltz-2 cofold |
| 17 | NPC243469 | lox | npass_xtb_best_cross_target | 0.5713 | 0.0641 | 0.6378 | Boltz-2 cofold |
| 18 | NPC243469 | mmp1 | npass_xtb_best_cross_target | 0.5713 | 0.0641 | 0.6378 | Boltz-2 cofold |
| 19 | NPC243469 | mc1r | npass_xtb_best_cross_target | 0.5713 | 0.0641 | 0.6378 | Boltz-2 cofold |
| 20 | NPC243469 | nr3c1 | npass_xtb_best_cross_target | 0.5713 | 0.0641 | 0.6378 | Boltz-2 cofold |
| 21 | NPC243469 | tyrp1 | npass_xtb_best_cross_target | 0.5713 | 0.0641 | 0.6378 | Boltz-2 cofold |
| 22 | NPC194985 | ctgf | npass_xtb_best_cross_target | 0.5713 | 0.0641 | 0.6378 | Boltz-2 cofold |
| 23 | NPC194985 | lox | npass_xtb_best_cross_target | 0.5713 | 0.0641 | 0.6378 | Boltz-2 cofold |
| 24 | NPC194985 | mmp1 | npass_xtb_best_cross_target | 0.5713 | 0.0641 | 0.6378 | Boltz-2 cofold |
| 25 | NPC194985 | mc1r | npass_xtb_best_cross_target | 0.5713 | 0.0641 | 0.6378 | Boltz-2 cofold |

## Curator Use

- `acquisition_score` 상위 후보 중 synthesis gate가 `red`가 아닌 것을 우선한다.
- 이미 labeled pair는 중복 cofold하지 말고 MD/pose/consensus 보강 여부만 본다.
- 모델은 local surrogate이므로 논문에는 후보 선택 heuristic으로만 서술한다.
