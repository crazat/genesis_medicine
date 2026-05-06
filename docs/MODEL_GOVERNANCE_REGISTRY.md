# Model Governance Registry

- timestamp: `2026-05-06T12:46:35+09:00`
- registry_csv: `pilot/cpu_meaningful/ai_model_governance_registry.csv`
- model_cards: `docs/model_cards`
- purpose: FDA-style context-of-use, risk, validation, monitoring 관점으로 AI/ML/automation component를 관리한다.

## Registry

| model | risk | context of use | validation status | allowed claim |
|---|---|---|---|---|
| boltz2_cofold | tier2 | protein-ligand cofold triage for skin target hypotheses | local calibration and PoseBusters/MD cross-check required | in silico prioritization only; no binding or efficacy claim |
| openmm_md | tier2 | pose stability and drift/failure-mode assessment | trajectory RMSD summaries; force-field and timescale caveats remain | short-timescale stability support only |
| admet_ai | tier2 | AMES/hERG/DILI/skin reaction prefiltering | external model; no local wet-lab validation yet | predicted safety risk only |
| rdkit_descriptors | tier1 | skin-window, CMC, novelty, scaffold and formulation heuristics | deterministic cheminformatics; salt/tautomer review needed | descriptor-based heuristic only |
| active_learning_rf | tier1 | next cofold/docking candidate acquisition | local scaffold-domain gate and leave-one-out MAE | queue selection heuristic only |
| xtb_gfn2 | tier1 | conformer and quantum descriptor refinement for NPASS candidates | methodology/atlas support; not direct activity evidence | quantum descriptor prioritization only |
| open_targets_evidence | tier2 | target prioritization and claim strength limitation | API-derived evidence with manual biological interpretation | target evidence support only |
| codex_curator_loop | tier2 | compute queueing, paper queueing, and decision documentation | human-supervised automation; logs/provenance required | automation workflow support only |

## Curator Rule

- `tier2` component가 paper main claim에 영향을 주면 orthogonal check 또는 명확한 limitation이 필요하다.
- model card가 없는 새 predictor/agent는 manuscript evidence로 쓰지 않는다.
- retraining, prompt update, version change가 있으면 registry와 provenance manifest를 같이 갱신한다.
