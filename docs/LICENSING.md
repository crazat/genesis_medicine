# 라이선스 매트릭스 — 상업화 가이드

> 2026-04 기준. 새 의존성 추가 시 이 표를 먼저 업데이트하고 `src/genesis_medicine/licensing/registry.py`에 등록한다.

## 분류 규칙

| 태그 | 허용 프로파일 | 설명 |
|---|---|---|
| `commercial-safe` | research + commercial | Apache-2.0 · MIT · BSD · CC0 · CC-BY (귀속 필요) |
| `commercial-share-alike` | research + commercial (+ 파생물 공개 의무) | CC BY-SA 등 |
| `commercial-conditional` | research + commercial (단, 조건 충족 시) | Gemma, Cambrian 등 사용·매출 임계 |
| `research-only` | research | CC-BY-NC, 학술 전용, 비상업 표기 |
| `blocked` | 어느 쪽도 불가 | 회사 정책상 사용 금지 |

## 모델 (ML)

| 이름 | 버전 | 라이선스 | 태그 | 근거 URL |
|---|---|---|---|---|
| AlphaFold 3 | 2024-11 | 코드 Apache-2.0 / **웨이트 비상업** | research-only | github.com/google-deepmind/alphafold3/blob/main/WEIGHTS_TERMS_OF_USE.md |
| Protenix | v2 (2026-04-08) | Apache-2.0 (코드+웨이트) | commercial-safe | github.com/bytedance/Protenix |
| Boltz-1 / Boltz-2 | 2.0 | MIT (코드+웨이트) | commercial-safe | github.com/jwohlwend/boltz |
| Chai-1 / Chai-2 | 2025 | 코드 Apache-2.0 / **웨이트 비상업** | research-only | github.com/chaidiscovery/chai-lab |
| HelixFold3 | 2024 | Apache-2.0 | commercial-safe | github.com/PaddlePaddle/PaddleHelix |
| OpenFold2 | 2025 | Apache-2.0 | commercial-safe | github.com/aqlaboratory/openfold |
| ESMFold (ESM-2) | 2023 | MIT | commercial-safe | github.com/facebookresearch/esm |
| ESM-3 (Cambrian) | 2024+ | Cambrian (매출 임계) | commercial-conditional | evolutionaryscale.ai |
| RoseTTAFold All-Atom | 2024 | 주로 BSD, 일부 웨이트 NC | research-only (안전 기본) | github.com/baker-laboratory/RoseTTAFold-All-Atom |
| DiffDock-L | 2023 | MIT | commercial-safe | github.com/gcorso/DiffDock |
| NeuralPLexer-2 | 2024 | Apache-2.0 | commercial-safe | github.com/zrqiao/NeuralPLexer |
| GNINA | 1.3 | Apache-2.0 | commercial-safe | github.com/gnina/gnina |
| AutoDock Vina | 1.2 | Apache-2.0 | commercial-safe | github.com/ccsb-scripps/AutoDock-Vina |
| REINVENT 4 | 2024+ | Apache-2.0 | commercial-safe | github.com/MolecularAI/REINVENT4 |
| DiffSBDD | 2023 | MIT | commercial-safe | github.com/arneschneuing/DiffSBDD |
| TargetDiff | 2023 | MIT | commercial-safe | github.com/guanjq/targetdiff |
| Pocket2Mol | 2022 | MIT | commercial-safe | github.com/pengxingang/Pocket2Mol |
| RFdiffusion | 2023+ | BSD-3 변형 | commercial-safe | github.com/RosettaCommons/RFdiffusion |
| TxGemma | 2024 | Gemma (조건부) | commercial-conditional | huggingface.co/google/txgemma |
| BioMedGPT-LM | 2023 | MIT | commercial-safe | github.com/PharMolix/OpenBioMed |
| ADMET-AI | 2024 | MIT | commercial-safe | github.com/swansonk14/admet_ai |
| Chemprop | 2.0 | MIT | commercial-safe | github.com/chemprop/chemprop |
| MolFormer-XL | 2022 | Apache-2.0 | commercial-safe | github.com/IBM/molformer |
| Uni-Mol2 / Uni-Mol Docking V2 | 2024 | MIT | commercial-safe | github.com/deepmodeling/Uni-Mol |
| BERN2 | 2022 | BSD-2 | commercial-safe | github.com/dmis-lab/BERN2 |
| GliNER-BioMed | 2024 | Apache-2.0 | commercial-safe | github.com/urchade/GLiNER |
| PubMedBERT / BioBERT | — | MIT / Apache-2.0 | commercial-safe | — |
| BioGPT | 2022 | MIT | commercial-safe | github.com/microsoft/BioGPT |

