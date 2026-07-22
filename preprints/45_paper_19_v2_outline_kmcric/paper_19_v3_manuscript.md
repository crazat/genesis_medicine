---
title: "Korean Pharmacopoeia Herbal Natural-Product Repositioning onto MMP-1 Collagenase: A Five-Layer Analytical Pipeline Integrating ADMET Druggability, LLM-Driven Out-of-Distribution Retrosynthesis, KIOM Transcriptomic Overlay, Atomistic Zn²⁺ Mechanism, and a Korean-Specificity Capstone"
authors: ["Han, Cheongwoo"]
date: 2026-06-29
draft_version: 0.3
orcid: 0009-0004-4805-8815
---

# Korean Pharmacopoeia Herbal Natural-Product Repositioning onto MMP-1 Collagenase: A Five-Layer Analytical Pipeline Integrating ADMET Druggability, LLM-Driven Out-of-Distribution Retrosynthesis, KIOM Transcriptomic Overlay, Atomistic Zn²⁺ Mechanism, and a Korean-Specificity Capstone

**Author:** Cheongwoo Han (sole author), Independent Researcher, ORCID 0009-0004-4805-8815 (corresponding: crazat7@gmail.com)

**Status:** v0.3 working manuscript (2026-06-29). Layers 1–2 report verified computational results; Layers 3–5 are presented as the integrative analytical framework with the underlying public-resource citations. Companion to paper #19 v1 (Zenodo, 2026-05-04) and the paper_A MMP-1 NNP-reliability study.

---

## Abstract

Matrix metalloproteinase-1 (MMP-1, EC 3.4.24.7) is the Zn²⁺-dependent interstitial collagenase central to cutaneous photoaging, periodontitis, and tissue remodeling, yet decades of synthetic hydroxamate inhibitor development produced zero approved drugs, largely on toxicity and drug-likeness grounds. We ask whether Korean Pharmacopoeia herbal natural products (NPs) occupy a more favorable repositioning niche, and present a five-layer analytical pipeline applied to an 86-compound Korean herbal NP set. **Layer 1 (ADMET):** across 86 herbal NPs versus a 15-member synthetic MMP-1 hydroxamate/ChEMBL reference set, the herbal NPs are simultaneously more drug-like (mean QED 0.508 vs 0.385) and less predicted-mutagenic (mean ADMET-AI AMES 0.373 vs 0.773) — i.e. they occupy a more favorable ADMET niche than the synthetic inhibitor class despite their lower nominal target affinity. **Layer 2 (retrosynthesis):** an LLM-driven retron-library reasoning approach solves 34/86 (39.5%) of the macrocyclic/terpenoid/polycyclic Korean herbal scaffolds, versus 0/86 for a USPTO-template reaction engine (AiZynthFinder) — establishing the Korean Pharmacopoeia scaffold class as an out-of-distribution (OOD) case study for template-based retrosynthesis. **Layer 3** overlays the KIOM KORE-Map 1.1 RNA-seq transcriptomic resource (including its 2026 dyspepsia-formula expansion) onto MMP-1/collagen dermatology pathways. **Layer 4** specifies the atomistic Zn²⁺ binding-mode characterization protocol (Boltz-2 cofold + GFN2-xTB + neural-network-potential cross-validation) transferred from the companion paper_A framework. **Layer 5** is a Korean-specificity capstone combining Korean traditional formula constituents, the KIOM transcriptomic layer, and Korean-population skin-aging GWAS loci (FCRL5 wrinkle, OCA2 pigmentation). A three-source negative-finding audit (WHO TKDL, KISTI ScienceON, and the Korean medical-society literature) returns zero prior Korean-herbal × MMP-1 × LLM-retrosynthesis × omics-overlay integrations, defining the white-space niche this work occupies.

**Keywords:** Korean traditional medicine; natural products; MMP-1; matrix metalloproteinase; ADMET; QED; LLM retrosynthesis; out-of-distribution; KORE-Map; KIOM; drug repositioning; photoaging

---

## 1. Introduction

### 1.1 The repositioning case for Korean Pharmacopoeia natural products

Matrix metalloproteinase-1 is the rate-limiting interstitial collagenase initiating the degradation of fibrillar type-I/II/III collagen that underlies dermal photoaging, periodontal collagenolysis, and the remodeling component of several chronic diseases. Despite three decades of medicinal-chemistry effort, no selective MMP-1 inhibitor has reached approval: the hydroxamate chemotype (marimastat, batimastat, rebimastat) failed on musculoskeletal-syndrome toxicity driven by pan-MMP off-target binding and unfavorable drug-likeness. This motivates a repositioning question oriented not toward new synthetic warheads but toward chemotypes with intrinsically favorable absorption/toxicity profiles — a niche in which dietary and pharmacopoeial natural products are plausibly advantaged.

