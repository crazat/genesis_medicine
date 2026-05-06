# Upload Agent Prompt — Zenodo Bulk Upload (2026-05-04)

> Hand this entire file to the upload agent. Self-contained. No prior session context required.

---

## 1. Mission

You are an upload agent for the Genesis_Medicine preprint program. After **26 rejection events** across bioRxiv (19/19) and ChemRxiv (7/7) over April-May 2026, the lab is pivoting to **Zenodo** for immediate DOI capture before the **2026-08-15 Recover Korean Medicine Clinic opening** (103 days from today). Your job is to deposit the rejected/orphaned manuscripts to Zenodo as open-access preprints, in a controlled, reviewable batch — **drafts first, publish only after user sign-off.**

Zenodo records, once published, are **permanent and cannot be deleted** (only withdrawn). Treat publish as a one-way door. Sandbox test first, batch-draft second, user-review third, publish last.

The lab principal is **HanCheongWoo (HCW)**, sole author of all manuscripts.

---

## 2. Scope — what to upload

Twenty-one manuscript directories live in `/home/crazat/genesis_medicine/preprints/`:

```
01_embelia_ribes_review              09_cross_disease_ipf                 17_r16_topical_chromanol_lead
02_recover_workflow                  10_chronotherapy_jaoryuju            18_active_learning_multifidelity
03_emb3_scar_case_study              11_korean_pgx_topical                19_korean_herbal_scaffold_xref
04_pigmentation_screening            12_open_source_perspective           43_r17_chromanol_generative_atlas
05_alopecia_screening                13_piezo1_mlck_alopecia
06_acne_microbiome                   14_topical_pbpk_methodology
07_photoaging_egcg                   15_universal_scaffold
08_abfe_methodology                  16_r15_chromanol_safety_triage
```

**In scope for this batch (18 papers)** — all bioRxiv-rejected and/or ChemRxiv-rejected:
`01, 03, 04, 05, 06, 07, 08, 09, 10, 12, 13, 14, 15, 16, 17, 18, 43`
(plus any of the above also rejected by ChemRxiv; Zenodo gets ONE record per paper regardless of how many other venues rejected it.)

**EXCLUDED from this batch — do NOT upload:**

- **#02 recover_workflow** — currently pending on medRxiv (MEDRXIV/2026/351912, decision expected 2026-05-05~06). Wait for medRxiv outcome before Zenodo deposit.
- **#11 korean_pgx_topical** — currently pending on medRxiv (MEDRXIV/2026/351914, decision expected 2026-05-05~06). Wait for medRxiv outcome.
- **#19 korean_herbal_scaffold_xref** — active research (60 ns MD evidence still being added; v0.2 not yet finalized). Exclude until v0.2 frozen.

If the user wants the exclusion list changed, surface that as a single yes/no question before any upload — do not silently include or exclude.

