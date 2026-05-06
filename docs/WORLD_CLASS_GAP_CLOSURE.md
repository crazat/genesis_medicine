# World-Class Drug Discovery Gap Closure

- timestamp: `2026-05-06T12:46:37+09:00`
- candidate_rows: `2328`
- matrix_csv: `pilot/cpu_meaningful/world_class_gap_closure_matrix.csv`
- queue_policy_json: `pilot/auto_queue_decision_policy.json`
- readiness_counts: `{'cheap_compute_or_paper_with_fto_caveat': 378, 'triage_accumulating': 1193, 'hold_or_benchmark_only': 757}`
- heavy_compute_permission_counts: `{'short_triage_only': 378, 'cheap_compute_only': 1193, 'hold': 757}`
- creative_discovery_status_counts: `{'implemented_running': 1, 'gap_detected': 1, 'partial_post_filter_only': 1, 'partial_chromanol_constrained_only': 1, 'static_pocket_gate_only': 1, 'roadmap_only': 1, 'partial_decoy_gate_only': 1, 'partial_gate_only': 1, 'planned_gate_only': 1, 'partial_deterministic_curator': 1}`
- target MSA missing count: `14`
- MMP-1 ZAFF status: `blocked_zaff_not_integrated`

## Meaning

이 파일은 개별 gate를 하나로 합친 master decision layer다. 후보가 좋은 cofold/MD 값을 가져도 prior-art, Markush/FTO, synthesis, safety, target biology, model uncertainty, dermal translation, FE readiness 중 하나가 막히면 비싼 계산이나 강한 claim으로 자동 승격하지 않는다.

## Queue Policy

- R17 expanded green-target 60 ns: `3/3` complete; already-running panel은 완료시킨다.
- 새 chromanol 100-200 ns, RBFE/ABFE, synthesis/purchase, commercial novelty claim은 Markush/FTO review 전까지 보류한다.
- NPASS/xTB/descriptor/atlas 같은 cheap CPU 계산은 계속 허용한다.
- MMP-1 direct-binding 강화 claim은 ZAFF/MCPB holo-Zn ABFE gate 통과 전까지 금지한다.
- EMB-3/quinone류는 GSH/NAC trapping, DPRA/KeratinoSens/h-CLAT, ROS/redox, photostability, skin S9/metabolite package 전까지 safety-positive claim 금지다.
- creative generation은 synthesis/prior-art/novelty/uncertainty/phenomics guard 없이 신규 long-MD/FE/lead claim으로 올리지 않는다.
- active-learning short cofold는 GPU 유휴 방지용 triage로 허용하지만, 결과는 master gate 통과 전까지 보조 evidence다.
- target-key MSA가 없는 target은 cofold queue에서 차단하고 cache 준비를 먼저 한다.
- `wetlab_translation_priority`는 더 큰 GPU 반복보다 CRO/DMTL/IVRT/IVPT/Cell Painting package를 먼저 만든다.

## Readiness By Target

| target | wetlab | paper | FTO-caveated | triage | hold |
|---|---:|---:|---:|---:|---:|
| ar | 0 | 0 | 0 | 0 | 1 |
| ctgf | 0 | 0 | 0 | 40 | 41 |
| dct | 0 | 0 | 125 | 40 | 41 |
| lox | 0 | 0 | 0 | 40 | 41 |
| mc1r | 0 | 0 | 0 | 40 | 40 |
| mitf | 0 | 0 | 0 | 0 | 1 |
| mmp1 | 0 | 0 | 0 | 0 | 190 |
| nr3c1 | 0 | 0 | 0 | 40 | 40 |
| ptgs2 | 0 | 0 | 0 | 0 | 102 |
| sirt1 | 0 | 0 | 0 | 0 | 1 |
| srd5a1 | 0 | 0 | 0 | 0 | 1 |
| srd5a2 | 0 | 0 | 0 | 0 | 1 |
| srebp1 | 0 | 0 | 0 | 0 | 1 |
| tgfb1 | 0 | 0 | 128 | 0 | 1 |
| tyr | 0 | 0 | 125 | 40 | 41 |
| tyrp1 | 0 | 0 | 0 | 40 | 41 |
| untargeted | 0 | 0 | 0 | 913 | 173 |

## Top Action Rows

