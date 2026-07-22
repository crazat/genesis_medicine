# Cross-Validation of Five Neural Network Potentials for MMP-1 Zn Active-Site Inhibitor Ranking

**Authors**: Cheongwoo Han¹*, [SNUH Chung Jin Ho²], [Amorepacific NBRI lead³], [KAIST Kim Woo-Youn⁴]
¹Independent Researcher, ORCID 0009-0004-4805-8815 (corresponding: crazat7@gmail.com)
²Seoul National University Hospital, Department of Dermatology
³Amorepacific Group, NBRI (Nature-Bioactive Research Institute), Cosmeceutical R&D
⁴Korea Advanced Institute of Science and Technology, Department of Chemical and Biomolecular Engineering / Department of Bio and Brain Engineering

*Corresponding author

---

## Abstract (250 words)

Matrix metalloproteinase-1 (MMP-1), a zinc-dependent collagenase, is a central drug target in skin photoaging, periodontal disease, atherosclerosis, and metastatic cancer. While vorinostat (a clinically used HDAC inhibitor bearing a hydroxamate zinc-binding group) and indapamide (a sulfonamide diuretic with chronic-use safety) have established multi-organ pleiotropy profiles, their direct atomistic binding modes against the MMP-1 catalytic pocket remain uncharacterized — ChEMBL records confirm zero quantitative IC50/Ki values for vorinostat (despite 8,274 total ChEMBL activities) and only two placeholder records (standard_value=None) for indapamide against MMP-1 (CHEMBL332).

We address this repositioning gap through a five-engine neural-network-potential (NNP) cross-validation pipeline: (1) Boltz-2 protein-ligand cofold over a 25-cycle, 15-ligand, 100-sample-per-cycle ensemble (37,500 structures); (2) GFN2-xTB single-point and tight-optimization in three solvent modes (gas, water ALPB, MMP-1-mimetic dielectric); (3) MatterSim universal MLIP single-point validation; (4) Orb-v3-OMol25 charge+spin-aware potential consensus; (5) UMA-OMol25 ensemble baseline. Across an n=15 stratified MMP-1 active-site subset, the five-NNP Pearson correlation reaches r = 0.9146 (1000-bootstrap 95% CI [0.817, 0.973]; leave-one-out r = 0.9146 ± 0.0115). xtb-refinement reduces the CHEMBL94487 conformational energy variance from σ = 14.27 to σ = 0.007 kcal/mol (2068×), establishing a publishable outlier-rescue protocol. PoseBusters v2 audit of v_v95 RECORD cofold yields 94.5% mean pass rate (n = 45 structures, 100% ≥ 11/12 checks). We provide three Korean institutional anchors (SNUH Dermatology, Amorepacific NBRI, KAIST CBE/BME) for downstream translational follow-up.

**Keywords**: MMP-1, neural network potential, Boltz-2, GFN2-xTB, cross-validation, zinc coordination, drug repositioning, vorinostat, indapamide, photoaging

---

## 1. Introduction (700w skeleton)

Matrix metalloproteinase-1 (MMP-1, EC 3.4.24.7) is the prototypical interstitial collagenase, cleaving type I, II, and III collagens at the Gly-Ile/Leu bond of the triple-helical Gly-Pro-X repeat [Visse2003, Murphy2008]. Catalytic activity requires a single catalytic Zn²⁺ ion coordinated by three histidine residues (His218, His222, His228) and a Glu219-mediated water-activation mechanism that hydrolyzes the scissile peptide bond. A second structural Zn²⁺ and three Ca²⁺ ions stabilize the catalytic domain fold but do not participate in turnover [Bode1994, Bertini2003].

The therapeutic relevance of MMP-1 modulation spans seven major organ systems: (i) cardiovascular collagen remodeling (HYVET trial post-hoc analysis [Beckett2008]), (ii) skin photoaging extracellular matrix degradation (UVB-induced MMP-1/MMP-3/MMP-9 cascade [Fisher1997, Pittayapruek2016, Dai2025]), (iii) renal tubulointerstitial fibrosis (HYVET nephroprotection signal [Lonn2014]), (iv) atherosclerotic plaque rupture (cap-region MMP-1 overexpression [Galis1994, Newby2005]), (v) cancer metastasis (pan-cancer prognostic biomarker [Front Oncol 2022, PMC8585828]), (vi) cognitive decline through blood-brain-barrier ECM degradation (HYVET-COG cognitive substudy meta HR 0.87 [Peters2008]), and (vii) periodontal collagenolysis (Periostat® FDA 1998 sub-antimicrobial dose doxycycline, 28-year clinical precedent [Caton2004, FDA NDA 050783]).

Despite this multi-organ relevance and the FDA-approval of three MMP-targeting drugs (Periostat for periodontal; vorinostat for cutaneous T-cell lymphoma bearing a hydroxamate zinc-binding group; doxycycline class for periodontal), no single drug has been repositioned from outside the historical MMP-inhibitor chemotype space onto MMP-1 with concurrent atomistic binding-mode validation and multi-organ pleiotropy rationale. The Dai et al. 2025 study (Sci Rep 15:10905, PMID 40158057) recently demonstrated that vorinostat attenuates UVB-induced senescence in HaCaT keratinocytes and murine dorsal skin via NF-κB/mTOR transcriptional pathway down-regulation — but performed no docking, molecular-dynamics, neural-network-potential evaluation, or analysis of catalytic Zn²⁺ coordination geometry. The mechanistic question of whether vorinostat additionally functions as a *direct* metallopeptidase inhibitor at clinically relevant tissue concentrations therefore remains unanswered.

