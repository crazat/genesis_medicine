# Model Card: boltz2_cofold

- timestamp: `2026-05-06T12:46:35+09:00`
- component: `Boltz-2 cofold affinity/confidence`
- context_of_use: `protein-ligand cofold triage for skin target hypotheses`
- decision_influence: `high`
- decision_consequence: `medium`
- risk_tier: `tier2`
- validation_status: `local calibration and PoseBusters/MD cross-check required`
- uncertainty_controls: `confidence_score, ligand_iptm, replicate affinity heads, pose sanity gate`
- allowed_claim: `in silico prioritization only; no binding or efficacy claim`

## Required Controls

- Record input/output file paths in `docs/RUN_PROVENANCE_MANIFEST.md`.
- Do not use this component as standalone evidence for clinical or wet-lab efficacy.
- If output conflicts with orthogonal evidence, downgrade manuscript claim strength.
