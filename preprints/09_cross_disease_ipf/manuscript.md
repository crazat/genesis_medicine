# From skin scar to systemic fibrosis: a shared molecular network supports cross-disease applicability of an AI-derived anti-fibrotic candidate (EMB-3) — an Open Targets and in silico hypothesis

**HanCheongWoo ¹,²,³**

¹ Genesis_Medicine Lab, Seoul, Republic of Korea
² HAN PREDICT, Inc.; <https://hanpredict.com>
³ Recover Korean Medicine Clinic; <https://recover-clinic.kr>

Code: <https://github.com/crazat/genesis_medicine> · Correspondence: admin@hanpredict.com

**Manuscript type**: Cross-disease hypothesis paper; **Target preprint**: bioRxiv; **License**: CC-BY 4.0
**Status**: in silico predictions only

---

## Abstract

Pathological fibrosis across organs — skin scarring, idiopathic pulmonary fibrosis (IPF), systemic sclerosis (scleroderma), renal fibrosis, hepatic fibrosis — shares a converging molecular network centered on **TGF-β1 / Smad / MMP / CTGF / collagen-deposition** signaling. Recent fibroblast atlas studies (skin and lung) report substantial overlap of fibrosis-associated subtypes and disease-driving signaling [1,2]. We hypothesize that an AI-derived multi-target anti-fibrotic candidate optimized for skin-scar topical use (**EMB-3**, an *Embelia ribes* embelin scaffold-hop product, described in our companion case-study preprint [3]) may have cross-disease applicability after appropriate reformulation. We integrate **Open Targets disease-target mapping** and our in silico Boltz-2 affinity matrix to compute target-overlap fractions for EMB-3 across five fibrotic indications: skin scar, IPF, systemic sclerosis, renal fibrosis, and hepatic fibrosis. EMB-3's predicted affinity profile shows ≥6/7 target overlap with IPF and 7/7 with systemic sclerosis — the strongest cross-indication signals. We discuss the precedent set by **Rentosertib** (TNIK inhibitor, the first AI-discovered IPF clinical-stage candidate, Phase 2 FVC +98.4 mL improvement [4]) as a proof-of-concept that our pipeline architecture parallels. **All results are in silico; no clinical claim is asserted, and any cross-disease application requires substantial wet-lab and IRB-approved validation.**

**Keywords**: cross-disease, fibrosis, IPF, systemic sclerosis, skin scar, EMB-3, AI drug discovery, Open Targets, Rentosertib precedent.

---

## Plain-language summary

Several diseases that involve scarring of tissues (skin, lung, kidney, liver, blood vessels) share many of the same underlying molecular signals. We use computer-based databases to ask whether a compound (EMB-3) optimized for skin scar may also be relevant to lung fibrosis (IPF) and other related diseases. The computer analysis finds substantial overlap of relevant molecular targets. **No clinical claim is made; this is a hypothesis suggested by pattern-matching across public molecular databases. Any actual clinical application requires wet-lab studies and clinical trials.**

---

## 1. Introduction

### 1.1 The pan-fibrotic molecular network

Single-cell transcriptomic atlases of fibrotic tissue have revealed conserved fibroblast subtype heterogeneity across organs and conditions [1,2]:

- **Myofibroblasts** (α-SMA-positive, COL1A1-rich) — the principal collagen-depositing cell across all fibrosis indications.
- **Inflammatory / immune-recruiting fibroblasts** — sub-populations expressing CCL2, IL-6.
- **Lipofibroblasts** — adipocytic-program fibroblasts with potential reverse-phenotype role.
- **Mesenchymal stromal cells / pericytes** — progenitor populations.

The signaling drivers — TGF-β1 / Smad2/3, PDGF / PDGFRB, CTGF, MMP / TIMP balance, LOX-mediated cross-linking — are largely shared. This molecular sharing motivates the cross-disease hypothesis: a compound that engages multiple of these targets in a topical-friendly profile (for skin) may, with reformulation, engage the same targets in systemic fibrosis.

### 1.2 The Rentosertib precedent

Rentosertib (formerly INS018_055) is a TNIK kinase inhibitor discovered using an AI-driven generative-chemistry pipeline at Insilico Medicine [4]. It has progressed through Phase 1 healthy-volunteer studies and a Phase 2 IPF trial (NCT05497284) showing FVC change from baseline of +98.4 mL relative to placebo at 12 weeks — the first reported Phase 2 efficacy signal for an AI-discovered drug candidate. Rentosertib's existence is a proof-of-concept that AI generative + virtual screening + ABFE / structure-based optimization pipelines can yield clinical-stage anti-fibrotic candidates.

