# Paper Factory Queue

- timestamp: `2026-05-06T12:46:57+09:00`
- manuscript_md_count: `20`
- manuscript_pdf_count: `19`
- principle: 논문 수를 늘리되, 같은 결과를 과장 반복하지 않는다. 각 paper는 독립 질문, 독립 figure set, 명확한 in silico limitation을 가져야 한다.

## Production Rule

1. 결과가 완료되면 먼저 `summary.json`/CSV를 검증한다.
2. 논문 후보는 `ready`, `near-ready`, `accumulating`, `awaiting more GPU`로 분류한다.
3. `ready` 후보는 원고 초안/figure/table을 만들고, `near-ready` 후보는 마지막 계산 완료 즉시 승격한다.
4. wet-lab claim, clinical claim, efficacy claim은 금지한다. 표현은 `in silico`, `candidate`, `prioritization`, `hypothesis`로 제한한다.

## Current Queue

| ID | Paper candidate | Status | Evidence now | Next action |
|---|---|---|---|---|
| P15 | Universal scaffold family across 14 skin targets | ready/v1.8 | PDF=yes; figures 1-10 integrated; batch2 5/5 | Submit/update preprint; keep only in-silico claims. |
| P16 | R16 topical chromanol lead paper | complete PDF+figures; 200ns complete | R16 cofold rows=18; 30ns matrix=18; TGFB1 60ns=6/6; pigment 60ns=3/3; anchor 100ns=3/3; anchor 200ns=3/3; figures=5; pose gate pass/review/fail=20/12/0 | Submission-ready as an in-silico preprint; next work is CRO/Markush/FTO package, not stronger efficacy or commercial claims. |
| P17 | R15 chromanol safety-first fragment triage | complete PDF+figures; prior-art caveat added | triage rows=38; 14-target cofold rows=14; top3 30ns=3/3; figures=4; pose gate pass/review/fail=20/12/0 | Submission-ready as a safety-first in-silico fragment triage; R15 parent exact PubChem hit keeps composition novelty/commercial claims blocked. |
| P18 | NPASS topical natural-product xTB atlas | accumulating | best candidate rows=80; 96conf ladder partially complete | Refresh ladder summary after each 96/120/144conf tier and select top candidates for Boltz-2 cofold. |
| P19 | Conformer-ladder sensitivity in xTB natural-product triage | accumulating | 12/24/36/48/72conf complete; 96conf running | Compare rank stability by conformer depth; write methodology/results note after 96conf full tier. |
| P20 | Skin PBPK + Potts-Guy permeability methodology | existing preprint; update candidate | preprint #14 exists; NPASS logKp proxy now feeds downstream ranking | Revise with NPASS atlas examples and current Recover topical formulation caveats. |
| P21 | Boltz-2/MD validation methodology and failure modes | existing preprint; update candidate | preprint #8 exists; extended MD drift caveats and chromanol PoseBusters gate now available (pose gate pass/review/fail=20/12/0) | Update with SREBP1 x R14_5 late drift, raw-pose clash review, MD relaxation, and ABFE limitations. |
| P22 | Korean herbal scaffold alignment and Tanimoto evidence | draft candidate | R14_5-ferulic acid 0.42; R12_23-EGCG 0.34; R12_4-EGCG 0.30 | Build herbal-alignment figures and write as translational perspective, not efficacy claim. |
| P23 | Pigmentation-target focused chromanol/pterocarpan paper | outline started | DCT/TYR R16 30ns matrix complete; pigment 60ns=3/3 | Expand outline into manuscript sections and add pigment-focused figures/tables. |
| P24 | Scar/fibrosis TGFB1/MMP1-focused topical lead paper | outline started | R16 TGFB1 top6 60ns complete; MMP1 R12_4/R14_5 extended 30ns strong | Expand outline into manuscript sections and CRO endpoint table. |
| P25 | Target evidence and modality-gated dermatology discovery map | ready for methods/results outline | target gate green/yellow/red=13/10/8; modality rows=31; novelty rows=112 | Write as systems-improvement paper: Open Targets evidence, modality fit, and compute queue gating. |
| P26 | Reproducible autonomous in-silico dermatology workflow | ready for methods update | provenance manifest=yes; wet-lab feedback schema=yes; auto planner/daemon active | Use as methodology paper/update: provenance hashes, wet-lab feedback loop, and queue decision protocol. |
| P27 | Synthesis-aware chromanol/natural-product candidate triage | ready for methods/results outline | synthesis/retrosynthesis gate rows=112; novelty rows=112 | Write as practical candidate-selection paper: availability, analog novelty, SA gate, and no-retrosynthesis caveat. |
| P28 | Active-learning and multi-fidelity autonomous queueing | ready for methods/results outline | active-learning rows=672; BO/action plan rows=112; provenance manifest=yes | Write as systems paper: surrogate acquisition, cost-aware fidelity ladder, and protected queue rules. |
| P29 | Topical formulation BO and IVRT/IVPT feedback workflow | ready for translational-methods outline | formulation BO rows=60; wet-lab schema=yes | Use for CRO-ready translational paper/RFQ appendix: IVRT, IVPT, retention, irritation, stability. |
| P30 | Pocket and structure-consensus calibration for DL cofolding | ready for methodology outline | pocket gate rows=31; structure consensus rows=32; pose gate pass/review/fail=20/12/0 | Write calibration/failure-mode paper around Boltz confidence, PoseBusters, MD, pocket plausibility, and missing cross-model consensus. |
| P31 | Free-energy validation plan for chromanol lead prioritization | ready for methodology outline | FE plan rows=32; RBFE readiness doc=yes | Write as staged validation paper/protocol: Boltz/MD triage to OpenFE RBFE/ABFE/CBFE without overclaiming. |
| P32 | Dermal regulatory safety and topical IVPT pre-gate | ready for translational-methods outline | dermal regulatory rows=112; formulation rows=60 | Use OECD TG497, ICH S10, and FDA IVPT framing for topical lead safety/translation paper. |
| P33 | Perturbation-biology gate for skin target validation | ready for systems-biology outline | perturbation target rows=32; wet-lab schema=yes | Write as virtual-cell/phenotype bridge: target evidence, cell context, and wet-lab endpoint linkage. |
| P34 | Hydration and residence-time follow-up for stable chromanol poses | ready for methodology outline | hydration/kinetics rows=32; structure consensus rows=32 | Write as MD limitation paper: RMSD stability is not kinetics; propose WaterKit/GIST/SMD follow-up. |
| P35 | Ultra-large active-learning screening roadmap for dermatology leads | ready for roadmap/methods outline | ultra-large roadmap rows=50; active-learning rows=672 | Use as scalable discovery systems paper: NPASS to ZINC/REAL/active docking without brute-force overreach. |
| P36 | Model validation, applicability domain, and uncertainty in autonomous triage | ready for methods/results outline | uncertainty rows=672; active-learning rows=672 | Write as rigorous ML validation paper: scaffold domain, activity-cliff risk, and conformal-style intervals. |
| P37 | Cell Painting phenomics bridge for dermatology candidate triage | ready for translational-methods outline | phenomics rows=752; wet-lab schema=yes | Use as phenotype-bridge paper/protocol: JUMP/CPJUMP-style morphology, disease-cell assay anchors, and no-MOA-claim caveat. |
| P38 | Developability and CMC pre-gate for topical chromanol/NPASS leads | ready for translational-methods outline | CMC rows=112; dermal regulatory rows=112; formulation rows=60 | Write as lead-de-risking paper: solubility, pH stability, excipient compatibility, solid-form, and scale-up risk. |
| P39 | Patent/FTO watchlist and claim-discipline workflow | ready for operations/IP outline | IP/FTO rows=752; local novelty rows=112 | Use as internal/commercial-translational methods note; keep legal/FTO conclusions pending manual review. |
| P40 | FAIR assay metadata and CRO feedback ingestion workflow | ready for reproducibility-methods outline | FAIR dictionary rows=33; wet-lab ingested rows=0 | Write as reproducibility/CRO handoff paper: ISA/BAO/RO-Crate-ready metadata and queue feedback rules. |
| P41 | Regulatory-grade AI/model governance registry for autonomous discovery | ready for governance-methods outline | model registry rows=8; provenance manifest=yes | Write as AI governance paper: context-of-use, model cards, risk tiers, validation status, and claim limits. |
| P42 | Cross-model structure consensus and negative-control readiness | ready for methods/results outline | structure consensus v1 rows=32; v2 rows=32; pose gate pass/review/fail=20/12/0 | Write as DL cofolding claim-discipline paper: Boltz/PoseBusters/MD/pocket/applicability-domain plus cross-model gaps. |
| P43 | Constrained generative chromanol analog design queue | complete PDF+figures | generative chromanol rows=330; R17 cofold rows=240/240; R17 top green-target 10ns=3/3; R17 top green-target 30ns=3/3; R17 top green-target 60ns=3/3; R17 next green-target 10ns=3/3; R17 next green-target 30ns=3/3; R17 next green-target 60ns=3/3; R17 expanded green-target 10ns=3/3; R17 expanded green-target 30ns=3/3; R17 expanded green-target 60ns=3/3; figures=4; PDF=yes; route enumeration rows=1082; photosafety v2 rows=1082 | Write as hit-to-lead expansion paper/protocol; keep expanded fluorinated candidates as in-silico, wet-lab-pending examples. |
| P44 | Route-enumerated synthesis planning for chromanol/NPASS leads | ready for translational-methods outline | route enumeration rows=1082; synthesis gate rows=112; CMC rows=112 | Use as synthesis-readiness paper/RFQ appendix; avoid lead expansion for route_review/route_hard candidates. |
| P45 | Skin cell-state anchored dermatology target validation | ready for systems-biology outline | skin cell-state rows=32; perturbation rows=32; phenomics rows=752 | Write as disease-cell endpoint paper: melanocyte/fibroblast/sebocyte/keratinocyte mapping and phenotype-first rules. |
| P46 | Photosafety and skin-sensitization preclinical assay package | ready for translational-safety outline | photosafety v2 rows=1082; dermal regulatory rows=112 | Write as topical-safety gate paper/RFQ appendix using OECD TG497 and ICH S10 caveats. |
| P47 | Design-make-test-learn experiment-card workflow | ready for CRO/wet-lab operations outline | DMTL cards=16; wet-lab ingested rows=0; FAIR dictionary rows=33 | Use as closed-loop operating paper: compute result to CRO assay card to wet-lab feedback ingestion. |
| P48 | Benchmark-grade decoy validation for DL cofolding | ready for validation-methods outline | structure benchmark rows=32; structure consensus v2 rows=32; pose gate pass/review/fail=20/12/0 | Build decoy/cross-model/PLIF protocol paper and keep binding claims caveated until benchmark controls exist. |
| P49 | Human skin spatial-atlas anchored target triage | ready for systems-biology outline | skin spatial rows=32; skin cell-state rows=32; target gate green/yellow/red=13/10/8 | Add site/cell/niche tables to target-focused papers and prioritize atlas anchors over docking-only ranking. |
| P50 | Target engagement and deconvolution assay readiness | ready for DMTL/CRO outline | target engagement rows=32; DMTL cards=16; target gate green/yellow/red=13/10/8 | Write CETSA/TPP/SPR/reporter readiness table and separate direct engagement from phenotype-only claims. |
| P51 | Dermal PBPK and finite-dose IVRT/IVPT workflow | ready for translational-methods outline | dermal PBPK rows=1082; dermal regulatory rows=112; formulation rows=60 | Build finite-dose IVRT/IVPT/PBPK parameter table and CRO RFQ appendix before stronger topical exposure claims. |
| P52 | Genetic causality and direction-of-effect target validation | ready for evidence-methods outline | genetic causality rows=31; target gate green/yellow/red=13/10/8 | Use Open Targets Genetics/MR/pQTL/eQTL or phenotype evidence caveats before direction-of-effect claims. |
| P53 | Metabolism and reactive-metabolite risk gate | ready for safety-methods outline | metabolite risk rows=1082; photosafety v2 rows=1082; quinone safety rows=1006 | Write BioTransformer/FAME-style follow-up plan and block safety-positive language for reactive-alert candidates. |
| P54 | Pharmacovigilance signal and class-safety caveat workflow | ready for safety-surveillance outline | pharmacovigilance rows=442; model registry rows=8 | Draft AEMS/FAERS/literature-signal workflow and state explicitly that signal is not causation. |
| P55 | Single-cell foundation-model reliability for virtual-cell claims | ready for ML-reliability outline | single-cell FM rows=32; perturbation rows=32; phenomics rows=752 | Write zero-shot reliability and simple-baseline control paper before using foundation-model claims as primary evidence. |
| P56 | Quinone reactivity and sensitization gate for EMB-3-class leads | ready for safety-methods outline | quinone safety rows=1006; photosafety v2 rows=1082; metabolite risk rows=1082 | Write as EMB-3/Embelin-class safety caveat paper or appendix: GSH/NAC trapping, DPRA/KeratinoSens/h-CLAT, ROS/redox cycling, ICH S10 photostability, and skin S9 metabolism before safety-positive claims. |
| P57 | World-class gap-closure master gate for autonomous discovery | ready for systems/operations paper | master rows=2328; readiness counts={'cheap_compute_or_paper_with_fto_caveat': 378, 'triage_accumulating': 1193, 'hold_or_benchmark_only': 757}; heavy-compute counts={'short_triage_only': 378, 'cheap_compute_only': 1193, 'hold': 757} | Use as the top-level decision layer tying prior-art/FTO, structure consensus, FE, synthesis, dermal translation, phenotype biology, uncertainty, and governance into one queue policy. |
| P58 | Creative-discovery gap matrix and active-learning fallback | ready for systems/creative-discovery paper | creative gap rows=10; active-learning candidates=672; active cofold manifests=496; completed short-cofold rows=480; pending short-cofold pairs=160; runnable short-cofold pairs=0; blocked missing-MSA pairs=160; missing target A3M=14 | Write as the creative-discovery operating paper: synthesis-native generation, scaffold hopping, target MSA cache, cryptic-pocket, phenomics-first objective, and GPU fallback rules. |

