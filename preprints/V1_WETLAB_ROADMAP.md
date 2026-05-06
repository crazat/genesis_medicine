# Genesis_Medicine v1.0 Wet-Lab Integration Roadmap

**Author**: HanCheongWoo · **Date**: 2026-05-04 · **Horizon**: 2026-08-15 (clinic open) → 2027-Q1 (bioRxiv re-attempt)

---

## 1. Why this roadmap exists

19/19 bioRxiv + 7/7 ChemRxiv rejections (April–May 2026) converge on a single screener pattern: "in silico without new wet-lab data is not a complete research paper." Reframing did not help (v0.3/v0.4/v0.8 all rejected). The **only structural fix** is one wet-lab data point added to one (or two) flagship manuscripts. With Recover Korean Medicine Clinic opening **2026-08-15**, the window for cheap, IRB-friendly clinic-side validation opens shortly after. This document selects **two** candidates with the highest wet-lab return per dollar / per day, and locks a 9-month timeline.

The remaining 15 papers stay parked on Zenodo (DOI captured, citable) until either (a) the cosmeceutical / clinic case stream produces relevant secondary data that can be retrofitted, or (b) external collaborators bring assay capacity.

---

## 2. Candidate evaluation (5 papers, 6 axes)

Evaluation rubric, each axis scored 1-5 (5 = best):

| Axis | Definition |
|---|---|
| **A. Compound count** | Fewer is better. Single molecule = 5; 14-compound panel = 1. |
| **B. Assay accessibility** | Off-the-shelf kit / cell line = 5; bespoke tissue / animal = 1. |
| **C. Cost per data point** | <$200 = 5; $200-1k = 3; >$1k = 1. |
| **D. Clinic fit** | Endpoint matches Recover's scope (skin: pigment, scar, acne, alopecia) = 5. |
| **E. IRB friendliness** | No human subjects required for first wet-lab anchor = 5. |
| **F. Manuscript leverage** | Adding 1 wet-lab data row salvages the central claim = 5. |

| # | Paper | A | B | C | D | E | F | Total | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| **#4** | pigmentation_screening | 3 | 5 | 5 | 5 | 5 | 5 | **28** | 🟢 Pick #1 |
| **#3** | emb3_scar_case_study | 5 | 4 | 4 | 5 | 5 | 4 | **27** | 🟢 Pick #2 |
| **#6** | acne_microbiome | 4 | 3 | 3 | 5 | 5 | 4 | 24 | yellow — defer |
| **#13** | piezo1_mlck_alopecia | 4 | 1 | 1 | 5 | 4 | 5 | 20 | red — high novelty, high cost |
| **#16** | r15_chromanol_safety_triage | 1 | 2 | 2 | 4 | 5 | 2 | 16 | red — too broad, defer |

### Why #4 wins (28/30)

- **Mushroom tyrosinase IC50** is the textbook whitening-cosmeceutical assay: kit $50, 96-well plate, 1 day, standard L-DOPA / kojic acid positive control. Top 3 candidates from the screen (Glabridin, Baicalein, plus one) get IC50 numbers in a week. This converts the manuscript from "in silico screen" to "in silico screen + wet-lab IC50 confirmation" — exactly the format bioRxiv considers complete.
- **Scope match**: pigmentation / whitening is the most commercially direct asset for Recover's first-quarter cosmeceutical line.
- **No IRB needed** for tyrosinase IC50 (no human subjects, no animal). IRB filing 2026-04-27 covers later patient case studies.

### Why #3 wins (27/30)

- **Single molecule** (EMB-3) — narrowest possible wet-lab scope. One synthesis batch (or commercial sourcing of close analog) + one HPLC stability run + one HDF (human dermal fibroblast) migration / TGF-β1-stimulated collagen assay. ~$800 reagent, ~3 weeks bench.
- **Case-study format** is editorially accepted at bioRxiv even for n=1 wet-lab — the "case study" framing is what we already paid for in the v0.3/v0.4 reframe attempts.
- **EMB-3 is the lab's flagship lead**; wet-lab data here supports every downstream paper that cites EMB-3 (#1 review, #15 universal scaffold, #16-17 chromanol R-series).

### Why #6 is parked (24/30)

- Sebocyte cell line (SZ95) is licensable but not free; *C. acnes* anaerobic culture requires anaerobic chamber. Both are doable but step-up from #3/#4.
- Wait until Recover clinic has dermatologist + culture facility online (likely Q4 2026, post-soft-launch).

