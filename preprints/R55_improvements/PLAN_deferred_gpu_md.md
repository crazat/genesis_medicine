# PLAN — R55 deferred items (need GPU slot or MD; not compute-now)

The R55 compute-now items (#1a xtb numerical floor, #4 scoring rules, #3/#2-cheap descriptor→σ)
were executed (see r55_*.txt/.csv). The following need a dedicated GPU slot or MD and are
queued behind the running Boltz cascade.

## #1b — Boltz-2 σ_iptm numerical-floor arm (GPU)
Goal: separate algorithmic-seed variance from BF16/GPU numerical non-determinism in σ_iptm.
Evidence it matters: temp=0 LLM inference gives 80/1000 unique outputs purely from batch-size
reduction-order; BF16 vs FP32 swings accuracy std up to 9% (arXiv:2506.09501; Thinking Machines 2025-09).
Protocol:
1. Fixed input + fixed seed, run Boltz-2 cofold N≈10 times on ONE ligand at:
   - Arm A (numerical floor): vary batch size / GPU load, default BF16 — measure residual σ_iptm.
   - Arm B (algorithmic): `torch.use_deterministic_algorithms(True)` + `CUBLAS_WORKSPACE_CONFIG=:4096:8`,
     fixed batch=1, fixed GPU — measure residual σ_iptm.
2. σ²_total = σ²_algorithmic + σ²_numerical; report the partition.
Cost: ~10 single-ligand cofold runs ≈ minutes each → ~1 cofold-cycle equivalent. Run between
cascade decades (e.g., after v330) or on a fixed-seed mini-batch. Expected: confirms our
inter-cycle σ_iptm (already known <0.003 = infra-deterministic) is dominated by genuine
diffusion sampling, not BF16 noise — neutralizes the "σ is just FP noise" reviewer objection.

## #2 (heavy) — mechanistic metastability tiered test (GPU/MD)
Cheap screen (DONE compute-now): RotatableBonds/HBD/HBA vs σ_E correlation (ρ up to 0.61) — see
r55_descriptor_sigma. Heavy tiers, in cost order:
1. **AFsample2 MSA-column masking** on the 15 ligand complexes → cluster outputs; correlate
   #conformational-clusters with σ_iptm (hypothesis: high-σ ligands split into >1 basin). (Commun Biol 2025)
2. **PLACER** repeat-prediction per ligand → pose-cluster count; multimodal = genuine alternate
   binding mode vs unimodal = sampling jitter. (PMID 39386615; already in paper_B validator stack)
3. **Open-BPMD** (JCIM 2022/2024) on all 15 holo poses → PoseScore/PersScore metastability metric;
   correlate with σ_iptm/σ_E — likely the single best mechanistic figure (15 ligands feasible, ~hrs each).
4. **OneOPES / BioEmu** gold-standard free-energy landscape on the 2-3 highest-σ ligands only
   (basin count + populations; test σ ∝ basin entropy −Σpᵢln pᵢ). (JCTC 2024; Science 2025)
Anchor framing: Structure 2025 (PMID 41005302) — pLDDT conflates flexibility & uncertainty
*in the ligand-bound regime* → σ is the residual; this justifies the dynamics probe.

## #3 (full) — structure→σ Error-Model regressor (needs more ligands)
n=15 PoC done (HBD ρ=0.61 for σ_E). Full version: train RF/GBM Error Model (JCIM 2026-01
PMC12848971 recipe) on the 140-ligand SAR set (paper_A) or the CA 2nd-target extension; benchmark
vs distance-to-training baseline (proven weak, SRCC 0.06-0.39); SHAP/counterfactual on the
meta-model to attribute σ to substructures. Deploy as a pre-screening σ-threshold gate.
Blocked only by ligand count → couple with the CA platform extension (R54 #2).

## Status
- Compute-now (#1a, #4, #3-PoC/#2-cheap): DONE, outputs in this dir.
- #1b: queue 1 GPU mini-run after current cascade decade.
- #2-heavy / #3-full: GPU/MD + larger ligand set → schedule with CA extension.
