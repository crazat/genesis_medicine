# HANDOFF — Upload Agent Runbook (paper_A v6)  ·  v2 (2026-06-02, post-PDF-review)

**For:** the agent (or person) executing the deposit/submission.
**Author of record:** Cheongwoo Han — **SOLE AUTHOR** — ORCID `0009-0004-4805-8815`, `crazat7@gmail.com`, Independent Researcher.
**Paper:** *Cross-Validation of Three Neural Network Potentials for MMP-1 Zn Active-Site Inhibitor Ranking: A Computationally-Driven Repositioning Study of Vorinostat and Indapamide*

Read §0 first. **TASK 1 (Zenodo) is READY — only the SI zip (§2.5) remains before the final Publish click. TASK 2 (JCIM) is BLOCKED until the §3.3 readiness gate passes.**

Base directory for all paths: `/home/crazat/genesis_medicine/preprints/23_paper_A_v6_mmp1_5nnp_xtb/`

---

## 0. GUARDRAILS — read before doing anything
1. **Single author. Do NOT add/restore/invent co-authors.** Author = Cheongwoo Han only. Any mention of SNUH / KAIST / Amorepacific / KMCRIC / Yonsei / Asan / Kolmar / Daewoong etc. is a **citation only**, never an author. (Co-author/co-PI claims were removed 2026-06-02.)
2. **Do NOT edit scientific content.** Your job = upload/submission mechanics + format conversion. If something looks wrong, flag it back; don't "fix" the science.
3. **The final irreversible action (Zenodo "Publish", ACS "Submit") needs the author's explicit GO for that specific deposit.** Prepare up to the final click, then get a clear "publish now" / "submit now". A published DOI is permanent and public.
4. **No secrets in files.** Use the author's own logged-in session. Never write passwords/tokens into any file.
5. **Two manuscript versions, NOT interchangeable:** `manuscript_v0.2.md` = comprehensive → **Zenodo**; `manuscript_JCIM_v0.1.md` = condensed → **JCIM** (still being trimmed).

---

