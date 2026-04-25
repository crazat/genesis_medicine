# CLAUDE.md — Genesis_Medicine v2

> Claude Code가 세션 시작 시 자동 로드하는 프로젝트 가이드.
> 세부 설계: `docs/ARCHITECTURE.md` · v1 검수: `docs/CODE_REVIEW.md` · 라이선스: `docs/LICENSING.md`

---

## 🎯 NEXT ACTIONS — 다음 세션에서 바로 할 일 (2026-04-25 v2.1 ultrathink 갱신)

> 이 섹션은 작업이 한 단계 진전될 때마다 업데이트한다.
> 사용자가 새 세션을 열면 이 목록부터 확인하고, **제일 위 항목을 먼저 제안**할 것.

### ✅ 완료 (2026-04-25 세션까지)
- ~~Windows 원본 삭제, 환경 부트스트랩~~ — `.venv` Python 3.11.15.
- ~~라이선스 게이트~~ — **83개 컴포넌트** 등록, **118개 테스트** 전부 통과.
- ~~Open Targets 호출~~ — 알츠하이머 상위 50 타겟 중 49개 UniProt ID 확인.
- ~~Boltz-2 BACE1 파일럿~~ — 9/10 화합물 공동접힘 성공. confidence=0.873.
- ~~v2.1 고도화 ultrathink 구현~~ — 11단계 아키텍처 뼈대 + 15개 새 컴포넌트:
  - **Stage 1.5** TxGNN 약물 재창출 (A1)
  - **Stage 2.5** AlphaFlow + BioEmu cryptic pocket 앙상블 (A2)
  - **Stage 4 보강** PoseBench v2 검증, DrugCLIP 설정, Active Learning (B4)
  - **Stage 5 보강** NeuralPLexer3 어댑터 (research only, A5), ConsensusPredictor (B5)
  - **Stage 5.5** BindCraft 단백질 바인더 (B1), PROTAC/분자글루 (B2)
  - **Stage 6** ADMET-AI v2 어댑터
  - **Stage 7** 한약 reverse_mapping + network_pharmacology
  - **Stage 8'** OpenMM-ML + MACE-OFF24(M) refine (A3)
  - **Stage 8.5** FEP-SPell-ABFE / pmx ABFE (A4)
  - **자체 MMseqs2-GPU MSA 모듈** (S4 — 상업 빌드 블로커 해소)
  - Boltz-2 affinity head 설정 완전 노출 (S1), cuEquivariance 가속 지원 (S2)

### 🟡 즉시 실행 (의존성 설치 + 실 추론 런)
1. **가속 스택 설치** — `pip install -e '.[accel]'` + (선택) `pip install boltz-blackwell` → `no_kernels: false`로 30~50% 가속.
2. **자체 MMseqs2-GPU 빌드** — `bash scripts/setup/install_mmseqs2_gpu.sh` (1TB 디스크, 24~48h). 이후 commercial 빌드 진짜 가능.
3. **Boltz-2 affinity head 실런** — BACE1 9개 compound로 `sampling_steps_affinity=200, diffusion_samples_affinity=5, affinity_mw_correction=true` 추론.
4. **TxGNN 가중치 다운로드 + 알츠하이머 re-purposing 실런** — `https://github.com/mims-harvard/TxGNN` 에서 체크포인트 받아 `MONDO_0004975` 기준 zero-shot top 20 후보 생성.
5. **AlphaFlow로 BACE1 cryptic pocket 탐색** — 50 컨포머 샘플 → P2Rank → apo에 없던 포켓 검출.
6. **DrugCLIP Stage A 실런** — COCONUT 2.0 700k → 1k 프리필터 검증.
7. **ADMET-AI v2 + OpenMM-ML 10 ns** — 상위 20 후보에 대해 BBB/hERG/DILI 게이트 + MACE-OFF24 안정성.

### 🟢 상위 로드맵 (참고)
- 다음 질병 적용: **NSCLC 또는 파킨슨 권고** (BACE1은 임상적으로 막혀있음).
- ABFE (Stage 8.5) 본격 검증 — FEP-SPell-ABFE로 top 10에 대해 160 ns/replica × 3 replicas.
- IP 타임스탬프 + DVC 추적 본격 활성 (commercial 빌드 감사).

