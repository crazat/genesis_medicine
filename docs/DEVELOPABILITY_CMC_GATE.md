# Developability CMC Gate

- timestamp: `2026-05-06T12:46:34+09:00`
- rows: `112`
- gate_counts: `{'green': 34, 'yellow': 78, 'red': 0}`
- purpose: hit/lead 후보를 solubility, stability, excipient compatibility, solid-form risk, scale-up risk 관점으로 조기 제한한다.

## Top Rows

| candidate | target | gate | cLogP | logS proxy | alerts | next |
|---|---|---|---:|---:|---|---|
| NPC42783 |  | green | 2.482 | -1.911 | high_flexibility_impurity_method_watch | advance with solubility, pH stability, and vehicle compatibility screen |
| NPC323980 |  | green | 2.089 | -1.906 | none_detected | advance with solubility, pH stability, and vehicle compatibility screen |
| NPC184593 |  | green | 1.405 | -1.194 | volatile_or_retention_risk | advance with solubility, pH stability, and vehicle compatibility screen |
| NPC249078 |  | green | 2.725 | -3.034 | none_detected | advance with solubility, pH stability, and vehicle compatibility screen |
| NPC314289 |  | green | 1.184 | -1.076 | none_detected | advance with solubility, pH stability, and vehicle compatibility screen |
| NPC302293 |  | green | 1.695 | -2.345 | none_detected | advance with solubility, pH stability, and vehicle compatibility screen |
| NPC193781 |  | green | 1.696 | -2.485 | none_detected | advance with solubility, pH stability, and vehicle compatibility screen |
| NPC325130 |  | green | 1.184 | -1.414 | none_detected | advance with solubility, pH stability, and vehicle compatibility screen |
| NPC241081 |  | green | 2.722 | -3.467 | none_detected | advance with solubility, pH stability, and vehicle compatibility screen |
| NPC195282 |  | green | 2.725 | -3.034 | none_detected | advance with solubility, pH stability, and vehicle compatibility screen |
| NPC475968 |  | green | 1.943 | -2.522 | none_detected | advance with solubility, pH stability, and vehicle compatibility screen |
| NPC179262 |  | green | 3.353 | -4.363 | none_detected | advance with solubility, pH stability, and vehicle compatibility screen |
| NPC77156 |  | green | 1.071 | -1.57 | none_detected | advance with solubility, pH stability, and vehicle compatibility screen |
| NPC329253 |  | green | 2.987 | -3.2 | none_detected | advance with solubility, pH stability, and vehicle compatibility screen |
| NPC59871 |  | green | 2.708 | -4.361 | none_detected | advance with solubility, pH stability, and vehicle compatibility screen |
| NPC196715 |  | green | 2.987 | -3.134 | none_detected | advance with solubility, pH stability, and vehicle compatibility screen |
| NPC107271 |  | green | 1.958 | -2.651 | none_detected | advance with solubility, pH stability, and vehicle compatibility screen |
| NPC33067 |  | green | 1.08 | -1.402 | none_detected | advance with solubility, pH stability, and vehicle compatibility screen |
| NPC261839 |  | green | 2.281 | -2.974 | none_detected | advance with solubility, pH stability, and vehicle compatibility screen |
| NPC168128 |  | green | 1.203 | -1.668 | none_detected | advance with solubility, pH stability, and vehicle compatibility screen |
| NPC192944 |  | green | 1.053 | -2.701 | none_detected | advance with solubility, pH stability, and vehicle compatibility screen |
| NPC254230 |  | green | 1.201 | -1.733 | none_detected | advance with solubility, pH stability, and vehicle compatibility screen |
| NPC25947 |  | green | 3.31 | -4.635 | none_detected | advance with solubility, pH stability, and vehicle compatibility screen |
| NPC329473 |  | green | 2.345 | -2.771 | none_detected | advance with solubility, pH stability, and vehicle compatibility screen |
| NPC228980 |  | green | 2.345 | -2.771 | none_detected | advance with solubility, pH stability, and vehicle compatibility screen |
| R15_chromanol_Me6_Me9 | tgfb1 | green | 1.552 | -2.339 | catechol_or_resorcinol;phenol | advance with solubility, pH stability, and vehicle compatibility screen |
| R15_chromanol_Me6_Me10 | tgfb1 | green | 1.552 | -2.339 | catechol_or_resorcinol;phenol | advance with solubility, pH stability, and vehicle compatibility screen |
| R15_chromanol_Me9_Me10 | tgfb1 | green | 1.552 | -2.339 | catechol_or_resorcinol;phenol | advance with solubility, pH stability, and vehicle compatibility screen |
| R15_chromanol_Me9_Me10 | tyr | green | 1.552 | -2.339 | catechol_or_resorcinol;phenol | advance with solubility, pH stability, and vehicle compatibility screen |
| R15_chromanol_Me6_Me9 | tyr | green | 1.552 | -2.339 | catechol_or_resorcinol;phenol | advance with solubility, pH stability, and vehicle compatibility screen |
| R15_chromanol_Me6_Me9 | dct | green | 1.552 | -2.339 | catechol_or_resorcinol;phenol | advance with solubility, pH stability, and vehicle compatibility screen |
| R15_chromanol_Me9_Me10 | dct | green | 1.552 | -2.339 | catechol_or_resorcinol;phenol | advance with solubility, pH stability, and vehicle compatibility screen |
| R15_chromanol_Me6_Me10 | tyr | green | 1.552 | -2.339 | catechol_or_resorcinol;phenol | advance with solubility, pH stability, and vehicle compatibility screen |
| R15_chromanol_Me6_Me10 | dct | green | 1.552 | -2.339 | catechol_or_resorcinol;phenol | advance with solubility, pH stability, and vehicle compatibility screen |
| NPC213764 |  | yellow | 0.531 | -0.577 | volatile_or_retention_risk | run CMC de-risking before lead claim: kinetic solubility, pH stability, excipient compatibility |

## Curator Rule

- `green`: lead table에 둘 수 있으나 solubility/pH stability/vehicle compatibility는 pending으로 명시한다.
- `yellow`: 더 큰 GPU 확장 전에 CMC de-risking 또는 구조 수정 후보로 보낸다.
- `red`: manuscript lead claim에서 제외하고 failure-mode 또는 redesign 후보로만 쓴다.
