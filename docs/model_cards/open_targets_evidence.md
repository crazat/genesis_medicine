# Model Card: open_targets_evidence

- timestamp: `2026-05-06T12:46:35+09:00`
- component: `Open Targets / evidence gates`
- context_of_use: `target prioritization and claim strength limitation`
- decision_influence: `high`
- decision_consequence: `medium`
- risk_tier: `tier2`
- validation_status: `API-derived evidence with manual biological interpretation`
- uncertainty_controls: `green/yellow/red gate and disease-context notes`
- allowed_claim: `target evidence support only`

## Required Controls

- Record input/output file paths in `docs/RUN_PROVENANCE_MANIFEST.md`.
- Do not use this component as standalone evidence for clinical or wet-lab efficacy.
- If output conflicts with orthogonal evidence, downgrade manuscript claim strength.