### 기술 노트 (v2.1 ultrathink 추가분)
- **`no_kernels: false`가 기본** — `cuequivariance-torch>=0.7` 필요. 미설치 환경은 yaml override로 `no_kernels=true`.
- **MSA factory** — commercial 빌드에서는 `colabfold_public` 요청해도 `mmseqs2_local`로 강제 전환.
- **NeuralPLexer3 웨이트 CC-BY-NC-SA** → `conf/structure/neuralplexer3.yaml`이 `build_profile: research` 자동 — commercial에서 호출 시 LicenseViolation.
- **분자글루** (`molglue_jtvae`)은 학습 데이터 NC 가능성 때문에 안전 기본 research-only.
- **pmx**는 GPL-3 — 서브프로세스 격리 + research 한정. `fep_spell_abfe` (MIT)를 commercial 기본으로.

### 새 대화를 시작하는 Claude에게
사용자에게 어느 단계부터 갈지 먼저 확인하고 진행할 것.
**우선순위 권고**: 1 (가속 설치) → 3 (affinity 실런) → 4 (TxGNN 신가치) → 2 (MMseqs2 상업화).

---

## 프로젝트 한 줄 요약
AlphaFold 시대의 **신약 · 한약(생약) 후보물질 발굴 파이프라인**. **상업 제품화 전제**로 설계.

## 🏢 상업화 원칙 (Commercial Mode)

본 프로젝트는 **상용 출시 예정**. 빌드 프로파일이 이분법적이다.

| 프로파일 | 용도 | 허용 라이선스 |
|---|---|---|
| `research` | 내부 탐색·검증 | 모든 오픈 (CC-BY-NC · Gemma · 학술용 포함) |
| `commercial` | 외부 출시 빌드 | **Apache-2.0 · MIT · BSD · CC0 · CC-BY만** |

### 상업 빌드 허용 (확인 완료)
- 구조: Boltz-2 (MIT), Protenix v2 (Apache-2.0), ESMFold (MIT 버전)
- 도킹/생성: DiffDock-L (MIT), GNINA (Apache-2.0), REINVENT 4 (Apache-2.0), DiffSBDD (MIT), TargetDiff (MIT), RFdiffusion (BSD-3)
- ADMET: ADMET-AI (MIT), Chemprop 2.0 (MIT), Uni-Mol2 (MIT), MolFormer-XL (Apache-2.0)
- 화학 DB: COCONUT 2.0 (CC0), LOTUS (CC0), PubChem (Public domain), ZINC (무료 상용)
- 바이오 DB: Open Targets (CC-0), UniProt/SwissProt (CC BY 4.0), AlphaFold DB 구조 (CC BY 4.0), PrimeKG (MIT), Reactome (CC BY 4.0), WikiPathways (CC0)
- 런타임: RDKit (BSD-3), OpenMM (MIT), Hydra (MIT), Prefect (Apache-2.0), MLflow (Apache-2.0)
- ⚠️ ChEMBL 35 (CC BY-SA 3.0) — **share-alike** 주의. 파생 데이터 공개 시 동일 라이선스.

### 상업 빌드 제외 (research 전용)
- ❌ AlphaFold 3 공식 웨이트 (비상업)
- ❌ Chai-1/Chai-2 웨이트 (비상업)
- ❌ HERB 2.0 (CC-BY-NC)
- ❌ TCMSP 데이터 덤프 (학술 전용)
- ❌ BATMAN-TCM, SymMap, ETCM, TCMID, KTKP (학술 전용)
- ⚠️ TxGemma / Gemma (상업 가능하나 조건 있음, 법무 검토)
- ⚠️ ESM-3 Cambrian (매출 임계치 이하만 자유, 초과 시 라이선스 필요)
- ⚠️ KEGG (상용 유료) → **Reactome + WikiPathways로 대체** (기본 파이프라인)
- ⚠️ ColabFold 공용 MSA 서버 (학술용) → 상용은 **자체 MMseqs2 인스턴스**

