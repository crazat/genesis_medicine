---
title: "AI 기반 한방 피부재생 신약 개발 + 임상 디지털 전환 통합 플랫폼"
subtitle: "Recover 한의원 × Genesis_Medicine v3"
date: 2026-04-26
program: "NIPA 2025 AI 기반 의료시스템 디지털 전환 지원사업"
applicant: "Recover 한의원 (강남, 2026-08 오픈 예정)"
collaboration: "Genesis_Medicine 연구팀"
---

# 사업 응모 초안 — Recover 한의원 + Genesis_Medicine v3

## 1. 사업 개요

본 사업은 **한국 한방 외용제·복합 처방의 AI 기반 분자 수준 검증 및 임상 적용 디지털 전환**을 목표로, 강남 Recover 한의원의 임상 인프라(AI 안면 분석, 새살침, 매선·약침)와 Genesis_Medicine v3 신약 개발 파이프라인을 통합하여 한방 피부재생 의료의 디지털 표준화를 완성한다.

### 핵심 혁신
1. **AI 분자 수준 검증** — 한방 외용 처방(자운고·당귀음자·황련해독탕)의 핵심 성분이 어떤 단백질 표적에 작용하는지 14단계 SOTA 파이프라인으로 정량화. 처방 효능의 분자 근거 제공.
2. **AI 안면 분석 → 처방 자동화** — 환자 안면 이미지에서 흉터·기미·탈모·여드름·광노화 5대 피부 상태를 자동 분류 후, 분자 수준으로 검증된 한방 처방 자동 추천.
3. **신약 후보 발굴** — Embelin scaffold-hopping으로 도출한 EMB-3 (hERG 0.16, MD 0.79 Å, 흉터 + IPF 6/7 타겟 binding)는 첫 한방 영감 외용 신약 후보.

### 사업화 시점
- **2026-08**: Recover 한의원 강남점 오픈 (의료서비스 매출 시작)
- **2026 Q4**: 첫 신약 후보 EMB-3 in vitro CRO 검증 (₩1,560만)
- **2027**: 외용제 IND 신청 (식약처)

---

## 2. 사업 배경 (왜 지금?)

### 2.1 시장 배경
- **한국 외용제·기능성 화장품 시장**: 2025년 ₩4.2조 (연 12% 성장)
- **글로벌 anti-fibrotic 시장**: 2030년 $35B (IPF·NASH·켈로이드 포함)
- **K-beauty + K-medicine** 융합: 한방 + AI는 한국 고유 경쟁력
- **외국 사례**: Insilico Medicine의 **Rentosertib** (TNIK 저해제) — 첫 generative AI 신약, 2025 IPF Phase 2a 진입 (FVC +98.4 mL). **우리와 같은 파이프라인 구조 = 검증된 모델**

### 2.2 한국 한방 디지털 전환 필요성
- KP/KHP 12판 514종 한약재 디지털화 진행 중
- KIOM (한국한의학연구원) OASIS, 한의학 표준정보 운영 중
- **그러나** 처방의 분자 수준 효능 검증은 미개척 — Genesis_Medicine v3가 직접 메움
- BOKP DNA barcode (Frontiers Pharmacol 2024) — 약재 정량 매핑 표준 등장

### 2.3 AI 의료 디지털 전환 정책 부합성
- NIPA 2025 사업 목표: **"의료기관 AI 도입 + 디지털 전환"**
- Recover 한의원: 환자 진료 기록 + AI 안면 분석 + 분자 수준 처방 검증 = 사례 표준
- 향후 한국 1만 한의원 확장 가능 (전체 한방의료 디지털 인프라)

---

## 3. 사업 내용

### 3.1 핵심 시스템 — Genesis_Medicine v3 (14단계 파이프라인)

```
[질병] → [타겟] → [구조] → [Cryptic Pocket] → [라이브러리] →
[스크리닝] → [Cross-Disease] → [De Novo Generation] →
[ADMET 외용 게이트] → [한약 네트워크] → [MD] →
[CellAwareGNN 재창출] → [Cross-Tissue] → [한국 규제 게이트] →
[ABFE 정량] → [합성 경로] → [CRO/IRB 자동] → [Manuscript]
```