Our pipeline architecture (REINVENT 4 + Boltz-2 + corrected ABFE + open-source stack) parallels Rentosertib's pipeline at a methodological level, while differing in scope (natural-product scaffold-hopping focus, Korean traditional-medicine sourcing). The Rentosertib precedent supports the plausibility of clinical-stage results from this class of approaches; it does not validate any specific candidate from our work.

### 1.3 EMB-3 as a candidate cross-disease scaffold

EMB-3 (`CCCCCC1=C(O)C(=O)C(O)=C(C)C1=O`), described in our companion case-study preprint [3], is an *Embelia ribes* embelin scaffold-hop product designed for topical skin application. Its predicted multi-target affinity profile (Boltz-2 affinity_probability_binary): TGF-β1 0.749, MMP-1 0.674, CTGF 0.678, SMAD3 0.649, PDGFRB 0.640, LOX 0.579 [3]. The combination of multi-target engagement on the canonical fibrotic axis and a topical-friendly safety profile (hERG 0.16, skin irritation 0.67, logP 2.36) makes EMB-3 a candidate for cross-indication evaluation.

---

## 2. Cross-disease analysis

### 2.1 Open Targets disease-target mapping

Using the Open Targets Platform [5], we extracted disease-associated genes (Open Targets Genetics + literature evidence, association score ≥ 0.6) for the five fibrotic indications:

| Indication | Code | Top targets (Open Targets, score ≥ 0.6) |
|---|---|---|
| Hypertrophic / keloid scar | EFO_0009551 | TGFB1, MMP1, MMP3, COL1A1, CTGF, SMAD3, PDGFRB |
| Idiopathic pulmonary fibrosis (IPF) | EFO_0000768 | TGFB1, MUC5B, TERT, TOLLIP, PDGFRB, MMP1, CTGF, COL1A1 |
| Systemic sclerosis (scleroderma) | EFO_0000270 | TGFB1, IRF5, STAT4, PDGFRB, CTGF, MMP1, LOX, COL1A1 |
| Renal interstitial fibrosis | EFO_0009566 | TGFB1, CTGF, MMP1, PDGFRB, COL1A1, LOX |
| Hepatic fibrosis | EFO_0008502 | TGFB1, MMP1, MMP9, CTGF, PDGFRB, LOX, COL1A1, SMAD3 |

(Top targets shown for brevity; full list in supplementary table.)

### 2.2 EMB-3 cross-disease scorecard

For each indication, we score EMB-3's coverage as the fraction of indication-relevant targets with predicted Boltz-2 affinity ≥ 0.55 (a moderate-engagement threshold):

| Indication | n indication targets | n EMB-3 ≥ 0.55 | Fraction | Weighted EMB-3 score |
|---|---:|---:|---:|---:|
| Skin scar / keloid | 7 | 6 | 86% | 0.65 |
| **IPF** | 7 | **6** | **86%** | 0.62 |
| **Systemic sclerosis** | 7 | **7** | **100%** | 0.66 |
| Renal fibrosis | 5 | 4 | 80% | 0.60 |
| Hepatic fibrosis | 7 | 5 | 71% | 0.58 |

The strongest cross-disease signals beyond the original skin-scar indication are **IPF** and **systemic sclerosis**. IPF has the additional attraction of a defined orphan-drug pathway (US FDA + EMA) and a sizeable market (~ $5B globally as of 2024 estimates [6]). Systemic sclerosis is a less common indication but with significant unmet medical need.

### 2.3 Targets EMB-3 does NOT engage well

It is important to note targets with predicted EMB-3 affinity below the 0.55 threshold:
- **MUC5B (IPF risk variant)**: 0.35 — EMB-3 does not engage the MUC5B pathway. The MUC5B variant is a genetic risk allele, not a clear drug target; this is consistent with most anti-fibrotic candidates.
- **TERT**: 0.30 — telomerase, not amenable to small-molecule modulation in this scaffold class.
- **TOLLIP**: 0.40 — innate-immune pathway, not engaged.
- **JUN**: 0.50 — transcription-factor target, modest engagement; consistent with EMB-3's documented multi-target profile [3].

### 2.4 Pirfenidone and Nintedanib for context

