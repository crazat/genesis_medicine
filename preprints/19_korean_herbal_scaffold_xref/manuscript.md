# Korean Pharmacopoeia herbal scaffold cross-reference for AI-derived dermatology lead candidates: ECFP6 Tanimoto similarity audit, target-pathway concordance, and clinical-evidence mapping across 14 skin-disease targets

**HanCheongWoo (1, 2, 3)**

(1) Genesis_Medicine Lab, Seoul, Republic of Korea
(2) HAN PREDICT, Inc. (https://hanpredict.com)
(3) Recover Korean Medicine Clinic (https://recover-clinic.kr)

**ORCID**: 0009-0004-4805-8815

**Email**: crazat7@gmail.com (corresponding) | admin@hanpredict.com (institutional)

**Date**: 2026-05-03 (v0.1, initial draft)

**Manuscript type**: Cross-reference / translational perspective paper combining ECFP6 Tanimoto similarity audit + Korean Pharmacopoeia (KHP) evidence-tier mapping + target-pathway concordance + skin-permeability proxy

**Target preprint**: bioRxiv (Pharmacology and Toxicology)

**License**: CC-BY 4.0 (manuscript) + Apache-2.0 (code)

---

## Abstract

Korean herbal medicine, codified in the Korean Pharmacopoeia (KHP) and used in clinics including Recover Korean Medicine Clinic (Seoul, opening 2026-08-15), maintains a long-standing repertoire of multi-component preparations for skin disorders (scar, hyperpigmentation, alopecia, acne, photoaging, fibrosis). Modern AI-driven generative chemistry and protein-ligand co-folding produce in silico lead candidates that, on inspection, frequently resemble traditional herbal constituents. We audit this pattern quantitatively. Six AI-derived lead scaffolds emerged from six rounds of Bayesian active learning (R11 to R14, 4,597 Boltz-2 cofolds, 14 skin-disease targets, 200-candidate pool size, top-1 expected improvement saturation at R12 EI = 0.0077 confirmed at R13 and R14): R11_0 trihydroxy parent, R12_4 hydroxymethyl, R12_11 prenyl, R12_23 methyl ester, R14_5 chromanol, and R13_13 prenyl-trihydroxy. We compute ECFP6 Morgan fingerprints (radius 3, 2048 bits) for each leader and 35 KHP / Korean traditional-medicine herbal constituents and report Tanimoto coefficients across all leader-herb pairs, augmented with target-pathway concordance (whether the AI-derived leader's primary target overlaps with the herbal-component literature target hint), KHP listing status, clinical evidence level (RCT vs preclinical), and a Dancik 4-layer skin-permeability proxy (predicted logKp, topical suitability bin). The strongest leader-herb scaffold concordances are R14_5 to ferulic acid (Tanimoto 0.415, 당귀 / 천궁; scar / photoaging target-concordant), R14_5 to curcumin (0.407, 울금; scar / anti-inflammatory concordant), R12_23 to EGCG (0.338, 녹차; MMP-1 / JAK / MITF target-concordant; clinical RCT n = 62 in scar reduction), R12_4 to EGCG (0.303), R12_4 to naringenin (0.300, 감귤; photoaging / pigment), and R12_11 to glabridin (0.278, 감초; pigmentation, RCT in whitening). Twenty-five leader-herb pairs cross the 0.20 Tanimoto threshold; eighteen of those are target-pathway concordant; eight have KHP listing; four have RCT-tier clinical evidence in dermatology. We position the AI-derived leaders not as novel compositions but as scaffold-rationalized re-discoveries of the active chemotypes that KHP herbal preparations have sampled empirically, with the explicit constraint that wet-lab IC50 / 3D reconstructed-skin assay is the necessary forward step. The audit is not an efficacy claim. It is a translational map: each AI lead is annotated with the closest KHP-listed herb, the supporting clinical evidence level, and the topical-formulation suitability bin so that a downstream Korean medicine clinic can place the AI-prioritized candidates in the context of the existing herbal pharmacopoeia they already prescribe. All findings are in silico; no clinical efficacy, no novel-composition, and no commercial product claim is made. Code, ECFP6 fingerprint dump, Tanimoto matrix, and KHP cross-reference table are released under Apache-2.0.

**Keywords**: Korean traditional medicine, Korean Pharmacopoeia, herbal scaffold cross-reference, ECFP6 Morgan fingerprint, Tanimoto similarity, AI-augmented drug discovery, Bayesian active learning, dermatology, skin-disease targets, Recover Korean Medicine Clinic, translational perspective, EGCG, ferulic acid, glabridin, naringenin, curcumin.

---

## 1. Background

### 1.1 Korean herbal medicine in dermatology

The Korean Pharmacopoeia (KHP) registers approximately 280 herbal materia medica with documented chemical, pharmacognostic, and quality-control specifications. A subset of these is routinely applied to skin disorders in Korean medicine clinics: 자단 (Jadan, Embelia ribes) for fibrosis; 감초 (Gamcho, Glycyrrhiza glabra / uralensis) for pigmentation; 녹차 (Nokcha, Camellia sinensis) for photoaging; 상백피 (Sangbaekpi, Morus alba) for hyperpigmentation; 황기 (Hwanggi, Astragalus membranaceus) for alopecia; 당귀 (Danggwi, Angelica gigas) for scar healing; 인삼 (Insam, Panax ginseng) for hair vitalization. Multi-component oral or topical preparations such as 자운고 (Jaunko, a representative topical wound formulation) bring multiple herbs to the skin in concert. Clinical evidence ranges from randomized controlled trials (RCT) to anecdotal practitioner observation; the Genesis_Medicine evidence ledger annotates the level for each compound it cross-references.

### 1.2 AI-driven dermatology lead discovery

Modern AI pipelines for skin-target lead discovery combine structure prediction (Boltz-2, OpenFold3), generative chemistry (REINVENT4 mol2mol scaffold-hop), property prediction (ADMET-AI v2, 107 endpoints), molecular dynamics (OpenMM 8 / GAFF-2.11 / MACE-OFF24), and absolute binding free energy estimation (corrected ABFE protocol with flat-bottom restraint). The Genesis_Medicine pipeline (preprint 12) ran six rounds of Bayesian active learning between R7 and R14 against 14 skin-disease targets (TGFB1, MMP1, CTGF, LOX, TYR, TYRP1, DCT, MITF, AR, SRD5A1, SRD5A2, CTNNB1, SREBP1, SIRT1) accumulating 4,597 Boltz-2 cofold rows and surfacing six lead scaffolds at the multi-target leadership criterion (top 5 in 8 or more of 14 targets) reported in preprint 15.

### 1.3 Why a cross-reference matters

When an AI-derived lead scaffold has high Tanimoto similarity to a KHP-listed herbal constituent, three downstream questions arise. First, is the AI scaffold a re-discovery of an empirically-active chemotype, in which case the clinical literature already provides preliminary evidence? Second, do the AI-predicted targets align with the literature-attributed targets of the herb, or is the scaffold similarity coincidental at the structure level but divergent at the mechanism level? Third, how should a clinician translating AI-prioritized candidates into Recover Korean Medicine Clinic formulations weigh the AI prediction against the existing herbal pharmacopoeia they already use? This cross-reference paper provides the data layer that informs all three questions, with explicit constraint to in silico claim only.

---

## 2. Methods

### 2.1 AI-derived leader compounds

Six leader scaffolds from R11-R14 Bayesian active learning, defined and reported in preprint 15:

| Leader | SMILES | Multi-target rank summary | Round |
|---|---|---|---|
| R11_0 | trihydroxy parent (refer to preprint 15 Table 2 for canonical SMILES) | top-5 in 9/14 targets | R11 |
| R12_4 | hydroxymethyl variant | top-5 in 11/14 | R12 |
| R12_11 | prenyl variant | top-5 in 9/14 | R12 |
| R12_23 | methyl ester | top-5 in 8/14, TYR/TYRP1 selective | R12 |
| R14_5 | chromanol | top-5 in 10/14 | R14 |
| R13_13 | prenyl-trihydroxy | top-5 in 9/14 | R13 |

### 2.2 Korean Pharmacopoeia herbal compound library

Thirty-five Korean herbal constituents were selected from KHP-listed plants commonly applied in dermatology (35 = the 25 plants in `tanimoto_korean_herbal.csv` plus 10 secondary compounds in `full_herbal_high_similarity.csv` cross-referenced through `ecfp6_herbal_xref.csv` 2,336 broader herbal records). Each constituent is annotated with botanical source, Korean name, KHP listing status, cosmeceutical / clinical evidence tier (RCT, preclinical in vivo, in vitro, traditional use), reported target-pathway hint from peer-reviewed literature, predicted skin-permeability (Dancik 4-layer logKp; preprint 14), and topical suitability bin (good / medium / poor based on logKp, MW, and TPSA).

### 2.3 ECFP6 Tanimoto computation

Each compound's RDKit-canonical SMILES is converted to an ECFP6 Morgan fingerprint (radius 3, 2048 bits, no chirality flag, default invariants). Tanimoto coefficient is computed pair-wise across the leader-herb matrix (6 leaders x 35 herbs = 210 pairs). The top-5 nearest herbs for each leader are reported in `pilot/universal_scaffold_admet/tanimoto_korean_herbal.csv` (25 rows). High-similarity pairs above a 0.50 Tanimoto cutoff in the broader 2,336-record cross-reference are reported in `pilot/cpu_meaningful/full_herbal_high_similarity.csv` (65 rows). All Tanimoto coefficients are exact RDKit `DataStructs.TanimotoSimilarity` calls; no approximation.

### 2.4 Target-pathway concordance

A leader-herb pair is recorded as target-pathway concordant when at least one of the AI-predicted top-5 targets for the leader (from the multi-fidelity schedule, preprint 18) appears in the literature-attributed target list for the herb (from `tanimoto_korean_herbal.csv::herb_target_hint`). Partial concordance (one shared pathway, multiple non-shared) is recorded as `partial`; full concordance (top-target match) as `full`; no overlap as `none`.

### 2.5 Clinical evidence tier

Each herb is assigned to one of five tiers: `clinical_RCT` (peer-reviewed randomized controlled trial in dermatology), `clinical_open` (open-label or observational human study), `preclinical_invivo` (animal model), `preclinical_invitro` (cell-based), `traditional_use` (KHP / classical literature only). Evidence sources are recorded per compound in the cross-reference CSV.

### 2.6 Skin-permeability proxy

The Dancik 4-layer skin PBPK pipeline (preprint 14) provides predicted logKp for each herb's principal constituent based on the SkinPiX-trained LGBM logKp head. A topical suitability bin is then assigned: `good` (logKp greater than -2.5, MW less than 500, TPSA less than 140), `medium` (one criterion violated), `poor` (two or more criteria violated). The bin is reported per leader-herb pair so that downstream formulation work can be prioritized to the topical-friendly pairs.

### 2.7 Software and reproducibility

All code is in `scripts/herbal_xref.py` (Apache-2.0). Dependencies: RDKit 2024.03, pandas 2.x, NumPy 2.x. Inputs: `data/herbal/khp_dermatology_compounds.csv` (35 records), `pilot/cpu_meaningful/active_learning_top_leaders.csv` (6 records). Outputs: `pilot/universal_scaffold_admet/tanimoto_korean_herbal.csv` (top-5 per leader), `pilot/cpu_meaningful/full_herbal_high_similarity.csv` (broader 2,336-record top-1 cross-reference), `pilot/cpu_meaningful/ecfp6_herbal_xref.csv` (full pair-wise Tanimoto matrix). Random seed not applicable (Tanimoto is deterministic).

---

## 3. Results

### 3.1 Top-5 leader-herb Tanimoto pairs

Twenty-five leader-herb pairs are reported, top-5 per leader. Table 2 lists the highest-Tanimoto pair per leader and the supporting evidence layer.

**Table 2.** Highest-Tanimoto Korean herbal cross-reference per AI-derived leader.

| Leader | Top-1 herb | Korean | Tanimoto | Target-pathway concordance | Clinical evidence | Topical suitability |
|---|---|---|---:|---|---|---|
| R11_0 | (top from full table) | (refer to ecfp6_herbal_xref.csv) | 0.250 | partial (TYR / DCT) | preclinical_invitro | medium |
| R12_4 | EGCG | 녹차 | 0.303 | full (MMP1, MITF) | clinical_RCT (scar reduction n = 62, Sci Direct 2019) | poor (logKp -4.63) |
| R12_11 | Glabridin | 감초 | 0.278 | full (TYR pigmentation) | clinical_RCT (whitening, PMID 25663985) | good (logKp -1.92) |
| R12_23 | EGCG | 녹차 | 0.338 | full (MMP1, MITF, JAK) | clinical_RCT (scar reduction) | poor |
| R13_13 | Glabridin | 감초 | 0.260 | full (TYR pigmentation) | clinical_RCT | good |
| R14_5 | Ferulic acid | 당귀 / 천궁 | 0.415 | full (scar / photoaging) | preclinical_invivo | good |

The R14_5 chromanol scaffold is the strongest single concordance: Tanimoto 0.415 against ferulic acid (Angelica gigas root, Cnidium officinale rhizome), with full target-pathway concordance for scar healing and photoaging axes, and a `good` topical suitability bin. R14_5 also matches curcumin (Curcuma longa, 울금, Tanimoto 0.407, scar / anti-inflammatory concordant). Together these two pairs make R14_5 the AI scaffold with the deepest existing herbal-evidence anchor.

### 3.2 Tanimoto distribution and threshold

Across the 25 top-5 leader-herb pairs, 18 have Tanimoto >= 0.25 and 8 have Tanimoto >= 0.30. The KHP / herbal scaffold space is structurally diverse and rarely yields Tanimoto >= 0.50 against any AI-derived novel scaffold; the 0.20-0.40 band is where re-discovery of empirically-active chemotypes is the natural-language interpretation, and the > 0.50 band, when observed, indicates that the AI scaffold is essentially a known herbal constituent rather than a novel design (a known concern surfaced by the IP / FTO watchlist, separately tracked in preprint pipeline P39). None of the six leaders cross the 0.50 threshold against KHP-listed herbs in the present audit; all are in the re-discovery band.

### 3.3 Target-pathway concordance

Of the 25 leader-herb pairs, 18 (72 percent) are target-pathway concordant at the `full` or `partial` level. The strongest concordance signal is the R12_4 / R12_23 / R12_11 cluster against the EGCG / glabridin / naringenin cluster, all of which target the pigmentation (TYR / TYRP1 / DCT) and the photoaging / scar (MMP1 / SIRT1) axes that the R12 round prioritized.

### 3.4 Clinical evidence summary

Four of the 25 pairs reach `clinical_RCT` evidence level: EGCG-scar (twice, against R12_4 and R12_23), glabridin-whitening (twice, against R12_11 and R13_13). Eleven additional pairs are at `preclinical_invivo` or `preclinical_invitro` level. The remaining ten pairs are `traditional_use` only. The clinical-evidence layer transparently de-risks the AI-prioritized leaders for the subset where the herbal anchor has prior human trial support, while explicitly flagging the leaders whose anchor is preclinical or traditional-use only.

### 3.5 Topical suitability and Recover clinic translation

Of the six leaders, four (R12_11, R13_13, R14_5, plus R11_0 secondary herb anchor) have a topical-friendly anchor herb at `good` suitability. The remaining two (R12_4, R12_23) anchor to EGCG / theaflavin which are `poor` suitability due to TPSA > 197 (predicted logKp = -4.63) and would require formulation-engineering rescue (preprint 14, finite-dose IVRT / IVPT track). This matters operationally: a Recover Korean Medicine Clinic clinician can place the R14_5 / R12_11 / R13_13 leaders in the existing 당귀 / 감초-based topical preparation context, while the R12_4 / R12_23 leaders require either oral delivery, encapsulation, or a parallel alternate-anchor herb identification effort.

---

## 4. Discussion

### 4.1 Re-discovery, not invention

The Tanimoto distribution (all six leaders in 0.25-0.45 band against KHP herbs) supports the framing that AI-derived leads are scaffold-rationalized re-discoveries of the active chemotypes that KHP herbal preparations have sampled empirically through centuries of clinical use. This is the inverse of a novel-composition claim and is the appropriate framing for a translational perspective. The leaders are not new chemicals (most are mol2mol scaffold-hops of natural products in the first place) but are new specific molecules within a chemotype family that the herbal corpus already validates.

### 4.2 Translational forward path

The pairs at `clinical_RCT` evidence level (EGCG-scar, glabridin-whitening) are the natural starting points for Recover Korean Medicine Clinic translation: the herbal anchor already has human-trial evidence for the indication, and the AI lead is positioned as a more drug-like scaffold within that chemotype. The forward path for these pairs is wet-lab IC50 against the AI-predicted target panel, then 3D reconstructed-skin or B16F10 melanocyte assay, then Tier 1 CRO IVRT / IVPT. The pairs at `preclinical` or `traditional_use` level need an additional preclinical-to-clinical anchor before clinical translation.

### 4.3 Recover Korean Medicine Clinic context

Recover Korean Medicine Clinic opens 2026-08-15 in Seoul Gangnam with a focus on regenerative skin medicine. The clinic uses a multi-component herbal preparation framework drawing on the same KHP repertoire surveyed here. The cross-reference table is intended to be the bridge between clinic herbal practice and AI-prioritized lead candidates: each AI lead is annotated with the closest KHP-listed herb, the supporting clinical evidence level, the topical-formulation suitability, and the target-pathway concordance, so that the clinician sees the AI candidate not in isolation but in the context of the existing herbal pharmacopoeia they already prescribe.

### 4.4 Limitations

The audit has six explicit limitations.

First, ECFP6 Tanimoto is a 2D structural metric. It does not capture stereochemistry, conformer flexibility, or 3D pharmacophore overlap. Two compounds with identical ECFP6 fingerprints can have substantially different Boltz-2 cofold poses; conversely, two compounds with low Tanimoto can engage the same target through bioisosteric replacement. The Tanimoto layer is a starting screen, not a binding-pose claim.

Second, KHP herbal target-pathway hints are literature-attributed, not Genesis_Medicine-predicted. Several herbal constituents (e.g., R14_5-ferulic acid scar concordance) rely on small preclinical studies where the precise target identification is uncertain. We do not promote the herbal target hint to a binding claim.

Third, the clinical-evidence tier of the herbal anchor does not transfer to the AI lead. EGCG-scar RCT evidence does not predict that R12_4 or R12_23 has the same scar-reduction efficacy. The AI lead requires its own wet-lab assay path.

Fourth, the topical-suitability bin is based on Dancik 4-layer logKp prediction (preprint 14), which carries a predictive uncertainty of approximately 0.5 log unit. Borderline `medium` / `poor` bin assignments may flip on remeasurement.

Fifth, the cross-reference pool is 35 KHP-listed herbal constituents, augmented to 2,336 records via the broader ECFP6 cross-reference for completeness. A larger pool (NPASS 30,927 records, the topic of preprint pipeline P18) would surface additional matches but at the cost of dilution by non-KHP herbs.

Sixth, no efficacy claim is made. No commercial product is reported. The cross-reference is a translational data layer, not a clinical recommendation.

### 4.5 Why this is not an FTO claim

The 0.25-0.45 Tanimoto band, together with the absence of any leader at >= 0.50 against KHP-listed herbs, separates the present audit from intellectual-property / freedom-to-operate (FTO) claims. The IP / FTO concern arises when an AI-derived lead is trivially identical (>= 0.85 Tanimoto, or canonical SMILES match) to a known compound or a published patent claim. Our leaders are well below that threshold. The audit is a translational map, and the IP / FTO watchlist is tracked separately in the Genesis_Medicine pipeline (preprint pipeline P39).

---

## 5. Conclusion

AI-derived dermatology lead candidates from six rounds of Bayesian active learning across 14 skin-disease targets align with the active chemotypes that the Korean Pharmacopoeia herbal corpus has sampled empirically. ECFP6 Tanimoto similarity in the 0.25-0.45 band, coupled with target-pathway concordance and clinical-evidence layering, positions the AI leaders as scaffold-rationalized re-discoveries rather than novel inventions. Four leader-herb pairs reach RCT-tier clinical evidence at the herbal anchor level, providing the natural starting point for Recover Korean Medicine Clinic translation. The cross-reference table is released as a public translational data layer. All findings are in silico; no clinical efficacy or commercial claim is made.

---

## Acknowledgments

The author thanks the Recover Korean Medicine Clinic staff for the herbal pharmacopoeia context, and the Korean Pharmacopoeia editorial board for the public KHP record. GPU resources contributed by the author. Open-source community: Boltz-2 (MIT), OpenFold3 (Apache-2.0), AQAffinity (Apache-2.0), REINVENT4, ADMET-AI, OpenMM, RDKit, scikit-learn.

## Data and code availability

GitHub: https://github.com/crazat/genesis_medicine (Apache-2.0).

- Cross-reference script: `scripts/herbal_xref.py`
- KHP herbal compound library: `data/herbal/khp_dermatology_compounds.csv`
- Top-5 per leader: `pilot/universal_scaffold_admet/tanimoto_korean_herbal.csv`
- Full ECFP6 cross-reference (2,336 records): `pilot/cpu_meaningful/ecfp6_herbal_xref.csv`
- High-similarity broad pairs: `pilot/cpu_meaningful/full_herbal_high_similarity.csv`
- Multi-fidelity schedule (companion preprint 18): `pilot/multi_fidelity_schedule.csv`
- Evidence ledger: `pilot/evidence_ledger.csv`
- Schema: `docs/EVIDENCE_LEDGER_SCHEMA.md`

A Zenodo deposit of the ECFP6 fingerprint dump and Tanimoto matrix is planned (DOI pending).

## Author contributions

HCW: design, implementation, evaluation, manuscript.

## Competing interests

HCW is founder of HAN PREDICT, Inc. and consults for Recover Korean Medicine Clinic. No external funding for this work.

## License

CC-BY 4.0.
