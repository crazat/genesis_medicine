# PLAN — Carbonic anhydrase as 2nd target → platform paper (R54 #2)

Goal: convert two single-target (MMP-1) reliability papers into ONE transferable dual-modality
reliability PLATFORM by re-running the identical protocol on a 2nd Zn-metalloenzyme — carbonic
anhydrase (CA) — which shares the sulfamoyl zinc-binding-group chemistry of our diuretics and has
far more public affinity data.

## Why CA is the ideal 2nd target
- Sulfamoyl (–SO₂NH₂) is the canonical CA zinc-binding group; sulfonamide diuretics (indapamide,
  etc.) are established sub-nM CA inhibitors (Supuran lineage; indapamide–CA II crystal exists).
- Abundant high-quality Ki/IC50 data (CA I/II/IX/XII) for calibration — orders of magnitude more
  than MMP-1 — so the σ-vs-experiment story (R54 #3) is far easier on CA.
- Live 2025 venue/conversation: "Hidden CA targets in dermatology: 23 dermatology drugs vs human
  CA I/II" (*J Enzyme Inhib Med Chem* 2025, 10.1080/14756366.2025.2540935) → CA-generalization
  paper home = JEIMC.
- CA II vs IX/XII isoform selectivity is an open, crystallography-rich problem (ChemRxiv
  2025-sh383) → σ_iptm-across-isoforms can be pitched as a selectivity-confidence tool.

## Execution checklist
1. **[CPU, ready now]** Assemble ligand set: the same sulfonamide diuretic panel + a CA-reference
   set (acetazolamide, dorzolamide, etc.) with public Ki for CA I/II/IX/XII from ChEMBL.
2. **[GPU — BLOCKED by video pause]** Boltz-2 cofold of the ligand set against CA isoform
   structures (CA II 1CA2/3KS3-class; CA IX, CA XII), N reseed cycles → σ_iptm per ligand×isoform.
   *Cannot run while GPU is reserved for video; queue behind the paused v311–v320 cascade.*
3. **[CPU, ready after step 2 SDFs exist]** Reuse pdb_to_sdf + the sept-matrix xtb templates on the
   CA-bound ligand poses → σ_E. Identical pipeline to MMP-1; only SDF_DIR/tag change (sed clone).
4. **[CPU, ready]** Apply the conformal layer + multiverse/G-theory + σ_iptm-static analyses
   (all three R54 scripts are target-agnostic — point them at the CA cohort).
5. Cross-target claim: show the dual-modality reliability protocol (σ_E ⟂ σ_iptm) transfers
   MMP-1 → CA with consistent behaviour = platform, not one-off.

## Status
- Steps 1, 3–5 are CPU-only and reuse existing code with a sed clone (like the v136_v155 floor).
- Step 2 needs GPU → **deferred until the user releases the GPU** (currently paused for video).
- Recommended sequence once GPU free: finish v311–v320 Boltz cascade (paper_B widening), then a
  short CA cofold cascade.

## IP / framing guardrail
Keep the contribution framed as method + repositioning EVIDENCE, not a composition-of-matter or
sulfonamide-for-skin use claim (pre-existing cosmetic sulfamide IP, e.g. L'Oréal US 8,293,256).
FTO on reliability-as-method appears open; preprint + Zenodo DOI is sufficient defensive publication.