Korean Pharmacopoeia herbal natural products are an attractive, under-examined source: they carry centuries of human-exposure precedent, occupy distinctive macrocyclic/terpenoid/polycyclic scaffold space, and are embedded in a uniquely Korean research-resource ecosystem (KIOM transcriptomics, Korean-population dermatological genetics). This work extends paper #19 v1 (a Korean-herbal scaffold cross-reference) into a quantitative five-layer repositioning pipeline against MMP-1.

### 1.2 The five-layer pipeline

We integrate: (1) **ADMET druggability** profiling of 86 Korean herbal NPs against a synthetic MMP-1 inhibitor reference set; (2) **LLM-driven retrosynthesis** quantifying synthetic accessibility of the herbal scaffolds as an out-of-distribution benchmark against a USPTO-template engine; (3) a **KIOM KORE-Map transcriptomic overlay** linking herbal-ingredient cellular responses to MMP-1/collagen pathways; (4) an **atomistic Zn²⁺ binding-mode** characterization protocol transferred from the companion paper_A reliability framework; and (5) a **Korean-specificity capstone** combining Korean formula constituents, the KIOM transcriptomic layer, and Korean-population skin-aging GWAS loci.

### 1.3 Contributions

- A verified ADMET comparison establishing that Korean herbal NPs occupy a more drug-like, less-mutagenic niche than the synthetic MMP-1 hydroxamate class (Layer 1, §3.1).
- A verified out-of-distribution retrosynthesis benchmark: LLM-with-retron-library reasoning solves 39.5% of Korean herbal scaffolds where a USPTO-template engine solves 0% (Layer 2, §3.2).
- An integrative framework (Layers 3–5) connecting the verified chemoinformatic results to the KIOM transcriptomic resource, the paper_A atomistic Zn²⁺ pipeline, and Korean-population dermatological genetics.
- A three-source negative-finding audit quantifying the white-space niche (§1.4, §4).

### 1.4 Prior-art white space

