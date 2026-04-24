# 기존 Genesis_Medicine 코드 검수 (2026-04)

작성: Claude (Opus 4.7)

## 1. 전체 구조 문제

```
Genesis_Medicine/
├── 01_data_acquisition.ipynb   # PubMed abstract 수집
├── Dockerfile                  # CUDA 12.6 + Python 3.11
├── requirements.txt            # torch 2.6 + transformers + torch-geometric
├── proteins/
│   └── AF-P56817-F1-model_v4.pdb  # BACE1 단일 PDB (수동 다운)
└── scripts/
    ├── fetch_abstracts.py      # PubMed 검색
    ├── run_ner.py              # NER 샘플 1줄
    ├── run_ner_abstracts.py    # NER batch
    ├── find_protein_targets.py # 타겟 후보 선정
    └── analyze_results.py      # (내용 확인 실패)
```

**근본 문제**: 노트북·스크립트 간 연결 없음, 설정 하드코딩, 단계별 산출물이 "문자열 리포트"에서 끝나며 실제 파이프라인 없음.

## 2. 단계별 결함

### 2.1 `fetch_abstracts.py`
- `retmax=20000`을 한 번의 `efetch`에 전달 → NCBI는 실질적으로 **최대 10000건**만 반환. 결과 로그에 9999건만 잡힌 이유. **batch 분할 필수** (200~500건씩, `retstart` 사용).
- 출력 파일명이 **`nsclc_abstracts.csv`**인데 쿼리는 알츠하이머 → 템플릿 복사 잔재. 잘못된 파일명으로 저장되어 이후 단계에서 혼란.
- Entrez `tool`, `api_key` 파라미터 미설정 → rate limit 3 req/s로 제한.
- 단일 실행, 재시도/체크포인트 없음.

### 2.2 `run_ner.py`
- 한 문장 하드코딩 테스트. 폐기 대상.

### 2.3 `run_ner_abstracts.py`
- 모델 `d4data/biomedical-ner-all` (2022년 학습, DistilBERT 기반) — **성능 구세대**. 2025+ 에는 **BERN2**, **GliNER-BioMed**, **PubMedBERT-NER**, 또는 **BioBERT-v1.2** 파인튜닝이 SOTA.
- `aggregation_strategy="simple"` + 임계값 없음 → score 0.3짜리 노이즈도 통과.
- `device=0` 하드코딩 → GPU 없을 때 크래시.
- `all_entities = ner_pipeline(hf_dataset['abstract'], batch_size=64)`는 **전체 메모리에 로드**. 45 MB CSV는 ok지만 확장성 없음. `Dataset.map()` 또는 `iterator` 사용해야 함.
- NumPy float → Python float 변환 로직은 필요하긴 하나, `json.dumps(default=str)`로 훨씬 간결하게 처리 가능.

### 2.4 `find_protein_targets.py` — **가장 문제 많은 코드**
- **유전자 매칭이 단순 어휘 교집합**: `words.intersection(gene_list)` → HGNC 심볼 중 일상 영어 단어와 겹치는 것이 수십 개 (`SET`, `CAT`, `HR`, `IMPACT`, `ACE`, `APP`, `MAP`, `STAR` 등). **대량 오탐**.
- HGNC URL 경로 `storage.googleapis.com/public-download-files/hgnc/...` — **2024년경 URL 변경됨**. `https://ftp.ebi.ac.uk/pub/databases/genenames/hgnc/tsv/hgnc_complete_set.txt`가 안정적.
- `line.split('\t')[1]` → HGNC TSV 컬럼 순서 변경 시 silent failure. `pandas.read_csv(sep='\t')` + 컬럼명 지정이 안전.
- 'hippocampus' 문자열 매칭에 의존 — NER entity_group 필터링 후 `word` 필드를 lowercase stripping 없이 검사. 실제 `word`는 sub-token일 수 있음 (`"hippocam"`, `"##pus"`).
- **약물 가능성(druggability) 검증 전혀 없음**: 단순 언급 빈도 = 타겟 가치 아님.
- **AlphaFold 연동이 print문 "안내 메시지"로 끝남**. 실제 호출/다운로드/구조 분석 없음.
- **포켓 탐색·도킹·스코어링 없음**. 이 스크립트가 "단백질 예측 프로그램"으로 보이게 하는 원인.

