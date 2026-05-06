# Pre-Compute Prior-Art Gate

- timestamp: `2026-05-02T21:43:57+09:00`
- rows: `1322`
- pubchem_network_checked: `False`
- pubchem_network_limit: `80`
- gate_counts: `{'hold_expensive_compute_until_prior_art_review': 32, 'hold_expensive_compute_until_markush_review': 579, 'cheap_compute_allowed_prior_art_pending': 711}`
- purpose: expensive GPU/CPU/wet-lab spend before public-prior-art, Markush, legal-status, and academic/commercial value review is avoided.
- legal caveat: this is technical triage, not attorney FTO opinion.

## Source Stack

| layer | role |
|---|---|
| public/free | PubChem PUG-REST exact/same-connectivity |
| public/free | SureChEMBL compound-patent associations |
| public/free | WIPO PATENTSCOPE exact/substructure/Markush |
| public/free | Google Patents text/family search |
| public/free | Lens patent/scholarly API |
| public/free | EPO OPS family/legal-status API |
| public/free | USPTO Patent Public Search/PatentsView |
| public/free | OpenAlex/Crossref/PubMed scholarly search |
| professional/manual | CAS REGISTRY/MARPAT/STNext or CAS IP Finder |
| professional/manual | Derwent Innovation/DWPI + chemistry resource |
| professional/manual | Reaxys/SciFinder-n literature and synthesis search |
| professional/manual | patent attorney claim chart and legal-status opinion |

## Decision Rule

- `deprioritize_or_benchmark_only`: known/close analog. Do not spend lead-optimization compute unless it is a benchmark or a clear new-use hypothesis.
- `hold_expensive_compute_until_prior_art_review`: exact/same-connectivity public hit. Cheap ranking may continue, but MD 60-200 ns, RBFE/ABFE, synthesis, and commercial claims wait.
- `hold_expensive_compute_until_markush_review`: scaffold/use/halogen Markush risk. Cheap ranking may continue; professional Markush and claim chart are required before heavy follow-up.
- `cheap_compute_allowed_prior_art_pending`: no current block, but composition/use/formulation claims still require manual/professional review.

## Current Hold Queue

