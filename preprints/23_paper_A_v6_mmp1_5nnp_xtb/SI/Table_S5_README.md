# Supplementary Table S5 — Sulfonamide-Diuretic Class MMP-1 Audit (n=17)

## Purpose

Standalone CSV companion to **Section 5.4** of paper_A v6 manuscript:
"Sulfonamide-diuretic class extension (out-of-distribution hypothesis test) — n=17 systematic audit"

Full per-compound ChEMBL bioactivity audit against MMP-1 (ChEMBL target ID 332) for the 17 FDA-approved sulfonamide diuretics covering thiazide, thiazide-like, loop, and carbonic-anhydrase-inhibitor subclasses.

## Data provenance

- **Database**: ChEMBL (release v33+ as queried 2026-05-19)
- **Query infrastructure**: `chembl_webresource_client` Python API — `chembl_webresource_client.new_client.activity` filtered by target_chembl_id='CHEMBL332' (MMP-1) per compound ChEMBL ID
- **Query script**: `/tmp/sulfa_diuretic_mmp1_query.py` (working copy retained 2026-05-19, see also paper_A references.md entry 77)
- **Raw output**: `/tmp/sulfa_diuretic_results.json`

## Field definitions

| Column | Definition |
|--------|-----------|
| `rank` | Display order in paper_A v6 Section 5.4 main-text table |
| `compound` | Common drug name (INN) |
| `chembl_id` | ChEMBL compound identifier |
| `subclass` | Pharmacological subclass (thiazide / thiazide-like / loop / carbonic_anhydrase_inhibitor) |
| `mmp1_chembl332_records` | Count of bioactivity records returned by ChEMBL query against ChEMBL332 |
| `record_status` | `zero_records` (no MMP-1 bioactivity entry whatsoever) or `DrugMatrix_qualitative_value_None` (single-concentration screen with `standard_value=None`, no extractable IC50/Ki) |
| `quantitative_ic50_ki` | Yes/No — whether any quantitative IC50 or Ki measurement is extractable. **For all 17 = No.** |
| `tanimoto_to_indapamide_morgan_r2_2048` | Morgan fingerprint Tanimoto similarity (radius 2, 2048 bits) to indapamide (CHEMBL406); used to confirm scaffold-similarity is NOT the basis of class extension |
| `wetlab_priority` | Recommended ranking for follow-up wet-lab cofold + xtb refinement work — P1 (top), P2, P3, P4 (out-of-target) |
| `structural_isostery_note` | One-line pharmacophore observation |

## Key findings (cross-referenced in manuscript Section 5.4)

- **17/17 zero quantitative MMP-1 IC50/Ki measurements**
- **9/17 carry no MMP-1 binding records whatsoever** (Zidapamide, Clopamide, Xipamide, Quinethazone, Bendroflumethiazide, Hydroflumethiazide, Methyclothiazide, Polythiazide, Bumetanide)
- **8/17 carry only single-concentration qualitative DrugMatrix panel entries** (Indapamide, Chlortalidone, Metolazone, Hydrochlorothiazide, Trichlormethiazide, Furosemide, Torsemide, Acetazolamide)
- **Tanimoto similarity to indapamide < 0.40 across 14/14 non-reference compounds** — confirms class boundary defined by *shared pharmacophore* (Ar–SO₂NH₂ + adjacent H-bond donor / chloro substituent SMARTS substructure), not whole-molecule scaffold similarity
- **Priority wet-lab candidate**: Xipamide (CHEMBL517199, P1) — structurally closest to indapamide (chlorobenzenesulfonamide + 2,6-dimethylaniline carboxamide preserves indapamide's Cl-Ar-SO₂NH₂ + adjacent carbonyl H-bond acceptor pharmacophore)

## Patent landscape freedom-to-operate (cross-reference Section 5.4 footnote)

All 17 compounds have composition-of-matter patents long expired (generic FDA-approved status). Patent landscape audit (Lens.org + Google Patents + Espacenet + USPTO, 2026-05-19) identified six prior MMP-inhibitor sulfonamide patent families (EP1208092A4, US 6,548,667, US 6,297,247, US 6,153,612, US 5,977,141, US 5,859,061, CA 2,719,457 — see references 65-70). All claim *newly synthesized* sulfonamide chemotypes and do **not** extend to the existing FDA-approved sulfonamide-diuretic chemotype repositioning claim space.

## Open Targets Platform 26.03 EMA+PMDA-inclusive cross-validation (queried 2026-05-20)

Independent cross-validation of the n=17 audit via **Open Targets Platform release 26.03** (released 2026-03-23; references 78-80) — a six-source unified GraphQL-queryable resource combining ClinicalTrials.gov AACT v2, ChEMBL 36, Therapeutic Target Database (TTD), EMA Human Drugs Database, PMDA approvals, DailyMed, and the ChEMBL drug-warnings table.

**MMP-1 (Ensembl ENSG00000196611) known drug entities in OT 26.03 = 5**:
- Marimastat (CHEMBL279785, Phase 3 lung/pancreas/breast cancer)
- Doxycycline (CHEMBL1200699, APPROVED — periodontitis/rosacea/acne + 165 other indications)
- Doxycycline hyclate (CHEMBL3989740)
- Doxycycline calcium (CHEMBL2364574)
- Rebimastat (CHEMBL76222, Phase 3 oncology)

**Cross-validation outcomes against n=17**:
- **0/17 sulfonamide diuretics overlap** with MMP-1's drug list
- **17 compounds MoA targets** map exclusively to SLC12A3 (thiazide/thiazide-like), SLC12A1 (loop), CA1/CA2/CA4/CA12 (acetazolamide) — **none lists MMP1**
- **0 ongoing MMP-1 clinical trials** for any of the 17 compounds
- **0 newly-discovered MMP-1 trial signal** that would update Section 5 narrative
- **Zidapamide (CHEMBL6378) absent from OT 26.03 entirely** — consistent with withdrawal from active research catalogues; paper_A v6 main text flags this explicitly

**Bumetanide / Acetazolamide oncology trials documented but NOT MMP-1 annotated**: Bumetanide HCC Phase 1-2 (CV/autism/AD/Down/T2DM/HCC); Acetazolamide HCC Phase 3 + SCLC Phase 1 (glaucoma/altitude/HCC/SCLC/MS/migraine). These oncology indications are documented in OT 26.03 but registered against carbonic anhydrase and SLC12 family targets, not MMP1.

**Net audit conclusion** (six-source EMA+PMDA-inclusive): The ChEMBL-only claim "0/17 sulfonamide diuretics have any quantitative MMP-1 IC50/Ki determination" is **independently corroborated** by OT 26.03; no new ongoing MMP-1 trial signal identified that would update Section 5 narrative.

API endpoint: `https://api.platform.opentargets.org/api/v4/graphql`
MMP-1 target page: `https://platform.opentargets.org/target/ENSG00000196611`

## Citation

When citing this Supplementary Table S5, reference paper_A v6 main manuscript Section 5.4 + this Supplementary README.

## Version

- v0.1 (2026-05-20, D-10 acceleration of D-3 deliverable)
- Source data freeze: ChEMBL query 2026-05-19
- Patent freeze: 2026-05-19
- Authors: Cheongwoo Han (ORCID 0009-0004-4805-8815)
