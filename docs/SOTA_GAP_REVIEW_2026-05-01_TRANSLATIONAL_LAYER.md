# SOTA Gap Review 2026-05-01: Translational Layer Perspective

timestamp: `2026-05-01T14:39:17+09:00`

## Current Compute Snapshot

- GPU: R16 chromanol anchor triad 100 ns is active. `TGFB1` and `DCT` are complete at 100 ns, `TYR` is running.
- CPU: protected NPASS queues and two xTB 120conf ladders are active. CPU idle is low, so no additional heavy CPU queue is recommended now.
- No duplicate GPU/CPU job should be launched from this review.

## High-Level Verdict

Genesis_Medicine is now strong in autonomous queueing, Boltz-2 cofolding, OpenMM MD follow-up, xTB conformer refinement, ADMET/skin-window triage, paper factory generation, provenance, model governance, route/safety gates, and DMTL carding.

The remaining gap versus global SOTA is no longer simply "more docking". The larger gaps are:

1. benchmark-grade structure validation and decoy enrichment,
2. disease-site-specific human skin atlas anchoring,
3. target engagement and target deconvolution planning,
4. mechanistic dermal exposure and IVRT/IVPT/PBPK linkage,
5. target causality and direction-of-effect genetics,
6. metabolite/reactive-metabolite risk,
7. executable synthesis planning with route cost/stock/condition feasibility,
8. pharmacovigilance and real-world safety signal monitoring,
9. cautious use of single-cell foundation models with zero-shot reliability caveats.

## Priority Gap 1: Benchmark-Grade Structure Validation

Evidence:
- PoseBench reports that DL cofolding often outperforms classical docking but remains challenged by new protein-ligand poses, multiligand targets, MSA sensitivity, and chemical specificity.
- Boltz-2 improves affinity prediction, but independent use still needs cross-model/physics/negative-control checks before strong claims.

Current system status:
- `STRUCTURE_CONSENSUS_V2` already combines Boltz, PoseBusters, MD, pocket plausibility, and applicability-domain rules.
- Actual cross-model execution with Chai-1/DiffDock/Vina/PLIF and target-specific decoys is not yet implemented.

Recommended improvement:
- Add `structure_benchmark_decoy_gate`:
  - known active or literature ligand if available,
  - matched property decoys,
  - scrambled target or irrelevant target negative control,
  - PLIF overlap score,
  - enrichment proxy: candidate should beat decoys by Boltz affinity and/or pose-confidence margin.

Paper value:
- Extend P42 into a benchmark-oriented paper rather than only a claim-discipline paper.

## Priority Gap 2: Disease-Site-Specific Skin Atlas Anchoring

Evidence:
- A 2026 Nature Genetics skin atlas resolves about 1.2 million cells, 45 cell types, 114 samples, and 15 anatomic sites, showing multicellular neighborhoods and disease-associated disruption.
- Skin location matters: follicle density, pH, lipid composition, moisture, immune-stromal niches, and disease vulnerability vary by site.

Current system status:
- `SKIN_CELL_STATE_EVIDENCE_GATE` maps targets to broad skin cell states.
- It does not yet distinguish scalp/face/trunk/follicular/sebaceous/perivascular/melanocyte niche contexts.

Recommended improvement:
- Add `skin_spatial_atlas_gate`:
  - target expression by skin cell type,
  - indication-specific anatomical site,
  - disease niche class such as follicular, sebaceous, melanocyte, fibroblast, perivascular immune-stromal,
  - assay implication: keratinocyte, melanocyte, fibroblast, sebocyte, hair follicle organoid, or reconstructed skin model.

Paper value:
- Strengthen P45 and disease-specific chromanol papers by showing why a target belongs to a specific skin compartment.

## Priority Gap 3: Target Engagement and Deconvolution

Evidence:
- TPP/CETSA-style proteome profiling can identify direct and indirect drug targets in living cells by drug-induced protein thermal stability changes.
- This matters especially for natural products and phenotypic hits, where a docking target may be hypothesis-only.

Current system status:
- DMTL cards exist, but target-engagement assay planning is not a first-class gate.
- Current wet-lab cards emphasize endpoint design more than direct target engagement.

Recommended improvement:
- Add `target_engagement_assay_gate`:
  - direct biochemical assay available: yes/no,
  - cellular target engagement option: CETSA, nanoBRET, SPR/ITC, TPP/MS,
  - target-deconvolution path for phenotypic hits,
  - assay material readiness: recombinant protein, antibody, cell line, tissue model.

