# Synthesis 외주 RFQ (EMB-3 + r3_6 + EGCG + Embelin baseline)

> **목적**: CRO Tier 1 wet-lab assay 시료 확보
> **예산**: ₩300–500만 (4 분자 × 1 g)
> **기간**: 4–6주

---

## 합성 외주 후보 3사

| 회사 | 강점 | 견적 형태 |
|---|---|---|
| **Enamine REAL** | 글로벌 최저가, 단순 화합물 | 1 g 약 $300–800 (~₩40만–₩100만) |
| **WuXi AppTec** | 한국 진출 + custom synthesis | 1 g ₩60–150만 |
| **DT Pharma** | 한국 + 천연물 경험 | 1 g ₩50–150만 |
| **자체 한국 lab** (서울대/연세 약학) | 외부 collaborator 통한 합성 | 시료 free + co-author 조건 |

---

## 합성 spec (4 분자)

### 분자 1: EMB-3 (round 2 winner)

```
SMILES: CCCCCC1=C(O)C(=O)C(O)=C(C)C1=O
IUPAC: 2,5-dihydroxy-3-hexyl-6-methylcyclohexa-2,5-diene-1,4-dione
MW: 224.26 g/mol
구조 핵심: 1,4-benzoquinone + 6-hexyl + 5-Me + 2,3-OH (dual-OH motif)
순도: ≥95% (HPLC)
QC: 1H NMR + 13C NMR + HRMS confirm
보관: -20°C, dark, sealed under N2 (산화 민감)
```

### 분자 2: r3_6 (round 3 winner)

```
SMILES: CCCCCC1=C(O)C(=O)C(O)=C(C)C1=O
주의: EMB-3과 동일 SMILES → 단일 분자로 합성 (중복 견적 X)
```

### 분자 3: EGCG (Sigma-Aldrich 상용)

```
출처: Sigma-Aldrich E4143 (또는 동일 spec 한국 vendor 카탈로그)
SMILES: O[C@H]1Cc2c(O)cc(O)cc2O[C@@H]1OC(=O)c1cc(O)c(O)c(O)c1
순도: ≥95%
가격: 100 mg ~₩30만 (Sigma)
수량: 1 g 합성 외주 또는 Sigma 직구매 10×100 mg
```

### 분자 4: Embelin baseline

```
출처: Sigma-Aldrich E1406 또는 외주 합성
SMILES: CCCCCCCCCCCC1=C(O)C(=O)C(O)=C(O)C1=O
IUPAC: 2,5-dihydroxy-3-undecyl-1,4-benzoquinone
MW: 294.43 g/mol
순도: ≥95%
참조: Sigma 100 mg 약 ₩50만, 1 g 외주 ₩100만
```

---

## 합성 경로 (EMB-3, 외주 lab 참조)

### Step 1: 2,5-dihydroxy-1,4-benzoquinone 시작
- 시작 원료: 1,2,4,5-tetrahydroxybenzene (Aldrich)
- 산화: Ag2O / Et2O, RT 1h → 2,5-dihydroxy-1,4-benzoquinone
- 수율: ~60%

### Step 2: 6-methyl alkylation
- 6-methyl-2,5-dihydroxy-1,4-benzoquinone via methyl iodide / Cs2CO3
- 수율: ~50%

### Step 3: 3-hexyl alkylation (final)
- hexyl bromide / NaH / DMF, 60°C 6h
- column chromatography (silica, EtOAc/hexane 30:70)
- 최종 수율: ~30% overall

총 3 step, ~6–10일

---

## 견적 요청 email template (Enamine 한국 partner)

```
제목: Custom synthesis quote — 1 g of 2,5-dihydroxy-3-hexyl-6-methylcyclohexa-2,5-diene-1,4-dione

Hello,

I would like to request a quote for the custom synthesis of the following
compound:

  SMILES: CCCCCC1=C(O)C(=O)C(O)=C(C)C1=O
  Molecular weight: 224.26 g/mol

Required spec:
  - Quantity: 1 g
  - Purity: ≥95% (HPLC)
  - QC: 1H NMR, 13C NMR, HRMS confirm
  - Storage: -20°C, dark, sealed under inert gas

Requested timeline: 4–6 weeks
Delivery: South Korea (Seoul)

Please provide:
  1. Quote (USD or KRW)
  2. Estimated delivery date
  3. CoA template

Thank you,
한청우, KMD
Recover Korean Medicine Clinic / HAN PREDICT, Inc.
crazat7@gmail.com
```

---

## 사용자 action

1. 3사 견적 요청 (W0)
2. 견적 비교 (1주 회신)
3. 가장 빠르고 저렴한 곳 선택
4. 합성 시작 (W2)
5. 시료 도착 (W6–8)
6. CRO Tier 1 assay 시작 (W8–9)

---

## 잔여 시료 활용

1 g × 4 분자 = 4 g, assay 사용량 약 100–300 mg per compound
**잔여 700–800 mg per compound 활용**:
- Animal model 흉터 mouse 도즈 시험 (Tier 3 Path B 진입 시)
- Recover 한의원 외용제 prototype 제조 (자운고 base + 1–5%)
- 추가 cell line 검증 (HSF, primary keratinocyte)
- 안정성 시험 (-20°C 6mo, 25°C 6mo, 40°C 1mo)
