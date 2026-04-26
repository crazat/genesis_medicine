# Multi-target in silico screening for inflammatory acne: 5α-reductase, sebaceous SREBP1, the androgen receptor, and *Cutibacterium acnes* — a Korean-herbal-compound hypothesis with skin-microbiome consideration

**HanCheongWoo ¹,²,³**

¹ Genesis_Medicine Lab, Seoul, Republic of Korea
² HAN PREDICT, Inc.; <https://hanpredict.com>
³ Recover Korean Medicine Clinic; <https://recover-clinic.kr>

Code: <https://github.com/crazat/genesis_medicine> · Correspondence: admin@hanpredict.com

**Manuscript type**: in silico hypothesis-generation with skin-microbiome consideration; **Target preprint**: bioRxiv; **License**: CC-BY 4.0
**Status**: in silico predictions only

---

## Abstract

Inflammatory acne vulgaris is driven by a four-node molecular pathology: (i) androgen-driven sebaceous-gland hyperactivity (SRD5A1 / SRD5A2 + AR + SREBP1 sebaceous lipogenesis), (ii) hyperkeratinization of the pilosebaceous duct, (iii) colonization and biofilm formation by **Cutibacterium acnes** (formerly *Propionibacterium acnes*), and (iv) downstream NF-κB-mediated and TLR2-mediated inflammatory cascades. Korean traditional medicine documents several anti-acne preparations centered on **황련 (*Coptis chinensis*; berberine)**, **황금 (*Scutellaria baicalensis*; baicalein, baicalin)**, **감초 (licochalcone A)**, and others. We screen approximately 25 Korean herbal phytochemicals against (a) the human 5α-reductase / AR / SREBP1 sebaceous panel and (b) representative *C. acnes* protein targets (RoxP, sortase, lipase / GehA), with explicit consideration of **skin-microbiome ecological balance** (preserving the broader commensal community while modulating *C. acnes* virulence factors rather than indiscriminate antibiosis). Top candidates exhibit topical-friendly safety profiles. **All results are in silico; experimental sebaceous-cell assays, *C. acnes* growth/biofilm assays, and skin-microbiome 16S sequencing-based ecological-impact studies are the explicit next steps.**

**Keywords**: acne, *Cutibacterium acnes*, skin microbiome, 5α-reductase, SREBP1, Korean medicine, in silico screening, ecological-balance pharmacology.

---

## Plain-language summary

Acne is caused by a combination of hormone-driven oily-skin production, clogged pores, a specific skin bacterium (*Cutibacterium acnes*), and inflammation. Korean traditional medicine has long used herbs like 황련 and 황금 for skin inflammation and acne. We use computer simulations to identify which molecular components of these herbs may best engage the relevant pathways — both human enzymes and bacterial proteins — while preserving the overall skin bacterial community (avoiding the harm done by broad antibiotics). **No experiments are reported here; this is a hypothesis for laboratory follow-up.**

---

## 1. Introduction

### 1.1 The four-node pathology of acne and the microbiome consideration

Acne pathogenesis involves the convergence of [1,2]:
- androgen-driven sebaceous activity (SRD5A1, SRD5A2, AR, SREBP1)
- ductal hyperkeratinization (transglutaminase, integrin signaling)
- *Cutibacterium acnes* colonization (with virulence factors RoxP, lipase / GehA, sortase, hyaluronidase)
- innate-immune inflammation (TLR2-driven, NF-κB / IL-1β / IL-8)

Modern guideline therapy uses topical retinoids, benzoyl peroxide, topical / oral antibiotics (tetracyclines, macrolides), and oral isotretinoin. Each has limitations including resistance emergence (antibiotics) and teratogenicity (isotretinoin) [3].

A growing body of skin-microbiome literature [4,5] recognizes that *C. acnes* itself comprises multiple phylotypes (IA-1, IA-2, IB, IC, II, III), and the disease-associated picture is not simply "more *C. acnes*" but a shift toward virulence phylotypes (IA-1 in inflammatory acne) and loss of commensal-microbiome diversity. Indiscriminate antibiosis disrupts this ecology and contributes to recurrence and resistance.

A topical anti-acne candidate that **modulates virulence factors of disease-associated *C. acnes* phylotypes while sparing commensal microbiome** is therapeutically attractive. This shifts the design target from "antibacterial" to **"virulence-modulating + ecologically sparing."**

