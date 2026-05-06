# Structure Consensus Calibration

- timestamp: `2026-05-06T12:46:10+09:00`
- rows: `32`
- class_counts: `{'high_confidence': 6, 'usable_with_caveat': 18, 'review_before_claim': 8}`
- purpose: Boltz affinity만으로 claim하지 않고 pose sanity와 MD 안정성을 합쳐 confidence를 보정한다.

## Top Calibrated Pairs

| job | target | compound | class | score | pose | MD |
|---|---|---|---|---:|---|---|
| r16_03_dct | dct | R15_chromanol_Cl_pos9 | high_confidence | 0.7593 | pass | strong_stable |
| r15_chrom_tyr | tyr | R15_chromanol | high_confidence | 0.7574 | pass | strong_stable |
| r16_05_tgfb1 | tgfb1 | R15_chromanol_Me6_Me9 | high_confidence | 0.7536 | pass | strong_stable |
| r16_02_dct | dct | R15_chromanol_Cl_pos6 | high_confidence | 0.7514 | pass | strong_stable |
| r16_02_tyr | tyr | R15_chromanol_Cl_pos6 | high_confidence | 0.7492 | pass | strong_stable |
| r16_03_tgfb1 | tgfb1 | R15_chromanol_Cl_pos9 | usable_with_caveat | 0.7435 | review | strong_stable |
| r16_02_tgfb1 | tgfb1 | R15_chromanol_Cl_pos6 | high_confidence | 0.7355 | pass | strong_stable |
| r15_chrom_dct | dct | R15_chromanol | usable_with_caveat | 0.7333 | review | strong_stable |
| r16_06_tgfb1 | tgfb1 | R15_chromanol_Me9_Me10 | usable_with_caveat | 0.7263 | review | strong_stable |
| r15_chrom_tgfb1 | tgfb1 | R15_chromanol | usable_with_caveat | 0.7158 | review | strong_stable |
| r16_04_tgfb1 | tgfb1 | R15_chromanol_Me6_Me10 | usable_with_caveat | 0.7143 | review | strong_stable |
| r16_01_tgfb1 | tgfb1 | R15_chromanol_Cl_pos10 | usable_with_caveat | 0.704 | review | strong_stable |
| r15_chrom_ptgs2 | ptgs2 | R15_chromanol | usable_with_caveat | 0.6475 | pass | missing |
| r16_03_tyr | tyr | R15_chromanol_Cl_pos9 | usable_with_caveat | 0.637 | pass | missing |
| r16_01_dct | dct | R15_chromanol_Cl_pos10 | usable_with_caveat | 0.6307 | review | missing |
| r16_01_tyr | tyr | R15_chromanol_Cl_pos10 | usable_with_caveat | 0.626 | pass | missing |
| r15_chrom_tyrp1 | tyrp1 | R15_chromanol | usable_with_caveat | 0.6248 | pass | missing |
| r16_06_tyr | tyr | R15_chromanol_Me9_Me10 | usable_with_caveat | 0.6062 | pass | missing |
| r16_05_tyr | tyr | R15_chromanol_Me6_Me9 | usable_with_caveat | 0.6045 | pass | missing |
| r16_05_dct | dct | R15_chromanol_Me6_Me9 | usable_with_caveat | 0.5986 | pass | missing |
| r16_06_dct | dct | R15_chromanol_Me9_Me10 | usable_with_caveat | 0.5982 | pass | missing |
| r16_04_tyr | tyr | R15_chromanol_Me6_Me10 | usable_with_caveat | 0.5644 | review | missing |
| r16_04_dct | dct | R15_chromanol_Me6_Me10 | usable_with_caveat | 0.5506 | review | missing |
| r15_chrom_mmp1 | mmp1 | R15_chromanol | usable_with_caveat | 0.5295 | review | missing |
| r15_chrom_sirt1 | sirt1 | R15_chromanol | review_before_claim | 0.5024 | review | missing |

## Curator Use

- `high_confidence`는 manuscript main table에 넣을 수 있다.
- `usable_with_caveat`는 raw pose/MD caveat와 함께 보조 표 또는 discussion에 둔다.
- `review_before_claim`은 cross-model consensus 또는 wet-lab 전까지 강한 lead claim을 피한다.
