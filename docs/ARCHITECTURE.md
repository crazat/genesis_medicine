# Genesis_Medicine v2 — Architecture (2026-04)

> "Google의 단백질 예측 프로그램을 이용해 신약/한약 구조 예측" 재설계  
> 작성: Claude Opus 4.7 (1M) · 2026-04-25 · ultrathink

## 1. 재설계의 대전제

### 1.1 2024~2026년 사이에 일어난 핵심 변화
1. **AlphaFold 3 공개 (2024-11)** — 단백질·핵산·저분자 리간드·PTM·이온을 **하나의 diffusion 모델**로 통합 예측. 도킹의 패러다임 자체가 바뀜.
2. **AF3 웨이트는 여전히 비상업 전용** ([WEIGHTS_TERMS_OF_USE](https://github.com/google-deepmind/alphafold3/blob/main/WEIGHTS_TERMS_OF_USE.md)). 신약 프로젝트에 직접 쓸 수 없음.
3. **오픈 대안 폭발**:
   - **Protenix v2** (ByteDance, **2026-04-08 릴리스**, Apache-2.0) — AF3를 벤치마크에서 능가하는 첫 완전 오픈 모델.
   - **Boltz-2** (MIT, 2025-06) — AF3-급 공동접힘 + **FEP 수준 친화도 예측을 1000× 속도**로. 둘 다 상용 OK.
4. **천연물 DB 대형화** — COCONUT 2.0이 63개 NP 소스 통합, 700k 화합물 CC0.
5. **LLM 기반 de novo**: TxGemma, BioMedGPT, REINVENT 4가 실제 파이프라인에 들어옴.

### 1.2 사용자 원래 의도와 매핑
- "구글의 단백질 예측 프로그램" = AlphaFold 계열 → **Protenix v2 + Boltz-2 + AlphaFold DB**로 현대적 대체.
- "신약 개발" = 합성 분자 de novo + 가상 스크리닝 → **REINVENT 4 + DiffSBDD + Uni-Mol2 + GNINA**.
- "기성 약(한약/생약) 구조 예측" = 알려진 천연물의 타겟·메커니즘 해석 → **COCONUT + HERB + TCMSP + KTKP** 라이브러리를 **네트워크 약리학**으로 역해석.

### 1.3 설계 원칙
1. **오픈 웨이트·상용 허용** 도구만 기본 스택에 포함. 가두리(gated) 모델은 선택 옵션.
2. **단계적 스크리닝** — 값싼 임베딩 유사도 → 도킹 → 공동접힘 → MD. 각 단계마다 99% 탈락시킴.
3. **설정 주도(Config-driven)** — Hydra로 질병/타겟/라이브러리/모델 전부 YAML.
4. **재현성** — DVC + MLflow + seed 고정 + 컨테이너.
5. **Windows+CUDA 12 우선** — WSL2 Ubuntu 22.04 + Docker 기본 전제. 네이티브 win32은 cheminfo 계층만.

## 2. 참고 기술 스택 (2026-04 SOTA)

| 계층 | 선택 | 라이선스 | 근거 |
|---|---|---|---|
| 구조예측(단백질+리간드) | **Protenix v2** | Apache-2.0 | AF3 능가, 2026-04 릴리스, 상용 OK |
| 구조예측(친화도 포함) | **Boltz-2** | MIT | FEP 1000× 속도, 완전 오픈 |
| 빠른 단일시퀀스 | **ESMFold** (ESM-3) | Cambrian (조건부 상용) | MSA 없이 초급속 |
| 공개 구조 DB | **AlphaFold DB** 214M | 무료 | UniProt 전체 커버 |
| 포켓 탐색 | **P2Rank** / **FPocket** | Apache-2.0 / GPL | P2Rank가 ML 기반, 더 정확 |
| 블라인드 도킹 | **DiffDock-L** | MIT | PoseBusters 38% top-1 |
| 도킹 재스코어 | **GNINA 1.3** | Apache-2.0 | CNN 스코어링 |
| de novo 생성 | **REINVENT 4** | Apache-2.0 | 멀티 오브젝티브 RL |
| 포켓 조건부 생성 | **DiffSBDD**, **TargetDiff**, **Pocket2Mol** | MIT | 3D 포켓 조건부 |
| 분자 언어모델 | **TxGemma** (Google) / **MolFormer-XL** / **Uni-Mol2** | Gemma / Apache-2.0 / MIT | 멀티모달 치료제 FM |
| ADMET 예측 | **ADMET-AI** (41 endpoints) + **Chemprop 2.0** | MIT | Stanford Zitnik lab |
| 타겟 ID | **Open Targets Platform API** + **PrimeKG** | Apache-2.0 / MIT | target-disease KG |
| 바이오 NER | **BERN2** / **GliNER-BioMed** | BSD-2 / Apache-2.0 | d4data 구모델 대체 |
| 문헌 임베딩 | **PubMedBERT** / **BioGPT** | MIT / MIT | 초록 임베딩·검색 |
| 천연물 DB | **COCONUT 2.0** + **LOTUS** | CC0 / CC0 | 700k+ 화합물 |
| 한약 DB | **HERB 2.0** + **TCMSP** + **BATMAN-TCM 2.0** + **SymMap** + **KTKP** | 혼합 | TCM·K-TCM 커버 |
| 화학 툴킷 | **RDKit 2025.03+** | BSD-3 | 사실상 표준 |
| MD 정제 | **OpenMM 8.x** | MIT | CUDA 12 지원 |
| 설정 관리 | **Hydra** + **Pydantic v2** | MIT / MIT | YAML 기반 |
| 실험 추적 | **MLflow** | Apache-2.0 | 로컬 서버 |
| 데이터 버전 | **DVC** | Apache-2.0 | Git-friendly |
| 워크플로 | **Prefect 3** | Apache-2.0 | Python 네이티브 DAG |
| 대시보드 | **Panel** / **Streamlit** + **py3Dmol** | BSD / Apache | 3D 시각화 |

## 3. 전체 파이프라인 (9단계)

```
┌─────────────────────────────────────────────────────────────────┐
│  [0] Disease Config (YAML: MeSH term, ICD-10, 목표 지표)        │
└────────────────────────────────┬────────────────────────────────┘
                                 ▼
┌──────────────────────────────────────────────────────────────────┐
│  [1] Target Discovery                                            │
│    • Open Targets GraphQL (evidence-weighted genes)              │
│    • PubMed Entrez batched → BERN2 NER → entity-normalized       │
│    • PrimeKG multi-hop (disease → pathway → protein)             │
│    • Druggability filter (TRACTABILITY, IDG 목록)                │
│  → targets.parquet (UniProt, gene, evidence, priority)           │
└────────────────────────────────┬─────────────────────────────────┘
                                 ▼
┌──────────────────────────────────────────────────────────────────┐
│  [2] Structure Preparation                                       │
│    • AlphaFold DB lookup (214M pre-computed)                     │
│    • 미제공 → Protenix v2 (local GPU, Apache-2.0)                │
│    • 부족하면 Boltz-2 apo                                         │
│    • P2Rank/FPocket → top-K 포켓 + residue list                  │
│  → structures/{uniprot}.cif + pockets.json                       │
└────────────────────────────────┬─────────────────────────────────┘
                                 ▼
┌──────────────────────────────────────────────────────────────────┐
│  [3] Ligand Library Assembly                                     │
│    • ChEMBL 35 (알려진 활성)                                      │
│    • COCONUT 2.0 (700k NPs, CC0)                                 │
│    • HERB 2.0 + TCMSP + KTKP (한약 화합물)                        │
│    • Enamine REAL / ZINC22 subset (합성 가능 가상)                │
│    • RDKit canonicalize → InChIKey dedup                         │
│    • PAINS, Lipinski, NP-likeness, QED 필터                       │
│  → ligands.parquet (SMILES, InChIKey, source, tags)              │
└────────────────────────────────┬─────────────────────────────────┘
                                 ▼
┌──────────────────────────────────────────────────────────────────┐
│  [4] Multi-Stage Virtual Screening                               │
│    Stage A: Uni-Mol2 embedding 유사도 → top 1-5%                 │
│    Stage B: DiffDock-L blind pose → top 1-5k                     │
│    Stage C: Boltz-2 co-folding + affinity → top 100              │
│    Stage D: GNINA CNN rescoring → ranked                         │
│  → screening_results.parquet (pose, score, affinity, rank)       │
└────────────────────────────────┬─────────────────────────────────┘
                                 ▼
┌──────────────────────────────────────────────────────────────────┐
│  [5] De Novo Generation (선택)                                    │
│    • DiffSBDD/TargetDiff 포켓 조건부 시드 (500~5k 생성)            │
│    • REINVENT 4 멀티 오브젝티브 RL (affinity + QED + SA + SAS)    │
│    • TxGemma prompt-based 후보 제안                               │
│  → novel_ligands.parquet + same 스크리닝 파이프로 반환             │
└────────────────────────────────┬─────────────────────────────────┘
                                 ▼
┌──────────────────────────────────────────────────────────────────┐
│  [6] ADMET & Safety Filtering                                    │
│    • ADMET-AI (41 endpoints, Chemprop 기반)                      │
│    • Lipinski/BBB/hERG/DILI flags                                │
│    • Structural alerts (Brenk, NIH)                              │
│  → admet_filtered.parquet                                        │
└────────────────────────────────┬─────────────────────────────────┘
                                 ▼
┌──────────────────────────────────────────────────────────────────┐
│  [7] Herbal Network-Pharmacology Overlay                         │
│    • 살아남은 천연물 SMILES → HERB/TCMSP/KTKP 역매핑               │
│    • 원천 한약재 → 한의학 증상(SymMap) → 현대 질병 매핑            │
│    • KEGG hsa05010 등 경로 교차검증                               │
│    • KHP/KP/MFDS 수록 여부 (규제 친화도)                          │
│  → herb_report.parquet (herb, compound, target, pathway, KHP)    │
└────────────────────────────────┬─────────────────────────────────┘
                                 ▼
┌──────────────────────────────────────────────────────────────────┐
│  [8] MD Refinement (상위 10~50개, 선택)                           │
│    • OpenMM 8 GPU, 10~50 ns NPT                                  │
│    • MM-GBSA 재평가 · 포즈 안정성 RMSF                            │
│  → md_results.parquet                                            │
└────────────────────────────────┬─────────────────────────────────┘
                                 ▼
┌──────────────────────────────────────────────────────────────────┐
│  [9] Reporting                                                   │
│    • MLflow 실험 로그 (parameters, metrics, artifacts)            │
│    • Panel 대시보드 (3D 포즈, 랭킹 테이블, 한약 네트워크 그래프)     │
│    • PDF 요약 (질병·Top10 화합물·Top5 한약)                        │
└──────────────────────────────────────────────────────────────────┘
```

## 4. 디렉터리 구조

```
Genesis_Medicine/
├── README.md
├── pyproject.toml                    # uv/hatch 관리
├── docker/
│   ├── Dockerfile.base                # CUDA 12.6 + Python 3.11 공통
│   ├── Dockerfile.structure           # Protenix v2 + Boltz-2
│   ├── Dockerfile.gen                 # REINVENT 4 + DiffSBDD
│   └── docker-compose.yml             # MLflow + Postgres + 서비스
├── conf/                              # Hydra 계층적 설정
│   ├── config.yaml                    # 기본 조합
│   ├── disease/
│   │   ├── alzheimer.yaml
│   │   ├── nsclc.yaml
│   │   └── parkinson.yaml
│   ├── target_discovery/
│   │   └── default.yaml
│   ├── structure/
│   │   ├── protenix.yaml
│   │   ├── boltz2.yaml
│   │   └── alphafold_db.yaml
│   ├── library/
│   │   ├── chembl.yaml
│   │   ├── coconut.yaml
│   │   ├── herb_tcm.yaml
│   │   └── ktkp.yaml
│   ├── screening/
│   │   ├── diffdock.yaml
│   │   └── boltz2_affinity.yaml
│   ├── generation/
│   │   ├── reinvent4.yaml
│   │   └── diffsbdd.yaml
│   └── admet/
│       └── admet_ai.yaml
├── src/genesis_medicine/
│   ├── __init__.py
│   ├── cli.py                         # 진입점 (typer)
│   ├── io/
│   │   ├── pubmed.py                  # 배치·재시도·체크포인트
│   │   ├── open_targets.py            # GraphQL
│   │   ├── uniprot.py
│   │   ├── alphafold_db.py
│   │   ├── chembl.py
│   │   ├── coconut.py
│   │   ├── lotus.py
│   │   ├── herb.py
│   │   ├── tcmsp.py
│   │   ├── ktkp.py                    # 한국전통지식포털 (스크래퍼)
│   │   ├── symmap.py
│   │   └── khp_mfds.py                # KP/KHP 파서 (PDF → JSON)
│   ├── targets/
│   │   ├── discover.py                # 파이프라인 오케스트레이션
│   │   ├── ner.py                     # BERN2 / GliNER 래퍼
│   │   ├── kg_primekg.py
│   │   └── druggability.py
│   ├── structure/
│   │   ├── base.py                    # Protocol
│   │   ├── alphafold_db_adapter.py
│   │   ├── protenix_adapter.py
│   │   ├── boltz2_adapter.py
│   │   ├── esmfold_adapter.py
│   │   └── pocket.py                  # P2Rank / FPocket
│   ├── ligand/
│   │   ├── library.py                 # 통합 라이브러리 빌더
│   │   ├── filters.py                 # PAINS, Lipinski, NP-likeness
│   │   ├── featurize.py               # Uni-Mol2, MolFormer 임베딩
│   │   └── conformers.py              # RDKit ETKDG
│   ├── screening/
│   │   ├── embedding_similarity.py    # Stage A
│   │   ├── diffdock_adapter.py        # Stage B
│   │   ├── boltz2_cofolding.py        # Stage C
│   │   └── gnina_rescore.py           # Stage D
│   ├── generation/
│   │   ├── reinvent4_adapter.py
│   │   ├── diffsbdd_adapter.py
│   │   └── txgemma_ideation.py
│   ├── admet/
│   │   └── admet_ai_adapter.py
│   ├── herbal/
│   │   ├── reverse_mapping.py         # compound → herb
│   │   ├── network_pharmacology.py    # KEGG/Reactome 교차
│   │   └── regulatory.py              # KHP/KP 수록 검증
│   ├── md/
│   │   └── openmm_refine.py
│   ├── reporting/
│   │   ├── mlflow_tracker.py
│   │   ├── dashboard_panel.py
│   │   └── pdf_report.py
│   └── utils/
│       ├── logging.py                 # loguru
│       ├── cache.py                   # requests-cache + diskcache
│       └── seed.py
├── pipelines/
│   ├── full_pipeline.py               # Prefect flow
│   └── subflows/
│       ├── target_discovery.py
│       ├── structure_prep.py
│       ├── screening.py
│       ├── generation.py
│       └── herbal_overlay.py
├── notebooks/                         # 탐색용 (운영 코드 없음)
│   └── exploratory_alzheimer_bace1.ipynb
├── tests/
│   ├── conftest.py
│   ├── fixtures/                      # 최소 PDB, SMILES 샘플
│   ├── unit/
│   └── integration/
├── data/                              # DVC 추적
│   ├── raw/
│   ├── processed/
│   ├── structures/
│   └── external/
├── mlruns/                            # MLflow
├── docs/
│   ├── ARCHITECTURE.md                # (이 문서)
│   ├── CODE_REVIEW.md
│   ├── DATA_SOURCES.md
│   ├── INSTALL_WINDOWS.md
│   └── adr/                           # Architecture Decision Records
└── scripts/                           # 일회성 ETL
    ├── bootstrap_chembl.py
    ├── bootstrap_coconut.py
    └── migrate_v1_data.py
```

## 5. 핵심 모듈 인터페이스

### 5.1 StructurePredictor Protocol (Python)

```python
# src/genesis_medicine/structure/base.py
from typing import Protocol, runtime_checkable
from pathlib import Path
from pydantic import BaseModel

class LigandSpec(BaseModel):
    smiles: str
    name: str | None = None
    ccd_code: str | None = None

class StructurePredictionRequest(BaseModel):
    protein_sequences: list[str]                  # chain당 FASTA
    ligands: list[LigandSpec] = []
    rna_sequences: list[str] = []
    dna_sequences: list[str] = []
    template_cif: Path | None = None
    seed: int = 42
    num_recycles: int = 10
    num_samples: int = 5

class StructurePredictionResult(BaseModel):
    cif_path: Path
    plddt_mean: float
    confidence_json: Path
    affinity_pKd: float | None = None             # Boltz-2 only

@runtime_checkable
class StructurePredictor(Protocol):
    def predict(self, req: StructurePredictionRequest) -> StructurePredictionResult: ...
```

→ 세 어댑터 (`protenix`, `boltz2`, `esmfold`)는 동일 인터페이스 구현. 파이프라인은 어댑터에 무관.

### 5.2 Hydra 설정 조합 예시

```yaml
# conf/config.yaml
defaults:
  - disease: alzheimer
  - target_discovery: default
  - structure: protenix           # ← 여기서 엔진 교체 가능
  - library: coconut
  - screening: boltz2_affinity
  - generation: reinvent4
  - admet: admet_ai
  - _self_

project:
  name: genesis_medicine
  output_dir: ${oc.env:GENESIS_OUT,./runs}
  seed: 42
  device: cuda:0
```

```bash
# 실행 예
python -m genesis_medicine disease=alzheimer library=herb_tcm structure=boltz2
```

### 5.3 Prefect Flow

```python
# pipelines/full_pipeline.py (요약)
@flow(name="genesis_full_pipeline")
def run(cfg: Config):
    targets = discover_targets.submit(cfg.disease, cfg.target_discovery)
    structures = prep_structures.map(targets, cfg.structure)
    library = build_library.submit(cfg.library)
    screening = multi_stage_screen.map(structures, library, cfg.screening)
    novel = generate_de_novo.map(structures, cfg.generation) if cfg.generation.enabled else []
    combined = merge_and_admet(screening, novel, cfg.admet)
    herbal = herbal_overlay(combined, cfg.library)
    refined = md_refine(herbal.top(50), cfg.md) if cfg.md.enabled else herbal
    return build_report(refined, cfg)
```

## 6. 데이터 수집 계층 개선 (v1 버그 수정 반영)

### 6.1 PubMed 배치 (`io/pubmed.py`)
- `retmax`를 **500건 청크**로 쪼개 반복 `efetch`, 각 청크별 JSON 캐시.
- `api_key` 지원 (rate limit 10 req/s).
- `diskcache`로 PMID → record 캐시 (재실행 시 미발송).
- Tenacity로 5xx/타임아웃 지수 백오프.
- 출력 파일명은 **질병 키에서 파생** (`{disease_key}_abstracts.parquet`).

### 6.2 HGNC 대체 (타겟 정규화)
- v1의 HGNC 어휘 교집합 제거.
- **BERN2 / GliNER-BioMed** 정규화 결과 (`normalized_id`) 그대로 사용 — NCBI Gene ID나 UniProt ID로 자동 매핑됨.
- fallback: [genenames.org REST](https://rest.genenames.org/) (`/fetch/symbol/{s}`).

### 6.3 Open Targets GraphQL
- 질병 EFO → 우선순위화된 타겟 리스트 (Overall Association Score, Genetic Evidence, Somatic Mutations, Tractability Bucket).
- BERN2 결과와 **점수 곱/가중 합산**으로 최종 순위. 단순 빈도 ❌.

## 7. 재현성 · 운영

| 항목 | 도구 | 비고 |
|---|---|---|
| 환경 | Docker (compose) | CUDA 12.6 베이스 |
| Python | uv + pyproject | 3.11 고정 |
| 시드 | `utils.seed.set_all` | numpy, torch, random, cuda |
| 데이터 | DVC | S3/MinIO 원격 |
| 실험 | MLflow | local tracking server |
| 설정 | Hydra + OmegaConf | override 지원 |
| 로깅 | loguru → 파일 + stderr | rotation 일간 |
| 테스트 | pytest + pytest-xdist | 유닛·통합 분리 |
| CI | GitHub Actions | lint/type/test/integration |
| 린트 | ruff + mypy | strict |

## 8. 개발 단계 (마일스톤)

| 단계 | 기간 | 결과물 |
|---|---|---|
| **M0: 부트스트랩** | 3일 | 디렉터리, Docker, Hydra, CI, 유닛테스트 프레임워크 |
| **M1: 타겟 발굴** | 1주 | Open Targets + BERN2 + PubMed 파이프라인, 알츠하이머 파일럿 |
| **M2: 구조 어댑터** | 2주 | AlphaFold DB + Protenix + Boltz-2 어댑터, BACE1 단일 타겟 end-to-end |
| **M3: 리간드 라이브러리** | 1주 | ChEMBL + COCONUT ETL, 필터링 |
| **M4: 다단계 스크리닝** | 2주 | Uni-Mol2 + DiffDock + Boltz-2 affinity + GNINA |
| **M5: 한약 레이어** | 1.5주 | HERB/TCMSP/KTKP ETL, 역매핑, 네트워크약리 |
| **M6: 생성 모델** | 2주 | DiffSBDD + REINVENT 4 통합 |
| **M7: ADMET + MD + 리포트** | 1.5주 | 최종 대시보드 |
| **M8: 두 번째 질병 이식** | 1주 | NSCLC/파킨슨 재현, 설정만 바꿔 동작 확인 |

≈ 14주 (1인 GPU 1장 기준). M0~M2가 핵심 스파이크.

## 9. 위험과 완화

| 위험 | 영향 | 완화 |
|---|---|---|
| Protenix v2 메모리 > GPU VRAM | 추론 실패 | Boltz-2 대체, chain crop, Docker swap |
| KTKP는 공식 API 없음 | ETL 비용 | 수동 크롤 → JSONL 1회 스냅샷, 매뉴얼 재갱신 분기별 |
| HERB CC-BY-NC | 상업화 걸림돌 | 내부 연구용으로 한정, 상업 단계에선 COCONUT만 |
| 대규모 NP 라이브러리 GPU 시간 | 비용 폭증 | 단계적 스크리닝 (A→D) 필수, Stage A에서 99% 컷 |
| AF3/Protenix 훈련셋 누출 | 벤치마크 과대평가 | PoseBusters + 시간 분리 테스트셋 검증 |
| Windows 네이티브 CUDA 호환성 | 설치 실패 | WSL2 + Docker만 공식 지원 |

## 10. 다음 행동 (즉시)

1. 이 문서 + CODE_REVIEW 를 팀/본인이 검토 → 합의.
2. `M0` 부트스트랩 먼저: `pyproject.toml`, Docker 베이스, Hydra 디폴트 설정, 첫 유닛테스트.
3. **M1 스파이크**: 알츠하이머 한 질병으로 Open Targets + BERN2만 돌려 `targets.parquet` 생성. 여기서부터 **파이프라인 뼈대**가 서면 나머지는 어댑터 붙이기.

---

### 참고 출처 (2026-04 검증)
- [Boltz-2 github](https://github.com/jwohlwend/boltz) · [MIT paper](https://jclinic.mit.edu/boltz-2-towards-accurate-and-efficient-binding-affinity-prediction/) · [bioRxiv](https://www.biorxiv.org/content/10.1101/2025.06.14.659707v1)
- [Protenix github](https://github.com/bytedance/Protenix) · [Protenix 서비스](https://neurosnap.ai/service/Protenix%20(AlphaFold3))
- [AlphaFold3 weights terms](https://github.com/google-deepmind/alphafold3/blob/main/WEIGHTS_TERMS_OF_USE.md) · [Nature 보도](https://www.nature.com/articles/d41586-024-03708-4)
- [COCONUT 2.0 NAR](https://academic.oup.com/nar/article/53/D1/D634/7908792) · [다운로드](https://coconut.naturalproducts.net/download)
