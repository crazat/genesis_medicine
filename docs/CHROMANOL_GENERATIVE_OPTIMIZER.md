# Chromanol Generative Optimizer

- timestamp: `2026-05-06T12:46:11+09:00`
- rows: `330`
- action_counts: `{'Boltz-2_next_when_GPU_free': 240, 'keep_for_route_or_safety_review': 82, 'archive_low_priority': 8}`
- purpose: R15/R16 chromanol core 주변에서 valid RDKit analog를 만들어 다음 Boltz/route/safety 큐 후보를 넓힌다.

## Top Local Designs

| design | target | priority | cLogP | TPSA | novelty | route | photosafety | action |
|---|---|---:|---:|---:|---|---|---|---|
| chromanol_arom9+arom10_Cl+Cl_tgfb1 | tgfb1 | 0.8137 | 2.242 | 49.69 | new_local_design | route_ready | aryl_halogen_review | Boltz-2_next_when_GPU_free |
| chromanol_arom6+arom9_Cl+Cl_tgfb1 | tgfb1 | 0.8117 | 2.242 | 49.69 | new_local_design | route_ready | aryl_halogen_review | Boltz-2_next_when_GPU_free |
| chromanol_arom9_Cl_tgfb1 | tgfb1 | 0.8003 | 1.589 | 49.69 | known_or_precomputed | route_ready | aryl_halogen_review | keep_for_route_or_safety_review |
| chromanol_arom6+arom10_Cl+Cl_tgfb1 | tgfb1 | 0.7999 | 2.242 | 49.69 | new_local_design | route_ready | aryl_halogen_review | Boltz-2_next_when_GPU_free |
| chromanol_arom6+arom9_Cl+Me_tgfb1 | tgfb1 | 0.7995 | 1.897 | 49.69 | new_local_design | route_ready | aryl_halogen_review | Boltz-2_next_when_GPU_free |
| chromanol_arom6+arom9_Me+Cl_tgfb1 | tgfb1 | 0.7995 | 1.897 | 49.69 | new_local_design | route_ready | aryl_halogen_review | Boltz-2_next_when_GPU_free |
| chromanol_arom9+arom10_Cl+Me_tgfb1 | tgfb1 | 0.7995 | 1.897 | 49.69 | new_local_design | route_ready | aryl_halogen_review | Boltz-2_next_when_GPU_free |
| chromanol_arom9+arom10_Me+Cl_tgfb1 | tgfb1 | 0.7995 | 1.897 | 49.69 | new_local_design | route_ready | aryl_halogen_review | Boltz-2_next_when_GPU_free |
| chromanol_arom10_Cl_tgfb1 | tgfb1 | 0.7932 | 1.589 | 49.69 | known_or_precomputed | route_ready | aryl_halogen_review | keep_for_route_or_safety_review |
| chromanol_arom6+arom10_Cl+Me_tgfb1 | tgfb1 | 0.7884 | 1.897 | 49.69 | new_local_design | route_ready | aryl_halogen_review | Boltz-2_next_when_GPU_free |
| chromanol_arom6+arom10_Me+Cl_tgfb1 | tgfb1 | 0.7884 | 1.897 | 49.69 | new_local_design | route_ready | aryl_halogen_review | Boltz-2_next_when_GPU_free |
| chromanol_arom6+arom9_F+Cl_tgfb1 | tgfb1 | 0.7879 | 1.728 | 49.69 | new_local_design | route_ready | aryl_halogen_review | Boltz-2_next_when_GPU_free |
| chromanol_arom6+arom9_Cl+F_tgfb1 | tgfb1 | 0.7879 | 1.728 | 49.69 | new_local_design | route_ready | aryl_halogen_review | Boltz-2_next_when_GPU_free |
| chromanol_arom9+arom10_F+Cl_tgfb1 | tgfb1 | 0.7879 | 1.728 | 49.69 | new_local_design | route_ready | aryl_halogen_review | Boltz-2_next_when_GPU_free |
| chromanol_arom9+arom10_Cl+F_tgfb1 | tgfb1 | 0.7879 | 1.728 | 49.69 | new_local_design | route_ready | aryl_halogen_review | Boltz-2_next_when_GPU_free |
| chromanol_arom9+arom10_OMe+Cl_tgfb1 | tgfb1 | 0.7879 | 1.598 | 58.92 | new_local_design | route_ready | aryl_halogen_review | Boltz-2_next_when_GPU_free |
| chromanol_arom6_Cl_tgfb1 | tgfb1 | 0.7864 | 1.589 | 49.69 | known_or_precomputed | route_ready | aryl_halogen_review | keep_for_route_or_safety_review |
| chromanol_arom6+arom9_Cl+OMe_tgfb1 | tgfb1 | 0.7825 | 1.598 | 58.92 | new_local_design | route_ready | aryl_halogen_review | Boltz-2_next_when_GPU_free |
| chromanol_arom6+arom9_OMe+Cl_tgfb1 | tgfb1 | 0.7825 | 1.598 | 58.92 | new_local_design | route_ready | aryl_halogen_review | Boltz-2_next_when_GPU_free |
| chromanol_arom9+arom10_Cl+OMe_tgfb1 | tgfb1 | 0.7825 | 1.598 | 58.92 | new_local_design | route_ready | aryl_halogen_review | Boltz-2_next_when_GPU_free |
| chromanol_arom6+arom10_F+Cl_tgfb1 | tgfb1 | 0.7783 | 1.728 | 49.69 | new_local_design | route_ready | aryl_halogen_review | Boltz-2_next_when_GPU_free |
| chromanol_arom6+arom10_Cl+F_tgfb1 | tgfb1 | 0.7768 | 1.728 | 49.69 | new_local_design | route_ready | aryl_halogen_review | Boltz-2_next_when_GPU_free |
| chromanol_arom9+arom10_Me+Me_tgfb1 | tgfb1 | 0.7758 | 1.552 | 49.69 | known_or_precomputed | route_ready | none_detected | keep_for_route_or_safety_review |
| chromanol_arom6+arom9_Me+Me_tgfb1 | tgfb1 | 0.7738 | 1.552 | 49.69 | known_or_precomputed | route_ready | none_detected | keep_for_route_or_safety_review |
| chromanol_arom6+arom10_Cl+OMe_tgfb1 | tgfb1 | 0.7723 | 1.598 | 58.92 | new_local_design | route_ready | aryl_halogen_review | Boltz-2_next_when_GPU_free |
| chromanol_arom6+arom10_OMe+Cl_tgfb1 | tgfb1 | 0.7723 | 1.598 | 58.92 | new_local_design | route_ready | aryl_halogen_review | Boltz-2_next_when_GPU_free |
| chromanol_arom9+arom10_Cl+Cl_mmp1 | mmp1 | 0.7721 | 2.242 | 49.69 | new_local_design | route_ready | aryl_halogen_review | Boltz-2_next_when_GPU_free |
| chromanol_arom9_Me_tgfb1 | tgfb1 | 0.7703 | 1.244 | 49.69 | new_local_design | route_ready | none_detected | Boltz-2_next_when_GPU_free |
| chromanol_arom6+arom9_Cl+Cl_mmp1 | mmp1 | 0.7701 | 2.242 | 49.69 | new_local_design | route_ready | aryl_halogen_review | Boltz-2_next_when_GPU_free |
| chromanol_arom10_Me_tgfb1 | tgfb1 | 0.7632 | 1.244 | 49.69 | new_local_design | route_ready | none_detected | Boltz-2_next_when_GPU_free |
| chromanol_arom9+arom10_Cl+Cl_ptgs2 | ptgs2 | 0.7625 | 2.242 | 49.69 | new_local_design | route_ready | aryl_halogen_review | Boltz-2_next_when_GPU_free |
| chromanol_arom6+arom10_Me+Me_tgfb1 | tgfb1 | 0.7621 | 1.552 | 49.69 | known_or_precomputed | route_ready | none_detected | keep_for_route_or_safety_review |
| chromanol_arom9+arom10_Cl+Cl_dct | dct | 0.7613 | 2.242 | 49.69 | new_local_design | route_ready | aryl_halogen_review | Boltz-2_next_when_GPU_free |
| chromanol_arom6+arom9_Cl+Cl_ptgs2 | ptgs2 | 0.7605 | 2.242 | 49.69 | new_local_design | route_ready | aryl_halogen_review | Boltz-2_next_when_GPU_free |
| chromanol_arom6+arom9_Cl+Cl_dct | dct | 0.7593 | 2.242 | 49.69 | new_local_design | route_ready | aryl_halogen_review | Boltz-2_next_when_GPU_free |

## Curator Rule

- `Boltz-2_next_when_GPU_free`는 GPU가 비고 현재 R16 100 ns가 끝난 뒤 cofold 후보로 올린다.
- `known_or_precomputed`는 중복 계산하지 않고 기존 R15/R16 evidence에 합친다.
- `aryl_halogen_review`는 pigment target에서 photosafety gate를 먼저 본다.
