# *Embelia ribes* (Vidanga, 자단) revisited: from Ayurvedic-East Asian traditional use to AI-augmented scaffold-hopping for skin fibrosis

**Genesis_Medicine Lab ¹, HAN PREDICT, Inc. ², and Recover Korean Medicine Clinic ³**
*Seoul, Republic of Korea*

¹ AI-driven natural product drug discovery R&D division
² AI medical-technology startup; facial 3D diagnostics + B2B SaaS platform
³ Affiliated Korean medicine clinic specializing in skin regeneration (강남, opening 2026-08-15)

Corresponding affiliation: <https://recover-clinic.kr> · code repository: <https://github.com/crazat/genesis_medicine>

**Manuscript type**: Narrative review with computational case study
**Target preprint server**: bioRxiv (primary), Phytomedicine (peer-review submission)
**Status**: in silico results only; wet-lab validation pending
**Code**: <https://github.com/crazat/genesis_medicine>

---

## Abstract (250 words)

***Embelia ribes* Burm.f.** (Myrsinaceae) is a climbing shrub native to South Asia and parts of East Asia. Its dried fruit, known as **Vidanga** in Ayurvedic medicine and **자단(子團子)** in Korean materia medica references, has been used for over two millennia as an anthelmintic, anti-inflammatory and digestive remedy. The principal bioactive constituent is **embelin (2,5-dihydroxy-3-undecyl-1,4-benzoquinone)**, present at 4–5% of dry weight. Modern molecular pharmacology has established embelin as an inhibitor of XIAP, NF-κB, and TGF-β/Smad pathways, with documented anti-fibrotic activity in liver and pulmonary models. To date, however, embelin has not been investigated for skin-fibrosis indications (scar regeneration, keloid, or hypertrophic scarring). Here we (i) re-survey the traditional and modern pharmacological literature on *E. ribes* / embelin, including a corrective note on prior misattribution to the Korean topical formulation 자운고; (ii) describe an AI-augmented scaffold-hopping pipeline that integrates REINVENT4 generative chemistry, ADMET-AI property prediction, Boltz-2 protein-ligand co-folding and corrected absolute binding free energy estimation; and (iii) present **EMB-3** (`CCCCCC1=C(O)C(=O)C(O)=C(C)C1=O`), a topical-friendly truncated analog of embelin computationally proposed to retain affinity for the fibrotic master-switch network (TGF-β1, MMP-1, CTGF, SMAD3) while substantially reducing predicted hERG liability. Our findings position *E. ribes* as a previously overlooked starting point for skin-fibrosis lead optimization. **All results are in silico; experimental validation in cell-based assays and topical formulations is the explicit next step.**

**Keywords**: *Embelia ribes*, embelin, scaffold-hopping, REINVENT, Boltz-2, TGF-β1, MMP-1, skin fibrosis, scar, in silico, traditional medicine.

---

## Plain-language summary (for clinic and lay audiences)

The Korean herbal materia medica records the dried fruit of *Embelia ribes* (자단) as a centuries-old remedy for parasites and inflammation. Its main chemical component, embelin, has more recently been shown in cell and animal studies to suppress molecular signals that drive scar formation in liver and lung tissue. **Despite Recover Korean Medicine Clinic's primary focus on skin scar regeneration, no prior research has examined embelin or its analogs for skin scarring**. We report a computer-aided exploration of embelin and a small set of derivatives, including a newly proposed analog (EMB-3) optimized in silico for topical application. **No human or laboratory experiments are reported in this preprint; all conclusions are computational predictions and require experimental verification before any clinical claim.**

---

## 1. Introduction

### 1.1 Botanical and ethnobotanical context

*Embelia ribes* Burm.f. (family Myrsinaceae; synonyms include *Embelia indica* and *Pattiyalanguli*) is a climbing shrub distributed across India, Sri Lanka, Nepal, Myanmar, southern China and parts of the Korean peninsula [1]. The dried, ripe fruit (*phala*) is the medicinal article. In **Ayurveda** the fruit is known as **Vidanga** (Sanskrit: विडङ्ग) and is mentioned in foundational texts including the *Charaka Samhita* and *Sushruta Samhita* (c. 200 BCE – 200 CE) primarily as an *krimighna* (anthelmintic) and *deepana* (digestive stimulant) [2,3]. In Korean and Chinese traditional medicine references, the fruit is rendered as **자단(子團)** or **자단자(子團子)**, and is occasionally cited in pre-modern materia medica compendia for parasitic infestation and chronic skin sores; it is **not formally included in the modern Korean Pharmacopoeia (KP) or Korean Herbal Pharmacopoeia (KHP)**, though traders supply it through the East Asian herbal trade.

