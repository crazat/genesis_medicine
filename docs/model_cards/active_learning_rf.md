# Model Card: active_learning_rf

- timestamp: `2026-05-06T12:46:35+09:00`
- component: `RandomForest active-learning surrogate`
- context_of_use: `next cofold/docking candidate acquisition`
- decision_influence: `medium`
- decision_consequence: `low`
- risk_tier: `tier1`
- validation_status: `local scaffold-domain gate and leave-one-out MAE`
- uncertainty_controls: `tree ensemble variance, applicability-domain gate`
- allowed_claim: `queue selection heuristic only`

## Required Controls

- Record input/output file paths in `docs/RUN_PROVENANCE_MANIFEST.md`.
- Do not use this component as standalone evidence for clinical or wet-lab efficacy.
- If output conflicts with orthogonal evidence, downgrade manuscript claim strength.
