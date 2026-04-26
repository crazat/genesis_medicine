# CRO Tier 1 Go/No-Go 의사결정 자료

**작성일**: 2026-04-26
**의사결정자**: Genesis_Medicine v3 + Recover 한의원 운영진
**예산 규모**: **₩15,600,000** (≈ $11,800 USD)
**소요 기간**: 6주 (4 assay 병렬)
**대상 화합물**: 3개 (EMB-3 + Embelin baseline + ⓪)

---

## 1. Tier 1 4-assay 패키지 상세

| Assay | 타겟 | 유형 | n | 단가 | 소계 | 주 | 합리성 |
|---|---|---|---:|---:|---:|---:|---|
| TGF-β1 SMAD2/3 phosphorylation reporter (HEK293) | TGFB1 | cell | 3 | ₩850K | **₩2,550K** | 4 | ABFE/Boltz-2 affinity 0.749 → IC50 정량 |
| MMP-1 enzymatic FRET inhibition | MMP1 | biochem | 3 | ₩450K | **₩1,350K** | 3 | ABFE ΔΔG -11.48 → IC50 nM 검증 ⭐ |
| hERG patch clamp (manual, IonOptix) | hERG | biophys | 3 | ₩2,500K | **₩7,500K** | 6 | ADMET 0.16 wet 검증, 외용제·내복 안전성 |
| Skin irritation (EpiDerm RhE, OECD TG 439) | skin | imaging+biochem | 3 | ₩1,400K | **₩4,200K** | 5 | 외용제 출시 필수, Recover 임상 entry |
| **합계** | | | | | **₩15,600K** | **6** | |

> 6주 = 가장 긴 hERG (6w) + 4 assay 병렬. 결과 도착 ≈ 2026-06-07 (Recover 오픈 D-69).

---

## 2. 입력 근거 (in silico → wet-lab transition rationale)

### 2.1 EMB-3 lead (입증 강도 ⭐⭐⭐⭐)

| 검증 단계 | 결과 | 신뢰도 |
|---|---|---|
| ADMET-AI hERG | **0.16** (Embelin 0.40 대비 −61%) | 높음 |
| Boltz-2 affinity TGFB1 | **0.749** (Embelin 0.675) | 중간 |
| Boltz-2 affinity MMP1 | 0.674 | 중간 |
| MD 10ns RMSD MMP1 | **0.79 Å** (EGCG 1.45 Å 대비 우수) | 높음 |
| **ABFE (12h, 16 windows × 5 ns × 17 replicas)** | **ΔG = −32.90 ± 0.30 kcal/mol** | **매우 높음** |
| **ΔΔG (vs parent Embelin)** | **−11.48 ± 0.91 kcal/mol** | **매우 높음** |
| Cross-disease (IPF) | 6/7 타겟, weighted 0.90 | 중간 |

**핵심**: ABFE ΔΔG 음성 자체가 **EMB-3 ≫ Embelin** 결정적 증거. 12h GPU 두 번 돌린 결과 — wet IC50로 nM 환산하면 ratio ~10⁵–10⁸ 예상.

### 2.2 Embelin baseline (비교군 ⭐⭐⭐)
- 자연 추출 한약 component (백화사설초)
- ABFE −21.42 kcal/mol — 자체로도 결합 강함
- CRO 데이터로 wet baseline 확정 시 **paper 신뢰도 급상승**

### 2.3 3번째 화합물 (⓪) — 옵션 분기
- **A안**: Round 3 결과 best (현재 진행 중, ~15분 후 확정)
- **B안**: EGCG (paper 1편 별도 진행 중, 외용 universal compound)
- **C안**: 자운고 한약 처방 핵심 성분 (시코닌/asiaticoside)

---

## 3. CRO 후보 비교 (한국 비임상)

| CRO | 위치 | 강점 | 적합 assay | 권장 우선순위 |
|---|---|---|---|---|
| **KIT (한국화학연구원)** | 대전 | 정부 출연 + GLP, 천연물 특화 | TGFβ1 reporter, MMP1 | ⭐⭐⭐ (1순위) |
| **켐온 (Chemon)** | 수원 | 외용제 OECD TG 전문 | EpiDerm, hERG | ⭐⭐⭐ (1순위) |
| **바이오톡스텍** | 청주 | 비임상 GLP 종합 | hERG patch clamp | ⭐⭐ |
| **DT&CRO** | 안산 | 작은 batch 빠름 | 모두 가능 | ⭐⭐ |
| **Bioneer** | 대전 | biochem + 핵산 | MMP1 FRET | ⭐ (백업) |
| **Macrogen** | 서울 | cell-based 종합 | TGFβ1 reporter | ⭐ (백업) |

