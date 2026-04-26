# Paper Plan — Genesis_Medicine v3 첫 in silico methodology paper

**작성일**: 2026-04-26
**Target submission**: 2026-07-15 (12주 timeline)
**Target journal**: J Cheminform (1순위) → RSC Med Chem (2순위) → Phytomedicine (3순위)

---

## 1. Working title

> **AI-driven scaffold-hopping of Embelin yields a multi-target anti-fibrotic
> lead candidate: an in silico investigation with calibrated absolute binding
> free energy**

대안:
- "Calibrated ABFE-driven optimization of Embelin scaffold for skin fibrosis"
- "From *Embelia ribes* to topical anti-fibrotic lead via REINVENT4 + Boltz-2 + ABFE"

---

## 2. Key claims (defensible)

### Strong claims (in silico, calibrated)
1. **Pipeline integration**: REINVENT4 mol2mol + ADMET-AI + Boltz-2 cofold + corrected ABFE forms a reproducible end-to-end skin-targeted lead optimization workflow
2. **Calibration check**: ABFE protocol validated on T4L99A·benzene benchmark (literature ΔG = -5.18 kcal/mol)
3. **Boltz-2 ranking on MMP-1**: established Spearman ρ = X (n=15 ChEMBL inhibitors)
4. **EMB-3 lead candidate**: scaffold-hop derivative of Embelin with hERG predicted improvement (0.40 → 0.16) and computationally favorable MMP-1 binding (calibrated ΔG_bind = X kcal/mol)
5. **Multi-target SAR**: TGF-β1/MMP-1/CTGF/SMAD3 affinity matrix of 5-8 compounds
6. **Selectivity**: EMB-3 vs MMP-2/3/9/13 selectivity index
7. **Cross-disease hypothesis**: based on shared TGF-β/MMP signaling, EMB-3 may apply to IPF (signal generated, wet-lab pending)

### Limitations explicitly stated
- ABFE absolute uncertainty ~1-2 kcal/mol; ranking more reliable than absolute
- No experimental IC50 or crystal structure
- Boltz-2 cofold poses are predictions
- Topical application requires formulation studies not yet performed
- Synthesis of EMB-3 not attempted (retrosynthesis predicted only)

### Claims we will NOT make
- "Novel composition" or "patent-ready lead" without IP analysis
- "Clinical candidate" or "preclinical lead"
- "Confirmed mechanism" without wet-lab
- 자운고 connection (false; corrected per `EMBELIN_LITERATURE_REVIEW.md`)
- "AlphaFold-era drug discovery" hype — replaced with sober methodology framing

---

## 3. Section-by-section outline

### Title page
- Authors, affiliations
- Genesis_Medicine v3 + Recover 한의원 acknowledgment

### Abstract (250 words)
- Background: skin fibrosis molecular targets + Embelin natural product context
- Methods: REINVENT4 + ADMET filter + Boltz-2 + corrected ABFE
- Calibration: T4L99A · benzene + Boltz-2 MMP-1 ChEMBL set
- Results: EMB-3 candidate, ΔG_bind = X kcal/mol, hERG improved
- Conclusion: in silico evidence for novel anti-fibrotic scaffold; wet-lab validation pending

### 1. Introduction (≈ 700 words)
- 1.1 Skin fibrosis (keloid/hypertrophic scar): molecular targets (TGF-β1, MMPs, CTGF)
- 1.2 Embelin: natural product context — *Embelia ribes* (Ayurvedic Vidanga, East Asian 자단), known XIAP/NF-κB/TGF-β activity in cancer/liver/lung; **no skin fibrosis study to date**
- 1.3 AI-driven lead optimization landscape (Boltz-2, REINVENT4) and the ABFE absolute binding gap
- 1.4 This work: integrated pipeline + calibration + scaffold-hopping case study

