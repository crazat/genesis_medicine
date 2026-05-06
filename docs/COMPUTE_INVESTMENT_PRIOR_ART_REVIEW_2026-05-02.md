# Compute Investment And Prior-Art Review

- timestamp: `2026-05-02T18:05:00+09:00`
- scope: currently queued and completed Genesis_Medicine compute programs
- purpose: decide whether each topic is original enough, scientifically valuable enough, and commercially differentiated enough to justify continued CPU/GPU spend
- caveat: this is technical triage, not legal freedom-to-operate opinion

## Current Queue Status

| resource | current state | decision |
|---|---|---|
| GPU | active: `scripts/run_r17_chromanol_generative_expanded_green_60ns.py`; last observed GPU util about 65%; 2/3 expanded R17 60 ns jobs complete | let current 3rd 60 ns job finish; do not launch new chromanol 100/200 ns or RBFE/ABFE until prior-art/Markush checkpoint |
| CPU | active: protected NPASS conformer queue `PID 15578` plus xTB NPASS refinement tiers `top3000/top7000/top9000` | continue cheap CPU atlas/refinement; downrank public exact-hit molecules to benchmark-only |
| curator/planner | `auto_queue_cpu_gpu_daemon.sh` active; deterministic planner points to R17 expanded 60 ns and next xTB tier | keep daemon, but expensive follow-up must respect `PRECOMPUTE_PRIOR_ART_GATE.md` |

## Core Design Coverage

The following core layers are now present in the system and are referenced by `docs/CODEX_CURATOR_LOOP_PROMPT.md`:

| layer | implemented artifact | current meaning |
|---|---|---|
| prior-art/FTO pre-gate | `scripts/write_precompute_prior_art_gate.py`, `docs/PRECOMPUTE_PRIOR_ART_GATE.md`, `pilot/cpu_meaningful/precompute_prior_art_gate.csv` | blocks new expensive compute when public exact hits or Markush risk are detected |
| IP watchlist | `docs/IP_FTO_WATCHLIST.md` | blocks novelty/commercial claims before patent-family and legal-status review |
| target evidence | `docs/TARGET_EVIDENCE_GATE.md`, `docs/POCKET_EVIDENCE_GATE.md` | separates direct-binding narrative from phenotype/network hypothesis |
| structure discipline | `docs/STRUCTURE_CONSENSUS_V2.md`, `docs/STRUCTURE_BENCHMARK_DECOY_GATE.md`, chromanol pose sanity outputs | keeps Boltz/MD claims as in-silico evidence, not confirmed binding |
| safety/developability | quinone, photosafety, metabolite, dermal regulatory, CMC gates | blocks safety-positive claims for quinone/reactive/phototoxic/sensitization risk candidates |
| formulation/translation | dermal PBPK/IVPT, formulation BO, DMTL cards, FAIR assay schema | converts compute leads into CRO/wet-lab endpoint packages |
| paper factory | `docs/PAPER_FACTORY_QUEUE.md` | separates finished/near-ready/accumulating papers while avoiding duplicated claims |
| governance/provenance | model registry, run provenance, wet-lab ingestion schema | makes later submission/CRO handoff auditable |

Missing or deliberately not automated: professional CAS MARPAT/STNext, Derwent/DWPI, paid chemistry patent systems, and attorney claim charts. The system now demands them before commercial novelty/FTO claims, but it cannot replace them.

## Prior-Art Gate Summary

Current `precompute_prior_art_gate.csv` has `1322` rows.

| gate | count | compute implication |
|---|---:|---|
| `cheap_compute_allowed_prior_art_pending` | 725 | descriptor/xTB/short triage can continue; no strong novelty claim yet |
| `hold_expensive_compute_until_markush_review` | 579 | no new 60-200 ns MD, RBFE/ABFE, synthesis/purchase, or commercial claim before Markush/claim review |
| `hold_expensive_compute_until_prior_art_review` | 18 | public exact/same-connectivity hit; benchmark/control only unless a genuinely new use hypothesis is separately justified |

Exact public hits currently include repeated `NPC23134` and `NPC306277` rows. These should not receive expensive lead-optimization compute except as benchmarks.

## Program-Level Decision