### 2.5 `Dockerfile`
- `apt-get install python3-pip` → Ubuntu 22.04의 pip는 **Python 3.10용**으로 연결됨. `python3.11 -m pip`로 명시해야 3.11 환경에 설치됨 (일부 패키지가 3.10에 설치되는 버그 가능).
- `pip install -r requirements.txt`가 torch 2.6 CPU wheel을 받을 가능성 — CUDA용 인덱스(`--index-url https://download.pytorch.org/whl/cu126`) 미지정.
- 과학 계산 기본 패키지 (rdkit, openmm, biopython) 미설치.
- root 사용, non-root user 없음.
- 캐시 레이어 최적화 안 됨.

### 2.6 `requirements.txt`
- `torch==2.6.0` 고정 → 2026-04 기준 PyTorch 2.7/2.8 가용. 단, Boltz/Protenix 요구사항에 맞춰 고정이 필요하므로 **각 서브시스템별로 lock file 분리** 권장.
- `biopython` 있음 ✓, `transformers` 있음 ✓, `torch-geometric` 있음 ✓
- **누락**: rdkit, openmm, py3dmol, mdanalysis, prody, requests_cache, pyyaml, hydra-core, mlflow, dvc, loguru
- 버전 pinning 부족 → 재현성 없음.

### 2.7 노트북 `01_data_acquisition.ipynb`
- 스크립트와 100% 중복 (동일 함수). 한 쪽만 유지 권장. 탐색은 노트북, 운영은 CLI 스크립트 원칙.

## 3. 설계 차원 누락

| 영역 | 현재 | 필요 |
|---|---|---|
| 목표 질병 정의 | 하드코딩 (알츠하이머) | 설정 파일 기반 (질병→MeSH→MoA 매핑) |
| 타겟 발굴 | 키워드 빈도 | 지식그래프 + 문헌 + druggability |
| 구조 예측 | 수동 PDB 1개 | 자동 AlphaFold DB 쿼리 + Boltz-2 로컬 추론 |
| 포켓 탐색 | 없음 | FPocket / DoGSiteScorer |
| 리간드 라이브러리 | 없음 | ChEMBL + COCONUT + 한약 DB |
| 도킹 | 없음 | Boltz-2 co-folding + GNINA 재스코어링 |
| ADMET 필터 | 없음 | ADMET-AI + Lipinski + BBB |
| 생성 모델 | 없음 | REINVENT 4 / TargetDiff |
| 보고서 | print() | HTML / MLflow / 인터랙티브 대시보드 |
| 재현성 | 없음 | Hydra config + DVC + 시드 고정 |
| 테스트 | 없음 | pytest + small synthetic fixture |

## 4. 보존할 가치

- PubMed 수집 아이디어 ✓ (파이프라인화 필요)
- NER 기반 타겟 탐색 접근 ✓ (모델·검증 업그레이드 필요)
- BACE1 (P56817) PDB 파일 — 알츠하이머 파일럿 대상으로 그대로 활용
- Alzheimer abstracts 9999건 → **재수집·전처리해서 RAG용 지식 베이스**로 재활용 가능
- Dockerfile + CUDA 베이스 → 전면 개편하되 컨테이너 접근 유지

## 5. 결론

기존 코드는 **프로토타입 탐색 단계의 스케치**로 평가. "단백질 예측 프로그램"을 표방하기엔 실제 구조예측·도킹·스코어링이 전무하고, 타겟 선정도 어휘 교집합이라 오탐이 심함. 재사용보다는 **재설계가 효율적**. 단, 질병 데이터 수집·NER 파이프라인은 교체하여 `targets/` 모듈로 살림.
