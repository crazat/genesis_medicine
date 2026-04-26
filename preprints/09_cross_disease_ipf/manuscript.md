# From skin scar to systemic fibrosis: Open Targets evidence and the limits of canonical anti-fibrotic axis-based cross-disease hypothesis (an EMB-3 in silico case)

**HanCheongWoo ¹,²,³**

¹ Genesis_Medicine Lab, Seoul, Republic of Korea
² HAN PREDICT, Inc.; <https://hanpredict.com>
³ Recover Korean Medicine Clinic; <https://recover-clinic.kr>

Code: <https://github.com/crazat/genesis_medicine> · Correspondence: admin@hanpredict.com

**Manuscript type**: Cross-disease hypothesis paper with Open Targets evidence audit; **Target preprint**: bioRxiv; **License**: CC-BY 4.0
**Status**: in silico predictions only; no clinical claim
**Version**: v0.2 (2026-04-26) — replaces v0.1 fabricated overlap percentages with real Open Targets queries

---

## Abstract (250 words)

Pathological fibrosis across organs — skin scarring, idiopathic pulmonary fibrosis (IPF), systemic sclerosis, renal fibrosis, hepatic fibrosis — is widely framed in medicinal-chemistry literature as sharing a converging **TGF-β / Smad / MMP / CTGF / collagen-deposition** master-switch network. We investigated whether this conceptual axis-sharing translates to evidence-based cross-disease applicability for an AI-derived multi-target candidate (**EMB-3**, an *Embelia ribes* embelin scaffold-hop, described in companion preprint [3]) by querying the **Open Targets Platform v4 GraphQL API** for both directions: (a) for each fibrotic indication, what targets are associated above OT score ≥ 0.4? (b) for each canonical anti-fibrotic target, what fibrotic-spectrum diseases are associated? **The results substantially temper the cross-disease hypothesis as initially framed**: only PDGFRB among 9 canonical anti-fibrotic targets shows consistent OT association (≥ 0.4) across fibrotic-spectrum diseases (IPF 0.59, systemic sclerosis 0.55, ILD 0.57, pulmonary fibrosis 0.56, dermatofibrosarcoma protuberans 0.57). Other canonical targets (TGFB1, MMP1, CTGF, SMAD3, MMP3/9, LOX, COL1A1) show ≤ 1 fibrotic disease above the threshold. The "TGF-β master-switch" axis is supported in review literature but is not mirrored in Open Targets genetic-evidence-weighted association scoring. The Rentosertib (TNIK inhibitor, IPF Phase 2) precedent demonstrates that AI-discovered anti-fibrotic candidates can reach clinical efficacy, but cross-disease translation requires evidence-grounded, not framework-asserted, target prioritization. **All EMB-3 affinity values are in silico; cross-disease translation requires substantial wet-lab validation.**

**Keywords**: cross-disease, fibrosis, IPF, Open Targets, EMB-3, evidence audit, PDGFRB, TGF-β master-switch.

---

## Plain-language summary

Diseases involving tissue scarring (skin scars, lung fibrosis, scleroderma, kidney/liver fibrosis) are often described as sharing the same underlying molecular signals. We checked the public Open Targets database to see how strongly that "shared signal" claim is supported by genetic and literature evidence. The honest answer is: **only one of the canonical anti-fibrotic targets (PDGFRB) shows strong evidence-based association with multiple fibrotic diseases.** The others (TGF-β1, MMP-1, CTGF, etc.) appear in fibrosis biology and review literature but are not strongly supported by Open Targets evidence aggregation. This is important because it tempers the original cross-disease hypothesis: a compound engaging the canonical axis may still be relevant in fibrotic disease, but the supporting argument is review-literature-based, not Open-Targets-database-based. **No clinical claim is made.**

---

## 1. Background and version note

This is **version 0.2** of the manuscript. Version 0.1 (2026-04-26 morning) included a "cross-disease scorecard" table claiming that EMB-3's predicted affinity profile overlapped 86% with IPF associated targets, 100% with systemic sclerosis, 80% with renal fibrosis, and 71% with hepatic fibrosis. Those percentages were not derived from a real Open Targets query — they were synthesized on the basis of memory of canonical anti-fibrotic targets. **We retract those v0.1 numbers explicitly.**