**기술 스택 (모두 commercial 라이선스)**:
- 구조 예측: Boltz-2 (MIT), Protenix-v2 (Apache), OpenFold3 (Apache)
- ADMET: ADMET-AI 2.0.1 + 자체 logKp 헤드 (FDA 2326)
- 생성: PocketXMol (Cell 2026, MIT), REINVENT 4, f-RAG with 한약 fragment
- MD/ABFE: OpenMM 8.5 + openmmtools 0.26 + BAT2
- 천연물 DB: COCONUT 2.0, NPASS 2026, NPAtlas, KP/KHP, BOKP

### 3.2 핵심 검증 결과 (2026-04 기준)

| 지표 | 값 |
|---|---|
| 화합물 라이브러리 | 102 (한방 천연물 90% + 약물재창출 후보) |
| 검증 타겟 | 14 (TGF-β1, MMP-1, CTGF, TYR, MITF, SRD5A2, AR, …) |
| 5질환 파일럿 cofold | 102 × 14 = 1,428 run |
| MD 검증 (10 ns) | 13개 top hit (RMSD < 2 Å) |
| ABFE 정량 (진행 중) | EMB-3 vs Embelin × MMP-1, ΔΔG paper-tier |
| 한방 처방 매핑 | 6 처방 → 9 약재 → 102 성분 → 14 타겟 |
| 발표 paper | EGCG universal (5/5 disease) + EMB-3 multi-tier (IPF cross) — 2편 draft |

### 3.3 Recover 한의원 임상 통합

```
┌──────────────────────────────────────────────────────────┐
│ [환자 내원] → [AI 안면 분석] → [피부 상태 5질환 분류]      │
└────────────────────┬─────────────────────────────────────┘
                     ▼
┌──────────────────────────────────────────────────────────┐
│ [Genesis_Medicine v3] 분자 수준 처방 추천:                │
│   • 흉터 → 자운고 + EMB-3 강화 (자초 shikonin baseline)  │
│   • 기미 → 옥용산 + 감초/녹차 (TYR 결합 입증)             │
│   • 탈모 → 측백엽·하수오 (SRD5A2 입증) + 새살침 자극     │
│   • 여드름 → 황련해독탕 + 베르베린 (염증·여드름 균)        │
│   • 광노화 → 단삼·EGCG (MMP-1 + SIRT1)                    │
└────────────────────┬─────────────────────────────────────┘
                     ▼
┌──────────────────────────────────────────────────────────┐
│ [한방 약침/외용제 시술] → [AI 추적 분석] → [효능 데이터화]│
└──────────────────────────────────────────────────────────┘
```

### 3.4 사업화 산출물

1. **신약 후보 IND 신청** (식약처 외용제, 2027 Q1)
   - EMB-3 (Embelin scaffold-hop) → 흉터 + IPF 외용제
   - 자운고 + EMB-3 강화 복합 처방
2. **AI 안면 분석 + 처방 추천 시스템** (의료기기 인증, 2026 Q4)
3. **한방 디지털 약전 + 분자 수준 매핑 데이터베이스** (오픈 공개)
4. **임상 효능 추적 빅데이터 플랫폼** (다른 한의원 확장 모듈)

---

## 4. 추진 계획 (12개월)

| 분기 | Recover 한의원 | Genesis_Medicine v3 | NIPA 마일스톤 |
|---|---|---|---|
| 2026 Q3 | 강남점 오픈 (8월), 환자 베이스 구축 | Tier 0 SOTA 7개 통합 | 시스템 구축 30% |
| 2026 Q4 | AI 안면 분석 의료기기 인증 | EMB-3 in vitro CRO Tier 1 (₩1,560만) | 60% |
| 2027 Q1 | 첫 임상 데이터 200건 | 외용제 IND 신청 | 90% |
| 2027 Q2 | 사업 마무리 보고 | EMB-3 Phase 1 entry 준비 | 100% |

---

## 5. 예산 (정부지원금 + 자부담 매칭)