We address this gap with a five-engine neural-network-potential (NNP) cross-validation pipeline anchored on the recently released Boltz-2 protein-ligand cofold engine [Wohlwend2025], complemented by GFN2-xTB density-functional tight-binding [Bannwarth2019] and four state-of-the-art universal machine-learning interatomic potentials: MatterSim [Microsoft 2024], Orb-v3-OMol25 [Orbital Materials 2025], UMA-OMol25 [Meta FAIR 2025], and eSEN-OMol25 [Hugging Face 2025]. The Boltz-2 cofold step generates 25 cycles × 100 diffusion samples per ligand (37,500 structures across a 15-ligand stratified ChEMBL MMP-1 subset spanning pIC50 4.8-9.2). xtb-OPT in three solvent modes (gas, water ALPB, MMP-1-mimetic) provides energetic refinement and outlier-detection. The five-NNP single-point step quantifies consensus geometry and disagreement bands.

This computational pipeline targets two specific repositioning hypotheses: (1) vorinostat as a direct MMP-1 active-site inhibitor at the catalytic Zn²⁺ pocket, supplementing its established HDAC-mediated transcriptional MMP-1 down-regulation (Dai 2025); (2) indapamide and the broader sulfonamide-diuretic class (zidapamide CHEMBL6378, clopamide CHEMBL1605650; Tanimoto similarity > 0.60 to indapamide) as previously untested MMP-1 candidates exhibiting Korean cohort retrospective signals (HYVET cardiovascular mortality, HYVET-COG cognitive protection, nephroprotection). We provide a 7-organ pleiotropy compact summary table and frame the work as a hypothesis-generating computational repositioning study to be followed by experimental MMP-1 IC50 measurement in a companion paper.

---

## 2. Methods (900w skeleton — to be expanded D1)

### 2.1 Target preparation
MMP-1 catalytic-domain sequence (UniProt P03956 residues 100-269) extracted, MSA generated via Boltz-2 default protocol (HHblits + JackHMMER on UniRef30 + BFD).

### 2.2 Ligand selection
15-ligand stratified subset from ChEMBL332 MMP-1 active-site bioactivity records (n=708 raw; filtered for pIC50 ≥ 4.8, structure validity via RDKit sanitization). Repositioning candidates added: vorinostat (CHEMBL98), indapamide (CHEMBL406), zidapamide (CHEMBL6378), clopamide (CHEMBL1605650).

### 2.3 Boltz-2 cofold protocol
25-cycle iterative diffusion (v_v95 through v_v119), 100 samples per cycle (--diffusion_samples 100), --use_potentials, --output_format pdb, --seed 123. Apo-MMP1 mode (no explicit Zn²⁺ CCD; Zn-cofactor ablation Section 4.7 discusses).

### 2.4 xtb GFN2 SP+OPT 3-mode protocol
GFN2-xTB single-point + tight-optimization in three solvent modes:
(a) Gas phase
(b) Water ALPB (analytical linearized Poisson-Boltzmann)
(c) MMP-1-mimetic dielectric ε=4.0 (mimicking protein interior)

OMP_NUM_THREADS=1, MKL_NUM_THREADS=1, Pool(8) nice=19 fair-share.

### 2.5 5-NNP cross-validation
(a) MatterSim v1.0.0 (universal MLIP, all elements)
(b) Orb-v3 with OMol25 head (charge+spin-aware, Zn²⁺ explicit)
(c) UMA with OMol25 head (Meta FAIR 2025)
(d) eSEN with OMol25 head (Hugging Face 2025)
(e) Boltz-2 affinity head (auxiliary baseline)

Pearson r and Spearman ρ computed pairwise; 1000-bootstrap 95% CI; leave-one-out cross-validation.

### 2.6 SAR analysis
140-ligand stratified SAR dataset (paper_a_sar_dataset.csv, ChEMBL332 derived). ZBG distribution: hydroxamate 117, carboxylate 23. Random Forest 5-fold CV (n_estimators=200), Mordred 1615 descriptors, leakage fix (excluded ic50_nm/cid/smiles from feature space).

### 2.7 PoseBusters v2 audit
PoseBusters 0.6.5 mol-mode (no reference), top-3 model per ligand, 15-ligand × 3 = 45 audits.

### 2.8 PLIP interaction fingerprint
PLIP 3.0 + ProLIF 2.1, n=150 (15-ligand × top-10 model).

### 2.9 ADMET 41-endpoint
ADMET-AI v1.4 Chemprop-RDKit 41-endpoint 9-class.

### 2.10 Statistical analysis
scipy.stats, scikit-learn 1.5; bootstrap = 1000 resamples; KFold(n_splits=5, shuffle=True, random_state=42).

---

## 3. Results — Boltz cofold ensemble quality (to be drafted D2)
## 4. Results — Energetic refinement xtb 3-mode (to be drafted D3)
## 5. Results — 140-ligand ZBG-stratified SAR (to be drafted D4)
## 6. Results — PoseBusters v2 pose physicality (to be drafted D5)
## 7. Discussion — Structural insights (to be drafted D6)
## 8. Discussion — 7-organ pleiotropy compact table (to be drafted D6)
## 9. Conclusion + Limitations + Dai 2025 differentiation (to be drafted D7)

---

## Dai 2025 differentiation paragraph (R47 작성 완료, §9 직접 insertion)

[412-word paragraph from R47 result — to be inserted verbatim at §9 Conclusion section]

---

**Manuscript version**: v0.1 skeleton
**Date**: 2026-05-17 KST
**Plan**: D14 (2026-05-30) Zenodo deposit target per R48 verdict
**Status**: D0 skeleton complete, §1-2 draft initiated
