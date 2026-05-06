# Genesis_Medicine 후속 작업 의뢰 — Zenodo 17편 published DOI 확보 완료 (2026-05-04)

> **위치**: 이 파일을 `/home/crazat/genesis_medicine/preprints/ZENODO_RESULT_HANDOFF.md` 로 복사 후 Genesis_Medicine 측 Claude Code 세션에 다음과 같이 전달:
> "다음 파일을 읽고 후속 작업을 진행해. 파일 경로: `/home/crazat/genesis_medicine/preprints/ZENODO_RESULT_HANDOFF.md`"

---

## 1. 핵심 결과: Zenodo 17편 PUBLISHED, DOI 발급 완료

`ZENODO_UPLOAD_AGENT_PROMPT.md` 의 4-phase workflow 를 단축 (Sandbox 생략, production draft → 검수 → publish) 로 실행. 17편 모두 publish 성공.

### 발급된 DOI 17개

| # | Slug | DOI | URL |
|---|---|---|---|
| 1 | embelia_ribes_review | `10.5281/zenodo.20018329` | https://zenodo.org/record/20018329 |
| 3 | emb3_scar_case_study | `10.5281/zenodo.20018333` | https://zenodo.org/record/20018333 |
| 4 | pigmentation_screening | `10.5281/zenodo.20018337` | https://zenodo.org/record/20018337 |
| 5 | alopecia_screening | `10.5281/zenodo.20018339` | https://zenodo.org/record/20018339 |
| 6 | acne_microbiome | `10.5281/zenodo.20018370` | https://zenodo.org/record/20018370 |
| 7 | photoaging_egcg | `10.5281/zenodo.20018372` | https://zenodo.org/record/20018372 |
| 8 | abfe_methodology | `10.5281/zenodo.20018254` | https://zenodo.org/record/20018254 |
| 9 | cross_disease_ipf | `10.5281/zenodo.20018374` | https://zenodo.org/record/20018374 |
| 10 | chronotherapy_jaoryuju | `10.5281/zenodo.20018376` | https://zenodo.org/record/20018376 |
| 12 | open_source_perspective | `10.5281/zenodo.20018343` | https://zenodo.org/record/20018343 |
| 13 | piezo1_mlck_alopecia | `10.5281/zenodo.20018378` | https://zenodo.org/record/20018378 |
| 14 | topical_pbpk_methodology | `10.5281/zenodo.20018345` | https://zenodo.org/record/20018345 |
| 15 | universal_scaffold | `10.5281/zenodo.20018349` | https://zenodo.org/record/20018349 |
| 16 | r15_chromanol_safety_triage | `10.5281/zenodo.20018351` | https://zenodo.org/record/20018351 |
| 17 | r16_topical_chromanol_lead | `10.5281/zenodo.20018353` | https://zenodo.org/record/20018353 |
| 18 | active_learning_multifidelity | `10.5281/zenodo.20018356` | https://zenodo.org/record/20018356 |
| 43 | r17_chromanol_generative_atlas | `10.5281/zenodo.20018359` | https://zenodo.org/record/20018359 |

### 종합 status (2026-05-04)