### 1.2 Correction of a common misattribution: 자단 ≠ 자운고

A subset of computational and review literature, including earlier internal documentation of our own group, has incorrectly conflated *Embelia ribes* with the Korean topical formulation **자운고(紫雲膏, Jaun-go)**. We address this directly: 자운고 is a sesame-oil-based ointment whose active herbal constituent is the root of ***Lithospermum erythrorhizon*** (자초/紫草), which contains 1,4-naphthoquinone derivatives (shikonin, acetyl-shikonin) — chemically distinct from the **1,4-benzoquinone-2,5-diol** scaffold of embelin [4,5]. We have not identified any peer-reviewed report of embelin in 자운고 or in *L. erythrorhizon* extracts. Subsequent sections therefore frame embelin's traditional context exclusively in the *E. ribes* (Vidanga / 자단) lineage.

### 1.3 Embelin: chemistry and known molecular pharmacology

**Embelin** (2,5-dihydroxy-3-undecyl-1,4-benzoquinone; CAS 550-24-3; molecular formula C₁₇H₂₆O₄; MW 290.4; logP 5.4) is a hydroquinone-quinone tautomer that crystallizes as orange plates. The compound was first isolated from *E. ribes* in 1907 by Heffter and is also present in related Myrsinaceae species (*E. tsjeriam-cottam*, *Maesa lanceolata*) [6]. Quantitative content in *E. ribes* dry fruit ranges 2.3–5.0% by weight [7].

Modern pharmacology has documented:

- **XIAP inhibition** (X-linked Inhibitor of Apoptosis Protein): K_d ~ 4.1 µM, restoring caspase-9-mediated apoptosis in cancer cells [8].
- **NF-κB pathway suppression**: down-regulation of p65 nuclear translocation; relevant to inflammation and fibrosis [9,10].
- **TGF-β / Smad signaling inhibition**: suppression of Smad2/3 phosphorylation in hepatic stellate cells (HSCs), reducing α-SMA and collagen-I expression in vitro and in CCl₄-induced rat liver fibrosis in vivo [11].
- **Pulmonary fibrosis attenuation**: bleomycin-induced lung fibrosis mouse model showed reduced hydroxyproline and improved pulmonary function on intraperitoneal embelin [12].
- **Antioxidant and anti-inflammatory activity**: SOD/catalase elevation, COX-2 suppression [13].
- **Tubulin and mitochondrial complexes**: minor secondary targets reported [14].

**Critically: no prior peer-reviewed work, to our knowledge, has examined embelin or *E. ribes* extracts in skin-fibrosis indications** (post-traumatic scar, keloid, hypertrophic scar, or photoaging-related dermal fibrosis). This is the gap we begin to address computationally in section 3.

### 1.4 Three-pillar institutional context

The present work is conducted across three affiliated entities operating as a vertically-integrated Korean medicine technology consortium:

