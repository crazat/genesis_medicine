# Dangling-citation audit — the two calibration anchors (2026-07-21)

Follow-up to `FABRICATED_PANEL_SCOPE_2026_07_16.md` and the deposit-correction packages of 2026-07-18 and
2026-07-21. The 07-18 package flagged a ripple: *"the withdrawn §3.6 calibration was cited by preprints #3–#7 …
as justification that the Boltz-2 ranking is 'calibrated at |ρ|≈0.72'; those citations dangle — a separate
follow-up."* This is that follow-up. It is also a correction of that flag, which was imprecise in both
directions.

**Headline:** two different calibration anchors were circulating in the corpus and had been conflated. One is
void. The other is real, reproduces on recomputation, and was being cited for the wrong paper and applied to the
wrong metric. Treating them as one — deleting both, or defending both — would have been wrong either way.

## Anchor A — "|ρ| ≈ 0.72" — VOID

- **What**: Spearman ρ = −0.724 (p = 0.002), Pearson r = −0.762, **n = 15**, Boltz-2 `affinity_pred` vs pIC50.
- **Originally reported**: `08_abfe_methodology` §3.6. The `.md` §3.6 is now a withdrawal stub, so the surviving
  record of the numbers is the stale render `08_abfe_methodology/manuscript.html` (lines 652, 780, 1221).
- **Source data**: `data/chembl_mmp1_calibration.csv` — 15 rows; columns `chembl_id,smiles,ic50_nm,reference,notes`.
  **This is the fabricated panel.** Its potency column and literature attributions are the fabricated material.
- **Status**: withdrawn in full 2026-07-18. Any citation of it as evidence is void.

## Anchor B — "Pearson R = −0.453, n = 93" — REAL, but mis-cited

- **Originally reported**: `18_active_learning_multifidelity/manuscript.md:164`.
- **Source data**: `pilot/cpu_meaningful/chembl_boltz2_calibration.csv` (93 rows), a Boltz-2-joined derivative of
  `pilot/cpu_queue/chembl_mmp1_extended.csv`, which carries **real per-record ChEMBL document identifiers**
  (CHEMBL1130592, CHEMBL1132530, CHEMBL1133789, CHEMBL1134203, CHEMBL1145069, CHEMBL1145787).
- **Recomputed from the file, 2026-07-21**: `affinity_pred_value` vs pIC50 → **Pearson −0.4535, Spearman −0.4582**.
  Reproduces the published −0.453.
- **Provenance positively established** (not merely inferred from the embedded identifiers):
  `scripts/cpu_queue_worker.sh:130-160` performs a live retrieval against
  `https://www.ebi.ac.uk/chembl/api/data/activity.json` with
  `target_chembl_id='CHEMBL321'` (MMP-1 interstitial collagenase), `standard_type='IC50'`,
  `standard_units='nM'`, preserving `document_chembl_id` per record, and writes
  `pilot/cpu_queue/chembl_mmp1_extended.csv`. **This is exactly the "recorded, scripted retrieval" that the
  scope document says the fabricated panel lacks.** The number is sound and the data has genuine provenance.
- **The Anchor A consumer script** is `scripts/boltz2_calibration_mmp1.py` (line 150 defaults `--csv` to the
  fabricated panel; lines 113-120 compute the Spearman/Pearson pair). It *consumes* the fabricated CSV; it does
  not generate it — consistent with the scope document's finding that no script generates that file.
- Note: the 07-18 package's path `data/chembl_mmp1_extended.csv` is imprecise — the file lives under
  `pilot/cpu_queue/`.

**But two independent defects in how it was cited:**

1. **Broken attribution.** Preprints #4, #5, #13, #15 credited the figure to *"preprint #8"* or to *"the parallel
   MMP-1 calibration set"*. The string `0.453` occurs **zero times** in `08_abfe_methodology/manuscript.md` and
   zero times in its `.html`. Preprint #8 never reported it — #8's calibration was the n=15 fabricated one. So
   these citations pointed at the withdrawn section while quoting a number that came from #18. The wording also
   read as though the anchor came from the fabricated panel, which it did not.