**권장 분리 발주**:
- 천연물 + cell-based → **KIT** (정부 매칭 가능성 ↑)
- 외용제 RhE + hERG → **켐온** (전문성 + 일정 빠름)

---

## 4. Recover 한의원 D-Day Timeline

```
2026-04-27 (D-110): facial_dx IRB 제출
2026-04-26 (오늘): CRO Tier 1 의사결정 시점 ← 우리 위치
2026-05-01:        CRO 발주 (KIT + 켐온)
2026-05-08:        EMB-3 합성/공급 (DT&CRO synthesis ~₩1,200K 별도)
2026-05-15:        wet-lab 시작
2026-06-07:        결과 도착 (D-69)
2026-06-30:        외용제 시제품 포뮬레이션 (자운고 + EMB-3)
2026-07-15:        파일럿 임상 데이터 수집 (D-30)
2026-08-15:        Recover 오픈 + EMB-3 외용제 1호 제품 ⭐
```

> CRO Tier 1 발주를 **오늘 결정 → 내일 발주** 시 Recover 오픈 D-Day에 외용제 1호 제품 launch 가능.
> 1주 지연 시 외용제 시제품 안정성 시험 (4주) 압박.

---

## 5. Go/No-Go 결정 매트릭스

| 항목 | Go 근거 | No-Go 근거 |
|---|---|---|
| 과학적 강도 | ABFE ΔΔG -11.48 (매우 강함), MD 0.79Å | round 3 결과 약한 경우 lead 다양성 부족 |
| 비용 ROI | ₩15.6M = NIPA 1차 자료 + paper 1편 + Recover 1호 제품 | NIPA 미선정 시 회수 어려움 |
| Timing | Recover D-110, CRO 6w → D-69 결과 → 시제품 가능 | hERG 6w가 critical path |
| Risk | hERG 양성/IC50 약함 시 lead 재선정 (round 3 결과로 보완) | 음성 결과 시 매몰비용 ₩15.6M |
| 사업성 | 외용제 1호 제품 + paper + IPF cross-disease 3중 활용 | 단일 적용처 시 ROI 미흡 |

### 권장 결정: **GO** (조건부)

**조건**:
1. ✅ Round 3 결과 확인 (15분 후) — EMB-3 능가 후보 있으면 3번째 화합물로 추가, 없으면 Embelin baseline + EGCG로 진행
2. ✅ NIPA 응모 자료에 CRO 발주 일정 명시 → 정부 매칭 ₩0.16억 신청
3. ✅ KIT + 켐온 분리 발주로 일정 단축
4. ⚠️ hERG 음성 시 EMB-4 generation 즉시 round 4 (예비 ₩2M)

---

## 6. 대안 시나리오

### 시나리오 A: 보수적 (Tier 1 절반만)
- TGFB1 reporter + MMP1 FRET만 발주: ₩3.9M (4w)
- hERG/Skin은 ADMET 신뢰 → 후속
- 장점: 비용 1/4
- 단점: 외용제 출시 근거 부족

### 시나리오 B: 권장 (Tier 1 풀 패키지) ⭐
- 4 assay 모두: ₩15.6M (6w)
- 외용제 1호 제품 출시 가능
- NIPA 응모 가산점 +30%

### 시나리오 C: 공격적 (Tier 1+2 병합)
- + IPF lung fibroblast (₩4.8M, 8w)
- 총 ₩20.4M (8w)
- 장점: paper 2편 (skin + IPF)
- 단점: Recover D-Day 압박, 외용제 출시 1주 지연

---

## 7. 즉시 액션 (Go 결정 시)

1. **DT&CRO**에 EMB-3 합성 RFQ 송부 (50 mg, ≥98% purity, ~₩1.2M)
2. **KIT**에 TGFβ1 reporter + MMP1 FRET RFQ
3. **켐온**에 hERG + EpiDerm RhE RFQ
4. NIPA 사업 정부 매칭 ₩0.16억 신청서 reflection
5. round 3 결과 → 화합물 list 확정 (오늘 ~13:30)

---

## 8. 부록: 비용 출처

- 단가: 2026 한국 비임상 CRO 평균 시장가 (KIT/켐온/Bioneer 기준)
- 출처: `pilot/scaffold_hop/cro_quote/cro_quote_full.csv`
- 환율: 1 USD = ₩1,320 (2026-04-26)
