# Zenodo deposit correction package — fabricated ligand panel (2026-07-18)

**Author decision (2026-07-16):** *fix the science first, then correct the deposits once the corrected results exist.*
The science fix is now substantially complete (real-121-panel σ_E transfer, σ_iptm discrimination + DUD-E decoy
control, R14 deliverable ledger). This package prepares the deposit corrections. **Author executes the actual
Zenodo uploads** (interactive login); this repo only holds the corrected manuscripts + notes.

## Scope

Three PUBLISHED Zenodo records (2026-05-15) used the fabricated 15-ligand calibration panel
(`data/chembl_mmp1_calibration.csv`). Correction mechanism = **new version under the same concept DOI**
(Zenodo versioned supersede, NOT retraction — the author's choice; supersede preserves citability while
replacing the contaminated content).

| # | concept DOI | title | grade | source manuscript |
|---|---|---|---|---|
| 20 | 10.5281/zenodo.20134439 | The OMol25 Paradox | HIGH (3 names, 10 potency) | `20_paper_A_zn_mmp1_cross_nnp_paradox/manuscript.md` |
| 21 | 10.5281/zenodo.20134442 | Steering potentials … | LOW (0 names, 1 potency) | `21_paper_B_boltz_cofold_use_potentials_protocol/manuscript.md` |
| 22 | 10.5281/zenodo.20134447 | de novo … LigandMPNN | MEDIUM (0 names, 36 potency, false "known inhibitor") | `22_paper_C_zn_metallohydrolase_denovo_pipeline/manuscript.md` |

Two DRAFT (unpublished) manuscripts were also contaminated. Corrected 2026-07-18:
- `08_abfe_methodology/manuscript.md` — DONE. Contamination was localized to §3.6 (Boltz-2-vs-ChEMBL potency
  calibration against fabricated pIC50); §3.6 withdrawn in full (stub), the 3 spillover mentions (Status line,
  §4.1 marimastat parenthetical, revision-history entry) fixed, and a rendered disclosure added under the banner.
  The ABFE core (T4L99A/benzene benchmark, EMB-3 application) is panel-independent and untouched. Verified: 0
  residual named-drug assertions. Ripple to flag: the withdrawn §3.6 calibration was cited by preprints #3–#7
  (herbal/dermatology, themselves panel-CLEAN) as justification that "the Boltz-2 ranking is calibrated at
  |ρ|≈0.72"; that justification is now void and those citations dangle — a separate follow-up.
- `paper_A_zaff_abfe_limitations/manuscript.tex` — PARTIAL, scope decision pending. The scope-file "0 potency"
  grade was wrong: the whole ACCURACY axis (ΔGexp = RT ln IC50; the "reproducibility is not accuracy" thesis;
  sign-flips; potency-class stratification; Figs 2–3) rests on the fabricated potencies. Applied now: a rendered
  provenance+accuracy-axis disclosure after \maketitle, and the keystone false-provenance sentence ("extracted
  from ChEMBL with manual cross-reference to the original literature") corrected. NOT done (deliberately, to
  avoid a misleading half-clean state): the 30 name de-identifications and the accuracy-axis removal/rewrite —
  that is the same restate-as-methodology-vs-re-run-on-real-panel decision paper_A faced, and it is the author's.
  The reproducibility/pipeline content (replicate dispersion, ReplicaExchangeSampler deadlock, NaN-warmup fix,
  NPAtlas xtb cross-method) survives identity-independently.

CLEAN / already handled: `23_paper_A_v6 manuscript_v0.3` (rebuilt, 0 hits), `24_paper_B_v1` (§2.2 rewritten, LOW),
`19_korean_herbal_scaffold_xref` (0 hits).

## Shared correction note (insert into each corrected version, adapt the bracketed finding-type)

