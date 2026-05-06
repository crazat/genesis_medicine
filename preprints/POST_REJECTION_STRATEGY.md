# Genesis_Medicine 후속 전략 수립 의뢰 (2026-05-04)

> **위치**: 이 파일을 `/home/crazat/genesis_medicine/preprints/POST_REJECTION_STRATEGY.md` 로 복사 후 Genesis_Medicine 측 Claude Code 세션에 다음과 같이 전달:
> "다음 파일을 읽고 후속 전략을 제안해. 파일 경로: `/home/crazat/genesis_medicine/preprints/POST_REJECTION_STRATEGY.md`"

---

## 1. 핵심 사실: bioRxiv 19편 전수 Reject

2026-05-03 bioRxiv 에 17편 신규/재제출 + 이전 4/28 거절 2편 = **합계 19편 모두 Reject** (5/4 dashboard 재확인). 이전 메모에 "19편 New status, screening 대기" 로 잘못 기록됐던 것을 5/4 audit 으로 발견.

### 거절 사유 (screener 표준 문구 2종, 의미 동일)

> 1. "We regret to inform you that your manuscript is inappropriate for bioRxiv. All submissions are screened to ensure they match bioRxiv posting criteria and scope. **bioRxiv is intended for complete research papers with new data/analysis and your submission does not fall into that article type.**"
>
> 2. "During the screening process our affiliate scientists determined that **this manuscript is not a complete research manuscript within the scope of bioRxiv**."

### 거절된 19편 ID

| # | Slug | bioRxiv ID | Reject Date |
|---|---|---|---|
| 1 | embelia_ribes_review | BIORXIV/2026/722483 | 2026-05-03 |
| 3 | emb3_scar_case_study | BIORXIV/2026/722476 | 2026-05-03 |
| 4 | pigmentation_screening v0.3 | BIORXIV/2026/722471 | 2026-05-03 |
| 4 v1 | pigmentation_screening v1 | BIORXIV/2026/721241 | 2026-04-28 |
| 5 | alopecia_screening v0.3 | BIORXIV/2026/722473 | 2026-05-03 |
| 5 v1 | alopecia_screening v1 | BIORXIV/2026/721248 | 2026-04-28 |
| 6 | acne_microbiome | BIORXIV/2026/721254 | 2026-05-03 |
| 7 | photoaging_egcg | BIORXIV/2026/721257 | 2026-05-03 |
| 8 | abfe_methodology | BIORXIV/2026/722479 | 2026-05-03 |
| 9 | cross_disease_ipf | BIORXIV/2026/721261 | 2026-05-03 |
| 10 | chronotherapy_jaoryuju | BIORXIV/2026/721263 | 2026-05-03 |
| 12 | open_source_perspective | BIORXIV/2026/722485 | 2026-05-03 |
| 13 | piezo1_mlck_alopecia | BIORXIV/2026/721264 | 2026-05-03 |
| 14 | topical_pbpk_methodology | BIORXIV/2026/722481 | 2026-05-03 |
| 15 | universal_scaffold | BIORXIV/2026/722463 | 2026-05-03 |
| 16 | r15_chromanol_safety_triage | BIORXIV/2026/722464 | 2026-05-03 |
| 17 | r16_topical_chromanol_lead | BIORXIV/2026/722467 | 2026-05-03 |
| 18 | active_learning_multifidelity v0.1 | BIORXIV/2026/722486 | 2026-05-03 |
| 43 | r17_chromanol_generative_atlas | BIORXIV/2026/722468 | 2026-05-03 |

### v0.3/v0.4/v0.8 reframing 도 효과 없음

- 4 layer evidence stack (Boltz-2 cofold + ChEMBL pIC50 anchor + 30-200 ns MD + ADMET-AI 107-endpoint) 강조 → 거절
- ABFE T4 lysozyme L99A · benzene calibration 추가 → 거절
- Dancik 4-layer ODE + LightGBM logKp 102-compound 4-vehicle eval → 거절
- 7-tool active core + 40+ adapter scaffold + multi-fidelity BO scheduler → 거절
- ASCII sanitize + Romanized title (Vidanga, Jadan) → 거절

→ **screener 가 in silico computational/screening/methodology/framework 을 일괄 "wet-lab data 없으면 not complete research" 판정**. paper 형식 보정으로 우회 불가능.

## 2. 종합 status (2026-05-04)

| 트랙 | 제출 | 거절 | 잔존 |
|---|---|---|---|
| bioRxiv | 19 | 19 (100%) | 0 |
| medRxiv | 2 | 0 | 2 (New, screening 진행 중) |
| ChemRxiv | 7 | 7 (100%, 4/30 curator) | 0 |
| **합계** | **28** | **26 (93%)** | **2** |

