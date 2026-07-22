# Upload Agent Prompt — Qeios Bulk Cross-Post (2026-05-08)

> Hand this entire file to the upload agent. Self-contained. No prior session context required.

---

## 1. Mission

You are an upload agent for the Genesis_Medicine preprint program. After the **April-May 2026 rejection wave** (bioRxiv 19/19, ChemRxiv 7/7, medRxiv 2/2 — all in-silico-only screening rejected), 17 manuscripts were captured on Zenodo as permanent open-access records (DOIs `10.5281/zenodo.20018254` through `20018378`). Genesis is now expanding the academic trace by **cross-posting the same 17 manuscripts to Qeios** — an open peer-review platform with **no editorial rejection** (every submission is published; review is post-publication and open).

Qeios deposits are **free** (no APC), gain a **Crossref DOI** automatically (`10.32388/...`), and become **search-indexed** within 24-48 hours. This is Option B from `POST_REJECTION_STRATEGY.md` — the cheapest, fastest action that materially adds peer-review track to all 17 papers.

The lab principal is **HanCheongWoo (HCW)**, sole author of all manuscripts.

The **Recover Korean Medicine Clinic opens 2026-08-15 (D-99 from today)**. Qeios trace must be in place before clinic launch so external readers can cite the work alongside the Zenodo records.

---

## 2. Scope — what to upload

The same 17 papers that received Zenodo DOIs on 2026-05-04. Source of truth: `/home/crazat/genesis_medicine/preprints/_metadata/{N}_{slug}_metadata.json`.

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