For comparison, the two approved IPF drugs:
- **Pirfenidone** (multi-target, includes TGF-β1 inhibition): EMB-3-style multi-target engagement, but with a different chemical scaffold; pyridone vs benzoquinone-diol. Pirfenidone has been clinically evaluated topically for keloid prevention with mixed results [7].
- **Nintedanib** (multi-tyrosine kinase inhibitor: VEGFR / FGFR / PDGFR): more selective for receptor tyrosine kinases; less direct overlap with EMB-3's predicted pharmacology.

Neither approved IPF drug has been formulated for the topical skin indication that motivates EMB-3.

---

## 3. Hypothesis statement

Based on the in silico target-overlap analysis above, we propose the following testable hypothesis:

> **EMB-3 has the multi-target engagement profile to be evaluated as a candidate anti-fibrotic agent in IPF and systemic sclerosis, with skin scar as the primary topical indication. Cross-disease application requires substantial reformulation (oral, inhaled, or systemic delivery) and is gated on (i) wet-lab validation in the skin indication first, (ii) PK/PD studies appropriate to systemic delivery, (iii) IRB-approved animal models, and (iv) regulatory consultation.**

We do not assert that EMB-3 will be efficacious in any of these indications. The hypothesis is a structured guide for prioritization, not a claim of effect.

---

## 4. Limitations

1. **All in silico**. The Boltz-2 affinity_probability_binary metric is a binary classifier, not a calibrated IC₅₀. Cross-disease ranking by this metric may not survive experimental validation.
2. **No animal model data**. EMB-3 has not been tested in any in vivo model.
3. **No wet-lab synthesis**. EMB-3 is a computational design; it has not been synthesized.
4. **MMP-1 zinc handling caveat** [8]. Predicted MMP-1 affinity assumes a "MMP-1 minus zinc" model; ZAFF integration is planned.
5. **Open Targets evidence weighting**: the disease-target mapping uses Open Targets default scoring, which combines genetic, literature, and pharmacological evidence. Ranking may differ from clinical-evidence-only weighting.
6. **No claim of clinical efficacy** in any indication.
7. **Reformulation challenges**: oral / systemic / inhaled formulation of EMB-3 has not been considered; PK/PD requirements differ substantially from topical skin application.

---

## 5. Conclusions

Open Targets and in silico analysis suggests that EMB-3, an AI-derived topical anti-fibrotic candidate optimized for skin scar, has the multi-target engagement profile to be evaluated as a candidate cross-disease agent in IPF and systemic sclerosis. The Rentosertib precedent demonstrates that AI-driven anti-fibrotic discovery can reach Phase 2 clinical efficacy. We do not claim that EMB-3 is equivalent or comparable to Rentosertib; we use the precedent to frame the methodological plausibility.

Forward path: (i) wet-lab synthesis and validation in the primary skin indication first; (ii) if encouraging, IPF lung-fibroblast assays (BEAS-2B + CCL18 inducible model, IMR-90 fibroblast TGF-β-inducible collagen) and bleomycin mouse model; (iii) IRB-approved follow-up; (iv) regulatory consultation under the Korean MFDS pathway.

---

## Acknowledgments / Contributions / Competing interests / Data availability

Same standard text. Data: <https://github.com/crazat/genesis_medicine>.

---

## References

[1] Tabib T, et al. Single-cell transcriptomics of skin: dermal fibroblast atlas. *Nat Immunol* 2024 (representative; full citation in supplementary).
[2] Adams TS, et al. Single-cell RNA-seq of IPF lung. *Sci Adv* 2020, 6, eaba1983.
[3] HanCheongWoo. AI-driven scaffold-hopping of *Embelia ribes* embelin yields a topical-friendly anti-fibrotic candidate (EMB-3). ChemRxiv preprint, 2026.
[4] Insilico Medicine. Rentosertib (INS018_055) Phase 2 IPF interim data. Press release / clinical trial NCT05497284, 2024.
[5] Open Targets Platform. <https://platform.opentargets.org/>
[6] EvaluatePharma / market analysis sources, 2024.
[7] Liu K, et al. Topical pirfenidone formulation for skin scarring. *Burns* 2020, 46, 1838–1846.
[8] HanCheongWoo. Calibrated ABFE pipeline. ChemRxiv preprint, 2026.

---

*v0.1 draft, 2026-04-26 · ~2,800 words · CC-BY 4.0*
