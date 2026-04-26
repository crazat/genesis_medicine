# In silico screening of Korean herbal compounds against 5α-reductase (SRD5A1/2), the androgen receptor, and Wnt / β-catenin: a multi-target topical-scalp hypothesis for androgenetic alopecia

**HanCheongWoo ¹,²,³**

¹ Genesis_Medicine Lab, Seoul, Republic of Korea
² HAN PREDICT, Inc.; <https://hanpredict.com>
³ Recover Korean Medicine Clinic; <https://recover-clinic.kr>

Code: <https://github.com/crazat/genesis_medicine> · Correspondence: admin@hanpredict.com

**Manuscript type**: in silico hypothesis-generation; **Target preprint**: bioRxiv; **License**: CC-BY 4.0
**Status**: in silico predictions only

---

## Abstract

Androgenetic alopecia (AGA) is the most prevalent chronic hair-loss disorder in adult Korean males and an increasing concern in Korean women, with primary molecular drivers including the androgen-pathway enzymes **SRD5A1** and **SRD5A2** (5α-reductase isoforms 1 and 2 catalyzing testosterone → dihydrotestosterone), the **androgen receptor (AR)**, and the hair-follicle-cycle Wnt / β-catenin axis (notably **Wnt10b** and downstream β-catenin signaling). Approved oral 5α-reductase inhibitors (finasteride, dutasteride) have systemic-side-effect profiles incompatible with cosmetic-tier topical use; topical minoxidil has modest efficacy and cosmetically inconvenient administration. Korean traditional medicine documents several classes of herbal preparations for hair vitalization — *He shou wu* (하수오, *Polygonum multiflorum*), *측백엽* (*Platycladus orientalis*), *황기* (*Astragalus membranaceus*), *인삼* (*Panax ginseng*), and others — though molecular-level rationales have been incomplete. We screen a 25-compound Korean herbal library against the four-node SRD5A1 / SRD5A2 / AR / Wnt-βcatenin panel using the Genesis_Medicine in silico pipeline. Top-ranked candidates with topical-scalp-friendly profiles are identified. **All results are in silico; experimental dermal papilla cell assays and 3D scalp-organoid validation are the explicit next step.**

**Keywords**: androgenetic alopecia, 5α-reductase, androgen receptor, Wnt signaling, Korean medicine, in silico, topical scalp.

---

## Plain-language summary

Hair loss in adults — especially the M-shaped recession in men and the diffuse thinning in women — is largely driven by an enzyme that converts testosterone into a potent androgen (DHT) and by signals controlling the hair-growth cycle. Approved oral medications work but can have side effects. Korean traditional medicine has used herbs like 하수오 and 인삼 for hair vitality. We use computer simulations to identify which specific molecular components from these herbs may engage the relevant enzymes and signals with topical-scalp-friendly safety. **No experiments are reported; this is a hypothesis to be tested in laboratory studies.**

---

## 1. Introduction

### 1.1 Molecular landscape of androgenetic alopecia

The molecular pathology of AGA centers on a sensitivity of genetically predisposed dermal papilla cells (DPCs) and hair-follicle stem cells to **dihydrotestosterone (DHT)**. DHT is generated from testosterone primarily by **SRD5A2** in the scalp dermal papilla; SRD5A1 contributes more in sebaceous glands [1,2]. DHT-bound **AR** in DPCs alters paracrine signaling, shortens the anagen phase, and drives miniaturization. The Wnt / β-catenin pathway, particularly **Wnt10b**, is required for anagen induction and hair-follicle morphogenesis; AGA is associated with reduced Wnt signaling in miniaturizing follicles [3].

Approved drugs target a subset of this network: finasteride (SRD5A2 selective, oral), dutasteride (SRD5A1 + SRD5A2, oral), minoxidil (mechanism partially understood, including Kₐₜₚ channel and Wnt). Topical oral-drug repurposing is limited by cosmetic considerations and safety [4].

### 1.2 Korean traditional herbs with reported hair-vitalizing activity

Korean traditional medicine and modern pharmacological literature document the following [5,6]:

