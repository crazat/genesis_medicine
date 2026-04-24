# Genesis_Medicine v2

> AlphaFold 시대의 신약 & 한약(생약) 후보물질 발굴 파이프라인

## 한 줄 요약
질병 이름만 주면 — **타겟 발굴 → 단백질 구조 예측 → 리간드 라이브러리(합성 분자 + 천연물 + 한약 성분) 다단계 가상 스크리닝 → 친화도·ADMET·한약 역매핑 → 리포트**까지 연결되는 end-to-end 파이프라인.

## 왜 재설계했나 (v1 → v2)
| 영역 | v1 (2025-07) | v2 (2026-04) |
|---|---|---|
| 구조 예측 | 수동 PDB 1개 (BACE1) | **Protenix v2** (Apache-2.0, AF3 능가) + **Boltz-2** (MIT, FEP 1000× 속도) |
| 타겟 발굴 | HGNC 어휘 교집합 (오탐 심함) | **Open Targets GraphQL** + **BERN2 NER** + **PrimeKG** |
| 도킹 | 없음 | **DiffDock-L** + **GNINA 1.3** + **Boltz-2 공동접힘** |
| 생성 모델 | 없음 | **DiffSBDD** + **REINVENT 4** + **TxGemma** |
| ADMET | 없음 | **ADMET-AI** (41 TDC 엔드포인트) |
| 한약 | 없음 | **COCONUT 2.0** + **HERB** + **TCMSP** + **KTKP** + **BATMAN-TCM 2.0** |
| 오케스트레이션 | 단발 스크립트 | **Hydra** 설정 + **Prefect 3** DAG + **MLflow** |

## 빠른 시작

```bash
# 1) WSL2 + Docker Desktop (docs/INSTALL_WINDOWS.md 참조)
git clone <이 저장소>
cd Genesis_Medicine

# 2) 로컬 venv
uv venv --python 3.11 && source .venv/bin/activate
uv pip install -e ".[dev]"

# 3) 알츠하이머 파일럿 (타겟 발굴까지만)
python -m genesis_medicine.cli run disease=alzheimer structure=boltz2

# 4) 한약 집중 모드
python -m genesis_medicine.cli run disease=alzheimer library=herb_tcm
```

## 문서

- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — 전체 설계 · 9단계 파이프라인 · 기술 스택 · 마일스톤
- [docs/CODE_REVIEW.md](docs/CODE_REVIEW.md) — v1 코드 검수 (보존할 것 vs 버릴 것)
- [docs/INSTALL_WINDOWS.md](docs/INSTALL_WINDOWS.md) — WSL2 + CUDA 12 설치
- [conf/](conf/) — Hydra 설정 (질병·엔진·라이브러리 선택 가능)

## 법적·규제 주의
- **AlphaFold 3 공식 웨이트**는 비상업 전용. 본 프로젝트는 기본 경로에서 사용하지 않음.
- **HERB CC-BY-NC** 데이터는 내부 연구용. 상업화 단계에선 COCONUT/LOTUS (CC0)로 한정.
- 본 도구는 **연구 보조 수단**이며 임상·규제 판단을 대체하지 않음. 한국 식약처 IND 진입 시 KHP/KP 수록 여부 등 별도 확인 필요.

## 라이선스
Apache-2.0 (코드). 데이터는 각 소스 라이선스 준수.