In v0.2, the cross-disease analysis is grounded in real Open Targets v4 GraphQL queries (`scripts/query_open_targets.py` and `scripts/query_target_to_diseases.py` in our open-source repository) executed on 2026-04-26.

---

## 2. The pan-fibrotic master-switch literature claim

Single-cell transcriptomic atlases of fibrotic tissue [1,2] and review literature [3,4] frame the molecular pathology of fibrosis across organs as converging on a shared **TGF-β1 / Smad2/3 / MMP / CTGF** master-switch. Key elements:

- **Myofibroblasts** (α-SMA-positive, COL1A1-rich) — collagen-depositing in skin, lung, kidney, liver, heart.
- **Driver signaling**: TGF-β1 / Smad, PDGF / PDGFRB, CTGF / CCN2 amplification.
- **Effector**: MMP / TIMP balance, LOX-mediated cross-linking, collagen accumulation.

This framework is widely cited and clinically influential — it underlies the development of TGF-β-targeting agents (Galunisertib), PDGFR inhibitors (Nintedanib for IPF), and anti-fibrotic small molecules in clinical pipeline. The framework is not wrong; the question is whether the framework's conceptual axis-sharing maps onto **evidence-based** cross-disease association (e.g., genetic variants, clinical-trial-validated targets, OMIM disease genes) at the resolution of single-target enrichment.

---

## 3. EMB-3 candidate profile (recap from companion preprint)

EMB-3 (`CCCCCC1=C(O)C(=O)C(O)=C(C)C1=O`) is an in silico-derived chain-truncated analog of embelin from *Embelia ribes* [3]. Its predicted multi-target affinity profile from Round-1 Boltz-2 cofold (`affinity_probability_binary` metric):

| Target | Boltz-2 affinity_probability_binary |
|---|---:|
| TGFB1 | 0.749 |
| MMP1 | 0.674 |
| CTGF | 0.678 |
| SMAD3 | 0.649 |
| PDGFRB | 0.640 |
| LOX | 0.579 |
| VEGFA | 0.563 |
| JUN | 0.497 |
| FGF2 | 0.484 |

Topical-friendly safety profile (logP 2.36, hERG 0.155, AMES 0.106) and 10 ns MD stability on MMP-1 (RMSD 0.79 Å). All values are in silico.

---

## 4. Open Targets query: forward direction (disease → targets)

### 4.1 Method

For each of 5 fibrotic indications, we queried the OT GraphQL endpoint for the top 50 associated targets ranked by overall association score. We then computed the overlap with EMB-3's predicted-binding profile (compounds with Boltz-2 affinity_probability_binary ≥ 0.55 considered "engaged"). Code: `scripts/query_open_targets.py`.

### 4.2 Results

| Indication (EFO ID) | n targets ≥ 0.4 score | n EMB-3 ≥ 0.55 affinity overlap | Overlap fraction |
|---|---:|---:|---:|
| Hypertrophic / keloid scar (EFO_0009551) | 31 | 0 | 0% |
| **Idiopathic pulmonary fibrosis** (EFO_0000768) | **26** | **1 (PDGFRB)** | **3.8%** |
| Systemic sclerosis (EFO_0000270) | — | — | (correct ID is EFO_0000717; see §5) |
| Renal interstitial fibrosis (EFO_0009566) | 50 | 0 | 0% |
| Hepatic fibrosis (EFO_0008502) | 0 | 0 | (low OT data coverage) |

### 4.3 Honest interpretation

The overlap fractions are **dramatically lower** than the v0.1 fabricated values. Inspection of the OT top-50 disease-target lists reveals why: OT scoring weights **genetic-evidence (loss-of-function, GWAS), somatic mutation, and curated literature evidence** — which surfaces disease-causing variants (TERT, MUC5B, PARN for IPF; ELN, FBN1 for keloid; NPHP3, IFT140 for renal fibrosis) and structural-gene defects, not necessarily the medicinal-chemistry-tractable "drug targets" emphasized in the master-switch literature.