### 한약 처리 원칙 (상업 vs 연구)
- 네트워크 약리학 **분석은 research 프로파일에서** HERB/TCMSP/KTKP 활용해 수행.
- 도출된 "후보 화합물 SMILES 자체"는 자연물이므로 **상업 빌드로 이식 가능** (데이터가 아니라 발견물을 사용).
- 단, 출시물에서 "HERB/TCMSP 데이터 기반"이라는 마케팅 문구 사용 금지 (라이선스 귀속 문제).

### 상업화 부속 요구
1. **자체 MSA 인프라**: MMseqs2 (BSD-2, 상용 OK) 자체 호스팅. ColabFold 공용 서버 의존 제거.
2. **감사 추적**: MLflow run_id + DVC data hash + 모델 체크포인트 SHA 자동 기록.
3. **IP 타임스탬프**: de novo 생성 분자는 생성 일시·시드·모델 해시 영구 기록 (특허 우선일).
4. **신뢰성 태그**: 예측마다 `confidence`, `license_tag`, `data_provenance`.
5. **규제 친화도**: 한국 출시 시 KHP/KP 수록 한약재 우선 가중치.
6. **개인정보**: 환자 데이터 결합 시 개인정보보호법 + GDPR + HIPAA. 현재는 환자 데이터 비포함 전제.

## 실행 환경 (절대 규칙)
- **진짜 저장소**: WSL2 ext4 `/home/crazat/genesis_medicine/`
  - Windows `C:\Projects\Genesis_Medicine\`는 과거 호환. **새 파일 쓰지 말 것**.
- **Python**: 3.11, `uv` 관리.
- **GPU**: CUDA 12.6 (호스트 드라이버 → WSL 자동 전달).
- **쉘**: bash (WSL Ubuntu 22.04).

## 기본 명령

```bash
cd ~/genesis_medicine
uv venv --python 3.11 && source .venv/bin/activate
uv pip install -e ".[dev]"

# 상업 빌드 (기본, 라이선스 게이트 필수 통과)
pytest tests/test_license_gate.py
python -m genesis_medicine.cli run build_profile=commercial disease=alzheimer

# 연구 빌드 (내부 탐색)
python -m genesis_medicine.cli run build_profile=research disease=alzheimer library=herb_tcm_full
```

## 디렉터리 지도
```
~/genesis_medicine/
├── CLAUDE.md                       # 이 파일 (세션 자동 로드)
├── README.md · pyproject.toml
├── conf/                           # Hydra
│   ├── build_profile/              # commercial.yaml / research.yaml  ★ M0.5
│   ├── disease/ structure/ library/ screening/ generation/ admet/ herbal/
├── src/genesis_medicine/
│   ├── structure/                  # Boltz-2 + Protenix v2 + OpenFold3 + AFDB 어댑터
│   ├── screening/                  # 6단계 캐스케이드: DrugCLIP→Uni-Mol2→FlowDock→Boltz-2→GNINA→PoseBusters + ECR
│   ├── generation/                 # FlowMol3 + DecompDiff + REINVENT 4 + SATURN/AiZynthFinder 합성 검증
│   ├── io/ ligand/ admet/ herbal/ md/ utils/
│   └── licensing/                  # 게이트·provenance (76 테스트 통과)
├── pipelines/full_pipeline.py      # Prefect 3 DAG
├── docker/
├── tests/
│   ├── unit/ integration/
│   └── test_license_gate.py        # ★ CI 블로커
└── docs/
    ├── ARCHITECTURE.md · CODE_REVIEW.md · INSTALL_WINDOWS.md
    └── LICENSING.md                # ★ 상업화 라이선스 매트릭스
