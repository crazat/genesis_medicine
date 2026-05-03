# Genesis_Medicine

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![bioRxiv](https://img.shields.io/badge/bioRxiv-19%20preprints-red)](#preprints)
[![ORCID](https://img.shields.io/badge/ORCID-0009--0004--4805--8815-A6CE39?logo=orcid&logoColor=white)](https://orcid.org/0009-0004-4805-8815)
[![Manuscripts: CC-BY 4.0](https://img.shields.io/badge/Manuscripts-CC--BY%204.0-lightgrey)](https://creativecommons.org/licenses/by/4.0/)

> Open-source autonomous in silico drug-discovery pipeline for Korean traditional medicine. Combines AlphaFold-3-class cofold (Boltz-2 + OpenFold3 + AQAffinity), REINVENT4 generative chemistry, ADMET-AI 107-endpoint safety panel, OpenMM 8 corrected absolute binding free energy, and a cost-aware multi-fidelity Bayesian-optimization scheduler with runtime-gated cascading tiers. 19 bioRxiv preprints released. Recover Korean Medicine Clinic (Seoul Gangnam, opening 2026-08-15) is the translational anchor.

---

## What this is

Genesis_Medicine is the open-source pipeline behind a 19-paper bioRxiv preprint program (2026-04 to 2026-05) on AI-augmented dermatology lead discovery. It is built around the principle that AI-derived lead candidates are most credible when they (a) are scaffold-rationalized re-discoveries of empirically-active herbal chemotypes, (b) are validated through multi-engine ensemble cofold and corrected ABFE, (c) carry explicit limitation statements on calibration, applicability domain, and translational gap, and (d) are released alongside the code, evidence ledger, and gate definitions that produced them.

The pipeline is operational on a single RTX 5090 / 32 GB workstation under WSL2 Ubuntu. No HPC required.

## Repo layout

| Layer | Path | Purpose |
|---|---|---|
| Active core (7 tools) | `src/genesis_medicine/` | Boltz-2 cofold, REINVENT4 generative, ADMET-AI v2, OpenMM 8 + openmmtools 0.26, RDKit, ChEMBL, Open Targets v4 GraphQL |
| Adapter scaffold (40+ tools) | `src/genesis_medicine/{structure,affinity,generative,...}/` | OpenFold3, AQAffinity, Chai-1, Protenix-v2, PocketXMol, FlowMol3, DiffSBDD, TurboHopp, MACE-OFF24, AIMNet2, PoseBusters, PROTAC designer, TxGNN |
| Multi-fidelity BO scheduler | `scripts/multi_fidelity_bo_scheduler.py` | Cost-aware acquisition, scientific gates, runtime gates, queue-state persistence |
| Evidence ledger | `pilot/evidence_ledger.csv` (789 rows x 136 cols) | Single CSV joining all tier outputs per (compound, target) pair |
| Calibration | `scripts/run_openfold3_chembl_calibration.py` + `pilot/calibration/` | ChEMBL pIC50 anchor (Boltz-2 R = -0.453, AQAffinity R = -0.292, n = 93 MMP-1 holdout) |
| Manuscripts | `preprints/<NN>_<slug>/manuscript.md` | 19 bioRxiv preprints (see [Preprints](#preprints)) |
| Configs | `conf/` | Hydra configs for disease, target, library, formulation |

## Preprints

19 bioRxiv preprints released between 2026-04-26 and 2026-05-03. Status as of 2026-05-03:

| # | Title (short) | Status | bioRxiv ID |
|---|---|---|---|
| 1 | Embelia ribes (Vidanga, Jadan) revisited - AI scaffold-hopping for skin fibrosis | New (resubmit v0.3) | BIORXIV/2026/722483 |
| 2 | Recover Korean Medicine Clinic workflow | New (medRxiv) | MEDRXIV/2026/351912 |
| 3 | EMB-3 scar case study v0.4 | New (resubmit v0.4) | BIORXIV/2026/722476 |
| 4 | Pigmentation TYR / TYRP1 / DCT multi-target evaluation v0.3 | New (resubmit v0.3) | BIORXIV/2026/722471 |
| 5 | Alopecia SRD5A2 / AR / beta-catenin multi-target evaluation v0.3 | New (resubmit v0.3) | BIORXIV/2026/722473 |
| 6 | Acne microbiome | New | BIORXIV/2026/721254 |
| 7 | Photoaging EGCG (MMP-1, SIRT1) | New | BIORXIV/2026/721257 |
| 8 | ABFE methodology v0.8 (T4L99A, EMB-3 x MMP-1) | New (resubmit v0.8) | BIORXIV/2026/722479 |
| 9 | Cross-disease IPF | New | BIORXIV/2026/721261 |
| 10 | Chronotherapy 자오류주 | New | BIORXIV/2026/721263 |
| 11 | Korean PGx topical | New (medRxiv) | MEDRXIV/2026/351914 |
| 12 | Open-source perspective v0.4 (this pipeline) | New (resubmit v0.4) | BIORXIV/2026/722485 |
| 13 | PIEZO1 / MLCK alopecia | New | BIORXIV/2026/721264 |
| 14 | Topical PBPK methodology v0.3 (102-cmp x 4-vehicle) | New (resubmit v0.3) | BIORXIV/2026/722481 |
| 15 | Universal pterocarpan scaffold (14 targets) | New | BIORXIV/2026/722463 |
| 16 | R15 chromanol safety triage | New | BIORXIV/2026/722464 |
| 17 | R16 topical chromanol lead (200 ns) | New | BIORXIV/2026/722467 |
| 18 | Multi-fidelity BO scheduler with runtime gating v0.2 | New | BIORXIV/2026/722486 |
| 19 | Korean Pharmacopoeia herbal scaffold cross-reference v0.1 | Drafted; submission pending | (pending) |
| 43 | R17 constrained generative chromanol atlas | New | BIORXIV/2026/722468 |

DOIs (`10.1101/2026.MM.DD.XXXXXX`) issue 24 to 72 hours after submission. See `preprints/_metadata/*.json` for per-paper metadata and `preprints/RESUBMISSION_PLAN.md` for the rejection-and-recovery audit.

## Quick start

```bash
# 1) WSL2 + CUDA 12.8 prerequisite
git clone https://github.com/crazat/genesis_medicine
cd genesis_medicine

# 2) Local venv
uv venv --python 3.11 && source .venv/bin/activate
uv pip install -e ".[dev]"

# 3) OpenFold3 + AQAffinity stack (HuggingFace gated; accept terms first)
huggingface-cli login
bash external_tools/aqaffinity_install.sh

# 4) Build evidence ledger from existing pilot CSVs
.venv/bin/python scripts/build_evidence_ledger.py

# 5) Run the multi-fidelity scheduler
.venv/bin/python scripts/multi_fidelity_bo_scheduler.py --top 30

# 6) Pilot a disease screen
python -m genesis_medicine.cli run disease=alzheimer structure=boltz2
python -m genesis_medicine.cli run disease=alzheimer library=herb_tcm
```

## Documentation

- `preprints/RESUBMISSION_PLAN.md` - 19-paper rejection / re-submission audit and Wave plan
- `preprints/UPLOAD_AGENT_PROMPT.md` - bioRxiv submission agent prompt (self-contained)
- `docs/PAPER_FACTORY_QUEUE.md` - 44 paper candidates (P15-P58) with evidence rows
- `docs/PAPER_PLAN.md` - methodology paper outline (Embelin scaffold-hopping, J Cheminform target)
- `docs/PREPRINT_SUBMISSION_GUIDE.md` - manual bioRxiv / medRxiv submission procedure
- `docs/INSTALL_WINDOWS.md` - WSL2 + CUDA 12 installation
- `docs/ARCHITECTURE.md` - 9-stage pipeline architecture
- `pilot/scientific_gates.yaml` - 30+ scientific gates (action: flag / hold / suppress)

## Three-pillar institutional context

- **HAN PREDICT, Inc.** - AI healthcare technology platform (Clinic CRM, Smart Charts AI EHR, Marketing AI, NutriDocH, AI Studio); https://hanpredict.com
- **Recover Korean Medicine Clinic** - Korean medicine clinic specializing in skin regeneration, Seoul Gangnam, opening 2026-08-15; https://recover-clinic.kr
- **Genesis_Medicine Lab** - AI-driven natural product drug discovery R&D division (this repo)

## Honest limitations

- All findings are in silico; no clinical efficacy, no commercial product, and no novel-composition claim.
- Boltz-2 affinity_probability_binary is a relative-ranking predictor (Pearson R = -0.453 vs pIC50, n = 93 MMP-1 holdout); not an absolute potency estimate.
- AQAffinity standalone correlation on the same holdout is R = -0.292; ensemble use (mean rank of Boltz-2 and AQAffinity) is the recommended consume pattern (cross-engine agreement R = 0.109 indicates orthogonal signal).
- MMP-1 ABFE without explicit holo-Zn cofactor (ZAFF / MCPB.py) returns delta-G_bind approximately 0 kcal/mol; quantitative MMP-1 affinity claim is gated on ZAFF integration (`mmp1_zinc_pending` gate).
- Scientific gates encode 30+ veto / flag rules: quinone reactivity review, prior-art / FTO watchlist, PoseBusters / cross-model consensus, dermal regulatory, skin sensitization, single-cell foundation-model reliability.
- The Korean Pharmacopoeia (KHP) cross-reference (preprint 19) reports re-discoveries in the 0.25-0.45 ECFP6 Tanimoto band, separated from the IP / FTO concern band (>= 0.85) by construction.

## Legal and regulatory notes

- **AlphaFold 3 official weights** are non-commercial use only and not used in the default execution path.
- **HERB database** is CC-BY-NC; commercial use is restricted and the active core defaults to **COCONUT 2.0** and **LOTUS** (CC0) for the natural-product axis.
- **AQAffinity weights** are Apache-2.0 but distributed via gated HuggingFace; users must accept terms of use before download.
- This repository is Apache-2.0 licensed (code). Each external_tool / external submodule retains its own license; see individual subdirectory LICENSE files.
- This is research software. It does not replace clinical or regulatory judgment. Any IND filing through Korea MFDS or another regulator requires independent KHP / KP listing review.

## Citation

If you use this software or build on the preprints, please cite:

- The relevant per-preprint DOI (`10.1101/2026.MM.DD.XXXXXX`, see `preprints/_metadata/*.json`).
- The repository: `CITATION.cff`.

## Acknowledgments

- Recover Korean Medicine Clinic (clinic context and herbal pharmacopoeia anchor)
- Open-source community: Boltz-2 (MIT), OpenFold3 (Apache-2.0), SandboxAQ AQAffinity (Apache-2.0, gated), OpenMM, openmmtools, OpenFE, REINVENT4, ADMET-AI, RDKit, scikit-learn

## License

Apache-2.0 (code). Manuscripts are CC-BY 4.0. Data sources retain their own licenses.

---

**Correspondence**: HanCheongWoo (sole author of preprints 1-19) - `crazat7@gmail.com` (ORCID-registered) | `admin@hanpredict.com` (institutional)

**ORCID**: [0009-0004-4805-8815](https://orcid.org/0009-0004-4805-8815)