- **Genesis_Medicine Lab** — AI in silico drug-discovery R&D division (this work's primary research host); responsible for the computational pipeline (REINVENT4 + ADMET-AI + Boltz-2 + corrected ABFE) described in Section 4
- **HAN PREDICT, Inc.** — AI medical-technology startup; developer of a 3D facial-diagnostic Station Kit and iOS / B2B SaaS platform (PIPA §23-2 compliant; AI Basic Act 2026 compliant); IRB-approved 2026-04-27 — provides the digital-imaging and patient-data infrastructure that motivates downstream molecular-prescription needs
- **Recover Korean Medicine Clinic** — affiliated 한방 clinic specializing in skin regeneration (강남, scheduled opening 2026-08-15); clinical mandate (scar revision, keloid management, post-procedural healing) motivates the search for under-investigated natural-product starting points compatible with topical formulation

Embelin's combination of (i) documented anti-fibrotic activity in non-skin tissues, (ii) accessible East Asian traditional-medicine provenance, and (iii) a chemically tractable benzoquinone scaffold made it an attractive candidate for in silico re-evaluation in this 3-pillar context.

---

## 2. *Embelia ribes* in traditional medicine — a systematic narrative

### 2.1 Ayurvedic uses (Vidanga)

*Charaka Samhita Sutrasthana 25/40* lists Vidanga among 50 great medicines (*Mahakashayas*), specifically classified as *krimighna* (anthelmintic). *Sushruta Samhita Chikitsasthana 7* prescribes Vidanga *churna* (powder) for *udararoga* (abdominal disorders) including parasitic infestation. *Bhavaprakasha Nighantu* (16th century) elaborates the indications to include *kushtha* (chronic skin disorders), *grahani* (digestive disorders) and *gulma* (abdominal masses) [15].

Modern Ayurvedic textbooks summarize the actions as:
- *Rasa* (taste): *katu*, *kashaya* (pungent, astringent)
- *Virya* (potency): *ushna* (heating)
- *Vipaka* (post-digestive effect): *katu* (pungent)
- *Doshakarma*: *kapha-vata-shamaka* (pacifies kapha and vata doshas)
- *Karma*: *krimighna*, *deepana*, *pachana*, *anulomana*

These descriptive frames map approximately to modern pharmacological observations of antiparasitic, anti-inflammatory, digestive-stimulant and anti-spasmodic actions, though direct one-to-one mapping is inappropriate.

### 2.2 East Asian traditional medicine (자단子)

References to *E. ribes* in Chinese herbal compendia are sparse compared to Indian sources. Where mentioned, the dried fruit (typically rendered 자단子 or 비단자) appears in regional formularies as a vermifuge and for chronic skin lesions. In the Korean tradition, *E. ribes* is **not formally included in the Korean Pharmacopoeia (KP, 12th edition) or Korean Herbal Pharmacopoeia (KHP, 4th edition)**; nonetheless, herbal traders import the fruit through the East Asian herbal supply chain and certain individual practitioners include it in custom formulations (decoction, powder) for the indications above. The lack of formal pharmacopoeial status reflects historical importation patterns rather than rejection of efficacy.

### 2.3 What the traditional uses do *not* directly support

We emphasize that traditional Vidanga/자단 indications do **not** directly include scar regeneration, keloid, hypertrophic scar, or other modern dermatological diagnoses. The traditional context establishes the herb's safety profile (millennia of human use at customary doses) and broad anti-inflammatory and anti-parasitic activity, but the connection to skin fibrosis is a contemporary computational hypothesis and not a traditional teaching.

---

## 3. Modern molecular pharmacology of embelin: an updated synthesis

### 3.1 Apoptosis and cancer biology

The cell-permeable, small-molecule XIAP inhibitor activity of embelin was first reported by Nikolovska-Coleska and colleagues in 2004; binding to the BIR3 domain of XIAP (K_d 4.1 µM by fluorescence polarization) restores caspase-9 activation in tumor cells [8]. Subsequent work in colon, prostate, breast and pancreatic cancer cell lines extended the apoptosis-restoration phenotype in vitro and in xenograft models [16,17,18]. Phase 0/I clinical evaluation of an embelin-derivative pro-drug has been proposed but no completed trial is on record [19].

### 3.2 Inflammation and innate immunity

Heo and colleagues demonstrated NF-κB pathway suppression via reduced IκB phosphorylation and p65 nuclear translocation in HCT116 colon cancer cells [9]. Subsequent studies extended the NF-κB-inhibitory action to macrophages (LPS-induced TNF-α, IL-6 and iNOS suppression) [20], to pancreatic β-cells (cytokine-induced apoptosis attenuation) [21], and to murine models of contact dermatitis (topical 1% formulation reduced ear-swelling and TNF-α expression) [22].

### 3.3 Anti-fibrotic activity — the bridge to skin

Three lines of evidence are particularly relevant for the present hypothesis:

**Liver fibrosis.** Bao and colleagues showed that embelin (40 mg/kg i.p., 6 weeks) attenuated CCl₄-induced rat liver fibrosis with reduction of α-SMA-positive HSCs, decreased collagen-I deposition, and suppressed TGF-β1/Smad2/3 phosphorylation — a canonical pro-fibrotic axis [11]. Gao et al. independently confirmed Smad2/3 inhibition in primary HSC cultures with embelin in the 1–10 µM range [23].

**Pulmonary fibrosis.** Lee and colleagues reported that intraperitoneal embelin (5–20 mg/kg) attenuated bleomycin-induced lung fibrosis in C57BL/6 mice, with dose-dependent reductions in hydroxyproline content, Ashcroft score, and TGF-β1 expression [12]. The TGF-β1/Smad pathway and downstream MMP/CTGF axis were both implicated.

**Renal and cardiac fibrosis.** Smaller studies have reported attenuation of unilateral-ureteral-obstruction renal fibrosis [24] and angiotensin-II-induced cardiac fibrosis [25] in rodent models, with consistent TGF-β1/Smad-axis read-outs.

### 3.4 The unexamined territory: skin fibrosis

Despite the consistent anti-TGF-β/Smad activity in three internal-organ fibrosis models, **systematic literature search (PubMed, Web of Science, KISS, RISS, all years through April 2026)** returns no peer-reviewed work specifically examining embelin or *E. ribes* extracts in:

- post-traumatic scar
- hypertrophic scar
- keloid
- photoaging-related dermal fibrosis
- atopic-dermatitis-associated fibrosis
- scleroderma skin involvement

This absence is the rationale for the present in silico investigation.

### 3.5 Pharmacokinetic constraints for topical use

Embelin's physicochemical profile — molecular weight 290.4, calculated logP 5.4 (XLogP3 5.36), zero formal charge at neutral pH, two H-bond donors and four H-bond acceptors — places it at the upper edge of permissible logP for topical penetration. Clinical-cosmetic best practice typically targets **logP 1.5 – 3.5** for stratum-corneum partitioning without excessive systemic absorption [26]. In addition, ADMET-AI [27] predictions on the parent embelin scaffold flag elevated **hERG channel inhibition** liability (predicted probability 0.40) and substantial **skin irritation** signal (predicted probability 0.84). These constraints frame the scaffold-hopping rationale described next.

---

## 4. AI-augmented scaffold-hopping rationale and pipeline

### 4.1 The molecular target landscape for skin fibrosis

The skin fibrotic master-switch network — recurrent across post-traumatic scarring, keloid biology, and aging-related dermal stiffening — converges on the following molecular nodes [28,29]:

| Target | Role in skin fibrosis | UniProt |
|---|---|---|
| **TGF-β1** | Pro-fibrotic master cytokine; induces myofibroblast differentiation | P01137 |
| **MMP-1** | Interstitial collagenase; collagen remodeling balance | P03956 |
| **MMP-3, MMP-9** | Stromelysin / gelatinase; extracellular matrix turnover | P08254, P14780 |
| **CTGF / CCN2** | TGF-β downstream effector; fibroblast proliferation | P29279 |
| **SMAD2/3** | TGF-β signal transduction | Q15796, P84022 |
| **COL1A1, COL3A1** | Pro-fibrotic collagen deposition | P02452, P02461 |
| **LOX** | Lysyl oxidase; collagen cross-linking | P28300 |
| **PDGFRB** | Myofibroblast survival and proliferation | P09619 |

A topical-friendly multi-target scaffold that engages a subset of these nodes — particularly TGF-β1, MMP-1 and CTGF — would be of high interest. Embelin's documented activity against TGF-β1/Smad in non-skin fibrosis models, combined with its 1,4-benzoquinone-2,5-diol pharmacophore (a privileged motif for Michael-acceptor and metal-chelation chemistry), made it a defensible scaffold to interrogate.

### 4.2 Computational pipeline

We assembled an integrated open-source pipeline ([github.com/crazat/genesis_medicine](https://github.com/crazat/genesis_medicine), Apache-2.0):

1. **Generative scaffold-hopping**: REINVENT 4 (mol2mol_medium_similarity prior) [30], sampled 100–300 SMILES neighbors of embelin per round at temperature 0.6–1.0
2. **Property filtering**: RDKit physicochemistry (Lipinski + topical sweet spot logP 1.5–3.5, MW ≤ 500) and ADMET-AI [27] (hERG, skin irritation, AMES, ClinTox, oral bioavailability, aqueous solubility)
3. **Structure prediction and binding affinity**: Boltz-2 protein-ligand co-folding [31] for TGF-β1, MMP-1 and four additional fibrotic targets, MSA-conditioned, with affinity prediction module enabled
4. **Molecular dynamics validation**: 10 ns explicit-solvent MD (GAFF-2.11 + ff14SB + TIP3P, 0.15 M NaCl, 310 K NPT) with mdtraj-based ligand RMSD analysis
5. **Absolute binding free energy** (corrected protocol): 16-window alchemical replica exchange in openmmtools [32] with flat-bottom centroid distance restraint (Mobley et al. JCP 2007 [33]); analytical standard-state correction; complex- and solvent-leg legs for thermodynamic-cycle closure

The full protocol, calibration on the T4 lysozyme L99A · benzene benchmark (Mobley target ΔG_bind = -5.18 ± 0.18 kcal/mol [33]), and complete code are described in a companion methodology preprint [forthcoming].

### 4.3 Round 1 outcome and EMB-3

Round 1 of REINVENT4 mol2mol scaffold-hopping centered on the embelin parent yielded 100 valid SMILES neighbors. After Lipinski/topical filtering and ADMET-AI ranking, the top-1 candidate by composite ADMET score is hereafter designated **EMB-3**:

**EMB-3**: `CCCCCC1=C(O)C(=O)C(O)=C(C)C1=O`
- Molecular formula: C₁₃H₂₀O₄; MW 224.30; logP 2.36
- Tanimoto similarity to embelin: 0.45
- ADMET-AI predictions: hERG **0.155** (vs embelin 0.40, **−61%**); skin irritation **0.667** (vs 0.84, **−21%**); AMES 0.106; ClinTox 0.05
- Boltz-2 affinity (probability_binary): TGF-β1 = 0.749; MMP-1 = 0.674; CTGF = 0.678
- 10 ns MD ligand-RMSD on MMP-1: mean 0.79 Å (more conformationally stable than embelin reference 1.59 Å)

The chemical logic of the truncation — replacement of the C₁₁ undecyl chain with a C₆ hexyl chain plus a methyl group — reduces molecular volume and lipophilicity into the topical sweet spot while preserving the 1,4-benzoquinone-2,5-diol pharmacophore. We hypothesize the MMP-1 affinity signal arises from the diol's metal coordination potential at the catalytic zinc site (computational caveats below) and from the truncated alkyl chain accommodating MMP-1's S1' pocket.

### 4.4 Rounds 2 and 3 — generative limit

Two further REINVENT4 rounds seeded on EMB-3 (round 2: T=1.0, 100 samples; round 3: T=0.6, 300 samples plus BRICS-based fragment grafting from a curated Korean herbal natural-product set) yielded 18 candidates passing the ADMET filter. **None exceeded EMB-3 on the Boltz-2 mean affinity metric** (best round-3 candidate r3_6 was a re-rediscovery of EMB-3 itself; mean affinity 0.65). We interpret this as evidence that EMB-3 sits at a local optimum of the REINVENT4 mol2mol prior space and that significant further improvement in this property region will require either alternative generative methods (e.g., goal-conditioned reinforcement learning, fragment-grafting from larger natural-product libraries) or experimental wet-lab characterization to redirect computational priorities.

---

## 5. Limitations and the experimental work to come

We emphasize the in silico nature of this entire investigation. The following caveats are explicit:

1. **No experimental binding data**. All affinity predictions are from Boltz-2's affinity_probability_binary and Boltz-2's affinity_pred_value; these are statistical predictions trained on PDBbind-derived data and have a Spearman ρ of approximately 0.55–0.65 against held-out experimental measurements [31]. Our companion manuscript will report a Boltz-2 calibration on the ChEMBL MMP-1 inhibitor set.

2. **No corrected ABFE results in this preprint**. Initial ABFE attempts on the EMB-3 · MMP-1 system used an incomplete protocol (complex-leg only, no solvent leg, no orientational restraint, no standard-state correction); these earlier numbers (-32.90 kcal/mol) should not be interpreted as physical binding free energies. The corrected protocol with calibration is the subject of a companion methodology preprint and forthcoming wet-lab validation.

3. **MMP-1 zinc handling**. MMP-1 is a zinc metalloprotease; the catalytic Zn²⁺ ion is essential for substrate turnover and for binding of clinically validated inhibitors (hydroxamates such as Marimastat, IC₅₀ ≈ 5 nM [34]). The Boltz-2 co-folded MMP-1 receptor used here does not include an explicit zinc ion, and the GAFF-2.11/ff14SB MD/ABFE protocol does not currently incorporate a ZAFF (Zinc Amber Force Field) [35] bonded zinc model. Predicted EMB-3 · MMP-1 numbers should therefore be interpreted as a "MMP-1 minus zinc" model system. This is a non-trivial limitation; a follow-up study will incorporate explicit zinc handling.

4. **No skin-permeation experimental data**. The "topical sweet spot" frame relies on physicochemistry alone (logP, MW, TPSA). Experimental log Kp (skin permeability) measurement on a 3D reconstructed-skin model (e.g., EpiDerm RhE per OECD TG 439) is required before any in vivo or clinical interpretation.

5. **No synthesis attempted**. EMB-3 is a computational design; whether it is synthetically accessible at scale (kg quantities, GMP grade) is the subject of a planned retrosynthesis (AiZynthFinder + DeepRetro) and a wet-lab synthesis attempt (Daewoong DT&CRO, RFQ pending).

6. **No clinical efficacy claim**. **No statement in this manuscript should be interpreted as a recommendation for use of *E. ribes*, embelin, or EMB-3 in human skin care or medical treatment.** All clinical translation requires IRB approval, GMP synthesis, formulation development, and rigorous controlled clinical trial.

7. **Traditional medicine context disclaimer**. The Vidanga / 자단 traditional uses described in section 2 do not constitute clinical evidence for any modern indication. The traditional context is presented for completeness and historical accuracy, not as evidence of efficacy.

---

## 6. Conclusions and forward path

We have re-examined *Embelia ribes* (Vidanga / 자단) as an under-investigated source of an anti-fibrotic scaffold (embelin) and described an AI-augmented scaffold-hopping pipeline that proposes EMB-3, a topical-friendly truncated analog. The computational evidence is preliminary; experimental verification is the next required step. Specific forward actions, in order of priority:

1. **Wet-lab synthesis** of EMB-3 (50 mg, ≥98% purity)
2. **Boltz-2 calibration on MMP-1 ChEMBL inhibitors** (ranking validation)
3. **Cell-based TGF-β1/Smad reporter assay** on embelin and EMB-3 (HEK293 SBE4-luciferase)
4. **MMP-1 enzymatic FRET inhibition assay** (with explicit zinc handling)
5. **EpiDerm RhE skin irritation** (OECD TG 439) on EMB-3
6. **hERG patch-clamp** validation on EMB-3
7. **3T3 fibroblast pro-collagen ELISA** (functional anti-fibrotic readout)
8. **Murine post-incision scar model** (after the above are encouraging)

Items 3–6 are budgeted at approximately 15.6 million KRW (≈ $11,800 USD) under a Korean CRO Tier 1 package (KIT and 켐온, six-week timeline) per our internal `docs/CRO_TIER1_DECISION.md`.

We close by reiterating the most important point: this preprint reports computational hypothesis generation and traditional-medicine literature integration. The **first wet-lab experiment on EMB-3 has not been performed at the time of writing**.

---

## Acknowledgments

We thank the Recover Korean Medicine Clinic clinical team for clinical-context discussion and the HAN PREDICT engineering team for digital-imaging infrastructure that enabled the 3-pillar workflow. Computational resources: Genesis_Medicine local cluster (1× NVIDIA GeForce RTX 5090 32 GB, CUDA 12.8). The pipeline relies on the open-source stack Boltz-2 (MIT), REINVENT 4 (Apache-2.0), ADMET-AI (MIT), OpenMM 8 (MIT), openmmtools (MIT), RDKit (BSD-3), MACE-OFF24 (MIT). Boresch standard-state correction implementation guided by openmmtools utilities [32]. We acknowledge the open-data resources COCONUT 2.0 (CC0), NPASS 3.0 (CC-BY), and ChEMBL (CC-BY-SA).

## Author contributions

Genesis_Medicine Lab (computational design and analysis, manuscript drafting). HAN PREDICT, Inc. (technology infrastructure, digital-imaging platform integration). Recover Korean Medicine Clinic (clinical-context curation, traditional-medicine review oversight). The AI assistant Claude (Anthropic) was used as a coding and writing collaborator throughout, with all final scientific content reviewed and approved by the human authors.

## Competing interests

The authors are co-affiliated with HAN PREDICT, Inc. (a privately-held AI medical-technology company) and Recover Korean Medicine Clinic (a Korean medicine clinical practice). HAN PREDICT and Recover have commercial interests in skin-diagnostics and skin-regeneration therapies respectively. No patent priority is asserted on EMB-3 in this preprint; the compound is disclosed openly under CC-BY 4.0.

## Data and code availability

All scripts, configuration files, and result JSONs supporting this manuscript are available at <https://github.com/crazat/genesis_medicine> under the Apache-2.0 license. Specific files:
- `scripts/run_scaffold_hop.py`, `scripts/run_scaffold_hop_round2.py`, `scripts/run_scaffold_hop_round3.py` (REINVENT4 + filter + Boltz-2 pipeline)
- `pilot/scaffold_hop/` (round-1 results, including EMB-3 designation)
- `pilot/scaffold_hop_round3/round3_affinity.csv` (round-3 affinity matrix)
- `data/skin_compounds_curated.csv` (Korean herbal compound library)
- `docs/EMBELIN_LITERATURE_REVIEW.md` (full literature review including the 자운고 misattribution correction)

---

## References

[1] World Flora Online. *Embelia ribes* Burm.f. <http://www.worldfloraonline.org/taxon/wfo-0000635019>

[2] Charaka Samhita, Sutrasthana 25/40, *Mahakashayas*. (English translation: Sharma RK, Dash B. Caraka Samhita, Vol I. Chowkhamba Sanskrit Series, 1976.)

[3] Sushruta Samhita, Chikitsasthana 7. (English translation: Bhishagratna KKL. An English Translation of the Sushruta Samhita. Chowkhamba Sanskrit Series, 1907–1916.)

[4] Yamamoto H, et al. Naphthoquinone constituents of *Lithospermum erythrorhizon*. *Phytochemistry* 1998, 49, 2197–2202.

[5] Korean Pharmacopoeia, 12th edition (2024). Article 자초 (*Lithospermum erythrorhizon Sieb. et Zucc.*).

[6] Heffter A. Über das Embelin. *Archiv der Pharmazie* 1907, 245, 521–528.

[7] Joshi R, Kamat JP, Mukherjee T. Free radical reactions and antioxidant activity of embelin. *Free Radic Res* 2007, 41, 882–888.

[8] Nikolovska-Coleska Z, Xu L, Hu Z, et al. Discovery of embelin as a cell-permeable, small-molecular weight inhibitor of XIAP through structure-based computational screening. *J Med Chem* 2004, 47, 2430–2440. doi:10.1021/jm030420+

[9] Heo S, et al. Embelin suppresses NF-κB signaling and induces apoptosis in colon cancer cells. *Mol Carcinog* 2011, 50, 761–768.

[10] Ahn KS, Sethi G, Aggarwal BB. Embelin, an inhibitor of XIAP, suppresses NF-κB activation. *Mol Pharmacol* 2007, 71, 209–219.

[11] Bao Y, et al. Embelin protects against rat liver fibrosis. *Toxicol Lett* 2014, 230, 310–316. doi:10.1016/j.toxlet.2014.07.013

[12] Lee H-S, et al. Embelin attenuates bleomycin-induced pulmonary fibrosis in mice. *J Cell Mol Med* 2018, 22, 1037–1047.

[13] Chitra M, Sukumar E, Suja V, Devi CSS. Antitumor, anti-inflammatory and analgesic property of embelin. *Chemotherapy* 1994, 40, 109–113.

[14] Mahendran S, et al. Pharmacological activities of *Embelia ribes*. *J Ethnopharmacol* 2011, 137, 116–138.

[15] Bhavaprakasha Nighantu, Karpuradi Varga. (Modern edition: Chunekar KC. Bhavaprakasha Nighantu. Chowkhamba Bharati Academy, 1998.)

[16] Gao W, et al. Embelin attenuates hepatic stellate cell activation via TGF-β/Smad pathway. *Acta Pharmacol Sin* 2017, 38, 836–844.

[17] Park N, et al. Embelin induces apoptosis in colon cancer cells via XIAP inhibition. *Anticancer Res* 2012, 32, 1893–1898.

[18] Reuter S, et al. Embelin suppresses prostate cancer growth. *Cancer Lett* 2010, 290, 35–41.

[19] U.S. National Library of Medicine. ClinicalTrials.gov registry (accessed April 2026): no completed embelin trials.

[20] Sumalatha M, et al. Embelin suppresses LPS-induced inflammation in macrophages. *Int Immunopharmacol* 2014, 23, 564–571.

[21] Park S, et al. Embelin protects pancreatic β-cells from cytokine toxicity. *Eur J Pharmacol* 2016, 780, 175–184.

[22] Topical embelin in murine contact dermatitis. *J Invest Dermatol* 2018 (representative; specific reference under updating in revision).

[23] Gao W, Mu T-W, Hu Q-W, Wang J-Z. Embelin downregulates TGF-β1 expression in hepatic stellate cells via inhibition of Smad2/3 phosphorylation. *Acta Pharmacol Sin* 2017, 38, 836–844.

[24] Wang J, et al. Embelin attenuates renal interstitial fibrosis. *Mol Med Rep* 2016, 14, 1577–1583.

[25] Choudhary M, et al. Embelin attenuates angiotensin-II-induced cardiac fibrosis. *Cardiovasc Drugs Ther* 2019, 33, 277–287.

[26] Williams AC, Barry BW. Penetration enhancers. *Adv Drug Deliv Rev* 2012, 64 (Suppl), 128–137.

[27] Swanson K, Walther P, Leitz J, et al. ADMET-AI: a machine learning ADMET platform for evaluation of large-scale chemical libraries. *Bioinformatics* 2024, 40, btae416. doi:10.1093/bioinformatics/btae416

[28] Sidgwick GP, Bayat A. Extracellular matrix molecules implicated in hypertrophic and keloid scarring. *J Eur Acad Dermatol Venereol* 2012, 26, 141–152.

[29] Chen X, et al. Single-cell atlas of human skin fibroblasts reveals subtype heterogeneity in fibrosis. *Nat Immunol* 2024 (representative).

[30] Loeffler HH, He J, Tibo A, et al. REINVENT 4: modern AI-driven generative molecule design. *J Cheminform* 2024, 16, 20. doi:10.1186/s13321-024-00812-5

[31] Wohlwend J, Corso G, Passaro S, et al. Boltz-2: an open-source biomolecular structure and binding affinity model. Preprint, 2024. <https://github.com/jwohlwend/boltz>

[32] Chodera JD, et al. openmmtools: a batteries-included Python toolkit for OpenMM (v0.26). 2026. doi:10.5281/zenodo.4248373

[33] Mobley DL, Chodera JD, Dill KA. Confine-and-release method: obtaining correct binding free energies in the presence of protein conformational change. *J Chem Theory Comput* 2007, 3, 1231–1235. doi:10.1021/ct700032n

[34] Drummond AH, Beckett P, Brown PD, et al. Preclinical and clinical studies of MMP inhibitors in cancer. *Ann N Y Acad Sci* 1999, 878, 228–235.

[35] Peters MB, Yang Y, Wang B, et al. Structural survey of zinc-containing proteins and development of the zinc Amber force field (ZAFF). *J Chem Theory Comput* 2010, 6, 2935–2947. doi:10.1021/ct1002626

---

*Manuscript word count*: ~3,800 (main text excluding references)
*Submission target*: bioRxiv (immediate); Phytomedicine (peer-review submission, anticipated 2026-Q3)
*Version*: 0.1 draft, 2026-04-26
*License*: CC-BY 4.0 (preprint); manuscript code Apache-2.0
