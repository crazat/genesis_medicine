# Model Card: openmm_md

- timestamp: `2026-05-06T12:46:35+09:00`
- component: `OpenMM molecular dynamics`
- context_of_use: `pose stability and drift/failure-mode assessment`
- decision_influence: `high`
- decision_consequence: `medium`
- risk_tier: `tier2`
- validation_status: `trajectory RMSD summaries; force-field and timescale caveats remain`
- uncertainty_controls: `replicate/extension MD, last-third RMSD, drift caveat`
- allowed_claim: `short-timescale stability support only`

## Required Controls

- Record input/output file paths in `docs/RUN_PROVENANCE_MANIFEST.md`.
- Do not use this component as standalone evidence for clinical or wet-lab efficacy.
- If output conflicts with orthogonal evidence, downgrade manuscript claim strength.
