# Upload Agent Prompt — OSF Preprints Batch 2 (5-paper supplement, 2026-05-08)

> **Context**: Batch 1 (17 Zenodo-cross-link papers, Group A) is already in progress under `OSF_UPLOAD_AGENT_PROMPT.md`. This file adds **5 more papers** that were excluded from Batch 1. Run this batch **after** Batch 1 reaches Phase 4 (or in parallel if API rate-limit allows).

---

## 1. Mission

Add the following **5 manuscripts** to OSF Preprints, none of which are part of the Batch 1 (17 Zenodo cross-link) scope. The author block, license, COI, IRB caveat, Bepress subjects, and 4-phase workflow are **identical to Batch 1** — re-use the conventions from `OSF_UPLOAD_AGENT_PROMPT.md` §4-§6 verbatim. The differences are scope, file readiness, and cross-deposit disclosure.

The lab principal is **HanCheongWoo (HCW)**, sole author. **Recover Korean Medicine Clinic opens 2026-08-15 (D-99)**; OSF trace must be in place before then.

---

## 2. Scope — 5 papers, 2 groups

### Group B — medRxiv-rejected, no Zenodo record (2 papers)

OSF is the **first** open-access deposit for these. They have `manuscript.pdf` + `manuscript.md` + `_metadata/{N}_*_metadata.json` ready.

| # | Slug | medRxiv submission ID | Reject date |
|---|---|---|---|
| 02 | recover_workflow | `MEDRXIV/2026/351912` | 2026-05-05~08 |
| 11 | korean_pgx_topical | `MEDRXIV/2026/351914` | 2026-05-05~08 |

### Group C — Net-new manuscripts, no prior submission anywhere (3 papers)

OSF is the **canonical** preprint record. File state varies — see "File-build instructions" below.

| Slug | Files present | Files missing | Notes |
|---|---|---|---|
| `19_korean_herbal_scaffold_xref` | `manuscript.md`, `manuscript.html` | `manuscript.pdf` | v0.2 (60 ns MD evidence in body), no figures |
| `paper_A_zaff_abfe_limitations` | `manuscript.tex`, `manuscript.html`, `figures/*.png` | `manuscript.pdf` | v1.0, 14-compound MMP-1 ABFE benchmark, 3 figures |
| `paper_B_xtb_robustness` | `manuscript.tex`, `manuscript.html`, `figures/*.png` | `manuscript.pdf` | v1.0, companion paper to paper_A, 3 figures |

**File-build instructions for Group C** (do once at session start, before Phase 1 of this batch):

For each Group C paper:
1. Try to build PDF: `pandoc manuscript.{md,tex} -o manuscript.pdf --pdf-engine=xelatex` (fallback: `--pdf-engine=weasyprint`).
2. If both engines unavailable on the host, **upload `manuscript.html` as the OSF primary file** (OSF accepts HTML — `text/html` content-type). Do NOT abort the deposit for missing PDF.
3. For paper_A and paper_B, attach the `figures/*.png` files as supplementary OSF files (separate `osfstorage` uploads under the same preprint resource).

---

## 3. Cross-deposit disclosure variants (different per group)

### Group B (#02, #11)

OSF API metadata block:
```json
{
  "original_publication_date": "2026-05-08",
  "external_identifier": null
}
```

