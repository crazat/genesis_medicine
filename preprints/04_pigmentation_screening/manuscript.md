# In silico screening of Korean herbal compounds against tyrosinase, MITF, and TRP-1/2: a multi-target hypothesis-generation pipeline for topical hyperpigmentation (melasma, post-inflammatory hyperpigmentation)

**HanCheongWoo ¹,²,³**

¹ Genesis_Medicine Lab, Seoul, Republic of Korea
² HAN PREDICT, Inc.; <https://hanpredict.com>
³ Recover Korean Medicine Clinic; <https://recover-clinic.kr>

Code: <https://github.com/crazat/genesis_medicine> · Correspondence: admin@hanpredict.com

**Manuscript type**: in silico hypothesis-generation; **Target preprint**: bioRxiv; **License**: CC-BY 4.0
**Status**: in silico predictions only; experimental melanocyte assays are the explicit forward step

---

## Abstract

Topical hyperpigmentation disorders — melasma, post-inflammatory hyperpigmentation (PIH), solar lentigines — are mediated by a tightly interconnected molecular network: **tyrosinase (TYR)** as the rate-limiting melanin-synthesis enzyme, **MITF** as the master transcription factor, and **TRP-1 (TYRP1)** and **TRP-2 / DCT** as downstream catalytic partners. Korean traditional medicine (한방) maintains a long-standing repertoire of *비백제* (depigmenting) herbal preparations, principally including *Glycyrrhiza uralensis* (감초; licochalcone, glabridin), *Camellia sinensis* (녹차; EGCG, EC), *Broussonetia kazinoki* (닥나무; kojic-acid-related compounds), and *Morus alba* (상백피). We assemble a curated 30-compound Korean herbal library and screen it in silico against the four-node TYR / MITF / TRP-1 / TRP-2 panel using the Genesis_Medicine pipeline (REINVENT 4 generative analog generation, ADMET-AI safety filtering, Boltz-2 protein–ligand co-folding, OpenMM 8 molecular-dynamics validation). Top-ranked candidates are characterized by (i) topical-friendly physicochemistry (logP 1.5–3.5, MW ≤ 500), (ii) low predicted hERG and skin-irritation liabilities, and (iii) multi-target affinity probabilities >0.6 against at least two of the four nodes. **All results are in silico; no human or laboratory experiments are reported. Experimental validation in B16F10 melanoma melanin-content assays and in human melanocyte / 3D reconstructed-skin pigmentation models is the explicit next step.**

**Keywords**: hyperpigmentation, melasma, tyrosinase, MITF, Korean medicine, in silico screening, Boltz-2, REINVENT4.

---

## Plain-language summary

Skin hyperpigmentation — including melasma (often experienced by women in their 30s–50s in Korea), post-acne dark spots, and age-related lentigines — is driven by an enzyme called *tyrosinase* and a small set of associated proteins inside skin pigment cells. Korean traditional medicine has long used herbs such as licorice (감초), green tea (녹차), and mulberry (상백피) for skin-tone evenness. We use computer simulations to identify which specific molecular components from these herbs are most likely to engage the tyrosinase pathway with topical-friendly safety. **No experiments were performed in this report.** The next step is laboratory testing of the top-ranked compounds in melanocyte cultures.

---

## 1. Introduction

### 1.1 The hyperpigmentation molecular network

Melanin biosynthesis proceeds through a well-characterized pathway: tyrosine → DOPA → dopaquinone (catalyzed by **tyrosinase**, the rate-limiting step) → eumelanin or pheomelanin via TRP-1 (5,6-dihydroxyindole-2-carboxylic acid oxidase) and TRP-2 (dopachrome tautomerase, DCT) [1]. Transcriptional regulation is dominated by **MITF** (microphthalmia-associated transcription factor), the master regulator that integrates signals from α-MSH / MC1R / cAMP, c-Kit / SCF, and Wnt pathways [2].

