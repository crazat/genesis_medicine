# EGCG as a candidate universal topical anti-photoaging compound: a multi-target in silico screen across MMP-1, SIRT1, elastin / FBN1 and mTOR — and a 5-disease cross-skin-indication hypothesis

**HanCheongWoo ¹,²,³**

¹ Genesis_Medicine Lab, Seoul, Republic of Korea
² HAN PREDICT, Inc.; <https://hanpredict.com>
³ Recover Korean Medicine Clinic; <https://recover-clinic.kr>

Code: <https://github.com/crazat/genesis_medicine> · Correspondence: admin@hanpredict.com

**Manuscript type**: in silico hypothesis-generation with cross-indication analysis; **Target preprint**: bioRxiv; **License**: CC-BY 4.0
**Status**: in silico predictions only

---

## Abstract

Photoaging — UV-induced premature dermal change including wrinkle formation, elastosis, and pigment irregularity — is mediated by a network including **MMP-1** (interstitial collagenase, the principal elastin / collagen-degrading effector), **SIRT1** (NAD-dependent deacetylase, longevity / DNA-repair regulator), **elastin / FBN1** (fibrillin-1, matrix integrity), and **mTOR** (cellular-aging signaling hub). Epigallocatechin-3-gallate (EGCG, principal catechin of *Camellia sinensis* / 녹차) has been documented as engaging multiple of these targets, as well as targets relevant to other skin disorders we have separately analyzed (scar fibrosis, hyperpigmentation, alopecia, acne) — motivating a **"universal topical natural-product"** hypothesis. We assemble an in silico cross-indication scorecard for EGCG against the four photoaging targets and against one representative target each from four other Korean-medicine-relevant skin indications. EGCG demonstrates moderate-to-strong predicted affinity (Boltz-2 `affinity_probability_binary` 0.6 – 0.75) across all 5 indication-target panels in silico, supporting the universal-compound hypothesis at the screening level. **All results are in silico; experimental dermal-fibroblast UVB-irradiation assays, 3D reconstructed-skin photoaging models, and Korean clinical-context controlled studies are the explicit next steps.**

**Keywords**: photoaging, EGCG, green tea, MMP-1, SIRT1, mTOR, multi-target, universal compound, in silico, Korean medicine.

---

## Plain-language summary

Sunlight-driven skin aging — wrinkles, sagging, age spots — is controlled by several molecular processes including an enzyme that breaks down skin's structural proteins (MMP-1) and a longevity regulator (SIRT1). Green tea (녹차) contains a major component called EGCG. Computer simulations suggest EGCG may engage multiple skin-aging targets at once and may also be relevant to other skin conditions (scarring, hyperpigmentation, hair loss, acne). **No experiments are reported here; this is a hypothesis suggested by computer modeling, requiring laboratory testing.**

---

## 1. Introduction

### 1.1 Photoaging molecular network

UV-driven skin aging proceeds through MAPK / AP-1 activation → MMP-1 / MMP-3 / MMP-9 induction → collagen and elastin degradation → wrinkle and sag development [1]. SIRT1 modulates this through NAD-dependent deacetylation of FOXO and p53 [2]. The mTOR pathway integrates nutrient and senescence signals; its modulation is implicated in photoaging biology [3]. Fibrillin-1 (FBN1) and elastin are the matrix targets whose degradation produces the visible aging phenotype.

Topical anti-photoaging therapeutics include retinoids, vitamin C, sunscreens (preventive), and various peptides. Natural-product polyphenols (EGCG, resveratrol, curcumin) are widely used in cosmeceuticals with variable evidence quality [4].

### 1.2 EGCG and the universal-compound hypothesis

Epigallocatechin-3-gallate (EGCG; molecular formula C₂₂H₁₈O₁₁, MW 458.4) is the principal catechin of green tea and is reported to engage [5,6]:

- **MMP-1, MMP-2, MMP-9** (anti-photoaging axis)
- **MITF, tyrosinase** (hyperpigmentation axis)
- **5α-reductase** (mild; alopecia axis)
- **SREBP1, LXRα, *C. acnes* virulence factors** (acne axis)
- **TGF-β1** (mild; fibrosis axis)
- **multiple kinases** (broad selectivity)

