# Free-energy Validation Plan

- timestamp: `2026-05-06T12:46:32+09:00`
- rows: `32`
- existing_rbfe_edge_rows: `15`
- method_counts: `{'RBFE_network': 5, 'ABFE_scout': 1, 'ABFE_or_CBFE_scout': 6, 'defer': 20}`
- OpenFE status: `openfe_missing_install_or_env`
- purpose: Boltz/MD 후보를 논문용 claim 전에 RBFE/ABFE/CBFE follow-up으로 올릴지 결정한다.

## Priority FE Follow-ups

| rank | target | compound | method | priority | consensus | pose | MD | next |
|---:|---|---|---|---:|---|---|---|---|
| 1 | dct | R15_chromanol_Cl_pos9 | RBFE_network | 0.8793 | high_confidence | pass | strong_stable | prepare OpenFE edge map; run short solvent/complex sanity first |
| 2 | tyr | R15_chromanol | ABFE_scout | 0.8774 | high_confidence | pass | strong_stable | prepare OpenFE edge map; run short solvent/complex sanity first |
| 3 | tgfb1 | R15_chromanol_Me6_Me9 | RBFE_network | 0.8736 | high_confidence | pass | strong_stable | prepare OpenFE edge map; run short solvent/complex sanity first |
| 4 | dct | R15_chromanol_Cl_pos6 | RBFE_network | 0.8714 | high_confidence | pass | strong_stable | prepare OpenFE edge map; run short solvent/complex sanity first |
| 5 | tyr | R15_chromanol_Cl_pos6 | RBFE_network | 0.8692 | high_confidence | pass | strong_stable | prepare OpenFE edge map; run short solvent/complex sanity first |
| 6 | tgfb1 | R15_chromanol_Cl_pos6 | RBFE_network | 0.8555 | high_confidence | pass | strong_stable | prepare OpenFE edge map; run short solvent/complex sanity first |
| 7 | tgfb1 | R15_chromanol_Cl_pos9 | ABFE_or_CBFE_scout | 0.7635 | usable_with_caveat | review | strong_stable | fix pose caveat or run replicate MD before production FE |
| 8 | dct | R15_chromanol | ABFE_or_CBFE_scout | 0.7533 | usable_with_caveat | review | strong_stable | fix pose caveat or run replicate MD before production FE |
| 9 | tgfb1 | R15_chromanol_Me9_Me10 | ABFE_or_CBFE_scout | 0.7463 | usable_with_caveat | review | strong_stable | fix pose caveat or run replicate MD before production FE |
| 10 | tgfb1 | R15_chromanol | ABFE_or_CBFE_scout | 0.7358 | usable_with_caveat | review | strong_stable | fix pose caveat or run replicate MD before production FE |
| 11 | tgfb1 | R15_chromanol_Me6_Me10 | ABFE_or_CBFE_scout | 0.7343 | usable_with_caveat | review | strong_stable | fix pose caveat or run replicate MD before production FE |
| 12 | tgfb1 | R15_chromanol_Cl_pos10 | ABFE_or_CBFE_scout | 0.724 | usable_with_caveat | review | strong_stable | fix pose caveat or run replicate MD before production FE |
| 13 | ptgs2 | R15_chromanol | defer | 0.3237 | usable_with_caveat | pass | missing | do not spend FE budget until pose/MD/target caveat improves |
| 14 | tyr | R15_chromanol_Cl_pos9 | defer | 0.3185 | usable_with_caveat | pass | missing | do not spend FE budget until pose/MD/target caveat improves |
| 15 | dct | R15_chromanol_Cl_pos10 | defer | 0.3154 | usable_with_caveat | review | missing | do not spend FE budget until pose/MD/target caveat improves |
| 16 | tyr | R15_chromanol_Cl_pos10 | defer | 0.313 | usable_with_caveat | pass | missing | do not spend FE budget until pose/MD/target caveat improves |
| 17 | tyrp1 | R15_chromanol | defer | 0.3124 | usable_with_caveat | pass | missing | do not spend FE budget until pose/MD/target caveat improves |
| 18 | tyr | R15_chromanol_Me9_Me10 | defer | 0.3031 | usable_with_caveat | pass | missing | do not spend FE budget until pose/MD/target caveat improves |
| 19 | tyr | R15_chromanol_Me6_Me9 | defer | 0.3023 | usable_with_caveat | pass | missing | do not spend FE budget until pose/MD/target caveat improves |
| 20 | dct | R15_chromanol_Me6_Me9 | defer | 0.2993 | usable_with_caveat | pass | missing | do not spend FE budget until pose/MD/target caveat improves |
| 21 | dct | R15_chromanol_Me9_Me10 | defer | 0.2991 | usable_with_caveat | pass | missing | do not spend FE budget until pose/MD/target caveat improves |
| 22 | tyr | R15_chromanol_Me6_Me10 | defer | 0.2822 | usable_with_caveat | review | missing | do not spend FE budget until pose/MD/target caveat improves |
| 23 | dct | R15_chromanol_Me6_Me10 | defer | 0.2753 | usable_with_caveat | review | missing | do not spend FE budget until pose/MD/target caveat improves |
| 24 | mmp1 | R15_chromanol | defer | 0.2647 | usable_with_caveat | review | missing | do not spend FE budget until pose/MD/target caveat improves |
| 25 | sirt1 | R15_chromanol | defer | 0.2512 | review_before_claim | review | missing | do not spend FE budget until pose/MD/target caveat improves |

## Hard Blocker: MMP-1 Zinc/ZAFF ABFE

- gate: `MMP1_ZAFF_ABFE_MUST_PASS`
- status: `blocked_zaff_not_integrated`
- current receptor Zn atoms: `0`
- required value: `restraint_corrected_delta_g_bind_kcal_mol < 0`
- strict pass: `upper_uncertainty_bound_below_0_kcal_mol`
- details: `docs/MMP1_ZAFF_ABFE_GATE.md`
- Until this gate passes, MMP-1 claims remain zinc-model-limited and cannot be described as ZAFF-corrected ABFE-confirmed binding.

## Curator Rule

- MMP-1 zinc/ZAFF ABFE is a hard blocker for any statement stronger than Boltz/MD-supported MMP-1 engagement.
- GPU가 바쁠 때는 이 plan을 생성만 하고 FE production은 큐잉하지 않는다.
- `RBFE_network`는 같은 target의 R16 chloro/dimethyl analog series에 우선 적용한다.
- `ABFE_or_CBFE_scout`는 paper claim 보강용 소규모 validation으로만 사용한다.
- `openfe_missing_install_or_env`이면 설치/환경 점검 문서화만 하고 heavy FE를 실행하지 않는다.