```

## 기술 스택 요약 (v2.1)
- **구조 예측**: Boltz-2 (MIT) + Protenix v2 (Apache-2.0) + **OpenFold3 (Apache-2.0)** + **ConsensusPredictor** 앙상블. + **NeuralPLexer3** (research 한정, covalent ligand). AF3 웨이트 배제.
- **앙상블 (Stage 2.5)**: **AlphaFlow** + **BioEmu** conformational → cryptic pocket 검출.
- **타겟 발굴 + 재창출 (Stage 1 + 1.5)**: Open Targets + BERN2 + PrimeKG + **TxGNN zero-shot 약물 재창출** (17,080 질병).
- **스크리닝 6단계**: **DrugCLIP** 프리필터 → Uni-Mol2 임베딩 → **FlowDock** → Boltz-2 affinity head (MW 보정) → **GNINA 1.3** → **PoseBusters**. **ECR** 합의 + **PoseBench v2** 벤치마크 + **Active Learning Deep Docking**.
- **생성**: **FlowMol3** + **DecompDiff** + REINVENT 4 + **SATURN** + **AiZynthFinder**. **BindCraft** (단백질 바인더) + **PROTAC/분자글루** (Stage 5.5).
- **ADMET (Stage 6)**: **ADMET-AI v2** (Chemprop 2.0 기반, 41 endpoints). BBB/hERG/DILI/QED 게이트.
- **MD + ABFE (Stage 8' + 8.5)**: **OpenMM-ML + MACE-OFF24(M)** ML-MM refine → **FEP-SPell-ABFE** (MIT) 절대 결합자유에너지.
- **경로 DB**: KEGG 대신 **Reactome + WikiPathways**.
- **천연물 DB**: COCONUT 2.0 (CC0) + LOTUS (CC0) + **NPASS 3.0** + **NPAtlas 3.0** + **Dr. Duke** (USDA).
- **MSA 인프라**: 자체 호스팅 **MMseqs2-GPU** (1.65× 가속, 상업 OK). ColabFold 공용 서버는 research 한정.
- **가속**: **cuEquivariance v0.7** + **boltz-blackwell** (RTX 5090 Blackwell 전용).
- **오케스트레이션**: Hydra + Prefect 3 + MLflow + DVC.

## 파일럿
알츠하이머 · BACE1 (P56817). `proteins/AF-P56817-F1-model_v4.pdb` + `conf/disease/alzheimer.yaml`.

## 개발 규칙 (Claude 준수)
1. Windows 경로에 새 파일 쓰지 말 것.
2. 어댑터는 `structure/base.py`의 `StructurePredictor` Protocol 준수.
3. 설정 하드코딩 금지. 모든 파라미터는 `conf/*.yaml`.
4. 외부 API는 `io/` 캐시+재시도 경유.
5. 새 모델·데이터 추가 시 `docs/LICENSING.md` 매트릭스 등록 + `build_profile` 태그.
6. `test_license_gate.py` 실패 상태로 merge 금지.
7. 상용·비상용 코드/데이터 섞지 말 것 (어댑터 분리).

## 금지
- `.env`, API 키 commit 금지.
- AF3 공식 웨이트를 기본 경로에 넣지 말 것.
- HERB/TCMSP/KTKP 데이터를 `commercial` 프로파일에서 참조 금지.
- KTKP/MFDS 스크래핑 시 robots.txt · 약관 준수.

## 현재 상태 (2026-04-25)
- M0 부트스트랩 완료. `.venv` Python 3.11.15, Boltz-2 v2.2.1, RTX 5090 32GB.
- M0.5 **라이선스 게이트** 완료 — **83개 컴포넌트** 등록, **118개 테스트** 전부 통과.
- M1 **Open Targets + BACE1 파일럿** 완료 — 9/10 화합물 공동접힘 성공 (confidence=0.873).
- **v2 고도화** 완료 — 6단계 스크리닝 캐스케이드 + ECR + FlowMol3/DecompDiff 생성 + SATURN 합성 검증.
- **v2.1 ultrathink 고도화** 완료 (2026-04-25) — **11단계 아키텍처** + 15개 새 어댑터:
  - TxGNN 약물 재창출 (Stage 1.5)
  - AlphaFlow/BioEmu conformational ensemble (Stage 2.5)
  - BindCraft 단백질 바인더 / PROTAC·분자글루 (Stage 5.5)
  - ADMET-AI v2 (Stage 6)
  - OpenMM-ML + MACE-OFF24 (Stage 8')
  - FEP-SPell-ABFE (Stage 8.5)
  - 자체 MMseqs2-GPU MSA (상업 빌드 블로커 해소)
  - PoseBench v2 검증 + Active Learning Deep Docking
  - Protenix/OpenFold3/Boltz-2 ConsensusPredictor
  - NeuralPLexer3 (research only, covalent ligand)
- M2~M9 어댑터 뼈대 + 설정 + 테스트 완비. 실 추론 런 단계만 남음.