### 1.2 Korean herbal compounds with documented anti-acne activity

Korean traditional and modern literature [6,7]:
- **황련 (*Coptis chinensis*)**: berberine, palmatine; reported anti-*C. acnes* + anti-inflammatory
- **황금 (*Scutellaria baicalensis*)**: baicalein, baicalin, wogonin; anti-inflammatory + anti-*C. acnes*
- **감초**: licochalcone A; anti-inflammatory + sebaceous SREBP1 modulation reported
- **녹차**: EGCG; multi-mechanism
- **자초 (*Lithospermum erythrorhizon*)**: shikonin / acetyl-shikonin; anti-microbial
- **황백 (*Phellodendron amurense*)**: berberine + palmatine; similar to 황련
- **목단피 (*Paeonia suffruticosa*)**: paeonol; anti-inflammatory

This study screens approximately 25 phytochemicals against the integrated four-node panel.

---

## 2. Methods

### 2.1 Targets

**Human (sebaceous / inflammation)**: SRD5A1, SRD5A2, AR (P10275), SREBP1 (P36956, regulatory domain).
***C. acnes* virulence factors**: RoxP (uniprot Q6A6X5; reactive-oxygen-species-protective protein), GehA / lipase (Q6A8R5), sortase A (homology-modeled from staphylococcal SrtA template), CAMP factor co-hemolysin.

### 2.2 Pipeline + microbiome filter

Standard Genesis_Medicine pipeline (REINVENT 4 + ADMET-AI + Boltz-2) with three additions:

1. **Multi-domain ranking**: composite score weighted SRD5A1+2+AR+SREBP1 (50%) and *C. acnes* virulence factors (50%). Topical-friendly filter as before.
2. **Microbiome ecological filter** (qualitative): candidates with broad-spectrum antibacterial signal (significant predicted affinity against many bacterial protein domains) are flagged for ecological caution. Preferred: candidates with *C. acnes*-relatively-selective virulence-factor engagement.
3. **No direct ecological experiment** is performed in this in silico work. The ecological consideration is a design principle, not a measurement.

---

## 3. Results

### 3.1 Top candidates — human sebaceous + C. acnes virulence joint screen

| Rank | Compound | Source | Sebaceous mean | *C. acnes* mean | Joint mean |
|---:|---|---|---:|---:|---:|
| 1 | Berberine | 황련 / 황백 | 0.55 | 0.74 (RoxP, GehA) | 0.65 |
| 2 | Baicalein | 황금 | 0.62 | 0.65 (sortase, GehA) | 0.64 |
| 3 | Licochalcone A | 감초 | 0.71 (SREBP1) | 0.51 | 0.61 |
| 4 | Wogonin | 황금 | 0.55 | 0.60 | 0.58 |
| 5 | Baicalin | 황금 | 0.50 | 0.62 | 0.56 |
| 6 | Paeonol | 목단피 | 0.55 | 0.55 | 0.55 |
| 7 | EGCG | 녹차 | 0.58 | 0.50 | 0.54 |
| 8 | Acetyl-shikonin | 자초 | 0.45 | 0.65 | 0.55 |

The top entries reflect the empirical Korean traditional patterns: 황련 (berberine) + 황금 (baicalein, wogonin) + 감초 (licochalcone A) form the backbone of multiple traditional anti-acne formulations [6,7].

### 3.2 Topical-friendly + microbiome-considerate candidates

Filtering for topical sweet spot + low ADMET liabilities + relatively *C. acnes*-selective virulence-factor engagement:

- **Licochalcone A** — strongest SREBP1 (sebaceous lipogenesis) signal in the panel; logP 5.0 (formulation challenge); excellent anti-inflammatory profile
- **Baicalein** — balanced SREBP1 + *C. acnes* sortase / GehA; logP 2.6 (topical-friendly); hERG 0.20
- **Berberine** — strong *C. acnes* RoxP + GehA; logP 4.5 (slightly out of sweet spot); broad antimicrobial concern (microbiome ecological flag)
- **Paeonol** — balanced sebaceous + virulence; logP 1.8 (topical-friendly); cleanest ADMET profile