## Immediate Writing Priority

1. P16/P17: R16 topical chromanol lead paper와 R15 safety-first triage paper는 PDF+figures 완료 상태로 유지한다; 다음은 submit/CRO/FTO 패키지다.
2. P43: R17 constrained generative chromanol analog paper는 expanded green-target 60 ns 3/3 완료로 PDF+figures complete 상태다; 다음은 Markush/FTO, cross-model/decoy/PLIF, wet-lab/formulation 패키지다.
3. P18/P19: NPASS xTB atlas/methodology pair. 96conf tier 완료 후 자동 승격한다.
4. P24: scar/fibrosis TGFB1/MMP1 focused paper. CRO RFQ와 직접 연결되는 translational paper로 쓴다.
5. P25/P26: target evidence gate와 provenance/wet-lab feedback schema는 기존 논문들의 방법론 보강 또는 독립 systems paper로 분리 가능하다.
6. P27/P28: synthesis gate와 active-learning/multi-fidelity planner는 계산 큐가 왜 특정 후보를 고르는지 설명하는 독립 방법론 논문으로 바로 작성 가능하다.
7. P29/P30: formulation BO와 structure consensus calibration은 wet-lab/CRO 연결성과 DL cofolding 한계를 보강하는 별도 논문 후보로 유지한다.
8. P31/P32: free-energy validation과 dermal regulatory safety gate는 R16/R15 lead claim의 가장 중요한 보강 축이다.
9. P33-P36: perturbation biology, hydration/kinetics, ultra-large roadmap, ML uncertainty는 글로벌 SOTA 대비 부족한 부분을 메우는 methodology paper 후보로 유지한다.
10. P37-P41: phenomics, CMC, IP/FTO, FAIR assay ingestion, model governance는 compute-only 시스템을 translational operating system으로 확장하는 논문 후보로 유지한다.
11. P42-P47: cross-model consensus, generative chromanol design, route enumeration, skin cell-state, photosafety, DMTL card는 글로벌 SOTA gap-closure 논문 후보로 유지한다.
12. P48-P56: decoy benchmark, spatial atlas, target engagement, dermal PBPK/IVPT, genetic causality, metabolite risk, pharmacovigilance, single-cell FM reliability, quinone safety는 최신 translational SOTA gap-closure 논문 후보로 유지한다.
13. P57: world-class gap-closure master gate는 모든 gate를 하나로 묶는 운영/방법론 paper로 유지하고, 새 GPU/FE/합성 승격 판단의 최상위 근거로 쓴다.
14. P58: creative-discovery gap matrix는 chromanol 주변 최적화에서 벗어나 synthesis-native, scaffold-hop, phenomics-first, cryptic-pocket, target-cache-aware discovery로 확장하는 독립 시스템 논문 후보로 쓴다.

