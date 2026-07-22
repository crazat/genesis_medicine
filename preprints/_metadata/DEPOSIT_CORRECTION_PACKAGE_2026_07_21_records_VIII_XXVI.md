# Zenodo deposit correction package — Records VIII & XXVI (2026-07-21)

Companion to `DEPOSIT_CORRECTION_PACKAGE_2026_07_18.md`, which corrected the three cross-NNP records
(#20 / #21 / #22, concept DOIs 20134439 / 20134442 / 20134447 → superseded 2026-07-19, result map
`ZENODO_CORRECTION_RESULT_2026_07_19.md`). That batch did **not** touch two other *published* records that use
the same fabricated 15-ligand panel (`data/chembl_mmp1_calibration.csv`). This package prepares those two.

As before: correction mechanism is a **new version under the same concept DOI** (Zenodo versioned supersede, not
retraction — preserves citability, replaces contaminated content). The author executes the actual Zenodo uploads
(interactive login); this repo holds the corrected manuscripts, rebuilt PDFs, and the version-note text.

## Scope — the two records the 2026-07-18 batch missed

| Record | DOI | title (as published) | published | grade | source manuscript |
|---|---|---|---|---|---|
| **VIII** | 10.5281/zenodo.20018254 | A calibrated absolute binding free energy pipeline … OpenMM 8 / openmmtools 0.26 | 2026-05-04 (v0.8) | **HIGH** (10 names, 39 potency; localized to §3.6) | `08_abfe_methodology/manuscript.md` |
| **XXVI** | 10.5281/zenodo.20247828 | Cross-Validation of Three NNPs for MMP-1 Zn Active-Site Inhibitor Ranking: A Computationally-Driven Repositioning Study of Vorinostat and Indapamide | 2026-06-02 (single-author) | **HIGH** (identity + potency + the entire repositioning narrative) | rebuilt as `23_paper_A_v6_mmp1_5nnp_xtb/manuscript_v0.3_reproducibility.md` |

Both were fixed locally on 2026-07-16/18 but never superseded on Zenodo. Record XXVI is the source of the
"Vorinostat / Indapamide" claims still visible on recover-clinic.kr/research (Card 01) — see
`HANDOFF_recover_clinic_research_page_CORRECTIONS_2026_07_20.md`, blockers C-1 and C-2. The page cannot be
truthfully fixed until these two records are superseded, because its links resolve to the contaminated content.

---

## Record VIII — 20018254 (08_abfe)

- **Contamination**: HIGH by name-density (10 drug names, 39 potency mentions) but structurally *localized* — the
  panel enters only in §3.6 (a Boltz-2-front-end-vs-pIC50 potency calibration) and one §4.1 zinc parenthetical.
  The ABFE method itself (flat-bottom centroid restraint, analytical standard-state correction, T4L99A/benzene
  benchmark, EMB-3 application) does not use the panel and is untouched.
- **Correction applied (2026-07-16/18)**: §3.6 withdrawn in full; the 3 spillover mentions fixed; a rendered
  disclosure added. Verified 0 residual named-drug assertions in the body.
- **Deposit-ready artifact (built 2026-07-21)**: `08_abfe_methodology/manuscript_v0.9_corrected_deposit.md` +
  `…/manuscript_v0.9_corrected_deposit.pdf` (92 KB). This is `manuscript.md` with the internal
  "⛔ DO NOT SUBMIT OR DEPOSIT" working-guard stripped and replaced by the publication correction banner below.
  (The working `manuscript.md` keeps its guard and is NOT the file to upload.)
- **Title / metadata**: unchanged. Suggested version label: `v0.9 (2026-07-21 correction)`.
- **Files to attach to the new version**: `manuscript_v0.9_corrected_deposit.pdf`,
  `manuscript_v0.9_corrected_deposit.md`, `figures/*` (unchanged).

Version-note text (paste into the Zenodo new-version Description / Additional notes):

> Correction (version 2, 2026-07-21) — fabricated ligand-panel annotations. After this record was first deposited
> (2026-05-04), a primary-source audit (2026-07-16) established that the 15-ligand calibration panel used in
> Section 3.6 (`data/chembl_mmp1_calibration.csv`) carries fabricated compound names, potency values, and
> literature attributions. A structure-first PubChem lookup finds that all seven entries naming a specific drug
> are a different molecule than named — e.g. the entry labelled prinomastat is C23H30N2O5S against prinomastat's
> C18H21N3O5S2 (PubChem CID 466151) — and 14 of the 15 structures are unknown to PubChem (~119 M compounds). No
> script in the repository generates the file and it carries no retrieval record; a previous automated session
> produced it and the circumstances are not recoverable. This version withdraws Section 3.6 in full (the
> Boltz-2-vs-pIC50 calibration, being a correlation against fabricated potency, has no verified ground truth) and
> removes every compound-identity and potency claim derived from the panel. Unaffected: the absolute binding free
> energy pipeline itself, its T4 lysozyme L99A / benzene benchmark, and the EMB-3 application — none use the panel.
> Full scope: `preprints/_metadata/FABRICATED_PANEL_SCOPE_2026_07_16.md`.

- **Ripple to note (not blocking)**: the withdrawn §3.6 calibration was cited by preprints #3–#7
  (herbal / dermatology, themselves panel-CLEAN) as justification that the Boltz-2 ranking is "calibrated at
  |ρ|≈0.72". That justification is now void and those citations dangle — a separate follow-up.