Paper value:
- New paper candidate: target-engagement-ready dermatology in-silico triage, or merge into P47 DMTL.

## Priority Gap 4: Dermal Exposure, IVRT/IVPT, and PBPK

Evidence:
- FDA IVPT guidance frames topical products as complex products and recommends IVPT comparisons for topical bioequivalence.
- EMA topical product guidance explicitly includes quality, equivalence testing, skin permeation, in vitro release, stratum corneum sampling, and tape stripping.

Current system status:
- `TOPICAL_FORMULATION_BO` exists.
- `DERMAL_REGULATORY_SAFETY_GATE` exists.
- A mechanistic dermal PBPK/finite-dose IVPT bridge is still thin.

Recommended improvement:
- Add `dermal_pbpk_ivpt_gate`:
  - finite-dose IVPT readiness,
  - donor skin number assumptions,
  - receptor medium compatibility,
  - skin retention vs permeation objective,
  - Q3/formulation sameness or difference,
  - Potts-Guy/logKp and stratum-corneum binding caveat,
  - PBPK input completeness.

Paper value:
- Strengthen P29/P32 and make topical lead claims more defensible.

## Priority Gap 5: Target Causality and Direction-of-Effect Genetics

Evidence:
- Open Targets integrates clinical precedence, GWAS, fine-mapping, colocalization, Locus-to-Gene, gene burden, ClinVar, and direction-of-effect concepts.
- Modern target validation increasingly asks whether activating or inhibiting a target is directionally consistent with disease benefit and safety.

Current system status:
- `TARGET_EVIDENCE_GATE` exists.
- It does not yet fully encode target direction-of-effect, pQTL/eQTL colocalization, MR-style caveats, or PheWAS adverse-trait flags.

Recommended improvement:
- Add `genetic_causality_direction_gate`:
  - Open Targets overall association,
  - genetic evidence type,
  - direction of target modulation,
  - disease trait direction,
  - safety trait warnings,
  - "direction unknown" limitation when evidence is not causal.

Paper value:
- Strengthen P25 and all target-focused manuscripts by reducing target-biology overclaim.

## Priority Gap 6: Metabolism and Reactive-Metabolite Risk

Evidence:
- BioTransformer 3.0 predicts human, gut, and environmental biotransformations and supports multi-step human biotransformation sequences.
- It reports enzyme/reaction provenance and can be used programmatically or as command-line software.

Current system status:
- ADMET, photosafety, and sensitization gates exist.
- Metabolite generation, phenolic oxidation, quinone-like risk, sulfate/glucuronide products, and reactive metabolite flags are not yet explicit.

Recommended improvement:
- Add `metabolite_reactive_risk_gate`:
  - predicted Phase I/II metabolites,
  - phenol/catechol/quinone-imine-like alerts,
  - skin metabolism caveat,
  - reactive metabolite or sensitization-linked metabolite warning,
  - metabolite SMILES exported for downstream ADMET and docking only as exploratory.

Paper value:
- Strengthen P46 and topical chromanol safety narratives.

## Priority Gap 7: Executable CASP, Not Just Route Heuristics

Evidence:
- AiZynthFinder 4.0 adds filter policies, multiple expansion models, scoring, route clustering, and improved industrial-use features.
- The paper reports broad use across hundreds of thousands of molecules and highlights stock, route shape, and reaction-space analysis.

Current system status:
- `ROUTE_ENUMERATION_GATE` and `SYNTHESIS_RETROSYNTHESIS_GATE` are heuristic.
- They do not yet run a CASP engine with purchasable stock, route cost, step count, route confidence, condition prediction, or route clustering.

Recommended improvement:
- Add CASP readiness phase:
  - keep current heuristic as tier 0,
  - run AiZynthFinder or ASKCOS only on `route_ready` top candidates,
  - record route count, shortest route, stock availability, route cost proxy, risky transformations,
  - avoid TensorFlow multiprocessing fork issues by isolating CASP in a separate non-fork script or ONNX-backed path.

Paper value:
- P44 becomes much stronger if it contains executable route evidence.

## Priority Gap 8: Pharmacovigilance and Real-World Safety Signal Layer

