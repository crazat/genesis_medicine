# JCIM Submission Prep Plan — paper_A v6 (single-author)

Target: **J. Chem. Inf. Model. (ACS)**, non-OA route (free to publish; reader-pays).
Fallback if rejected: **PLoS ONE** (fee-assistance applicable). Zenodo priority already secured.

## Why condensation is the core task
`manuscript_v0.2.md` (536 lines, 239 refs, ~5,200 words core + heavy appendix narrative) accreted R27–R56 frontier-tech / Korean-funding / K-medical-tourism / commercialization / co-author-corridor material. For Zenodo that breadth is fine; for **JCIM it reads as non-scientific padding** and invites desk-rejection on focus. The JCIM version must be a tight computational-chemistry paper.

## KEEP (core science → JCIM)
- §2 Methods (target prep, ligand selection, Boltz-2 cofold protocol, xtb GFN2 3-mode, 3-NNP cross-val, PoseBusters, statistics)
- §3 Boltz-2 cofold ensemble quality (convergence, cross-NNP consensus r=0.9146, pose stability, cofold-vs-pIC50)
- §4 xtb energetic refinement (top-1/top-3 stability, **CHEMBL94487 σ 14.27→0.007 rescue**, σ-outlier n=5, Mordred correlation, mandatory-OPT-rescue workflow, Zn-cofactor ablation, **conformal intervals §4.10**, multiverse variance decomposition §4.11)
- §5 SAR (140-ligand ZBG-stratified RF, leakage-corrected, sub-RFs, **n=17 sulfonamide-diuretic OOD audit**, indapamide Tanimoto)
- §6 PoseBusters audit (94.5% pass, fail-mode, benchmark comparison)
- §9.2 Limitations (expand — wet-lab gap as honest limitation + future work)
- Figures 1–5 (all keep)

## CUT or move to Zenodo-SI only (NOT in JCIM body)
- §3.6 Korean HPC 2-tier infrastructure narrative
- §5.5 Korean pharmacogenomic / cis-MR / GWAS corridor narrative (condense to 1-2 sentences max, or cut)
- §6.6–6.8 DDI safety extended + Korean/APAC cosmeceutical regulatory + federated ADMET (condense §6.6.1 selectivity to keep; cut tourism/regulatory)
- §8 7-organ pleiotropy "Korean cohort linkage" table → keep mechanism, cut the institutional-corridor columns
- §9.3 Future Directions — cut funding-pathway bullets (NIH SBIR/ARPA-H/Wellcome/Schmidt/NRF/TIPS/IPO/commercialization), PROTAC v7 trajectory, quantum-computing v7, Genesis Medicine Lab incorporation. Keep 1 short "future work" paragraph (wet-lab validation + class extension).
- All "institutional reference network" residual framing (already neutralized; verify none reads as collaboration)

## Reference trim 239 → ~90
- Drop refs cited ONLY by the cut narrative sections (funding/tourism/commercialization/frontier-round picks).
- Keep refs that are load-bearing for KEEP sections (methods tools, benchmark comparisons, MMP-1 biology core, repositioning precedent, Dai et al. differentiation).
- Renumber sequentially after trim; sync in-text `ref N` ↔ references.md.

## JCIM formatting
- Structure: Title / Abstract / Introduction / Methods / Results and Discussion / Conclusions / Associated Content (SI → Zenodo DOI) / Author Information / References.
- Abstract ≤ 250 words (current OK). TOC graphic (can reuse Figure 1 or a composite).
- Figures: separate high-res files (PDF/TIFF 300+ dpi) — already have PNG+PDF.
- SI: point to the Zenodo data DOI (don't inline 27k CSVs).
- Single corresponding author: Cheongwoo Han, crazat7@gmail.com, ORCID 0009-0004-4805-8815, Independent Researcher.

## Order of execution (autonomous, multi-tick)
1. [done] Cover letter draft (`cover_letter_JCIM_v0.1.md`)
2. Create `manuscript_JCIM_v0.1.md` = copy of v0.2, then apply CUT list (keep v0.2 intact as the Zenodo/comprehensive version)
3. Reference trim + renumber on the JCIM copy
4. Reformat to JCIM section structure + Associated Content (Zenodo SI DOI)
5. Final word-count + ref-count + figure-callout consistency pass
6. Hand to user for submission (user does the ACS Paragon upload)