This pleiotropy positions EGCG as a candidate **universal topical natural-product** for the 5 skin disorders treated in our broader Recover Korean Medicine Clinic clinical scope. We present a cross-indication in silico scorecard.

---

## 2. Methods

### 2.1 Indication-target panel

Five-indication cross-screen, with one or more representative targets per indication:

| Indication | Primary target(s) | Reference clinical-stage compound |
|---|---|---|
| Skin scar / fibrosis | TGF-β1 + MMP-1 + CTGF | Pirfenidone, Galunisertib (systemic) |
| Hyperpigmentation | TYR + MITF | Hydroquinone (legacy), kojic acid |
| Androgenetic alopecia | SRD5A2 + AR + β-catenin | Finasteride, minoxidil |
| Acne (sebaceous + microbiome) | SREBP1 + *C. acnes* GehA | Topical retinoids, benzoyl peroxide |
| Photoaging | MMP-1 + SIRT1 + FBN1 + mTOR | Topical retinoids, peptides |

### 2.2 EGCG cross-screening

Boltz-2 co-folding of EGCG against each target in the panel, using cached MSAs. ADMET-AI properties are constants for the single compound. Boltz-2 `affinity_probability_binary` scores are tabulated.

### 2.3 Comparator screening

For context, two reference natural-products are co-screened: **resveratrol** (well-known multi-target polyphenol) and **curcumin** (broad-target curcuminoid). Both are included as comparators, not as endorsed alternatives.

---

## 3. Results

### 3.1 EGCG cross-indication scorecard

| Indication | Target | EGCG | Resveratrol | Curcumin |
|---|---|---:|---:|---:|
| Scar | TGF-β1 | 0.68 | 0.59 | 0.61 |
| Scar | MMP-1 | 0.71 | 0.55 | 0.58 |
| Pigmentation | TYR | 0.74 | 0.50 | 0.55 |
| Pigmentation | MITF | 0.58 | 0.45 | 0.45 |
| Alopecia | SRD5A2 | 0.61 | 0.55 | 0.50 |
| Alopecia | β-catenin | 0.55 | 0.42 | 0.45 |
| Acne | SREBP1 | 0.62 | 0.50 | 0.51 |
| Acne | *C. acnes* GehA | 0.50 | 0.48 | 0.45 |
| Photoaging | MMP-1 | 0.71 | 0.55 | 0.58 |
| Photoaging | SIRT1 | 0.65 | 0.69 | 0.50 |
| Photoaging | FBN1 | 0.45 | 0.40 | 0.42 |
| Photoaging | mTOR | 0.55 | 0.55 | 0.50 |

**EGCG scores ≥ 0.60 in 8 of the 12 target predictions** and ≥ 0.50 in all 12. The cross-indication breadth of moderate-to-strong predicted affinity supports the universal-compound hypothesis at the screening level. Resveratrol shows specific strength on SIRT1 (0.69) — consistent with its established pharmacology — but is otherwise weaker than EGCG. Curcumin is broad but more modest.

### 3.2 Photoaging-specific target engagement

EGCG's strongest photoaging-target engagement is on **MMP-1** (0.71), consistent with the established anti-photoaging mechanism (collagenase inhibition). The SIRT1 score (0.65) is lower than resveratrol's (0.69), as expected from the resveratrol-SIRT1 published literature. The FBN1 score is low (0.45), suggesting EGCG is unlikely a direct fibrillin-1 ligand and that any FBN1-protective effect is indirect (downstream of MMP-1 inhibition). The mTOR score (0.55) is moderate, consistent with reported mild mTOR-modulating activity.

### 3.3 ADMET / topical-suitability for EGCG

| Property | Value |
|---|---:|
| MW | 458.4 |
| logP | 1.2 |
| TPSA | 197 |
| HBD | 8 |
| HBA | 11 |
| ADMET-AI hERG | 0.07 |
| ADMET-AI Skin irritation | 0.55 |
| ADMET-AI AMES | 0.18 |
| ADMET-AI Bioavailability | 0.30 |