## 데이터 소스

| 이름 | 라이선스 | 태그 | 비고 |
|---|---|---|---|
| PubMed / PubMedCentral | Public domain (대부분) | commercial-safe | 일부 저작권 abstract는 제외 필요 |
| UniProt / SwissProt | CC BY 4.0 | commercial-safe | 귀속 표기 |
| AlphaFold DB 구조 | CC BY 4.0 | commercial-safe | 귀속 표기 |
| Open Targets Platform | CC0 | commercial-safe | |
| PrimeKG | MIT + 원 소스 귀속 | commercial-safe | 결합 DB 귀속 체인 주의 |
| Hetionet | CC0 | commercial-safe | |
| PubChem | Public domain | commercial-safe | |
| ChEMBL 35 | CC BY-SA 3.0 | commercial-share-alike | 파생 공개 시 동일 라이선스 |
| ZINC22 | 무료 상용 허용 | commercial-safe | 귀속 |
| Enamine REAL | 상업 라이선스 필요 | blocked (기본), 계약 시 해제 | |
| COCONUT 2.0 | CC0 | commercial-safe | |
| LOTUS | CC0 | commercial-safe | |
| Super Natural III | 학술 | research-only | |
| NPASS v2.0 | 학술 | research-only | |
| CMAUP v2 | 학술 | research-only | |
| HERB 2.0 | CC-BY-NC | research-only | |
| TCMSP | 학술 전용 표기 | research-only | |
| TCMID | 학술, 간헐적 오프라인 | research-only | |
| BATMAN-TCM 2.0 | 학술 | research-only | |
| SymMap v2 | 학술 | research-only | |
| ETCM v2.0 | 학술 | research-only | |
| KTKP (koreantk.com) | 한국 정부저작물 (CC BY 2.0 KR 추정, 확인 필요) | research-only (안전 기본) | 공식 허가 시 commercial-conditional |
| Dr. Duke's DB | Public domain (USDA) | commercial-safe | |
| KEGG | 유료 상업 라이선스 필요 | research-only (기본), 유료 계약 시 해제 | |
| Reactome | CC BY 4.0 | commercial-safe | KEGG 대체 |
| WikiPathways | CC0 | commercial-safe | KEGG 대체 |
| KHP (Korean Herbal Pharmacopoeia) | 정부 저작물 (MFDS) | commercial-safe (참조용) | PDF 파싱 허용 여부 재확인 권장 |

## 런타임·도구

| 이름 | 라이선스 | 태그 |
|---|---|---|
| RDKit | BSD-3 | commercial-safe |
| OpenMM | MIT | commercial-safe |
| MDAnalysis | GPL-2 | 주의: 코드 결합 제약 → 서브프로세스 경계로 격리 |
| Hydra | MIT | commercial-safe |
| Prefect 3 | Apache-2.0 | commercial-safe |
| MLflow | Apache-2.0 | commercial-safe |
| DVC | Apache-2.0 | commercial-safe |
| Biopython | Biopython License (BSD-유사) | commercial-safe |
| HMMER | BSD-3 | commercial-safe |
| MMseqs2 | BSD-2 | commercial-safe |
| ColabFold (코드) | MIT | commercial-safe |
| ColabFold **공용 MSA 서버** | 학술 | research-only. 상용은 자체 서버 구축 |

## 규제 · 지식재산 체크리스트

- [ ] 상업 빌드 CI에서 `test_license_gate.py` 블로커 활성
- [ ] 모든 모델·데이터 사용처에 `license_tag` 메타데이터 태깅
- [ ] 자체 MSA 서버(MMseqs2) 운영 구축 (ColabFold 공용 서버 의존 제거)
- [ ] de novo 생성 분자의 타임스탬프·시드·모델체크포인트 해시 영구 저장 (특허 우선일)
- [ ] ChEMBL 35 기반 파생 데이터셋 공개 정책 결정 (CC BY-SA 3.0 전파)
- [ ] TxGemma, ESM-3 사용 여부에 따른 법무 검토
- [ ] KEGG 경로 의존 제거 → Reactome/WikiPathways 이관 완료 확인
- [ ] KTKP/MFDS 데이터 상업 사용 허가 취득 여부 기록
- [ ] 환자/임상 데이터 결합 전 개인정보보호법·GDPR·HIPAA 준수 설계
