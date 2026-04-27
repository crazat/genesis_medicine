# MFDS Pre-IND Consultation 준비 문서

> **목적**: 천연물 기반 외용제 신약 (cosmeceutical → 의약외품 → 일반의약품) 등록 path 확립
> **신청 시기**: M6 (2026-10), CRO Tier 1 IC50 결과 도착 후
> **신청 비용**: ₩0 (식약처 무료)
> **참조**: 의약품 임상시험 사전상담 ([MFDS](https://www.mfds.go.kr/brd/m_99/list.do?menu_no=2613))

---

## 1. 회의 신청 양식 (대본)

```
신청 분야: 천연물 외용제 신약 사전상담
요청 사항:
  1. cosmeceutical → 의약외품 → 일반의약품 등록 path 가능성
  2. 천연물 신약 IND 제출 위한 비임상 패키지 범위
  3. 흉터 외용제 임상시험 1상 진입 요건
  4. AI in silico 신약 발굴 데이터의 IND 제출 자료 인정 여부

준비 자료:
  - Pre-IND briefing book (12편 preprint + Genesis_Medicine 시스템 백서)
  - 현재까지 in silico 결과 요약 (Boltz-2 + ABFE + ADMET 14 target)
  - CRO Tier 1 IC50 wet-lab 결과
  - EMB-3 / EGCG / r3_6 분자 spec
```

---

## 2. Pre-IND Briefing Book 구성

### Section A: 화합물 개요
- **EMB-3 (lead candidate)**:
  - SMILES: `CCCCCC1=C(O)C(=O)C(O)=C(C)C1=O`
  - 분자량: 224.26 g/mol
  - logP: 2.36
  - 출처: Embelin (Embelia ribes) scaffold-hop
  - 기전: TGF-β1/Smad pathway + MMP-1 dual inhibition (in silico)

### Section B: 적응증 정의
- **1차 적응증**: 비후성 흉터 (hypertrophic scar) + 켈로이드 (keloid)
- **시장 규모**: 한국 매년 신규 흉터 환자 약 50만 명, 외용 치료 미충족 욕구 70%+
- **기존 치료**: silicone sheet, intralesional triamcinolone, fractional laser, **Pirfenidone 8% gel (off-label)**
- **EMB-3 차별점**: dual-target (TGF-β1 + MMP-1), in silico safety profile (hERG 0.16, Lipinski pass)

### Section C: 비임상 데이터 패키지

#### in silico 결과 (Genesis_Medicine 자체)
| 항목 | 결과 |
|---|---|
| Boltz-2 cofold MMP-1 binding | affinity_prob_binary 0.598 (active threshold > 0.5) |
| Boltz-2 cofold TGFB1 binding | affinity_prob_binary 0.703 |
| ABFE T4L99A·benzene calibration | 1.17 kcal/mol (±2 kcal/mol PASS) |
| MD 10 ns RMSD MMP-1 × EMB-3 | 0.79 Å (안정) |
| ADMET-AI hERG | 0.16 (low risk, < 0.5 threshold) |
| ADMET-AI Lipinski violations | 0 |
| ADMET-AI logKp (skin permeation) | -2.4 (외용 적합) |

#### Wet-lab 결과 (CRO Tier 1, M3까지 수집)
- MMP-1 catalytic assay IC50
- TGFBR1 kinase assay IC50
- HSF cell line CTGF mRNA suppression (선택)

### Section D: 임상 개발 계획
- **Phase 1a healthy volunteer (외용제)**: 단회/반복 용량 안전성 + 피부 자극, n=24, Recover 한의원 IRB
- **Phase 2a (흉터 환자)**: 4주 외용 적용 + VSS scar score, n=30–50, Korean specialty hospital + Recover

### Section E: 제조 + GMP
- **현재 상태**: in silico only
- **필요 단계**: GMP synthesis 1 kg drug substance (Korean CMO 한미/대웅)
- **외용제 formulation**: 자운고 base + EMB-3 1–5%

### Section F: 규제 path
- **Step 1**: cosmeceutical (화장품법) — Recover 한의원 자체 시판
- **Step 2**: 의약외품 (KFDA quasi-drug) — 제한된 효능 표시 가능
- **Step 3**: 일반의약품 (KFDA OTC drug) — 임상 1+2 통과 후
- **Step 4**: 전문의약품 (Phase 2 pivotal + Phase 3) — 최종 단계

---

## 3. 식약처 회의 질문 list (사전상담)

1. **AI in silico 신약 발굴 데이터의 IND 제출 자료 인정 범위는?**
   → 다른 Korean pharma 사례 (Insilico Korea 진출 시) 참조
2. **천연물 외용제 cosmeceutical → 의약품 path의 가속 가능성?**
   → ICH M4Q 모듈 3 면제 조건 확인
3. **EMB-3 (Embelin scaffold-hop)의 "신물질" vs "천연물 유도체" 분류?**
   → 식약처 신물질 가이드라인 [의약품 안전관리원](https://www.mfds.go.kr/eng/index.do)
4. **Pirfenidone 8% 외용 gel precedent 기반 비임상 단축 가능 여부?**
5. **외용제 흉수 적용 임상에서 primary endpoint VSS scar score 인정?**
6. **Recover 한의원 자체 임상 outcome 데이터의 사전 IND 활용?**

---

## 4. 준비 timeline (신청 → 회의)

| Week | 작업 |
|---|---|
| W-12 (M3, 2026-07) | CRO Tier 1 결과 도착 |
| W-10 | Pre-IND Briefing Book draft 시작 |
| W-8 | external collaborator (의약화학 PhD) 검토 |
| W-6 | 식약처 회의 신청 (사이트 양식) |
| W-4 | 회의 일정 확정 (보통 4–6주 대기) |
| W-2 | Briefing Book 최종본 + 발표 자료 (PPT 30 슬라이드) |
| W-1 | 식약처 사전 송부 |
| W0 (M6, 2026-10) | **회의 진행** (90분, 식약처 5–8명 참석) |
| W+2 | 회의록 + 다음 단계 path 확정 |

---

## 5. 사용자 action

1. **W-12**: CRO Tier 1 결과 도착 (Genesis_Medicine 보고)
2. **W-10**: Briefing Book draft 검토
3. **W-6**: 식약처 회의 신청 (사용자 직접 제출, [MFDS 의약품 사전상담 신청](https://www.mfds.go.kr/brd/m_220/list.do?menu_no=599))
4. **W0**: 회의 직접 참석 (Recover 한의원 대표 + Genesis_Medicine 시스템 발표)
5. **W+2**: 회의록 기반 next-step path 확정 (Path A vs B)

---

## 6. 회의 결과 → 다음 단계

| 식약처 피드백 | 평가 | 다음 단계 |
|---|---|---|
| "cosmeceutical 시판 후 OTC drug path 가능" | best case | Path A 가속 + Tier 3 동시 |
| "비임상 패키지 확장 후 IND 제출 가능" | likely case | Tier 3 GLP toxicology 진행 |
| "신물질 분류, 전체 비임상 필요" | worst case | Korean pharma partnership 우선 |

---

**연락처**: 식약처 의약품정책과 02-2640-7501 / 의약품임상정책과 02-2640-1421