2. **Metric mismatch — substantive.** −0.453 was measured on `affinity_pred_value`. The screens rank on
   `affinity_prob_binary`. Recomputed on the same 93 rows: `affinity_prob_binary` vs pIC50 →
   **Pearson +0.178, Spearman +0.048** — no ranking ability. The abstracts of #4 and #5 used −0.453 to certify
   that `affinity_probability_binary` is a validated relative-ranking predictor. It never measured that metric.
   The rankings are relative and **uncalibrated**; corrected wording now says so.

## Fixes applied 2026-07-21

| preprint | line | anchor | what was wrong | fix |
|---|---|---|---|---|
| `08_abfe_methodology` (`manuscript.md` + `manuscript_v0.9_corrected_deposit.md`) | 257 / 234 | A | *"the Boltz-2-alone signal is still calibrated against ChEMBL (§3.6)"* — the file cites the section it itself withdrew | ground withdrawn explicitly; retained on the weaker relative-ranking claim only |
| `12_open_source_perspective` | 296 | A | *"ChEMBL ρ=0.72 calibration"* credited as a headline system contribution | removed from the contribution list |
| `03_emb3_scar_case_study` | 221 | A | future-work item promising *"Boltz-2 calibration on the 15-compound ChEMBL MMP-1 inhibitor panel (in progress)"* | replaced: panel withdrawn; any replacement needs a recorded, scripted retrieval |
| `04_pigmentation_screening` | 28 (abstract) | B | wrong attribution + certifies the wrong metric | re-attributed to #18 + named the file; states the ranking metric is uncalibrated |
| `05_alopecia_screening` | 28 (abstract) | B | same | same |
| `13_piezo1_mlck_alopecia` | 65 | B | *"carried over from MMP-1 study"* — ambiguous between the fabricated panel and the real cohort | names the real cohort and the metric |
| `15_universal_scaffold` | 597 | B | *"r = −0.453 (preprint #8)"* — #8 never reported it | re-attributed to #18 |

Each corrected manuscript carries a `<!-- correction-2026-07-21 -->` banner stating what changed. **No result,
ranking, or figure value changes anywhere.** These are provenance and scope-of-claim corrections.

## Scope corrections to the 2026-07-18 ripple flag

- **"#3–#7" was overstated.** `06_acne_microbiome` and `07_photoaging_egcg` carry **no anchor citation at all**
  — #6's only `calibrat` hit is a bibliography entry, #7 has none. Neither needed a correction and neither was
  touched.
- **"#3–#7" also under-reached.** The void Anchor A was additionally cited by `12_open_source_perspective`, and
  the mis-cited Anchor B by `13_piezo1_mlck_alopecia` and `15_universal_scaffold` — none of which were in the
  flagged range.
- **Already handled, no action**: `05_alopecia_screening:208` (carries an explicit inline |ρ|≈0.72 withdrawal
  from the 07-18 pass) and `03_emb3_scar_case_study:193`.
- **False positives, no action**: `16`, `17`, `43` (`0.72` as affinity/RMSD values); `20`, `22` (`0.72x` are
  cross-NNP correlation-matrix cells, unrelated to pIC50; both already carry 07-18 banners); `18` (origin of
  Anchor B, correctly sourced); `24` (full disclosure at line 49).

## Known-remaining, not fixed here

- **Stale `.html` renders.** `08_abfe_methodology/manuscript.html` still carries the full withdrawn §3.6
  including the ρ = −0.724 numbers. It is not a deposited artifact, but it is the last surviving copy of those
  figures and should be regenerated or clearly marked.
- **Stale companion citations** (hygiene, not integrity): manuscripts cite companion works as *"ChemRxiv
  preprint, 2026"* or *"forthcoming"*. ChemRxiv rejected all seven; the real records are on Zenodo/OSF and the
  DOIs are in `CLAUDE.md`. Affected: `01:171`, `02:50`, `03:238/326/357`, `04:205`, `05:198/200`, `06:185/186`,
  `07:163/164`, `09:206/209`, `12:233/234`. (`20:478` cites an external forthcoming Boltz-2x paper — leave.)
