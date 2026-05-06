# Model Card: codex_curator_loop

- timestamp: `2026-05-06T12:46:35+09:00`
- component: `Codex autonomous curator`
- context_of_use: `compute queueing, paper queueing, and decision documentation`
- decision_influence: `high`
- decision_consequence: `medium`
- risk_tier: `tier2`
- validation_status: `human-supervised automation; logs/provenance required`
- uncertainty_controls: `protected PID rules, no duplicate outputs, provenance manifest, action log`
- allowed_claim: `automation workflow support only`

## Required Controls

- Record input/output file paths in `docs/RUN_PROVENANCE_MANIFEST.md`.
- Do not use this component as standalone evidence for clinical or wet-lab efficacy.
- If output conflicts with orthogonal evidence, downgrade manuscript claim strength.
