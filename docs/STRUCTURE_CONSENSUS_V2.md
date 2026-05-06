# Structure Consensus V2

- timestamp: `2026-05-06T12:46:11+09:00`
- rows: `32`
- claim_counts: `{'claim_ready_in_silico': 0, 'claim_with_caveat': 8, 'needs_cross_model': 5, 'triage_only': 19}`
- purpose: single-model Boltz claim을 피하고, PoseBusters/MD/pocket/applicability-domain을 합쳐 orthogonal validation priority를 정한다.

## Top Claim-Readiness Rows

| job | target | compound | readiness | score | pose | MD | pocket | next |
|---|---|---|---|---:|---|---|---|---|
| r16_03_dct | dct | R15_chromanol_Cl_pos9 | claim_with_caveat | 0.7338 | pass | long_stable | direct_pocket_plausible | supplement/main-candidate table; request cross-model consensus before strong claim |
| r16_02_dct | dct | R15_chromanol_Cl_pos6 | claim_with_caveat | 0.7276 | pass | long_stable | direct_pocket_plausible | supplement/main-candidate table; request cross-model consensus before strong claim |
| r16_02_tyr | tyr | R15_chromanol_Cl_pos6 | claim_with_caveat | 0.7262 | pass | long_stable | direct_pocket_plausible | supplement/main-candidate table; request cross-model consensus before strong claim |
| r16_05_tgfb1 | tgfb1 | R15_chromanol_Me6_Me9 | claim_with_caveat | 0.6803 | pass | long_stable | interface_or_biologic | supplement/main-candidate table; request cross-model consensus before strong claim |
| r16_02_tgfb1 | tgfb1 | R15_chromanol_Cl_pos6 | claim_with_caveat | 0.6661 | pass | long_stable | interface_or_biologic | supplement/main-candidate table; request cross-model consensus before strong claim |
| r16_03_tgfb1 | tgfb1 | R15_chromanol_Cl_pos9 | claim_with_caveat | 0.6657 | review | long_stable | interface_or_biologic | supplement/main-candidate table; request cross-model consensus before strong claim |
| r16_06_tgfb1 | tgfb1 | R15_chromanol_Me9_Me10 | claim_with_caveat | 0.6536 | review | long_stable | interface_or_biologic | supplement/main-candidate table; request cross-model consensus before strong claim |
| r16_04_tgfb1 | tgfb1 | R15_chromanol_Me6_Me10 | claim_with_caveat | 0.6434 | review | long_stable | interface_or_biologic | supplement/main-candidate table; request cross-model consensus before strong claim |
| r16_01_tgfb1 | tgfb1 | R15_chromanol_Cl_pos10 | needs_cross_model | 0.636 | review | long_stable | interface_or_biologic | run Chai-1/DiffDock/Vina or PLIF/negative-control check before manuscript lead claim |
| r15_chrom_tyr | tyr | R15_chromanol | needs_cross_model | 0.5927 | pass | missing | direct_pocket_plausible | run Chai-1/DiffDock/Vina or PLIF/negative-control check before manuscript lead claim |
| r15_chrom_ptgs2 | ptgs2 | R15_chromanol | triage_only | 0.5869 | pass | missing | direct_pocket_plausible | keep as queue candidate or negative-control/failure-mode evidence |
| r16_03_tyr | tyr | R15_chromanol_Cl_pos9 | triage_only | 0.5772 | pass | missing | direct_pocket_plausible | keep as queue candidate or negative-control/failure-mode evidence |
| r15_chrom_dct | dct | R15_chromanol | needs_cross_model | 0.5713 | review | missing | direct_pocket_plausible | run Chai-1/DiffDock/Vina or PLIF/negative-control check before manuscript lead claim |
| r16_01_dct | dct | R15_chromanol_Cl_pos10 | needs_cross_model | 0.569 | review | missing | direct_pocket_plausible | run Chai-1/DiffDock/Vina or PLIF/negative-control check before manuscript lead claim |
| r16_01_tyr | tyr | R15_chromanol_Cl_pos10 | triage_only | 0.5684 | pass | missing | direct_pocket_plausible | keep as queue candidate or negative-control/failure-mode evidence |
| r15_chrom_tyrp1 | tyrp1 | R15_chromanol | triage_only | 0.5683 | pass | missing | direct_pocket_plausible | keep as queue candidate or negative-control/failure-mode evidence |
| r16_06_tyr | tyr | R15_chromanol_Me9_Me10 | triage_only | 0.5537 | pass | missing | direct_pocket_plausible | keep as queue candidate or negative-control/failure-mode evidence |
| r16_05_tyr | tyr | R15_chromanol_Me6_Me9 | triage_only | 0.5527 | pass | missing | direct_pocket_plausible | keep as queue candidate or negative-control/failure-mode evidence |
| r16_05_dct | dct | R15_chromanol_Me6_Me9 | triage_only | 0.5476 | pass | missing | direct_pocket_plausible | keep as queue candidate or negative-control/failure-mode evidence |
| r16_06_dct | dct | R15_chromanol_Me9_Me10 | triage_only | 0.5472 | pass | missing | direct_pocket_plausible | keep as queue candidate or negative-control/failure-mode evidence |
| r16_04_tyr | tyr | R15_chromanol_Me6_Me10 | triage_only | 0.5192 | review | missing | direct_pocket_plausible | keep as queue candidate or negative-control/failure-mode evidence |
| r16_04_dct | dct | R15_chromanol_Me6_Me10 | triage_only | 0.5082 | review | missing | direct_pocket_plausible | keep as queue candidate or negative-control/failure-mode evidence |
| r15_chrom_tgfb1 | tgfb1 | R15_chromanol | needs_cross_model | 0.5054 | review | missing | interface_or_biologic | run Chai-1/DiffDock/Vina or PLIF/negative-control check before manuscript lead claim |
| r15_chrom_mmp1 | mmp1 | R15_chromanol | triage_only | 0.4861 | review | missing | direct_pocket_plausible | keep as queue candidate or negative-control/failure-mode evidence |
| r15_chrom_srd5a2 | srd5a2 | R15_chromanol | triage_only | 0.4742 | pass | missing | direct_pocket_plausible | keep as queue candidate or negative-control/failure-mode evidence |
| r15_chrom_ar | ar | R15_chromanol | triage_only | 0.4543 | pass | missing | direct_pocket_plausible | keep as queue candidate or negative-control/failure-mode evidence |
| r15_chrom_lox | lox | R15_chromanol | triage_only | 0.4508 | pass | missing | direct_pocket_plausible | keep as queue candidate or negative-control/failure-mode evidence |
| r15_chrom_sirt1 | sirt1 | R15_chromanol | triage_only | 0.4141 | review | missing | unknown | keep as queue candidate or negative-control/failure-mode evidence |
| r15_chrom_srd5a1 | srd5a1 | R15_chromanol | triage_only | 0.4003 | pass | missing | direct_pocket_plausible | keep as queue candidate or negative-control/failure-mode evidence |
| r15_chrom_srebp1 | srebp1 | R15_chromanol | triage_only | 0.3939 | pass | missing | missing | keep as queue candidate or negative-control/failure-mode evidence |

## Curator Rule

- `claim_ready_in_silico`: 논문 main table 가능. 단, `in silico`와 orthogonal-model 미실행 caveat를 유지한다.
- `claim_with_caveat`: 보조 표 또는 제한적 main candidate. cross-model 또는 wet-lab 전까지 binding-confirmed 표현 금지.
- `needs_cross_model`: Chai-1/DiffDock/Vina/PLIF/negative-control 중 하나 이상을 먼저 큐잉한다.
- `triage_only`: 후보 탐색 또는 failure-mode paper에만 사용한다.