- **Two distinct "n=93" cohorts.** #18's file is 91 `=` + 2 censored `>` records; #24 describes its n=93 as the
  95-row extended set minus the 2 censored records. Both are n=93 by construction, not identity. Do not treat
  them as interchangeable.
- **No generating script found** for either CSV. The fabricated panel's lack of a generator is established. For
  the extended/Boltz-2 CSVs the evidence of authenticity is the embedded ChEMBL document IDs, **not** a recorded
  retrieval script — so their provenance is strong but not scripted. A future re-derivation should record it.
- **`paper_A_zaff_abfe_limitations`** remains at the PARTIAL correction state set on 2026-07-18; its
  accuracy-axis rewrite is an open author decision and was not touched here.

## ⚠ Live-pipeline exposure — beyond the publication record, NOT yet remediated

The publication record is now corrected, but **the fabricated panel is still wired into the executable
pipeline**. `data/chembl_mmp1_calibration.csv` is a declared Snakemake input (`Snakefile:26` and `:83`) and is
read by at least nine scripts:

- `scripts/boltz2_calibration_mmp1.py` (the withdrawn Anchor A calculation itself)
- `scripts/dude_decoy_benchmark.py:48`
- `scripts/dude_xtb_score_actives_decoys.py:24`
- `scripts/dude_xtb_refine_432_actives_decoys.py:29`
- `scripts/abfe_benchmark_prepare.py:41`
- `scripts/round27_paperA/anchor_sigma_ic50_analyze.py:87`
- four `scripts/round12/*` jobs

**Any re-run of the Snakefile still ingests fabricated potency data**, which would regenerate contaminated
results downstream of a record that has just been corrected. Partial remediation exists in exactly one place:
`scripts/round27_paperA/build_decoy_panel_zinc.py:13` notes *"The old actives do not exist."*

Recommended remediation, in order: (1) rename the file to `chembl_mmp1_calibration.WITHDRAWN.csv` or move it to
a quarantine directory so every consumer fails loudly rather than silently computing on fabricated potency;
(2) triage the nine consumers — those that need only structures may be repointed at
`data/mmp1_panel_pubchem.csv` (121 compounds with per-row PubChem CID, assay AID and retrieval timestamp),
those that need potency have no valid input and should be disabled; (3) remove it from the Snakefile inputs.
This is code remediation, not a deposit correction, and was not attempted in this pass.


## Deposit corrections applied (2026-07-21)

All seven corrected manuscripts were superseded on Zenodo (new version under the same concept DOI) and updated
on OSF (corrected PDF uploaded as a new file version; node DOI unchanged). All seven concept DOIs verified to
resolve to the corrected version.

| preprint | Zenodo concept DOI | new version DOI | OSF GUID (new file version) |
|---|---|---|---|
| #3  | 10.5281/zenodo.20018332 | 10.5281/zenodo.21466637 | vk5e9 (v3) |
| #4  | 10.5281/zenodo.20018336 | 10.5281/zenodo.21466642 | hdxv3 (v2) |
| #5  | 10.5281/zenodo.20018338 | 10.5281/zenodo.21466645 | nkzxb (v2) |
| #8  | 10.5281/zenodo.20018253 | 10.5281/zenodo.21466648 | tmhev (v3) |
| #12 | 10.5281/zenodo.20018342 | 10.5281/zenodo.21466649 | eh2f7 (v2) |
| #13 | 10.5281/zenodo.20018377 | 10.5281/zenodo.21466653 | kmh4y (v2) |
| #15 | 10.5281/zenodo.20018348 | 10.5281/zenodo.21466656 | rnxs9 (v2) |

Tooling: `C:\Users\craza\zenodo_correct_orchestrate_v3.py` (prep|verify|publish),
`C:\Users\craza\osf_correct_citations_2026_07_21.py` (inspect|apply, reuses the Zenodo note text verbatim so
both platforms carry the same statement), `C:\Users\craza\apply_banner_build_2026_07_21.py` (banner insert +
weasyprint rebuild).