| candidate | target | readiness | heavy compute | paper | blockers/caveats | next |
|---|---|---|---|---|---|---|
| R15_chromanol_Cl_pos10 | dct | cheap_compute_or_paper_with_fto_caveat | short_triage_only | in_silico_with_fto_caveat | Markush/FTO review required before heavy follow-up; medium IP/FTO/Markush review risk; cross-model/PLIF/negative-control validation required; benchmark decoys or orthogonal structure model required; OECD TG497/ICH S10 safety counterscreen required; CMC/developability yellow gate; model applicability-domain caveat: activity_cliff_risk | prepare Markush/FTO package; use only completed data for caveated papers |
| R15_chromanol_Cl_pos10 | tgfb1 | cheap_compute_or_paper_with_fto_caveat | short_triage_only | in_silico_with_fto_caveat | Markush/FTO review required before heavy follow-up; medium IP/FTO/Markush review risk; target evidence yellow: phenotype/cell context required; cross-model/PLIF/negative-control validation required; benchmark decoys or orthogonal structure model required; OpenFE/RBFE environment missing; OECD TG497/ICH S10 safety counterscreen required; CMC/developability yellow gate; model applicability-domain caveat: activity_cliff_risk | prepare Markush/FTO package; use only completed data for caveated papers |
| R15_chromanol_Cl_pos10 | tyr | cheap_compute_or_paper_with_fto_caveat | short_triage_only | in_silico_with_fto_caveat | Markush/FTO review required before heavy follow-up; medium IP/FTO/Markush review risk; cross-model/PLIF/negative-control validation required; OECD TG497/ICH S10 safety counterscreen required; CMC/developability yellow gate; model applicability-domain caveat: activity_cliff_risk | prepare Markush/FTO package; use only completed data for caveated papers |
| R15_chromanol_Cl_pos6 | dct | cheap_compute_or_paper_with_fto_caveat | short_triage_only | in_silico_with_fto_caveat | Markush/FTO review required before heavy follow-up; medium IP/FTO/Markush review risk; OpenFE/RBFE environment missing; OECD TG497/ICH S10 safety counterscreen required; CMC/developability yellow gate; model applicability-domain caveat: activity_cliff_risk | prepare Markush/FTO package; use only completed data for caveated papers |
| R15_chromanol_Cl_pos6 | tgfb1 | cheap_compute_or_paper_with_fto_caveat | short_triage_only | in_silico_with_fto_caveat | Markush/FTO review required before heavy follow-up; medium IP/FTO/Markush review risk; target evidence yellow: phenotype/cell context required; OpenFE/RBFE environment missing; OECD TG497/ICH S10 safety counterscreen required; CMC/developability yellow gate; model applicability-domain caveat: activity_cliff_risk | prepare Markush/FTO package; use only completed data for caveated papers |
| R15_chromanol_Cl_pos6 | tyr | cheap_compute_or_paper_with_fto_caveat | short_triage_only | in_silico_with_fto_caveat | Markush/FTO review required before heavy follow-up; medium IP/FTO/Markush review risk; OpenFE/RBFE environment missing; OECD TG497/ICH S10 safety counterscreen required; CMC/developability yellow gate; model applicability-domain caveat: activity_cliff_risk | prepare Markush/FTO package; use only completed data for caveated papers |
| R15_chromanol_Cl_pos9 | dct | cheap_compute_or_paper_with_fto_caveat | short_triage_only | in_silico_with_fto_caveat | Markush/FTO review required before heavy follow-up; medium IP/FTO/Markush review risk; OpenFE/RBFE environment missing; OECD TG497/ICH S10 safety counterscreen required; CMC/developability yellow gate; model applicability-domain caveat: activity_cliff_risk | prepare Markush/FTO package; use only completed data for caveated papers |
| R15_chromanol_Cl_pos9 | tgfb1 | cheap_compute_or_paper_with_fto_caveat | short_triage_only | in_silico_with_fto_caveat | Markush/FTO review required before heavy follow-up; medium IP/FTO/Markush review risk; target evidence yellow: phenotype/cell context required; OpenFE/RBFE environment missing; OECD TG497/ICH S10 safety counterscreen required; CMC/developability yellow gate; model applicability-domain caveat: activity_cliff_risk | prepare Markush/FTO package; use only completed data for caveated papers |
| R15_chromanol_Cl_pos9 | tyr | cheap_compute_or_paper_with_fto_caveat | short_triage_only | in_silico_with_fto_caveat | Markush/FTO review required before heavy follow-up; medium IP/FTO/Markush review risk; cross-model/PLIF/negative-control validation required; OECD TG497/ICH S10 safety counterscreen required; CMC/developability yellow gate; model applicability-domain caveat: activity_cliff_risk | prepare Markush/FTO package; use only completed data for caveated papers |
| R15_chromanol_Me6_Me10 | dct | cheap_compute_or_paper_with_fto_caveat | short_triage_only | in_silico_with_fto_caveat | Markush/FTO review required before heavy follow-up; cross-model/PLIF/negative-control validation required; model applicability-domain caveat: activity_cliff_risk | prepare Markush/FTO package; use only completed data for caveated papers |
| R15_chromanol_Me6_Me10 | tgfb1 | cheap_compute_or_paper_with_fto_caveat | short_triage_only | in_silico_with_fto_caveat | Markush/FTO review required before heavy follow-up; target evidence yellow: phenotype/cell context required; OpenFE/RBFE environment missing; model applicability-domain caveat: activity_cliff_risk | prepare Markush/FTO package; use only completed data for caveated papers |
| R15_chromanol_Me6_Me10 | tyr | cheap_compute_or_paper_with_fto_caveat | short_triage_only | in_silico_with_fto_caveat | Markush/FTO review required before heavy follow-up; cross-model/PLIF/negative-control validation required; model applicability-domain caveat: activity_cliff_risk | prepare Markush/FTO package; use only completed data for caveated papers |
| R15_chromanol_Me6_Me9 | dct | cheap_compute_or_paper_with_fto_caveat | short_triage_only | in_silico_with_fto_caveat | Markush/FTO review required before heavy follow-up; cross-model/PLIF/negative-control validation required; model applicability-domain caveat: activity_cliff_risk | prepare Markush/FTO package; use only completed data for caveated papers |
| R15_chromanol_Me6_Me9 | tgfb1 | cheap_compute_or_paper_with_fto_caveat | short_triage_only | in_silico_with_fto_caveat | Markush/FTO review required before heavy follow-up; target evidence yellow: phenotype/cell context required; OpenFE/RBFE environment missing; model applicability-domain caveat: activity_cliff_risk | prepare Markush/FTO package; use only completed data for caveated papers |
| R15_chromanol_Me6_Me9 | tyr | cheap_compute_or_paper_with_fto_caveat | short_triage_only | in_silico_with_fto_caveat | Markush/FTO review required before heavy follow-up; cross-model/PLIF/negative-control validation required; model applicability-domain caveat: activity_cliff_risk | prepare Markush/FTO package; use only completed data for caveated papers |
| R15_chromanol_Me9_Me10 | dct | cheap_compute_or_paper_with_fto_caveat | short_triage_only | in_silico_with_fto_caveat | Markush/FTO review required before heavy follow-up; cross-model/PLIF/negative-control validation required; model applicability-domain caveat: activity_cliff_risk | prepare Markush/FTO package; use only completed data for caveated papers |
| R15_chromanol_Me9_Me10 | tgfb1 | cheap_compute_or_paper_with_fto_caveat | short_triage_only | in_silico_with_fto_caveat | Markush/FTO review required before heavy follow-up; target evidence yellow: phenotype/cell context required; OpenFE/RBFE environment missing; model applicability-domain caveat: activity_cliff_risk | prepare Markush/FTO package; use only completed data for caveated papers |
| R15_chromanol_Me9_Me10 | tyr | cheap_compute_or_paper_with_fto_caveat | short_triage_only | in_silico_with_fto_caveat | Markush/FTO review required before heavy follow-up; cross-model/PLIF/negative-control validation required; model applicability-domain caveat: activity_cliff_risk | prepare Markush/FTO package; use only completed data for caveated papers |
| chromanol_arom10_CN_dct | dct | cheap_compute_or_paper_with_fto_caveat | short_triage_only | in_silico_with_fto_caveat | Markush/FTO review required before heavy follow-up; OECD TG497/ICH S10 safety counterscreen required; formulation rescue before exposure claim | prepare Markush/FTO package; use only completed data for caveated papers |
| chromanol_arom10_CN_tgfb1 | tgfb1 | cheap_compute_or_paper_with_fto_caveat | short_triage_only | in_silico_with_fto_caveat | Markush/FTO review required before heavy follow-up; target evidence yellow: phenotype/cell context required; OECD TG497/ICH S10 safety counterscreen required; formulation rescue before exposure claim | prepare Markush/FTO package; use only completed data for caveated papers |
| chromanol_arom10_CN_tyr | tyr | cheap_compute_or_paper_with_fto_caveat | short_triage_only | in_silico_with_fto_caveat | Markush/FTO review required before heavy follow-up; OECD TG497/ICH S10 safety counterscreen required; formulation rescue before exposure claim | prepare Markush/FTO package; use only completed data for caveated papers |
| chromanol_arom10_Cl_dct | dct | cheap_compute_or_paper_with_fto_caveat | short_triage_only | in_silico_with_fto_caveat | Markush/FTO review required before heavy follow-up; medium IP/FTO/Markush review risk; cross-model/PLIF/negative-control validation required; benchmark decoys or orthogonal structure model required; OECD TG497/ICH S10 safety counterscreen required; CMC/developability yellow gate | prepare Markush/FTO package; use only completed data for caveated papers |
| chromanol_arom10_Cl_tgfb1 | tgfb1 | cheap_compute_or_paper_with_fto_caveat | short_triage_only | in_silico_with_fto_caveat | Markush/FTO review required before heavy follow-up; medium IP/FTO/Markush review risk; target evidence yellow: phenotype/cell context required; cross-model/PLIF/negative-control validation required; benchmark decoys or orthogonal structure model required; OECD TG497/ICH S10 safety counterscreen required; CMC/developability yellow gate | prepare Markush/FTO package; use only completed data for caveated papers |
| chromanol_arom10_Cl_tyr | tyr | cheap_compute_or_paper_with_fto_caveat | short_triage_only | in_silico_with_fto_caveat | Markush/FTO review required before heavy follow-up; medium IP/FTO/Markush review risk; cross-model/PLIF/negative-control validation required; OECD TG497/ICH S10 safety counterscreen required; CMC/developability yellow gate | prepare Markush/FTO package; use only completed data for caveated papers |
| chromanol_arom10_F_dct | dct | cheap_compute_or_paper_with_fto_caveat | short_triage_only | in_silico_with_fto_caveat | Markush/FTO review required before heavy follow-up | prepare Markush/FTO package; use only completed data for caveated papers |
| chromanol_arom10_F_tgfb1 | tgfb1 | cheap_compute_or_paper_with_fto_caveat | short_triage_only | in_silico_with_fto_caveat | Markush/FTO review required before heavy follow-up; target evidence yellow: phenotype/cell context required | prepare Markush/FTO package; use only completed data for caveated papers |
| chromanol_arom10_F_tyr | tyr | cheap_compute_or_paper_with_fto_caveat | short_triage_only | in_silico_with_fto_caveat | Markush/FTO review required before heavy follow-up | prepare Markush/FTO package; use only completed data for caveated papers |
| chromanol_arom10_Me_dct | dct | cheap_compute_or_paper_with_fto_caveat | short_triage_only | in_silico_with_fto_caveat | Markush/FTO review required before heavy follow-up | prepare Markush/FTO package; use only completed data for caveated papers |
| chromanol_arom10_Me_tgfb1 | tgfb1 | cheap_compute_or_paper_with_fto_caveat | short_triage_only | in_silico_with_fto_caveat | Markush/FTO review required before heavy follow-up; target evidence yellow: phenotype/cell context required | prepare Markush/FTO package; use only completed data for caveated papers |
| chromanol_arom10_Me_tyr | tyr | cheap_compute_or_paper_with_fto_caveat | short_triage_only | in_silico_with_fto_caveat | Markush/FTO review required before heavy follow-up | prepare Markush/FTO package; use only completed data for caveated papers |
| chromanol_arom10_OH_dct | dct | cheap_compute_or_paper_with_fto_caveat | short_triage_only | in_silico_with_fto_caveat | Markush/FTO review required before heavy follow-up; OECD TG497/ICH S10 safety counterscreen required; formulation rescue before exposure claim | prepare Markush/FTO package; use only completed data for caveated papers |
| chromanol_arom10_OH_tgfb1 | tgfb1 | cheap_compute_or_paper_with_fto_caveat | short_triage_only | in_silico_with_fto_caveat | Markush/FTO review required before heavy follow-up; target evidence yellow: phenotype/cell context required; OECD TG497/ICH S10 safety counterscreen required; formulation rescue before exposure claim | prepare Markush/FTO package; use only completed data for caveated papers |
| chromanol_arom10_OH_tyr | tyr | cheap_compute_or_paper_with_fto_caveat | short_triage_only | in_silico_with_fto_caveat | Markush/FTO review required before heavy follow-up; OECD TG497/ICH S10 safety counterscreen required; formulation rescue before exposure claim | prepare Markush/FTO package; use only completed data for caveated papers |
| chromanol_arom10_OMe_dct | dct | cheap_compute_or_paper_with_fto_caveat | short_triage_only | in_silico_with_fto_caveat | Markush/FTO review required before heavy follow-up; OECD TG497/ICH S10 safety counterscreen required; formulation rescue before exposure claim | prepare Markush/FTO package; use only completed data for caveated papers |
| chromanol_arom10_OMe_tgfb1 | tgfb1 | cheap_compute_or_paper_with_fto_caveat | short_triage_only | in_silico_with_fto_caveat | Markush/FTO review required before heavy follow-up; target evidence yellow: phenotype/cell context required; OECD TG497/ICH S10 safety counterscreen required; formulation rescue before exposure claim | prepare Markush/FTO package; use only completed data for caveated papers |
| chromanol_arom10_OMe_tyr | tyr | cheap_compute_or_paper_with_fto_caveat | short_triage_only | in_silico_with_fto_caveat | Markush/FTO review required before heavy follow-up; OECD TG497/ICH S10 safety counterscreen required; formulation rescue before exposure claim | prepare Markush/FTO package; use only completed data for caveated papers |
| chromanol_arom6+arom10_Cl+Cl_dct | dct | cheap_compute_or_paper_with_fto_caveat | short_triage_only | in_silico_with_fto_caveat | Markush/FTO review required before heavy follow-up; OECD TG497/ICH S10 safety counterscreen required | prepare Markush/FTO package; use only completed data for caveated papers |
| chromanol_arom6+arom10_Cl+Cl_tgfb1 | tgfb1 | cheap_compute_or_paper_with_fto_caveat | short_triage_only | in_silico_with_fto_caveat | Markush/FTO review required before heavy follow-up; target evidence yellow: phenotype/cell context required; OECD TG497/ICH S10 safety counterscreen required | prepare Markush/FTO package; use only completed data for caveated papers |
| chromanol_arom6+arom10_Cl+Cl_tyr | tyr | cheap_compute_or_paper_with_fto_caveat | short_triage_only | in_silico_with_fto_caveat | Markush/FTO review required before heavy follow-up; OECD TG497/ICH S10 safety counterscreen required | prepare Markush/FTO package; use only completed data for caveated papers |
| chromanol_arom6+arom10_Cl+F_dct | dct | cheap_compute_or_paper_with_fto_caveat | short_triage_only | in_silico_with_fto_caveat | Markush/FTO review required before heavy follow-up; OECD TG497/ICH S10 safety counterscreen required | prepare Markush/FTO package; use only completed data for caveated papers |
| chromanol_arom6+arom10_Cl+F_tgfb1 | tgfb1 | cheap_compute_or_paper_with_fto_caveat | short_triage_only | in_silico_with_fto_caveat | Markush/FTO review required before heavy follow-up; target evidence yellow: phenotype/cell context required; OECD TG497/ICH S10 safety counterscreen required | prepare Markush/FTO package; use only completed data for caveated papers |
| chromanol_arom6+arom10_Cl+F_tyr | tyr | cheap_compute_or_paper_with_fto_caveat | short_triage_only | in_silico_with_fto_caveat | Markush/FTO review required before heavy follow-up; OECD TG497/ICH S10 safety counterscreen required | prepare Markush/FTO package; use only completed data for caveated papers |
| chromanol_arom6+arom10_Cl+Me_dct | dct | cheap_compute_or_paper_with_fto_caveat | short_triage_only | in_silico_with_fto_caveat | Markush/FTO review required before heavy follow-up; OECD TG497/ICH S10 safety counterscreen required | prepare Markush/FTO package; use only completed data for caveated papers |
| chromanol_arom6+arom10_Cl+Me_tgfb1 | tgfb1 | cheap_compute_or_paper_with_fto_caveat | short_triage_only | in_silico_with_fto_caveat | Markush/FTO review required before heavy follow-up; target evidence yellow: phenotype/cell context required; OECD TG497/ICH S10 safety counterscreen required | prepare Markush/FTO package; use only completed data for caveated papers |
| chromanol_arom6+arom10_Cl+Me_tyr | tyr | cheap_compute_or_paper_with_fto_caveat | short_triage_only | in_silico_with_fto_caveat | Markush/FTO review required before heavy follow-up; OECD TG497/ICH S10 safety counterscreen required | prepare Markush/FTO package; use only completed data for caveated papers |
| chromanol_arom6+arom10_Cl+OMe_dct | dct | cheap_compute_or_paper_with_fto_caveat | short_triage_only | in_silico_with_fto_caveat | Markush/FTO review required before heavy follow-up; OECD TG497/ICH S10 safety counterscreen required | prepare Markush/FTO package; use only completed data for caveated papers |
| chromanol_arom6+arom10_Cl+OMe_tgfb1 | tgfb1 | cheap_compute_or_paper_with_fto_caveat | short_triage_only | in_silico_with_fto_caveat | Markush/FTO review required before heavy follow-up; target evidence yellow: phenotype/cell context required; OECD TG497/ICH S10 safety counterscreen required | prepare Markush/FTO package; use only completed data for caveated papers |
| chromanol_arom6+arom10_Cl+OMe_tyr | tyr | cheap_compute_or_paper_with_fto_caveat | short_triage_only | in_silico_with_fto_caveat | Markush/FTO review required before heavy follow-up; OECD TG497/ICH S10 safety counterscreen required | prepare Markush/FTO package; use only completed data for caveated papers |
| chromanol_arom6+arom10_F+Cl_dct | dct | cheap_compute_or_paper_with_fto_caveat | short_triage_only | in_silico_with_fto_caveat | Markush/FTO review required before heavy follow-up; OECD TG497/ICH S10 safety counterscreen required | prepare Markush/FTO package; use only completed data for caveated papers |
| chromanol_arom6+arom10_F+Cl_tgfb1 | tgfb1 | cheap_compute_or_paper_with_fto_caveat | short_triage_only | in_silico_with_fto_caveat | Markush/FTO review required before heavy follow-up; target evidence yellow: phenotype/cell context required; OECD TG497/ICH S10 safety counterscreen required | prepare Markush/FTO package; use only completed data for caveated papers |

