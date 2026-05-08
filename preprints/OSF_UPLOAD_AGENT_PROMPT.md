# Upload Agent Prompt — OSF Preprints Bulk Cross-Post (2026-05-08, FULL 22-paper scope)

> Hand this entire file to the upload agent. Self-contained. No prior session context required.

---

## 1. Mission

You are an upload agent for the Genesis_Medicine preprint program. After the **April-May 2026 rejection wave** (bioRxiv 19/19, ChemRxiv 7/7, medRxiv 2/2 — all in-silico-only screening rejected), the Genesis program now consists of three categories of manuscripts:

1. **17 already-Zenodo papers** with permanent DOIs `10.5281/zenodo.20018254`–`20018378` (deposited 2026-05-04 after the bioRxiv/ChemRxiv rejection wave).
2. **2 medRxiv-rejected papers** (#02, #11) that did not receive a Zenodo deposit and have only the medRxiv submission ID as prior trace.
3. **3 net-new manuscripts** (#19, paper_A, paper_B) authored 2026-05-04 through 2026-05-08, never submitted to any venue, requiring a fresh OSF deposit as their canonical preprint record.

Genesis is now consolidating the academic trace by **cross-posting all 22 manuscripts to OSF Preprints** — the Center for Open Science hosting service with **no editorial review** (it is a deposit service, not a peer-review platform).

OSF Preprints deposits are **free** (no APC), assigned a **Crossref DOI** automatically (`10.31219/osf.io/{guid}` form), and indexed by Google Scholar / OpenAIRE within 24-72 hours. This is the preferred Option B from `POST_REJECTION_STRATEGY.md` — the cheapest, fastest action that materially adds OSF-indexed academic trace to all 22 papers without any editorial gating.

The lab principal is **HanCheongWoo (HCW)**, sole author of all manuscripts.

The **Recover Korean Medicine Clinic opens 2026-08-15 (D-99 from today)**. OSF trace must be in place before clinic launch so external readers can cite the work alongside the Zenodo records.

---

## 2. Scope — what to upload

Source of truth: `/home/crazat/genesis_medicine/preprints/_metadata/{N}_{slug}_metadata.json` (one file per paper). All 22 metadata files exist on disk as of 2026-05-08; if any are missing, abort and report.

### Group A — 17 Zenodo-cross-link papers

These have full Zenodo records and `manuscript.pdf` files. Cross-deposit disclosure cites the Zenodo DOI as `isVersionOf`.

```
01 embelia_ribes_review              13 piezo1_mlck_alopecia
03 emb3_scar_case_study              14 topical_pbpk_methodology
04 pigmentation_screening            15 universal_scaffold
05 alopecia_screening                16 r15_chromanol_safety_triage
06 acne_microbiome                   17 r16_topical_chromanol_lead
07 photoaging_egcg                   18 active_learning_multifidelity
08 abfe_methodology                  43 r17_chromanol_generative_atlas
09 cross_disease_ipf
10 chronotherapy_jaoryuju
12 open_source_perspective
```

### Group B — 2 medRxiv-rejected papers (no Zenodo record)

These have `manuscript.pdf` but no Zenodo DOI. Cross-deposit disclosure cites the medRxiv submission ID and rejection note instead. Treat OSF as the **first** open-access record for these two.

```
02 recover_workflow              # MEDRXIV/2026/351912, rejected 2026-05-05~08
11 korean_pgx_topical            # MEDRXIV/2026/351914, rejected 2026-05-05~08
```

### Group C — 3 net-new manuscripts (no prior submission)

These have **no prior submission** at any venue. Treat OSF as the **canonical** preprint record. Of these, the file states differ:

```
19 korean_herbal_scaffold_xref   # manuscript.md + manuscript.html exist; manuscript.pdf MISSING
paper_A_zaff_abfe_limitations    # manuscript.tex + manuscript.html exist; manuscript.pdf MISSING; figures/*.png present
paper_B_xtb_robustness           # manuscript.tex + manuscript.html exist; manuscript.pdf MISSING; figures/*.png present
```

**Final scope: 22 records.**

**File-build instructions for Group C** (do once at session start, before Phase 1):

For each Group C paper:
1. If `manuscript.pdf` is missing, build it via the most-available engine:
   - First try: `pandoc manuscript.{md,tex} -o manuscript.pdf --pdf-engine=xelatex`
   - If xelatex/pdflatex unavailable: `pandoc manuscript.{md,tex} -o manuscript.pdf --pdf-engine=weasyprint`
   - If both unavailable: upload `manuscript.html` as the OSF primary file (OSF accepts HTML).
2. If figures are referenced (paper_A/B), include the `figures/` directory in the OSF upload bundle.
3. Verify the built file is non-empty and renders the title block + abstract + first results table correctly before proceeding.

**File state for Group A and Group B**: all 19 papers already have `manuscript.pdf` confirmed. No build step needed.

If HCW asks to add or remove papers from the scope, surface that as a single yes/no question and do not silently change the list.

---

## 3. Why OSF Preprints specifically

| Feature | OSF Preprints | Zenodo (current) | Qeios | F1000Research |
|---|---|---|---|---|
| Cost | **$0** | $0 | $0 | $1,500/paper |
| Editorial gating | **none (hosting)** | none | none | yes |
| DOI minted | yes (Crossref `10.31219/...`) | yes (`10.5281/...`) | yes (`10.32388/...`) | yes |
| Search-indexed | **Google Scholar, OpenAIRE, BASE** | Google Scholar, BASE | Google Scholar | Google Scholar, PubMed |
| Time to live | **24-72 h** | already live | 24-48 h | 4-8 weeks |
| Provider taxonomy | **bepress (~1900 subjects)** | open keywords | open keywords | curated subjects |
| Embargo support | yes (date-based) | yes | no | no |
| Versioning | yes | yes | yes | yes |

OSF Preprints is the right choice because:
1. **Zero cost** for all 17 papers, no APC budget consumption.
2. **Pure hosting** — no scope rejection risk (the rejection that killed bioRxiv/ChemRxiv/medRxiv attempts).
3. **Bepress taxonomy** matches Genesis's interdisciplinary scope better than Qeios's open keywords (Pharmacology, Computational Biology, Medicinal Chemistry, Korean Traditional Medicine all have curated paths).
4. **OSF ecosystem** — Genesis can later upgrade individual records to full OSF Projects (with code/data linked), and OSF integrates with Open Science Framework's preregistration system if Genesis wants to pre-register clinic-side studies later (`PRE_REGISTRATION_TEMPLATE.md`).

F1000Research and Research Square remain reserved for selective high-priority papers (#1, #15, #43) per `POST_REJECTION_STRATEGY.md` §5.

---

## 4. Author / metadata block (use for ALL records)

```
Contributor:    Han, Cheongwoo                  (single author / first contributor; "Han" is family name)
ORCID:          0009-0004-4805-8815
Email:          crazat7@gmail.com               # MUST match the OSF account email
Affiliation:
  - Genesis_Medicine Lab, Seoul, Republic of Korea
  - HAN PREDICT, Inc. (https://hanpredict.com)
  - Recover Korean Medicine Clinic (https://recover-clinic.kr)

License:           CC-BY 4.0                    (OSF identifier: "CC-By Attribution 4.0 International")
Provider:          osf                          (default OSF Preprints; do NOT use a discipline-specific server like PsyArXiv)
Language:          English
Original publication date: 2026-05-04           (Zenodo deposit date — preserves chronology)
```

**Subjects (Bepress taxonomy)** — choose 2-3 per paper from this allow-list, mapping by paper character:

| Paper character | Bepress subject |
|---|---|
| Computational drug screening / methodology | `Pharmacology, Toxicology and Environmental Health > Pharmacology` |
| Free-energy / molecular dynamics / xtb | `Life Sciences > Biochemistry, Biophysics, and Structural Biology > Biophysics` |
| Cheminformatics / AI / ML | `Physical Sciences and Mathematics > Computer Sciences > Bioinformatics` |
| Korean / Asian traditional medicine | `Medicine and Health Sciences > Alternative and Complementary Medicine` |
| Dermatology / cosmeceutical | `Medicine and Health Sciences > Dermatology` |
| Open source / scientific software | `Physical Sciences and Mathematics > Computer Sciences > Software Engineering` |
| Pharmacogenomics | `Medicine and Health Sciences > Genetic Phenomena` |

**Tags (free-form keywords)** — 5-8 per paper, mirror the manuscript's existing tags. If `_metadata/{N}_{slug}_metadata.json` lacks `tags`, derive from the title and abstract.

**Description / abstract**: use the manuscript's `## Abstract` section verbatim, plain-text (no LaTeX). If LaTeX commands appear, render them via pandoc to markdown then strip remaining `\command{}` patterns.

**Conflict of interest (place at end of OSF abstract or as `notes`):**
> HCW is founder of HAN PREDICT, Inc. and consults for Recover Korean Medicine Clinic. No external funding for this work.

**IRB caveat (same location as COI):**
> In silico only. No wet-lab data and no patient data are reported. IRB approval was filed 2026-04-27 and is pending. Recover Korean Medicine Clinic opens 2026-08-15.

**Cross-deposit disclosure (REQUIRED, per-paper)** — three variants by group:

**Group A (17 Zenodo papers):**
```json
{
  "original_publication_date": "2026-05-04",
  "external_identifier": {
    "type":  "doi",
    "value": "10.5281/zenodo.{NNNNNNNN}"
  }
}
```
Additionally append to the abstract:
> **Prior version**: This manuscript is also deposited on Zenodo as DOI `10.5281/zenodo.{NNNNNNNN}` ({zenodo_url}), published 2026-05-04. Previously screened by bioRxiv (`BIORXIV/2026/{nnnnnn}`) and not selected for posting; some manuscripts also screened by ChemRxiv 2026-04-30 (curator letter, scope mismatch).

**Group B (2 medRxiv-rejected papers, no Zenodo)**:
```json
{
  "original_publication_date": "2026-05-08",
  "external_identifier": null
}
```
Append to the abstract:
> **Submission history**: This manuscript was screened by medRxiv (`MEDRXIV/2026/351912` for #02, `MEDRXIV/2026/351914` for #11) and not selected for posting; the screening pattern that affected this submission was the absence of new wet-lab or clinical patient data. OSF is the first open-access record for this manuscript.

**Group C (3 net-new papers, no prior submission)**:
```json
{
  "original_publication_date": "2026-05-08",
  "external_identifier": null
}
```
No prior-version disclosure needed. Optionally for paper_A / paper_B, append a single sentence noting the companion-paper relationship:
> **Companion paper**: paper_A (ZAFF-AMBER ABFE limitations, OSF DOI ...) and paper_B (xtb robustness, OSF DOI ...) form a paired methodology contribution to the Genesis_Medicine preprint series. Cross-cite once both DOIs are minted.

The `submission_id`, Zenodo DOI, Zenodo URL, and medRxiv ID for each paper are in `_metadata/{N}_{slug}_metadata.json` under fields `submission_id` (Group A only) and inferred from the slug for Group B (per the IDs listed in §2). For Group C, the `_metadata` files contain `submission_status: "net_new_no_prior_submission"`. Read the metadata; do not invent IDs or DOIs.

---

## 5. Workflow — 4 phases

**Phase 1 — Single test deposit (REQUIRED before bulk)**

OSF does not provide a separate sandbox; the production API is the only environment. To minimize risk:

- Test with **one paper only — paper #08 (abfe_methodology)** because it has the simplest metadata (no figures, no traditional medicine cross-refs, mostly text body).
- Create the preprint as **`primary_file_size_only`** (upload PDF), populate metadata per §4, but **do NOT call the publish endpoint** — leave in `initial` (draft) state.
- Verify on https://osf.io/preprints/ that the draft is visible to HCW (logged-in, private state).

**Stop after Phase 1. Report draft URL to HCW. Do not proceed without sign-off.**

**Phase 2 — Production drafts (16 papers, batch)**

After sign-off on the test deposit:
1. For each of the remaining 16 papers, create an OSF preprint draft (state: `initial`, NOT submitted).
2. Upload `manuscript.pdf` as the primary file (canonical version). If `manuscript.pdf` is missing, build it from `manuscript.md` or `manuscript.tex` via `pandoc` first.
3. Populate metadata per §4: title, abstract (with COI/IRB/prior-version), subjects (2-3 from Bepress), tags (5-8), license CC-BY 4.0, contributor block, original_publication_date 2026-05-04, external_identifier Zenodo DOI.
4. Save the draft URL to `_metadata/{N}_{slug}_metadata.json` under new field `osf_draft_url`.

**Stop after all 22 drafts created (17 Group A + 2 Group B + 3 Group C). Hand off list of draft URLs to HCW for review. Wait for go/no-go on each.**

**Phase 3 — Per-paper review pass**

HCW will provide a per-paper sign-off list (e.g., "publish all of Group A; publish #02 + #11 from Group B; publish paper_A + paper_B from Group C; hold #19 pending v0.2 freeze"). Only publish the green-light subset.

**Phase 4 — Publish + record DOI**

For each green-lit paper:
1. Transition OSF preprint state from `initial` → `submitted` (the OSF default provider auto-publishes since it has no moderation; on a moderated provider this would be `pending`).
2. Wait for state to settle to `accepted` (typically <60 sec for default OSF provider).
3. Capture the assigned Crossref DOI (`10.31219/osf.io/{guid}`) and `osf_url` (e.g., `https://osf.io/{guid}/`).
4. Append to `_metadata/{N}_{slug}_metadata.json`:
   ```json
   "osf_doi":          "10.31219/osf.io/{guid}",
   "osf_url":          "https://osf.io/{guid}/",
   "osf_published":    "2026-05-{DD}",
   "osf_guid":         "{guid}"
   ```
5. After all green-lit papers are published, write `preprints/OSF_RESULT_HANDOFF.md` summarizing all DOIs in the same table format used by `ZENODO_RESULT_HANDOFF.md`.

---

## 6. API contract (OSF JSON:API v2)

Endpoint root: `https://api.osf.io/v2/`. OSF uses **JSON:API** spec (note the `data.attributes` envelope).

**Authentication**: Bearer Personal Access Token (PAT) header. HCW must generate at https://osf.io/settings/tokens with scopes `osf.full_write`. The agent should expect `OSF_PAT` via env var or a `.env` file at the repo root; it is NOT checked into git.

```http
POST /v2/preprints/?embed=provider
Authorization: Bearer {OSF_PAT}
Content-Type: application/vnd.api+json

{
  "data": {
    "type": "preprints",
    "attributes": {
      "title": "...",
      "description": "<abstract + prior-version + COI + IRB caveat>",
      "tags": ["embelia-ribes", "EMB-3", "skin-fibrosis", "..."],
      "subjects": [
        ["584240da54be81056ceca9e5"],   // Pharmacology subject GUID — fetch from /v2/taxonomies/
        ["..."]                         // 1-2 more subject GUIDs
      ],
      "license_record": {
        "year": "2026",
        "copyright_holders": ["Han, Cheongwoo"]
      },
      "original_publication_date": "2026-05-04",
      "doi": null,                      // Let OSF mint
      "preprint_doi_created": null,
      "is_published": false             // Phase 2 draft state
    },
    "relationships": {
      "license": {
        "data": {
          "type": "licenses",
          "id":   "{CC-BY-4.0_license_id}"   // GET /v2/licenses/?filter[name]=CC-By%20Attribution%204.0%20International to discover
        }
      },
      "provider": {
        "data": { "type": "preprint-providers", "id": "osf" }
      }
    }
  }
}
```

**Upload primary file** (after preprint resource exists):
```http
PUT /v2/preprints/{preprint_id}/files/osfstorage/?name=manuscript.pdf
Authorization: Bearer {OSF_PAT}
Content-Type: application/pdf

<binary PDF body>
```

**Add contributor (single author)**:
```http
POST /v2/preprints/{preprint_id}/contributors/
{
  "data": {
    "type": "contributors",
    "attributes": {
      "permission": "admin",
      "bibliographic": true
    },
    "relationships": {
      "users": {
        "data": { "type": "users", "id": "{HCW_user_id}" }
      }
    }
  }
}
```

The HCW user GUID is discoverable via `GET /v2/users/me/` after authenticating. Cache it for the session.

**Add external identifier (Zenodo DOI cross-link)**:
```http
PATCH /v2/preprints/{preprint_id}/identifiers/
{
  "data": [{
    "type": "identifiers",
    "attributes": {
      "category": "doi",
      "value":    "10.5281/zenodo.{NNNNNNNN}"
    }
  }]
}
```

**Publish** (Phase 4):
```http
PATCH /v2/preprints/{preprint_id}/
{
  "data": {
    "id":   "{preprint_id}",
    "type": "preprints",
    "attributes": { "is_published": true }
  }
}
```

If the actual OSF API differs from this contract (the JSON:API endpoints occasionally rename), follow the live docs at `https://developer.osf.io/` and report any deviation in the result-handoff file.

---

## 7. Acceptance criteria (per paper)

A deposit is "complete" only if all of the following hold:

1. ✅ OSF preprint is in `is_published: true` state.
2. ✅ Crossref DOI is minted (`10.31219/osf.io/{guid}` form).
3. ✅ External identifier per group:
   - Group A: cites Zenodo DOI as `category: doi`.
   - Group B / C: external_identifier may be null; no Zenodo to link.
4. ✅ Description / abstract field contains COI + IRB caveat + per-group prior-version/submission-history disclosure verbatim.
5. ✅ Primary file uploaded and downloadable from the OSF page:
   - Groups A / B: `manuscript.pdf`.
   - Group C: `manuscript.pdf` if successfully built; else `manuscript.html` as fallback (acceptable per OSF spec).
6. ✅ Single contributor (HCW) with `bibliographic: true` and `permission: admin`.
7. ✅ License = CC-BY 4.0.
8. ✅ Subjects: 2-3 from Bepress taxonomy per §4.
9. ✅ `original_publication_date` set:
   - Group A: `2026-05-04` (Zenodo deposit date — preserves chronology).
   - Groups B / C: `2026-05-08` (OSF deposit date — first published date).
10. ✅ `_metadata/{N}_{slug}_metadata.json` updated with `osf_doi`, `osf_url`, `osf_published`, `osf_guid` fields.

If any check fails on a paper, do NOT publish it; flag in the result-handoff with status `BLOCKED` and the specific failure reason.

---

## 8. Edge cases / risk register

| Risk | Mitigation |
|---|---|
| OSF PAT not provisioned | First step is to confirm HCW has the token; if not, surface as a blocker |
| OSF requires confirmed institutional email | OSF accepts personal email after ORCID linking; verify HCW account is in `email_verifications: confirmed` state via `GET /v2/users/me/` |
| Bepress subject GUID lookup fails | Cache the full taxonomy via `GET /v2/taxonomies/?filter[parents__isnull]=true&page[size]=100` once at session start; fallback to `Pharmacology` if a chosen subject not found |
| PDF missing for a paper | Build via `pandoc manuscript.md -o manuscript.pdf --pdf-engine=xelatex` or `tectonic manuscript.tex`; fall back to upload `manuscript.md` directly if PDF build fails twice (OSF accepts markdown) |
| Single-author rejected | OSF requires ≥1 bibliographic contributor; single contributor is supported. If API returns validation error, report verbatim and stop |
| Zenodo cross-link rejected (category not `doi`) | OSF uses `category` enum; valid values include `doi`, `ark`, `purl`. If `doi` rejected, file as plain `external_url` in description |
| Already-published Zenodo manuscript triggers duplicate-content flag | OSF policy explicitly permits cross-posting; cite Zenodo DOI in description to make this explicit |
| Bibliography not in NLM/APA format | OSF does not require structured bibliography; the manuscript PDF carries its own references |
| API rate limit (`429 Too Many Requests`) | OSF default limit is 100 req/hr per token; throttle to 1 req per 4 sec; 17 papers × ~6 API calls ≈ 100 calls in 7 min |
| OSF `is_published: true` is irreversible | OSF allows withdrawing a preprint with a `withdraw_justification`, but the DOI persists with a "withdrawn" tombstone. Treat publish as a one-way door — same as Zenodo |
| Provider field defaults to discipline-specific (e.g., MetaArXiv) | Explicitly set `provider.data.id = "osf"` to use the default OSF Preprints server |
| Embargo or moderation triggers | OSF default provider has no moderation. If accidentally targeting a moderated provider, the state goes to `pending` instead of `accepted` — abort and re-target `osf` |

---

## 9. Result handoff template

After Phase 4 completes, write to `/home/crazat/genesis_medicine/preprints/OSF_RESULT_HANDOFF.md`:

```markdown
# Genesis_Medicine 후속 작업 의뢰 — OSF Preprints 17편 cross-post 완료 (2026-05-{DD})

## 1. 핵심 결과: OSF N편 PUBLISHED, DOI 발급 완료

### 발급된 OSF DOI

| # | Slug | Zenodo DOI | OSF DOI | URL |
|---|---|---|---|---|
| 1 | embelia_ribes_review | 10.5281/zenodo.20018329 | 10.31219/osf.io/{guid} | https://osf.io/{guid}/ |
| ... |

### 종합 status (2026-05-{DD})

| 트랙 | published | rejected | blocked | notes |
|---|---|---|---|---|
| Zenodo | 17 ✅ | - | - | (Group A only) |
| OSF    | N ✅ | - | M (사유 별첨) | Group A + B + C, 22편 시도 |
| medRxiv| - | 2 ❌ | - | #02, #11 |
| bioRxiv| - | 19 ❌ | - | |
| ChemRxiv|-| 7 ❌ | - | |

### Per-group OSF outcome

| Group | Papers | Successful | Failed/Blocked |
|---|---|---|---|
| A (Zenodo cross-link) | 17 | ... | ... |
| B (medRxiv-rejected, no Zenodo) | 2 | ... | ... |
| C (net-new, no prior submission) | 3 | ... | ... |
| **Total** | **22** | **N** | **M** |

## 2. 다음 step

- F1000Research 우선 3편 (#1, #15, #43) cross-post — 5/15부터 ($4,500)
- #4 tyrosinase IC50 wet-lab 시작 — 5/13 kit 주문, 6/15 결과
- 8/15 Recover Clinic open 후 wet-lab pipeline 4편 시작
```

---

## 10. Authorization & sign-off boundaries

- **Phase 1 (test deposit, draft only)**: agent autonomous.
- **Phase 2 (production drafts)**: agent autonomous, but stop and report after all 17 drafts created.
- **Phase 3 (per-paper publish list)**: REQUIRES HCW sign-off. Do not publish without explicit per-paper green light.
- **Phase 4 (publish)**: agent autonomous on green-lit papers only.

If at any phase the agent is uncertain whether an action is reversible (OSF treats `is_published: true` as one-way; only `withdrawn` tombstone is available), default to asking HCW.

---

## 11. Hand-off contact

- **HCW direct**: this Claude Code session in `/mnt/d` (Genesis_Medicine repo).
- **Result file**: `/home/crazat/genesis_medicine/preprints/OSF_RESULT_HANDOFF.md` (per §9 template).
- **Update log**: append to `/home/crazat/genesis_medicine/preprints/_metadata/{N}_{slug}_metadata.json` per §5 Phase 4.

When ready, confirm receipt of this prompt by listing the 17 paper directory names back, then await HCW's go-signal for Phase 1.