Evidence:
- FDA AEMS, formerly FAERS, consolidates adverse-event reporting and supports post-marketing safety surveillance for drugs and therapeutic biologics.
- FDA states AEMS is designed to improve data quality, standardization, analytics, and cross-product surveillance.

Current system status:
- IP/FTO, ADMET, dermal safety, and model governance exist.
- There is no FAERS/AEMS or analog-class adverse-event signal layer.

Recommended improvement:
- Add `pharmacovigilance_signal_gate`:
  - query known drugs or close analog classes,
  - extract MedDRA terms relevant to dermatology, cardiotoxicity, hepatotoxicity, photosensitivity, hypersensitivity,
  - use only as signal, not causation,
  - flag candidate classes needing safety-caveat wording.

Paper value:
- Strengthen P41/P46 and systemic-vs-topical path separation.

## Priority Gap 9: Single-Cell Foundation Models Need Reliability Controls

Evidence:
- scGPT demonstrates broad single-cell tasks including cell type annotation, multi-omic integration, perturbation response, and gene network inference.
- A Genome Biology zero-shot evaluation reports that scGPT/Geneformer can be outperformed by simpler methods in some zero-shot settings, emphasizing reliability checks.

Current system status:
- `PERTURBATION_BIOLOGY_GATE` and `PHENOMICS_SIGNATURE_GATE` exist.
- They correctly treat virtual-cell style evidence as hypothesis, but do not yet score zero-shot reliability or dataset proximity.

Recommended improvement:
- Add `single_cell_fm_reliability_gate`:
  - model used,
  - cell type match,
  - disease context match,
  - fine-tuning availability,
  - zero-shot only warning,
  - simpler-baseline comparison requirement.

Paper value:
- Strengthen P33/P37/P45 with honest SOTA nuance.

## Implementation Priority

Immediate lightweight scripts, no heavy compute:

1. `write_skin_spatial_atlas_gate.py`
2. `write_target_engagement_assay_gate.py`
3. `write_dermal_pbpk_ivpt_gate.py`
4. `write_metabolite_reactive_risk_gate.py`
5. `write_genetic_causality_direction_gate.py`
6. `write_pharmacovigilance_signal_gate.py`
7. `write_single_cell_fm_reliability_gate.py`
8. `write_structure_benchmark_decoy_gate.py`

Near-term heavier integration:

1. CASP engine integration for only top `route_ready` candidates.
2. Cross-model cofold/docking execution for only structure-consensus `needs_cross_model` rows.
3. IVRT/IVPT/PBPK parameter table for CRO RFQ.

## Sources

- PoseBench, Nature Machine Intelligence: https://www.nature.com/articles/s42256-025-01160-1
- Boltz-2 record and DOI: https://pubmed.ncbi.nlm.nih.gov/40667369/
- Boltz-2 project page: https://boltz.bio/boltz2
- FDA IVPT guidance: https://www.fda.gov/regulatory-information/search-fda-guidance-documents/in-vitro-permeation-test-studies-topical-drug-products-submitted-andas
- EMA topical product guidance: https://www.ema.europa.eu/en/quality-equivalence-locally-applied-locally-acting-cutaneous-products-scientific-guideline
- Open Targets evidence documentation: https://platform-docs.opentargets.org/evidence
- scGPT, Nature Methods: https://www.nature.com/articles/s41592-024-02201-0
- Single-cell FM zero-shot limitations, Genome Biology: https://genomebiology.biomedcentral.com/articles/10.1186/s13059-025-03574-x
- TPP protocol, Nature Protocols: https://www.nature.com/articles/nprot.2015.101
- AiZynthFinder 4.0, Journal of Cheminformatics: https://jcheminf.biomedcentral.com/articles/10.1186/s13321-024-00860-x
- BioTransformer 3.0, Nucleic Acids Research: https://academic.oup.com/nar/article/50/W1/W115/6583239
- OECD TG439 reconstructed human epidermis skin irritation: https://www.oecd.org/en/publications/test-no-439-in-vitro-skin-irritation-reconstructed-human-epidermis-test-method_9789264242845-en.html
- Human skin spatial atlas, Nature Genetics: https://www.nature.com/articles/s41588-026-02552-8
- TxGNN, Nature Medicine: https://www.nature.com/articles/s41591-024-03233-x
- FDA AEMS/FAERS: https://www.fda.gov/drugs/surveillance/fdas-adverse-event-reporting-system-faers