Append to the abstract (per-paper substitution):
> **Submission history**: This manuscript was screened by medRxiv (`MEDRXIV/2026/351912` for #02 / `MEDRXIV/2026/351914` for #11) and not selected for posting; the rejection pattern that affected this submission was the screener's "complete research paper requires new wet-lab or clinical patient data" criterion applied to in silico-only manuscripts. OSF is the first open-access record for this manuscript.

### Group C (#19, paper_A, paper_B)

OSF API metadata block:
```json
{
  "original_publication_date": "2026-05-08",
  "external_identifier": null
}
```

No prior-version disclosure needed. For paper_A and paper_B, append a single sentence noting the companion-paper relationship (after both DOIs are minted in Phase 4):
> **Companion paper**: paper_A (ZAFF-AMBER ABFE limitations, OSF DOI `10.31219/osf.io/{guid_A}`) and paper_B (xtb robustness, OSF DOI `10.31219/osf.io/{guid_B}`) form a paired methodology contribution to the Genesis_Medicine preprint series.

This requires a 2-step publish for paper_A/B: first publish paper_B, capture its DOI, then patch paper_A's description to embed paper_B's DOI before publishing paper_A. Or vice versa — order does not matter, but the second-published paper's `description` should reference the first's DOI. Acceptable to skip the cross-cite if it complicates the workflow; flag in the result-handoff if skipped.

The `_metadata/{slug}_metadata.json` files for all 5 papers are already on disk and contain the canonical title, abstract, COI, IRB caveat, and category fields. Read; do not invent.

---

## 4. Re-use Batch 1 conventions

For **everything else** — author block, license (CC-BY 4.0), Bepress subject mapping, OSF API contract (JSON:API v2 endpoints), 4-phase workflow, acceptance criteria, edge cases, authorization & sign-off boundaries — refer to `OSF_UPLOAD_AGENT_PROMPT.md` §4-§10.

The only Batch 2 deviations beyond §2-§3 of this file:

1. **Group C `original_publication_date`** = `2026-05-08` (not `2026-05-04`); reflects the actual OSF deposit date for these net-new manuscripts.
2. **Acceptance criterion #5** (primary file): for Group C, accept either `manuscript.pdf` OR `manuscript.html` as the primary file (OSF supports both); flag in the metadata which format was uploaded.
3. **Acceptance criterion #3** (external_identifier): for Group B/C, accept `null` external_identifier (no Zenodo to cross-link).

---

## 5. Phase boundaries — Batch 2 specific

- **Phase 1** (test deposit): skip — Batch 1 already validated the OSF flow on paper #08. Proceed directly to Phase 2 drafts.
- **Phase 2** (drafts): create 5 drafts (2 Group B + 3 Group C). Save draft URLs to `_metadata/{slug}_metadata.json` under `osf_draft_url`.
- **Phase 3** (per-paper sign-off): hand back to HCW the 5 draft URLs. Wait for green-light list.
- **Phase 4** (publish + record DOI): publish green-lit papers, append `osf_doi`, `osf_url`, `osf_published`, `osf_guid` fields to each `_metadata` file.

After Phase 4 completes, append to (do NOT overwrite) `/home/crazat/genesis_medicine/preprints/OSF_RESULT_HANDOFF.md`:

```markdown
## Batch 2 (5-paper supplement, 2026-05-{DD})

### Group B (medRxiv-rejected, no Zenodo)

| # | Slug | medRxiv ID | OSF DOI | URL |
|---|---|---|---|---|
| 02 | recover_workflow | MEDRXIV/2026/351912 | 10.31219/osf.io/{guid} | https://osf.io/{guid}/ |
| 11 | korean_pgx_topical | MEDRXIV/2026/351914 | 10.31219/osf.io/{guid} | https://osf.io/{guid}/ |

### Group C (net-new, canonical OSF record)

| Slug | OSF DOI | URL | Primary file format |
|---|---|---|---|
| 19_korean_herbal_scaffold_xref | 10.31219/osf.io/{guid} | https://osf.io/{guid}/ | pdf or html |
| paper_A_zaff_abfe_limitations | 10.31219/osf.io/{guid} | https://osf.io/{guid}/ | pdf or html |
| paper_B_xtb_robustness | 10.31219/osf.io/{guid} | https://osf.io/{guid}/ | pdf or html |

### Updated total

| 트랙 | published | rejected | blocked |
|---|---|---|---|
| Zenodo | 17 ✅ | - | - |
| OSF (Batch 1 + 2) | N ✅ | - | M |
| medRxiv | - | 2 ❌ | - |
| bioRxiv | - | 19 ❌ | - |
| ChemRxiv | - | 7 ❌ | - |
```

---

## 6. Hand-off

When ready, confirm receipt of this batch by listing the 5 paper slugs back, then await HCW's go-signal for Phase 2.