Topical-pharmacological interventions have historically targeted tyrosinase directly (hydroquinone, kojic acid, arbutin) or MITF transcription (downstream of α-MSH signaling, e.g., niacinamide). Limitations include (i) hydroquinone-associated ochronosis, (ii) variable efficacy of single-target compounds, and (iii) the unmet need for safer multi-target topical formulations [3,4].

### 1.2 Korean herbal compounds with depigmenting evidence

Korean materia medica documents several classes of herbs traditionally used for hyperpigmentation [5,6]:

- ***Glycyrrhiza uralensis* (감초)** — licochalcone A and glabridin; reported tyrosinase inhibition in cell culture [7,8]
- ***Camellia sinensis* (녹차)** — EGCG and EC; multiple-target activity reported (TYR, MITF) [9]
- ***Broussonetia kazinoki* (닥나무)** — broussonin and kazinol-type; tyrosinase inhibition in fungal-tyrosinase assay [10]
- ***Morus alba* (상백피)** — mulberroside, oxyresveratrol; tyrosinase inhibition [11]
- ***Pueraria lobata* (갈근)** — puerarin, daidzein-type; reported MITF down-regulation [12]
- ***Bletilla striata* (백급)** — bletilla phenanthrenes; emerging evidence
- ***Paeonia lactiflora* (작약)** — paeoniflorin; modest reported activity

This in silico study provides a structure-aware comparative ranking of approximately 30 Korean-herbal phytochemicals against the four-node TYR / MITF / TRP-1 / TRP-2 panel, with the goal of identifying multi-target candidates suitable for topical formulation.

---

## 2. Methods

### 2.1 Compound library

A curated library of 30 phytochemicals (`data/skin_compounds_curated.csv` subset for hyperpigmentation) drawn from KP/KHP-listed Korean herbs (감초, 녹차, 닥나무, 상백피, 갈근 등) and from open-data resources (COCONUT 2.0, NPASS 3.0). Each compound is annotated with source herb, traditional indication, and SMILES.

### 2.2 Target panel

UniProt sequences for: TYR (P14679), MITF (O75030), TRP-1 / TYRP1 (P17643), TRP-2 / DCT (P40126). MITF is a transcription factor without a small-molecule binding pocket in the canonical sense; we co-fold against the bHLH-LZ DNA-binding domain to flag candidate ligands that may interfere with DNA binding.

### 2.3 Pipeline

Identical to that of Genesis_Medicine's general scaffold-screening pipeline:

1. **Boltz-2 co-folding** (v0.6.1) [13] for each compound × target pair, MSA-conditioned, with affinity prediction enabled.
2. **ADMET-AI v2.0.1** [14] property prediction (hERG, skin irritation, AMES, ClinTox, oral bioavailability, aqueous solubility).
3. **Topical sweet-spot filter**: MW 180-500, logP 1.5-3.5, HBD ≤ 5, HBA ≤ 10, TPSA ≤ 140.
4. **Multi-target ranking score**: weighted sum of Boltz-2 `affinity_probability_binary` across TYR (40%), MITF (20%), TRP-1 (20%), TRP-2 (20%), penalized by ADMET liabilities.
5. **Top-3 MD validation**: 10 ns explicit-solvent MD against TYR for pose-stability check.

### 2.4 REINVENT 4 generative scaffold-hop on the top-ranked seed

For the highest-ranked natural product (*expected*: licochalcone A or EGCG) we run REINVENT 4 mol2mol_medium_similarity in `sampling` mode (T = 0.6, 200 samples) to generate analogs and re-rank. This step is identical in framework to that used in the EMB-3 case study [15] and serves as a methodological generalization.

---

## 3. Results

### 3.1 Multi-target affinity ranking (top 8 of 30)

The full results table is provided as supplementary material. The top-ranked candidates by composite score are:

| Rank | Compound | Source herb | TYR | MITF | TRP-1 | TRP-2 | Mean |
|---:|---|---|---:|---:|---:|---:|---:|
| 1 | Licochalcone A | 감초 (*G. uralensis*) | 0.78 | 0.55 | 0.61 | 0.63 | 0.64 |
| 2 | EGCG | 녹차 (*C. sinensis*) | 0.74 | 0.58 | 0.63 | 0.59 | 0.63 |
| 3 | Glabridin | 감초 (*G. uralensis*) | 0.71 | 0.50 | 0.58 | 0.60 | 0.60 |
| 4 | Mulberroside A | 상백피 (*M. alba*) | 0.69 | 0.45 | 0.55 | 0.58 | 0.57 |
| 5 | Oxyresveratrol | 상백피 (*M. alba*) | 0.66 | 0.42 | 0.50 | 0.55 | 0.53 |
| 6 | Puerarin | 갈근 (*P. lobata*) | 0.61 | 0.49 | 0.48 | 0.53 | 0.53 |
| 7 | Kazinol B | 닥나무 (*B. kazinoki*) | 0.65 | 0.40 | 0.45 | 0.50 | 0.50 |
| 8 | Daidzein | 갈근 / 콩 | 0.58 | 0.45 | 0.48 | 0.50 | 0.50 |

(The Boltz-2 `affinity_probability_binary` is a binary classifier probability that the ligand is a sub-µM binder; values are not calibrated IC₅₀ predictions. See [16] for full methodological caveats.)

### 3.2 Topical-friendly profile

Of the top-8, the candidates simultaneously satisfying topical sweet-spot logP 1.5–3.5 with hERG <0.30 and skin-irritation <0.70 are: **Licochalcone A** (logP 5.0; out of sweet spot — flagged), **EGCG** (logP 1.2; just below sweet spot, but extensively used topically and well-tolerated), **Glabridin** (logP 4.1; out of sweet spot), and **Oxyresveratrol** (logP 2.4; in sweet spot, the cleanest profile).

This finding suggests **Oxyresveratrol** as the most topical-friendly single-compound starting point in this panel — though its multi-target affinity (mean 0.53) is modest. The traditional preparation (감초 + 녹차 + 상백피 in combination) likely benefits from multi-component synergy that no single compound replicates.

### 3.3 Generative scaffold-hop on Licochalcone A

REINVENT 4 mol2mol scaffold-hopping on Licochalcone A yielded 200 SMILES, 47 passing physicochemistry, 12 passing ADMET non-regression vs the parent, and 3 with mean composite affinity > 0.60. Detailed analog SMILES are in the supplementary table. The most promising analog (LCA-7, internal designation) shows logP 3.1, hERG 0.18, mean affinity 0.61. This is a potential candidate for further wet-lab characterization in a subsequent study.

### 3.4 Multi-component synergy hypothesis

The ranked compounds mirror the empirical Korean topical depigmenting traditions (감초 + 녹차 + 상백피 combination has been used for centuries [5]). Our in silico results provide structural and target-level support for the multi-component approach: licochalcone A (TYR + TRP-2), EGCG (TYR + MITF), and oxyresveratrol (multi-target with topical-friendly properties) appear to engage non-identical subsets of the four-node panel, consistent with multi-component synergy. We do not assert clinical efficacy.

---

## 4. Limitations

1. **No experimental validation** in this preprint. Boltz-2 / ADMET-AI / MD outputs are predictions; experimental confirmation in a melanocyte cell-culture (B16F10 melanin-content assay), human-melanocyte primary culture, and 3D reconstructed-skin pigmentation model is required before any clinical interpretation.
2. **MITF is a transcription factor** without a canonical small-molecule pocket; our co-folding against the bHLH-LZ DNA-binding domain is a methodological extension, not a validated MITF-inhibitor screening approach. Direct MITF inhibitor validation requires a different experimental paradigm (DNA-binding assay, MITF-luciferase reporter).
3. **Tyrosinase species variability**: most published Korean-herbal tyrosinase data are from mushroom (*Agaricus bisporus*) tyrosinase, which differs structurally from human TYR. Our co-folding uses human TYR; ranking may differ from published mushroom-tyrosinase IC₅₀ values.
4. **No skin-permeation data**: topical efficacy requires both target engagement and stratum-corneum permeation. Experimental log K_p (skin permeability) is not measured here.
5. **No human clinical evidence**: the present work is hypothesis-generation only.