| program | evidence | originality/commercial status | compute decision |
|---|---|---|---|
| R17 constrained generative chromanol | 240/240 Boltz-2 cofold; top/next 60 ns panels 3/3 stable; expanded 60 ns currently 2/3 complete | scientifically strong as a constrained-design and robustness paper; commercial novelty is not cleared because chromanol/benzopyran Markush risk remains | finish current 60 ns job; then pause new heavy chromanol expansion until exact/substructure/Markush review package is prepared |
| R16 topical chromanol anchor triad | 200 ns triad complete; TGFB1/DCT/TYR stable with sub-angstrom to near-sub-angstrom RMSD profile | strongest current in-silico lead family; exact public hits not seen for checked chlorinated examples, but scaffold/use/halogen claim risk remains | use completed data for manuscript and CRO hypothesis; no automatic 300 ns/RBFE/synthesis before Markush/FTO review |
| R15 base chromanol | 14-target cofold and top3 MD complete; triple-safe chromanol has logP 0.94 and weak topical window | base chromanol is known/low composition novelty; useful as safety-first comparator and systemic-vs-topical narrative | no expensive expansion as a commercial lead; keep as benchmark/control and paper context |
| NPASS xTB atlas/refinement | CPU ladder active; many rows remain cheap-compute eligible | academic atlas value is high; individual compounds need public exact/similarity filtering before lead claims | continue CPU xTB/refinement; exact-hit candidates are benchmark-only; promote only baseline-watch/non-hit candidates to later Boltz after screening |
| EMB-3/quinone family | high historical interest; quinone gate flags reactivity/sensitization blocker; MMP1 ZAFF gate still blocked | high-upside but not clean enough for safety-positive or MMP1 ABFE-confirmed claims | hold expensive MMP1/lead claims until quinone wet-lab package and ZAFF/MCPB holo-Zn ABFE/CBFE model pass |
| MMP-1 Zn/ZAFF ABFE | gate says current receptor has 0 explicit Zn atoms; legacy negative values rejected as decoupling-only | binding proof is not established; this is a technical blocker, not a negative result | prioritize ZAFF/MCPB model building as a methods task before any "perfectly binds MMP-1" language |
| extended MD batch2 universal scaffold | 5/5 complete; `srebp1 x R14_5` last-10 ns drift 2.08 A caveat | valuable as robustness/failure-mode evidence; not a distinct commercial lead by itself | use in preprint #15 and methods/failure-mode papers; no extra heavy compute unless tied to a specific lead question |

## Investment Ranking

1. Highest near-term scientific ROI: finish the active R17 expanded 60 ns run and turn R17/R16 into a constrained-design/topical-lead manuscript with explicit Markush/FTO caveat.
2. Highest translational de-risking ROI: MMP-1 ZAFF/MCPB holo-Zn model and quinone safety package, because these directly control whether EMB-3/MMP-1 claims are credible.
3. Highest CPU ROI: keep NPASS xTB/conformer refinement running, but pass candidates through prior-art and safety gates before GPU promotion.
4. Highest commercial-upside but gated: R16/R17 exact or near-exact no-hit chromanol analogs, only after PubChem/SureChEMBL/PATENTSCOPE/Lens/EPO OPS and professional Markush/claim chart review.
5. Lowest current ROI for expensive compute: R15 base chromanol, exact-hit NPASS rows, and EMB-3 MMP1 ABFE claims before Zn/quinone blockers are resolved.

## Go / Hold Rules From Here

- Already running jobs are allowed to finish unless they are broken or duplicative.
- New cheap CPU work is allowed when it contributes to atlas, ranking, or manuscript figures.
- New GPU 10-30 ns triage is allowed only for non-duplicate candidates with no public exact hit and a clear paper/decision role.
- New 60-200 ns MD, RBFE/ABFE, synthesis/purchase, and commercial novelty language require prior-art/Markush review first.
- A `PubChem no_hit` result is not enough for FTO. It only means exact public identity was not found in that layer.
- Any chromanol lead statement must say "in-silico candidate" and "Markush/FTO and wet-lab validation pending".

## External Source Basis

- WIPO FTO/public-domain guide: https://www.wipo.int/publications/en/details.jsp?id=4501
- WIPO PATENTSCOPE Markush search: https://www.wipo.int/en/web/patentscope/w/news/2021/news_0006
- EPO Open Patent Services: https://www.epo.org/en/searching-for-patents/data/web-services/ops
- SureChEMBL patent chemistry resource: https://academic.oup.com/nar/article/44/D1/D1220/2503067
- PubChem PUG-REST: https://pubchem.ncbi.nlm.nih.gov/docs/pug-rest
- CAS MARPAT Markush coverage: https://www.cas.org/es-es/training/documentation/markush