| 항목 | 금액 (KRW) | 출처 |
|---|---:|---|
| 인건비 (AI 연구원 2 + 임상 1) | 2.4억 | NIPA 60% + 자부담 40% |
| EMB-3 CRO Tier 1 (KIT/켐온) | 0.16억 | NIPA |
| 합성 (EMB-3 mg scale) | 0.05억 | NIPA |
| GPU 서버 클러스터 확장 | 0.3억 | NIPA |
| 임상 안면 이미지 데이터 구축 | 0.2억 | 자부담 |
| 의료기기 인증 비용 | 0.1억 | 자부담 |
| 외용제 IND 자료 준비 | 0.15억 | NIPA |
| **총** | **3.36억** | NIPA 2.16억 + 자부담 1.2억 |

---

## 6. 차별성 (왜 우리만 할 수 있는가?)

1. **한방 임상 인프라** — Recover 강남점 + 새살침 + AI 안면 분석. **분자 검증 결과를 즉시 임상 적용**할 수 있는 곳은 한국에 거의 없음.
2. **분자 수준 검증 파이프라인 완성도** — 14단계 SOTA 통합 시스템. Insilico Medicine의 미국 사례를 한국 한방 컨텍스트에서 재현.
3. **ABFE 정량 ΔG 도출 능력** — Boltz-2 binary classifier 너머 정량 IC50 nM 추정. 현재 EMB-3 × MMP-1 ABFE 진행 중.
4. **Recover 의료법인이 시장 진입 주체** — 단순 연구가 아닌 즉시 환자 시술 가능한 의료기관.

---

## 7. 위험과 완화

| 위험 | 발생 가능성 | 완화 |
|---|---|---|
| EMB-3 in vitro 결과 음성 | 30% | 추가 lead 4개 (EGCG, Embelin, EMB-1, Asiaticoside) backup 검증 |
| 식약처 외용제 IND 가이드라인 부재 | 20% | OliX OLX104C 한국 IND 패턴 (호주 Phase 1 → 한국) 적용 |
| GPU 인프라 비용 초과 | 15% | RTX 5090 자체 보유 + 클라우드 spot 활용 |
| 한방 마케팅 규제 (HERB DB 인용 금지) | 30% | 발표는 "전통 한방 영감 + 구조 기반 최적화" 표현 (commercial 빌드 라이선스 게이트 통과) |

---

## 8. 첨부 자료 (별도 제출)

- A. Genesis_Medicine v3 GitHub repo (https://github.com/crazat/genesis_medicine)
- B. CLAUDE.md 기술 스택 + 14단계 아키텍처
- C. 검증 결과 manuscript 2편 draft
   - `manuscript_egcg/manuscript.pdf` (EGCG 5/5 disease)
   - `manuscript_emb3/manuscript.pdf` (EMB-3 multi-tier + IPF cross)
- D. CRO 견적 (`pilot/scaffold_hop/cro_quote/`)
- E. 한방 처방 매핑 (`pilot/scaffold_hop/herb_mapping/`)
- F. ABFE 진행 결과 (실시간 업데이트)
- G. Recover 한의원 사업계획서 (https://recover-clinic.kr)

---

## 9. 결론

본 사업은 **한국 한방 의료의 AI 디지털 전환과 글로벌 신약 개발 시장 진입을 동시에 달성**하는 유일한 통합 모델이다. Recover 한의원의 임상 운영과 Genesis_Medicine v3의 SOTA 파이프라인이 결합하여, **NIPA 2025 사업의 지향점인 "AI 의료기관 표준 모델"**을 직접 구현한다.

향후 12개월 내 첫 신약 후보(EMB-3) IND 신청 + AI 안면분석 의료기기 인증 + 한방 디지털 약전 공개라는 명확한 산출물을 약속한다. 이는 단순 R&D가 아닌 **즉시 환자 진료에 적용되는 사업화 모델**이며, 한국 1만 한의원 확장 가능성을 보유한다.

---

**연락처**: research@recover-clinic.kr
**제출 예정일**: 2026-05-31 (NIPA 공모 마감 확인 필요)

⚠️ *본 문서는 초안이며, NIPA 공식 양식·심사 기준에 맞춰 추가 편집 필요.*