---

## Record XXVI — 20247828 (paper_A v6)

- **Contamination**: HIGH and structural. The published record's *title itself* names two drugs, and its central
  claim is a "repositioning study of Vorinostat and Indapamide". Both identifications are wrong (CHEMBL406 ≠
  indapamide, CHEMBL98 ≠ vorinostat; the pipeline computed different molecules), the potency axis is fabricated,
  and the manuscript's headline r>0.97 descriptor correlations do not reproduce (they sit at r≈0). This is not a
  §-local fix; the repositioning narrative is the paper.
- **Correction = full reconstruction (built 2026-07-16, finalized 2026-07-18)**:
  `23_paper_A_v6_mmp1_5nnp_xtb/manuscript_v0.3_reproducibility.md`. Ground-up rebuild that claims neither identity
  nor potency; every retained claim traces to a named source file. §6.1 lists exactly what was removed (the whole
  repositioning narrative, all potency-dependent modelling, the 5-compound ΔE_relax comparison, the |r|>0.97
  descriptor table, the composite SHAP figure, and every compound identity/potency). Verified clean (single name
  hit = the refutation in §2.2).
- **Deposit-ready artifact (rebuilt 2026-07-21)**: `…/manuscript_v0.3_reproducibility.pdf` (534 KB, figures
  embedded). Old stale PDF (Jul 16) replaced.
- **⚠ Metadata changes the author must approve — this is a title-and-content supersede, not a patch:**
  - **New title**: "Reproducibility of a Boltz-2 / GFN2-xTB / three-NNP stack on the MMP-1 catalytic Zn²⁺ site:
    per-cell σ_E, a calibrated numeric floor, and what the ensemble does not license." (drops both drug names and
    the repositioning framing).
  - **Figure set changes**: v6 figures 3–5 (`xtb_3mode_outlier`, `shap_top20_dual`, `7organ_pleiotropy`) are
    withdrawn; new figures 1–2 (`figure1_v03_nnp_redundancy`, `figure2_v03_rank_vs_pearson`) replace them.
  - Suggested version label: `v7 — reproducibility reconstruction (2026-07-21 correction)`.
- **Files to attach**: `manuscript_v0.3_reproducibility.pdf`, `manuscript_v0.3_reproducibility.md`,
  `figures/figure1_v03_*`, `figures/figure2_v03_*`. Do **not** re-attach the withdrawn v6 figures. The SI (σ_E
  sept-matrix, conformal, PoseBusters) may be re-attached as-is (panel-independent).

Version-note text (paste into the Zenodo new-version Description / Additional notes):

> Correction (new version, 2026-07-21) — fabricated ligand-panel annotations and withdrawn repositioning
> narrative. A primary-source audit (2026-07-16) established that the 15-ligand panel underlying this work carries
> fabricated compound names and potency values (all seven named entries are a different molecule than named; 14 of
> 15 structures are unknown to PubChem), and a quantitative-claims audit found the paper's descriptor correlations
> and its repositioning identifications to be unreproducible. This version is a ground-up reconstruction that makes
> no claim about the identity, potency, or therapeutic candidacy of any compound. The original title's
> "repositioning study of Vorinostat and Indapamide" framing is withdrawn in full: the two compounds were
> misidentified and their supporting analyses do not reproduce. What survives, and all this version claims, is the
> reproducibility characterisation of the co-fold → xtb → three-NNP stack (per-cell σ_E, conformal coverage,
> two-arm numeric floor, NNP redundancy). Full scope: `preprints/_metadata/FABRICATED_PANEL_SCOPE_2026_07_16.md`;
> removed-claims ledger: §6.1 of the corrected manuscript.

- **⚠ CRITICAL downstream — JCIM submission linkage (author decision, journal correspondence)**: this record is
  cited as "preprint of record" in an active *J. Chem. Inf. Model.* submission (ID
  `51B8CAD3-7F60-4C3D-AEFD-501DEDC76284`, submitted 2026-06-02). That submitted manuscript **is** the contaminated
  repositioning paper. Superseding the Zenodo record with a differently-titled reconstruction leaves the JCIM
  submission pointing to a record that no longer matches it. The author must decide whether to withdraw or correct
  the JCIM submission. This is outside the Zenodo package and cannot be executed here — flagged for the author.

---

## Author execution checklist (Zenodo new version, per record)

1. Open the record page (`https://zenodo.org/records/20018254` / `…/20247828`) → **New version**.
2. Replace the manuscript file(s) with the corrected PDF + MD above; for XXVI also swap the figure set and update
   the **Title** field to the new title.
3. Paste the version-note text into the version Description / Additional notes.
4. Keep the same concept DOI (a new version DOI mints automatically). License unchanged (CC-BY-4.0). Single author
   (Cheongwoo Han, ORCID 0009-0004-4805-8815).
5. **Publish.** The concept DOI now resolves to the corrected version; the old version stays citable but flagged
   superseded.
6. After publish: record the new version DOIs in `zenodo_upload_log.csv` and `ZENODO_CORRECTION_RESULT_2026_07_19.md`,
   then unblock the recover-clinic page fixes (handoff C-1 / C-2).

## What is NOT done here (author's remaining decisions)
- The actual Zenodo uploads (interactive login).
- The XXVI title change and JCIM submission handling (journal correspondence).
- The #3–#7 dangling-citation cleanup (ripple from Record VIII §3.6 withdrawal).