**Final scope: 17 records** (paper #01, #03, #04, #05, #06, #07, #08, #09, #10, #12, #13, #14, #15, #16, #17, #18, #43).

**EXCLUDED — do NOT cross-post:**
- **#02 recover_workflow** — medRxiv outcome already received (rejected 5/5-8); a separate decision on whether to cross-post #02 is pending the wet-lab roadmap (see `V1_WETLAB_ROADMAP.md`). Hold for HCW sign-off.
- **#11 korean_pgx_topical** — same as #02; medRxiv rejected, awaiting wet-lab pivot. Hold.
- **#19 korean_herbal_scaffold_xref** — v0.2 still finalizing 60 ns MD evidence. Exclude until v0.2 frozen.

If HCW asks to add or remove papers from the scope, surface that as a single yes/no question and do not silently change the list.

---

## 3. Why Qeios specifically

| Feature | Qeios | F1000Research | Research Square |
|---|---|---|---|
| Cost | **$0** | $1,500/paper | ~$1,000/paper |
| Editorial rejection | **none** | yes (~80% accept) | yes (lighter) |
| DOI minted | yes (Crossref) | yes | yes |
| Open peer review | **yes, post-publication** | yes, pre-publication | hybrid |
| Time to live | **24-48 h** | 4-8 weeks | 2-4 weeks |

Qeios is the only venue in this set where 17/17 deposits are guaranteed to result in a citable peer-reviewable record without spending APC budget. F1000Research and Research Square are reserved for selective high-priority papers (#1, #15, #43 — see `POST_REJECTION_STRATEGY.md` §5).

---

## 4. Author / metadata block (use for ALL records)

```
Creator:    Han, Cheongwoo                  (single author; "Han" is family name)
ORCID:      0009-0004-4805-8815
Email:      crazat7@gmail.com               # MUST match the Qeios / ORCID account email
Affiliation:
  - Genesis_Medicine Lab, Seoul, Republic of Korea
  - HAN PREDICT, Inc. (https://hanpredict.com)
  - Recover Korean Medicine Clinic (https://recover-clinic.kr)

License:           CC-BY-4.0
Article type:      Research Article         (or "Review" for #01, #19; "Opinion" for #12)
Subject category:  Pharmacology / Computational Biology / Medicinal Chemistry
                   (per-paper, see _metadata.json subject_area field)
Language:          eng
Publication date:  2026-05-08 (deposit date)
```

**COI (place at end of manuscript or `notes` field):**
> HCW is founder of HAN PREDICT, Inc. and consults for Recover Korean Medicine Clinic. No external funding for this work.

**IRB caveat:**
> In silico only. No wet-lab data and no patient data are reported. IRB approval was filed 2026-04-27 and is pending. Recover Korean Medicine Clinic opens 2026-08-15.

**Cross-deposit disclosure (REQUIRED, per-paper, in `notes` and `related_identifiers`):**
> This manuscript is also deposited on Zenodo as DOI `{zenodo_doi}` (record `{zenodo_url}`), published 2026-05-04. Previously screened by bioRxiv (`BIORXIV/2026/{nnnnnn}`) and not selected for posting; some manuscripts also screened by ChemRxiv 2026-04-30 (curator letter, scope mismatch). Both fields below should reference the Zenodo DOI as the prior version.
>
> **Qeios `related_identifiers` field**:
> ```json
> [{"identifier": "10.5281/zenodo.{NNNNNNNN}",
>   "relation": "isVersionOf",
>   "resource_type": "publication-preprint"}]
> ```

The `submission_id`, Zenodo DOI, and Zenodo URL for each paper are in `_metadata/{N}_{slug}_metadata.json`. Read; do not invent.

---

## 5. Workflow — 4 phases

**Phase 1 — Sandbox / dry-run (REQUIRED)**

Qeios provides a sandbox at `https://sandbox.qeios.com` (separate API key). Test with **one paper only — paper #08 (abfe_methodology)** because it has the simplest metadata (no figures, no traditional medicine cross-refs that might trigger keyword filters). Verify:

- API authentication works (Bearer token)
- Markdown body uploads correctly (figures inlined or referenced via `figures/` subpath)
- DOI minting succeeds (sandbox DOIs are throwaway but the workflow is identical)
- `related_identifiers` accepts the Zenodo DOI in `isVersionOf` relation
- `notes` field renders the COI + IRB caveat correctly

**Stop after Phase 1. Report sandbox URL to HCW. Do not proceed without sign-off.**

**Phase 2 — Production drafts (16 papers, batch)**

After sign-off on the sandbox example:
1. For each of the remaining 16 papers, create a Qeios draft (status: `draft`, NOT published).
2. Use the `manuscript.md` body verbatim (or `manuscript.tex` if .md missing — convert to markdown via pandoc).
3. Attach the `manuscript.pdf` from each paper's directory as the canonical-version file.
4. Populate metadata per §4.
5. Save the draft URL to `_metadata/{N}_{slug}_metadata.json` under new field `qeios_draft_url`.

**Stop after all 17 drafts created. Hand off list of draft URLs to HCW for review. Wait for go/no-go on each.**

**Phase 3 — Per-paper review pass**

HCW will provide a per-paper sign-off list (e.g., "publish 1, 3, 4, 5, 7, 8, 10, 12, 15, 18, 43; hold 6, 9, 13, 14, 16, 17 pending revision"). Only publish the green-light subset.

**Phase 4 — Publish + record DOI**

For each green-lit paper:
1. Transition Qeios record from `draft` → `published`.
2. Capture the assigned Crossref DOI (`10.32388/{Q-XXXXXX}`) and `qeios_url` (e.g., `https://www.qeios.com/read/Q-XXXXXX`).
3. Append to `_metadata/{N}_{slug}_metadata.json`:
   ```json
   "qeios_doi":          "10.32388/Q-XXXXXX",
   "qeios_url":          "https://www.qeios.com/read/Q-XXXXXX",
   "qeios_published":    "2026-05-{DD}"
   ```
4. After all green-lit papers are published, create a result-handoff file at `preprints/QEIOS_RESULT_HANDOFF.md` summarizing all DOIs in the same table format used by `ZENODO_RESULT_HANDOFF.md`.

---

## 6. API contract (Qeios v1)

Endpoint root: `https://api.qeios.com/v1` (production), `https://api.sandbox.qeios.com/v1` (sandbox).

```http
POST /articles
Authorization: Bearer {QEIOS_API_KEY}
Content-Type: application/json

{
  "title":                 "...",
  "abstract":              "...",
  "body_markdown":         "...",
  "authors": [{
      "given_name":  "Cheongwoo",
      "family_name": "Han",
      "orcid":       "0009-0004-4805-8815",
      "email":       "crazat7@gmail.com",
      "affiliations": [
        "Genesis_Medicine Lab, Seoul, Republic of Korea",
        "HAN PREDICT, Inc. (https://hanpredict.com)",
        "Recover Korean Medicine Clinic (https://recover-clinic.kr)"
      ]
  }],
  "license":              "CC-BY-4.0",
  "article_type":         "research-article",     // or "review", "opinion"
  "subject_categories":   ["Pharmacology", "Computational Biology"],
  "language":             "eng",
  "related_identifiers": [{
      "identifier":     "10.5281/zenodo.{N}",
      "relation":       "isVersionOf",
      "resource_type":  "publication-preprint"
  }],
  "notes": "<COI + IRB caveat + cross-deposit disclosure as per §4>",
  "status": "draft"
}
```

If the actual Qeios API differs from this contract (Qeios docs may have updated since this prompt was written 2026-05-08), follow the live docs at `https://www.qeios.com/api` and report any deviation in the result-handoff file.

The API key (`QEIOS_API_KEY`) must be obtained by HCW from `https://www.qeios.com/account/api` after creating a free Qeios account linked to the same ORCID and email above. The agent should expect this key to be passed via env var or a `.env` file at the repo root; it is NOT checked into git.

---

## 7. Acceptance criteria (per paper)

A Qeios deposit is "complete" only if all of the following hold:

1. ✅ Qeios article is in `published` state.
2. ✅ Qeios DOI is minted (`10.32388/Q-XXXXXX` form).
3. ✅ `related_identifiers` correctly cites the Zenodo DOI as `isVersionOf`.
4. ✅ `notes` field contains COI + IRB caveat + cross-deposit disclosure verbatim.
5. ✅ Manuscript body matches `manuscript.md` (or .tex-converted markdown) — diff < 1% (allow figure-path rewrites).
6. ✅ Author block matches §4 single-author metadata.
7. ✅ License = CC-BY-4.0.
8. ✅ `_metadata/{N}_{slug}_metadata.json` updated with `qeios_doi`, `qeios_url`, `qeios_published` fields.

If any check fails on a paper, do NOT publish it; flag in the result-handoff with status `BLOCKED` and the specific failure reason.

---

## 8. Edge cases / risk register

| Risk | Mitigation |
|---|---|
| Qeios API key not yet provisioned | First step is to confirm HCW has the key; if not, surface as a blocker |
| Qeios rejects an article body for "scope mismatch" | Qeios scope is broader than ChemRxiv; should not happen, but if it does, escalate to HCW (do not silently retry) |
| Markdown conversion strips figures | Re-attach figures as `figures/figN.png` and reference `![](figures/fig1.png)` syntax |
| Multiple authors required by Qeios (single-author rejected) | Qeios accepts single-author; if API returns validation error, report verbatim and stop |
| Cross-deposit `relation` field rejects `isVersionOf` | Try `references` as fallback; if both fail, report and stop |
| Already-published Zenodo manuscript triggers duplicate-content flag | Qeios policy explicitly permits cross-posting from Zenodo; cite Zenodo DOI in `notes` to make this explicit |
| Subject category not in Qeios taxonomy | Use closest match from Qeios's subject list; if uncertain on >2 papers, surface as a question |
| API rate limit (≥10 req/min) | Throttle to 1 req per 15 sec; 17 papers × 4 API calls ≈ 70 calls = 17 min total |

---

## 9. Result handoff template

After Phase 4 completes, write to `/home/crazat/genesis_medicine/preprints/QEIOS_RESULT_HANDOFF.md`:

```markdown
# Genesis_Medicine 후속 작업 의뢰 — Qeios 17편 cross-post 완료 (2026-05-{DD})

## 1. 핵심 결과: Qeios N편 PUBLISHED, DOI 발급 완료

### 발급된 Qeios DOI

| # | Slug | Zenodo DOI | Qeios DOI | URL |
|---|---|---|---|---|
| 1 | embelia_ribes_review | 10.5281/zenodo.20018329 | 10.32388/Q-XXXXXX | https://www.qeios.com/read/Q-XXXXXX |
| ... |

### 종합 status (2026-05-{DD})

| 트랙 | published | rejected | blocked |
|---|---|---|---|
| Zenodo | 17 ✅ | - | - |
| Qeios  | N ✅ | - | M (사유 별첨) |
| medRxiv| - | 2 ❌ | - |
| bioRxiv| - | 19 ❌ | - |
| ChemRxiv|-| 7 ❌ | - |

## 2. 다음 step

- F1000Research 우선 3편 (#1, #15, #43) cross-post — 5/15부터 ($4,500)
- #4 tyrosinase IC50 wet-lab 시작 — 5/13 kit 주문, 6/15 결과
- 8/15 Recover Clinic open 후 wet-lab pipeline 4편 시작
```

---

## 10. Authorization & sign-off boundaries

- **Phase 1 (sandbox)**: agent autonomous.
- **Phase 2 (production drafts)**: agent autonomous, but stop and report after all 17 drafts created.
- **Phase 3 (per-paper publish list)**: REQUIRES HCW sign-off. Do not publish without explicit per-paper green light.
- **Phase 4 (publish)**: agent autonomous on green-lit papers only.

If at any phase the agent is uncertain whether an action is reversible (Qeios does NOT permit deletion after publish — only retraction notes), default to asking HCW.

---

## 11. Hand-off contact

- **HCW direct**: this Claude Code session in `/mnt/d` (Genesis_Medicine repo).
- **Result file**: `/home/crazat/genesis_medicine/preprints/QEIOS_RESULT_HANDOFF.md` (per §9 template).
- **Update log**: append to `/home/crazat/genesis_medicine/preprints/_metadata/{N}_{slug}_metadata.json` per §5 Phase 4.

When ready, confirm receipt of this prompt by listing the 17 paper directory names back, then await HCW's go-signal for Phase 1.
