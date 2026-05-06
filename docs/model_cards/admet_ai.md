# Model Card: admet_ai

- timestamp: `2026-05-06T12:46:35+09:00`
- component: `ADMET-AI predictors`
- context_of_use: `AMES/hERG/DILI/skin reaction prefiltering`
- decision_influence: `medium`
- decision_consequence: `medium`
- risk_tier: `tier2`
- validation_status: `external model; no local wet-lab validation yet`
- uncertainty_controls: `orthogonal counterscreen and dermal regulatory gate`
- allowed_claim: `predicted safety risk only`

## Required Controls

- Record input/output file paths in `docs/RUN_PROVENANCE_MANIFEST.md`.
- Do not use this component as standalone evidence for clinical or wet-lab efficacy.
- If output conflicts with orthogonal evidence, downgrade manuscript claim strength.