## Compute-to-Paper Decision Logic

- target evidence gate `green` + stable MD/cofold + plausible safety -> compute expansion and target-focused paper 후보.
- synthesis gate `green` + novelty `novel_or_distinct` + active-learning acquisition high -> Boltz-2 또는 MD 후속 후보.
- multi-fidelity BO plan이 `single-point wet-lab`을 추천하면 더 큰 GPU 확장보다 assay/IVRT/IVPT 설계를 우선 고려한다.
- structure consensus `high_confidence`는 main table 후보, `usable_with_caveat`는 보조 표 또는 limitation 후보로 둔다.
- pocket gate가 `hard_or_indirect`인 target은 direct binding claim을 피하고 phenotype/network claim으로 낮춘다.
- formulation BO rows가 생기면 CRO RFQ appendix와 P29 manuscript table에 동시에 반영한다.
- free-energy validation plan이 `RBFE_network`를 추천해도 GPU가 이미 MD에 쓰이면 production FE는 보류하고 protocol/edge plan만 갱신한다.
- dermal regulatory gate `red` 후보는 topical lead claim에서 제외하고, `yellow`는 OECD TG497/ICH S10/FDA IVPT caveat를 붙인다.
- perturbation biology `high` target은 phenotype/LINCS/Geneformer/scGPT 연결 후보로 올리고, `low` target은 direct biology claim을 피한다.
- hydration/kinetics gate의 residence proxy 후보는 60-100 ns 안정성 이후에만 SMD/tauRAMD-style follow-up으로 올린다.
- ultra-large roadmap stage1 이상은 외부 library/storage/license 확인 전에는 실제 download/docking을 큐잉하지 않는다.
- model uncertainty `activity_cliff_risk` 또는 `novel_scaffold`는 direct Boltz/pose/MD 없이 paper main table에 올리지 않는다.
- phenomics gate `priority_cell_painting`은 더 큰 GPU 반복보다 disease-cell phenotype/Cell Painting assay 설계를 우선 고려한다.
- CMC gate `yellow/red` 후보는 lead claim보다 solubility, pH stability, excipient compatibility, solid-form risk 보강으로 돌린다.
- IP/FTO watchlist `high_review` 후보는 patent/FTO 수동 검토 전까지 novelty/commercial claim을 금지한다.
- FAIR assay schema 필수 metadata가 없는 wet-lab row는 논문 main evidence가 아니라 QC 보류로 둔다.
- model governance `tier2` component가 main claim에 영향을 주면 orthogonal check 또는 explicit limitation을 붙인다.
- structure consensus v2 `needs_cross_model`은 Chai-1/DiffDock/Vina/PLIF/negative-control 중 하나 이상을 먼저 요구한다.
- chromanol generative optimizer `Boltz-2_next_when_GPU_free`는 현재 GPU MD가 끝난 뒤 non-duplicate 후보만 큐잉한다.
- route enumeration `route_review/route_hard`는 synthesis route 확인 전 lead expansion에서 제외한다.
- skin cell-state `phenotype_first`는 추가 docking보다 cell assay endpoint 설계를 우선한다.
- photosafety v2 `yellow`는 OECD TG497/ICH S10 assay package를 같이 붙이고, `red`는 topical lead claim에서 제외한다.
- quinone safety `quinone_reactivity_review`는 GSH/NAC trapping, DPRA/KeratinoSens/h-CLAT, ROS/redox cycling, ICH S10 photostability, skin S9 metabolism 전까지 EMB-3/quinone safety-positive claim을 금지한다.
- DMTL `single_point_wetlab_card`는 추가 GPU 반복보다 CRO/wet-lab quote/assay ordering 후보로 승격한다.
- structure benchmark `benchmark_decoys_required_before_strong_claim`은 cross-model/decoy/PLIF control 전까지 direct binding strong claim을 금지한다.
- skin spatial atlas `spatially_anchorable`은 site/cell/niche table을 target paper main evidence로 올리고, `atlas_review`는 docking보다 atlas/literature 확인을 우선한다.
- target engagement `engagement_assay_ready`는 DMTL/wet-lab card로 승격하고, `deconvolution_first`는 direct target engagement claim을 보류한다.
- dermal PBPK/IVPT `ivpt_pbpk_ready`는 finite-dose IVRT/IVPT/PBPK table 후보로 올리고, `formulation_rescue_needed`는 추가 docking보다 formulation BO를 우선한다.
- genetic causality `direction_needs_genetic_or_phenotype_support`는 Open Targets Genetics/MR/pQTL/eQTL 또는 phenotype evidence 없이는 direction-of-effect claim을 금지한다.
- metabolite risk `reactive_metabolite_review`는 BioTransformer/FAME-style follow-up 전까지 safety-positive language를 금지한다.
- pharmacovigilance `pv_signal_review`는 AEMS/FAERS/literature signal check 전까지 class-safety claim을 제한한다.
- single-cell FM `zero_shot_reliability_review`는 simple baseline/fine-tuning/cell-type proximity control 없이는 virtual-cell 결과를 보조 evidence로만 둔다.
- world-class master gate `hold_or_benchmark_only` 또는 `heavy_compute_permission=hold`는 신규 long-MD/FE/합성/상업 claim을 차단한다.
- world-class master gate `wetlab_translation_priority`는 더 큰 GPU 반복보다 CRO/DMTL/IVRT/IVPT/Cell Painting package를 우선한다.
- creative discovery matrix의 `target_msa_coverage` gap은 target-specific cofold를 차단한다. MC1R처럼 target-key A3M이 없으면 cache 준비가 먼저다.
- active-learning short cofold 결과는 GPU 유휴 방지용 triage다. 완료 row는 master gate에 들어가지만 long-MD/FE/lead claim은 synthesis/prior-art/safety/phenomics/uncertainty gate 이후다.
- 새 scaffold 또는 scaffold-hop queue는 synthesis-native generation, novelty/diversity guard, decoy/benchmark guard 없이 paper main lead로 올리지 않는다.
- target evidence gate `yellow` -> phenotype/cell/wet-lab endpoint가 같이 있어야 manuscript claim에 포함한다.
- target evidence gate `red` -> negative-control, limitation, future-work로만 사용한다.
- GPU MD stable + cofold affinity meaningful + ADMET/skin-window plausible -> target-focused paper 후보.
- 대량 CPU screen만 있고 target cofold가 없으면 atlas/methodology paper 후보로 유지한다.
- drift 또는 toxicity caveat가 있으면 failure-mode/methodology paper로 전환한다.
- 같은 molecule/target 결과라도 universal-scaffold paper, topical-lead paper, methodology paper의 질문이 다르면 분리 가능하다.
