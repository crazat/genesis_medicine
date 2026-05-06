# Creative Discovery Gap Matrix

- timestamp: `2026-05-06T12:46:36+09:00`
- matrix_csv: `pilot/cpu_meaningful/creative_discovery_gap_matrix.csv`
- queue_policy_json: `pilot/creative_discovery_queue_policy.json`
- active-learning pending short-cofold pairs: `160`
- active-learning runnable short-cofold pairs: `0`
- active-learning blocked missing-MSA pairs: `160`
- active-learning in-flight manifest rows: `496`
- active-learning completed cofold result rows: `480`
- target-key A3M missing: `14` / `31`

## Meaning

이 파일은 창의적 신물질 발굴 기술이 실제 큐 정책에 연결됐는지 보는 상위 점검표다. 점수가 좋은 후보라도 synthesis, prior-art/FTO, novelty/diversity, phenomics, target cache, ensemble-pocket gate가 없으면 long-MD/FE/lead claim으로 자동 승격하지 않는다.

## Matrix

| priority | layer | status | evidence | readiness gate | compute policy | next queue action |
|---|---|---|---|---|---|---|
| P0 | active_learning_gpu_fallback | implemented_running | active-learning rows=672; pending short-cofold pairs=160; runnable=0; blocked missing-MSA pairs=160; manifests=496; completed result rows=480 | short_triage_allowed_only | GPU-free windows may run short Boltz-2 cofold; long MD/FE still require master-gate promotion | continue non-duplicate active-learning cofold batches; send hits back to master gate before MD |
| P0 | target_msa_coverage | gap_detected | skin target configs=31; available target A3M=17; missing target A3M=14 | block_target_specific_cofold_for_missing_msa | targets without target-key A3M are not eligible for automatic cofold queueing | prepare missing target-key MSA/sequence cache before queueing MC1R/RARG/TLR2/NLRP3-style targets |
| P0 | synthesis_native_generation | partial_post_filter_only | synthesis gate rows=112; route enumeration rows=1082; AiZynthFinder installed=False; ASKCOS cli installed=False | generation_requires_route_or_building_block_guard | generate-first/filter-later is not enough for expensive follow-up | add reaction-template/building-block enumeration lane before expanding non-chromanol designs |
| P0 | scaffold_hopping_shape_pharmacophore | partial_chromanol_constrained_only | chromanol generator rows=330; no separate shape/pharmacophore scaffold-hop queue detected | new_scaffold_requires_novelty_synthesis_uncertainty_gate | cheap CPU descriptors/enumeration allowed; heavy GPU requires prior-art and synthesis guard | create scaffold-hop queue around stable R16/R17 pharmacophores instead of only substituent scans |
| P1 | cryptic_pocket_dynamic_ensemble | static_pocket_gate_only | pocket evidence rows=31; no dynamic cryptic-pocket ensemble output detected | ensemble_pocket_required_before_pocket_specific_generation | do not claim cryptic/allosteric binding from static cofold alone | add ensemble pocket scout shortlist; only then launch pocket-specific generation |
| P1 | ultra_large_tangible_space | roadmap_only | ultra-large roadmap rows=50; no licensed library download/stage1 embedding output detected | license_storage_stage1_required | do not brute-force large libraries; use active-learning compression | prepare ZINC/REAL/Enamine subset license/storage checklist, then CPU embedding pre-screen |
| P1 | reward_hacking_novelty_benchmark | partial_decoy_gate_only | structure benchmark rows=32; no MolScore/Tartarus-style generative benchmark matrix detected | new_generator_requires_benchmark_and_decoys | affinity-only optimization cannot promote a molecule to lead status | add diversity/novelty/synthesis/decoy benchmark table for every new generator lane |
| P1 | phenomics_first_generation | partial_gate_only | phenomics rows=752; generator score still not phenomics-objective-native | phenotype_objective_required_for_moa_claim | Cell Painting/JUMP-style evidence should guide generation when direct pocket evidence is weak | feed disease-cell phenotype priority into next acquisition/generation score |
| P2 | new_modality_lanes | planned_gate_only | modality novelty doc exists=True; covalent/allosteric/glue/macrocycle generator lane not detected | high_risk_modality_requires_separate_safety_ip_gate | do not mix high-risk modality claims into ordinary topical small-molecule queue | keep covalent/allosteric/degrader/glue/macrocycle as separate benchmark or future-work lanes |
| P2 | agentic_hypothesis_evolution | partial_deterministic_curator | world-class master gate exists=True; creative matrix now generated | curator_must_read_creative_matrix_each_tick | LLM-style hypothesis generation must remain auditable and gate-bound | use this matrix in curator loop context before choosing the next queue |

## Target Cache Gap

- target-specific Boltz-2 cofold는 `data/msa/{target}.a3m`가 없으면 자동 큐잉하지 않는다.
- missing target-key A3M examples: `col1a1, f2rl1, mc1r, mmp3, mmp9, mylk, nlrp3, nr3c1, piezo1, ptgdr2, rarg, srebf1, tlr2, wnt10b`

## Curator Rules

- GPU가 비면 active-learning short Boltz-2 cofold는 허용한다. 단 결과는 triage이며, master gate 통과 전 long-MD/FE로 올리지 않는다.
- 새 scaffold 생성은 docking/affinity 단일 목적 최적화가 아니라 novelty, synthesis, prior-art, uncertainty, phenomics guard를 동시에 요구한다.
- chromanol 주변 치환체 탐색과 별도로 shape/pharmacophore scaffold-hop lane을 만들어야 한다.
- cryptic/allosteric pocket 주장은 static cofold가 아니라 ensemble pocket scout 이후에만 쓴다.
- phenomics-first 후보는 직접 target binding보다 disease-cell phenotype rescue objective를 우선한다.
