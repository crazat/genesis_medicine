# DMTL Experiment Card Factory

- timestamp: `2026-05-06T12:46:28+09:00`
- rows: `16`
- bucket_counts: `{'single_point_wetlab_card': 10, 'route_or_safety_prerequisite': 2, 'compute_followup_card': 4}`
- purpose: 계산 결과를 바로 CRO/wet-lab이 읽을 수 있는 design-make-test-learn card로 변환한다.

## Cards

| card | candidate | target | priority | bucket | path |
|---|---|---|---:|---|---|
| DMTL_002 | R15_chromanol_Me6_Me9 | tgfb1 | 0.8164 | single_point_wetlab_card | docs/experiment_cards/R15_chromanol_Me6_Me9__tgfb1.md |
| DMTL_001 | R15_chromanol_Cl_pos9 | tgfb1 | 0.8122 | single_point_wetlab_card | docs/experiment_cards/R15_chromanol_Cl_pos9__tgfb1.md |
| DMTL_003 | R15_chromanol_Me6_Me10 | tgfb1 | 0.7957 | single_point_wetlab_card | docs/experiment_cards/R15_chromanol_Me6_Me10__tgfb1.md |
| DMTL_004 | R15_chromanol_Me9_Me10 | tgfb1 | 0.7954 | single_point_wetlab_card | docs/experiment_cards/R15_chromanol_Me9_Me10__tgfb1.md |
| DMTL_005 | R15_chromanol_Cl_pos6 | tgfb1 | 0.7417 | single_point_wetlab_card | docs/experiment_cards/R15_chromanol_Cl_pos6__tgfb1.md |
| DMTL_007 | R15_chromanol_Cl_pos9 | dct | 0.7265 | single_point_wetlab_card | docs/experiment_cards/R15_chromanol_Cl_pos9__dct.md |
| DMTL_006 | R15_chromanol_Cl_pos10 | tgfb1 | 0.7168 | single_point_wetlab_card | docs/experiment_cards/R15_chromanol_Cl_pos10__tgfb1.md |
| DMTL_008 | R15_chromanol_Cl_pos6 | dct | 0.716 | single_point_wetlab_card | docs/experiment_cards/R15_chromanol_Cl_pos6__dct.md |
| DMTL_009 | R15_chromanol_Cl_pos6 | tyr | 0.705 | single_point_wetlab_card | docs/experiment_cards/R15_chromanol_Cl_pos6__tyr.md |
| DMTL_013 | R15_chromanol_Cl_pos9 | tyr | 0.6735 | route_or_safety_prerequisite | docs/experiment_cards/R15_chromanol_Cl_pos9__tyr.md |
| DMTL_014 | R15_chromanol_Cl_pos10 | tyr | 0.66 | route_or_safety_prerequisite | docs/experiment_cards/R15_chromanol_Cl_pos10__tyr.md |
| DMTL_015 | R15_chromanol_Me9_Me10 | tyr | 0.6596 | compute_followup_card | docs/experiment_cards/R15_chromanol_Me9_Me10__tyr.md |
| DMTL_016 | R15_chromanol_Me6_Me9 | tyr | 0.6522 | compute_followup_card | docs/experiment_cards/R15_chromanol_Me6_Me9__tyr.md |
| DMTL_017 | R15_chromanol_Me6_Me9 | dct | 0.6508 | compute_followup_card | docs/experiment_cards/R15_chromanol_Me6_Me9__dct.md |
| DMTL_018 | R15_chromanol_Me9_Me10 | dct | 0.6497 | compute_followup_card | docs/experiment_cards/R15_chromanol_Me9_Me10__dct.md |
| DMTL_010 | R15_chromanol | tgfb1 | 0.6439 | single_point_wetlab_card | docs/experiment_cards/R15_chromanol__tgfb1.md |

## Curator Rule

- `single_point_wetlab_card`: 추가 GPU보다 assay ordering/quote 준비가 우선이다.
- `route_or_safety_prerequisite`: route/safety gate를 먼저 해결한다.
- `compute_followup_card`: GPU/CPU가 비면 cofold/MD/free-energy follow-up 후보로 둔다.
