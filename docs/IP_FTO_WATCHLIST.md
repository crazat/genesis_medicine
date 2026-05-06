# IP FTO Watchlist

- timestamp: `2026-05-06T12:46:35+09:00`
- rows: `752`
- risk_counts: `{'high_review': 0, 'medium_review': 11, 'baseline_watch': 741}`
- manual_review_template: `data/ip_fto_manual_review_template.csv`
- purpose: local Tanimoto novelty와 실제 patent/FTO 검토를 분리해, 신규성/상업성 claim을 과장하지 않는다.

## Review Queue

| candidate | target | risk | novelty | scaffold | query terms |
|---|---|---|---|---|---|
| NPC23134 |  | medium_review | close_series | C1CCOCC1 | NPC23134 OR C1CCOCC1 OR skin topical small molecule |
| NPC306277 |  | medium_review | close_series | acyclic | NPC306277 OR acyclic OR skin topical small molecule |
| R15_chromanol_Cl_pos10 | tgfb1 | medium_review | locally_distinct | c1ccc2c(c1)CCCO2 | R15_chromanol_Cl_pos10 OR c1ccc2c(c1)CCCO2 OR chromanol OR benzopyran OR topical dermatology OR halogenated analog Markush OR scar OR fibrosis OR collagen OR TGF beta |
| R15_chromanol_Cl_pos10 | dct | medium_review | locally_distinct | c1ccc2c(c1)CCCO2 | R15_chromanol_Cl_pos10 OR c1ccc2c(c1)CCCO2 OR chromanol OR benzopyran OR topical dermatology OR halogenated analog Markush OR melanin OR tyrosinase OR hyperpigmentation |
| R15_chromanol_Cl_pos10 | tyr | medium_review | locally_distinct | c1ccc2c(c1)CCCO2 | R15_chromanol_Cl_pos10 OR c1ccc2c(c1)CCCO2 OR chromanol OR benzopyran OR topical dermatology OR halogenated analog Markush OR melanin OR tyrosinase OR hyperpigmentation |
| R15_chromanol_Cl_pos9 | tgfb1 | medium_review | locally_distinct | c1ccc2c(c1)CCCO2 | R15_chromanol_Cl_pos9 OR c1ccc2c(c1)CCCO2 OR chromanol OR benzopyran OR topical dermatology OR halogenated analog Markush OR scar OR fibrosis OR collagen OR TGF beta |
| R15_chromanol_Cl_pos9 | dct | medium_review | locally_distinct | c1ccc2c(c1)CCCO2 | R15_chromanol_Cl_pos9 OR c1ccc2c(c1)CCCO2 OR chromanol OR benzopyran OR topical dermatology OR halogenated analog Markush OR melanin OR tyrosinase OR hyperpigmentation |
| R15_chromanol_Cl_pos9 | tyr | medium_review | locally_distinct | c1ccc2c(c1)CCCO2 | R15_chromanol_Cl_pos9 OR c1ccc2c(c1)CCCO2 OR chromanol OR benzopyran OR topical dermatology OR halogenated analog Markush OR melanin OR tyrosinase OR hyperpigmentation |
| R15_chromanol_Cl_pos6 | tgfb1 | medium_review | locally_distinct | c1ccc2c(c1)CCCO2 | R15_chromanol_Cl_pos6 OR c1ccc2c(c1)CCCO2 OR chromanol OR benzopyran OR topical dermatology OR halogenated analog Markush OR scar OR fibrosis OR collagen OR TGF beta |
| R15_chromanol_Cl_pos6 | dct | medium_review | locally_distinct | c1ccc2c(c1)CCCO2 | R15_chromanol_Cl_pos6 OR c1ccc2c(c1)CCCO2 OR chromanol OR benzopyran OR topical dermatology OR halogenated analog Markush OR melanin OR tyrosinase OR hyperpigmentation |
| R15_chromanol_Cl_pos6 | tyr | medium_review | locally_distinct | c1ccc2c(c1)CCCO2 | R15_chromanol_Cl_pos6 OR c1ccc2c(c1)CCCO2 OR chromanol OR benzopyran OR topical dermatology OR halogenated analog Markush OR melanin OR tyrosinase OR hyperpigmentation |
| R15_chromanol | tgfb1 | baseline_watch | locally_distinct | c1ccc2c(c1)CCCO2 | R15_chromanol OR c1ccc2c(c1)CCCO2 OR chromanol OR benzopyran OR topical dermatology OR scar OR fibrosis OR collagen OR TGF beta |
| R15_chromanol | tyr | baseline_watch | locally_distinct | c1ccc2c(c1)CCCO2 | R15_chromanol OR c1ccc2c(c1)CCCO2 OR chromanol OR benzopyran OR topical dermatology OR melanin OR tyrosinase OR hyperpigmentation |
| R15_chromanol | dct | baseline_watch | locally_distinct | c1ccc2c(c1)CCCO2 | R15_chromanol OR c1ccc2c(c1)CCCO2 OR chromanol OR benzopyran OR topical dermatology OR melanin OR tyrosinase OR hyperpigmentation |
| R15_chromanol | ptgs2 | baseline_watch | locally_distinct | c1ccc2c(c1)CCCO2 | R15_chromanol OR c1ccc2c(c1)CCCO2 OR chromanol OR benzopyran OR topical dermatology |
| R15_chromanol | sirt1 | baseline_watch | locally_distinct | c1ccc2c(c1)CCCO2 | R15_chromanol OR c1ccc2c(c1)CCCO2 OR chromanol OR benzopyran OR topical dermatology |
| R15_chromanol | tyrp1 | baseline_watch | locally_distinct | c1ccc2c(c1)CCCO2 | R15_chromanol OR c1ccc2c(c1)CCCO2 OR chromanol OR benzopyran OR topical dermatology OR melanin OR tyrosinase OR hyperpigmentation |
| R15_chromanol | ar | baseline_watch | locally_distinct | c1ccc2c(c1)CCCO2 | R15_chromanol OR c1ccc2c(c1)CCCO2 OR chromanol OR benzopyran OR topical dermatology OR androgen OR alopecia OR 5 alpha reductase |
| R15_chromanol | mmp1 | baseline_watch | locally_distinct | c1ccc2c(c1)CCCO2 | R15_chromanol OR c1ccc2c(c1)CCCO2 OR chromanol OR benzopyran OR topical dermatology OR scar OR fibrosis OR collagen OR TGF beta |
| R15_chromanol | srebp1 | baseline_watch | locally_distinct | c1ccc2c(c1)CCCO2 | R15_chromanol OR c1ccc2c(c1)CCCO2 OR chromanol OR benzopyran OR topical dermatology |
| R15_chromanol | mitf | baseline_watch | locally_distinct | c1ccc2c(c1)CCCO2 | R15_chromanol OR c1ccc2c(c1)CCCO2 OR chromanol OR benzopyran OR topical dermatology OR melanin OR tyrosinase OR hyperpigmentation |
| R15_chromanol | lox | baseline_watch | locally_distinct | c1ccc2c(c1)CCCO2 | R15_chromanol OR c1ccc2c(c1)CCCO2 OR chromanol OR benzopyran OR topical dermatology OR scar OR fibrosis OR collagen OR TGF beta |
| R15_chromanol | srd5a1 | baseline_watch | locally_distinct | c1ccc2c(c1)CCCO2 | R15_chromanol OR c1ccc2c(c1)CCCO2 OR chromanol OR benzopyran OR topical dermatology OR androgen OR alopecia OR 5 alpha reductase |
| R15_chromanol | ctgf | baseline_watch | locally_distinct | c1ccc2c(c1)CCCO2 | R15_chromanol OR c1ccc2c(c1)CCCO2 OR chromanol OR benzopyran OR topical dermatology OR scar OR fibrosis OR collagen OR TGF beta |
| R15_chromanol | srd5a2 | baseline_watch | locally_distinct | c1ccc2c(c1)CCCO2 | R15_chromanol OR c1ccc2c(c1)CCCO2 OR chromanol OR benzopyran OR topical dermatology OR androgen OR alopecia OR 5 alpha reductase |
| NPC20938 |  | baseline_watch | locally_distinct | C1CCOCC1 | NPC20938 OR C1CCOCC1 OR skin topical small molecule |
| NPC35553 |  | baseline_watch | locally_distinct | C1CCOCC1 | NPC35553 OR C1CCOCC1 OR skin topical small molecule |
| NPC120104 |  | baseline_watch | locally_distinct | C1CCOCC1 | NPC120104 OR C1CCOCC1 OR skin topical small molecule |
| NPC256808 |  | baseline_watch | locally_distinct | C1CC[C@H](O[C@@H]2C[C@@H]3CCC2C3)OC1 | NPC256808 OR C1CC[C@H](O[C@@H]2C[C@@H]3CCC2C3)OC1 OR skin topical small molecule |
| NPC251201 |  | baseline_watch | locally_distinct | C1CC[C@@H]2CC[C@H]3[C@@H]4CCCC4CC[C@@H]3C2C1 | NPC251201 OR C1CC[C@@H]2CC[C@H]3[C@@H]4CCCC4CC[C@@H]3C2C1 OR skin topical small molecule |
| NPC83285 |  | baseline_watch | locally_distinct | C1CCC(O[C@H]2CCCCO2)CC1 | NPC83285 OR C1CCC(O[C@H]2CCCCO2)CC1 OR skin topical small molecule |
| NPC196136 |  | baseline_watch | locally_distinct | C1CCC2C(C1)CC[C@H]1[C@@H]3CCCC3CC[C@H]21 | NPC196136 OR C1CCC2C(C1)CC[C@H]1[C@@H]3CCCC3CC[C@H]21 OR skin topical small molecule |
| NPC228994 |  | baseline_watch | locally_distinct | C1CCC2C(C1)CC[C@H]1[C@@H]3CCCC3CC[C@H]21 | NPC228994 OR C1CCC2C(C1)CC[C@H]1[C@@H]3CCCC3CC[C@H]21 OR skin topical small molecule |
| NPC327468 |  | baseline_watch | locally_distinct | C1CCC2C(C1)CCC1C3CCCC3CCC21 | NPC327468 OR C1CCC2C(C1)CCC1C3CCCC3CCC21 OR skin topical small molecule |
| NPC329253 |  | baseline_watch | locally_distinct | C1CC2CC3CCC(OC3)C2C1 | NPC329253 OR C1CC2CC3CCC(OC3)C2C1 OR skin topical small molecule |

## Curator Rule

- `high_review`: patent/FTO 검토 전에는 novelty, freedom-to-operate, commercial differentiation claim을 금지한다.
- `medium_review`: manuscript에는 local novelty까지만 쓰고 외부 patent search pending을 명시한다.
- `baseline_watch`: follow-up 가능하지만 composition/use/formulation claim은 수동 검토 후에만 쓴다.
