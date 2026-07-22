# PLAN — Reliability data as a community benchmark (R54 #4)

Turn the reseed-variance corpus into a reusable, citable benchmark (white space: no benchmark
covers semiempirical-QM free-energy reseed variance OR co-folding-confidence reproducibility;
MLIPAudit arXiv:2511.20487 Nov 2025 explicitly excludes uncertainty-calibration / reproducibility).

## Assets to release
- paper_A σ_E corpus: `sigma_e_v212_v303_unified_consolidated.csv` (1,755 cells × ~92–149 reseeds)
  + per-cycle reconstruction; specification-curve table (117 cells).
- paper_B σ_iptm corpus: `sigma_iptm_unified_v143_v303_percycle.csv` (15 ligands × 161 cycles × 100 samples).
- Derived reliability layers (this work): conformal intervals, multiverse/G-theory components,
  static-vs-σ table.

## Hosting / submission targets
1. **Polaris (polarishub.io)** — drug-discovery-native benchmark hub (Recursion/Valence + pharma).
   Path: `polaris-lib` `upload_dataset` + define a custom "prediction-reliability / reseed-variance"
   benchmark; propose via GitHub Discussion #87 ("Datasets or benchmarks to add"). Prototype with a
   single GFN2 slice first. **[needs Polaris account — user action]**
2. **Croissant 1.1 metadata** (MLCommons, Feb 2026) — emit JSON-LD with the new provenance/lineage
   fields encoding "161 reseed cycles, per-cell RNG/config" → machine-traceable + Google Dataset
   Search discoverable. (HuggingFace/Kaggle/OpenML auto-emit it.)
3. **Peer-reviewed wrapper** — *Nature Scientific Data* Data Descriptor (our reseed CVs ARE the
   mandatory technical-validation section) OR *J. Cheminformatics* Data Note (lowest friction; our
   Zenodo CC release already meets their reproducibility-only policy).
4. **NeurIPS 2026 "Evaluations & Datasets" track** — broadened to treat evaluation as science
   ("how reliable are reliability scores"); reseed-variance fits exactly; code required at submission.
5. **Zenodo Community** "Prediction Reliability in Comp-Chem" — group all 17+ existing DOIs + the new
   reliability datasets under one citable collection identity. **[user action on Zenodo]**

## Documentation to ship (drafts to write next)
- Datasheet for Datasets (Gebru template): collection process, RNG/seed handling, known limits
  (furan/ALPB failures, GFN0/1/2 non-comparable absolute energies).
- Model card for the evaluation harness (xtb sept-matrix + Boltz cofold reseed pipeline).
- Reproducibility: the 3 R54 scripts (conformal / multiverse-gtheory / iptm-static) + the
  consolidate scripts, containerized for an ACM/NeurIPS artifact badge.

## Status
- Data + derived layers EXIST and are release-ready.
- Croissant JSON + datasheet are writable now (next sub-step).
- Polaris/Zenodo-Community uploads are EXTERNAL actions requiring the user's accounts → flagged,
  not auto-executed.

## Competitive note
MLIPAudit / MLIP-Arena benchmark MLIPs but exclude UQ/reproducibility → contribute a
reseed-variance/UQ-calibration module (file a GitHub issue/PR) to plant a flag in an active venue.