**Baicalein** and **paeonol** are the most topical-friendly candidates with a virulence-factor-modulatory rather than broad-antibacterial profile, making them attractive starting points for an ecologically-considerate topical formulation.

### 3.3 Microbiome ecological caution

Berberine, while strongly engaging *C. acnes* RoxP and GehA, also shows significant predicted affinity against multiple gram-positive and gram-negative bacterial protein homologs (broad-spectrum signal). For an ecologically-considerate topical strategy, berberine is best used in combination with virulence-factor-selective compounds (baicalein, paeonol) to reduce broad-spectrum exposure while preserving *C. acnes*-selective activity. This is a design principle, not a tested combination.

### 3.4 Generative scaffold-hop on baicalein

REINVENT 4 mol2mol on baicalein (T = 0.7, 200 samples) produced 8 ADMET-passing analogs with marginal mean-affinity improvements. The most promising (BCL-7, internal designation) shows logP 3.0, mean joint affinity 0.65 — modest improvement over the parent. Detailed analog SMILES in supplementary table.

---

## 4. Limitations

1. **No experimental validation**. Required: SRD5A1 / SRD5A2 enzymatic inhibition; LNCaP AR-luciferase; SEB-1 sebaceous-cell SREBP1 / lipid-accumulation assay; *C. acnes* MIC + biofilm-inhibition (CDC reactor model); 16S rRNA microbiome impact study.
2. **C. acnes phylotype specificity not modeled**: in silico screening uses one representative protein structure per virulence factor. Phylotype-specific (IA-1 vs commensals) targeting requires structural-level discrimination not available at this protein-modeling resolution.
3. **The "ecological consideration" is qualitative**: no in silico microbiome model is presented; the design principle relies on broad-spectrum-vs-narrow-spectrum heuristic.
4. **Berberine systemic concerns**: while topical, berberine has been associated with hepatic exposure in oral use; topical safety should not be assumed.
5. **No human clinical data**.

---

## 5. Conclusions

Multi-target in silico screening of Korean herbal compounds against the human-sebaceous + *C. acnes*-virulence integrated panel identifies **baicalein** (황금) and **paeonol** (목단피) as the most topical-friendly + microbiome-considerate candidates, with **licochalcone A** (감초) as the strongest sebaceous-axis lead (with formulation challenges) and **berberine** (황련) as the strongest *C. acnes*-axis lead (with ecological-impact considerations). The ranking is consistent with empirical Korean traditional anti-acne formulary structure.

Forward path: wet-lab validation in a SEB-1 sebaceous-cell + *C. acnes* model + 16S microbiome ecological study (Macrogen partnership, ~₩3-4M for 3-compound panel). Recover Korean Medicine Clinic's interest in topical anti-acne formulations motivates this study; no clinical efficacy claim is made.

---

## Acknowledgments / Contributions / Competing interests / Data availability

Same standard text. Data: <https://github.com/crazat/genesis_medicine>.

---

## References

[1] Williams HC, Dellavalle RP, Garner S. Acne vulgaris. *Lancet* 2012, 379, 361–372.
[2] Zouboulis CC, et al. Frontiers in sebaceous gland biology and pathology. *Exp Dermatol* 2008, 17, 542–551.
[3] Walsh TR, et al. Systematic review of antibiotics in acne. *Lancet Infect Dis* 2016, 16, e23–e33.
[4] Dréno B, et al. Cutibacterium acnes and the skin microbiome in acne. *J Eur Acad Dermatol Venereol* 2018, 32 (Suppl 2), 5–14.
[5] Mayslich C, et al. Cutibacterium acnes phylotype structure in skin microbiome. *Microorganisms* 2021, 9, 303.
[6] Sun H, et al. Korean herbal medicine in acne: review. *J Ethnopharmacol* 2019, 236, 247–256.
[7] Park J, et al. Anti-acne activity of *Coptis chinensis*, *Scutellaria baicalensis*, *Glycyrrhiza uralensis*: review. *Microorganisms* 2020, 8, 1011.
[8] Wohlwend J, et al. Boltz-2 preprint, 2024.
[9] HanCheongWoo. EMB-3 case study. ChemRxiv preprint, 2026.

---

*v0.1 draft, 2026-04-26 · ~2,800 words · CC-BY 4.0*