### Why #13 / #16 are deferred

- **#13** PIEZO1/MLCK axis requires hair follicle organoid or primary dermal papilla cells (HDP). Cost $5-10k for one experiment, expertise gap. Defer to 2027 or external collaborator.
- **#16** is a fragment-triage paper across 14 targets — adding 1 wet-lab anchor doesn't salvage 14 independent claims. Better to deprecate #16 as a methodology preprint and roll its useful pieces into #43 (chromanol generative atlas) which has the better target focus.

---

## 3. Timeline — 9 months, gated milestones

```
2026
├── 05-04  ← TODAY. Zenodo 17 DOIs captured. Roadmap published.
├── 05-15  Order tyrosinase IC50 kit ($50, ~1 wk lead)
├── 06-01  Decide EMB-3 sourcing (synthesis vs commercial analog) — if commercial,
│          Sigma / TCI inventory check; else queue 1-step synthesis at clinic-affiliated lab
├── 07-15  Recover clinic interior + bench setup (1 mo before opening)
├── 08-15  Recover Korean Medicine Clinic OPENS (D-day)
├── 09-01  Wet-lab bench operational. Tyrosinase IC50 #4 → top-3 candidates measured
├── 10-01  #4 wet-lab data table complete. Manuscript #4 v1.0 draft started.
├── 10-15  EMB-3 in hand. HPLC stability + HDF migration assay started.
├── 11-15  #3 wet-lab data table complete. Manuscript #3 v1.0 draft started.
├── 12-01  Both v1.0 manuscripts feature-complete (in silico + wet-lab section).
├── 12-15  Internal review (HCW + 1 external reviewer, e.g. Recover medical advisor)
└── 12-31  Submit #4 v1.0 to bioRxiv (Pharmacology) — 1st re-attempt

2027
├── 01-15  Submit #3 v1.0 to bioRxiv (Pharmacology / Cell Biology)
├── 02-15  Decision window (~2 wk screening). Two outcomes:
│          - PASS → posted preprint with DOI. peer-review submission to Phytomedicine /
│                  J Cosmet Dermatol Sci begins.
│          - REJECT (low prob given wet-lab anchor) → file for medRxiv with clinic
│                  case-study reframe.
└── Q2-Q4  Wet-lab cycle 2: #6 acne_microbiome (sebocyte assay) once #3/#4 pipeline
            is stable; remaining 13 Zenodo papers retrofit opportunistically.
```

### Gate definitions

- **Gate 1 (2026-09-01)**: Wet-lab bench operational at Recover. Block: clinic interior delays. Mitigation: identify 1 contract assay lab (e.g., Korean Drug Development Fund-affiliated CRO) as fallback.
- **Gate 2 (2026-10-01)**: #4 IC50 numbers in hand. Block: assay variability. Mitigation: 3 biological replicates × 2 technical = 6 wells per compound; flag any compound with >50% CV for re-test.
- **Gate 3 (2026-11-15)**: #3 wet-lab anchor in hand. Block: EMB-3 not commercially available. Mitigation: switch to embelin (parent) + add structural-comparison section, or commission custom synthesis (~$2k, 6-week TAT).
- **Gate 4 (2026-12-31)**: #4 v1.0 submitted. Block: bioRxiv screener still rejects. Mitigation pre-emptive: bake the wet-lab IC50 figure into Figure 1 of the manuscript (not buried in Methods); use title with "+ wet-lab IC50 confirmation" suffix.

---

## 4. Budget (point estimate, 9 months)

