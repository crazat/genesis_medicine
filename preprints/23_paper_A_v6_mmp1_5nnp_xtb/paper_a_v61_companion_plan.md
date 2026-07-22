# paper_A v6.1 Companion Paper Plan — Systematic HDAC Inhibitor Class Computational Repositioning for MMP-1

**Sequence**: paper_A v6 (Part I, D14 Zenodo 2026-05-30) → **paper_A v6.1 companion (D90-D180)** → paper_A Part II Korean HIRA retrospective (D300) → paper_A Part III Nat Rev DD perspective (D540)

**Authoring lead**: Cheongwoo Han (crazat7@gmail.com, ORCID 0009-0004-4805-8815)
**Date drafted**: 2026-05-17 KST (R50 results-derived)

---

## Title (draft)

**"Systematic Computational Repositioning of FDA-Approved Histone Deacetylase Inhibitors Against MMP-1: Atomistic Binding-Mode Rationalization Across Five Zinc-Binding Group Chemotypes"**

## Abstract sketch (~250w)

Histone deacetylase (HDAC) inhibitors are clinically approved for cutaneous T-cell lymphoma (Vorinostat, Romidepsin), peripheral T-cell lymphoma (Belinostat), multiple myeloma (Panobinostat, withdrawn 2022), Duchenne muscular dystrophy (Givinostat, 2024), and clinical-stage indications (Mocetinostat, Entinostat). All six drugs target intracellular HDAC enzymes via zinc-binding group (ZBG) chemotypes — yet none has been characterized for direct matrix metalloproteinase-1 (MMP-1) catalytic Zn²⁺ engagement at the atomistic level, despite the canonical hydroxamate ZBG (Vorinostat, Belinostat, Panobinostat, Givinostat) being chemically isosteric to clinical MMP-pan inhibitors (marimastat, ilomastat). All seven HDAC inhibitors examined here have zero quantitative ChEMBL332 (MMP-1) records as of 2026-05-17, defining a class-wide repositioning gap.

We apply the paper_A v6 atomistic pipeline (Boltz-2 cofold 25 cycles × 100 samples per ligand = 15,000 cofold structures across 6 ligands, GFN2-xTB SP+OPT 3-mode, 6-NNP cross-validation Orb-v2 + MACE-OMol25 + Orb-v3-OMol25 + UMA-OMol25 + eSEN-OMol25 + SevenNet-Omni) systematically across **three ZBG taxa**: (i) hydroxamate (Vorinostat reference + Belinostat + Panobinostat + Givinostat); (ii) **bicyclic depsipeptide prodrug → thiol** (Romidepsin, with custom Boltz protocol including intracellular GSH-mediated disulfide reduction modeling); (iii) benzamide (Mocetinostat + Entinostat) as ZBG-geometry negative controls.

