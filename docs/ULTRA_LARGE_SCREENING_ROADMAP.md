# Ultra-large Screening Roadmap

- timestamp: `2026-05-06T12:46:33+09:00`
- rows: `50`
- purpose: NPASS-scale local screen을 ZINC/Enamine REAL급 ultra-large active-learning campaign으로 확장하기 위한 단계별 큐다.

## Stages

| stage | target | scope | nominal size | status | queue rule |
|---|---|---|---:|---|---|
| stage0_local_surrogate | ctgf | local NPASS/R15/R16 candidate pool | 672 | already available | refresh active-learning surrogate and remove duplicate labeled pairs |
| stage0_local_surrogate | lox | local NPASS/R15/R16 candidate pool | 672 | already available | refresh active-learning surrogate and remove duplicate labeled pairs |
| stage0_local_surrogate | mmp1 | local NPASS/R15/R16 candidate pool | 672 | already available | refresh active-learning surrogate and remove duplicate labeled pairs |
| stage0_local_surrogate | dct | local NPASS/R15/R16 candidate pool | 672 | already available | refresh active-learning surrogate and remove duplicate labeled pairs |
| stage0_local_surrogate | mc1r | local NPASS/R15/R16 candidate pool | 672 | already available | refresh active-learning surrogate and remove duplicate labeled pairs |
| stage0_local_surrogate | nr3c1 | local NPASS/R15/R16 candidate pool | 672 | already available | refresh active-learning surrogate and remove duplicate labeled pairs |
| stage1_orderable_subset | ctgf | ZINC/Enamine/REAL purchasable subset | 50000 | future lightweight download | screen descriptors and apply synthesis/dermal gates before docking |
| stage1_orderable_subset | lox | ZINC/Enamine/REAL purchasable subset | 50000 | future lightweight download | screen descriptors and apply synthesis/dermal gates before docking |
| stage1_orderable_subset | mmp1 | ZINC/Enamine/REAL purchasable subset | 50000 | future lightweight download | screen descriptors and apply synthesis/dermal gates before docking |
| stage1_orderable_subset | dct | ZINC/Enamine/REAL purchasable subset | 50000 | future lightweight download | screen descriptors and apply synthesis/dermal gates before docking |
| stage1_orderable_subset | mc1r | ZINC/Enamine/REAL purchasable subset | 50000 | future lightweight download | screen descriptors and apply synthesis/dermal gates before docking |
| stage1_orderable_subset | nr3c1 | ZINC/Enamine/REAL purchasable subset | 50000 | future lightweight download | screen descriptors and apply synthesis/dermal gates before docking |
| stage2_active_docking | ctgf | active-learning selected purchasable compounds | 5000 | future CPU/GPU window | dock/cofold only top acquisition batches for green targets |
| stage2_active_docking | lox | active-learning selected purchasable compounds | 5000 | future CPU/GPU window | dock/cofold only top acquisition batches for green targets |
| stage2_active_docking | mmp1 | active-learning selected purchasable compounds | 5000 | future CPU/GPU window | dock/cofold only top acquisition batches for green targets |
| stage2_active_docking | dct | active-learning selected purchasable compounds | 5000 | future CPU/GPU window | dock/cofold only top acquisition batches for green targets |
| stage2_active_docking | mc1r | active-learning selected purchasable compounds | 5000 | future CPU/GPU window | dock/cofold only top acquisition batches for green targets |
| stage2_active_docking | nr3c1 | active-learning selected purchasable compounds | 5000 | future CPU/GPU window | dock/cofold only top acquisition batches for green targets |
| stage3_synthon_space | ctgf | synthon/V-SYNTHES style enumerated space | 1000000 | future design campaign | enumerate analogs around chromanol/pterocarpan motifs |
| stage3_synthon_space | lox | synthon/V-SYNTHES style enumerated space | 1000000 | future design campaign | enumerate analogs around chromanol/pterocarpan motifs |
| stage3_synthon_space | mmp1 | synthon/V-SYNTHES style enumerated space | 1000000 | future design campaign | enumerate analogs around chromanol/pterocarpan motifs |
| stage3_synthon_space | dct | synthon/V-SYNTHES style enumerated space | 1000000 | future design campaign | enumerate analogs around chromanol/pterocarpan motifs |
| stage3_synthon_space | mc1r | synthon/V-SYNTHES style enumerated space | 1000000 | future design campaign | enumerate analogs around chromanol/pterocarpan motifs |
| stage3_synthon_space | nr3c1 | synthon/V-SYNTHES style enumerated space | 1000000 | future design campaign | enumerate analogs around chromanol/pterocarpan motifs |
| stage4_wetlab_shortlist | ctgf | CRO-orderable shortlist | 30 | after cofold/MD/safety | single-point phenotype or IVRT/IVPT confirmation |
| stage4_wetlab_shortlist | lox | CRO-orderable shortlist | 30 | after cofold/MD/safety | single-point phenotype or IVRT/IVPT confirmation |
| stage4_wetlab_shortlist | mmp1 | CRO-orderable shortlist | 30 | after cofold/MD/safety | single-point phenotype or IVRT/IVPT confirmation |
| stage4_wetlab_shortlist | dct | CRO-orderable shortlist | 30 | after cofold/MD/safety | single-point phenotype or IVRT/IVPT confirmation |
| stage4_wetlab_shortlist | mc1r | CRO-orderable shortlist | 30 | after cofold/MD/safety | single-point phenotype or IVRT/IVPT confirmation |
| stage4_wetlab_shortlist | nr3c1 | CRO-orderable shortlist | 30 | after cofold/MD/safety | single-point phenotype or IVRT/IVPT confirmation |
| stage0_top_active_learning_seed | dct | npass_xtb_best_cross_target | 1 | acquisition=0.6534 | seed future purchasable analog search around NPC243469 |
| stage0_top_active_learning_seed | dct | npass_xtb_best_cross_target | 1 | acquisition=0.6534 | seed future purchasable analog search around NPC194985 |
| stage0_top_active_learning_seed | dct | npass_xtb_best_cross_target | 1 | acquisition=0.6534 | seed future purchasable analog search around NPC196715 |
| stage0_top_active_learning_seed | dct | npass_xtb_best_cross_target | 1 | acquisition=0.6534 | seed future purchasable analog search around NPC261839 |
| stage0_top_active_learning_seed | dct | npass_xtb_best_cross_target | 1 | acquisition=0.6534 | seed future purchasable analog search around NPC469970 |
| stage0_top_active_learning_seed | ctgf | npass_xtb_best_cross_target | 1 | acquisition=0.6378 | seed future purchasable analog search around NPC243469 |
| stage0_top_active_learning_seed | lox | npass_xtb_best_cross_target | 1 | acquisition=0.6378 | seed future purchasable analog search around NPC243469 |
| stage0_top_active_learning_seed | mmp1 | npass_xtb_best_cross_target | 1 | acquisition=0.6378 | seed future purchasable analog search around NPC243469 |
| stage0_top_active_learning_seed | mc1r | npass_xtb_best_cross_target | 1 | acquisition=0.6378 | seed future purchasable analog search around NPC243469 |
| stage0_top_active_learning_seed | nr3c1 | npass_xtb_best_cross_target | 1 | acquisition=0.6378 | seed future purchasable analog search around NPC243469 |

## Curator Rule

- 현재 CPU/GPU 포화 상태에서는 stage0 문서화만 수행한다.
- stage1 이상은 외부 library download/라이선스/저장공간을 확인한 뒤 별도 큐로 올린다.
- ultra-large campaign은 full docking이 아니라 active-learning 압축 screen으로만 설계한다.
