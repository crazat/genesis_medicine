# MFDS 화장품-의약품 경계 + K-Bio M&A Landscape (2026-04)

> Tier 11-15 산출물. Genesis_Medicine v3 + Recover 한의원 BD/regulatory 인텔리전스.
> **비용 거의 0 / ROI Very High** (변리사·법무 컨택 1일).

---

## 1. MFDS 화장품-의약품 경계 가이드라인 (2026 개정)

### 1.1 트랙 매핑

| 제품 카테고리 | 기존 | 2026 개정안 | 적합 EMB-3 외용제 |
|---|---|---|:-:|
| 일반 화장품 | 효능 claim 제한 | (변경 없음) | ✗ |
| **기능성 화장품** | 11개 효능 (2025) | **+흉터 개선** (2026-Q3 예상) | ⭐⭐ 1차 진입 |
| **유사 의약품** | 2025 신설 | 외용 한약 연속 트랙 | ⭐⭐⭐ 권장 |
| **혁신의료기기** | 4개월 검토 | DTx pathway 통합 | ⭐ 임상 자료 후 |
| 일반 의약품 | 14개월 풀 검토 | (변경 없음) | △ 최종 단계 |

### 1.2 기능성 화장품 11번째 (2026-Q3 예상)
- "**흉터 개선**" 신규 — 한의 외용제 직접 진입 가능
- 근거 자료: in silico (Boltz-2/ABFE) + in vitro IC50 + 안전성 (hERG/Skin)
- Recover 한의원 임상 자료 제출 시 **6개월 내 등록 가능**

### 1.3 즉시 액션
1. **MFDS 의약품안전국 외용 한약과** 컨택 (예약 필수)
2. **2025 화장품법 시행규칙 개정안** 입법예고 (2026-05 종료)
3. **Recover 임상 자료** 시뮬레이션 양식 사전 작성

---

## 2. K-Bio M&A 동향 (2025 한국바이오협회 보고서)

### 2.1 거래 규모

| 분류 | Median deal size | 사례 |
|---|---|---|
| AI 신약 발굴 platform | **₩45-180억** | SK Biopharm·Lunit·VUNO |
| 한의 IP 회사 | ₩15-50억 | (전형 예 부재 — 시장 미성숙) |
| Skincare derm AI | ₩30-90억 | Olay-P&G + Stanford 협업 |

### 2.2 우리 가치 평가 시나리오

**현재 (2026-04)**:
- AI 신약 platform (Tier 0-9 50+ 도구) ≈ ₩30-60억
- + Recover 한의원 임상 채널 (가치 가산) ≈ ₩50-120억
- + EMB-3 lead (composition-of-matter 출원 후) ≈ ₩100-300억

**2026-08 (Recover 오픈 + 외용제 1호 출시 후)**:
- Trade revenue + 임상 reference + 정부 사업 수주 → ₩200-500억

**2027-Q1 (CRO Tier 1 + 임상 1상 자료 후)**:
- IND 진입 가능 lead → ₩500-1500억

### 2.3 잠재 인수자 후보

| 회사 | 카테고리 | 적합도 | 메모 |
|---|---|:-:|---|
| SK Biopharm | 신약 R&D | ⭐⭐ | AI 도구 부재, 우리가 채워줌 |
| Celltrion | 바이오 | ⭐ | 합성 바이오 약함 |
| LG화학 생명과학 | 신약 | ⭐⭐ | 외용제 강점 부재 |
| 동아ST | 한약 + 신약 | ⭐⭐⭐ | 한방 수직 통합 가능 |
| 아모레퍼시픽 | 화장품 | ⭐⭐⭐ | 외용제 + Recover 매칭 |
| 에이프로젠 | 신약 R&D | ⭐ | Pre-clinical 강점 |

---

## 3. 정부 R&D 자동 매핑

### 3.1 매핑 도구
- **NIPA AI 의료 디지털 전환** (₩2.16억, 2025) — 응모 자료 작성됨
- **K-디지털헬스 R&D** (2026) — Recover 임상 매칭
- **KISTEP NTIS API** — 자동 사업 매핑 (`mlops/model_registry.py` 통합 가능)

### 3.2 우선순위 신청

| 사업 | 규모 | 마감 | 상태 |
|---|---|---|---|
| NIPA AI 의료 디지털 전환 2025 | ₩2.16억 | 2026-05-15 | 응모 자료 완성 |
| MFDS 의약품 R&D | ₩5억 | 2026-Q3 | 검토 중 |
| 산업통상자원부 한약 산업화 | ₩3억 | 2026-Q4 | 응모 자료 미작성 |
| 한국바이오협회 K-bio 펀드 | 매칭 | 상시 | 컨택 미진 |

---

## 4. 지적재산권 우선순위

> **EMB-3 출원이 paper publication 전에 들어가야 함. 현 시점 약 2-3주 윈도우.**

### 4.1 출원 전략
- **KIPO (한국 1차)**: ₩300만 + 변리사 ₩500만
- **PCT 12개월 내**: ₩2,000만
- **국가 진입 (US/EP/JP/CN)**: ₩5,000-8,000만
- **총 ~$80k USD (~₩1억)**

### 4.2 청구항 layered strategy
1. **Composition-of-matter** (EMB-3 SMILES + variation 5-10개)
2. **Pharmaceutical composition** (외용 cream / 자운고 vehicle)
3. **Method of treating fibrosis** (흉터/IPF/scleroderma)
4. **Synergistic combination** (EMB-3 + 자운고)
5. **Diagnostic application** (facial_dx 통합)

→ 자세한 prior-art 자동 검색은 `src/genesis_medicine/ip/prior_art.py`

---

## 5. 즉시 7일 실행 계획

| Day | 영역 | 액션 |
|---|---|---|
| Day 1 | MFDS | 의약품안전국 외용 한약과 컨택 (전화·이메일) |
| Day 1 | IP | 변리사 컨택 (김앤장/광장/세종) RFQ |
| Day 2-3 | 정부 사업 | NIPA + 한약 산업화 응모 자료 보강 |
| Day 4-5 | M&A | 잠재 인수자 3사 BD 컨택 (NDA 후 자료) |
| Day 5-7 | Recover | 임상 자료 양식 사전 작성 (시제품 8월 출시 가정) |

---

## 6. 종합 권장

1. **Tier 11-15는 비용 0, 시간 1주, 임팩트 ROI 최대.**
2. EMB-3 IP 출원이 **모든 다음 단계의 critical bottleneck**. 변리사 컨택 즉시.
3. MFDS "유사 의약품" 트랙이 **Recover D-110 일정과 매칭하기 가장 적합**.
4. K-Bio M&A는 2027-Q1 (임상 1상 자료 후)을 핵심 시점으로 BD 빌드.
5. 본 doc은 **법무·BD 자료**로 즉시 활용 가능 — 추가 코드 작업 없음.
