# Model Card: rdkit_descriptors

- timestamp: `2026-05-06T12:46:35+09:00`
- component: `RDKit physicochemical descriptors`
- context_of_use: `skin-window, CMC, novelty, scaffold and formulation heuristics`
- decision_influence: `medium`
- decision_consequence: `low`
- risk_tier: `tier1`
- validation_status: `deterministic cheminformatics; salt/tautomer review needed`
- uncertainty_controls: `canonicalization, duplicate checks, manual review`
- allowed_claim: `descriptor-based heuristic only`

## Required Controls

- Record input/output file paths in `docs/RUN_PROVENANCE_MANIFEST.md`.
- Do not use this component as standalone evidence for clinical or wet-lab efficacy.
- If output conflicts with orthogonal evidence, downgrade manuscript claim strength.
