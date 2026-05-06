# Route Enumeration Gate

- timestamp: `2026-05-06T12:46:11+09:00`
- rows: `1082`
- gate_counts: `{'route_ready': 362, 'route_review': 378, 'route_hard': 342, 'red': 0}`
- purpose: SA score를 넘어서 실제 route enumeration이 필요한 후보와 바로 vendor/precursor search로 갈 후보를 분리한다.

## Top Route-Ready/Review Rows

| candidate | target | gate | family | steps | confidence | risk | next |
|---|---|---|---|---:|---:|---|---|
| chromanol_arom9+arom10_Cl+Cl_tgfb1 | tgfb1 | route_ready | chromanol_core_late_stage_substitution | 5 | 0.82 | no_major_route_risk | ASKCOS/AiZynthFinder route enumeration and vendor precursor search |
| chromanol_arom6+arom9_Cl+Cl_tgfb1 | tgfb1 | route_ready | chromanol_core_late_stage_substitution | 5 | 0.82 | no_major_route_risk | ASKCOS/AiZynthFinder route enumeration and vendor precursor search |
| chromanol_arom9_Cl_tgfb1 | tgfb1 | route_ready | chromanol_core_late_stage_substitution | 4 | 0.82 | no_major_route_risk | ASKCOS/AiZynthFinder route enumeration and vendor precursor search |
| chromanol_arom6+arom10_Cl+Cl_tgfb1 | tgfb1 | route_ready | chromanol_core_late_stage_substitution | 5 | 0.82 | no_major_route_risk | ASKCOS/AiZynthFinder route enumeration and vendor precursor search |
| chromanol_arom6+arom9_Cl+Me_tgfb1 | tgfb1 | route_ready | chromanol_core_late_stage_substitution | 4 | 0.82 | no_major_route_risk | ASKCOS/AiZynthFinder route enumeration and vendor precursor search |
| chromanol_arom6+arom9_Me+Cl_tgfb1 | tgfb1 | route_ready | chromanol_core_late_stage_substitution | 4 | 0.82 | no_major_route_risk | ASKCOS/AiZynthFinder route enumeration and vendor precursor search |
| chromanol_arom9+arom10_Cl+Me_tgfb1 | tgfb1 | route_ready | chromanol_core_late_stage_substitution | 4 | 0.82 | no_major_route_risk | ASKCOS/AiZynthFinder route enumeration and vendor precursor search |
| chromanol_arom9+arom10_Me+Cl_tgfb1 | tgfb1 | route_ready | chromanol_core_late_stage_substitution | 4 | 0.82 | no_major_route_risk | ASKCOS/AiZynthFinder route enumeration and vendor precursor search |
| chromanol_arom10_Cl_tgfb1 | tgfb1 | route_ready | chromanol_core_late_stage_substitution | 4 | 0.82 | no_major_route_risk | ASKCOS/AiZynthFinder route enumeration and vendor precursor search |
| chromanol_arom6+arom10_Cl+Me_tgfb1 | tgfb1 | route_ready | chromanol_core_late_stage_substitution | 4 | 0.82 | no_major_route_risk | ASKCOS/AiZynthFinder route enumeration and vendor precursor search |
| chromanol_arom6+arom10_Me+Cl_tgfb1 | tgfb1 | route_ready | chromanol_core_late_stage_substitution | 4 | 0.82 | no_major_route_risk | ASKCOS/AiZynthFinder route enumeration and vendor precursor search |
| chromanol_arom6+arom9_F+Cl_tgfb1 | tgfb1 | route_ready | chromanol_core_late_stage_substitution | 5 | 0.82 | no_major_route_risk | ASKCOS/AiZynthFinder route enumeration and vendor precursor search |
| chromanol_arom6+arom9_Cl+F_tgfb1 | tgfb1 | route_ready | chromanol_core_late_stage_substitution | 5 | 0.82 | no_major_route_risk | ASKCOS/AiZynthFinder route enumeration and vendor precursor search |
| chromanol_arom9+arom10_F+Cl_tgfb1 | tgfb1 | route_ready | chromanol_core_late_stage_substitution | 5 | 0.82 | no_major_route_risk | ASKCOS/AiZynthFinder route enumeration and vendor precursor search |
| chromanol_arom9+arom10_Cl+F_tgfb1 | tgfb1 | route_ready | chromanol_core_late_stage_substitution | 5 | 0.82 | no_major_route_risk | ASKCOS/AiZynthFinder route enumeration and vendor precursor search |
| chromanol_arom9+arom10_OMe+Cl_tgfb1 | tgfb1 | route_ready | chromanol_core_late_stage_substitution | 5 | 0.82 | no_major_route_risk | ASKCOS/AiZynthFinder route enumeration and vendor precursor search |
| chromanol_arom6_Cl_tgfb1 | tgfb1 | route_ready | chromanol_core_late_stage_substitution | 4 | 0.82 | no_major_route_risk | ASKCOS/AiZynthFinder route enumeration and vendor precursor search |
| chromanol_arom6+arom9_Cl+OMe_tgfb1 | tgfb1 | route_ready | chromanol_core_late_stage_substitution | 5 | 0.82 | no_major_route_risk | ASKCOS/AiZynthFinder route enumeration and vendor precursor search |
| chromanol_arom6+arom9_OMe+Cl_tgfb1 | tgfb1 | route_ready | chromanol_core_late_stage_substitution | 5 | 0.82 | no_major_route_risk | ASKCOS/AiZynthFinder route enumeration and vendor precursor search |
| chromanol_arom9+arom10_Cl+OMe_tgfb1 | tgfb1 | route_ready | chromanol_core_late_stage_substitution | 5 | 0.82 | no_major_route_risk | ASKCOS/AiZynthFinder route enumeration and vendor precursor search |
| chromanol_arom6+arom10_F+Cl_tgfb1 | tgfb1 | route_ready | chromanol_core_late_stage_substitution | 5 | 0.82 | no_major_route_risk | ASKCOS/AiZynthFinder route enumeration and vendor precursor search |
| chromanol_arom6+arom10_Cl+F_tgfb1 | tgfb1 | route_ready | chromanol_core_late_stage_substitution | 5 | 0.82 | no_major_route_risk | ASKCOS/AiZynthFinder route enumeration and vendor precursor search |
| chromanol_arom9+arom10_Me+Me_tgfb1 | tgfb1 | route_ready | chromanol_core_late_stage_substitution | 3 | 0.82 | no_major_route_risk | ASKCOS/AiZynthFinder route enumeration and vendor precursor search |
| chromanol_arom6+arom9_Me+Me_tgfb1 | tgfb1 | route_ready | chromanol_core_late_stage_substitution | 3 | 0.82 | no_major_route_risk | ASKCOS/AiZynthFinder route enumeration and vendor precursor search |
| chromanol_arom6+arom10_Cl+OMe_tgfb1 | tgfb1 | route_ready | chromanol_core_late_stage_substitution | 5 | 0.82 | no_major_route_risk | ASKCOS/AiZynthFinder route enumeration and vendor precursor search |
| chromanol_arom6+arom10_OMe+Cl_tgfb1 | tgfb1 | route_ready | chromanol_core_late_stage_substitution | 5 | 0.82 | no_major_route_risk | ASKCOS/AiZynthFinder route enumeration and vendor precursor search |
| chromanol_arom9+arom10_Cl+Cl_mmp1 | mmp1 | route_ready | chromanol_core_late_stage_substitution | 5 | 0.82 | no_major_route_risk | ASKCOS/AiZynthFinder route enumeration and vendor precursor search |
| chromanol_arom9_Me_tgfb1 | tgfb1 | route_ready | chromanol_core_late_stage_substitution | 3 | 0.82 | no_major_route_risk | ASKCOS/AiZynthFinder route enumeration and vendor precursor search |
| chromanol_arom6+arom9_Cl+Cl_mmp1 | mmp1 | route_ready | chromanol_core_late_stage_substitution | 5 | 0.82 | no_major_route_risk | ASKCOS/AiZynthFinder route enumeration and vendor precursor search |
| chromanol_arom10_Me_tgfb1 | tgfb1 | route_ready | chromanol_core_late_stage_substitution | 3 | 0.82 | no_major_route_risk | ASKCOS/AiZynthFinder route enumeration and vendor precursor search |
| chromanol_arom9+arom10_Cl+Cl_ptgs2 | ptgs2 | route_ready | chromanol_core_late_stage_substitution | 5 | 0.82 | no_major_route_risk | ASKCOS/AiZynthFinder route enumeration and vendor precursor search |
| chromanol_arom6+arom10_Me+Me_tgfb1 | tgfb1 | route_ready | chromanol_core_late_stage_substitution | 3 | 0.82 | no_major_route_risk | ASKCOS/AiZynthFinder route enumeration and vendor precursor search |
| chromanol_arom9+arom10_Cl+Cl_dct | dct | route_ready | chromanol_core_late_stage_substitution | 5 | 0.82 | no_major_route_risk | ASKCOS/AiZynthFinder route enumeration and vendor precursor search |
| chromanol_arom6+arom9_Cl+Cl_ptgs2 | ptgs2 | route_ready | chromanol_core_late_stage_substitution | 5 | 0.82 | no_major_route_risk | ASKCOS/AiZynthFinder route enumeration and vendor precursor search |
| chromanol_arom6+arom9_Cl+Cl_dct | dct | route_ready | chromanol_core_late_stage_substitution | 5 | 0.82 | no_major_route_risk | ASKCOS/AiZynthFinder route enumeration and vendor precursor search |

## Curator Rule

- `route_ready`: GPU cofold/MD 확장 또는 CRO RFQ 후보로 유지한다.
- `route_review`: ASKCOS/AiZynthFinder/manual route 전까지 대규모 GPU 확장은 보류한다.
- `route_hard`: atlas/methodology paper에는 가능하지만 lead paper main table에는 올리지 않는다.