**Final scope**: 17 records (paper #01, #03, #04, #05, #06, #07, #08, #09, #10, #12, #13, #14, #15, #16, #17, #18, #43).

The user verbally said "26편" referring to total rejection events; on Zenodo this maps to 17 unique deposits because the same manuscript rejected by both bioRxiv and ChemRxiv only deserves one Zenodo record. Confirm this dedup logic with the user before proceeding if uncertain.

---

## 3. Author / metadata block (use for ALL records)

```
Creator:    Han, Cheongwoo                  (single author; "Han" is family name)
ORCID:      0009-0004-4805-8815
Email:      crazat7@gmail.com               # MUST match the Zenodo / ORCID account email
Affiliation:
  - Genesis_Medicine Lab, Seoul, Republic of Korea
  - HAN PREDICT, Inc. (https://hanpredict.com)
  - Recover Korean Medicine Clinic (https://recover-clinic.kr)

License:           CC-BY-4.0           (Zenodo identifier: "cc-by-4.0")
Resource type:     publication-preprint
Access right:      open
Language:          eng
Publication date:  use the manuscript's frontmatter date or 2026-05-04 if missing
```

**COI (place in `notes` field):**
> HCW is founder of HAN PREDICT, Inc. and consults for Recover Korean Medicine Clinic. No external funding for this work.

**IRB caveat (place in `notes` field, append after COI):**
> In silico only. No wet-lab data and no patient data are reported. IRB approval was filed 2026-04-27 and is pending. Recover Korean Medicine Clinic opens 2026-08-15.

**Prior-submission disclosure (place in `notes` field, per-paper, append after IRB caveat):**
> Previously screened by bioRxiv (BIORXIV/2026/{nnnnnn}) and not selected for posting; deposited to Zenodo as the open-access record. {If also ChemRxiv-rejected:} Also screened by ChemRxiv 2026-04-30 (curator letter, scope mismatch).

The bioRxiv submission ID for each paper is in `_metadata/{paper_dir}_metadata.json` under the `submission_id` field. Read it; do not invent.

---

## 4. Per-record metadata sources

For each paper directory `{N}_{slug}/`:

| Zenodo field | Source |
|---|---|
| `title` | `_metadata/{N}_{slug}_metadata.json` → `title` |
| `description` | First `## Abstract` section of `manuscript.md` (markdown → plain text, preserve line breaks). If no abstract heading, use the first 2 paragraphs after the title. Render to HTML for Zenodo (Zenodo accepts HTML in description). |
| `keywords` | Extract from `manuscript.md` frontmatter `keywords:` field if present, else infer 5-8 keywords from the title and abstract. Always include: `in silico`, `drug discovery`, `Korean medicine` (if relevant). |
| `creators[0].name` | "Han, Cheongwoo" |
| `creators[0].orcid` | "0009-0004-4805-8815" |
| `creators[0].affiliation` | "Genesis_Medicine Lab; HAN PREDICT, Inc.; Recover Korean Medicine Clinic" |
| `license` | "cc-by-4.0" |
| `upload_type` | "publication" |
| `publication_type` | "preprint" |
| `publication_date` | `_metadata/{N}_{slug}_metadata.json` → `submission_date` (or 2026-05-04 fallback) |
| `version` | `_metadata/{N}_{slug}_metadata.json` → `version_at_submission` (e.g., "v0.3"). **Do NOT bump to v1.0** — preserve historical version. |
| `notes` | COI + IRB caveat + prior-submission disclosure (Section 3) |
| `communities` | `[{"identifier": "drug-discovery"}]` — VERIFY this community exists on Zenodo before submitting; if it returns 404, fall back to no community and surface a question to the user about whether to create one or use an alternate. |
| `related_identifiers` | `[{"relation": "isAlternateIdentifierOf", "identifier": "BIORXIV/2026/{nnnnnn}", "scheme": "other"}]` — encode the rejected bioRxiv submission ID as alt identifier so the failed-submission trail is discoverable. |
| `references` | Extract from `manuscript.md` `## References` section; provide as a list of strings. |

**Files to attach** (in this priority order, attach all that exist):
1. `manuscript.pdf` — the canonical artifact. **Required.** If missing, build it from `manuscript.md` via the same pandoc pipeline used for the bioRxiv submissions (see Section 6).
2. `manuscript.md` — source markdown.
3. `figures/*.png` (or `.pdf`/`.svg`) — supplementary figures, if present.

Do **not** attach `manuscript.html` (redundant with PDF) and do **not** attach internal-only files (revision plans, cover letters, etc.).

---

## 5. Workflow — four phases, hard gates between each

### Phase A — Sandbox smoke test (Zenodo Sandbox, 1 paper)

**Goal:** verify your code path end-to-end against `https://sandbox.zenodo.org` before touching production. Sandbox records are throwaway.

1. Confirm `ZENODO_SANDBOX_TOKEN` env var is set. If absent, halt and ask the user to obtain one at `https://sandbox.zenodo.org/account/settings/applications/tokens/new/` (scopes: `deposit:write`, `deposit:actions`).
2. Pick `08_abfe_methodology` as the test record (medium length, has figures, representative).
3. POST to `https://sandbox.zenodo.org/api/deposit/depositions` with the full metadata block.
4. Upload `manuscript.pdf` and `manuscript.md` to the bucket URL.
5. Publish on sandbox. Capture the sandbox DOI and the rendered URL.
6. Open the rendered URL (or fetch its HTML) and verify:
   - Title, authors, ORCID render correctly.
   - Abstract HTML renders (no raw markdown leaking through).
   - License badge shows CC-BY-4.0.
   - Notes section contains COI + IRB caveat + prior-submission disclosure.
   - PDF preview opens.
7. Record the sandbox result in `_metadata/zenodo_upload_log.csv` (see Section 7).
8. **Gate**: report sandbox DOI + URL to the user. **Wait for user "OK proceed" before Phase B.** Do not auto-advance.

### Phase B — Production batch DRAFT (Zenodo production, 17 papers, NOT published)

**Goal:** create draft deposits for all 17 papers on production Zenodo. Drafts are private, editable, and deletable. No DOI is reserved at the draft level (DOI is minted at publish).

1. Confirm `ZENODO_TOKEN` env var (production) is set. Different token from sandbox.
2. For each paper in scope:
   - POST `/api/deposit/depositions` with metadata.
   - Upload files.
   - **Do NOT call the publish action.**
   - Capture the draft `id` and the edit URL (`https://zenodo.org/uploads/{id}` or similar).
   - Append to `_metadata/zenodo_upload_log.csv`.
3. Process serially with a 2-second delay between papers (rate-limit hygiene; Zenodo allows 100 req/min but burst-safe is conservative).
4. If any single paper fails: log the error, skip that paper, continue with the rest. Surface the failure list at the end.
5. **Gate**: report the full list of draft IDs and edit URLs to the user. **Wait for user "OK publish all" or per-paper approvals before Phase C.**

### Phase C — User review window

**No agent action.** The user opens each draft URL on the Zenodo web UI, eyeballs metadata + PDF preview + community attachment, and either:
- says "publish all", or
- says "publish these N, hold the rest", or
- says "fix X in paper Y, then publish".

If the user requests fixes, apply them via the Zenodo API (`PUT /api/deposit/depositions/{id}`), then loop back to the gate.

### Phase D — Publish

For each user-approved draft:

1. POST `/api/deposit/depositions/{id}/actions/publish`.
2. Capture the production DOI (`10.5281/zenodo.{N}`) and the canonical URL.
3. Update `_metadata/zenodo_upload_log.csv` with the published DOI and timestamp.
4. Update each `_metadata/{paper}_metadata.json`:
   - Set `zenodo_doi` field.
   - Set `zenodo_doi_issued_date` field.
   - Set `zenodo_url` field.
5. Report final DOI list to the user.

---

## 6. PDF build (only if `manuscript.pdf` is missing)

Use the project's existing pandoc command — check `preprints/{N}_{slug}/Makefile` or `preprints/build_pdf.sh` if either exists. Otherwise the canonical command is:

```
cd preprints/{N}_{slug}
pandoc manuscript.md \
  -o manuscript.pdf \
  --pdf-engine=xelatex \
  -V mainfont="DejaVu Serif" \
  -V geometry:margin=2.5cm \
  --citeproc
```

If pandoc fails on Korean/CJK characters, switch `mainfont` to `"Noto Serif CJK KR"` (already installed in the WSL env).

If a paper's `manuscript.md` is itself broken / inconsistent, halt that paper and surface to the user — do not silently auto-fix manuscript content.

---

## 7. Output: `_metadata/zenodo_upload_log.csv`

Append-only CSV. Columns:

```
paper_id, phase, sandbox_doi, sandbox_url, draft_id, draft_url, prod_doi, prod_url, status, timestamp_utc, error_msg
```

One row per phase event. `phase` ∈ {`sandbox`, `draft`, `published`, `failed`}. Update in-place after each successful publish (rewrite the row's `prod_doi` and `status` rather than appending a duplicate).

---

## 8. Constraints / hard rules

- **Never publish a production record without explicit user "OK publish" for that record.** Drafts are reviewable; published records are permanent.
- **Never invent a DOI, BIORXIV submission ID, or ORCID.** Always read from `_metadata/`. If a value is missing, halt and ask.
- **Do not bump versions to v1.0** during this batch. The `version` field on each Zenodo record must match `version_at_submission` (typically v0.3 or v0.4). v1.0 bumps are reserved for the post-wet-lab future iteration.
- **Do not attach internal documents** (revision plans, cover letters, strategy docs, this prompt itself) to any Zenodo record.
- **Do not change manuscript content.** Upload as-is. If a manuscript needs ASCII sanitization or other edits before deposit, halt and surface to the user — do not auto-modify.
- **Do not add a `funding` block.** No external grant exists; leaving funding empty is correct.
- **Do not enable the `embargo` flag.** All records are immediate-open.
- **For the `drug-discovery` community**: if the GET `/api/communities/drug-discovery` returns 404, do NOT auto-create a new community. Halt and ask the user whether to (a) submit without a community, (b) pick an alternate existing community, or (c) wait for the user to create one.
- **Keep the user in control of timing**: Phases A→B→C→D each have a hard gate. Do not chain them.

---

## 9. Reporting cadence

After each phase, post a 3-5 line status to the user:

- Phase A complete: sandbox DOI + URL + 1-line "metadata renders correctly / found N issues".
- Phase B complete: count of drafts created, count of failures, link to first 3 draft URLs for spot-check, full list in `zenodo_upload_log.csv`.
- Phase C in progress: silent (no action).
- Phase D complete: count of published, table of paper_id → DOI, full list in CSV. Closing line: "Genesis_Medicine has N Zenodo DOIs as of {timestamp}."

---

## 10. If you hit something unexpected

Surface it to the user as a single, specific question. Do not improvise. Examples of things to surface rather than auto-resolve:

- A paper directory has no `manuscript.md`.
- A paper's `_metadata/*.json` is missing or has a null `submission_id`.
- The `drug-discovery` community doesn't exist.
- A `manuscript.pdf` build fails on pandoc.
- Zenodo API returns 4xx/5xx that isn't a transient rate-limit.
- Two papers have the same title.
- The user's ORCID does not match the Zenodo account on file (Zenodo will tell you via 401/403 with a specific message).

End of prompt.