## 1. Identity & accounts
| Item | Value |
|------|-------|
| Author | Han, Cheongwoo |
| ORCID | 0009-0004-4805-8815 |
| Corresponding email | crazat7@gmail.com |
| Affiliation | Independent Researcher / Genesis Medicine (Korea) |
| Zenodo | log in via ORCID; 22 prior records (this = sequence #23) |
| ACS Paragon Plus | https://acsparagonplus.acs.org (create via ORCID if needed) |

---

## 2. TASK 1 — Zenodo deposit  ✅ READY (only SI zip pending)

**Goal:** citable DOI = priority date. Zero cost, no peer-review gate. **Do this FIRST.**
**Field-by-field values:** `DEPOSIT_READY_zenodo_v0.2.md` (same folder). Summary:

### 2.1 Metadata (paste verbatim)
- **Upload type:** Publication → **Preprint**
- **Title:** `Cross-Validation of Three Neural Network Potentials for MMP-1 Zn Active-Site Inhibitor Ranking: A Computationally-Driven Repositioning Study of Vorinostat and Indapamide`
- **Creators:** ONE row — `Han, Cheongwoo` · `Independent Researcher` · ORCID `0009-0004-4805-8815`
- **Description:** paste the Abstract (lines 14–20 of `manuscript_v0.2.md`)
- **License:** CC-BY-4.0
- **Keywords:** `Boltz-2; neural network potentials; GFN2-xTB; MMP-1; matrix metalloproteinase-1; zinc metalloprotease; drug repositioning; vorinostat; indapamide; sulfonamide diuretic; PoseBusters; cross-validation; reliability; conformal prediction`

### 2.2 Files to upload
| Upload | File | State |
|--------|------|-------|
| Manuscript (PDF) | `manuscript_v0.2.pdf` | ✅ **done + reviewed (50 pp, 0 breakage)** |
| Manuscript (md) | `manuscript_v0.2.md` | ✅ single-author |
| References | `references.md` | ✅ 239 refs (full set ok for Zenodo) |
| Figures 1–5 | `figures/figure[1-5]_*.{png,pdf}` | ✅ present |
| Headline dataset | `sigma_e_v212_v303_unified_consolidated.csv` | ✅ |
| Conformal layer | `conformal/` (+ `conformal_reliability_layer.py`) | ✅ |
| SI data bundle | `SI.zip` + `SI_README.md` | ⏳ **CREATE — see §2.4** |

### 2.3 PDF — already generated & verified ✅
`manuscript_v0.2.pdf` (50 pp) was produced with pandoc 3.9 + weasyprint using DejaVu (Latin/Greek/symbols) + NanumGothic (Korean) per-glyph fallback, and **reviewed page-by-page: 0 breakage** — Korean, σ/Zn²⁺/superscripts/arrows, the §8 multi-organ table (no overflow), reference list, and code blocks all render; single-author header confirmed on p1. No action needed unless the .md changes. To **regenerate** (e.g. after an edit):
```
mkdir -p ~/.fonts && cp /mnt/c/Windows/Fonts/NanumGothic-Regular.ttf /mnt/c/Windows/Fonts/NanumGothic-Bold.ttf ~/.fonts/ && fc-cache -f ~/.fonts
cd /home/crazat/genesis_medicine/preprints/23_paper_A_v6_mmp1_5nnp_xtb/
/home/crazat/miniforge3/bin/pandoc manuscript_v0.2.md -s -o manuscript_v0.2.pdf --pdf-engine=weasyprint -c /tmp/paperA_print.css --resource-path=.
```
(CSS at `/tmp/paperA_print.css`; if absent, see `scripts/round27_paperA/pdf_review_render.py` for the review/render tooling.)

### 2.4 SI bundle — the ONE remaining prep step ⏳
`SI/` = **27,260 CSVs (~1.7 GB)** — do NOT upload loose. Zip + add a README of the sept-matrix schema (3 GFN{0,1,2} × 3 calc{SP,OPT,OHESS} × 2 solvation{ALPB,GBSA} × N cohorts; filename `xtb_gfn{G}_{calc}_{solvation}_{solvent}_v{cohort}.csv`):
```
cd /home/crazat/genesis_medicine/preprints/23_paper_A_v6_mmp1_5nnp_xtb/
zip -r SI.zip SI/
```
If too unwieldy for one record, split SI into a **separate Zenodo data record** and cross-link (relation *isSupplementedBy*). (Author may prefer a curated subset — confirm if unsure.)

### 2.5 Execute
Fill metadata → attach files → **STOP, get author "publish now"** → **Publish** → write the DOI into §5 below and into `references.md` self-citation.

---

## 3. TASK 2 — JCIM submission  ✅ AUTHORIZED — JCIM-READY (2026-06-02) + author go-ahead given → PROCEED per §3.4
> Deliverables ready in base dir: `manuscript_JCIM_v0.1.md` (status-marked JCIM-READY) · `references_JCIM.md` (refs 1–43) · `cover_letter_JCIM_v0.1.md` · `figures/figure[1-5]_*.{png,pdf}` · `manuscript_JCIM_v0.1.pdf` (25 pp, body+refs, verified 0 breakage). Data&Code Availability already cites DOI 10.5281/zenodo.20247828. Submit to *J. Chem. Inf. Model.* (non-OA/subscription) per §3.4. Single author; no funding; no competing interests.

**Target:** *J. Chem. Inf. Model.* (ACS), **non-OA / subscription route = $0 to publish** (do NOT pick open-access/APC unless the author opts in). Fallback if rejected: **PLoS ONE** (§4).

### 3.1 Current state of the JCIM manuscript
`manuscript_JCIM_v0.1.md` is a condensed copy of v0.2, **work in progress (446 lines, was 532)**.
- ✅ Done: cover letter (`cover_letter_JCIM_v0.1.md`); §9.3 Future Directions condensed to science-only; §3.6 (Korean HPC) / §6.7 (federated ADMET) / §6.8 (K/APAC regulatory) cut.
- ⏳ Pending: §8 "Korean cohort linkage" table trim; §5.5 / §5.7 Korean-narrative condense; residual padding terms (Genesis Medicine Lab ×5, microneedle ×3, K-OMOP ×6, KHIDI ×1); **reference trim 239 → ~90 + renumber + in-text sync**; JCIM section reformat + Associated Content → Zenodo SI DOI.
- Tracking: `JCIM_submission_prep_plan.md` (cut list + order).

### 3.2 Already prepared
- Cover letter `cover_letter_JCIM_v0.1.md` (single-author; scope-fit; wet-lab limitation stated up front)
- Figures 1–5 (same files; PDFs are vector, fine for 300+ dpi requirement)

### 3.3 ⛔ JCIM READINESS GATE — ALL must be ✓ before submitting
- [ ] `manuscript_JCIM_v0.x` marked **"JCIM-READY"** by the author/preparing agent
- [ ] References ≤ ~100, renumbered, every in-text `ref N` resolves
- [ ] No funding/commercialization/regulatory/tourism/quantum/agent-ecosystem narrative left
- [ ] No co-author / co-PI / "institutional reference network" collaboration framing left
- [ ] Zenodo DOI (from TASK 1) cited in Associated Content / Data Availability
- [ ] Word count ~5,000–6,500; figure callouts consistent; JCIM section order applied
- [ ] PDF regenerated & spot-checked (use §2.3 command on the JCIM file)
- [ ] Author gives explicit "submit to JCIM now"

### 3.4 Execute (once gate passes)
ACS Paragon Plus → new submission → *J. Chem. Inf. Model.* → type: Article → upload manuscript + 5 figures (separate hi-res) + `cover_letter_JCIM_v0.1.md` → SI = Zenodo DOI link → corresponding author Cheongwoo Han → **subscription (non-OA)** → declare: single author, no funding, no competing interests, preprint on Zenodo (give DOI) → **STOP, get author "submit now"** → submit.

---

## 4. Fallback — PLoS ONE (only if JCIM rejects)
Lenient on in-silico-only ("scientific validity, not impact"). APC ~US$1,805 but **fee-assistance / Global Equity waiver applicable** (apply at submission). Reuse the JCIM-condensed manuscript; reformat to PLoS structure; same single-author declarations.

---

## 5. Status log (fill in as you go)
- Zenodo DOI: 10.5281/zenodo.20247828 (date: 2026-06-02)  ✅ PUBLISHED — record https://zenodo.org/records/20247828 (draft #20247828 updated to single-author; 17 files: manuscript pdf+md, references.md, 5 figs png+pdf, sigma_e consolidated csv, conformal.zip, SI.zip 96M + SI_README)
- JCIM submission ID: 51B8CAD3-7F60-4C3D-AEFD-501DEDC76284 (date: 2026-06-02)  SUBMITTED via ACS Publishing Center (ChronosHub) -> J. Chem. Inf. Model., Article, non-OA. Manuscript File=manuscript_JCIM_v0.1.docx (PDF->DOCX), cover_letter docx, 5 figs (Graphic for manuscript), Section=Computational Biochemistry, single corresponding author Cheongwoo Han, no funding/no COI, preprint of record Zenodo 10.5281/zenodo.20247828. Formal ci-2026 Manuscript ID pending by email.
- JCIM decision: __________________
- (if used) PLoS ONE submission ID: __________________

---

## 6. File inventory (absolute paths, base dir above)
- `manuscript_v0.2.md` — comprehensive (Zenodo), single-author
- `manuscript_v0.2.pdf` — ✅ generated + reviewed (50 pp, 0 breakage)
- `manuscript_JCIM_v0.1.md` — condensed (JCIM), **IN PROGRESS (446 lines)**
- `references.md` — 239 refs (full); JCIM-trimmed list TBD
- `cover_letter_zenodo_v0.1.md` — Zenodo cover/metadata
- `cover_letter_JCIM_v0.1.md` — JCIM cover letter
- `DEPOSIT_READY_zenodo_v0.2.md` — Zenodo field-by-field checklist
- `JCIM_submission_prep_plan.md` — JCIM condensation plan/cut list
- `figures/figure[1-5]_*.{png,pdf}` — 5 figures
- `SI/` — 27,260 σ_E CSVs (→ zip to `SI.zip` before upload)
- `conformal/`, `sigma_e_v212_v303_unified_consolidated.csv` — reliability data
- `scripts/round27_paperA/pdf_review_render.py` — PDF render + breakage-check tool (re-run to re-verify any regenerated PDF)

## 7. Escalation
If a gate item is ambiguous, or a system asks for a decision not covered here (journal change, OA-vs-subscription, affiliation detail, ethics/funding fields), **stop and ask the author** — do not change authorship or scientific content to satisfy a form.
