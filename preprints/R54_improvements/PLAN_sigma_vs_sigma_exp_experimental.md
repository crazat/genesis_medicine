# PLAN — σ-vs-σ_exp experimental validation (R54 #3, first-in-class whitespace)

Claim to establish: **"compounds that are hard to PREDICT (high computational σ_E / σ_iptm) are
also hard to MEASURE (high experimental replicate variance)."** No published study links
computational prediction variance to per-compound experimental measurement variance — genuine
first-in-class whitespace.

## Literature scaffold (cite to frame the gap)
- Experimental floor (the y-axis reference): cross-source pKi/IC50 noise MAE≈0.78 / RMSE≈1.04 log
  (Landrum & Riniker, *JCIM* 2024, 4c00049); independent-ITC RMSE ≈ 0.9 kcal·mol⁻¹; MST 34-lab
  benchmark Kd RSD ≈ 20 % (López-Méndez et al., *Eur. Biophys. J.* 2021) — the aleatoric measurement floor.
- Model-UQ side never linked to assay variance: *Sci Rep* 2024 (PMC10950896) finds no rank
  correlation between predicted uncertainty and actual error and explicitly does NOT examine assay
  reproducibility; Wan/Coveney (arXiv:2603.05532) tests self-reproducibility only.

## Experimental design
- **Compound selection = σ-STRATIFIED** (low / mid / high σ bins from our conformal + σ ranking),
  NOT pure top-uncertainty — so the experiment samples the full correlation range. Use the
  conformal `half_width` ranking (paper_B `conformal_sigma_iptm_paperB.csv`) + σ_E cells.
- **Primary method = MST** (NanoTemper Monolith): solution-phase (Zn-safe, no immobilization to
  perturb the catalytic Zn), tolerates divalent-cation buffers, gives per-titration fit error =
  per-compound σ_exp. Run each compound in triplicate; reference line = 20 % Kd RSD floor.
- **Mechanistic adjunct = native MS**: simultaneously reports Zn occupancy + ligand binding →
  test whether high-σ_E compounds are those showing mixed Zn-on/Zn-off populations (a direct
  mechanistic explanation for computational variance).
- **Thermodynamic anchor = ITC** on 3–5 compounds to set the absolute scale (caveat: sulfonamide
  aggregation can bias ITC Kd).
- **Analysis = 2D scatter**: x = computational σ (σ_E and σ_iptm), y = experimental replicate σ
  from MST; test for positive correlation; the 20 % RSD line is the measurement-noise floor.

## Korea-accessible routing
- **KBSI (한국기초과학지원연구원)** fee-for-service 분석지원: confirmed ITC + SPR + MALS + CD
  (537 instruments). File application for ITC (anchors) + SPR (kinetic confirmation); ask directly
  whether MST/nanoDSF/native-MS are on the menu.
- **University biophysics cores** (SNU/KAIST/POSTECH) for MST (Monolith) / nanoDSF (Prometheus) —
  reach via the KMCRIC / 이향숙 lab and Han Cheong Woo (Busan Nat'l) network for warm intro + academic rate.
- **MMP-1 (and CA) protein/kit** procurement via BTB Korea (BPS Bioscience distributor).
- Cloud-lab note: Strateos public subscription ended; use Emerald Cloud Lab or Amazon Bio
  Discovery (lab-in-the-loop, Apr 2026) if remote execution is wanted.

## Status
- Analysis scaffold (σ-stratified compound list + 2D-scatter framework) is READY from existing
  conformal/σ outputs — can be generated now on the computational side.
- Wet-lab steps are future (require funding + CRO/core engagement); this plan is the protocol +
  outreach package. Pairs naturally with the CA target (more public affinity data → easier validation).
