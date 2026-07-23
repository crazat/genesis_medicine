# Zenodo upload-agent prompt — paper_A_zaff (new deposit, 2026-07-23)

You are an upload agent with authenticated access to the author's Zenodo account. Deposit ONE new record.
Everything you need is below. The author (Cheongwoo Han) reviews and clicks Publish; do not invent metadata.

## Context (why this is a NEW record, not a supersede)

This manuscript, `paper_A_zaff_abfe_limitations`, was never deposited: an earlier LaTeX draft
(`manuscript.tex`) was built on a fabricated 15-ligand calibration panel and was quarantined on 2026-07-16,
never submitted or deposited. It has now been rewritten from scratch on a real, provenance-tracked panel
(14 PubChem MMP-1 inhibitors, each row carrying its PubChem CID, assay AID and retrieval timestamp) and the
accuracy axis re-derived on that panel. The rewrite is the file you are depositing. There is therefore no
prior DOI to supersede — mint a fresh record (new concept DOI).

Do NOT attach the old `manuscript.tex` or its stale `manuscript.pdf`/`manuscript.html`; they are the
superseded fabricated-panel draft and are retained in the repo for history only.

The two published records that DID use the fabricated panel are already corrected on Zenodo and are not part
of this task: Record VIII / 08_abfe (20018254 → new version 21466392) and Record XXVI / paper_A v6
(20247828 → new version 21466405). See `ZENODO_CORRECTION_RESULT_2026_07_19.md` and
`DEPOSIT_CORRECTION_PACKAGE_2026_07_21_records_VIII_XXVI.md`.

## The record to create

- Upload type: Publication → Preprint.
- Title:
  Systematic over-binding in ZAFF-AMBER absolute binding free energy calculations for zinc-metalloenzyme inhibitors: a 14-compound accuracy benchmark on MMP-1
- Authors / creators: Cheongwoo Han (single author).
  - ORCID: 0009-0004-4805-8815
  - Affiliations: Genesis Medicine Lab, Seoul, Republic of Korea; HAN PREDICT, Inc.; Recover Korean Medicine Clinic.
- License: Creative Commons Attribution 4.0 International (CC-BY-4.0) — same as the author's other records.
- Language: English.
- Publication date: 2026-07-23.
- Keywords: ABFE; ZAFF-AMBER; zinc metalloenzyme; MMP-1; hydroxamate; over-binding; MultiStateSampler; accuracy benchmark; free energy calculation.

### Files to attach (in this order)

Primary (repo path `preprints/paper_A_zaff_abfe_limitations/`):
1. `manuscript_v1_realpanel_accuracy.pdf`   ← main article
2. `manuscript_v1_realpanel_accuracy.md`     ← source
3. `figures/fig_accuracy_scatter.png`
4. `figures/fig_potency_residual.png`

Recommended supplementary (makes the deposit self-contained and auditable — the whole point is provenance):
5. `data/mmp1_panel_pubchem.csv`             ← the real panel (PubChem CID / assay AID / retrieval timestamp per row)
6. `pilot/abfe_realpanel_mmp1/abfe_subset.csv`        ← the 14-compound subset actually run (with SMILES)
7. `pilot/abfe_realpanel_mmp1/abfe_realpanel_results.csv`  ← per-compound ABFE dG + deviation
8. `pilot/abfe_realpanel_mmp1/abfe_realpanel_summary.json` ← aggregate statistics
9. `scripts/zaff_realpanel_manuscript_figures.py`    ← regenerates the warhead classification, stats and figures

Do not attach: `manuscript.tex`, `manuscript.pdf`, `manuscript.html` (superseded fabricated-panel draft).

### Description (paste into the Zenodo Description field)

> Absolute binding free energy (ABFE) calculation on zinc metalloenzymes stress-tests fixed-charge zinc force
> fields such as ZAFF-AMBER. We benchmark the ZAFF-AMBER + GAFF-2 + AM1-BCC ABFE protocol against experimental
> affinity for fourteen MMP-1 inhibitors drawn from PubChem bioassay records (IC50 0.78 nM to 98 µM; eleven
> hydroxamates, two carboxylates, one phosphonate), each carrying its PubChem CID, assay AID and retrieval
> timestamp. The protocol over-binds every compound, by 0.6 to 58.1 kcal/mol, and the over-binding is governed
> by the chelation strength of the warhead rather than by the measured potency: a weak (50 µM) hydroxamate still
> over-binds by 43 kcal/mol while a mid-potency (77 nM) phosphonate over-binds by only 4 kcal/mol. The rank
> correlation is weak and imprecise (Spearman 0.587, 95% CI [0.041, 0.847]; Pearson 0.631) with no sign-flips.
> Within-run statistical precision (0.5 to 0.9 kcal/mol) is not accuracy. We also document two pipeline failure
> modes and their fixes (a ReplicaExchangeSampler swap-all deadlock, and a production NaN crash requiring an
> explicit warmup) and contrast ABFE single-compound instability with population-level xtb rank stability. We
> recommend that fixed-charge ZAFF-AMBER ABFE not be used to rank zinc-chelating metalloenzyme inhibitors
> without warhead-stratified error budgeting. All data, code and provenance are attached and released at
> https://github.com/crazat/genesis_medicine (Apache-2.0).
>
> Provenance note: this is a fresh accuracy benchmark on a real, PubChem-sourced panel. An earlier draft of this
> work used a fabricated calibration panel and was withdrawn before any deposit; none of its compound identities,
> potencies or accuracy claims are carried into this record.

### Related identifiers (Zenodo "Related/alternate identifiers")

- "is documented by" → https://github.com/crazat/genesis_medicine (code repository, Apache-2.0).
- "is supplemented by" → 10.5281/zenodo.21466405 (corrected paper_A v6 reproducibility reconstruction; companion reliability paper).
- "is supplemented by" → 10.5281/zenodo.21466392 (corrected 08_abfe ABFE-pipeline methodology record).

## Execution checklist

1. New upload → set Upload type = Preprint, fill Title / Creator (with ORCID + affiliations) / License CC-BY-4.0 / Publication date 2026-07-23 / Keywords / Language English.
2. Attach files 1–4 (required) and 5–9 (recommended supplementary), in the order above; do not attach the superseded .tex/.pdf/.html.
3. Paste the Description text; add the three Related identifiers.
4. Save draft, then verify: title has no drug names; the PDF is `manuscript_v1_realpanel_accuracy.pdf` (14-compound real-panel version, not the fabricated-panel draft); Spearman/CI in the description match the abstract.
5. Publish. A fresh concept DOI + version DOI are minted.
6. After publish: append a row to `zenodo_upload_log.csv`
   (`paper_A_zaff,published,,,<draft_id>,<url>,<prod_doi>,<record_url>,published,<utc>,new deposit — real-panel accuracy benchmark`),
   add the record to `zenodo_published_index.md`, and report the DOI back to the author.

## What is NOT in scope here (author decisions)

- Journal submission of this manuscript (venue choice is the author's).
- Any change to the already-corrected records VIII / XXVI / #3–#22 (all done, see the correction result files).
- The JCIM submission linkage for the corrected paper_A v6 (separate journal correspondence, flagged in the VIII/XXVI package).
