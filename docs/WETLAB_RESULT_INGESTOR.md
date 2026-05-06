# Wet-lab Result Ingestor

- timestamp: `2026-05-06T12:46:35+09:00`
- status: `no_wetlab_results_yet`
- source_file: `data/wetlab_feedback_results.csv`
- result_template: `data/wetlab_feedback_results_template.csv`
- ingested_csv: `pilot/cpu_meaningful/wetlab_feedback_ingested.csv`
- decision_csv: `pilot/cpu_meaningful/wetlab_queue_decisions.csv`
- purpose: CRO/in-house assay 결과가 들어오면 quality/interpretation 기반으로 다음 compute 또는 논문 근거를 자동 분기한다.

## Decision Rules

| input | queue action |
|---|---|
| `quality_flag=pass` and `interpretation=promote` | BO/active-learning update and next fidelity promotion |
| `quality_flag=fail` or `interpretation=deprioritize` | duplicate compute block and negative evidence preservation |
| otherwise | repeat/QC hold before escalation |

## Curator Rule

- `data/wetlab_feedback_results.csv`가 생기면 이 ingestor를 먼저 실행하고, promote row만 후속 GPU/CPU 큐로 승격한다.
- template 파일은 예시용이다. 실제 결과는 `data/wetlab_feedback_results.csv`에 별도 저장한다.
