# Prompt for the Zenodo upload agent — corrected new versions of records #20, #21, #22

You are uploading corrected new versions of FIVE already-published Zenodo records: three substantive
de-identifications (#20, #21, #22) and two lighter dangling-citation fixes (#3, #5). The corrections are
INTEGRITY corrections (a fabricated ligand panel was removed/de-identified, and downstream references to a
withdrawn calibration were cleaned up). Your job is strictly to publish each corrected manuscript as a NEW
VERSION under the record's existing concept DOI — you must not alter the
science, change authorship, or create new records. Author is the sole author Cheongwoo Han (ORCID
0009-0004-4805-8815); license stays CC-BY 4.0.

## Preconditions
- You must be logged in to Zenodo as the account that owns these records (crazat7@gmail.com). If you are not
  authenticated, STOP and ask the human to log in — do not attempt to create parallel records.
- Repository root: /home/crazat/genesis_medicine . All paths below are relative to it.

## For EACH of the five records, do exactly this
1. Open the record's Zenodo page (URL below) and click "New version".
2. Remove the old manuscript file and upload the corrected PDF (path below). Keep any figure/data files that
   were in the original version unless they are listed as withdrawn in the version note.
3. Set the new version's "Additional notes" / description addendum to the VERSION NOTE text below (verbatim).
4. Leave everything else unchanged: same title (except #21, see its note), same authors, same concept DOI,
   CC-BY 4.0. Do NOT mint a new concept DOI.
5. Publish. Record the new version DOI it mints and report it back.
6. Do NOT retract or delete the old version — a versioned supersede is the intended mechanism (author's choice).

After all three: report the three new version DOIs and confirm each concept DOI now resolves to the corrected
version.

---

### Record #20 — "The OMol25 Paradox"
- Concept DOI / page: https://doi.org/10.5281/zenodo.20134439
- Corrected PDF: `preprints/20_paper_A_zn_mmp1_cross_nnp_paradox/manuscript_corrected_2026-07-18.pdf`
- VERSION NOTE: "Corrected version (2026-07-18), fabricated ligand-panel annotations removed. A primary-source
  audit (2026-07-16) established that the 15-ligand calibration panel used here carried fabricated compound
  names, potencies and literature attributions (all seven named entries are a different molecule than named;
  14 of 15 structures are unknown to PubChem). This version replaces the Section 2.1 ligand table with
  structure-only descriptors, deletes the drug names and the reported-IC50 column, retains ChEMBL accessions
  only as unverified structure keys, and withdraws the pIC50 biology-validation (Sections 3.5/4.5) in full. The
  headline OMol25-paradox result and all cross-NNP agreement statistics are unaffected — they are properties of
  computations on fixed structures, independent of compound identity or potency. Versioned correction, not a
  retraction. In silico only."

### Record #21 — "Steering potentials, not bug fixes, ..."
- Concept DOI / page: https://doi.org/10.5281/zenodo.20134442
- Corrected PDF: `preprints/21_paper_B_boltz_cofold_use_potentials_protocol/manuscript_corrected_2026-07-18.pdf`
- TITLE CHANGE: update the record title's tail from "...zinc-hydroxamate MMP-1 inhibitors" to
  "...zinc-hydroxamate-like MMP-1 active-site ligands" (matches the corrected manuscript).
- VERSION NOTE: "Corrected version (2026-07-18), identity disclaimer for a fabricated ligand panel. A
  primary-source audit (2026-07-16) established that the calibration panel's compound names and potencies are
  fabricated. This version softens 'inhibitors' to 'active-site ligands' in the title/subtitle, rewrites the
  Section 2.1 selection sentence to describe 15 structures under nominal ChEMBL identifiers used only as
  structure handles (removing the single pIC50 statement), and adds an identity note. The entire scientific
  result — that the --use_potentials steering flag eliminates catastrophic cofold-pose outliers — is
  unaffected. Versioned correction, not a retraction. In silico only."

### Record #22 — "End-to-end de novo design of Zn metallohydrolase binders ... LigandMPNN"
- Concept DOI / page: https://doi.org/10.5281/zenodo.20134447
- Corrected PDF: `preprints/22_paper_C_zn_metallohydrolase_denovo_pipeline/manuscript_corrected_2026-07-18.pdf`
- VERSION NOTE: "Corrected version (2026-07-18), a fabricated-panel identity misstatement removed. A
  primary-source audit (2026-07-16) established that the referenced calibration panel's annotations are
  fabricated. This version removes the false statement that 'CHEMBL406 [is] a known MMP-1 inhibitor in the
  ChEMBL database' and reframes all references to CHEMBL406 and to the '15 ChEMBL MMP-1 ligands' as
  calibration-panel structures of unverified identity. The headline result (LigandMPNN roughly doubles
  Zn-coordinating-residue recovery on 1HFC, 95.3% vs 46.4%, with ESM-C corroboration), the de novo library and
  MAP-Elites statistics, and the HETATM silent-fallback finding are all unaffected — none use the panel.
  Versioned correction, not a retraction. In silico only."

---

## Lighter dangling-citation fixes (these two only cited the now-withdrawn calibration; no fabricated content of their own)

### Record #3 — "AI-driven scaffold-hopping of Embelia ribes embelin ... (EMB-3)"
- Concept DOI / page: https://doi.org/10.5281/zenodo.20018333
- Corrected PDF: `preprints/03_emb3_scar_case_study/manuscript_corrected_2026-07-18.pdf`
- VERSION NOTE: "Corrected version (2026-07-18). This preprint contains no fabricated panel of its own; it had
  referenced a companion 15-compound MMP-1 calibration (in preprint #8) that has since been withdrawn because
  its panel carried fabricated potencies. Those two references are updated to state that the Boltz-2
  affinity_probability_binary metric is used purely as a relative-ranking signal (consistent with the model's
  reported held-out Spearman of about 0.55–0.65); no other content changes. In silico only."

### Record #5 — "Multi-target evaluation of Korean herbal compounds against SRD5A2 / AR / beta-catenin"
- Concept DOI / page: https://doi.org/10.5281/zenodo.20018339
- Corrected PDF: `preprints/05_alopecia_screening/manuscript_corrected_2026-07-18.pdf`
- VERSION NOTE: "Corrected version (2026-07-18). This preprint contains no fabricated panel of its own; one
  sentence had cited a within-class MMP-1 calibration of |rho| about 0.72 from companion preprint #8 §3.6 as
  support for the Boltz-2 screen. That calibration has been withdrawn (its panel carried fabricated potencies),
  so the citation is removed; the downgrade of the Emodin x AR hit rests on the Chai-1 ensemble disagreement,
  which is unaffected. The n=93 ChEMBL calibration anchor cited elsewhere in the abstract is a different,
  uncontaminated cohort and is unchanged. In silico only."

---

## Guardrails
- If any corrected PDF is missing or unreadable, STOP and report; do not upload a stale/old file.
- Do not edit the manuscript content yourself; upload the provided corrected PDF as-is.
- Do not touch any other Zenodo record. Only #20, #21, #22.
- If Zenodo requires a reason for a metadata/title change, cite "integrity correction; fabricated ligand-panel
  annotations removed (2026-07-16 audit)".
- Full background if needed: `preprints/_metadata/DEPOSIT_CORRECTION_PACKAGE_2026_07_18.md` and
  `preprints/_metadata/FABRICATED_PANEL_SCOPE_2026_07_16.md`.
