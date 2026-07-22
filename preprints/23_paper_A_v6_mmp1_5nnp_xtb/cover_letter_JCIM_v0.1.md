# Cover Letter — Journal of Chemical Information and Modeling

Cheongwoo Han
Independent Researcher
ORCID 0009-0004-4805-8815
crazat7@gmail.com

Date: [submission date]

To the Editors, *Journal of Chemical Information and Modeling*:

I am pleased to submit the manuscript **"Cross-Validation of Three Neural Network Potentials for MMP-1 Zn Active-Site Inhibitor Ranking: A Computationally-Driven Repositioning Study of Vorinostat and Indapamide"** for consideration as a research article.

**Scope and fit.** The work sits squarely within JCIM's computational-chemistry and cheminformatics scope. It develops and stress-tests a multi-engine reliability pipeline for protein–ligand structure prediction on a transition-metal target: (1) Boltz-2 protein–ligand co-folding over 25 reseed cycles × 100 diffusion samples; (2) GFN2-xTB single-point and tight-optimization energetic refinement in three solvent modes; and (3) a three-engine neural-network-potential consensus (Orb-v2, MACE-OMol25, Orb-v3-OMol25) over a stratified ChEMBL MMP-1 ligand set.

**Principal findings.**
- Cross-NNP ranking agreement reaches Pearson r = 0.9146 (1000-bootstrap 95% CI [0.817, 0.973]; leave-one-out r = 0.9146 ± 0.0115).
- An upstream GFN2-xTB OPT pre-relaxation collapses a conformational-energy outlier (CHEMBL94487) from σ = 14.27 to 0.007 kcal/mol — a 2,068-fold reduction — defining a generalizable mandatory-OPT-rescue workflow for NNP-scored ensembles.
- A PoseBusters v2 audit of the top-ranked co-folds yields a 94.5% mean physical-validity pass rate, exceeding the published Boltz-2 PDBBind benchmark (89.2%).
- Coverage-calibrated conformal intervals convert the per-ligand σ into a guaranteed-coverage reliability layer.
- The atomistic framework supports a falsifiable repositioning hypothesis: vorinostat and the sulfonamide-diuretic class (indapamide and 16 FDA-approved congeners) occupy the predictable-conformer regime against the MMP-1 catalytic Zn²⁺ pocket, a class for which ChEMBL contains no quantitative MMP-1 activity records.

**Novelty.** To our knowledge this is the first systematic per-ligand reliability characterization of Boltz-2 co-folding on a Zn²⁺ metalloprotease, the first demonstration of upstream xtb-OPT rescue of NNP energy outliers in this setting, and the first conformal-calibrated reliability layer applied to co-folding confidence.

**Scope limitation, stated plainly.** The study is computational. It generates a mechanistically grounded, experimentally testable repositioning hypothesis rather than experimental validation; the Limitations section delineates the wet-lab assays (fluorogenic MMP-1 inhibition, DSF) required to test it, framed as the explicit next step. I believe the methodological contributions (NNP cross-validation reliability, xtb-OPT rescue workflow, conformal layer) stand on their own merit independent of the repositioning application.

**Declarations.** This is a single-author manuscript. The work is in-silico and uses public ChEMBL/UniProt data; no human or animal subjects. Competing interests: the author is the founder of HAN PREDICT (Seoul), a medical-AI company whose research division (Genesis Medicine) develops computational drug-discovery methods related to this work; HAN PREDICT provided no funding and had no role in the study. There is no external funding. All data, code, and structures are openly deposited at Zenodo (CC-BY-4.0) under **DOI 10.5281/zenodo.20247828**. The manuscript is not under consideration elsewhere; that Zenodo record is the preprint of record.

Thank you for considering this submission.

Sincerely,
Cheongwoo Han