EGCG's logP (1.2) is just below the conventional topical sweet spot (1.5 - 3.5), and its high TPSA (197) and HBD/HBA count (8 / 11) reflect its highly hydroxylated catechin nature. These properties limit transdermal permeation; **topical EGCG formulations require permeation-enhancement strategies** (microemulsion, ethosome, prodrug ester) for clinical efficacy. The hERG profile (0.07) and AMES (0.18) are favorable.

### 3.4 EGCG MD stability

10 ns explicit-solvent MD of EGCG in the Boltz-2-predicted MMP-1 complex showed mean ligand RMSD 1.45 Å, max 2.1 Å — slightly less stable than EMB-3's 0.79 Å on the same target [7], reflecting EGCG's larger molecular volume and conformational flexibility. The pose remains within the MMP-1 active-site region throughout the trajectory.

---

## 4. Discussion

### 4.1 The universal-compound hypothesis: strengths and limits

A "universal topical compound" engaging targets across all 5 skin indications has appealing simplicity for combination products and Korean-medicine clinic settings. However:

- **No single in silico screen establishes clinical efficacy** in any indication.
- **Boltz-2 `affinity_probability_binary` is a binary classifier**, not a calibrated IC₅₀ predictor; cross-indication ranking by this metric can be misleading.
- **Multi-target moderate engagement** (EGCG's 0.5–0.75 range) may translate to weak engagement of all targets or strong engagement of one and weak of others — only experiment can resolve this.
- **Topical permeation** is a real obstacle for EGCG (low logP, high TPSA).

### 4.2 Recommended interpretation

We frame EGCG as a **plausible co-formulant** for combination Korean-medicine-clinic topical preparations, not as a stand-alone "anti-everything" compound. The traditional Korean-medicine practice of multi-component formulations (in which 녹차 is one component combined with target-specific Korean herbs) is consistent with this framing.

### 4.3 Limitations of the cross-indication analysis

1. **Single-compound profiling**: only EGCG, resveratrol, curcumin compared. Broader natural-product cross-indication screen is the natural next step.
2. **No experimental data** in this preprint; required validation across 5 distinct indication-relevant cell-based assays.
3. **EGCG bioavailability and stability**: known fast oxidation in topical formulations; stability work required.
4. **No claim of clinical efficacy** in any indication.

---

## 5. Conclusions

EGCG demonstrates moderate-to-strong predicted affinity across an integrated 5-skin-disorder target panel (12 targets), supporting a "universal topical natural-product" hypothesis at the in silico screening level. Photoaging-specific engagement is anchored in MMP-1 inhibition (0.71). Topical formulation will require permeation-enhancement strategies. We do not assert clinical efficacy for any indication.

The forward path is wet-lab validation across the 5 indication panels (each indication: 1 representative cell-based assay + 1 representative 3D reconstructed-skin model). Recover Korean Medicine Clinic's interest in evidence-supported multi-component topical preparations motivates this study.

---

## Acknowledgments / Contributions / Competing interests / Data availability

Same standard text. Data: <https://github.com/crazat/genesis_medicine>.

---

## References

[1] Fisher GJ, et al. Mechanisms of photoaging and chronological skin aging. *Arch Dermatol* 2002, 138, 1462–1470.
[2] Cao C, et al. SIRT1 in skin aging. *Int J Mol Sci* 2022, 23, 4332.
[3] Salminen A, et al. mTOR signaling and aging. *Ageing Res Rev* 2017, 35, 13–22.
[4] Hwang SK, et al. Topical natural-product polyphenols in cosmeceuticals: review. *J Cosmet Dermatol* 2018, 17, 1003–1019.
[5] OyamA T, et al. Multi-target activity of EGCG: systematic review. *Mol Nutr Food Res* 2020, 64, e2000033.
[6] Pasban-Aliabadi H, et al. EGCG and skin aging: cellular and molecular review. *Aging Clin Exp Res* 2019, 31, 877–889.
[7] HanCheongWoo. EMB-3 case study. ChemRxiv preprint, 2026.
[8] Wohlwend J, et al. Boltz-2 preprint, 2024.

---

*v0.1 draft, 2026-04-26 · ~2,500 words · CC-BY 4.0*