### 2. Methods (≈ 1500 words)
- 2.1 Software stack table: Boltz-2 v0.6.1, REINVENT4 v4.4, ADMET-AI v2.0.1, OpenMM 8.x + openmmtools 0.24, MACE-OFF24, RDKit
- 2.2 REINVENT4 scaffold-hop protocol: mol2mol_medium_similarity, T=1.0/0.6, 100/300 samples
- 2.3 ADMET filter cascade: physchem (Lipinski/topical sweet spot) + ADMET-AI (hERG/Skin/AMES)
- 2.4 Boltz-2 cofold: MSA generation, sampling/recycling, affinity prediction
- 2.5 **MD protocol**: ff14SB + GAFF-2.11 + AM1-BCC, TIP3P, 1.2 nm padding, 0.15 M NaCl, 310 K NPT, 10/50 ns
- 2.6 **Corrected ABFE**: Boresch restraints (k_r=10, k_θ=k_φ=100); complex + solvent legs; 16 windows × 5 ns × 17 replicas; analytical standard state correction (Boresch et al. 2003 eq. 32)
- 2.7 **Calibration**:
  - T4L99A · benzene (PDB 181L), expected ΔG_bind = -5.2 ± 0.2 kcal/mol
  - Boltz-2 MMP-1 ChEMBL set (n=15), Spearman/Pearson
- 2.8 Selectivity matrix: 5 MMPs × 5-8 ligands
- 2.9 Statistical analysis (MBAR, bootstrap CI, replicate runs)

### 3. Results (≈ 1800 words)
- 3.1 Pipeline calibration
  - T4L99A·benzene corrected ABFE: ΔG_bind = X ± Y kcal/mol (PASS/FAIL vs lit -5.18)
  - Boltz-2 MMP-1: Spearman ρ = X (n=15)
- 3.2 Embelin → EMB-3 scaffold-hop (Round 1)
  - 100 candidates → 1 lead, ADMET improvement
  - Tanimoto, MW, logP, polarity statistics
- 3.3 EMB-3 multi-target affinity
  - Boltz-2 affinity_pred: TGFB1/MMP1/CTGF/SMAD3
  - corrected ABFE on MMP-1: ΔG_bind = X ± Y kcal/mol (compared to Embelin parent)
  - corrected ABFE on TGFB1: optional
- 3.4 MD stability (10/50 ns)
  - RMSD trajectories, H-bond persistence, RMSF
- 3.5 Selectivity (MMP-2/3/9/13 panel)
- 3.6 Round 2 + Round 3 generative exploration
  - 음성 결과 → EMB-3 local optimum 입증
- 3.7 Cross-disease hypothesis (Open Targets IPF mapping)

### 4. Discussion (≈ 700 words)
- 4.1 What this study adds: corrected ABFE protocol + calibration → trustable ranking + reasonable absolute binding
- 4.2 Limitations:
  - in silico only; no IC50, no animal model
  - Boltz-2 absolute ranking limited (Spearman ~0.5-0.6)
  - ABFE absolute uncertainty ~1-2 kcal/mol
  - Topical formulation, skin permeation not experimentally measured
  - No synthesis of EMB-3 attempted
- 4.3 Comparison to literature scaffold-hopping AI papers (REINVENT4 publications, Boltz-2 use cases)
- 4.4 Honest traditional medicine context: Embelia ribes only, NOT 자운고 — `EMBELIN_LITERATURE_REVIEW.md`
- 4.5 Future work: synthesis (DT&CRO), wet-lab IC50 (KIT/켐온), animal scar model (mouse/rat)

### 5. Conclusion (≈ 200 words)
- One-paragraph summary
- "EMB-3 represents a calibrated in silico hypothesis, not a clinical candidate"

### Acknowledgments
- GPU resources, Recover 한의원 (motivation), open-source community (Boltz-2, REINVENT4, OpenMM)

### Data availability
- GitHub repo (Apache-2.0): scripts, configs, ABFE result JSONs
- ChEMBL accession IDs for calibration set
- ZENODO: ABFE trajectory checkpoints (optional, large)

---

## 4. Figures (8 main + ≤ 10 supplementary)

### Main
1. **Pipeline diagram** — REINVENT → ADMET → Boltz-2 → MD → ABFE flow
2. **Calibration**:
   (a) T4L99A·benzene ΔG_bind computed vs literature
   (b) Boltz-2 MMP-1 ChEMBL scatter (pIC50 vs predicted)