- ChemRxiv curator (Ben Mudrak, Senior PM) 2026-04-30 letter: "we don't feel that the nature and style of your research fits with what we post on ChemRxiv. As such, we request that you use another preprint service for your research findings."
- medRxiv 잔존 2편: MEDRXIV/2026/351912 (#2 Recover workflow), MEDRXIV/2026/351914 (#11 Korean PGx topical) — 5/5~5/6 결정 예상.
- **published DOI: 0편**.

## 3. Genesis_Medicine 측 결정 필요 사항

### A. 트랙 재선택 (각 paper 별로)

bioRxiv/ChemRxiv 트랙은 닫힘. 각 paper 를 어디로 보낼지 분류 필요:

1. **medRxiv 가능성 있는 paper** (clinical-link 가 명확한 것):
   - #2 recover_workflow (이미 제출 중)
   - #11 korean_pgx_topical (이미 제출 중)
   - 추가 후보: #6 acne_microbiome, #7 photoaging_egcg, #10 chronotherapy_jaoryuju, #13 piezo1_mlck_alopecia, #14 topical_pbpk_methodology — 임상 적용성을 본문 reframing 으로 강화하면 medRxiv 가능?
   - **Genesis_Medicine 판단 필요**: 어느 paper 가 medRxiv "clinical relevance" 기준 충족 가능한지?

2. **arXiv q-bio.BM / cs.LG 가능 paper** (computational methodology / ML):
   - #8 abfe_methodology (Biophysics → q-bio.BM)
   - #12 open_source_perspective (Bioinformatics → cs.LG / q-bio.BM)
   - #14 topical_pbpk_methodology (q-bio.QM)
   - #18 active_learning_multifidelity (cs.LG)
   - #43 r17_chromanol_generative_atlas (q-bio.BM)
   - **endorsement 필요할 수 있음** → 첫 paper 만 endorser 확보 후 나머지 자가 제출 가능.

3. **Zenodo / OSF Preprints (즉시 DOI, peer review 없음)**:
   - 모든 거절된 paper 가 즉시 DOI 받을 수 있음.
   - 단점: peer review 트랙이 아니라 학술적 weight 약함.
   - 장점: 클리닉 오픈 (8/15) 전 "DOI 보유 paper N편" 마케팅 가능.
   - **Genesis_Medicine 판단 필요**: 19편 모두 Zenodo 일괄 업로드할지, 핵심 5-6편만 선별할지?

4. **Research Square / Preprints.org / Authorea (lighter screening)**:
   - in silico 수용성 높음. screening 통과 가능성 큼.
   - DOI 발급 + searchable.

### B. v1.0 wet-lab integration 전략 (장기)

- IRB 신청 2026-04-27 → 승인 timeline?
- Recover Korean Medicine Clinic 8/15 오픈 후 case study 가능?
- 한 paper 에라도 wet-lab data 1 항목 추가 (예: HPLC validation, 환자 case n=5, in vitro IC50 1개) 시 bioRxiv 재시도 가능 → 어느 paper 가 가장 빠르게 wet-lab evidence 받을 수 있는지?

### C. manuscript 본문 수정이 필요한지 vs 트랙만 변경하면 되는지

각 paper 별로:
- **트랙만 변경 (Zenodo/arXiv)**: 본문 수정 불요. 즉시 업로드 가능.
- **medRxiv reframing**: clinical relevance / pharmacogenomic / case study angle 강화 필요. 본문 수정 1-3일.
- **bioRxiv 재시도 보류**: wet-lab data 추가 후만 재시도.

## 4. Genesis_Medicine 에 의뢰하는 작업

다음 4개 산출물 부탁:

### 1) `preprints/POST_REJECTION_TRACK_PLAN.md` 작성
19 거절 paper + 2 medRxiv 진행 paper + 7 ChemRxiv 거절 paper 각각에 대해:
- 권장 트랙 (medRxiv / arXiv / Zenodo / OSF / Research Square / wet-lab 대기)
- 본문 수정 필요 여부 + 수정 방향
- 우선순위 (8/15 클리닉 오픈 전 DOI 확보 관점)

### 2) `preprints/MEDRXIV_RESCUE_CANDIDATES.md` 작성
19 거절 bioRxiv paper 중 medRxiv 로 reframe 가능한 후보 + 각 paper 의 "clinical relevance hook" 제안 (어떤 단락 추가 / 어떤 강조 변경).

### 3) `preprints/ZENODO_BATCH_PLAN.md` 작성
Zenodo (또는 OSF Preprints) 일괄 업로드 시 메타데이터, community 선택 (예: zenodo community "drug-discovery" 등), version 정책 (v0.3 그대로 vs v1.0 으로 bump), DOI 인용 형식.

### 4) v1.0 wet-lab integration 로드맵 1쪽
8/15 클리닉 오픈 일정과 연동해서 어느 paper 가 wet-lab data 받기 가장 쉬운지, IRB 승인 timeline 과 정합성, 6개월 내 bioRxiv 재시도 목표 paper 1-2편 추천.

## 5. 제약 / 함정

- ORCID-linked email: `crazat7@gmail.com` 만 사용. `admin@hanpredict.com` 는 일부 시스템에서 ORCID account email mismatch 로 Approve disabled.
- IRB 승인 전이므로 wet-lab claim 금지 ("In silico only. Wet-lab and IRB pending.").
- COI 표준 문구: "HCW is founder of HAN PREDICT, Inc. and consults for Recover Korean Medicine Clinic. No external funding for this work." (단축형, 2026-05-03 이후 사용).
- License: CC-BY 4.0.
- author single (Cheongwoo Han), ORCID 0009-0004-4805-8815, affiliation: Genesis_Medicine Lab / HAN PREDICT, Inc. / Recover Korean Medicine Clinic.

## 6. 사용자 (Cheongwoo Han) 의 우선순위

1. **8/15 클리닉 오픈 전 published DOI 확보가 최우선**. peer review 약해도 Zenodo DOI 라도 있으면 마케팅 가능.
2. **2번째 우선**: 학술적 weight 있는 트랙 (arXiv / medRxiv / Research Square) 통과.
3. **3번째**: 장기적으로 wet-lab data 추가해서 bioRxiv 진입.
4. 시간 / 비용 부담 큰 wet-lab 은 IRB 승인 + 클리닉 오픈 후 case 누적 시점부터.

---

**의뢰 형식**: 위 4개 산출물 작성 후 사용자에게 핵심 요약 1-2 단락 + 권장 first-action 1개 (가장 빠른 DOI 확보 경로) 보고. 각 산출물 파일은 `/home/crazat/genesis_medicine/preprints/` 안에 저장.
