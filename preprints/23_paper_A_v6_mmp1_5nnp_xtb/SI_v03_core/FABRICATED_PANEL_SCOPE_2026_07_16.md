# Fabricated ligand panel — contamination scope and correction map (2026-07-16)

## What happened

`data/chembl_mmp1_calibration.csv` (2026-05-06, 15 rows, 1,779 bytes) carries ChEMBL identifiers, potency
values and literature attributions ("prinomastat (AG3340); Shalinsky 1999", "Batimastat (BB-94); Brown 1995",
…). **The structures in it are not those compounds, and appear not to be any published compounds.**

Established against a primary source (PubChem REST, `scripts/round27_paperA/verify_panel_identity_pubchem.py`):

| Claimed | PubChem CID | PubChem formula | Panel formula | Same molecule? |
|---|---|---|---|---|
| marimastat | 119031 | C15H29N3O5 | **C15H29N3O5** | **NO** — formula matches, skeleton differs |
| batimastat | 5362422 | C23H31N3O4S2 | C21H33N3O5 | NO |
| ilomastat | 132519 | C20H28N4O4 | C11H21N3O4 | NO |
| prinomastat | 466151 | C18H21N3O5S2 | C23H30N2O5S | NO |
| CGS 27023A | 9888897 | C18H24ClN3O5S | C22H18N2O4S | NO |
| vorinostat | 5311 | C14H20N2O3 | C13H18N2O5S | NO |
| RS-130830 | 3342298 | C19H20ClNO6S | C25H25FN2O4 | NO |

**7 of 7 named compounds are a different molecule.** Separately, an exact-structure lookup finds **14 of the
15 panel structures are unknown to PubChem** (~119 M compounds) — they are not published chemistry. Skeleton
comparison uses the connectivity block of the InChIKey, so stereochemistry and salt form cannot explain it.

Marimastat is the diagnostic case: the molecular formula is exactly right and the skeleton is wrong. A
transcription error does not produce that. It is the signature of a structure written to fit a formula.

No script generates the file; it contains no API-retrieval record; its identifiers intersect neither
ChEMBL-derived cohort held in this repository. The author's account (2026-07-16) is that a previous session of
this assistant produced it. **Neither the user nor the assistant recalls the circumstances, and no record of
them survives. Do not reconstruct a motive — record the fact and the date.**

Not established: whether the ChEMBL identifiers themselves are real. The EBI API is unreachable from this host
(`status.json` times out; the webresource client fails on `/spore` with HTTP 500), so "what is CHEMBL406 in
ChEMBL" is still unanswered. What is answered: the structure filed under it is not the drug the file names.

## What survives regardless

Every reproducibility claim. σ_iptm, σ_E, cross-NNP agreement, conformal coverage, the numeric floor, solvent
robustness and selection robustness are all statements about **whether a computation repeats on a fixed
input** — true or false independent of what that input is or how potent it is. The compute (37,500 + 241,500
structures) ran honestly on real, parseable molecules; only their names and potencies are fiction.

What dies: compound identity, potency, "known MMP-1 inhibitor", any structure–activity or repositioning claim,
and any figure or table that asserts them.

## Correction map

Severity is graded by whether the paper *asserts* identity/potency or merely *uses* the structures.

| Where | Status | Panel hits | Names asserted | Potency asserted | Grade |
|---|---|---|---|---|---|
| **#20** `10.5281/zenodo.20134439` "The OMol25 Paradox" | **PUBLISHED 2026-05-15** | 11 | 3 (Prinomastat, Marimastat, CGS27023A) | 10 | **HIGH** — a table states `CHEMBL406 (Prinomastat) | 3 nM | sulfonamide-hydroxamate`. The OMol25-paradox finding itself is a property of the engines and can survive re-framing. |
| **#21** `10.5281/zenodo.20134442` "Steering potentials…" | **PUBLISHED 2026-05-15** | 12 | 0 | 1 | **LOW** — lists the 15 identifiers but asserts no names; the `--use_potentials` protocol claim is about the computation. Likely fixable by an identity disclaimer. |
| **#22** `10.5281/zenodo.20134447` "…de novo design…" | **PUBLISHED 2026-05-15** | 6 | 0 | 36 | **MEDIUM** — asserts "CHEMBL406 hydroxamate scaffold (**a known MMP-1 inhibitor in the ChEMBL database**)", which is false. Most of its 36 potency mentions belong to other cohorts and must be triaged individually. |
| `08_abfe_methodology` | draft | 6 | **10** (all six drug names) | 39 | **HIGH** — heaviest name-assertion density of any manuscript. |
| `paper_A_zaff_abfe_limitations` | draft | 20 | **20** | 0 | **HIGH** — names throughout, no potency. |
| `23_paper_A_v6` v0.1 / v0.2 / JCIM | draft | 2 / 19 / 18 | yes | yes | **SUPERSEDED** by `manuscript_v0.3_reproducibility.md` (0 hits), which was rebuilt to claim neither identity nor potency. |
| `24_paper_B_v1` | draft | 54 | 0 (fixed 2026-07-16) | §3.10 only, from a clean cohort | **LOW** — §2.2 rewritten; the n=93 anchor uses `chembl_mmp1_extended.csv`, which carries real per-record document identifiers and is unaffected. |
| `19_korean_herbal_scaffold_xref` | draft | **0** | — | — | **CLEAN** |

## Order of work

The published record is not a reason to defer the underlying work (author's decision, 2026-07-16): fix the
science first, then correct the deposits once the corrected results exist. Zenodo supports versioned updates
under a stable concept DOI, so #20/#21/#22 can be superseded rather than retracted, if the author so chooses.
That choice is the author's alone and is not made here.

Prerequisite for any correction that wants its potency axis back: re-derive a ligand panel from a **recorded,
scripted retrieval**. That is blocked today by EBI being unreachable; PubChem is reachable and is a viable
alternative source for structures and identity, though not for ChEMBL activity records.

## Reproduce

```
python scripts/round27_paperA/verify_panel_identity_pubchem.py   # identity, structure-first, vs PubChem
```
Output: `preprints/23_paper_A_v6_mmp1_5nnp_xtb/SI/panel_identity_pubchem_verification.csv`
