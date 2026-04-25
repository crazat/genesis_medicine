# 사용자 등록이 필요한 외부 서비스 (8개)

> Genesis_Medicine v3 — 모든 자동 기능이 풀로 동작하려면 다음 API key들이 필요합니다.
> 모두 **무료**이며 등록 후 환경변수로 설정하면 자동 활용됩니다.

---

## 📋 우선순위별 정리

### 🔴 필수 (사용자 등록 권장 — paper 작성에 직접 영향)

#### 1. NCBI PubMed E-utilities API key ✅ 등록 완료 (2026-04-25)
- **목적**: PubMed 검색 rate limit 완화 (3 req/s → 10 req/s)
- **신청**: <https://www.ncbi.nlm.nih.gov/account/settings/> → "API Key Management"
- **소요**: 1분
- **설정**: 프로젝트 루트 `.env` (gitignore됨)
  ```
  NCBI_API_KEY=<redacted — see local .env>
  NCBI_EMAIL=<your-email>
  ```
- **검증**: `EGCG × hypertrophic scar` 라이브 호출 200 OK (PMIDs 41050098, 39068733, 36606405)
- **효과**: novelty 검증 + monitoring 약 3× 빠름. 자동 로드 — `genesis_medicine.novelty._ncbi_auth.ncbi_params()`.

#### 2. Semantic Scholar API key ✅ 등록 완료 (2026-04-25)
- **목적**: 광범위 학술 검색 (PubMed 외 conference, ArXiv 포함)
- **신청**: <https://www.semanticscholar.org/product/api> → "Request API Key" 양식
- **소요**: 폼 제출 → 1-3 영업일 이메일 회신
- **설정**: `.env` 의 `SEMANTIC_SCHOLAR_API_KEY=s2k-...`
- **검증**: `EGCG×scar×Boltz×MD 2024+` 쿼리 6 hits, 2026년 hypertrophic scar GWAS paper 즉시 식별
- **효과**: 1 req/sec sustained (anonymous 100 req/5min 대비). `genesis_medicine.monitoring.semantic_scholar.s2_headers()` 자동 첨부.

#### 3. NRF KCI Open API (한국 학술지)
- **목적**: 한방 paper 한국어 자동 검색 (시스템 novelty 핵심)
- **신청**: <https://www.kci.go.kr/kciportal/po/openapi/openApiList.kci>
  → "오픈 API 사용 신청" → IP 등록 + 사유 작성
- **소요**: 즉시 (자동 승인)
- **설정**:
  ```bash
  export KCI_API_KEY="your_key"
  ```
- **효과**: 한방·한국어 학술지 자동 카운트, 우리 시스템 novelty의 한국 측면 보강

---

### 🟡 권장 (paper 가치 강화)

#### 4. Lens.org API key (특허 검색)
- **목적**: 우리 hit 화합물에 대한 특허 자동 카운트
- **신청**: <https://www.lens.org/lens/user/subscriptions> → 무료 학술 계정
- **소요**: 5분 등록
- **설정**:
  ```bash
  export LENS_API_TOKEN="your_token"
  ```
- **효과**: novelty score의 patent 차원 자동 정확화 (현재 -1)

#### 5. REINVENT 4 prior 모델 (Zenodo)
- **목적**: Embelin/Curcumin scaffold hopping
- **다운로드**: <https://doi.org/10.5281/zenodo.15641296> (현재 일시적 500 에러,
  안정화 후 재시도)
- **소요**: 5-30분 (~1.5 GB)
- **저장 위치**: `external/REINVENT4/priors/`
- **필요한 파일**:
  - `mol2mol_medium_similarity.prior` (scaffold hopping 핵심)
  - `reinvent.prior` (de novo)
  - `libinvent.prior` (R-group)
- **효과**: 250 lead 후보 자동 생성 가능 (paper 1편 추가 가치)

---

### 🟢 선택 (장기 가치)

#### 6. DrugBank Open Data
- **목적**: 승인 약물 indication 자동 매핑 (재창출 검증)
- **신청**: <https://go.drugbank.com/releases/latest> → "Academic License" 신청
  (대학·연구소 필요)
- **소요**: 폼 제출 → 1-7일
- **저장 위치**: `data/drugbank/`
- **효과**: TxGNN 재창출 결과의 supplement 검증

#### 7. EBI ChEMBL 35 dump (선택)
- **목적**: 로컬 ChEMBL DB로 빠른 bioactivity 조회 (현재 API 사용 중)
- **다운로드**: <https://chembl.gitbook.io/chembl-interface-documentation/downloads>
- **크기**: 10+ GB
- **효과**: API 의존성 제거 + offline 가능

#### 8. MMseqs2-GPU + ColabFoldDB (장기)
- **목적**: 자체 호스팅 MSA (commercial 빌드 블로커 해소)
- **필요**: 1TB 디스크 + 24-48시간 빌드
- **스크립트**: `scripts/setup/install_mmseqs2_gpu.sh`
- **효과**: ColabFold 공용 서버 의존 제거 (commercial paper 출시 시 필수)

---

## 🔧 설정 일괄 적용

`~/.bashrc`에 다음 추가:

```bash
# Genesis_Medicine 외부 API
export NCBI_API_KEY="..."
export S2_API_KEY="..."
export KCI_API_KEY="..."
export LENS_API_TOKEN="..."

# (선택) 데이터 디렉터리 override
# export GENESIS_DATA="$HOME/genesis_medicine/data"
# export GENESIS_CACHE="$HOME/genesis_medicine/.cache"
```

이후 새 셸 또는 `source ~/.bashrc`.

## ✅ 등록 후 검증

```bash
cd ~/genesis_medicine
# 1. NCBI rate limit
.venv/bin/python -c "
import os; from genesis_medicine.novelty.pubmed_search import _esearch
r = _esearch('curcumin scar', retmax=2)
print('PubMed OK, n_hits =', r.get('count'))
"

# 2. Semantic Scholar
.venv/bin/python -c "
from genesis_medicine.monitoring import semantic_scholar_search
r = semantic_scholar_search('centella scar', limit=3)
print('S2 OK, total =', r.get('total'))
"

# 3. KCI (등록 완료 후)
.venv/bin/python -c "
from genesis_medicine.monitoring import kci_search
print(kci_search('한약 흉터'))
"
```

## 📅 우선순위 추천

**클리닉 8월 오픈 전까지 (~4개월):**
- 즉시 등록: 1. PubMed, 2. Semantic Scholar, 3. KCI (모두 무료, 등록 5-10분)
- 4월 중: 4. Lens.org (특허 검증)
- 6월 중: 5. REINVENT 4 prior 다운로드 (Zenodo 안정화 후)
- 8월 직전: 6. DrugBank Academic 신청 (대학 협력 시)
- 추후: 7-8 (장기 인프라)

이 가이드는 사용자가 직접 해야 하는 부분이며, 등록 완료되는 대로 시스템이 자동으로 활용합니다.