| candidate | target | risk | PubChem | gate | reason |
|---|---|---|---|---|---|
| NPC23134 |  | medium_review | hit/hit | hold_expensive_compute_until_prior_art_review | public exact/same-connectivity hit; continue only cheap benchmarking until patent/literature context is reviewed |
| NPC306277 |  | medium_review | hit/hit | hold_expensive_compute_until_prior_art_review | public exact/same-connectivity hit; continue only cheap benchmarking until patent/literature context is reviewed |
| R15_chromanol_Cl_pos10 | tgfb1 | medium_review | no_hit/no_hit | hold_expensive_compute_until_markush_review | generic scaffold/halogen/use-claim risk; allow cheap triage, hold 60-200ns/RBFE/ABFE/synthesis until Markush and claim chart review |
| R15_chromanol_Cl_pos10 | dct | medium_review | no_hit/no_hit | hold_expensive_compute_until_markush_review | generic scaffold/halogen/use-claim risk; allow cheap triage, hold 60-200ns/RBFE/ABFE/synthesis until Markush and claim chart review |
| R15_chromanol_Cl_pos10 | tyr | medium_review | no_hit/no_hit | hold_expensive_compute_until_markush_review | generic scaffold/halogen/use-claim risk; allow cheap triage, hold 60-200ns/RBFE/ABFE/synthesis until Markush and claim chart review |
| R15_chromanol_Cl_pos6 | tgfb1 | medium_review | no_hit/no_hit | hold_expensive_compute_until_markush_review | generic scaffold/halogen/use-claim risk; allow cheap triage, hold 60-200ns/RBFE/ABFE/synthesis until Markush and claim chart review |
| R15_chromanol_Cl_pos6 | dct | medium_review | no_hit/no_hit | hold_expensive_compute_until_markush_review | generic scaffold/halogen/use-claim risk; allow cheap triage, hold 60-200ns/RBFE/ABFE/synthesis until Markush and claim chart review |
| R15_chromanol_Cl_pos6 | tyr | medium_review | no_hit/no_hit | hold_expensive_compute_until_markush_review | generic scaffold/halogen/use-claim risk; allow cheap triage, hold 60-200ns/RBFE/ABFE/synthesis until Markush and claim chart review |
| R15_chromanol_Cl_pos9 | tgfb1 | medium_review | no_hit/no_hit | hold_expensive_compute_until_markush_review | generic scaffold/halogen/use-claim risk; allow cheap triage, hold 60-200ns/RBFE/ABFE/synthesis until Markush and claim chart review |
| R15_chromanol_Cl_pos9 | dct | medium_review | no_hit/no_hit | hold_expensive_compute_until_markush_review | generic scaffold/halogen/use-claim risk; allow cheap triage, hold 60-200ns/RBFE/ABFE/synthesis until Markush and claim chart review |
| R15_chromanol_Cl_pos9 | tyr | medium_review | no_hit/no_hit | hold_expensive_compute_until_markush_review | generic scaffold/halogen/use-claim risk; allow cheap triage, hold 60-200ns/RBFE/ABFE/synthesis until Markush and claim chart review |
| chromanol_arom10_CN_dct | dct | medium_review | no_hit/no_hit | hold_expensive_compute_until_markush_review | generic scaffold/halogen/use-claim risk; allow cheap triage, hold 60-200ns/RBFE/ABFE/synthesis until Markush and claim chart review |
| chromanol_arom10_CN_mmp1 | mmp1 | medium_review | no_hit/no_hit | hold_expensive_compute_until_markush_review | generic scaffold/halogen/use-claim risk; allow cheap triage, hold 60-200ns/RBFE/ABFE/synthesis until Markush and claim chart review |
| chromanol_arom10_CN_ptgs2 | ptgs2 | medium_review | no_hit/no_hit | hold_expensive_compute_until_markush_review | generic scaffold/halogen/use-claim risk; allow cheap triage, hold 60-200ns/RBFE/ABFE/synthesis until Markush and claim chart review |
| chromanol_arom10_CN_tgfb1 | tgfb1 | medium_review | no_hit/no_hit | hold_expensive_compute_until_markush_review | generic scaffold/halogen/use-claim risk; allow cheap triage, hold 60-200ns/RBFE/ABFE/synthesis until Markush and claim chart review |
| chromanol_arom10_CN_tyr | tyr | medium_review | no_hit/no_hit | hold_expensive_compute_until_markush_review | generic scaffold/halogen/use-claim risk; allow cheap triage, hold 60-200ns/RBFE/ABFE/synthesis until Markush and claim chart review |
| chromanol_arom10_Cl_dct | dct | medium_review | no_hit/no_hit | hold_expensive_compute_until_markush_review | generic scaffold/halogen/use-claim risk; allow cheap triage, hold 60-200ns/RBFE/ABFE/synthesis until Markush and claim chart review |
| chromanol_arom10_Cl_mmp1 | mmp1 | medium_review | no_hit/no_hit | hold_expensive_compute_until_markush_review | generic scaffold/halogen/use-claim risk; allow cheap triage, hold 60-200ns/RBFE/ABFE/synthesis until Markush and claim chart review |
| chromanol_arom10_Cl_ptgs2 | ptgs2 | medium_review | no_hit/no_hit | hold_expensive_compute_until_markush_review | generic scaffold/halogen/use-claim risk; allow cheap triage, hold 60-200ns/RBFE/ABFE/synthesis until Markush and claim chart review |
| chromanol_arom10_Cl_tgfb1 | tgfb1 | medium_review | no_hit/no_hit | hold_expensive_compute_until_markush_review | generic scaffold/halogen/use-claim risk; allow cheap triage, hold 60-200ns/RBFE/ABFE/synthesis until Markush and claim chart review |
| chromanol_arom10_Cl_tyr | tyr | medium_review | no_hit/no_hit | hold_expensive_compute_until_markush_review | generic scaffold/halogen/use-claim risk; allow cheap triage, hold 60-200ns/RBFE/ABFE/synthesis until Markush and claim chart review |
| chromanol_arom10_F_dct | dct | medium_review | no_hit/no_hit | hold_expensive_compute_until_markush_review | generic scaffold/halogen/use-claim risk; allow cheap triage, hold 60-200ns/RBFE/ABFE/synthesis until Markush and claim chart review |
| chromanol_arom10_F_mmp1 | mmp1 | medium_review | no_hit/no_hit | hold_expensive_compute_until_markush_review | generic scaffold/halogen/use-claim risk; allow cheap triage, hold 60-200ns/RBFE/ABFE/synthesis until Markush and claim chart review |
| chromanol_arom10_F_ptgs2 | ptgs2 | medium_review | no_hit/no_hit | hold_expensive_compute_until_markush_review | generic scaffold/halogen/use-claim risk; allow cheap triage, hold 60-200ns/RBFE/ABFE/synthesis until Markush and claim chart review |
| chromanol_arom10_F_tgfb1 | tgfb1 | medium_review | no_hit/no_hit | hold_expensive_compute_until_markush_review | generic scaffold/halogen/use-claim risk; allow cheap triage, hold 60-200ns/RBFE/ABFE/synthesis until Markush and claim chart review |

## Attorney/Professional DB Package

For each serious lead, export: canonical SMILES, InChIKey, Murcko scaffold, substituent map, targets/use cases, intended countries, intended launch window, public exact hits, top patent families, claim chart placeholders, and legal-status notes.

Required searches before expensive compute or commercial claim:

1. Exact identity and same-connectivity: PubChem, SureChEMBL, Google Patents text, Lens.
2. Similarity/substructure: PubChem fastsimilarity/fastsubstructure, ChEMBL, SureChEMBL.
3. Markush: WIPO PATENTSCOPE logged-in chemical search and CAS MARPAT/STNext/CAS IP Finder.
4. Legal status/family: EPO OPS/INPADOC, PATENTSCOPE family, national registers for intended jurisdictions.
5. Academic value: OpenAlex/Crossref/PubMed + positive/negative control landscape.
6. Commercial value: active assignees, granted/pending family count, expiry, claim overlap, formulation/use differentiation.