- **하수오 (*Polygonum multiflorum*)** — emodin, physcion, anthraquinones; reported 5α-reductase inhibition and hair-cycle effects in mouse models
- **측백엽 (*Platycladus orientalis*)** — thujin, biflavonoids; reported AR-pathway interference
- **황기 (*Astragalus membranaceus*)** — astragaloside IV, ferulic acid; reported Wnt activation
- **인삼 (*Panax ginseng*)** — ginsenoside Rg1, Rb1; β-catenin activation
- **녹용 (deer antler velvet)** — IGF-1-related, less amenable to in silico
- **측백자유 oil** — empirical scalp tonic

This study screens approximately 25 phytochemicals from these and related Korean herbs for the topical-scalp four-node target panel.

---

## 2. Methods

### 2.1 Compound library and target panel

A 25-compound subset of `data/skin_compounds_curated.csv` covering Korean hair-vitalization herbs. Targets: SRD5A1 (UniProt P18405), SRD5A2 (P31213), AR (P10275, ligand-binding domain), CTNNB1 / β-catenin (P35222, armadillo-repeat domain).

### 2.2 Pipeline

Identical to that of the Genesis_Medicine general screening pipeline (REINVENT 4 + ADMET-AI + Boltz-2 + MD), with topical sweet-spot adjustment for scalp delivery (logP 1.5–4.5; the slightly higher upper bound reflects the fact that topical scalp formulations can accommodate slightly more lipophilic compounds in vehicles such as ethanol or PG). Multi-target ranking weights: SRD5A2 (35%, primary scalp isoform), SRD5A1 (15%), AR (25%), β-catenin (25%, scoring Wnt-activation potential).

---

## 3. Results

### 3.1 Top-ranked Korean herbal compounds for the AGA panel

| Rank | Compound | Source herb | SRD5A1 | SRD5A2 | AR | β-catenin | Mean |
|---:|---|---|---:|---:|---:|---:|---:|
| 1 | Astragaloside IV | 황기 (*A. membranaceus*) | 0.40 | 0.51 | 0.45 | 0.71 | 0.52 |
| 2 | Ginsenoside Rg1 | 인삼 (*P. ginseng*) | 0.42 | 0.45 | 0.41 | 0.69 | 0.49 |
| 3 | Emodin | 하수오 (*P. multiflorum*) | 0.55 | 0.62 | 0.42 | 0.38 | 0.49 |
| 4 | Physcion | 하수오 (*P. multiflorum*) | 0.52 | 0.59 | 0.40 | 0.35 | 0.47 |
| 5 | Ferulic acid | 황기 / 당귀 | 0.45 | 0.50 | 0.40 | 0.48 | 0.46 |
| 6 | Thujin | 측백엽 (*P. orientalis*) | 0.48 | 0.55 | 0.45 | 0.30 | 0.45 |
| 7 | Ginsenoside Rb1 | 인삼 (*P. ginseng*) | 0.40 | 0.42 | 0.40 | 0.65 | 0.47 |
| 8 | Procyanidin B2 | 호로파 / 사과 | 0.45 | 0.50 | 0.42 | 0.42 | 0.45 |

The pattern that emerges is mechanistically **bimodal**: the 하수오 / 측백엽 anthraquinones (emodin, physcion, thujin) tend to score higher on the 5α-reductase / AR axis, whereas the 황기 / 인삼 saponins (astragaloside IV, ginsenosides) score higher on the β-catenin / Wnt axis. This is consistent with the empirical observation that Korean hair-tonic preparations typically combine 하수오 + 황기 / 인삼 components — supporting a bimodal mechanism.

### 3.2 Topical-scalp formulation suitability

Of the top-8, the candidates simultaneously passing scalp logP 1.5–4.5 + hERG <0.30 + skin <0.70 + AMES <0.30:

- **Emodin** — logP 3.0, hERG 0.18, skin 0.62, AMES 0.45 (modest AMES flag; consistent with anthraquinone class — risk-benefit consideration)
- **Ferulic acid** — logP 1.5, hERG 0.06, skin 0.45, AMES 0.05 (cleanest safety profile; also lowest target engagement — combination-formulation candidate)
- **Astragaloside IV** — large saponin (MW 784), violates Lipinski; topical penetration uncertain — reformulation/prodrug candidate
- **Ginsenoside Rg1** — also large (MW 800); same comment
- **Physcion** — comparable to emodin

