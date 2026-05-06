# Photosafety Sensitization V2

- timestamp: `2026-05-06T12:46:12+09:00`
- rows: `1082`
- gate_counts: `{'green': 366, 'yellow': 716, 'red': 0}`
- purpose: topical lead claim 전에 OECD TG497 skin sensitization과 ICH S10 photosafety 관점의 assay package를 자동 지정한다.

## Top Safety Rows

| candidate | target | gate | cLogP | sensitization | photosafety | assay |
|---|---|---|---:|---|---|---|
| NPC42783 | nan | green | 2.482 | none_detected | none_detected | baseline_irritation_IVRT_IVPT_panel |
| NPC323980 | nan | green | 2.089 | none_detected | none_detected | baseline_irritation_IVRT_IVPT_panel |
| NPC184593 | nan | green | 1.405 | none_detected | none_detected | baseline_irritation_IVRT_IVPT_panel |
| NPC249078 | nan | green | 2.725 | none_detected | none_detected | baseline_irritation_IVRT_IVPT_panel |
| NPC314289 | nan | green | 1.184 | none_detected | none_detected | baseline_irritation_IVRT_IVPT_panel |
| NPC302293 | nan | green | 1.695 | none_detected | none_detected | baseline_irritation_IVRT_IVPT_panel |
| NPC193781 | nan | green | 1.696 | none_detected | none_detected | baseline_irritation_IVRT_IVPT_panel |
| NPC325130 | nan | green | 1.184 | none_detected | none_detected | baseline_irritation_IVRT_IVPT_panel |
| NPC241081 | nan | green | 2.722 | none_detected | none_detected | baseline_irritation_IVRT_IVPT_panel |
| NPC195282 | nan | green | 2.725 | none_detected | none_detected | baseline_irritation_IVRT_IVPT_panel |
| NPC475968 | nan | green | 1.943 | none_detected | none_detected | baseline_irritation_IVRT_IVPT_panel |
| NPC77156 | nan | green | 1.071 | none_detected | none_detected | baseline_irritation_IVRT_IVPT_panel |
| NPC329253 | nan | green | 2.987 | none_detected | none_detected | baseline_irritation_IVRT_IVPT_panel |
| NPC59871 | nan | green | 2.708 | none_detected | none_detected | baseline_irritation_IVRT_IVPT_panel |
| NPC196715 | nan | green | 2.987 | none_detected | none_detected | baseline_irritation_IVRT_IVPT_panel |
| NPC107271 | nan | green | 1.958 | none_detected | none_detected | baseline_irritation_IVRT_IVPT_panel |
| NPC33067 | nan | green | 1.08 | none_detected | none_detected | baseline_irritation_IVRT_IVPT_panel |
| NPC261839 | nan | green | 2.281 | none_detected | none_detected | baseline_irritation_IVRT_IVPT_panel |
| NPC168128 | nan | green | 1.203 | none_detected | none_detected | baseline_irritation_IVRT_IVPT_panel |
| NPC254230 | nan | green | 1.201 | none_detected | none_detected | baseline_irritation_IVRT_IVPT_panel |
| NPC25947 | nan | green | 3.31 | none_detected | none_detected | baseline_irritation_IVRT_IVPT_panel |
| NPC329473 | nan | green | 2.345 | none_detected | none_detected | baseline_irritation_IVRT_IVPT_panel |
| NPC228980 | nan | green | 2.345 | none_detected | none_detected | baseline_irritation_IVRT_IVPT_panel |
| chromanol_arom9+arom10_Me+Me_tgfb1 | tgfb1 | green | 1.552 | none_detected | none_detected | baseline_irritation_IVRT_IVPT_panel |
| chromanol_arom6+arom9_Me+Me_tgfb1 | tgfb1 | green | 1.552 | none_detected | none_detected | baseline_irritation_IVRT_IVPT_panel |
| chromanol_arom9_Me_tgfb1 | tgfb1 | green | 1.244 | none_detected | none_detected | baseline_irritation_IVRT_IVPT_panel |
| chromanol_arom10_Me_tgfb1 | tgfb1 | green | 1.244 | none_detected | none_detected | baseline_irritation_IVRT_IVPT_panel |
| chromanol_arom6+arom10_Me+Me_tgfb1 | tgfb1 | green | 1.552 | none_detected | none_detected | baseline_irritation_IVRT_IVPT_panel |
| chromanol_arom9_F_tgfb1 | tgfb1 | green | 1.075 | none_detected | none_detected | baseline_irritation_IVRT_IVPT_panel |
| chromanol_arom6+arom9_F+Me_tgfb1 | tgfb1 | green | 1.383 | none_detected | none_detected | baseline_irritation_IVRT_IVPT_panel |
| chromanol_arom6+arom9_Me+F_tgfb1 | tgfb1 | green | 1.383 | none_detected | none_detected | baseline_irritation_IVRT_IVPT_panel |
| chromanol_arom9+arom10_F+Me_tgfb1 | tgfb1 | green | 1.383 | none_detected | none_detected | baseline_irritation_IVRT_IVPT_panel |
| chromanol_arom9+arom10_Me+F_tgfb1 | tgfb1 | green | 1.383 | none_detected | none_detected | baseline_irritation_IVRT_IVPT_panel |
| chromanol_arom6_Me_tgfb1 | tgfb1 | green | 1.244 | none_detected | none_detected | baseline_irritation_IVRT_IVPT_panel |
| chromanol_arom6+arom9_Me+OMe_tgfb1 | tgfb1 | green | 1.253 | none_detected | none_detected | baseline_irritation_IVRT_IVPT_panel |

## Curator Rule

- `green`: lead table 가능하지만 in-silico safety pre-gate로만 표현한다.
- `yellow`: photosafety/sensitization assay package를 논문 limitation과 CRO card에 붙인다.
- `red`: topical lead claim에서 제외한다.
