# Wet-lab Feedback Schema

- timestamp: `2026-05-06T12:46:31+09:00`
- feedback_template: `data/wetlab_feedback_template.csv`
- endpoint_priority: `pilot/cpu_meaningful/wetlab_endpoint_priority.csv`
- purpose: 계산 루프가 wet-lab 결과를 구조적으로 다시 받아 다음 큐잉을 판단하게 만든다.

## Required Columns

| column | purpose |
|---|---|
| experiment_id | raw wet-lab metadata 또는 분석값 |
| date | raw wet-lab metadata 또는 분석값 |
| compound_id | R15/R16/NPASS 등 계산 ID와 연결한다. |
| smiles | 동일성, salt/tautomer 확인, novelty 재계산에 쓴다. |
| target_or_pathway | TGFB1, TYR, DCT처럼 계산 target 또는 phenotype pathway. |
| disease_context | raw wet-lab metadata 또는 분석값 |
| assay_type | qPCR, enzyme, cell viability, melanin content 등. |
| cell_type_or_model | raw wet-lab metadata 또는 분석값 |
| endpoint | COL1A1, ACTA2, melanin, IC50, viability 등. |
| value | raw wet-lab metadata 또는 분석값 |
| unit | raw wet-lab metadata 또는 분석값 |
| dose | raw wet-lab metadata 또는 분석값 |
| dose_unit | raw wet-lab metadata 또는 분석값 |
| timepoint | raw wet-lab metadata 또는 분석값 |
| replicates | raw wet-lab metadata 또는 분석값 |
| control | raw wet-lab metadata 또는 분석값 |
| vendor_or_lab | raw wet-lab metadata 또는 분석값 |
| raw_file | raw wet-lab metadata 또는 분석값 |
| quality_flag | pass, review, fail 중 하나로 curator가 후속 큐를 결정한다. |
| interpretation | promote, hold, deprioritize 중 하나를 권장한다. |
| notes | raw wet-lab metadata 또는 분석값 |

## Endpoint Priority

| priority | context | recommended assay | decision rule |
|---:|---|---|---|
| 1 | scar/fibrosis topical lead | fibroblast TGF-beta induced COL1A1/ACTA2 qPCR + viability | lead only if anti-fibrotic signal appears below cytotoxic concentration |
| 2 | pigmentation topical lead | B16F10 or human melanocyte melanin content + tyrosinase activity | lead only if pigment endpoint changes without broad toxicity |
| 3 | systemic-safety chromanol fragment | commercial safety panel or orthogonal ADMET counterscreen | systemic path only if wet-lab safety remains clean |
| 4 | NPASS atlas candidates | single-concentration cellular phenotypic triage before more GPU | promote only candidates with phenotype signal and acceptable solubility |

## Curator Use

- 새 wet-lab row가 들어오면 `quality_flag`와 `interpretation`을 기준으로 GPU/CPU 후속 큐를 승격한다.
- wet-lab 음성 결과도 methodology/failure-mode paper의 근거로 보존한다.