The discrepancy is methodologically informative: **medicinal-chemistry "tractability targets" and OT "evidence-weighted disease genes" are largely disjoint sets** for fibrotic diseases. This is a non-trivial finding for the AI-driven anti-fibrotic discovery field.

---

## 5. Open Targets query: reverse direction (target → diseases)

### 5.1 Method

For 9 canonical anti-fibrotic master-switch targets, we queried OT for diseases associated at score ≥ 0.4 and filtered for fibrosis-spectrum disease names. Code: `scripts/query_target_to_diseases.py`.

### 5.2 Results

| Canonical target | n fibrotic-spectrum diseases (OT score ≥ 0.4) | Top hits |
|---|---:|---|
| **PDGFRB** | **6** | IPF (0.59), systemic scleroderma (0.55), ILD (0.57), pulmonary fibrosis (0.56), dermatofibrosarcoma (0.57), acroosteolysis-keloid syndrome (0.74) |
| TGFB1 | 1 | cystic fibrosis (0.44 only) |
| SMAD3 | 1 | coronary atherosclerosis (0.41) |
| MMP1 | 0 | (none ≥ 0.4) |
| MMP3 | 0 | (none ≥ 0.4) |
| MMP9 | 0 | (none ≥ 0.4) |
| CTGF / CCN2 | 0 | (none ≥ 0.4) |
| LOX | 0 | (none ≥ 0.4) |
| COL1A1 | 0 | (none ≥ 0.4) |

### 5.3 Honest interpretation

**PDGFRB is the only canonical anti-fibrotic target with consistent OT-fibrotic-disease association.** The other 8 canonical targets, despite their prominence in medicinal-chemistry review literature, are not enriched at the OT score ≥ 0.4 threshold for fibrotic-spectrum diseases. EMB-3's predicted affinity for PDGFRB is 0.640 (above our 0.55 engagement threshold), so PDGFRB is the **single canonical evidence-anchored cross-disease target** in EMB-3's profile.

(EFO_0000270 used in the v0.1 forward query was incorrect; the reverse query correctly identifies systemic scleroderma at EFO_0000717. Forward query in v0.2 should be repeated with this corrected ID; this is a planned refinement.)

---

## 6. The Rentosertib precedent

Rentosertib (formerly INS018_055) is a TNIK kinase inhibitor discovered by Insilico Medicine's AI-driven generative-chemistry pipeline [5]. It progressed through Phase 1 healthy-volunteer studies and a Phase 2 IPF trial (NCT05497284) with an FVC change from baseline of +98.4 mL relative to placebo at 12 weeks — the first reported Phase 2 efficacy signal for an AI-discovered drug candidate.

Rentosertib's existence is a proof-of-concept that AI generative + virtual screening + structure-based optimization can yield clinical-stage anti-fibrotic candidates. We note: **Rentosertib's target (TNIK) is itself not enriched in OT fibrotic disease association** (we re-queried; TNIK shows no fibrosis-spectrum association ≥ 0.4 in OT). This further supports the methodological observation that **OT-association enrichment and clinical-tractability are partially decoupled** for fibrotic targets — the Rentosertib clinical signal does not depend on TNIK being a "high-OT-evidence" disease gene.

By extension, EMB-3's path to a clinical signal does not require all of its canonical targets to be high-OT-evidence; it requires that the multi-target engagement, in vivo, modulates the fibrotic phenotype.

---

## 7. Restated cross-disease hypothesis (v0.2)

In light of the above, we restate the cross-disease hypothesis with appropriate hedging:

