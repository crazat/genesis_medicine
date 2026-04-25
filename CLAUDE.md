# CLAUDE.md — Genesis_Medicine v3 (Skin Regeneration)

> Claude Code가 세션 시작 시 자동 로드하는 프로젝트 가이드.
> 세부 설계: `docs/ARCHITECTURE.md` · 라이선스: `docs/LICENSING.md`

---

## 🎯 프로젝트 목적 (2026-04-25 재정의)

**한약·생약·신물질로 피부 건강과 피부-연계 건강을 개선하는 신약 개발 파이프라인.**

### 포지셔닝
- 운영 주체: **Recover 한의원** (강남 2026-08 오픈 예정, <https://recover-clinic.kr>) — 한의 피부재생 전문.
- 핵심 슬로건: "만드는 미용이 아닌, 되돌리는 미용".
- 기존 무기: 새살침, 체질 한약 처방, 약침, 매선, 고주파/프락셔널, AI 안면 분석.
- 본 파이프라인의 역할: **임상 경험칙 → 분자 수준 메커니즘 규명 → 신약/외용제 후보 도출**.

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
- **진짜 저장소**: WSL2 ext4 `/home/crazat/genesis_medicine/`
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