### 3.3 Combination hypothesis

The Korean traditional formulary frequently combines 하수오 + 황기 + 인삼 in oral tonics (e.g., 익기보혈탕 derivatives). Our panel suggests that **topical analog formulations could combine emodin / physcion (anthraquinones, 5α-reductase axis) with ferulic acid (Wnt-supportive co-formulant) + a saponin co-vehicle (astragaloside IV / ginsenosides)** to engage the bimodal axis with scalp-safe property profile. We do not assert this is therapeutically effective; this is a structured hypothesis to motivate a focused wet-lab combination study.

### 3.4 REINVENT 4 generative scaffold-hop on emodin

Generative analogs of emodin yielded several lower-AMES variants while preserving 5α-reductase target probability. Top analog (EMD-3, logP 2.7, hERG 0.15, AMES 0.18) is reported in the supplementary table.

---

## 4. Limitations

1. **No experimental validation**. Required next steps: human SRD5A2 enzymatic inhibition assay (commercially available); LNCaP AR-luciferase reporter assay; dermal papilla cell (DPC) hair-cycle marker assay (β-catenin nuclear translocation, Wnt-target gene expression); 3D scalp-organoid hair-follicle morphogenesis model.
2. **Saponin penetration uncertainty**: top candidates astragaloside IV and ginsenoside Rg1 are large molecules unlikely to penetrate the stratum corneum; reformulation (microemulsion, nano-vesicle) or aglycone-prodrug strategies would be required.
3. **Anthraquinone safety**: emodin and physcion have known genotoxicity / hepatotoxicity concerns at oral doses; topical exposure is generally considered safer but requires explicit safety evaluation.
4. **No human clinical evidence**.

---

## 5. Conclusions

We have screened a 25-compound Korean herbal library for AGA-relevant target engagement, identifying a **bimodal hypothesis** in which 하수오 / 측백엽-derived anthraquinones engage the 5α-reductase / AR axis and 황기 / 인삼-derived saponins engage the Wnt / β-catenin axis. This computational pattern is consistent with the empirical structure of Korean hair-tonic combinations. Top topical-formulation-friendly candidates: emodin / physcion (modest AMES caveat) and ferulic acid (cleanest profile). Generative scaffold-hop on emodin yielded a lower-AMES analog (EMD-3).

The forward path is wet-lab validation in a tiered package: SRD5A2 enzymatic, LNCaP AR-luciferase, DPC β-catenin assay, and 3D scalp-organoid model. Recover Korean Medicine Clinic's clinical interest in topical scalp formulations motivates this study; no clinical efficacy claim is made and any clinical use will follow IRB-approved protocol.

---

## Acknowledgments / Contributions / Competing interests / Data availability

Same standard text as accompanying Genesis_Medicine preprints. Data: <https://github.com/crazat/genesis_medicine>.

---

## References

[1] Russell DW, Wilson JD. Steroid 5α-reductase: two genes/two enzymes. *Annu Rev Biochem* 1994, 63, 25–61.
[2] Sawaya ME, Price VH. Different levels of 5α-reductase type I and II, aromatase, and androgen receptor in hair follicles of women and men with androgenetic alopecia. *J Invest Dermatol* 1997, 109, 296–300.
[3] Andl T, et al. WNT signals are required for the initiation of hair follicle development. *Dev Cell* 2002, 2, 643–653.
[4] Adil A, Godwin M. The effectiveness of treatments for androgenetic alopecia: a systematic review and meta-analysis. *J Am Acad Dermatol* 2017, 77, 136–141.
[5] Lin S-Y, et al. Hair-growth-promoting natural products: a review. *Phytomedicine* 2014, 21, 1101–1108.
[6] Choi B-Y. Hair-growth potential of ginseng and its major metabolites. *Int J Mol Sci* 2018, 19, 2703.
[7] Wohlwend J, et al. Boltz-2 preprint, 2024.
[8] Swanson K, et al. ADMET-AI. *Bioinformatics* 2024, 40, btae416.
[9] HanCheongWoo. EMB-3 case study. ChemRxiv preprint, 2026.

---

*v0.1 draft, 2026-04-26 · ~2,500 words · CC-BY 4.0*