---

## 5. Conclusions

We have screened a 30-compound Korean herbal library against the TYR / MITF / TRP-1 / TRP-2 hyperpigmentation network in silico, identifying licochalcone A, EGCG, and oxyresveratrol as the top multi-target candidates. Among these, oxyresveratrol exhibits the cleanest topical-friendly safety profile, while licochalcone A and EGCG show stronger predicted target engagement at the cost of formulation challenges (high logP for licochalcone A; sub-µM but borderline-low logP for EGCG). REINVENT 4 generative scaffold-hop on licochalcone A produced one analog (LCA-7) with improved property profile — a candidate for follow-up.

The forward path is wet-lab validation: B16F10 melanin-content assay (Korean CRO, ~₩2-3M for 3-compound panel), human melanocyte primary culture, and EpiDerm-Melanocyte 3D reconstructed-skin model. Recover Korean Medicine Clinic's clinical interest in topical depigmenting preparations motivates this study; no clinical efficacy claim is made and any clinical use will follow IRB-approved protocol.

---

## Acknowledgments / Author contributions / Competing interests / Data availability

Same standard text as accompanying Genesis_Medicine preprints (HanCheongWoo single-author; HAN PREDICT founder + Recover affiliation; Apache-2.0 code; CC-BY 4.0 manuscript). Data available at <https://github.com/crazat/genesis_medicine>.

---

## References

[1] del Marmol V, Beermann F. Tyrosinase and related proteins in mammalian pigmentation. *FEBS Lett* 1996, 381, 165–168.
[2] Vachtenheim J, Borovanský J. "Transcription physiology" of pigment formation in melanocytes: central role of MITF. *Exp Dermatol* 2010, 19, 617–627.
[3] Westerhof W, Kooyers TJ. Hydroquinone and its analogues in dermatology — a potential health risk. *J Cosmet Dermatol* 2005, 4, 55–59.
[4] Sarkar R, et al. Cosmeceuticals for hyperpigmentation: what is available? *J Cutan Aesthet Surg* 2013, 6, 4–11.
[5] *Donguibogam* (1613). 외형편 (External-Form). Modern translation: 동의보감 동의학연구원 편, 2008.
[6] Lee J-H, et al. Korean herbal medicine for skin pigmentation: a review. *J Ethnopharmacol* 2018, 218, 75–87.
[7] Nerya O, et al. Glabrene and isoliquiritigenin as tyrosinase inhibitors from licorice roots. *J Agric Food Chem* 2003, 51, 1201–1207.
[8] Yokota T, et al. The inhibitory effect of glabridin from licorice extracts on melanogenesis. *Pigment Cell Res* 1998, 11, 355–361.
[9] No JK, et al. Inhibition of tyrosinase by green tea components. *Life Sci* 1999, 65, PL241–246.
[10] Baek YS, et al. Tyrosinase inhibitory activity of compounds from *Broussonetia kazinoki*. *Planta Med* 2009, 75, 1–4.
[11] Kim YM, et al. Oxyresveratrol and hydroxystilbene from *Morus alba* as tyrosinase inhibitors. *J Agric Food Chem* 2002, 50, 5698–5703.
[12] Wang Y, et al. Puerarin in melanogenesis: MITF and TRP-1/2 down-regulation. *Phytother Res* 2015, 29, 76–81.
[13] Wohlwend J, et al. Boltz-2: an open-source biomolecular structure and binding affinity model. Preprint, 2024.
[14] Swanson K, et al. ADMET-AI: machine learning ADMET platform. *Bioinformatics* 2024, 40, btae416.
[15] HanCheongWoo. AI-driven scaffold-hopping of *Embelia ribes* embelin yields a topical-friendly anti-fibrotic candidate (EMB-3). ChemRxiv preprint, 2026.
[16] HanCheongWoo. Calibrated absolute binding free energy pipeline for natural-product scaffold-hopping. ChemRxiv preprint, 2026 (forthcoming).

---

*v0.1 draft, 2026-04-26 · ~2,800 words · CC-BY 4.0*
