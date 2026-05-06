# Synthesis and Retrosynthesis Gate

- timestamp: `2026-05-06T12:46:04+09:00`
- candidate_rows: `112`
- gate_counts: `{'green': 73, 'yellow': 36, 'red': 3}`
- CASP availability: `{'aizynthfinder_python': False, 'aizynthcli': False, 'askcos_cli': False}`
- purpose: 계산 후보를 실제 합성 가능성/route risk 관점에서 한 번 더 걸러낸다.

## Interpretation

- `green`: 현재 휴리스틱으로는 route risk가 낮다. vendor/building-block 또는 실제 retrosynthesis 확인으로 넘어갈 수 있다.
- `yellow`: 합성 가능할 수 있지만 stereochemistry, size, topology 또는 polarity 때문에 true retrosynthesis 확인이 필요하다.
- `red`: 계산 점수가 높아도 합성/조제 후보로 바로 승격하지 않는다.
- AiZynthFinder/ASKCOS가 설치되지 않은 경우 이 gate는 route solution이 아니라 conservative triage다.

## Top Candidates

| candidate | target | source | gate | score | risk |
|---|---|---|---|---:|---|
| R15_chromanol_Cl_pos9 | tgfb1 | r16_chromanol_topical_cofold | green | 1.0 | no major heuristic route risk |
| R15_chromanol_Cl_pos6 | tgfb1 | r16_chromanol_topical_cofold | green | 1.0 | no major heuristic route risk |
| R15_chromanol_Cl_pos10 | tgfb1 | r16_chromanol_topical_cofold | green | 1.0 | no major heuristic route risk |
| R15_chromanol_Cl_pos9 | dct | r16_chromanol_topical_cofold | green | 1.0 | no major heuristic route risk |
| R15_chromanol_Cl_pos6 | dct | r16_chromanol_topical_cofold | green | 1.0 | no major heuristic route risk |
| R15_chromanol_Cl_pos6 | tyr | r16_chromanol_topical_cofold | green | 1.0 | no major heuristic route risk |
| R15_chromanol_Cl_pos10 | dct | r16_chromanol_topical_cofold | green | 1.0 | no major heuristic route risk |
| R15_chromanol_Cl_pos9 | tyr | r16_chromanol_topical_cofold | green | 1.0 | no major heuristic route risk |
| R15_chromanol_Cl_pos10 | tyr | r16_chromanol_topical_cofold | green | 1.0 | no major heuristic route risk |
| R15_chromanol | tgfb1 | r15_chromanol_cofold | green | 0.94 | no major heuristic route risk |
| R15_chromanol | tyr | r15_chromanol_cofold | green | 0.94 | no major heuristic route risk |
| R15_chromanol | dct | r15_chromanol_cofold | green | 0.94 | no major heuristic route risk |
| R15_chromanol | ptgs2 | r15_chromanol_cofold | green | 0.94 | no major heuristic route risk |
| R15_chromanol | sirt1 | r15_chromanol_cofold | green | 0.94 | no major heuristic route risk |
| R15_chromanol | tyrp1 | r15_chromanol_cofold | green | 0.94 | no major heuristic route risk |
| R15_chromanol | ar | r15_chromanol_cofold | green | 0.94 | no major heuristic route risk |
| R15_chromanol | mmp1 | r15_chromanol_cofold | green | 0.94 | no major heuristic route risk |
| R15_chromanol | srebp1 | r15_chromanol_cofold | green | 0.94 | no major heuristic route risk |
| R15_chromanol | mitf | r15_chromanol_cofold | green | 0.94 | no major heuristic route risk |
| R15_chromanol | lox | r15_chromanol_cofold | green | 0.94 | no major heuristic route risk |

## Curator Use

- `green` 후보는 active-learning/Boltz/MD 후속으로 승격 가능하다.
- `yellow` 후보는 true retrosynthesis 또는 chemist review 없이는 논문에서 synthesizable claim을 하지 않는다.
- `red` 후보는 scaffold redesign, building-block replacement, 또는 negative-control로 분류한다.
