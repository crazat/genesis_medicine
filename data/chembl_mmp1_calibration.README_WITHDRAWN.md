# `chembl_mmp1_calibration.csv` — WITHDRAWN 2026-07-16

The file formerly at `data/chembl_mmp1_calibration.csv` (15 rows) was renamed to
`data/chembl_mmp1_calibration.WITHDRAWN.csv` on 2026-07-21 so that any consumer that treated it as real
data now fails loudly (`FileNotFoundError`) instead of silently recomputing on fabricated input.

## Why

A primary-source audit (2026-07-16, `scripts/round27_paperA/verify_panel_identity_pubchem.py`) established that
the file's compound names, potency values, and literature attributions are fabricated: all seven entries naming
a specific drug are a different molecule than named (e.g. the entry labelled prinomastat is C23H30N2O5S against
prinomastat's C18H21N3O5S2, PubChem CID 466151), and 14 of the 15 structures are unknown to PubChem's ~119 M
compounds. The file has no generating script and no retrieval record. Full scope and correction map:
`preprints/_metadata/FABRICATED_PANEL_SCOPE_2026_07_16.md`.

## What to use instead

`data/mmp1_panel_pubchem.csv` — 121 real MMP-1 active-site ligands, each row carrying `pubchem_cid`, `smiles`,
`formula`, `inchikey`, `value_nm` (real IC50), `pubchem_aid`, `assay_name`, and `retrieved_utc`. It supplies
both structures and provenance-backed potency; the fabricated file supplied neither truthfully.

## Who still reads the WITHDRAWN file, and why that is correct

Two tools study the file *as fabricated data* and are repointed to the `.WITHDRAWN.csv` name on purpose:

- `scripts/round27_paperA/verify_panel_identity_pubchem.py` — the forensic tool that demonstrates the fraud.
- `scripts/round27_paperA/anchor_sigma_ic50_analyze.py` — `pilot_rho()` recomputes the old fabricated-potency
  pilot (rho = +0.246) only as the labelled contrast the real n=93 anchor bound excludes. This comparison
  depends on fabricated potency; whether to keep it, drop it, or restate it is an author decision (flagged).

Everything else that read the old path (the withdrawn Boltz-2-vs-pIC50 calibration, the DUD-E `dude_*` scripts,
`abfe_benchmark_prepare.py`, the `round12/*` "15-inhibitor" scripts) treated it as real and is now fail-loud;
each is superseded by a real-panel equivalent (`build_decoy_panel_zinc.py`, the `abfe_realpanel_*` campaign,
`build_mmp1_panel_pubchem.py`). Do not repoint those to the WITHDRAWN file — that would re-ingest fabrication.

## Pipeline

The `chembl_calibration` rule (Snakefile) and stage (dvc.yaml), and the file's membership in `COMPOUND_LIBS`,
were removed on 2026-07-21 so `snakemake all` / `dvc repro` can no longer regenerate the withdrawn calibration.