| Item | Cost (KRW, mid) | Cost (USD, mid) | Note |
|---|---:|---:|---|
| Tyrosinase IC50 kit (Sigma T7755 + L-DOPA + kojic acid) | 80,000 | $60 | 1 kit, ~50 IC50 runs |
| Glabridin reference standard (~10 mg) | 60,000 | $45 | Sigma G2630 |
| Baicalein, Resveratrol references | 80,000 | $60 | Sigma |
| 96-well plates + tips | 100,000 | $75 | bulk |
| EMB-3 sourcing (custom synthesis 50 mg) | 2,500,000 | $1,900 | only if no commercial close analog |
| HPLC column + standards | 600,000 | $450 | C18 ODS, reusable |
| HDF cells (ATCC PCS-201-012) | 600,000 | $450 | one vial |
| Cell culture media + serum (3 mo) | 800,000 | $600 | DMEM + FBS + Pen/Strep |
| Migration assay kit (Cell BioLabs CBA-100) | 300,000 | $230 | 1 kit |
| TGF-β1 (PeproTech) | 150,000 | $115 | 10 µg |
| qPCR primers + master mix | 500,000 | $380 | optional, for SMAD readout |
| **Sub-total (in silico → wet-lab v1.0 for #3 + #4)** | **5,770,000** | **~$4,400** | 9 months |
| Contingency (20%) | 1,150,000 | $880 | re-runs, failed batches |
| **Total** | **6,920,000** | **~$5,280** | |

If EMB-3 commercial analog exists (e.g., embelin itself or 5-undecyl-resorcinol): subtract $1,900 → **total ~$3,380**.

---

## 5. Risks and mitigations

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| Recover clinic opening delayed past 2026-08-15 | medium | high | identify CRO fallback for assays (Gate 1 mitigation). Cost +30%. |
| EMB-3 not commercially available; custom synthesis fails | low-medium | medium | switch flagship to embelin (parent) for #3 v1.0 — same biology, easier sourcing. |
| Wet-lab IC50 disagrees badly with in silico (e.g., Glabridin shows no inhibition) | medium | medium | reframe manuscript honestly: "in silico / wet-lab disagreement reveals scoring artifact at X". Failed validation is still publishable when transparent. |
| bioRxiv re-attempt #4 v1.0 still rejected (screener perception that 1 wet-lab is "token") | low | high | escalate: 3 wet-lab anchors not 1 (top-3 IC50 + 1 western + 1 cell viability) before re-submit. Adds 1 month. |
| IRB approval not granted by 2026-12 | low | low for v1.0 (no patient data needed); high for v1.1 case studies | proceed with v1.0 manuscripts independently. Patient case studies require IRB → defer. |
| Author bandwidth (single-author bench + writing) | high | high | recruit 1 part-time wet-lab tech at Recover for ≥3 mo (clinic Q4 budget). |

---

## 6. Decisions to lock now

The user (HCW) needs to confirm or override these defaults before 2026-05-15:

1. **Pick: confirm #4 + #3 as the two v1.0 candidates?** ([yes / swap one for #6 / different pair])
2. **EMB-3 sourcing path: synthesis or commercial-analog?** ([commercial first, synthesis fallback / synthesis first / undecided — research it])
3. **Wet-lab tech recruitment: yes or no?** ([yes — post listing now / yes — after clinic opens / no — author bench])
4. **Bench fallback CRO: pick one or skip?** ([pick one — research now / skip — bet on clinic timeline])

Default: 1=yes, 2=commercial first, 3=yes after clinic opens, 4=research now.

---

## 7. ORCID / website publication-list status (Task 4 — informational)

- **ORCID 0009-0004-4805-8815 Works section**: Zenodo→ORCID auto-push is per-record. The user must, on each of the 17 Zenodo records, click **"Export to ORCID"** under the Settings tab, OR enable bulk auto-push at <https://zenodo.org/account/settings/auto-push/>. Recommended: enable bulk auto-push once, then any future Zenodo deposit appears in ORCID Works automatically.
- **recover-clinic.kr Publications page**: paste the HTML snippet from `_metadata/zenodo_published_index.md` Section 4 directly into the site CMS. 17 `<li>` entries, each is a DOI hyperlink + subject tag.
- **hanpredict.com Research / Publications page**: same HTML snippet. Suggest grouping by subject area (Pharmacology · Biophysics · Bioinformatics) for readability.
- **Verification step**: after auto-push, refresh ORCID profile and confirm 17 entries appear under Works > "Funding & Other works" or "Publications". If any record is missing, re-trigger the export from that specific Zenodo record's settings tab.

This is a user-side click-through task, ~10 minutes total. Genesis_Medicine cannot perform it from the API without Zenodo+ORCID credentials.

---

## 8. Cross-references

- Strategy parent doc: `preprints/POST_REJECTION_STRATEGY.md`
- Result handoff: `preprints/ZENODO_RESULT_HANDOFF.md`
- DOI canonical index: `preprints/_metadata/zenodo_published_index.md`
- Per-paper metadata: `preprints/_metadata/{NN}_{slug}_metadata.json` (each updated 2026-05-04 with `doi`, `doi_issued_date`, `zenodo_url`)
- Author-side clinic / IRB paperwork: out of scope; tracked in HAN PREDICT ops folder.

---

**End of roadmap.**
