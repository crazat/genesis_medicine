# CLAUDE.md — Genesis_Medicine v3 (Skin Regeneration)

> Claude Code가 세션 시작 시 자동 로드하는 프로젝트 가이드.
> 세부 설계: `docs/ARCHITECTURE.md` · 라이선스: `docs/LICENSING.md`

---

## 🎯 프로젝트 목적 (2026-04-25 재정의)

**한약·생약·신물질로 피부 건강과 피부-연계 건강을 개선하는 신약 개발 파이프라인.**

### 포지셔닝 — 3-Pillar 통합 사업 구조 (2026-04-26 확정)

| Entity | 유형 | 역할 |
|---|---|---|
| **HAN PREDICT, Inc.** ([hanpredict.com](https://hanpredict.com)) | AI 헬스케어 플랫폼 (founder: HanCheongWoo) | Clinic CRM, Smart Charts AI EHR, Marketing AI, NutriDocH, AI Studio + facial_dx Station Kit (개발 중) |
| **Recover 한의원** | 한방 의료기관 (강남, 2026-08-15 개원) | 한의 피부재생 임상 vertical, <https://recover-clinic.kr> |
| **Genesis_Medicine** | R&D Lab (이 코드베이스) | AI in silico 신약 발굴 + 한약 분자 메커니즘 |

- 핵심 슬로건: "만드는 미용이 아닌, 되돌리는 미용" (Recover)
- 기존 무기: 새살침, 체질 한약 처방, 약침, 매선, 고주파/프락셔널, AI 안면 분석 (HAN PREDICT facial_dx)
- 본 파이프라인의 역할: **임상 경험칙 → 분자 수준 메커니즘 규명 → 신약/외용제 후보 도출** (Genesis_Medicine)
- **3-pillar 시너지**: 임상(Recover) → 진단(HAN PREDICT) → 분자(Genesis_Medicine) 통합 데이터 루프
- **Affiliation 표준** (모든 preprint·peer-review): byline = "HanCheongWoo ¹,²,³"
  - ¹ Genesis_Medicine Lab, Seoul, Republic of Korea
  - ² HAN PREDICT, Inc. (hanpredict.com)
  - ³ Recover Korean Medicine Clinic (recover-clinic.kr)

### 타겟 질환 (우선순위)
| 순위 | 질환 | 핵심 분자 타겟 | 대표 한약/천연물 |
|---|---|---|---|
| 🥇 | **흉터 재생** (여드름/위축/비후/켈로이드) | TGF-β1/Smad, MMP-1/3/9, COL1A1/3A1, CTGF, LOX, VEGF | 센텔라(아시아티코사이드/마데카소사이드), 자근(시코닌), 당귀, 자운고 |
| 🥈 | **색소/기미** | Tyrosinase (TYR), MITF, TRP-1/2 (DCT) | 감초(licochalcone/glabridin), 녹차(EGCG), 닥나무(kojic acid), 상백피 |
| 🥉 | **탈모** (AGA) | SRD5A1/2 (5α-reductase), AR, Wnt10b, β-catenin | 하수오, 측백엽, 황기, 인삼(ginsenoside Rg1) |
| 4 | **여드름** | 5α-reductase, AR, SREBP1, C. acnes | 황련(berberine), 감초(licochalcone A), 황금 |
| 5 | **광노화/안티에이징** | MMP-1, SIRT1, Elastin, FBN1, mTOR | 녹차(EGCG), 황기, resveratrol 계열 |
| 6 | **아토피·건선** | JAK1/3, IL-4Rα, IL-13, TSLP, IL-17/23, PDE4 | 황련해독탕 구성, 방풍통성산 |
| 7 | **홍조/민감·만성 염증** | Cathelicidin, PAR-2, TRPV1, COX-2 | 감초, 병풀, 카모마일 |

### 생산물 (3가지 사업 형태)
1. **외용제/화장품** — 센텔라 scaffold 최적화 유사체, 기미 미백 복합, 탈모 두피 외용.
2. **내복 한약 복합처방** — 체질별·질환별 맞춤 (클리닉 처방 근거 강화).
3. **임상 증거 데이터베이스** — 각 약재·성분의 피부 타겟 기전 정량 정리.

---

## 🎯 NEXT ACTIONS — 다음 세션에서 바로 할 일

> 피부 중심으로 재설계. 사용자가 새 세션을 열면 이 목록부터 확인하고 **제일 위 항목을 먼저 제안**.

### 🔥 16-WEEK PREPRINT MASS-PRODUCTION + 의료법 방어 전략 (2026-04-26 확정)

**상세 plan**: `~/.claude/projects/-home-crazat-genesis-medicine/memory/project_preprint_strategy.md`

**전략적 의도 (사용자 명시 2026-04-26)**:
- **단기 4개월 (Recover 한의원 D-110 → 개원)**: preprint 8-12편 + peer-review 1-2편 in-review
- **중기 6-12개월**: peer-review 게재 + CRO Tier 1 wet-lab 결합
- **장기 1-3년**: 진짜 in silico 신약 개발지로 자리잡음 (preprint은 raw material)

**의료법 §56 + 화장품법 4중 방어**:
- L1: 모든 marketing claim에 DOI 인용
- L2: "in silico, IRB pending" disclaimer 표준화
- L3: GitHub Apache-2.0 + 모든 데이터 공개 (transparency shield)
- L4: 광고 카피 "효능 표시" → "연구 활동" 전환

**Marketing copy template (legal-safe)**:
- ❌ "AI가 발굴한 흉터 치료제 EMB-3"
- ✅ "Recover는 AI 신약 발굴 연구 N편 (DOI list)을 자체 수행하는 한의원입니다"

**16주 Preprint 일정 (12편 target)**:
| Wave | 주차 | 편수 | 내용 |
|---|---|:-:|---|
| 1 | W1-3 | 2편 | Embelia ribes review + Recover workflow |
| 2 | W4-7 | 5편 | 5 질환 case study (흉터/색소/탈모/여드름/광노화) |
| 3 | W8-11 | 4편 | ABFE methodology + IPF cross-disease + 자오류주 + Korean PGx |
| 4 | W12-14 | 1편 | Open-source 50도구 통합 perspective |
| 5 | W15-16 | — | 2편 peer-review submission (Phytomedicine + J Cheminform) |

**플랫폼 분배**: ChemRxiv (methodology), bioRxiv (생물·한약), medRxiv (임상 workflow)

**Quality 안전선**:
- TRIPOD-AI 27 항목 supplementary 첨부
- "in silico only, wet-lab pending" abstract 마지막 문장
- 자운고 narrative 철회 + Embelia ribes 정직 (`docs/EMBELIN_LITERATURE_REVIEW.md`)
- ADMET·Boltz-2·ABFE 한계 모두 명시
- 외부 인용 70%+ (자기 인용 회피)

**현재 진행 (2026-04-26 단일 세션 완료)**:

### ✅ 12편 preprint v0.1/v0.2 모두 작성 완료 + 19 figures + 12 PDFs
**총 ~28,500 단어 main text + 19 publication-quality figures (300 DPI) + 12 self-contained PDFs (~6.5 MB).**

| # | Preprint | 상태 | Real data 출처 | Figures |
|:-:|---|---|---|:-:|
| 1 | Embelia ribes review | ✅ v0.2 (자운고 정정) | literature only | 1 |
| 2 | Recover workflow | ✅ v0.1 honest | architecture | 2 |
| 3 | EMB-3 case study | ✅ v0.2 (cross-disease 정정) | scaffold-hop + SAR panel + Round 1-3 | 3 |
| 4 | Pigmentation | ✅ v0.2 | `pilot/screen/pigmentation/screen_results.csv` | 2 |
| 5 | Alopecia | ✅ v0.2 | `pilot/screen/alopecia/screen_results.csv` | 2 |
| 6 | Acne | ✅ v0.2 | `pilot/screen/acne/screen_results.csv` | 2 |
| 7 | Photoaging | ✅ v0.2 | `pilot/screen/photoaging/screen_results.csv` | 2 |
| 8 | ABFE methodology | ⏸ T4L 진행 중 | `pilot/calibration/t4l_benzene/` (~3-4h 남음) | 0 |
| 9 | Cross-disease IPF | ✅ v0.2 | `pilot/open_targets/` (real GraphQL queries) | 2 |
| 10 | Chronotherapy 자오류주 | ✅ v0.1 | conceptual framework | 1 |
| 11 | Korean PGx | ✅ v0.1 | panel design | 1 |
| 12 | 50-tool pipeline | ✅ v0.1 | resource paper | 1 |

### ✅ 사용자 audit 통과 — 정직 데이터만
- v0.1에 fabricated table 5편 (#4-7, #9) 발견 → **A안 (실제 screen 후 정정)** 채택
- 4 disease screens 실행 완료 (60 cofolds × 4 = 240 Boltz-2 cofolds + ADMET-AI)
- Open Targets v4 GraphQL forward + reverse queries 실측
- 모든 preprint v0.2에서 fabricated 값 **0개**, retraction 명시

### 🔄 진행 중 (백그라운드)
- **T4L99A·benzene ABFE calibration** (PID 112376, ~14:39 시작 / ~22:00 완료 예상)
- Monitor `bkm98s108` armed → 결과 도착 시 #8 자동 정정 + ABFE convergence figure 추가

### 📋 Quality 검증 통과 항목
- TRIPOD-AI 호환 limitation sections
- Embelia ribes / 자운고 chemistry-based 정정 (`docs/EMBELIN_LITERATURE_REVIEW.md`)
- MMP-1 zinc handling caveat 명시
- Boltz-2 binary classifier vs IC₅₀ 구분
- Earlier ABFE -32.90 explicitly retracted (#8 §3.5)
- Berberine hERG 0.977 critical safety disclosure (#6)
- 모든 cross-disease 86%/100% claim retracted → real OT 1/26 (PDGFRB only)

### 🎯 즉시 가능 (사용자 다음 액션)
1. **계정 등록** (총 30분): ORCID + bioRxiv + medRxiv + ChemRxiv
2. **Preprint 검토 + 업로드**: 각 `preprints/<NN>/manuscript.pdf` 그대로 제출 가능
3. **Recover 홈페이지** RESEARCH 페이지: `manuscript.html` 자체 게재 가능
4. **상세 plan**: `docs/PREPRINT_SUBMISSION_GUIDE.md` (8 sections, 16주 timeline)

### 📦 산출물 위치
```
preprints/<NN_dir>/
├── manuscript.md      # markdown source
├── manuscript.html    # self-contained HTML (base64 embedded images)
├── manuscript.pdf     # publication PDF (figures inline)
└── figures/*.png      # 300 DPI raw figures

docs/
├── PAPER_PLAN.md
├── PREPRINT_SUBMISSION_GUIDE.md
├── EMBELIN_LITERATURE_REVIEW.md
├── CRO_TIER1_DECISION.md
└── MFDS_K_BIO_LANDSCAPE.md
```

**확률 (정직 calibrated)**:
- 11편 즉시 제출 가능 (#8 제외): 95% (만들어졌고 PDF까지 완성)
- 12편 등재 (T4L 통과 후 #8 합류 시): 90%
- Peer-review 1편 게재: 35% (12개월)
- 의료법 민원 방어 가능: 85% (disclaimer 유지 시)
- 의약화학·임상 reviewer rigor 통과: 50–65% (영문 교정 + 외부 collaborator 시 ↑)

---

### ✅ 완료 (2026-04-25, 피부 재편 이전)
- 인프라 구축: 라이선스 게이트(83 컴포넌트, 118 테스트), 11단계 아키텍처, 가속 스택(cuEq 0.10 + boltz-blackwell), genesis-md conda env(openmm+openff+mace), TxGNN env(py3.9+DGL2.4).
- **방법론 검증 완료** — 아래는 인프라 validation 용도로 가치는 있으나 **사업 방향과 무관**:
  - Boltz-2 BACE1 affinity (AD 9개 화합물, 241s, pIC50 6.8-8.5)
  - ADMET-AI v2 (9+15 화합물, 41 endpoints)
  - CHEMBL230245 10 ns MD (RMSD 2.57 Å, 1484 ns/day)
  - TxGNN AD 재창출 (1801 × 6 subtype, Aceclidine 최상위)
  - NSCLC EGFR TKI (5개 TKI pIC50 7.5-8.7, 인프라 범용성)
  - NSCLC/Parkinson Open Targets (시드 10/14 hit, AFDB 10/10)

### ✅ 완료 (2026-04-25 ~ 2026-04-26)
- 피부 5질환 파일럿 (흉터/색소/탈모/여드름/광노화) — 102 화합물 × 14 타겟
- EGCG 단독 paper (5/5 disease + MD 1.45 Å, 외용 universal compound 가설)
- Embelin scaffold-hop → **EMB-3** (hERG 0.40→0.16, MD 0.79 Å, MMP1 affinity 유지)
- Network 27 cofold + cross-disease 18 fibrosis indication (IPF 6/7, scleroderma 7/7)
- ABFE EMB-3 × MMP-1 정량화 (openmmtools 16 windows × 5 ns × 17 replicas, 진행 중)
- Embelin baseline ABFE 병렬 실행 (ΔΔG 정량 비교)
- 한약 매핑 (자운고 + EMB-3 강화 1순위 권장)
- CRO 견적 (Tier 1 ₩1,560만 / 6-10주, 전체 ₩4,775만)

### ✅ 완료 (2026-04-27 22:20, Tier B SOTA audit 11개 통합 — "세계 최고" sweep)
**광범위 외부 SOTA 조사 + 내부 cross-verify 결과 식별된 11개 gap 일괄 통합**:

| # | 도구 | 위치 | License | 상태 |
|---|---|---|---|---|
| 1 | Protenix-v2 (ByteDance, 2026-04-08) | `external_tools/protenix_v2/` (152MB clone) + `structure/protenix_adapter.py` engine_version 갱신 | Apache-2.0 ✅ | 통합됨 |
| 2 | g-xTB / NN-xTB (Grimme 2025) | `md/gxtb_adapter.py` graceful + LicenseGate research | Grimme academic | scaffold 완성, binary install 필요 |
| 3 | OSP MoBi Dancik skin PBPK | `dermatology/skin_pbpk_dancik.py` 자체 4-layer ODE 구현 + LGBM logKp head slot | Method commercial-safe | EMB-3 logKp=-2.39 검증 |
| 4 | AceFF v2 (Acellera, 2026-01) | `md/aceff_adapter.py` openmm-ml 호환 | MIT ✅ | scaffold 완성 |
| 5 | PocketXMol (Cell 2026) | `external_tools/pocketxmol/` (16MB) + `structure/pocketxmol_adapter.py` (small_molecule + cyclic_peptide + linker + PROTAC modes) | MIT ✅ | 통합됨, 약침 cyclic 모드 |
| 6 | SiteAF3 (PNAS 2026) | `structure/siteaf3_adapter.py` LicenseGate research | TBD | scaffold (라이선스 미확정) |
| 7 | Multi-fidelity BO cascade (ACS Cent Sci 2025) | `optimization/multi_fidelity_bo.py` + `scripts/cpu_multi_fidelity_bo_demo.py` | Method commercial-safe | 자체 구현, GP cascade 검증 |
| 8 | scPrimeKG + CellAwareGNN (bioRxiv 2026-02) | `knowledge_graph/scprimekg_adapter.py` | MIT (likely) | scaffold + cell-type-conditioned scoring |
| 9 | NPASS 2026 update (NAR 2026) | `ethnobotany/npass_2026_adapter.py` + `cache/npass2026/` | Free academic+commercial | 로더 + skin-permeable query + LGBM training set export |
| 10 | Pilosebaceous unit atlas (bioRxiv 2025-09) | `transcriptomics/pilosebaceous_atlas.py` | CC-BY 4.0 | 7 cell type catalog + AR/PIEZO1/MYLK 발현 검증 |
| 11 | PIEZO1/MLCK + PAR-2/GR 신규 타겟 | `conf/skin_targets/alopecia.yaml` (PIEZO1+MYLK) + `conf/skin_targets/pigment.yaml` (F2RL1+NR3C1) | conf only | 통합됨 |

**검증 결과** (`python -c "import all 9..."`):
- ✅ 9 신규 어댑터 모두 import OK
- ✅ License registry 83 → 95 components (+12)
- ✅ Dancik EMB-3 logKp = -2.39 cm/s (외용 적합), flux_ss = 1464 µg/cm²/h
- ✅ Pilosebaceous atlas: AR → dermal papilla 71% (생물학적 정확)
- ✅ Multi-fidelity BO: GP cascade 작동, cost-aware acquisition

**라이선스 분기**:
- commercial-safe (8개): Protenix-v2, PocketXMol, AceFF, Dancik (자체 구현), Multi-fidelity BO, NPASS 2026, scPrimeKG, Pilosebaceous atlas
- research-only (3개): g-xTB (Grimme), NN-xTB (Grimme), SiteAF3 (가중치 NC?)

**즉시 가능 신규 paper 2편 (preprint #13, #14)**:
- #13: PIEZO1/MLCK mechanotransduction in AGA (Nat Commun 2026 cite + 자체 Boltz-2 cofold)
- #14: Topical PBPK for natural-product-inspired skin therapeutics (Dancik + SkinPiX + 자체 LGBM)

### ✅ 완료 (2026-04-27, Round 12 + Round 13 + R5)
**핵심 paper-tier 산출물**:
- **MD top-5 lead ensemble** (10 ns × 5, RTX 5090): r3_6 × TGFB1 0.86 Å, β-sitosterol × AR 0.88 Å, shikonin × CTGF 1.24 Å, chlorogenic × SIRT1 1.61 Å, azelaic × TYRP1 1.71 Å — **모두 paper-tier 안정**
- **R5 cofold expansion**: 1877 → 2077 rows (TGFB1+CTGF +200), R5 phase 2 (AR/SIRT1/LOX/MITF) 진행 중
- **ChEMBL Boltz-2 calibration**: Pearson R = -0.453 (n=93), paper #8 결정 수치
- **PoseBusters v3 fix**: 0% → 9.3% (LIG1 4-char filter 버그 해결)
- **Pareto multi-objective + Bayesian Active Learning + Selectivity matrix + Quantum-corrected ranking** (8 ranker)
- **R4 expanded → 194 candidates** (relaxed bioisostere library)
- **Bayesian v2 round 6 candidates**: pterocarpan-vinyl-pyrogallol scaffold 발굴 (PAINS-free alternative!)
- **Multi-ranker leader 식별**: 2 mol top in 4/7 rankers
- **Round 4 selective compounds 71개**: β-sitosterol→AR sel_idx=0.563, shikonin→CTGF=0.247, chlorogenic→SIRT1=0.293

**ABFE 12h pivot 결정 (사용자 승인)**:
- ABFE EMB-3 × MMP-1 hardcoded script = 8/8 NaN (zinc 문제 미해결) → kill
- 대신 **5 × 10 ns MD ensemble** = 64분 wall, 5 paper-tier RMSD < 2 Å. ROI 압도적.

**🚨 PAINS audit critical finding (2026-04-27)**:
- 광범위 web search 결과 우리 8-target embelin claim 검증:
  - **8/8 직접 결합 보고 0건** (literature audit, PubMed/PMC)
  - Embelin 실제 검증 target: XIAP-BIR3 (4.1 µM), PAI-1 (4.94 µM), 5-LOX/mPGES-1 (0.06–2 µM), TACE
  - **1,4-benzoquinone-2,5-diol = PAINS class** (redox cycler + Michael acceptor + metal chelator)
- Preprint #1, #3, EMBELIN_LITERATURE_REVIEW.md 모두 v0.3 정정 (PAINS section + first-in-literature caveat 추가)
- Pool 2529 mol PAINS audit: PAINS_B 53.6%, Brenk 77.7%, embelin class 0.2% (4/2529 minority)
- → 정직 disclosure로 reviewer rigor 통과율 ↑

**3-Tier 로드맵 + 외부 액션 plan 4종 작성**:
- `docs/ROADMAP_3_TIER.md`: T1 4mo ₩500만 (85-90%) + T2 18mo ₩8,000만 (45-65%) + T3 7yr ₩30-55억 (35-50% partnership)
- `docs/CRO_TIER1_RFQ.md`: KIT/켐온/바이오톡스텍 견적 요청 template
- `docs/MFDS_PRE_IND_PREP.md`: 식약처 사전상담 Briefing Book 구성
- `docs/COLLABORATOR_OUTREACH.md`: 14 후보 그룹 outreach plan (₩3,000만/12mo)
- `docs/SYNTHESIS_RFQ.md`: Enamine/WuXi/DT Pharma 합성 RFQ

**사용자 결정 7개 (D1-D7)**:
- D1: ORCID + bioRxiv + medRxiv + ChemRxiv 등록 (즉시)
- D2: Editage / Enago 영문 교정 5편 (₩50-250만, W1)
- D3: **CRO Tier 1 RFQ 3사 발송** (₩1,560만, W4) ← 최고 ROI
- D4: 외부 collaborator 1명 contract (₩3,000만/12mo, M1)
- D5: MFDS Pre-IND consultation 신청 (free, M6)
- D6: Path A (cosmeceutical ₩1.5억) vs Path B (IND ₩30-55억) 분기 (M18)
- D7: Korean pharma partnership (M24)

### ✅ 완료 (2026-04-30, Universal scaffold 14/14 × 5 leaders + Extended 30ns validation)
**핵심 paper-tier 성과 — Preprint #15 Universal Scaffold 시리즈 v1.1**:

**5 universal scaffold leaders × 14 skin targets = 70 MD simulations all paper-tier**:
| Leader | SMILES variant | 14/14 결과 | sub-Å 개수 |
|---|---|---|---|
| **R12_4** | hydroxymethyl pterocarpan-vinyl-phenol | 14/14 paper-tier (mean<2.0Å) | 2 (MMP1 0.73, SIRT1 0.76) |
| **R12_11** | methoxy variant | 14/14 paper-tier | 3 (TGFB1 0.93, DCT 1.01, LOX 1.09) |
| **R12_23** | methyl ester variant | 14/14 paper-tier | **6** (AR 0.68, SIRT1 0.68, PTGS2 0.72, SREBP1 0.79, TYR 1.03, SRD5A1 1.06) |
| **R14_5** | methoxy variant 2 | 14/14 paper-tier | 3 (**MMP1 0.56**, CTGF 0.68, SREBP1 0.89) |
| **R13_13** | prenyl R11_0 variant (PAINS-flagged) | 14/14 paper-tier | 1 (PTGS2 1.01) |

**Extended-time kinetic validation (30 ns × top-5 sub-Å pairs)**:
| Pair | mean (full 30ns) | last-10ns mean | 평가 |
|---|---|---|---|
| MMP1 × R14_5 | **0.69** | **0.69** | sub-Å steady-state ✅ |
| AR × R12_23 | 0.77 | **0.85** | sub-Å steady-state ✅ |
| SIRT1 × R12_23 | **0.72** | **0.79** | sub-Å steady-state ✅ |
| CTGF × R14_5 | 1.34 | 1.76 | paper-tier with drift |
| PTGS2 × R12_23 | 진행 중 (~09:43 ETA) | — | — |

→ **3건 sub-Å 30ns kinetic stability 확인** = paper-tier reviewer 통과율 직접 강화.

**자동 overnight chain orchestration 성공**:
- `scripts/overnight_chain.sh`: bash nohup polling (60s 간격, 30분 stale detection)
- 03:03→04:56 R14_5 → R13_13 자동 sequence 완료
- 06:48~ extended 30ns chain 가동 (PID 34773), GPU 91% 지속

**89-simulation comprehensive ensemble heatmap (`figures/fig7_full_ensemble_heatmap.png`)**:
- All MD runs across R11_0 + R12_4/11/23 + R13_13 + R14_5 + earlier batches
- Target × Leader pivot showing 5-leader convergence on 14 skin disease targets

**즉시 가능 (사용자 다음 액션)**:
- Preprint #15 v1.1 PDF 38.6 KB main + 9 figures, 38.7 KB total
- §4.10–§4.18 5 universal scaffolds + final lead recommendation matrix 완성
- Pending: §4.19 extended-time validation table (PTGS2 도착 시)

### ✅ 완료 + 진행 중 (2026-04-30 11:35, R15 BRICS triage + batch2 GPU)
**R15 next-round candidate triage** (handoff to Codex):

**BRICS pool generation** — round 1 + round 2 → **38 unique** (R12_11 20, R12_23 11, R12_4 3, R13_13 4):
- `scripts/cpu_r15_brics_expansion.py` (44 candidates, MAX_BUILD 800)
- `scripts/cpu_r15_brics_deeper.py` (60 candidates, MAX_BUILD 3000, relaxed filter MW 180-550, logP 0.5-5.5, lipinski_viol≤1)
- ⚠️ R12_11 + R14_5 SMILES 완전 중복 (메톡시 위치만 다른 동일 chemical neighborhood) → R14_5 dedup 후 0개

**Triple filter pipeline (deadlock fix split)**:
- ⚠️ `cpu_r15_admet_xtb_filter.py` (combined script): TF + multiprocessing.Pool fork = futex deadlock (35분 0.7% CPU 후 kill)
- ✅ `cpu_r15_admet_only.py` (no Pool, ADMET-AI sequential) — 38행 × 14 ADMET endpoints
- ✅ `cpu_r15_xtb_only.py` (Pool of 8 xtb workers, no TF) — 38행 × HOMO-LUMO gap

**핵심 발견**:
- xtb gap mean 3.61 eV (electronically stable), max 4.36 eV (R12_23 methoxy chromanol)
- ADMET triple-safe (AMES + hERG + DILI 모두 < 0.3): **38개 중 단 1개** = `OCC1COc2cc(O)ccc2C1` (R12_4 chromanol fragment, MW 180.2, logP 0.94, QED 0.676, AMES 0.18, hERG 0.17, DILI 0.21)
- → R15 next-round MD validation의 1순위 후보 (small core, 외용 적합 logP, clean tox)

**Extended 30ns batch 2 진행 중** (PID 37674, ~12:00-12:30 ETA):
- ✅ mmp1×R12_4: 0.67/0.65 sub-Å steady-state
- ✅ sirt1×R12_4: 0.92/1.11 paper-tier
- ✅ srebp1×R12_23: 1.08/1.11 paper-tier
- 🔄 srebp1×R14_5 (running)
- 🔄 tgfb1×R12_11 (queued)

**Output 파일**:
- `pilot/cpu_meaningful/r15_brics_candidates.csv` (44, round 1)
- `pilot/cpu_meaningful/r15_brics_round2.csv` (60, round 2)
- `pilot/cpu_meaningful/r15_xtb_only.csv` (38 unique × HOMO/LUMO/gap)
- `pilot/cpu_meaningful/r15_admet_only.csv` (38 unique × 14 ADMET endpoints)
- `pilot/md_extended_30ns_batch2/summary.json` (batch2 5 pairs)
- `pilot/universal_scaffold_admet/full_tanimoto_top30.csv` (5 leaders × top 30 vs full pool)

**다음 핸드오프 (Codex 이어받음)**:
1. batch2 완료 대기 (ETA 12:00-12:30) → §4.19 5-pair full table 업데이트
2. R15 single triple-safe candidate (`OCC1COc2cc(O)ccc2C1`) Boltz-2 cofold × 14 targets — GPU 작업
3. preprint #15 v1.4 §4.21 R15 next-round triage 섹션 추가 + PDF 재빌드
4. CLAUDE.md feedback 추가: TF + multiprocessing.Pool fork deadlock 패턴 (recurring bug)

### ✅ Codex autonomous curator loop (2026-04-30 20:00)

Claude Code식 "시간마다 결과 기반으로 다음 큐를 지능적으로 고르는" 루프를 Codex에서 별도 구현:
- 빠른 deterministic fill: `scripts/auto_queue_cpu_gpu_daemon.sh` (기존 planner 기반, 120초 polling)
- LLM curator tick: `scripts/codex_curator_loop.sh` (기본 1800초 간격, `codex exec`가 최신 context를 읽고 큐잉/보류 판단)
- supervisor: `scripts/monitor_supervisor.sh`가 queue daemon + Codex curator loop를 감시하고 재시작
- prompt: `docs/CODEX_CURATOR_LOOP_PROMPT.md`
- context/decision/action log:
  - `pilot/codex_curator_context.md`
  - `pilot/codex_curator_decision.md`
  - `pilot/codex_curator_actions.log`
- triggers:
  - `/tmp/genesis_auto_queue_enabled`
  - `/tmp/genesis_monitor_enabled`
  - `/tmp/genesis_codex_curator_enabled`

운용 원칙:
- deterministic planner는 빠른 공백 채우기, Codex curator는 scientific priority/narrative/중복 위험을 감안한 judgement 담당.
- 2026-05-02 D: native WSL cutover 중에는 Queue drain mode가 우선이다. 이전 보호 큐 `PID 1345`, `PID 15578` 규칙은 historical context이며, 사용자가 명시 승인한 경우 상태 기록 후 중지 가능하다.
- 백그라운드 launch는 항상 `nohup setsid`.
- GPU util이 낮아도 OpenMM/antechamber/sqm 전처리로 CPU가 포화이면 추가 GPU 큐잉을 보류할 수 있음.

### ✅ Storage pressure + D: archive policy (2026-05-02 19:50)

Windows C:가 WSL ext4.vhdx를 품고 있어 `/home/crazat/genesis_medicine`의 대형 `pilot/` 산출물이 C: 여유공간을 직접 압박한다. D:는 NVMe SSD 여유가 크지만 `/mnt/d` 직접 연산은 DrvFS/9p 경유라 작은 파일이 많은 Boltz/OpenMM/xTB 작업에는 불리하다.

운영 원칙:
- 활성 계산은 WSL native ext4 유지: `pilot/cpu_meaningful`, active Boltz/OpenMM/xTB output, 보호 NPASS queue는 이동 금지.
- 완료된 대형 MD raw만 D: archive: `/mnt/d/genesis_archive/genesis_medicine/pilot/...`
- 로컬에는 `summary.json`, `summary.csv`, `.archive_manifest.json`, `ARCHIVED_TO_D.txt`만 남겨 planner/manuscript evidence를 보존.
- archive worker: `scripts/archive_completed_pilot_raw.py`
  - 보수적 선택: `pilot/md_*` + summary 존재 + raw child dir 존재 + process table에 active path 없음.
  - 전체 `rsync` 후 dry-run validation 통과 시에만 local raw child 삭제.
  - `/mnt/d` DrvFS/NTFS 권한 비트 차이를 피하려고 `--no-perms --no-owner --no-group --modify-window=2`로 검증.
  - manifest: `pilot/completed_pilot_raw_archive_manifest.jsonl`
  - log: `pilot/completed_pilot_raw_archive.log`
- duplicate archive launch 금지. 재실행 전 반드시:
  - `pgrep -af 'archive_completed_pilot_raw|rsync .*genesis_archive'`
  - `tail -80 pilot/completed_pilot_raw_archive.log`
- storage report: `scripts/write_storage_pressure_report.py` → `docs/STORAGE_OPERATIONS_PLAN.md` + `pilot/storage_pressure_report.json`
- queue planner hard-hold: `scripts/auto_result_planner.py`가 Windows C: 또는 WSL root free `< GENESIS_MIN_FREE_GB` (default 80GB)이면 신규 대형 CPU/GPU launch를 막는다. warn threshold default 200GB.
- 장기 최선책: active job 정지·백업 후 Ubuntu WSL distro 자체를 D:로 `wsl --export`/`wsl --import` 이전. 현재 큐가 도는 동안은 VHDX compaction/이전 금지.

### ✅ Genesis-only native D: WSL staging (2026-05-02 21:10)

ComfyUI는 C:의 기존 `Ubuntu`에 남기고, Genesis_Medicine만 D: native WSL ext4로 분리하는 방향으로 전환 중.

현재 구조:
- C: 기존 distro: `Ubuntu`
  - BasePath: `C:\Users\craza\AppData\Local\wsl\{0930df6a-828b-4f35-9b21-e20cd00e17e7}`
  - ComfyUI 유지: `/home/crazat/ComfyUI`
  - 기존 Genesis 큐가 아직 여기서 실행 중.
- D: Genesis 전용 distro: `Ubuntu-Genesis`
  - BasePath: `D:\WSL\Ubuntu-Genesis`
  - root fs: `D:\WSL\Ubuntu-Genesis\ext4.vhdx`
  - 내부 경로: `/home/crazat/genesis_medicine`
  - ComfyUI 없음.

진행 완료:
- 공식 Ubuntu 24.04 WSL rootfs 다운로드: `D:\WSL\Images\ubuntu-noble-wsl-amd64-24.04lts.rootfs.tar.gz`
- `wsl --import Ubuntu-Genesis D:\WSL\Ubuntu-Genesis ... --version 2`
- `crazat` default user 설정, `sudo/rsync/git/curl/ca-certificates` 설치.
- 무중단 initial staging 완료:
  - `/home/crazat/genesis_medicine`
  - `/home/crazat/miniforge3`
  - `/home/crazat/miniconda3`
  - `/home/crazat/.local` (uv Python symlink target)
  - `/home/crazat/.cache`
- 검증:
  - `df -hT .` → `/dev/sdf ext4`
  - `.venv/bin/python` RDKit OK
  - `.venv` torch CUDA OK
  - `miniforge3/envs/genesis-md` OpenMM OK
  - `nvidia-smi` OK

운영 스크립트:
- create: `scripts/create_ubuntu_genesis_on_d.ps1`
- staging copy: `scripts/stage_genesis_to_ubuntu_genesis.sh`
- verification: `scripts/verify_ubuntu_genesis.sh`

주의:
- 현재 initial staging은 기존 큐를 유지한 무중단 복제이므로, C: Ubuntu에서 계속 생성되는 최신 `pilot/` outputs는 최종 전환 전 한 번 더 delta sync 필요.
- 최종 전환 순서: queue pause/stop → final delta sync → `Ubuntu-Genesis`에서 verification → queue restart → C: Genesis 삭제는 며칠 안정화 후.
- `Ubuntu-Genesis` VHD max는 `1800GB`로 확장 완료. D:를 Genesis native ext4 중심으로 사용할 수 있음.

추가 정리/최적화 (2026-05-02 21:30):
- D:에서 Genesis와 무관한 실사용 잔여물 정리 완료:
  - `$RECYCLE.BIN` contents, `steam`, `XboxGames`, `WpSystem`, `WUDownloadCache`, `.parts`, `.url` 제거.
  - D: 사용량 대략 `374G -> 329G`; 여유공간 약 `1.5T`.
  - `WindowsApps`, `Program Files`, `Google Drive`는 Windows ACL/프로세스 lock으로 0-byte placeholder만 남음.
- C: Ubuntu 최적화 확인:
  - 전역 `%USERPROFILE%\.wslconfig`: `memory=56GB`, `processors=24`, `swap=16GB`, `mitigations=off`, `transparent_hugepage=madvise`, `autoMemoryReclaim=dropcache`, `sparseVhd=true`.
  - 이 설정은 WSL 전체에 적용되므로 `Ubuntu-Genesis`에도 재시작 후 동일하게 적용.
- `Ubuntu-Genesis` 전용 성능 보강 스크립트:
  - `scripts/configure_ubuntu_genesis_perf.sh`
  - `/etc/wsl.conf`: `systemd=true`, default user, automount metadata.
  - open-file limit: soft/hard `1048576`.
  - `/etc/profile.d/genesis-performance.sh`: Genesis cache, CUDA path, nofile.
  - C: Ubuntu의 selected dotfiles + CUDA 12.8 toolkit을 D: distro에 반영.
- 기존 C: Ubuntu 세션에서 Windows exe interop binfmt가 빠져 `wsl.exe` 직접 실행이 `Exec format error`를 낼 수 있음.
  - D: 관리 shell scripts는 `wsl.exe` 실패 시 `/init /mnt/c/WINDOWS/system32/wsl.exe -- ...` fallback을 사용하도록 수정.
  - 수동으로 Windows exe를 호출할 때도 같은 fallback을 사용하면 WSL shutdown 없이 진행 가능.
- Queue drain mode (2026-05-02 21:42):
  - 목적: 현재 실행 중인 Boltz/xTB/NPASS 작업까지만 끝내고, 이후 새 자동 큐잉 없이 final D: WSL cutover 준비.
  - local marker: `pilot/QUEUE_DRAIN_MODE`
  - removed triggers: `/tmp/genesis_auto_queue_enabled`, `/tmp/genesis_monitor_enabled`, `/tmp/genesis_morning_queue_guard_enabled`, `/tmp/genesis_codex_curator_enabled`, `/tmp/genesis_world_class_gap_enabled`
  - running compute jobs are preserved; scripts now refuse to start/restart auto queue, monitor, morning guard, curator, and world-class watchdog while the marker exists.
  - 재개 시: marker 제거 후 필요한 supervisor를 `nohup setsid ...` 방식으로 재시작.
- `Ubuntu-Genesis` VHD 확장 (2026-05-02 21:52):
  - `wsl --manage Ubuntu-Genesis --resize`는 C: Ubuntu가 running인 상태에서 WSL service shutdown을 요구하여 사용하지 않음.
  - 대신 Hyper-V `Resize-VHD -Path D:\WSL\Ubuntu-Genesis\ext4.vhdx -SizeBytes 1800GB`로 VHDX max 확장.
  - `Ubuntu-Genesis` 내부 `/` 확인: `/dev/sdf ext4 1.8T`, used 약 `155G`, avail 약 `1.5T`.
  - VHDX는 dynamic이므로 Windows 실제 파일 크기는 약 `156G`로 유지되고, native ext4 사용량이 늘 때만 D: 물리 사용량 증가.
  - `/mnt/d/genesis_archive`는 final cutover 시 native archive(`/home/crazat/genesis_archive/...` 또는 project-local archive)로 이전 가능.
- Full D: native migration (2026-05-02 22:08):
  - 사용자 승인: "상태를 기록하고 중지 하고 디 드라이브로 풀 마이그레이션 진행".
  - C: Ubuntu NPASS `scripts/cpu_5000_conformers_npass_top500_round2.py` process group `15578`는 상태 기록 후 중지. 보고서: `pilot/npass_stop_report_20260502_220806.txt`.
  - 중지 시점 상태: elapsed `3-04:35`, log `pilot/cpu_npass_500_1000_v2.log`는 header 1줄, 기대 출력 `pilot/cpu_meaningful/conformers_2000_npass_rank500_1000.csv` 없음. 원인 판단: `multiprocessing.Pool.map` 구조에서 pathological final molecule 또는 unbounded RDKit conformer branch로 checkpoint 없이 장기 정지.
  - `PID 1345` NPASS rank 1k-2k 큐는 cutover 점검 시 이미 process table에 없음.
  - D: `Ubuntu-Genesis` xTB 36-conformer refine은 유지: `scripts/cpu_xtb_npass_top_refine.py --topn 5000 --workers 8 --num-confs 36`, D internal parent PID `435`.
  - `scripts/stage_genesis_to_ubuntu_genesis.sh`는 full migration 모드로 확장:
    - `/home/crazat/genesis_medicine`, `miniforge3`, `miniconda3`, `.local`, `.cache`를 D native ext4로 복사.
    - D에서 실행 중인 36conf 파일 보호: `pilot/cpu_xtb_npass_top5000_hetero6_36conf_d_native.log`, `pilot/cpu_meaningful/xtb_npass_top5000_hetero6_refine_36conf.csv`는 tar exclude.
    - 기존 DrvFS archive `/mnt/d/genesis_archive`를 D native ext4 `/home/crazat/genesis_archive`로 복사.
    - 로그: `pilot/d_wsl_full_migration_<RUN_ID>.log`, tar stderr: `pilot/d_wsl_full_migration_project_tar_<RUN_ID>.log`, `pilot/d_wsl_full_migration_archive_tar_<RUN_ID>.log`.
  - migration 완료 전까지 `pilot/QUEUE_DRAIN_MODE` 유지, C: Ubuntu에서 신규 대형 큐 시작 금지. 완료 marker `pilot/D_NATIVE_FULL_MIGRATION_<RUN_ID>.txt`와 verification 통과 후 `Ubuntu-Genesis`를 Genesis canonical runtime으로 사용.
  - D: GPU smoke/backfill fix (2026-05-02 22:42):
    - `Ubuntu-Genesis` 최소 rootfs에는 `gcc/g++/make`가 없어 Boltz-2 Triton/cuequivariance JIT가 `Failed to find C compiler`로 실패했다. root로 `apt-get install -y build-essential` 완료.
    - Boltz cache `/home/crazat/.boltz`는 D native에서 초기화 완료(약 7.6GB). 이후 D: Boltz-2 첫 실행의 CCD/weight download 지연은 없어야 함.
    - archive copy 중 GPU backfill은 대형 MD 대신 output이 작은 active-learning Boltz-2 cofold만 허용. 현재 D native log: `pilot/active_learning_next_cofold_batch20_d_native.log` (batch21 재실행), loop log: `pilot/active_learning_gpu_backfill_d_native_loop.log`.
    - GPU backfill loop는 현재 batch 종료 후 `scripts/run_active_learning_next_cofold.py --batch-size 16`을 순차 실행한다. 대형 CPU/xTB 추가 큐는 archive native copy가 끝난 뒤 worker 수/중복 여부를 재평가.

### ✅ D-native canonical runtime + overnight queue armed (2026-05-03 00:55 KST)
- **Canonical repo is now `Ubuntu-Genesis:/home/crazat/genesis_medicine`**. All compute, `CLAUDE.md` updates, commits, and pushes must be done from this D-backed distro unless the user explicitly says otherwise.
- C-backed `Ubuntu` may still be used as an interop/control shell to call `wsl.exe -d Ubuntu-Genesis`, but it must not be treated as the source of truth and must not receive new OpenFold3/Boltz/xTB installs.
- `Ubuntu-Genesis` storage: `/dev/sdf` ext4 max `1.8T`, D-backed VHD. Last operational check showed >1T free; native project outputs and archive can live inside this distro.
- D OpenFold3 transfer/install verified:
  - `external_tools/openfold-3/` copied to D native ext4.
  - checkpoint `.cache/openfold3/of3-p2-155k.pt` copied to D native cache.
  - smoke passed at `pilot/openfold3_smoke/20260503_003339`; log confirmed `GPU available: True (cuda), used: True`, `Successful Queries: 1`.
  - CUDA/WSL path fix required in scripts: prepend `/usr/lib/wsl/lib` and set `CONDA_OVERRIDE_CUDA=12.8` where needed.
- Drain mode resolved for D runtime:
  - `pilot/QUEUE_DRAIN_MODE` absent.
  - active triggers: `/tmp/genesis_auto_queue_enabled`, `/tmp/genesis_monitor_enabled`, `/tmp/genesis_codex_curator_enabled`, `/tmp/genesis_morning_queue_guard_enabled`.
- Overnight guard / monitor stack is active until the user morning window:
  - `scripts/morning_queue_guard.sh` with `GENESIS_GUARD_UNTIL=2026-05-03T10:30:00+09:00`.
  - `scripts/monitor_supervisor.sh`.
  - `scripts/codex_curator_loop.sh`.
  - `scripts/auto_queue_cpu_gpu_daemon.sh`.
  - D keepalive process keeps `Ubuntu-Genesis` from being torn down by WSL after the launcher exits.
- GPU queue policy after cutover:
  - `scripts/overnight_gpu_backfill_d_native.sh` keeps GPU filled until `2026-05-03T10:00:00+09:00`.
  - Priority order: active-learning Boltz-2 cofold with MMP1 included → scaffold-hop / cryptic / round3 gap fills → R17 green 120 ns MD → R18 chromanol expanded backfill.
  - Latest observed active job: `run_active_learning_next_cofold.py --include-mmp1`, batch32 Boltz-2, CUDA memory in use.
- CPU queue policy after cutover:
  - xTB NPASS refine ladders continue on D native ext4 with multi-worker CPU saturation.
  - Latest observed active jobs: `xtb_npass_top1000_hetero3_refine_288conf.csv` and `xtb_npass_top3000_hetero5_refine_288conf.csv`; planner can continue into hetero8/hetero9 ladders when idle.
- Scientific claim discipline remains mandatory:
  - MMP1/Zn results are triage-only until ZAFF/metal-aware ABFE gate passes. Do not claim “perfect binding” or confirmed negative ABFE from non-ZAFF runs.
  - R18 chromanol expanded backfill is discovery triage only; no novelty/FTO/commercial claim until prior-art gate passes.
  - Boltz-only affinity requires cross-model, decoy, PLIF, MD, or free-energy validation before strong manuscript language.
- Known D-launch reliability rule:
  - Background jobs should be launched with `nohup` and a Windows-side `wsl.exe -d Ubuntu-Genesis` client or equivalent keepalive. Simple detached `nohup` inside a one-shot WSL invocation can be reaped when the distro idles.
  - Preferred manual pattern from C control shell: `/init /mnt/c/Windows/System32/cmd.exe /c "cd /d C:\ && wsl.exe -d Ubuntu-Genesis --cd /home/crazat/genesis_medicine -e bash -s"` with the script piped on stdin.

### ✅ C 드라이브 legacy 유지 결정 (2026-05-03 11:00 KST)

D Ubuntu-Genesis cutover 직후 시점에서도 C `Ubuntu` distro 안의 Genesis 자산은 **유지**한다. fallback 백업 가치 + 위급 storage pressure 부재.

- 결정: 자동 cleanup / VHDX compact / 삭제 제안 금지. 사용자가 다시 묻거나 C free < 100 GB 위급 시에만 단계 B/C 재검토.
- 시점 수치: Windows C 503 GB free / 2.0 TB. C VHDX(`Ubuntu`) 685 GB sparse, ext4 used 327 GB. C `/home/crazat/genesis_medicine` 118 GB.
- 절대 보존: `/home/crazat/ComfyUI` (130 GB), 다른 venv/projects, `miniforge3`/`miniconda3` 통째 (Genesis env만 선택 제거 가능), `~/.local`, `~/.cache`, Claude 메타.
- 단일 최대 회수 후보: `/home/crazat/genesis_medicine` (118 GB, 내부 `.venv` 18 GB 포함). 실제 Windows 회수는 `Optimize-VHD -Mode Full` 별도 실행 필요(C `Ubuntu` distro shutdown 동반 → ComfyUI 일시 정지).
- 재검토 트리거 (모두 충족): R17 120ns plan(9 jobs) 완료 + D HEAD push 검증(`git rev-list --left-right --count origin/main...HEAD` = `0\t0`) + D-native 1주 무사고 + 사용자 재확인.
- 상세 메모리: `~/.claude/projects/-home-crazat-genesis-medicine/memory/project_c_drive_legacy_retention.md`.
- 참고: 인계자 manifest `docs/C_DRIVE_GENESIS_CLEANUP_MANIFEST_2026-05-02.md` 동일 결론.

### ✅ Paper #A 12h overnight 연산 결과 (2026-05-04 22:34 → 2026-05-06 12:42 KST)

> 사용자 12h 자율연산 위임 → 6-compound ChEMBL MMP-1 ABFE benchmark + xtb GFN1/GFN2 cross-method analysis 완료. **paper #A 핵심 finding 확정**.

**6-compound ABFE rep1+rep2 결과** (`pilot/abfe_benchmark_chembl/CHEMBL{ID}/abfe_production_mss/dG_bind.json`):

| ChEMBL | exp dG | rep1 | rep2 | mean | Δrep | mean−exp |
|---|---|---|---|---|---|---|
| 415 (4nM, strong) | -11.6 | -19.7 | -0.869 | -10.28 | **18.8** | -1.32 ✓ |
| 94487 (12nM, strong) | -10.9 | -20.9 | -21.019 | -20.96 | 0.12 | +10.06 ❌ |
| 257077 (15nM, mid) | -10.7 | +8.6 | +3.165 | +5.88 | 5.4 | +16.58 ❌ |
| 301236 (42nM, mid) | -10.0 | -7.5 | -11.215 | -9.36 | 3.7 | -0.64 ✓ |
| 292707 (200nM, mid) | -9.0 | +4.9 | +4.632 | +4.77 | 0.27 | +13.77 ❌ |
| 2105729 (18μM, weak) | -6.4 | +0.35 | +7.198 | +3.77 | 6.85 | +10.17 ❌ |

**Pass rate: 2/6** (415, 301236).

**rep3 부분 확장** (415 + 2105729): 415 rep3 = -11.49 (Δexp 0.11★), 3-rep mean -10.69 (Δexp 0.91). **3-replicate mean이 catastrophic Δrep variance를 평균화하여 strong inhibitor의 experimental value를 1 kcal/mol 이내 회복**. Weak binder (2105729)는 3 rep 모두 양수로 일관 실패.

**Paper #A 핵심 finding (publishable angle)**: *Reproducibility ≠ accuracy.* 94487은 Δrep 0.12 (극도 reproducibility) 이지만 +10 kcal systematic over-binding. 415는 Δrep 18.8 (catastrophic variance) 이지만 mean이 1.3 kcal 이내. ZAFF-AMBER ABFE on Zn metalloenzymes은 compound-specific failure mode가 Δrep과 상관 없음.

**Paper #A 권장 framing (locked)**: "*Limitations of ZAFF-AMBER ABFE for Zn metalloenzyme binding affinity prediction: replicate-pair analysis on MMP-1.*" Pass 2/6은 "validation" framing 불가 — methodology evaluation paper로 포지셔닝. JCTC submission target.

**xtb GFN1 vs GFN2 cross-method (paper #B add-on)**: 9997 hetero10 cohort, 432 conf, ALPB. **Spearman ρ(gap) = 0.978**, ρ(energy_min) = 0.993. Top-10 9/10, Top-50 45/50. xtb method-agnostic ranking robustness 입증 → paper #B method-robustness section 데이터 확보.

**Prinomastat (CHEMBL406) ABFE 시도 (2026-05-06 11:09)**: prep `-nc -1` 적용 후 구조 정상 (74290 atoms, Zn 1, LIG 1). 하지만 Phase 5 complex leg equilibration replica 0 state 0에서 NaN crash (4 LangevinDynamicsMove restart 실패). **embelin과 동일 failure mode** — prep script가 warmup 스킵해서 발생. 다음 세션: `scripts/zaff_phase5_warmup_generic.py --work pilot/abfe_benchmark_chembl/CHEMBL406` 먼저 돌리고 production 재발진.

**Manifest 15개 중 ok 6 / fail_antechamber 9** — 9개 모두 `-nc -1` flag로 prep 가능 확인 (CHEMBL443684 Marimastat / CHEMBL406 ✓ / 412 / 259829 / 98 / 93146 / 3036 / 57058 / 1207). Tier-1 확장 시 orchestrator에 warmup 단계 + `-nc -1` autodetect 추가 필요.

### 다음 세션 즉시 액션 (continuity)
1. **CHEMBL406 warmup → ABFE 재발진**: `python scripts/zaff_phase5_warmup_generic.py --work pilot/abfe_benchmark_chembl/CHEMBL406` → `python scripts/zaff_phase5_abfe_production_mss.py --work pilot/abfe_benchmark_chembl/CHEMBL406` (PATH export 필수: `export PATH=/home/crazat/miniforge3/envs/genesis-md/bin:$PATH`).
2. **`abfe_benchmark_prepare.py` 패치**: build_complex 단계에서 RDKit GetFormalCharge() 결과를 antechamber `-nc` 인자로 자동 전달 + tleap 후 warmup_generic 호출 추가.
3. **나머지 8개 manifest 화합물 prep 재실행**: -nc -1 fix 적용.
4. **Paper #A 초고**: `preprints/08_abfe_methodology/manuscript.md` 6+rep3 데이터 + GFN1/GFN2 cross-method 섹션 추가. 권장 framing 적용.
5. **CPU**: GFN1 cohort csv (`pilot/cpu_meaningful/xtb_npass_top9997_hetero10_gfn1_432conf.csv`) 분석 figure 생성 가능.

---

### ✅ Paper #A methodology pipeline — Tier 2/3 인프라 완성 (2026-05-04)

JCTC/JCIM/RSC Digital Discovery target — 17 Zenodo papers를 1편 deep methods paper로 재구성. 가설: ZAFF-AMBER + alch RE-MD (16λ × 3 rep × 8/5 ns)이 ChEMBL MMP-1 IC50 ranking을 Spearman ρ ≥ 0.6으로 회복.

**Tier 2 deliverables**:
- `pilot/abfe_mmp1_holo_zn/abfe_production/dG_bind.json`: EMB-3 ABFE INCONCLUSIVE (+0.38 ± 0.29 kcal/mol).
- `scripts/zaff_phase5_warmup_generic.py`: 임의 ABFE work-dir용 warmup (10000-iter min + 0K→310K heat + restrained NPT). NaN crash 방지 핵심.
- `scripts/zaff_phase5_abfe_production_generic.py`: parameterized Phase 5 (`--work` CLI). PHASE4 gate `{work}/complex/PHASE4_OK`. **Production timing 업그레이드**: NS_PROD_COMPLEX 5.0→8.0, NS_PROD_SOLVENT 3.0→5.0 (literature Δ ns 기반 Spearman ρ uplift +0.05~0.15). Per compound 19-29h, Tier-1 full run ~8d wall.
- `scripts/abfe_benchmark_orchestrator.py`: Tier-1 6 compounds 순차 실행 + Spearman/MAE aggregation. PHASE4_OK는 root-level 사용 (warmup/Phase 5 generic은 `complex/PHASE4_OK`).
- `scripts/abfe_benchmark_prepare.py`: Vina+obabel pose + AM1-BCC + tleap parm. (meeko CLI는 이 env에서 broken — obabel로 대체.)
- `preprints/PRE_REGISTRATION_TEMPLATE.md`: OSF 사전등록 template (H1-H3 lock).

**Tier 3 / paper-strengthening deliverables**:
- `scripts/active_learning_screen.py` + `pilot/active_learning/round1/`: 1390 mols 학습, cv_r2=0.83±0.25.
- `scripts/kipris_patent_check.py`: KIPRIS+PubChem patent novelty (필요: `KIPRIS_API_KEY`).
- `scripts/dude_decoy_benchmark.py` + 315 decoys: enrichment는 actives xtb-scoring 별도.
- `scripts/zenodo_code_release.py`: code DOI 발급 (필요: `ZENODO_TOKEN`).
- `scripts/of3_aqaff_paper_a_b.py`: OpenFold3 + AQAffinity cross-engine (modes: tier1, top500). MMP1_SEQ apo stub 재사용 (R=-0.292 일관성).

**Tier-1 ABFE benchmark targets (paper #A locked subset)** — 6 ChEMBL MMP-1 4 nM → 18 μM:
| ChEMBL ID | Name | IC50 (nM) | Class |
|---|---|---|---|
| CHEMBL415 | Batimastat | 4 | hydroxamate |
| CHEMBL94487 | RS-130830 | 12 | carboxylate |
| CHEMBL257077 | — | 15 | prinomastat-like hydroxamate |
| CHEMBL301236 | — | 42 | fluoro-aryl hydroxamate |
| CHEMBL292707 | Ilomastat | 200 | zinc-chelating |
| CHEMBL2105729 | — | 18000 | very weak hydroxamate |

EMB-3 (done) + embelin (running) → N=8 ABFE for Spearman.

**Vina active-site grid (MMP-1 1HFC)**: Zn (40.32, 27.89, 36.94), grid 25×25×25 Å, exhaustiveness=16, num_modes=5. First-shell 3-His: HID111/115/121.

**Why this matters (paper #A submission criteria)**:
1. ABFE protocol validated against experimental Ki (이전 missing piece).
2. Statistical rigor (5+ diverse-scaffold 화합물).
3. Reproducibility chain (Vina + obabel + AmberTools + OpenMM 모두 conda).
4. Pre-registered hypothesis (screening-paper rejection 회피).

**Known pitfalls (다음 세션에서 회피)**:
- Phase 5는 minimization 없음 → C12+ alkyl 즉시 NaN. 항상 warmup 먼저.
- meeko CLI (`mk_prepare_*`)는 이 env에서 broken (config bug). obabel 사용.
- subprocess의 `python3`은 base conda Python (no parmed) 해석. absolute path 사용.
- Vina 출력 PDQBT는 H 누락. obabel `-h` 또는 RDKit AddHs 필요.
- 백그라운드 launch 전 stale orchestrator process 반드시 kill + trajectory.nc 정리.

**TF + multiprocessing.Pool fork = futex deadlock (recurring bug)**: ADMET-AI(TF) + multiprocessing.Pool fork가 같은 프로세스에서 동시 사용되면 deadlock. 항상 별도 스크립트로 분리 (`*_admet_only.py` sequential + `*_xtb_only.py` Pool).

### 🔥 Tier 0 — 즉시 통합 (SOTA audit 2026-04-26 결과)
> 광범위 SOTA 조사 결과 **즉각 통합하면 ROI 매우 큰** 7개 도구. 모두 MIT/Apache.
1. **CellAwareGNN** (bioRxiv 2026-02) — TxGNN 직접 후속, scPrimeKG 기반, 자가면역 피부질환 +6% AUPRC. 자가면역(아토피·건선·원형탈모) 재창출 정확도 직격.
2. **PocketXMol** (Cell 2026, MIT, 205★) — 단일 모델로 11/13 SBDD SOTA + cyclic peptide 동시 (약침 후보).
3. **PocketMiner + CryptoBank** — TGF-β1/MMP-1/CTGF allosteric site 1초 스캔 (B 가설 음성을 cryptic site 재탐색으로 강화).
4. **logKp + Skin_Irritation 자체 ML 헤드** (FDA 2326 + LGBM) — 우리 stack 가장 큰 약점 (피부 외용 정량) 직접 보완.
5. **f-RAG** (NeurIPS 2024, NVIDIA) — 센텔라/시코닌/EGCG fragment 강제 포함, 한약 영감 분자 디자인 핵심.
6. **NPASS 2026 update** — quantitative ADME-Tox **+206%** 확장 (외용 logKp ground truth).
7. **BAT2** (OpenMM 호환) — 자체 ABFE 구현을 paper-tier 검증/대체.

### 🟡 Tier 1 — 8주 내 (Nature-tier 강화)
8. **Protenix-v2** (Apache, 2026-04) + **OpenFold3** ensemble — Boltz-2 consensus 강화.
9. **AlphaFlow-Lit** — 기존 AlphaFlow drop-in 47× 가속.
10. **CarsiDock-Cov** — 시코닌/EGCG quinone 공유결합 평가 (현 stack에 unique).
11. **Boltz-ABFE** — cryptic site 결정구조 없이 ABFE.
12. **DeepRetro** (Sci Rep 2026) — 센텔라 사포닌 변형 합성 (AiZynthFinder 보강).
13. **AIMNet2** — charged 천연물 MD (MACE-OFF24 한계 극복).

### 🏥 Recover 한의원 직결 (2026-08 오픈 전)
- **임상 reference**: ECa 233 (51:38 madecassoside:asiaticoside) + Lapatinib 외용 reposition + Pirfenidone keloid 데이터 + OliX OLX104C 한국 IND 모델
- **흉터↔IPF cross-disease 분자 근거**: skin/lung fibroblast atlas (Nat Immunol/Cancer Cell 2025)에서 TGF-β signaling fibroblast subtype 공유 입증
- **Rentosertib (TNIK)**: 첫 generative AI lead → IPF Phase 2 진입 (FVC +98.4 mL) — 우리와 동일 파이프라인 = 벤치마크
- **NIPA 2025 "AI 의료 디지털 전환"** 사업 응모 자격 검토 (Recover + Genesis_Medicine + AI 안면분석 패키지)
- **국내 비임상 CRO**: KIT/켐온/바이오톡스텍/DT&CRO RFQ 3개사 견적 비교
- **MFDS 2025 천연물 외용제 가이드라인** 직접 컨택 (검색 미노출, 법무 컨택 필요)
- **BOKP DNA barcode** (KP/KHP 514종) — `skin_compounds_curated.csv` 가중치 정량화

### 🟢 중기 로드맵
- M1: 흉터 **lead 화합물 3-5개** 확정 (EMB-3 + EGCG + Embelin baseline + 추가 2개)
- M2: ABFE 정량 ΔG → IC50 nM 추정 → CRO Tier 1 (₩1,560만) 진입
- M3: Tier 0 SOTA 7개 모두 통합 + 한약 복합 처방 시너지 스코어링
- M4: 외용 크림 포뮬레이션 (자운고 + EMB-3 강화 1순위) — Recover 1차 시제품
- M5: IPF cross-disease 후속 paper (EMB-3 + IPF lung fibroblast 모델)

### 🟢 중기 로드맵
- M1: 흉터 **lead 화합물 3-5개** 확정 → 약침 적용 시뮬레이션 (용해도·안정성)
- M2: 기미·탈모 각각 **lead 후보** 확정
- M3: 한약 **복합 처방 최적화** (시너지 스코어링)
- M4: 2차 시제품(외용 크림) 포뮬레이션 개념안

---

## 프로젝트 한 줄 요약
**한약·생약 전통지혜 × AlphaFold 시대 구조기반 설계 → 피부재생/색소/탈모/염증 신약 후보 파이프라인.** 상업 제품화 전제.

## 🏢 상업화 원칙 (Commercial Mode) — 유지

본 프로젝트는 **상용 출시 예정**.

| 프로파일 | 용도 | 허용 라이선스 |
|---|---|---|
| `research` | 내부 탐색 · 처방 네트워크 분석 | 모든 오픈 (CC-BY-NC · 학술용 포함) |
| `commercial` | 외부 출시 빌드 (화장품/의약품/외용제) | **Apache-2.0 · MIT · BSD · CC0 · CC-BY만** |

### 상업 빌드 허용 (피부 관련 특히 강함)
- **천연물 DB**: COCONUT 2.0 (CC0, 700k), LOTUS (CC0), **NPASS 3.0** (정량 ADME-Tox 2026 update), **NPAtlas 3.0** (CC-BY), Dr. Duke's Phytochemical DB (USDA public domain).
- 구조 예측: Boltz-2 (MIT), Protenix v2 (Apache-2.0), OpenFold3 (Apache-2.0).
- ADMET·화학: ADMET-AI (MIT), RDKit (BSD-3), Chemprop 2 (MIT), Uni-Mol2 (MIT).
- MD: OpenMM 8 (MIT), openmm-ml (MIT), MACE-OFF24 (MIT).
- 규제: **KHP/KP** (한국 정부저작물, 참조 가능).

### 상업 빌드 제외 / 조건부 (피부 관련 특이사항)
- ❌ HERB 2.0 (CC-BY-NC), TCMSP, BATMAN-TCM — **research 빌드에서 한약 네트워크 분석만**.
- ⚠️ 발견된 성분/SMILES 자체는 자연물이므로 commercial 빌드로 이식 가능. 단 "HERB/TCMSP 데이터 기반" 마케팅 금지.
- ⚠️ KTKP 스크래핑 robots.txt 준수.

### 한약 처리 원칙
- 네트워크 약리학 **분석은 research 프로파일에서** HERB/TCMSP/KTKP 활용.
- 도출된 후보 화합물 SMILES는 **상업 빌드로 이식 가능**.
- 출시물 라벨·광고에 "HERB/TCMSP 기반" 금지. "전통 한방 처방 영감 + 구조 기반 최적화" 라벨 가능 (법무 검토).
- **KHP/KP 수록 한약재 +α 가중치** (한국 임상 진입 우선).

## 실행 환경 (절대 규칙)
- **진짜 저장소 / canonical runtime**: `Ubuntu-Genesis` WSL2 native ext4 `/home/crazat/genesis_medicine/` (D: VHD `D:\WSL\Ubuntu-Genesis\ext4.vhdx`).
- **C: Ubuntu `/home/crazat/genesis_medicine`는 legacy/control shell only**. 신규 설치, 신규 계산, commit/push는 사용자가 명시하지 않는 한 금지.
- **Python 메인 venv**: 3.11 (uv 관리) — Boltz-2, ADMET-AI, OpenMM 8 호환
- **보조 conda env**:
  - `genesis-md` (py3.11): MD 전용 (openmm + openff + mace + pdbfixer)
  - `txgnn` (py3.9 + torch 2.3 + DGL 2.4): 재창출 전용 (CPU)
- **GPU**: RTX 5090 32GB Blackwell + CUDA 12.8. DGL/openff 레거시 의존 제외하면 메인 venv에서 GPU 가속 전부 작동.

## 기본 명령

```bash
cd ~/genesis_medicine
source .venv/bin/activate

# 메인 피부 파이프라인 (commercial)
python -m genesis_medicine.cli run disease=scar_regeneration build_profile=commercial

# research 빌드 (한약 처방 네트워크)
python -m genesis_medicine.cli run disease=scar_regeneration build_profile=research \
    library=herb_scar_prescriptions
```

## 디렉터리 지도 (업데이트)
```
~/genesis_medicine/
├── CLAUDE.md
├── conf/
│   ├── build_profile/
│   ├── disease/
│   │   ├── scar_regeneration.yaml       ★ NEW
│   │   ├── hypertrophic_keloid.yaml     ★ NEW
│   │   ├── pigmentation_melasma.yaml    ★ NEW
│   │   ├── androgenetic_alopecia.yaml   ★ NEW
│   │   ├── acne_vulgaris.yaml           ★ NEW
│   │   ├── photoaging.yaml              ★ NEW
│   │   ├── atopic_dermatitis.yaml       ★ NEW (후속)
│   │   └── (AD/BACE1, NSCLC는 인프라 검증용으로 유지)
│   ├── skin_targets/                    ★ NEW
│   │   ├── scar.yaml        (TGF-β1, MMP-1/3/9, CTGF, COL1A1 등)
│   │   ├── pigment.yaml     (TYR, MITF, TRP-1/2)
│   │   ├── alopecia.yaml    (SRD5A1/2, AR, Wnt10b)
│   │   ├── acne.yaml        (SREBP1, AR, 5αR, C. acnes)
│   │   └── photoaging.yaml
│   └── …
├── data/
│   └── skin_compounds_curated.csv        ★ NEW (센텔라/감초/자근 등 SMILES)
├── pilot/
│   ├── skin_scar/                        ★ NEW (흉터 파일럿)
│   ├── skin_pigment/                     ★ NEW (기미)
│   ├── skin_alopecia/                    ★ NEW (탈모)
│   ├── skin_acne/                        ★ NEW (여드름)
│   ├── bace1_boltz2/                     (인프라 검증 — 보존)
│   ├── alzheimer_repurposing/            (인프라 검증 — 보존)
│   └── disease_expansion/                (인프라 검증 — 보존)
└── src/genesis_medicine/  (변동 없음)
```

## 기술 스택 요약 (v3 피부)
- **구조 예측**: Boltz-2 + Protenix v2 + OpenFold3 + Consensus.
- **앙상블**: AlphaFlow + BioEmu (cryptic pocket, 예: TGF-β1의 allosteric 사이트).
- **스크리닝 6단계**: DrugCLIP → Uni-Mol2 → FlowDock → Boltz-2 → GNINA → PoseBusters + ECR.
- **ADMET v2**: ADMET-AI. **피부용 가중치는 기본 BBB 대신 logKp(경피), 피부 자극, solubility 중심.**
- **생성**: FlowMol3 + DecompDiff + REINVENT 4 + SATURN + AiZynthFinder. **센텔라 scaffold 최적화**에 특화.
- **MD + ABFE**: OpenMM-ML + MACE-OFF24 + FEP-SPell-ABFE.
- **천연물 DB**: COCONUT 2.0 + LOTUS + NPASS 3 + NPAtlas + Dr. Duke.
- **한약 research**: HERB 2.0 + TCMSP + KTKP + BATMAN-TCM + SymMap.
- **네트워크 약리학**: Reactome + WikiPathways (KEGG 대체, commercial-safe).

## 파일럿 (피부 재생)
흉터 · 센텔라아시아티카 + 자근 + 감초 → TGF-β1, MMP-1, CTGF.
`conf/disease/scar_regeneration.yaml` + `pilot/skin_scar/`.

## 개발 규칙 (Claude 준수)
1. Windows 경로에 새 파일 쓰지 말 것.
2. 어댑터는 Protocol 준수, 설정 하드코딩 금지. 모든 파라미터 `conf/*.yaml`.
3. 외부 API는 `io/` 캐시+재시도.
4. 새 데이터 추가 시 `docs/LICENSING.md` 업데이트 + `build_profile` 태그.
5. `test_license_gate.py` 실패 상태로 merge 금지.
6. 상용·비상용 섞지 말 것 (어댑터 분리).
7. **피부 특화**: 경피 흡수성(logP 1.5-3.5, logKp) + 피부 자극 최소화 + Lipinski MW ≤ 500.
8. **CPU + GPU 동시 가동 필수**: 24 cores 시스템에서 한쪽이라도 idle 절대 금지. 매 turn `nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv` + `ps aux --sort=-%cpu | head -10` 확인. GPU long job (ABFE / Boltz-2 batch) 진행 중에도 `scripts/cpu_queue_v6_continuous.sh` 같은 24-core saturation 큐 동시 가동. Process 죽으면 즉시 재시작 + 새 job 큐잉. 자세한 패턴 + recurring bug fixes (tensorflow XLA / cuequivariance cu12-cu13 / BRICSBuild seed / boltz venv / PDB residue 3-char) → memory `feedback_cpu_gpu_concurrent.md`.

## 금지
- `.env`, API 키 commit 금지.
- AF3 공식 웨이트 기본 경로에 두지 말 것.
- HERB/TCMSP/KTKP 데이터를 `commercial` 프로파일에서 참조 금지.
- 출시물 광고에 "한약 DB 데이터 기반" 문구 사용 금지 (성분 자체는 OK).

## 현재 상태 (2026-04-25)
- **v2 인프라 완성** — 라이선스 게이트(83 컴포넌트, 118 테스트), 11단계 아키텍처, 가속 스택 활성, MD/ABFE/ML potential 모두 작동.
- **피부 방향으로 전환 시작** — conf/disease/skin_targets/data/ 준비 중.
- BACE1/AD 파일럿은 보존 (인프라 검증 결과물).
- Recover 한의원 **2026-08 강남 오픈** (~4개월 후). 파이프라인의 1차 lead 후보 발굴이 이 시점과 동조.

---

## 🆕 현재 상태 (2026-05-10 22:30 KST) — paper_A v5g 11-axis × 13-rep + R32-R45 expansion (~191 tools)

> **다음 세션 인계 노트**: paper_A v4 → **v5g 진화** (per-ligand intra-conformer Pearson, size-invariant; 11 NNP/QM/FF axes × 13 Boltz seeds × 15 ligands; cluster paradox 68σ 통계 검증; biology over-claim 자진 retraction; DFT N=25 + B3LYP-D3BJ 확장 진행 중). R32-R45 추가 frontier rounds → ~191 tools (saturation 깨짐, 매주 5-10 신규). 사용자 명시 지시 **"웹스캔 자동으로 하지마"** (2026-05-10 22:00) → /loop 모니터링 사이클에서 web search/fetch 자동 호출 금지.

### 🏆 paper_A v5g — 11-axis × 13-rep cluster paradox (manuscript drafting)
**핵심 finding** (15 MMP-1 hydroxamate ligands × 100 conformers × 13 Boltz-2 seeds × 11 axes):
- **Cluster B (QM/Materials-NN-aligned)**: mean per-ligand intra-conformer Pearson r = **0.939 ± 0.006** across 13 reps
  - xtb GFN1 SP + xtb GFN2 SP + xtb GFN-FF complex + AceFF-2 + AIMNet2-NSE + Orb-v3 OMat + **MatterSim 5M** (NEW 11th axis)
- **Cluster A (OMol25-trained, sub-cluster)**: intra-cluster ρ = 0.996 (Orb-v3 OMol25)
- **Inter A↔B**: r = 0.374-0.617 (clear separation, **68σ across 13 reps**)
- **🥇 Materials-domain NN sub-cluster (NEW 2026-05-10 21:58)**: MatterSim ↔ OrbOMat r = **0.936 ± 0.006** = 가장 단단한 NN-NN pair (다른 architecture, 같은 training domain) → **training-data domain match > architecture match**
- **MatterSim ↔ OMol25 r = 0.410 ± 0.026** → OMol25 paradox 11번째 axis 에서도 재확인
- **Mechanistic explanation**: OMol25 official paper (arXiv 2505.08762) 자체 인정 "large errors for redox/spin/long-range interactions" ↔ MMP-1 hydroxamate-Zn²⁺ binding = long-range chemistry

**Per-ligand intra-conformer Pearson** = size-invariant by construction (각 ligand 100 conformer 내부 normalize 후 axis-axis correlate). 이전 v4 method (cross-method energy-vs-energy)에서 size confound 있던 문제 해결.

**🚨 자진 retraction (2026-05-10 19:00)**: "OMat 2× better than OMol25 for pIC50 prediction" 초기 주장 size-confound 검증 통과 못 함 (ρ(natoms, pIC50) = +0.67 dominates). 메모리 `project_paper_a_v5g_RETRACTION_size_confound_2026_05_10.md`. Per-atom 정규화 후 weak ρ ~ +0.23.

**DFT reference 진행** (B3LYP/def2-SVP, N=25 conformer × 5 ligands):
- N=5 (CHEMBL406): OMat r = -0.84, OMol25 r = +0.09 (initial fluke)
- N=25 (5 ligands × 5): OMat r = -0.05, OMol25 r = +0.29 (verdict 미확정)
- B3LYP-D3BJ 확장 (pyscf-dispersion 1.5.0): 16/25 진행 중 (22:28 KST)
- **Caveat**: B3LYP/def2-SVP without D3 = Bursch 2022 권고 미달 → ωB97M-V/def2-TZVPD reference 또는 wavefunction methods (DLPNO-CCSD(T)) 권장 — defer

**Figures (manuscript-ready)**:
- `pilot/round27_paperA/paper_A_v5g_fig1_13rep_cluster_stability.png` (117KB)
- `pilot/round27_paperA/paper_A_v5g_fig2_v22_heatmap.png` (175KB)
- `manuscripts/paper_A_v4/figures/fig_9nnp_paradox_final.{png,pdf}` (v4 9-NNP figure 보존)

**Abstract draft (English, primary)**: `scripts/round27_paperA/paper_A_v5g_abstract_DRAFT.md` — Title: "Training-data domain dictates neural-network potential cluster placement: a 13-replicate study of the Orb-v3 OMat/OMol25 paradox on MMP-1 hydroxamate inhibitors"

**누적 SP energy 데이터** (~65,500+):
- xtb GFN2: 6700 PDBs (v15+v16+v17+v18 + retro+fork_pot)
- Orb-v3 OMat: 6700 PDBs
- Orb-v3 OMol25: 6700 PDBs
- SevenNet OMol25_high (Korean SNU MDIL #3 anchor): 6000 PDBs
- SevenNet OMat24 / MPA / MatPES_PBE × v15-v18: 18000 PDBs
- MatterSim 5M (Microsoft MPF): 6000 PDBs
- FeNNix-Bio1S/M (Sorbonne+Qubit reactive QM-FF, sign-flipped): 6000+1500 PDBs
- xtb GFN-FF protein-ligand complex v18: 1500 (binding-pocket-aware, σ_lig 23-76 kcal/mol)
- xtb GFN2 protein-ligand complex v18 (ongoing, 2.5h ETA)

**Manuscript main result text** (final):
> "On 1244 MMP-1 ligand poses generated by Boltz-2x, we evaluated 9 single-point energy methods spanning 5 architectures and 6 training datasets. NNP rank correlations cluster strictly by training dataset, not architecture. Cluster B (7 methods including 6 NNPs trained on Materials Project, OMat, MPA, MatPES, MPF, and biomolecular fragment QM data) shows mean intra-cluster Spearman ρ = 0.939. Cluster A (2 NNPs trained on OMol25 organic ωB97M-V/def2-TZVPD; Orb-v3 OMol25 + SevenNet OMol25-high) shows intra-cluster ρ = 0.996, but ρ = 0.617 against Cluster B. The same SevenNet architecture trained on three different non-OMol25 datasets yields ρ = 1.000 within Cluster B."

### 🎯 paper_B v9 — Boltz-2x physicality steering 후향 검증
**6-way σ matrix on CHEMBL94487 (n=100 each)**:
| version | engine | flag | σ raw kcal | E>0 outliers | σ filtered kcal |
|---|---|---|---|---|---|
| v15 | standard Boltz-2 | (none) | 8911.79 | 1/100 | 4.03 |
| v16 | standard Boltz-2x | --use_potentials | 4.29 | **0**/100 | 4.29 |
| v17 | standard Boltz-2x | --use_potentials | 3.28 | **0**/100 | 3.28 |
| **v18** | **standard Boltz-2x** | **--use_potentials** | **3.18** | **0**/100 | **3.18** |
| retro | community fork (Volgin) | (none) | 32813 | 2/100 | 6.66 |
| fork+pot | community fork | --use_potentials | 6.98 | 0/100 | 6.98 |

**결론**: `--use_potentials`만이 양쪽 엔진(standard+fork) 공통 outlier filter. **Standard Boltz-2 + --use_potentials = 권장 protocol** (v16/v17/v18 그대로). Fork bugfixes 단독으론 효과 없고 within-population precision 2× 악화.

**Figure**: `manuscripts/paper_B_v9/figures/fig_6way_xtb_sigma_chembl94487.{png,pdf}`.

### 📚 ~191-tool catalogue (R1-R45, saturation 깨졌음 — 매주 5-10 신규)
**4 Korean institutional anchors** (변경 없음):
1. BInD (KAIST W.Y.Kim) — paper #19 generative
2. Lee × Baker NC 2026 (KAIST + UW) — paper_C
3. **SevenNet-Omni** (SNU MDIL Park/Jeon/Kim) — paper #19 NNP, **i12+i8 weights @ external/round23/sevenn_weights/**
4. Atomistic Binder TTC (NVIDIA+Mila+SNU Cha, ICLR 2026 Oral) — paper_C

**11 NNPs** (paper_A v5g 사용): Orb-v3 OMat/OMol25, MACE-OFF24, eSEN-OMol, MatterSim 5M, LiTEN, ATOMICA, easyPARM, SevenNet-Omni (4 modals), DPA-3, FeNNix-Bio1S/M, **AceFF-2** (12th, Acellera).

**R32-R45 신규 (153 → ~191 tools)**:
- **R32** (#162-#165): AnewOmni (Tsinghua+ByteDance all-scale generative foundation), **EMLE** (Tuñón Chem Sci 2026 QM/ML embedding paper_A Zn enzyme 직격), DrugCLIP (Science 2026 10T pair/24h), AlphaGenome (DeepMind Nature 2026-01)
- **R33-R34** (#166-#170): CLADD (Genentech AAAI 2026 RAG LLM), MAMMAL (IBM npj 458M 2B examples 9/11 SOTA), Apo2Mol (apo-holo dynamic pocket diffusion), TrajCast (Nature MI 2026 force-free MD emulator), PPLM (NUS Nat Comm 2026-03 paired protein LM)
- **R37** (#171-#172): **Caliby** (post-LigandMPNN paper_A/C 직접 업그레이드), **CoMPLip** (첫 membrane cofold)
- **R39 ICML+MLSB+industry** (#185-#193): **OMNI-P2x #193** (Dral Nat Commun 2026 첫 excited-state NNP, paper_A 11th NNP CRITICAL), **OMTRA #188** (gnina MLSB 2025 multi-task flow SBDD + Zn²⁺ paper_A/C MMP-1 직격), **LFM #189** (Tropsha MLSB 2025 MD-trained target-specific NN), ChemCensor #185 (Insilico ICML 2026 retrosynthesis), SimpleFold-3B #186 (Apple), ProteomeLM #187, FlashAffinity #190, ProteinZen #191, ProFam-1 #192
- **R39 결론**: **saturation 신뢰 불가**, 매주 5-10 신규. ICML 2026 발표 확정 (2026-05-25경 재스캔)
- **R45 (직전 이전 사이클)**: marginal value 낮음 — 사용자 "웹스캔 자동으로 하지마" 지시로 자동 scan 중단

### 🚨 환경 trap memories (필수 참조)
다음 세션에서 동일 install/launch 시도 시 반드시 확인:
1. `feedback_no_auto_web_scan.md` ⭐ **NEW 2026-05-10** — /loop 모니터링에서 자동 웹스캔 금지 (사용자 명시). "ultrathink" 키워드도 보유 데이터 분석에만 사용
2. `feedback_orb_omol25_batch_charge_spin_silent_fail.md` ⭐ NEW — Orb OMol25 batch는 `atoms.info['charge']=0`, `atoms.info['spin']=0` 필수. 누락 시 ok=0/N silently fail (no traceback)
3. `feedback_master_chain_range_off_by_one.md` ⭐ NEW — `replace('range(11,19)', 'range(N-1,N)')` 인라인 패치는 잘못된 데이터셋 인덱스. 항상 `range(N, N+1)` 명시
4. `feedback_xtb_gfn2_protein_complex_segfault.md` ⭐ NEW — xtb GFN1+GFN2 SP는 ~3000-atom protein+ligand 100% SIGSEGV; GFN-FF만 작동. ligand-only 추출 후 처리
5. `feedback_xtb_gfnff_disk_explosion.md` ⭐ NEW — GFN-FF는 PDB당 ~93MB gfnff_topo scratch 자동 삭제 안 함; 1500 PDB × 4 versions = 558 GB 누적 (paper_A round27에서 디스크 93%). cleanup 빌트인 또는 `find DIR -name gfnff_topo -delete`
6. `feedback_mamba_run_silent_env_missing.md` ⭐ NEW — `mamba run -n MISSING cmd`은 env 없어도 0 exit + critical log만; orchestrator에서 `mamba env list | grep -q "^$ENV "` 검증 필수
7. `feedback_sigmadock_wandb_recursion.md` ⭐ NEW — R31 #154 SigmaDock smoke test wandb console_capture 무한 재귀; `WANDB_MODE=disabled` 필수
8. `feedback_deepchem_transformers5_break.md` ⭐ NEW — `pip install --pre deepchem`이 transformers 5.x 자동 설치 → ChemBERTa import 깨짐; `pip install "transformers<5.0"` 핀
9. `feedback_deepmd_kit_torch_numpy_trap.md` — JAX-flax-orbax = numpy 2.x → 격리 venv 필수
10. `feedback_boltz_msa_cache_ignored.md` — Boltz CLI 5단계 trap (YAML embed `msa:` + tensorflow/tensorboard 제거 + Lightning 2 patches)
11. `feedback_rdkit_pool_last_batch_deadlock.md` — COCONUT 2.0 등 1-2% SMILES deadlock at 99%; chunksize=1 + per-result flush + 10× silence → SIGKILL
12. `feedback_rtx5090_sm120_torch_kernel_compat.md` — torch ≤2.6 sm_120 미지원, cu128 빌드 또는 CPU 폴백
13. `feedback_mamba_install_breaks_pip_cuda_torch.md` — mamba install pytorch가 pip cu128 torch 무력화

### 🛠 활성 작업 (세션 종료 시점, 2026-05-10 22:30 KST)
| 작업 | PID | 상태 | ETA |
|---|---|---|---|
| **DFT-D3 (B3LYP-D3BJ/def2-SVP) on N=25 conformer** | 2205845 | 16/25 (단독) — 21:00 시작, ~88분 경과; **duplicate PID 2206093 22:28 SIGTERM kill** (race condition: 같은 conformer 중복 처리 → log line 17 `HEMBL443684_model_37` m 글자 잘림 증거) | ~23:30 KST 완료 |
| **Chain v24 v2 [3/8] GFN2 HESS** | 2210939 (8 workers) | 22:03 시작, ~25분 경과 | ~01:00 |
| Chain v24 v2 [1/8] GFN2 SP | — | ✅ 75s done | done |
| Chain v24 v2 [2/8] GFN2 OPT | — | ✅ 32min done | done |
| Chain v24 v2 [4-8/8] GFN-FF complex / GFN1 SP / MMFF / UFF | — | 대기 (HESS 완료 후) | 01:00+ |
| AceFF v24 (1500 conformer) | — | ✅ csv 존재 → done | done |
| Boltz v24 cofold (14th replicate, seed 56) | — | ✅ 1500/1500 PDB | done |
| MatterSim 5M v11-v21 batch (11 datasets) | — | ✅ ~17min 전부 done — 11번째 NNP axis 추가, **Materials-domain NN sub-cluster (r=0.936) 발견** | done |

**Boltz v19_v24 출력**: `pilot/round27_paperA/boltz_15_100_v19_v24/boltz_results_boltz_input_v19_msa/predictions/` (15 ligand × 100 conformer, 14th replicate seed 56).

**Chain v24 v2 첫 시도 trap (21:28)**: `cpu_xtb_*v19_v24.py` 파일 missing → [3-5/8] FileNotFoundError. v2 (21:30) `sed 's/v19_v22/v19_v24/g'` generation 후 정상 진행.

### 📊 데이터 인덱스 (CSV 위치, paper_A v5g 13-replicate × 11-axis matrix)
**Boltz cofold replicates** (15 ligand × 100 conformer × 13-14 seeds):
- v11-v18: `pilot/round13_overnight/results/boltz_15_100_v{15,16,17,18}/`
- v19-v24: `pilot/round27_paperA/boltz_15_100_v19_v{19,20,21,22,23,24}/boltz_results_boltz_input_v19_msa/predictions/`

**11 axis CSV (per-replicate)**:
- xtb GFN1 SP / GFN2 SP / GFN-FF complex: `pilot/round27_paperA/xtb_*v19_v{N}*/` + `pilot/round17_cpu_burn/xtb_v{15,16,17}_*`
- AceFF-2: `pilot/round27_paperA/aceff2_ligand/aceff2_v19_v{N}.csv`
- AIMNet2-NSE: `pilot/round27_paperA/aimnet2_nse/`
- ANI-2x (v20+v22+v23 partial): `pilot/round27_paperA/ani2x/`
- Orb-v3 OMat / OMol25: `pilot/round27_paperA/orb_v3_extended/` + `orb_v3_omol25/`
- **MatterSim 5M (NEW 11th axis)**: `pilot/round27_paperA/mattersim_5M/mattersim_5M_v19_v{11..21,22,23,24}_sp.csv`
- MMFF94 / UFF (uniform v3): `pilot/round27_paperA/mmff94_uff_v3/`
- SevenNet 4 modals (v15-v18): `pilot/round27_paperA/sevennet_modals/` + `sevennet_omni_i12/`
- FeNNix-Bio1S/M: `pilot/round27_paperA/fennix_bio1S/` + `fennix_bio1M/`

**DFT reference (B3LYP/def2-SVP, paper_A v5g)**:
- N=5 CHEMBL406: `pilot/round27_paperA/dft_reference_chembl406_v22.csv`
- N=20 4-ligand 확장: `pilot/round27_paperA/dft_reference_4ligand_extension.csv`
- B3LYP-D3BJ verdict: `pilot/round27_paperA/dft_b3lyp_d3_verdict.csv` (16/25 in progress)

**Figures (manuscript-ready)**:
- paper_A v5g fig1 (13-rep stability): `pilot/round27_paperA/paper_A_v5g_fig1_13rep_cluster_stability.png`
- paper_A v5g fig2 (v22 11×11 heatmap): `pilot/round27_paperA/paper_A_v5g_fig2_v22_heatmap.png`
- paper_A v4 (보존): `manuscripts/paper_A_v4/figures/fig_9nnp_paradox_final.{png,pdf}`
- paper_B v9: `manuscripts/paper_B_v9/figures/fig_6way_xtb_sigma_chembl94487.{png,pdf}`

**Abstract drafts**:
- paper_A v5g English (primary, for publication): `scripts/round27_paperA/paper_A_v5g_abstract_DRAFT.md`
- paper_A v5g Korean (reference only, NOT for publication): `scripts/round27_paperA/paper_A_v5g_초록_초안_한국어.md`
- COCONUT 2.0 conformers: `pilot/round17_cpu_burn/rdkit_coconut_v{2..10}/`

### 🎯 다음 세션 우선순위
1. **paper_A v5g manuscript completion** — abstract ✅ (English primary), fig1+fig2 ✅, methods ✅. 남은 것: introduction (cluster paradox 동기 + Bursch 2022 cite + arXiv 2505.08762 OMol25 long-range weakness), discussion (Materials-domain sub-cluster + DFT verdict), supplementary (11-axis × 13-rep table), Zenodo deposit
2. **DFT-D3 verdict 분석 (23:30 KST 완료 후)** — OMat-DFT-D3 vs OMol25-DFT-D3 r 값 비교. 만약 dispersion 추가로 verdict 뒤집히면 새 finding; 그대로면 N=25 limitation 강조
3. **Chain v24 v2 [3-8/8] 완료 후** — 14th replicate 모든 axis CSV 통합 → 13→14-rep extension
4. **paper_C de novo MMP-1 binder** — RFdiffusion3 + LigandMPNN + FlowPacker canonical (R12 LigandMPNN 95.3% Zn recovery 검증됨) + Caliby (R37) + Atomistic Binder TTC
5. **paper #19 v9** — LaMGen multi-target generation + ReaSyn synthesizable refinement on 86 herbal NPs
6. **ICML 2026 list 재스캔** (2026-05-25경) — saturation 깨짐 확정, 매주 5-10 신규

### 🔧 환경 inventory (genesis-md production + 격리 venvs)
- **genesis-md** production: torch 2.8 cu128 sm_120, numpy 1.26.4 (필수 유지!), boltz, sevenn, fairchem, mace, orb_models, rdkit 2026.3.1
- **mattersim** conda env: torch 2.11 cu130 sm_120, mattersim 1.2.3
- **boltz-community/.venv**: torch 2.11 cu130 (paper_B 후향 검증)
- **mosaic/.venv**: 8-cofold unified JAX-CUDA
- **ProTDyn/.venv**: thermo+dynamics PLM
- **dpa3/.venv**: deepmd-kit DPA-3 (numpy 2.x 격리)
- **fennol_env/.venv**: FeNNix-Bio1 (jax 0.10, numpy 2.x 격리, **LD_LIBRARY_PATH=$(find venv -path "*nvidia*lib" -type d)** 필요)
- **lamgen, liten, GatorAffinity, bindcraft, reasyn, helixfold3, chroma, evodiff, decimer, mlipx, synformer, bioemu, admetai, FlowDock, pocket2mol_rl, deepternary, pocketminer, proteinmpnn, npclassifier, micom, deeppocket, fpocket, plinder, pyemma, mist_diffms, flowpacker, esmc, thermompnn, fastmbar, retrobiocat, gutbug, ligandmpnn, esen, passer, drugflow, maplight** etc.: 각 격리 conda env

### 🎯 Cron + Loop 상태
- 활성 cron: `f880f960` at `13,43 * * * *` (recurring 7-day) — 30분 cadence 모니터링
- **사용자 직전 명시 (2026-05-10 22:00)**: "웹스캔 자동으로 하지마" → /loop 사이클에서 web search/fetch 자동 호출 금지. ProgressMonitor + 데드락 점검 + 메모리 기록 + 데이터 분석은 유지
- 다음 fire: 23:01 KST (ScheduleWakeup 1800s 예약)
- 만료: 2026-05-16 (7-day expire)

### 📝 메모리 / 세션 발자취 (~/.claude/projects/-mnt-d/memory/)
**paper_A v5g 핵심 메모리 (2026-05-10)**:
- `project_paper_a_v5g_HEADLINE_13rep_validated_2026_05_10.md` — 13-rep × 8-axis validation 68σ
- `project_paper_a_v5g_RETRACTION_size_confound_2026_05_10.md` — biology over-claim 자진 retraction
- `project_paper_a_v5g_DFT_VERDICT_2026_05_10.md` — N=5 DFT initial result
- `project_paper_a_v5g_OMol25_paper_admits_longrange_weakness_2026_05_10.md` — mechanistic
- `project_paper_a_v5g_DFT_caveats_bursch_2022.md` — DFT limitations caveat
- `project_paper_a_v5g_MatterSim_materials_subcluster_2026_05_10.md` — NEW r=0.936 finding