> **EMB-3's predicted multi-target engagement profile (TGFB1, MMP1, CTGF, SMAD3, PDGFRB) overlaps with the medicinal-chemistry-literature canonical anti-fibrotic master-switch axis. The most evidence-anchored single-target connection to fibrotic-spectrum disease (per Open Targets ≥ 0.4 association) is PDGFRB, which appears across IPF, systemic sclerosis, interstitial lung disease, pulmonary fibrosis, and acroosteolysis-keloid-syndrome. The remaining canonical targets (TGFB1, MMP1, CTGF, SMAD3, LOX) feature in fibrosis review literature but are not enriched in Open Targets disease-target associations at the same threshold. EMB-3 may therefore be considered for cross-disease evaluation primarily through the PDGFRB-anchored, multi-target-supportive axis, with the recognition that the multi-target engagement on the broader axis is hypothesis-level rather than evidence-anchored at the OT scoring level.**

This is a substantially more conservative claim than the v0.1 framing.

---

## 8. Limitations

1. **All EMB-3 affinity values are in silico** Boltz-2 binary classifier outputs.
2. **Open Targets coverage varies by disease**: hepatic fibrosis returned 0 hits, possibly due to ID mismatch (EFO_0008502) or low data coverage. Systemic sclerosis (EFO_0000270) was not found via that ID; correct EFO_0000717 should be used in a v0.3 refinement.
3. **OT score threshold ≥ 0.4 is a moderate threshold**; loosening to ≥ 0.2 might surface more associations but with weaker evidence.
4. **OT does not capture all evidence types**: OT integrates genetic, somatic, literature, drug, RNA-expression, animal-model evidence, but the weighting may underweight drug-target tractability evidence relevant to medicinal chemistry.
5. **No experimental validation** of EMB-3 in any fibrotic disease model.
6. **Reformulation challenges** for systemic delivery of EMB-3 are not addressed.

---

## 9. Conclusions

A real Open Targets v4 audit of the cross-disease hypothesis substantially tempers the v0.1 framing: only PDGFRB among the canonical anti-fibrotic master-switch targets shows consistent OT-fibrotic-disease association at score ≥ 0.4. EMB-3's predicted multi-target engagement remains compatible with the medicinal-chemistry-literature canonical axis, but cross-disease translation is anchored on PDGFRB rather than on a broad master-switch axis enriched in OT.

The Rentosertib precedent demonstrates that AI-discovered anti-fibrotic candidates can reach clinical efficacy without requiring all targets to be high-OT-evidence. EMB-3's clinical-translation hypothesis is therefore methodologically plausible but evidence-thin at the single-target level outside PDGFRB.

Forward path: (i) wet-lab synthesis of EMB-3, (ii) cell-based TGF-β1/Smad reporter and MMP-1 enzymatic assays (with explicit zinc handling per [6]), (iii) PDGFRB enzymatic / cellular assays, (iv) animal models in the primary skin indication first, (v) cross-disease evaluation in IPF lung-fibroblast models only after primary-indication signals are established.

---

## Acknowledgments / Contributions / Competing interests / Data availability

Same standard text. Open Targets queries: `scripts/query_open_targets.py`, `scripts/query_target_to_diseases.py`. Raw OT JSON + processed CSVs: `pilot/open_targets/` at <https://github.com/crazat/genesis_medicine>.

---

## References

[1] Tabib T, et al. Single-cell transcriptomics of skin: dermal fibroblast atlas. *Nat Immunol* 2024.
[2] Adams TS, et al. Single-cell RNA-seq of IPF lung. *Sci Adv* 2020, 6, eaba1983.
[3] HanCheongWoo. AI-driven scaffold-hopping of *Embelia ribes* embelin yields a topical-friendly anti-fibrotic candidate (EMB-3). ChemRxiv preprint, 2026.
[4] Wynn TA, Ramalingam TR. Mechanisms of fibrosis: therapeutic translation for fibrotic disease. *Nat Med* 2012, 18, 1028–1040.
[5] Insilico Medicine. Rentosertib (INS018_055) Phase 2 IPF interim data. NCT05497284, 2024.
[6] HanCheongWoo. Calibrated absolute binding free energy pipeline. ChemRxiv preprint, 2026.
[7] Open Targets Platform v4 GraphQL API. <https://platform.opentargets.org/api>

---

*v0.2 draft, 2026-04-26 · ~2,800 words · CC-BY 4.0*
*v0.1 (fabricated cross-disease percentages) explicitly retracted in §1*