A three-source audit (WHO Traditional Knowledge Digital Library; KISTI ScienceON; Korean medical-society literature) returned zero prior integrations of Korean herbal NPs × MMP-1 × LLM-retrosynthesis × KIOM omics overlay; the nearest historical hit is a 2019 *Astragalus*/*Lithospermum* composite MMP-inhibition report. The present pipeline therefore occupies a previously unreported four-domain intersection.

---

## 2. Methods

### 2.1 Compound sets
86 Korean Pharmacopoeia herbal natural-product compounds (paper #19 v1 base set) and a 15-member synthetic MMP-1 inhibitor / ChEMBL reference set. SMILES, identifiers, and per-compound endpoints are provided in the supplementary data.

### 2.2 ADMET druggability (Layer 1)
ADMET-AI (Chemprop-RDKit multi-endpoint model) was applied to both compound sets. We report QED (quantitative estimate of drug-likeness) and the predicted Ames mutagenicity probability (AMES) as the two headline druggability/safety endpoints; full endpoint tables are in the supplementary data. Group means were computed over the 86 herbal NPs and the 15 reference compounds separately. Source: `pilot/round7/admetai_combined.csv` (101 rows = 86 herbal + 15 reference).

### 2.3 LLM-driven retrosynthesis (Layer 2)
Each of the 86 herbal NPs was submitted to an LLM-driven retrosynthetic-disconnection procedure backed by a curated retron library, recording for each molecule a binary solved/unsolved verdict, the best disconnection, and the proposed precursors. The comparator was AiZynthFinder using a USPTO-derived reaction-template policy. A molecule was scored "solved" when a complete disconnection to commercially-plausible precursors was produced. Source: `pilot/cpu_meaningful/paper19_claude_retrosynthesis_v3.csv` (86 rows, `claude_solved` field).

### 2.4 KIOM KORE-Map transcriptomic overlay (Layer 3)
The KIOM KORE-Map 1.1 bulk RNA-seq resource (Korea Institute of Oriental Medicine; *BMC Genomic Data* 2026) — comprising 1,075 baseline profiles plus a 2026 dyspepsia-formula expansion (이중탕 / 반하사심탕 / 보중익기탕 / 사역탕 plus single-herb constituents) — is used as the transcriptomic substrate. Herbal-ingredient cellular-response signatures are mapped onto MMP-1 / collagen / dermatology pathway gene sets for hit-enrichment scoring. This layer is presented as the analytical framework with its public-resource citation; the enrichment computation is reserved for v1.0.

### 2.5 Atomistic Zn²⁺ mechanism (Layer 4)
Top herbal NPs prioritized by Layers 1 and 3 are routed to the companion paper_A atomistic stack: Boltz-2 protein–ligand cofold (25 reseed cycles × 100 diffusion samples per ligand) against the MMP-1 catalytic domain (UniProt P03956, residues 100–269), GFN2-xTB three-mode energetic refinement (gas / water-ALPB / mimetic ε=4.0) with the σ_E energy-reproducibility outlier-rescue protocol, and three-engine neural-network-potential consensus (Orb-v2, MACE-OMol25, Orb-v3-OMol25). This layer specifies the protocol; per-compound binding-mode results are reserved for v1.0.

### 2.6 Korean-specificity capstone (Layer 5)
For each top-prioritized herbal NP we ask (a) whether its constituent occurs within the KIOM dyspepsia-formula panel, and (b) whether Korean-population skin-aging GWAS loci — FCRL5 (rs117381658, wrinkle) and OCA2 (rs74653330, pigmentation) — are mechanistically reachable through the MMP-1 axis. The capstone is the conjunction of Korean formula constituent × Korean transcriptomic signature × Korean dermatological GWAS locus.

---

## 3. Results

### 3.1 Layer 1 — Korean herbal NPs occupy a more favorable ADMET niche than synthetic MMP-1 inhibitors

Across the 86 Korean Pharmacopoeia herbal NPs versus the 15-member synthetic MMP-1 inhibitor / ChEMBL reference set, the herbal NPs are **simultaneously more drug-like and less predicted-mutagenic**:

| Endpoint | Korean herbal NPs (n=86) | Synthetic MMP-1 reference (n=15) | Direction |
|---|---|---|---|
| QED (drug-likeness; higher = better) | **0.508** | 0.385 | herbal more drug-like |
| AMES (predicted mutagenicity; lower = safer) | **0.373** | 0.773 | herbal less mutagenic |

The QED advantage (0.508 vs 0.385) and the mutagenicity advantage (0.373 vs 0.773, i.e. roughly half the predicted Ames-positive probability) together place the Korean herbal NP set in a more translationally-favorable ADMET region than the synthetic hydroxamate inhibitor class — consistent with the historical failure mode of the synthetic class being toxicity/drug-likeness rather than potency. This is the quantitative basis for treating Korean Pharmacopoeia NPs as a repositioning-advantaged source against MMP-1. Source: `pilot/round7/admetai_combined.csv`.

### 3.2 Layer 2 — Korean herbal scaffolds are an out-of-distribution class for template retrosynthesis

LLM-driven retron-library retrosynthesis solved **34 of 86 (39.5%)** of the Korean herbal NP scaffolds, with the solved set dominated by tractable disconnections to commercially-plausible precursors; the unsolved 52/86 are concentrated in complex polycyclic/terpenoid scaffolds that require chemoenzymatic rather than standard organic-chemistry routes. The USPTO-template comparator (AiZynthFinder) solved **0 of 86**. This 39.5%-vs-0% split establishes the Korean Pharmacopoeia scaffold class as **out-of-distribution relative to USPTO reaction templates**, and demonstrates that LLM-with-retron-library reasoning extends usefully into a scaffold class where reaction-template engines fail entirely. Source: `pilot/cpu_meaningful/paper19_claude_retrosynthesis_v3.csv` (`claude_solved`: 34 True / 52 False).

### 3.3 Layer 3 — KIOM transcriptomic overlay (framework)

The KIOM KORE-Map 1.1 resource provides the first Korean-traditional-medicine RNA-seq substrate for bridging herbal ingredients to the MMP-1/collagen mechanism, including its 2026 dyspepsia-formula expansion. The overlay maps herbal-ingredient cellular-response signatures onto MMP-1/collagen/dermatology pathway gene sets; the dyspepsia-formula sub-layer (e.g. 보중익기탕, central-qi tonification) introduces a candidate cross-tissue 비위-ECM rationale. The enrichment computation against this public resource is the principal v1.0 deliverable.

### 3.4 Layer 4 — atomistic Zn²⁺ binding mode (protocol)

Top herbal NPs prioritized by Layers 1 and 3 enter the paper_A atomistic stack (§2.5). The expected deliverables are (i) confirmation or exclusion of the σ_E energy-reproducibility outlier signature for chelator-bearing herbal NPs, (ii) per-ligand hydroxamate-isosteric Zn²⁺ coordination geometry, and (iii) three-NNP consensus ranking. Per-compound results are reserved for v1.0 and are not claimed here.

### 3.5 Layer 5 — Korean-specificity capstone (framework)

The capstone conjoins, for each prioritized herbal NP, the Korean formula-constituent membership, the KIOM transcriptomic signature, and reachability of the Korean-population GWAS loci (FCRL5 wrinkle; OCA2 pigmentation) through the MMP-1 axis. Without this layer the study would be one of many global NP-MMP-1 repositioning analyses; with it, the work becomes a Korean-ecosystem-anchored case study that is structurally difficult to reproduce outside the Korean research corridor.

---

## 4. Discussion

The two verified layers carry the central claim: Korean Pharmacopoeia herbal NPs are **ADMET-advantaged** relative to the synthetic MMP-1 inhibitor class (Layer 1: QED 0.508 vs 0.385; AMES 0.373 vs 0.773) while being **synthetically tractable through LLM reasoning where template engines fail** (Layer 2: 39.5% vs 0%). Together these reframe Korean herbal NPs from anecdotal traditional-use candidates into a quantitatively-characterized, repositioning-advantaged chemotype source for MMP-1.

The integrative layers (3–5) position this chemoinformatic result inside the Korean research ecosystem — the KIOM transcriptomic resource, the paper_A atomistic Zn²⁺ pipeline, and Korean-population dermatological genetics. The three-source negative-finding audit (§1.4) confirms that this specific four-domain integration is previously unreported.

**Limitations.** (1) Layers 3–5 are presented as framework with public-resource citations; their per-compound computations (transcriptomic enrichment, atomistic binding modes, capstone conjunction) are v1.0 deliverables and are not claimed as results here. (2) ADMET endpoints are model predictions, not assays. (3) The retrosynthesis "solved" verdict reflects disconnection plausibility, not executed synthesis. (4) MMP-1 affinity of the herbal NPs is not established in this work; the contribution is the repositioning-niche characterization, not a potency claim. (5) No compounds are synthesized and no biological activity is claimed.

---

## 5. Conclusion

Korean Pharmacopoeia herbal natural products occupy a more drug-like (QED 0.508 vs 0.385) and less predicted-mutagenic (AMES 0.373 vs 0.773) niche than the synthetic MMP-1 hydroxamate inhibitor class, and their distinctive scaffolds are out-of-distribution for template retrosynthesis (LLM 39.5% vs template 0%). Embedded in the KIOM transcriptomic resource, the paper_A atomistic Zn²⁺ pipeline, and Korean-population skin-aging genetics, these results define a Korean-ecosystem-anchored, white-space repositioning framework for MMP-1-mediated dermatological indications. The per-compound transcriptomic, atomistic, and capstone computations are the v1.0 deliverables.

---

## References (selected)

1. KIOM. **KORE-Map 1.1 — Korea Institute of Oriental Medicine bulk RNA-seq resource for Korean medicine pharmacology** (with 2026 dyspepsia-formula expansion). *BMC Genomic Data* 2026. DOI 10.1186/s12863-026-01409-7.
2. Swanson K, et al. **ADMET-AI: a machine learning ADMET platform for evaluation of large-scale chemical libraries**. *Bioinformatics* 2024;40(7):btae416.
3. Genheden S, et al. **AiZynthFinder: a fast, robust and flexible open-source software for retrosynthetic planning**. *J Cheminform* 2020;12:70.
4. Companion paper_A — Cross-validation of neural-network potentials for MMP-1 Zn active-site inhibitor ranking (Boltz-2 + GFN2-xTB + 3-NNP). Zenodo 2026.
5. paper #19 v1 — Korean herbal scaffold cross-reference. Zenodo 2026-05-04.
6. Korean-population skin-aging GWAS (FCRL5 rs117381658 wrinkle; OCA2 rs74653330 pigmentation). *Applied Sciences* 2022, with 2026 East Asian MR extension.

---

## Data and code availability
- Layer 1 ADMET: `pilot/round7/admetai_combined.csv` (86 herbal + 15 reference).
- Layer 2 retrosynthesis: `pilot/cpu_meaningful/paper19_claude_retrosynthesis_v3.csv`.
- Layer 3 resource: KIOM KORE-Map 1.1 (public, BMC Genomic Data 2026).

## Author contributions
Cheongwoo Han: conceptualization, computation, analysis, writing (sole author).

## Competing interests
The author is founder of HAN PREDICT, Inc. No external funding. In-silico only; no wet-lab or patient data.

## Version
- v0.1 (2026-05-20) 1-page outline.
- v0.2 (2026-05-22) 5-layer expansion (outline).
- **v0.3 (2026-06-29) full working manuscript: Layers 1–2 verified results (ADMET QED/AMES n=86 vs n=15; retrosynthesis 34/86 vs 0/86), Layers 3–5 framework.**