| 트랙 | published | rejected | pending |
|---|---|---|---|
| Zenodo | **17** ✅ | - | - |
| medRxiv | - | - | 2 (#2, #11, 5/5~6 결정 예상) |
| bioRxiv | - | 19 ❌ | - |
| ChemRxiv | - | 7 ❌ | - |

**Genesis_Medicine has 17 published DOIs as of 2026-05-04.** 8/15 클리닉 오픈 (D-103) 전 학술 trace 확보 완료.

### 제외된 paper

- **#2 recover_workflow** — medRxiv pending (MEDRXIV/2026/351912). medRxiv 결과 후 Zenodo cross-post 또는 메인 트랙으로 진행.
- **#11 korean_pgx_topical** — medRxiv pending (MEDRXIV/2026/351914). 동일.
- **#19 korean_herbal_scaffold_xref** — active research (60 ns MD evidence 추가 중, v0.2 미완). v0.2 frozen 후 Zenodo 추가 deposit.

## 2. 모든 record 의 메타데이터 구조 (Genesis_Medicine 측 참고용)

각 Zenodo record 는 다음과 같이 구성됨:

```yaml
title: <_metadata/{N}_{slug}_metadata.json 의 title>
upload_type: publication
publication_type: preprint
publication_date: <submission_date 필드, 또는 2026-05-04>
description: <manuscript.md 의 ## Abstract section 을 HTML 변환>
creators:
  - name: "Han, Cheongwoo"
    family_name: Han
    given_name: Cheongwoo
    orcid: 0009-0004-4805-8815
    affiliation: "Genesis_Medicine Lab; HAN PREDICT, Inc.; Recover Korean Medicine Clinic"
keywords:
  - in silico
  - drug discovery
  - <subject_area-derived>
  - Korean medicine (해당 시)
  - natural product (해당 시)
  - <legacy keywords (이전 batch)>
notes: |
  COI: HCW is founder of HAN PREDICT, Inc. and consults for Recover Korean Medicine Clinic.
  No external funding for this work.
  In silico only. No wet-lab data and no patient data are reported.
  IRB approval was filed 2026-04-27 and is pending.
  Recover Korean Medicine Clinic opens 2026-08-15.
  Previously screened by bioRxiv (BIORXIV/2026/{nnnnnn}) and not selected for posting;
  deposited to Zenodo as the open-access record.
license: cc-by-4.0
language: eng
access_right: open
version: <_metadata 의 version_at_submission 그대로, v0.2~v0.8>
```

**community 미지정**: `drug-discovery` slug 의 Zenodo community 는 존재하지 않아 비움. 적절한 community 발견 시 cross-submit 가능 (예: `asapdrugdiscovery`, `msca-itn-aidd`, `biosimddlab` 등).

## 3. Genesis_Medicine 에 의뢰하는 후속 작업 (5건)

### 1) `_metadata/<paper>_metadata.json` 17개에 Zenodo DOI 기록
17개 metadata JSON 모두 다음 필드를 채우기 (현재 `null` 상태):
```json
{
  "doi": "10.5281/zenodo.20018329",
  "doi_issued_date": "2026-05-04",
  "zenodo_url": "https://zenodo.org/record/20018329"
}
```
위 표 참고해서 17편 모두 일괄 업데이트.

### 2) `preprints/_metadata/zenodo_published_index.md` 작성
17편 published DOI 의 canonical 인덱스. citation 형식 (예: APA / BibTeX) 도 포함:
```
Han, C. (2026). Embelia ribes (Vidanga, Jadan) revisited:... Zenodo. https://doi.org/10.5281/zenodo.20018329
```

### 3) `preprints/<NN>_<slug>/manuscript.md` 의 frontmatter 에 DOI 추가
17편 manuscript.md 의 YAML frontmatter 에 다음 추가:
```yaml
---
title: ...
authors: ...
zenodo_doi: 10.5281/zenodo.20018329
zenodo_url: https://zenodo.org/record/20018329
zenodo_deposit_date: 2026-05-04
prior_history: bioRxiv BIORXIV/2026/722483 rejected 2026-05-03 (scope mismatch)
---
```

### 4) ORCID Works 동기화 확인 + recover-clinic.kr / hanpredict.com publication list 업데이트
- ORCID 0009-0004-4805-8815 의 Works 섹션 점검 (Zenodo→ORCID auto-push 활성화 시 17편 자동 표시).
- recover-clinic.kr, hanpredict.com 의 "Publications" 또는 "Research" 섹션에 17편 추가 (DOI 링크 포함).

### 5) v1.0 wet-lab integration 후보 1-2편 선정
8/15 클리닉 오픈 후 가장 빠르게 wet-lab data 추가 가능한 paper 1-2편 추천:
- 후보 기준: (a) 단일 화합물 또는 소수 candidate 만 검증하면 됨, (b) 클리닉 case 로 IRB-friendly endpoint, (c) HPLC/cell viability 등 lightweight assay 가능.
- 후보군: #3 emb3_scar (case study 형식), #4 pigmentation, #6 acne_microbiome, #13 piezo1_mlck_alopecia, #16 r15_chromanol_safety_triage 검토.
- 선정 시 v1.0 timeline (예: 2026-09 wet-lab 시작, 2026-12 first results, 2027 Q1 bioRxiv 재시도) 제안.

## 4. 사용자 작업 스타일 (Genesis_Medicine 도 동일하게 적용)

- **중간 확인 질문 금지** — 사용자가 "다 해", "쭉 진행" 류 지시를 한 번 내리면 batch 끝까지 자동 진행.
- 매 작업마다 진척 상황 1-2줄 보고만 (✅ 완료 형태). 장황한 설명 자제.
- 관련 메모리: `feedback_no_unnecessary_pauses.md`, `C:\Users\craza\CLAUDE.md` 의 "사용자 작업 스타일" 섹션.

## 5. 5건 산출물 우선순위 + 예상 시간

| # | 산출물 | 우선순위 | 예상 시간 |
|---|---|---|---|
| 1 | _metadata JSON 17개 DOI 기록 | 🔴 high (citation 가능 상태로) | 5분 |
| 2 | zenodo_published_index.md | 🔴 high (마케팅용) | 15분 |
| 3 | manuscript.md frontmatter DOI 추가 | 🟡 mid (re-deposit 시 참조) | 10분 |
| 4 | ORCID 동기화 + 웹사이트 publication list | 🟡 mid (사용자 액션 필요) | 보고만 |
| 5 | v1.0 wet-lab 후보 분석 1쪽 | 🟢 low (장기 전략) | 30분 |

## 6. 추가 참고

- 자동화 스크립트는 `C:\Users\craza\zenodo_upload.py`, `C:\Users\craza\zenodo_publish.py`, `run_zenodo.sh`, `run_publish.sh` 에 보관됨. 향후 #2, #11 medRxiv 결과 후 또는 #19 v0.2 frozen 시 동일 스크립트 재사용 가능.
- Zenodo API token 은 1회용. 재사용 시 사용자 (HCW) 가 https://zenodo.org/account/settings/applications/tokens/new/ 에서 새로 발급.
- 함정 모음 (재발 방지):
  - `related_identifiers.relation` 값 case-sensitive ("isAlternateIdentifierOf" 등 InvenioRDM 표준 enum 만 허용).
  - title 에 markdown italic asterisk → publish 전 PUT API 로 fix.
  - 한글/한자 UTF-8 정상 저장 (Windows console 표시만 깨짐).
  - Idempotency 없음 — 동일 paper 두 번 업로드 시 중복. DELETE `/api/deposit/depositions/{id}` 로 unsubmitted 만 삭제 가능.
  - drug-discovery slug community 없음, 비우는 게 안전.

---

**의뢰 형식**: 위 5개 작업 후 사용자에게 핵심 1-2 단락 + Genesis_Medicine 입장 다음 priority action 1개 추천. 각 산출물은 `/home/crazat/genesis_medicine/preprints/` 또는 `_metadata/` 안에 저장.
