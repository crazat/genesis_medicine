# Zenodo integrity-correction result — records #20/#21/#22 superseded (2026-07-19)

Executed `preprints/_metadata/ZENODO_UPLOAD_AGENT_PROMPT.md` in full. Each record was superseded by a
**new version under the same concept DOI** (Zenodo versioned supersede, NOT a retraction). Old versions remain
citable and flagged superseded. Author: Cheongwoo Han (ORCID 0009-0004-4805-8815); license CC-BY 4.0 unchanged.

| # | concept DOI | NEW version DOI | new record | version string |
|---|---|---|---|---|
| 20 | 10.5281/zenodo.20134438 | **10.5281/zenodo.21430921** | https://zenodo.org/records/21430921 | v5h-corrected-2026-07-18 |
| 21 | 10.5281/zenodo.20134441 | **10.5281/zenodo.21430923** | https://zenodo.org/records/21430923 | v0.1-corrected-2026-07-18 |
| 22 | 10.5281/zenodo.20134446 | **10.5281/zenodo.21430926** | https://zenodo.org/records/21430926 | v0.1-corrected-2026-07-18 |

Verified: each concept DOI's `/api/records/<conceptrecid>` now resolves to the corrected new version
(latest-version id MATCH for all three).

## What changed per record

- **Files** (all three): removed BOTH stale manuscript files (old `.pdf` + old `.md` — the old `.md` still
  carried the fabricated panel) and uploaded the corrected pair `manuscript_corrected_2026-07-18.pdf` +
  `manuscript_corrected_2026-07-18.md` (the corrected repo `manuscript.md`). No figure/data files existed in
  these deposits, so nothing else was touched.
  - #20 pdf md5 3546cfe29d017d24f980cefbbe79cee6 / md f5d9ea0a6b8934491b592f7e19ef0434
  - #21 pdf md5 62d492919183f15668ba95b4d903bd2f / md a32d0156451696e6e4cda2577f4994ef
  - #22 pdf md5 92c9856afe1319746d4fd20505924f90 / md 0e06bd7c74ff359076db65d98a451827
- **Additional notes** (`notes`): prepended `CORRECTION (new version, 2026-07-18): <verbatim VERSION NOTE>`.
- **Description**: prepended a highlighted correction banner (verbatim VERSION NOTE) above the original abstract.
- **Title**: #21 only — "...zinc-hydroxamate MMP-1 inhibitors" → "...zinc-hydroxamate-like MMP-1 active-site
  ligands". #20 and #22 titles unchanged.
- **Version** string bumped to `-corrected-2026-07-18` so the supersede is legible in the version picker.
- Unchanged: concept DOI, sole author + ORCID, CC-BY 4.0, keywords, upload_type/publication_type, COI note.

## Tooling (reusable)
- `C:\Users\craza\zenodo_correct_orchestrate.py` — prep|verify|publish <20|21|22>. Draft ids saved to
  `C:\Users\craza\zenodo_correction_notes\draft_<tag>.id`. Verbatim version notes in
  `C:\Users\craza\zenodo_correction_notes\note_{20,21,22}.txt`.
- `.env` ZENODO_TOKEN had `deposit:actions` scope → API newversion + publish (HTTP 202) succeeded end-to-end.

## Addendum (2026-07-19) — dangling-citation fixes #3, #5 (added to the prompt after the first three)

Same new-version supersede mechanism (same concept DOI, CC-BY 4.0, sole author). These two carried NO fabricated
panel of their own — only a citation to the now-withdrawn calibration; the corrected manuscripts reframe/remove
those citations. Files swapped both stale `.pdf` + `.md` for the corrected `manuscript_corrected_2026-07-18.pdf` + corrected `manuscript.md`. Titles unchanged.

| # | concept DOI | NEW version DOI | new record | version string |
|---|---|---|---|---|
| 3 (EMB-3 scar case study) | 10.5281/zenodo.20018332 | **10.5281/zenodo.21431020** | https://zenodo.org/records/21431020 | v0.4-corrected-2026-07-18 |
| 5 (AGA Korean-herbal eval) | 10.5281/zenodo.20018338 | **10.5281/zenodo.21431025** | https://zenodo.org/records/21431025 | v0.3-corrected-2026-07-18 |

Verified: both concept DOIs now resolve to the corrected new version (latest-version id MATCH).
- #3 pdf md5 86ce7a33d380437ea53b8543ae2b30cb / md f2c3d035e8a2ddede4f4f40c16c7eff9
- #5 pdf md5 461cc0edde29de82fcc040fb92152f80 / md ddb2ee731231fffc6e05b197fe1bfe04