## System Gaps Now Covered

- Cross-model/decoy/PLIF gap: `STRUCTURE_CONSENSUS_V2`와 `STRUCTURE_BENCHMARK_DECOY_GATE`를 master gate에 반영한다.
- Free-energy gap: `FREE_ENERGY_VALIDATION_PLAN`, `RBFE_UPGRADE_READINESS`, `MMP1_ZAFF_ABFE_GATE`를 반영한다.
- Prior-art/FTO gap: `PRECOMPUTE_PRIOR_ART_GATE`와 `IP_FTO_WATCHLIST`를 heavy-compute blocker로 반영한다.
- Synthesis/route gap: `SYNTHESIS_RETROSYNTHESIS_GATE`와 `ROUTE_ENUMERATION_GATE`를 반영한다.
- Topical translation gap: dermal regulatory, photosafety, dermal PBPK/IVPT, formulation BO, CMC gate를 반영한다.
- Biology/phenotype gap: target evidence, phenomics, target engagement, DMTL card를 반영한다.
- ML/governance gap: applicability-domain uncertainty와 model governance/provenance caveat를 queue policy에 반영한다.
- Creative discovery gap: active-learning GPU fallback, target MSA coverage, scaffold-hop, synthesis-native generation, cryptic-pocket, ultra-large, reward-benchmark, phenomics-first rules를 반영한다.

## Curator Rule

- `hold_or_benchmark_only`: 비싼 GPU/FE/합성/상업 claim 금지. 논문은 limitation, method, benchmark로만 사용한다.
- `cheap_compute_or_paper_with_fto_caveat`: 이미 끝난 데이터로 caveated in-silico paper는 가능하나 신규 long-MD/FE/synthesis는 보류한다.
- `paper_ready_in_silico`: main table 가능하지만 confirmed binding, clinical efficacy, commercial novelty 표현은 금지한다.
- `wetlab_translation_priority`: 다음 자원 투입은 CRO/wet-lab package가 우선이며, GPU 반복은 보조다.
- active-learning cofold 결과는 완료 즉시 이 matrix에 들어오지만, short triage evidence라 long-MD/FE 승격은 synthesis/prior-art/safety/phenomics/uncertainty gate를 다시 통과해야 한다.
- MC1R/RARG/TLR2/NLRP3처럼 target-key MSA가 없는 target은 cache 준비 전 자동 cofold를 큐잉하지 않는다.