3. **EMB-3 vs Embelin chemical structure + Tanimoto + ADMET radar chart**
4. **MD stability**: RMSD time series for 5-8 ligands
5. **Corrected ABFE breakdown**: ΔG_complex / ΔG_solvent / ΔG_release / ΔG_bind for top compounds
6. **Multi-target affinity matrix** (5-8 ligand × 5 target heatmap)
7. **Selectivity panel** (MMP-1 vs MMP-2/3/9/13)
8. **SAR scatter**: in silico ΔG_bind vs hERG vs MW (3D bubble or 2D facets)

### Supplementary
- S1: Round 2/3 음성 SAR detail
- S2: Boresch anchor selection per ligand + restraint geometry
- S3: ABFE convergence diagnostics (replica swap, energy histograms)
- S4: Open Targets IPF mapping detail
- S5: ADMET full predictions table
- S6-S10: traj snapshots, raw MBAR matrices, etc.

---

## 5. 12-week schedule

| Week | Deliverable | Status |
|---|---|---|
| **W1** | T4L99A·benzene calibration ABFE complete | 🔄 시작 |
| **W2** | T4L PASS → re-run EMB-3 + Embelin corrected ABFE | |
| **W3** | Boltz-2 MMP-1 ChEMBL calibration (15 compounds, ~3h GPU) | |
| **W4** | SAR expansion: 5-8 ligands selected (literature analogs + decoys) | |
| **W5** | Corrected ABFE on full SAR set (5-8 systems × 14h = 70-110h GPU) | |
| **W6** | Selectivity panel (MMP-2/3/9/13) — Boltz-2 cofold | |
| **W7** | MD 50 ns extension on top 3 ligands | |
| **W8** | Manuscript draft Introduction + Methods | |
| **W9** | Manuscript draft Results + Discussion + Figures | |
| **W10** | Internal review + revision + supplementary | |
| **W11** | Final figures + supplementary + cover letter | |
| **W12** | Submission to J Cheminform | |

---

## 6. Critical risk register

| Risk | Probability | Mitigation |
|---|---|---|
| T4L calibration fails (ΔG ≠ -5 ± 2) | 30% | Iterate on restraint placement, lambda schedule, eq time. Drop to RBFE if ABFE intractable |
| Boltz-2 MMP-1 Spearman < 0.4 | 40% | Acknowledge ranking limitation, frame as "preliminary screen" |
| EMB-3 ΔG_bind > 0 (non-binder) | 20% | Honest result; paper still valid as methodology + 음성 결과 |
| Reviewer asks for wet-lab | 90% | Address upfront in cover letter: "in silico methodology paper, wet-lab framework provided in `docs/CRO_TIER1_DECISION.md`" |
| 자운고 narrative residue in any text | 0% (정정 commit) | EMBELIN_LITERATURE_REVIEW.md 채택 |

---

## 7. 즉시 결정 필요

### A. ABFE calibration 우선순위 — **최우선** (W1)
- T4L99A·benzene 1차 calibration RUN — 시작 명령:
  ```bash
  source .venv/bin/activate
  python scripts/abfe_calibrate_t4l.py --out pilot/calibration/t4l_benzene/
  ```
  - 예상 wall: 8-10 h GPU
  - 결과 PASS → W2 EMB-3 재실행 진입

### B. Boltz-2 MMP-1 calibration — **병행 가능**
- ChEMBL CSV 이미 작성 (`data/chembl_mmp1_calibration.csv`, n=15)
- 실행:
  ```bash
  python scripts/boltz2_calibration_mmp1.py --out pilot/calibration/boltz2_mmp1/
  ```
  - 예상 wall: 3 h GPU

### C. Embelin 정정 commit — **즉시**
- Memory + chemcrow_wrapper의 자운고 매핑 삭제
- `EMBELIN_LITERATURE_REVIEW.md` 채택

---

## 8. Honest framing 체크리스트

- [ ] Abstract에 "in silico" 명시
- [ ] Methods 모든 protocol detail (restraint, calibration) 명시
- [ ] Results의 모든 ΔG에 uncertainty 동반
- [ ] Discussion 한계 명시 (no wet, no synthesis, no crystal)
- [ ] Conclusion "candidate ≠ clinical lead" 명시
- [ ] Cover letter 솔직 자기 평가