> **Correction (version N, 2026-07-18) — fabricated ligand-panel annotations.** After this record was first
> deposited (2026-05-15), a primary-source audit (2026-07-16) established that the 15-ligand calibration panel
> used here (`data/chembl_mmp1_calibration.csv`) carries fabricated compound **names, potency values, and
> literature attributions**. A structure-first PubChem lookup (`scripts/round27_paperA/verify_panel_identity_pubchem.py`)
> finds that **all seven entries naming a specific drug are a different molecule than named** — e.g. the entry
> labelled *prinomastat* is C23H30N2O5S against prinomastat's C18H21N3O5S2 (PubChem CID 466151), and the entry
> labelled *vorinostat* is C13H18N2O5S against C14H20N2O3 (CID 5311); comparison uses the InChIKey connectivity
> block, so stereochemistry and salt form cannot account for it. Separately, **14 of the 15 structures are
> unknown to PubChem** (~119 M compounds). No script in the repository generates the file and it carries no
> retrieval record; a previous automated session produced it and the circumstances are not recoverable.
> **This version removes every compound-identity and potency claim derived from that panel.** What is
> unaffected: the 15 structures parse and sanitise under RDKit and carry zinc-binding chemotypes, and the
> [ENGINE-PROPERTY / PROTOCOL / PIPELINE] finding of this work is a statement about whether a computation
> **repeats on a fixed input** — true or false independent of what the input is named or how potent it is — so
> it stands. Full scope and correction map: `preprints/_metadata/FABRICATED_PANEL_SCOPE_2026_07_16.md`.

## Per-deposit changelog (applied 2026-07-18; the full correction note is the banner at the head of each manuscript.md)

### #20 — The OMol25 Paradox (HIGH) — applied
- §2.1 ligand table replaced with a structure-only table (heavy atoms, formula, net charge, zinc-binding chemotype, all recomputed from the real SMILES by RDKit/SMARTS); drug names (Marimastat, Prinomastat, CGS27023A) and the "Reported IC50" column deleted; ChEMBL ids kept only as unverified structure keys. The stale "22–74 heavy / −1 to 0 charge" range corrected to the true 17–32 heavy, all neutral.
- §3.5 upgraded from "RETRACTION … (size confound)" to "Withdrawn: the pIC50 biology-validation is void — its potency axis is fabricated"; §4.5 object-lesson and §4.6 limitation-4 reframed to match; abstract retraction sentence upgraded from "confounded by ligand size" to "the potency axis was found to be fabricated".
- Identity phrasings in the abstract, §1.4, §2.3 and the §5 conclusion softened from "MMP-1 inhibitors / ChEMBL inhibitors" to "structurally diverse MMP-1-active-site ligands".
- Unaffected: the OMol25-paradox headline and all cross-NNP statistics (Tables 1–4; §3.1–3.4, §3.6–3.9; §2.6 timing).

### #21 — Steering potentials (LOW) — applied
- Title and subtitle "zinc-hydroxamate MMP-1 inhibitors" → "zinc-hydroxamate-like MMP-1 active-site ligands".
- §2.1 selection sentence rewritten to 15 active-site ligand structures under nominal ChEMBL identifiers used as structure handles; the single pIC50 clause and the "all major MMP-1 inhibitor scaffolds" claim removed; identity note added.
- Unaffected: the entire --use_potentials finding, all σ/outlier numbers, both tables, the figure, the recommended protocol.

### #22 — de novo / LigandMPNN (MEDIUM) — applied
- §3.4 false claim "the CHEMBL406 hydroxamate scaffold (a known MMP-1 inhibitor in the ChEMBL database)" removed and reframed as an unverified calibration-panel structure; §2.2/§3.4/§4.4 references to CHEMBL406 and to "15 ChEMBL MMP-1 ligands" reframed as structures of unverified identity; CHEMBL406_* run/file labels kept as opaque artifact keys.
- Unaffected: the LigandMPNN 1HFC recovery headline (95.3% vs 46.4%), ESM-C oracle, the de novo library/MAP-Elites statistics (§3.6), cost table, and the HETATM silent-fallback finding.
- Confirming fact: the repo's own ChEMBL-derived TDC data give CHEMBL406 = an unrelated (indapamide-type) compound, independently refuting the "known inhibitor" claim.

**Verification (2026-07-18):** grep of all three corrected manuscripts confirms no residual "Reported IC50" column, no "(Marimastat/Prinomastat/CGS27023A)" identity assertion, and no "known MMP-1 inhibitor" claim outside the correction note / its negation.

## Author execution checklist (Zenodo new version, per record)
1. Open the record's Zenodo page → "New version".
2. Upload the corrected manuscript (PDF regenerated from the corrected `manuscript.md`).
3. Paste the per-deposit changelog into the version "Description"/"Additional notes".
4. Keep the same concept DOI; a new version DOI mints automatically. License unchanged (CC-BY 4.0).
5. Publish. The concept DOI now resolves to the corrected version; old version stays citable but flagged superseded.