All FIVE prompt records (#3, #5, #20, #21, #22) are now superseded by corrected new versions.

---

## Addendum (2026-07-21) — Records VIII & XXVI superseded

Executed `preprints/_metadata/DEPOSIT_CORRECTION_PACKAGE_2026_07_21_records_VIII_XXVI.md` in full. Same
mechanism (new version under the same concept DOI, CC-BY 4.0, sole author Cheongwoo Han / ORCID
0009-0004-4805-8815). Both concept DOIs verified to resolve to the corrected version (latest-version id MATCH).

| Record | concept DOI | NEW version DOI | new record | version string |
|---|---|---|---|---|
| **VIII** (#8 abfe) | 10.5281/zenodo.20018253 | **10.5281/zenodo.21466392** | https://zenodo.org/records/21466392 | v0.9 (2026-07-21 correction) |
| **XXVI** (#26 paper_A v6) | 10.5281/zenodo.20247827 | **10.5281/zenodo.21466405** | https://zenodo.org/records/21466405 | v7 — reproducibility reconstruction (2026-07-21 correction) |

### Record VIII — 20018254 → 21466392
- **Files**: deleted `manuscript.md` + `manuscript.pdf`; uploaded `manuscript_v0.9_corrected_deposit.pdf`
  (md5 dfd20484c4d849fa7d563072ef4a1119) + `manuscript_v0.9_corrected_deposit.md`
  (md5 2a365ee788175a4abd1d14a80ec9f070). Final file count 2.
- **Figures**: the package listed `figures/* (unchanged)` — the deposit had **no** figures attached (verified
  before prep), so this was a no-op. The repo figure `calibration_boltz2_chembl_mmp1.png` belongs to the
  **withdrawn** §3.6 and was deliberately NOT introduced.
- **Metadata**: title unchanged; `notes` prefixed `CORRECTION (new version, 2026-07-21): <verbatim note>` above
  the existing COI block; `description` = correction banner prepended above the original (panel-independent)
  ABFE abstract; version → `v0.9 (2026-07-21 correction)`. Keywords unchanged.

### Record XXVI — 20247828 → 21466405
- **Files**: deleted the contaminated `manuscript_v0.2.{md,pdf}` and the three withdrawn v6 figures
  (`figure3_xtb_3mode_outlier`, `figure4_shap_top20_dual`, `figure5_7organ_pleiotropy`, .png+.pdf each = 8
  deletions); uploaded `manuscript_v0.3_reproducibility.pdf` (md5 9af8ff76560cd8afe568bd652395326d) + `.md`
  (md5 8871ff8d8f360ca9a76cb60ade2a175f) + `figure1_v03_nnp_redundancy.{png,pdf}` +
  `figure2_v03_rank_vs_pearson.{png,pdf}`. Final file count 15.
- **Retained** (verified panel-free before publish): `SI.zip` (37,528 entries; no calibration/panel file
  present), `conformal.zip`, `SI_README.md`, `references.md`,
  `sigma_e_v212_v303_unified_consolidated.csv`, and v6 figures 1–2 (`figure1_boltz_25cycle_convergence`,
  `figure2_5nnp_bootstrap_ci`) — not on the withdrawal list, and inspected as images: a wall-time convergence
  plot and an Orb-v2/MACE-OMol25 energy scatter, carrying no compound identity or potency. (Note: figure 2's
  title still reads "5-NNP" while the reconstruction is a three-NNP work.)
- **Title** changed as specified by the package (drops both drug names and the repositioning framing).
- **Description**: the v6 description **was** the withdrawn repositioning abstract (vorinostat/indapamide
  candidacy, the refuted r<-0.97 descriptor claim, the Xipamide wet-lab priority). A banner above it would have
  left the retracted narrative standing as the record's public summary, so the description was **replaced**:
  correction banner + the reconstruction's own abstract (verbatim from `manuscript_v0.3_reproducibility.md`).
  The superseded version keeps the original text and stays citable.
- **Keywords**: dropped `drug repositioning`, `vorinostat`, `indapamide`, `sulfonamide diuretic` (they assert
  exactly what this version withdraws, and would keep the record discoverable under the retracted claim); added
  `reproducibility`, `uncertainty quantification` (`conformal prediction` was already present). Not specified by
  the package — author-approved 2026-07-21.
- **Author-approved before publish** (2026-07-21): the title change, the description replacement, the keyword
  edit, and the VIII no-figure decision.

### Tooling
- `C:\Users\craza\zenodo_correct_orchestrate_v2.py` — prep|verify|publish <8|26>; same shape as the 2026-07-18
  orchestrator, with per-record explicit delete/upload file plans. Notes in
  `C:\Users\craza\zenodo_correction_notes\note_{8,26}.txt`, draft ids in `draft_{8,26}.id`.
- `.env` ZENODO_TOKEN retains `deposit:actions` → newversion + publish (HTTP 202) end-to-end.

### Still open after this batch
- **JCIM submission — RESOLVED 2026-07-21, no action needed.** Pre-send mailbox verification established that
  the manuscript (ID `ci-2026-01786n`; ChronosHub submission `51B8CAD3-7F60-4C3D-AEFD-501DEDC76284`) was
  **unsubmitted by the JCIM editorial office on 2026-06-03**, one day after submission, for three completeness
  defects (references cited but no reference list; "Data and code availability" heading rename; Supporting
  Information cited but not uploaded). It was never re-submitted and never entered peer review, so there is
  nothing pending to withdraw and the Zenodo supersede creates no journal-side mismatch. The 2026-07-21
  correction package's "CRITICAL downstream — JCIM submission linkage" flag rested on a wrong premise. The
  drafted withdrawal letter is retained, marked NOT APPLICABLE, at
  `C:\Users\craza\jcim_withdrawal\JCIM_withdrawal_letter_2026_07_21.md` — **not sent.**
- **#3–#7 dangling citations** to the withdrawn §3.6 "calibrated at |rho| ~ 0.72" justification: #3 and #5 were
  handled in the 2026-07-19 addendum; **#4, #6, #7 remain unreviewed.**
- **recover-clinic.kr/research** blockers C-1 / C-2 are now unblocked — both records resolve to corrected content.

---

## Addendum 2 (2026-07-21) — dangling-citation pass: 7 records superseded

Follow-up to the ripple flagged in `DEPOSIT_CORRECTION_PACKAGE_2026_07_18.md`. Full analysis:
`DANGLING_CITATION_AUDIT_2026_07_21.md`. All seven concept DOIs verified to resolve to the corrected version.

| # | concept DOI | NEW version DOI | version | OSF |
|---|---|---|---|---|
| 3  | 10.5281/zenodo.20018332 | **10.5281/zenodo.21466637** | v0.5-corrected-2026-07-21 | vk5e9 v3 |
| 4  | 10.5281/zenodo.20018336 | **10.5281/zenodo.21466642** | v0.4-corrected-2026-07-21 | hdxv3 v2 |
| 5  | 10.5281/zenodo.20018338 | **10.5281/zenodo.21466645** | v0.4-corrected-2026-07-21 | nkzxb v2 |
| 8  | 10.5281/zenodo.20018253 | **10.5281/zenodo.21466648** | v0.9.1 citation correction | tmhev v3 |
| 12 | 10.5281/zenodo.20018342 | **10.5281/zenodo.21466649** | v0.5-corrected-2026-07-21 | eh2f7 v2 |
| 13 | 10.5281/zenodo.20018377 | **10.5281/zenodo.21466653** | v0.3-corrected-2026-07-21 | kmh4y v2 |
| 15 | 10.5281/zenodo.20018348 | **10.5281/zenodo.21466656** | v0.5-corrected-2026-07-21 | rnxs9 v2 |

**No result, ranking or figure value changes in any of the seven.** These are provenance and
scope-of-claim corrections.

### Why #8 needed a second pass on the same day

The 2026-07-21 correction published earlier that day (10.5281/zenodo.21466392) withdrew §3.6 but **left a
sentence citing §3.6 as live support**: *"the Boltz-2-alone signal is still calibrated against ChEMBL (§3.6)"*.
The 07-18 verification had checked for residual named-drug assertions and this sentence contains none, so it
passed that check while still asserting the withdrawn calibration. Superseded by 10.5281/zenodo.21466648.
**Lesson for future correction passes: grep for cross-references to the withdrawn section, not only for the
withdrawn content's vocabulary.**

### The two anchors

- **Anchor A, "|rho| ~ 0.72"** (n=15, `data/chembl_mmp1_calibration.csv`) — the fabricated panel. **Void.**
  Cited as live support by #8, #12, and (as a forward promise) #3.
- **Anchor B, "R = -0.453, n=93"** (`pilot/cpu_meaningful/chembl_boltz2_calibration.csv`) — **real.**
  Provenance established: `scripts/cpu_queue_worker.sh:130-160` retrieves it live from the ChEMBL API
  (`target_chembl_id='CHEMBL321'`, IC50/nM) preserving `document_chembl_id` per record. Recomputed:
  Pearson -0.4535 / Spearman -0.4582, reproducing the published figure. It was cited wrongly, not wrongly
  derived: #4/#5/#13/#15 attributed it to preprint #8 (which never reported it) or to "the parallel MMP-1
  calibration set" (which reads as the fabricated panel), and #4/#5 used it to certify
  `affinity_prob_binary` — a metric it was never measured on, and which on the same 93 compounds carries
  essentially no potency signal (Pearson +0.178 / Spearman +0.048).

### Scope corrections to the 07-18 ripple flag
- **#6 and #7 needed nothing** — neither carries an anchor citation at all. The "#3-#7" range was overstated.
- **#12, #13, #15 were outside the flagged range but did need fixing.** The range was also under-reaching.

### Still open after this pass
- **⚠ The fabricated panel is still wired into the executable pipeline** — `Snakefile:26`/`:83` plus nine
  consumer scripts still read `data/chembl_mmp1_calibration.csv`. Any Snakefile re-run regenerates
  contaminated results. Remediation plan in the audit document; **not done.**
- Stale `.html` renders (notably `08_abfe_methodology/manuscript.html`) still carry the full withdrawn §3.6
  including the rho = -0.724 figures.
- Stale "ChemRxiv preprint, 2026 / forthcoming" companion citations across ~10 manuscripts (hygiene).
- `paper_A_zaff_abfe_limitations` (OSF q4z6w) remains at its 07-18 PARTIAL state — open author decision.