Hypothesized findings: (H1) hydroxamate class uniform sub-µM consensus affinity; (H2) reduced Romidepsin thiol comparable to captopril/mercaptoacetyl peptide MMP inhibitor reference; (H3) benzamide class ≥1 log₁₀ weaker (S1' pocket selectivity validated); (H4) **Givinostat-DMD muscle fibrosis MMP-1 axis** (PMID 18440885) establishes the **8th organ system** for paper_A pleiotropy framework.

## Scope and Tier classification

### Tier-1 ligands (atomistic deep-dive treatment, all 6 with full Boltz cofold protocol)

| Drug | ChEMBL ID | FDA status | ZBG class | Indications |
|------|-----------|------------|-----------|-------------|
| Vorinostat (SAHA) | CHEMBL98 | 2006 | Hydroxamate (simple aliphatic) | CTCL |
| **Belinostat (PXD101)** | **CHEMBL408513** | 2014 | Hydroxamate (sulfonyl cinnamic) | Peripheral T-cell lymphoma |
| **Panobinostat (LBH589)** | CHEMBL483254 | 2015 (withdrawn 2022) | Hydroxamate (cinnamic) | Multiple myeloma |
| **Givinostat (ITF-2357, Duvyzat®)** | **CHEMBL1213492** | **2024** | Hydroxamate | **Duchenne muscular dystrophy (first nonsteroidal therapy, all genotypes)** |
| **Romidepsin (FK228)** | **CHEMBL343448** | 2009 | **Bicyclic depsipeptide → thiol prodrug** | CTCL, peripheral T-cell lymphoma |

### Negative control ligands (benzamide class, expected null MMP-1 engagement)

| Drug | ChEMBL ID | FDA status | ZBG class |
|------|-----------|------------|-----------|
| Mocetinostat (MGCD0103) | CHEMBL272980 | Phase II | Benzamide (2-aminoanilide) |
| Entinostat (MS-275) | CHEMBL27759 | Phase III | Benzamide (2-aminoanilide) |

## Custom Boltz-2 protocol for Romidepsin thiol-ZBG hypothesis

Romidepsin (FK228) is a bicyclic depsipeptide prodrug; upon cellular uptake, intracellular glutathione (GSH) reduces an intramolecular disulfide bond between Cys2-S-S-Cys2' of the bicyclic core, exposing two free thiolates that engage the HDAC catalytic Zn²⁺ pocket (~7-9 Å Zn-to-S distance per available HDAC8 crystal structures, e.g., PDB 5VI6 analog). Standard Boltz-2 YAML cofold workflow handles closed-form (disulfide-bridged) Romidepsin; for the reduced thiol-Zn²⁺ MMP-1 binding hypothesis, we will:

1. Pre-reduce the SMILES (replace `SS` → `S.S` with hydrogen-saturated thiolates, net charge -1 from one deprotonated S⁻ at physiological pH 7.4)
2. Pre-protonate one thiol explicitly (OpenBabel `obabel -p 7.4` then manual edit if needed)
3. Boltz-2 cofold YAML with explicit `--include_ligand_protonation` if available, otherwise treat reduced form as separate ligand input
4. Cross-validate against captopril (CHEMBL1560) and ilomastat thiol MMP inhibitor reference set
5. 5-NNP cross-validation with explicit thiolate Zn²⁺ coordination (Orb-v3-OMol25 charge+spin-aware handles -1 thiolate explicitly)

## Hypotheses test plan

| Hypothesis | Test design | Expected outcome | Falsifiability |
|------------|-------------|------------------|----------------|
| **H1** Hydroxamate class uniform Zn coordination | 4 hydroxamate × 25 Boltz cycles × 100 samples × 5-NNP cross-val | Mean dG_bind range -8 to -12 kcal/mol consensus | Any drug ranking outside 1.5× CV = falsification |
| **H2** Reduced Romidepsin thiol vs captopril reference | Custom Boltz protocol + 5-NNP holo Zn-S coordination geometry | Comparable thiolate-Zn distance 2.3-2.5 Å | Distance > 3.0 Å or sub-stoichiometric coordination = falsification |
| **H3** Benzamide negative control | Mocetinostat + Entinostat 25-cycle Boltz consensus | dG_bind ≥ -3 kcal/mol (weak) or geometric mismatch | If benzamide ranks in top-4 with hydroxamate class = falsification of selectivity logic |
| **H4** Givinostat-DMD-MMP-1 axis | Korean DMD registry (~50-100 patients per Cohort Profile Y2024 study) + Givinostat exposure ATC L01XH04 | Muscle fibrosis biomarker correlation Givinostat-treated < untreated | No correlation in registry-level analysis = paper_A v6.1 §5 caveat |

## Methodology stack (identical to paper_A v6)

- **Boltz-2 cofold**: 25 cycles × 100 samples per ligand (Wohlwend 2025 bioRxiv 2025.06.14.659707)
- **GFN2-xTB SP+OPT 3-mode**: gas + water-ALPB + MMP-1-mimetic ε=4.0 (Bannwarth 2019 PMID 30741547)
- **5-NNP cross-validation**: Orb-v2 + MACE-OMol25 + Orb-v3-OMol25 + UMA-OMol25 + eSEN-OMol25 (paper_A v6 baseline, extended to 6-NNP with SevenNet-Omni for class extension validation)
- **PoseBusters v2 audit**: top-3 model per ligand × 6 ligands = 18 audits (target 94.5% pass rate parallel to paper_A v6)
- **140-ligand SAR Mordred descriptor analysis**: ZBG class-stratified RF (hydroxamate 117 from paper_A v6, +6 HDAC inhibitor candidates as out-of-distribution prediction set)
- **PLIP + ProLIF interaction fingerprints**: per-ligand × top-10 model = 60 PDBs
- **ADMET-AI 41-endpoint**: 6 ligands

## Korean HIRA cohort extension (paper_A Part II.1)

For paper_A Part II (D300 *JAMA Network Open* / *Lancet Healthy Longevity* target), HDAC inhibitor class adds:

- **Vorinostat (ATC L01XH01)**: Cosmetic dermatology cohort hint (Korean repurposing trial possible)
- **Belinostat (ATC L01XH02)**: PTCL national prescription pattern HIRA-NPS lookup
- **Panobinostat (ATC L01XH03, withdrawn)**: Historical 2015-2022 Korean prescription cohort
- **Givinostat (ATC L01XH04 expected)**: DMD/Becker family Korean cohort linkage (KMD Korean Muscular Dystrophy Registry, KOFAS Korean Familial Familial Ataxia and Spinocerebellar disorder, etc.)

ATC code linkage may not yet exist for newer drugs (Givinostat 2024); HIRA registry workaround = drug brand name (Duvyzat) + ICD-10 G71.0 (DMD).

## Timeline (post-paper_A v6 D14 Zenodo deposit)

```
D14    paper_A v6 Zenodo deposit (mini-preprint, 6 ligand pool incl Belinostat + Givinostat §5.8 supp)
D14-D60 paper_A v6 J Med Chem submission preparation + v6.1 prereqs collection
D60    paper_A v6 J Med Chem 1차 submission
D60-D90 paper_A v6.1 ligand pool finalization (6 ligands + 2 negative controls + reference set)
D90    paper_A v6.1 Boltz-2 cofold batch start (25 cycles × 6 ligands = 150 chain cycles, ~3-6 months wall on existing infrastructure)
D90-D150 5-NNP cross-validation + xtb 3-mode refinement + SAR analysis
D150-D180 Manuscript draft + Korean co-author intake
D180   paper_A v6.1 J Med Chem or Mol Pharm submission
```

## Expected ROI

- **Citation impact**: paper_A v6 (Part I) provides methodology + thesis, v6.1 confirms generalizability across class → cumulative citation effect 2-3× vs single paper alone
- **Translational impact**: Korean DMD therapy Givinostat-MMP-1 axis hint = potential clinical translation partnership with Italian Italfarmaco S.p.A. (Duvyzat® developer) + Korean DMD specialist clinics (Seoul National University Hospital Pediatric Neurology, Severance Pediatric Neurology, Asan Pediatric Neurology)
- **Methodology contribution**: First systematic atomistic repositioning across 5-ZBG-chemotype HDAC inhibitor class for MMP-1 = methodology template for other Zn-metalloenzyme targets (HDAC, carbonic anhydrase, BACE-1, etc.)

## Risk and mitigation

| Risk | Probability | Mitigation |
|------|-------------|------------|
| paper_A v6 J Med Chem rejection | 25% | Resubmit to *Mol Pharm* or *ChemMedChem* with v6.1 preprint companion as evidence of methodology robustness |
| Romidepsin custom protocol divergence | 30% | Fallback to closed-form Romidepsin only (excluded if thiol modeling fails) |
| Korean DMD cohort access blockage | 40% (rare disease cohort) | Partner with Korean DMD Patient Association (KDMDA) directly via Asan Pediatric Neurology |
| Class-wide R²=0.4 only (no consensus) | 25% | Document negative finding as publishable methodology limitation paper |
| 6-NNP infrastructure compute cost | 20% | xtb-Pool(8) Pool sustained 15min/1647 task throughput → 6 × 1647 = 10K tasks ~1.5h compute = trivially feasible on existing infrastructure |

## Publication venue strategy

- **1st choice**: *Journal of Medicinal Chemistry* (IF 7.4) — paper_A v6 trajectory continuation, computational repositioning core fit
- **2nd choice**: *Molecular Pharmaceutics* (IF 4.5) — pharmaceutical computational chemistry fit
- **3rd choice**: *ChemMedChem* (IF 3.6) — medicinal chemistry breadth
- **4th choice**: *European Journal of Medicinal Chemistry* (IF 6.0) — broader European medicinal chemistry audience

## References (R50-derived, 20 PMID/DOI 2022-2026)

(See R50 result memory inline; 20 references including Cao 2022 PMID 36030653 Belinostat-UVB, Bettica 2024 PMID 38508835 Givinostat-DMD, Cassier 2024 entinostat Phase III, Mocetinostat-OA PMC10544226, etc. + paper_A v6 references shared list 62 + this companion 추가 20 = ~82 total references for v6.1)

---

**Document status**: paper_A v6.1 companion paper plan v0.1 (D90-D180 trajectory, R50-derived)
**Date**: 2026-05-17 KST (paper_A v6 D14 Zenodo deposit 미리 v6.1 prereqs locked)
**Related memory rules**:
- `R50 HDAC inhibitor class extension` 결과 직접 활용
- `feedback_small_n_deterministic_fit_caveat` (Romidepsin n=6 candidates, validation 의무)
- `feedback_cascade_watcher_death_recovery` (Boltz cofold pipeline robustness)
