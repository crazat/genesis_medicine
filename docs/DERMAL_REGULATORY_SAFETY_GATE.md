# Dermal Regulatory Safety Gate

- timestamp: `2026-05-06T12:46:32+09:00`
- rows: `112`
- gate_counts: `{'green': 32, 'yellow': 80, 'red': 0}`
- purpose: 외용제 후보를 OECD TG497 skin sensitisation, ICH S10 photosafety, FDA IVRT/IVPT 관점의 in-silico pre-gate로 제한한다.

## Top Green/Yellow Candidates

| candidate | target | gate | cLogP | MW | alerts | photosafety | IVPT |
|---|---|---|---:|---:|---|---|---|
| R15_chromanol_Me6_Me9 | tgfb1 | green | 1.552 | 208.257 | none_detected | none_detected | ready_for_IVRT_IVPT_design |
| R15_chromanol_Me6_Me10 | tgfb1 | green | 1.552 | 208.257 | none_detected | none_detected | ready_for_IVRT_IVPT_design |
| R15_chromanol_Me9_Me10 | tgfb1 | green | 1.552 | 208.257 | none_detected | none_detected | ready_for_IVRT_IVPT_design |
| R15_chromanol_Me9_Me10 | tyr | green | 1.552 | 208.257 | none_detected | none_detected | ready_for_IVRT_IVPT_design |
| R15_chromanol_Me6_Me9 | tyr | green | 1.552 | 208.257 | none_detected | none_detected | ready_for_IVRT_IVPT_design |
| R15_chromanol_Me6_Me9 | dct | green | 1.552 | 208.257 | none_detected | none_detected | ready_for_IVRT_IVPT_design |
| R15_chromanol_Me9_Me10 | dct | green | 1.552 | 208.257 | none_detected | none_detected | ready_for_IVRT_IVPT_design |
| R15_chromanol_Me6_Me10 | tyr | green | 1.552 | 208.257 | none_detected | none_detected | ready_for_IVRT_IVPT_design |
| R15_chromanol_Me6_Me10 | dct | green | 1.552 | 208.257 | none_detected | none_detected | ready_for_IVRT_IVPT_design |
| NPC323980 |  | green | 2.089 | 174.284 | none_detected | none_detected | ready_for_IVRT_IVPT_design |
| NPC314289 |  | green | 1.184 | 132.203 | none_detected | none_detected | ready_for_IVRT_IVPT_design |
| NPC325130 |  | green | 1.184 | 144.214 | none_detected | none_detected | ready_for_IVRT_IVPT_design |
| NPC77156 |  | green | 1.071 | 170.208 | none_detected | none_detected | ready_for_IVRT_IVPT_design |
| NPC33067 |  | green | 1.08 | 142.198 | none_detected | none_detected | ready_for_IVRT_IVPT_design |
| NPC475968 |  | green | 1.943 | 256.386 | none_detected | none_detected | ready_for_IVRT_IVPT_design |
| NPC184593 |  | green | 1.405 | 118.176 | none_detected | none_detected | ready_for_IVRT_IVPT_design |
| NPC329253 |  | green | 2.987 | 238.371 | none_detected | none_detected | ready_for_IVRT_IVPT_design |
| NPC196715 |  | green | 2.987 | 238.371 | none_detected | none_detected | ready_for_IVRT_IVPT_design |
| NPC261839 |  | green | 2.281 | 284.396 | none_detected | none_detected | ready_for_IVRT_IVPT_design |
| NPC168128 |  | green | 1.203 | 183.295 | none_detected | none_detected | ready_for_IVRT_IVPT_design |
| NPC329473 |  | green | 2.345 | 234.387 | none_detected | none_detected | ready_for_IVRT_IVPT_design |
| NPC228980 |  | green | 2.345 | 234.387 | none_detected | none_detected | ready_for_IVRT_IVPT_design |
| NPC249078 |  | green | 2.725 | 238.371 | none_detected | none_detected | ready_for_IVRT_IVPT_design |
| NPC302293 |  | green | 1.695 | 242.359 | none_detected | none_detected | ready_for_IVRT_IVPT_design |
| NPC195282 |  | green | 2.725 | 238.371 | none_detected | none_detected | ready_for_IVRT_IVPT_design |
| NPC254230 |  | green | 1.201 | 183.295 | none_detected | none_detected | ready_for_IVRT_IVPT_design |
| NPC42783 |  | green | 2.482 | 188.311 | none_detected | none_detected | ready_for_IVRT_IVPT_design |
| NPC193781 |  | green | 1.696 | 254.37 | none_detected | none_detected | ready_for_IVRT_IVPT_design |
| NPC107271 |  | green | 1.958 | 254.37 | none_detected | none_detected | ready_for_IVRT_IVPT_design |
| NPC241081 |  | green | 2.722 | 308.462 | none_detected | none_detected | ready_for_IVRT_IVPT_design |

## Curator Rule

- `green`: topical lead paper main table에 둘 수 있지만 여전히 in-silico pre-gate다.
- `yellow`: OECD TG497/ICH S10/CRO assay plan을 같이 적고 강한 safety claim을 피한다.
- `red`: 외용 lead claim에서 제외하거나 구조 수정 후보로만 둔다.
