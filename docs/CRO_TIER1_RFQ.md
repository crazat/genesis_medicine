# CRO Tier 1 wet-lab IC50 RFQ Template

> **목적**: EMB-3 + EGCG + r3_6 (round 3 winner) IC50 측정 → preprint #3 v0.3 wet-lab section → Phytomedicine peer-review 35→55% 점프
> **예산 한도**: ₩1,560만 (3사 비교 후 최저가)
> **기간 한도**: 6–10주
> **결과 deliverable**: PDF 결과서 + raw data Excel + IC50 + 95% CI

---

## 견적 요청 3사

| CRO | 강점 | 컨택 |
|---|---|---|
| **KIT 한국화학연구원 부설 안전성평가연구소** | GLP 인증 + 천연물 경험 | https://www.kitox.re.kr (한글) |
| **켐온** (CHEMON) | 가장 빠른 turnaround | https://www.chemon.co.kr |
| **바이오톡스텍** (Biotoxtech) | KFDA GLP + 효력시험 통합 | https://www.biotoxtech.co.kr |
| **DT&CRO** (대안) | 외용제 ADME 추가 시 | https://www.dtncro.com |

---

## 요청 항목 1: 합성

| 항목 | 사양 |
|---|---|
| 분자 1 | **EMB-3**: SMILES `CCCCCC1=C(O)C(=O)C(O)=C(C)C1=O` |
| 분자 2 | **r3_6 (round 3 winner)**: SMILES `CCCCCC1=C(O)C(=O)C(O)=C(C)C1=O` (실은 동일 — 별도 구분 불필요) |
| 분자 3 | **EGCG**: SMILES `OC1=CC(O)=C(C[C@@H](OC(=O)C2=CC(O)=C(O)C(O)=C2)C(O)=C3C(=O)C=CC(=O)C3=C1)O` (Sigma-Aldrich E4143 사용 가능) |
| 분자 4 | **Embelin baseline**: SMILES `CCCCCCCCCCCC1=C(O)C(=O)C(O)=C(O)C1=O` (Sigma-Aldrich E1406) |
| 순도 | ≥95% (HPLC + NMR + HRMS confirm) |
| 수량 | 각 1 g (assay 충분 + 잔여 spec) |
| 보관 | -20°C, dark, anhydrous |

---

## 요청 항목 2: MMP-1 catalytic assay

| 항목 | 사양 |
|---|---|
| 효소 | recombinant human pro-MMP-1 (R&D systems Cat # 901-MP) |
| 기질 | MCA-Pro-Leu-Gly-Leu-Dpa-Ala-Arg-NH2 (R&D systems Cat # ES010) |
| 활성화 | APMA 1 mM, 37°C 1h pre-incubation |
| 용량-반응 | 7-point (0.001 / 0.01 / 0.1 / 1 / 10 / 30 / 100 μM) |
| Replicate | technical n=3 × biological n=2 |
| 양성 대조 | Marimastat (IC50 5 nM 확인) |
| 음성 대조 | DMSO 1% 단독 |
| 측정 | fluorescence kinetic (Ex 320/Em 405) for 60 min |
| 분석 | linear initial slope → % inhibition → 4-parameter logistic fit (GraphPad / Python) |
| 결과 | **IC50 + 95% CI** (Hill slope + R² 포함) |

---

## 요청 항목 3: TGFB1 receptor I kinase assay

| 항목 | 사양 |
|---|---|
| 효소 | recombinant human TGFBR1 (ALK5) catalytic domain (Carna Bio Cat # 09-141) |
| 방법 | ADP-Glo (Promega V9101) |
| ATP | 100 μM (Km 부근) |
| 기질 | MBP 0.1 mg/mL |
| 용량-반응 | 7-point 동일 |
| 양성 대조 | Galunisertib (IC50 56 nM 확인) |
| 결과 | **IC50 + 95% CI** |

---

## 요청 항목 4: 세포 단위 검증 (선택, +₩300만)

| 항목 | 사양 |
|---|---|
| 세포 | HSF (human skin fibroblast, ATCC CRL-2522) |
| 처리 | TGF-β1 5 ng/mL induction × test compound 0.1 / 1 / 10 μM × 24h |
| 측정 | CTGF mRNA qPCR (β-actin normalized) + COL1A1 mRNA |
| Replicate | n=3 × biological n=2 |
| 결과 | dose-dependent CTGF/COL1A1 suppression % |

---

## 일정

| Week | 작업 |
|---|---|
| W1 | 합성 시작 + 표준 효소 batch 확보 |
| W2–4 | 합성 완료 + QC (NMR + MS) |
| W5–6 | enzyme assay (MMP-1 + TGFBR1) |
| W7 | 데이터 분석 + IC50 fit |
| W8 | 결과 보고서 draft |
| W9–10 | 사용자 검토 + 최종 보고서 |

---

## 결과 deliverable spec

1. **PDF 보고서** (한국어 + 영문):
   - 합성 spec sheet (NMR + HRMS)
   - assay protocol 상세
   - Dose-response curves (per compound × per target)
   - IC50 + 95% CI 표
   - QC metrics (Z' factor, S/B ratio)
2. **raw data Excel**: 모든 plate readings + 시간 kinetics
3. **잔여 시료 반환**: 실험 후 800–900 mg per compound

---

## 사용자 action

1. 3사 RFQ email 발송 (이 문서 첨부)
2. 견적 비교 (보통 1주 회신)
3. 계약 체결 (₩1,560만 예산 내)
4. 합성 시료 도착 확인
5. **6–10주 후 IC50 결과 → preprint #3 v0.3 작성** (Genesis_Medicine 자동)

---

## 결과 시나리오 → 다음 단계

| IC50 결과 | 평가 | 다음 단계 |
|---|---|---|
| **MMP-1 IC50 < 100 nM** | EMB-3 클래스 진정한 신약 후보 | Path B (IND track) — Tier 3 lead optimization |
| **MMP-1 IC50 100 nM – 10 μM** | Cosmeceutical 후보 | Path A (외용제 fast-track) — 1.5억 / 3년 |
| **MMP-1 IC50 > 10 μM** | Boltz-2 false positive | r3_6 외 다른 lead 재시도, 또는 라운드 4 |
| **TGFB1 IC50 < MMP-1 IC50** | 흉터 핵심 dual-target 가설 강화 | Path B 우선 |
| **양쪽 모두 IC50 > 30 μM** | EMB-3 가설 부정 → 전면 재검토 | EGCG single-target 또는 baicalein 라운드 5 |

---

**연락처**: hancheongwoo@hanpredict.com (사용자 직접) · genesis-medicine@hanpredict.com (이 lab)
