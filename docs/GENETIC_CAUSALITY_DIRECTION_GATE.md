# Genetic Causality Direction Gate

- timestamp: `2026-05-06T12:46:30+09:00`
- rows: `31`
- gate_counts: `{'direction_plausible': 9, 'direction_needs_genetic_or_phenotype_support': 1, 'causality_weak_or_unknown': 21}`
- purpose: target evidence를 disease association뿐 아니라 desired direction-of-effect, genetic/MR caveat와 연결한다.

## Direction Rows

| target | gate | desired direction | OT skin | OT translational | next |
|---|---|---|---:|---:|---|
| ctgf | direction_plausible | inhibit_or_reduce_pathway | 0.0 | 0.329 | use target claim with explicit direction-of-effect caveat |
| lox | direction_plausible | inhibit_or_reduce_pathway | 0.409 | 0.0 | use target claim with explicit direction-of-effect caveat |
| mmp1 | direction_plausible | context_dependent_modulate | 0.612 | 0.0 | use target claim with explicit direction-of-effect caveat |
| dct | direction_plausible | context_dependent_pigment_modulate | 0.747 | 0.0 | use target claim with explicit direction-of-effect caveat |
| mc1r | direction_plausible | context_dependent_pigment_modulate | 0.717 | 0.0 | use target claim with explicit direction-of-effect caveat |
| nr3c1 | direction_plausible | agonize_or_modulate_with_barrier_safety_caveat | 0.604 | 0.0 | use target claim with explicit direction-of-effect caveat |
| tyr | direction_plausible | inhibit_for_depigmentation_or_preserve_for_hair_pigment | 0.858 | 0.0 | use target claim with explicit direction-of-effect caveat |
| tyrp1 | direction_plausible | context_dependent_pigment_modulate | 0.803 | 0.0 | use target claim with explicit direction-of-effect caveat |
| ar | direction_plausible | antagonize_in_acne_or_alopecia_context | 0.582 | 0.0 | use target claim with explicit direction-of-effect caveat |
| tgfb1 | direction_needs_genetic_or_phenotype_support | inhibit_or_reduce_pathway | 0.0 | 0.0 | add Open Targets direction/MR/pQTL/eQTL limitation before strong biology claim |
| ctnnb1 | causality_weak_or_unknown | unknown | 0.0 | 0.0 | keep as exploratory target or negative-control until causal evidence improves |
| fgf2 | causality_weak_or_unknown | unknown | 0.094 | 0.0 | keep as exploratory target or negative-control until causal evidence improves |
| vegfa | causality_weak_or_unknown | unknown | 0.0 | 0.0 | keep as exploratory target or negative-control until causal evidence improves |
| f2rl1 | causality_weak_or_unknown | unknown | 0.0 | 0.0 | keep as exploratory target or negative-control until causal evidence improves |
| mitf | causality_weak_or_unknown | unknown | 0.757 | 0.0 | keep as exploratory target or negative-control until causal evidence improves |
| mylk | causality_weak_or_unknown | unknown | 0.0 | 0.0 | keep as exploratory target or negative-control until causal evidence improves |
| piezo1 | causality_weak_or_unknown | unknown | 0.353 | 0.0 | keep as exploratory target or negative-control until causal evidence improves |
| ptgdr2 | causality_weak_or_unknown | unknown | 0.0 | 0.0 | keep as exploratory target or negative-control until causal evidence improves |
| srd5a1 | causality_weak_or_unknown | unknown | 0.481 | 0.0 | keep as exploratory target or negative-control until causal evidence improves |
| srd5a2 | causality_weak_or_unknown | unknown | 0.702 | 0.0 | keep as exploratory target or negative-control until causal evidence improves |
| wnt10b | causality_weak_or_unknown | unknown | 0.038 | 0.0 | keep as exploratory target or negative-control until causal evidence improves |
| nlrp3 | causality_weak_or_unknown | unknown | 0.0 | 0.0 | keep as exploratory target or negative-control until causal evidence improves |
| ptgs2 | causality_weak_or_unknown | inhibit_in_inflammatory_context | 0.0 | 0.0 | keep as exploratory target or negative-control until causal evidence improves |
| rarg | causality_weak_or_unknown | unknown | 0.609 | 0.0 | keep as exploratory target or negative-control until causal evidence improves |
| srebf1 | causality_weak_or_unknown | unknown | 0.0 | 0.0 | keep as exploratory target or negative-control until causal evidence improves |
| tlr2 | causality_weak_or_unknown | unknown | 0.0 | 0.0 | keep as exploratory target or negative-control until causal evidence improves |
| col1a1 | causality_weak_or_unknown | unknown | 0.542 | 0.0 | keep as exploratory target or negative-control until causal evidence improves |
| jun | causality_weak_or_unknown | unknown | 0.372 | 0.0 | keep as exploratory target or negative-control until causal evidence improves |
| mmp3 | causality_weak_or_unknown | unknown | 0.0 | 0.0 | keep as exploratory target or negative-control until causal evidence improves |
| mmp9 | causality_weak_or_unknown | unknown | 0.0 | 0.0 | keep as exploratory target or negative-control until causal evidence improves |
| sirt1 | causality_weak_or_unknown | unknown | 0.109 | 0.0 | keep as exploratory target or negative-control until causal evidence improves |

## Curator Rule

- `direction_plausible`: target-focused narrative 가능하지만 causal proof가 아니라는 caveat를 유지한다.
- `direction_needs_genetic_or_phenotype_support`: phenotype or genetic direction evidence를 먼저 보강한다.
- `causality_weak_or_unknown`: biology claim을 exploratory로 낮춘다.
