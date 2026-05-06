# Metabolite Reactive Risk Gate

- timestamp: `2026-05-06T12:46:29+09:00`
- rows: `1082`
- gate_counts: `{'low_reactive_alert': 720, 'metabolism_caveat': 352, 'reactive_metabolite_review': 10, 'structure_fix': 0}`
- purpose: BioTransformer/FAME류 대사체 예측 전 단계로 phenol/redox/quinone/aryl-halogen/reactive-metabolite risk를 표시한다.

## Metabolism Risk Rows

| candidate | target | gate | alerts | metabolism | next |
|---|---|---|---|---|---|
| NPC42783 | nan | low_reactive_alert | none_detected | standard phase I/II screen | standard metabolite prediction before wet-lab package |
| NPC213764 | nan | low_reactive_alert | none_detected | standard phase I/II screen | standard metabolite prediction before wet-lab package |
| NPC236761 | nan | low_reactive_alert | none_detected | standard phase I/II screen | standard metabolite prediction before wet-lab package |
| NPC88887 | nan | low_reactive_alert | none_detected | standard phase I/II screen | standard metabolite prediction before wet-lab package |
| NPC149567 | nan | low_reactive_alert | none_detected | standard phase I/II screen | standard metabolite prediction before wet-lab package |
| NPC323980 | nan | low_reactive_alert | none_detected | standard phase I/II screen | standard metabolite prediction before wet-lab package |
| NPC283633 | nan | low_reactive_alert | none_detected | standard phase I/II screen | standard metabolite prediction before wet-lab package |
| NPC184593 | nan | low_reactive_alert | none_detected | standard phase I/II screen | standard metabolite prediction before wet-lab package |
| NPC249078 | nan | low_reactive_alert | none_detected | standard phase I/II screen | standard metabolite prediction before wet-lab package |
| NPC306277 | nan | low_reactive_alert | none_detected | standard phase I/II screen | standard metabolite prediction before wet-lab package |
| NPC314289 | nan | low_reactive_alert | none_detected | standard phase I/II screen | standard metabolite prediction before wet-lab package |
| NPC157340 | nan | low_reactive_alert | none_detected | standard phase I/II screen | standard metabolite prediction before wet-lab package |
| NPC302293 | nan | low_reactive_alert | none_detected | standard phase I/II screen | standard metabolite prediction before wet-lab package |
| NPC244869 | nan | low_reactive_alert | none_detected | standard phase I/II screen | standard metabolite prediction before wet-lab package |
| NPC321253 | nan | low_reactive_alert | none_detected | standard phase I/II screen | standard metabolite prediction before wet-lab package |
| NPC36877 | nan | low_reactive_alert | none_detected | standard phase I/II screen | standard metabolite prediction before wet-lab package |
| NPC193781 | nan | low_reactive_alert | none_detected | standard phase I/II screen | standard metabolite prediction before wet-lab package |
| NPC325130 | nan | low_reactive_alert | none_detected | standard phase I/II screen | standard metabolite prediction before wet-lab package |
| NPC195282 | nan | low_reactive_alert | none_detected | standard phase I/II screen | standard metabolite prediction before wet-lab package |
| NPC475968 | nan | low_reactive_alert | none_detected | standard phase I/II screen | standard metabolite prediction before wet-lab package |
| NPC321400 | nan | low_reactive_alert | none_detected | standard phase I/II screen | standard metabolite prediction before wet-lab package |
| NPC73764 | nan | low_reactive_alert | none_detected | standard phase I/II screen | standard metabolite prediction before wet-lab package |
| NPC77156 | nan | low_reactive_alert | none_detected | standard phase I/II screen | standard metabolite prediction before wet-lab package |
| NPC57078 | nan | low_reactive_alert | none_detected | standard phase I/II screen | standard metabolite prediction before wet-lab package |
| NPC301586 | nan | low_reactive_alert | none_detected | standard phase I/II screen | standard metabolite prediction before wet-lab package |
| NPC237965 | nan | low_reactive_alert | none_detected | standard phase I/II screen | standard metabolite prediction before wet-lab package |
| NPC196715 | nan | low_reactive_alert | none_detected | standard phase I/II screen | standard metabolite prediction before wet-lab package |
| NPC33067 | nan | low_reactive_alert | none_detected | standard phase I/II screen | standard metabolite prediction before wet-lab package |
| NPC261839 | nan | low_reactive_alert | none_detected | standard phase I/II screen | standard metabolite prediction before wet-lab package |
| NPC328835 | nan | low_reactive_alert | none_detected | standard phase I/II screen | standard metabolite prediction before wet-lab package |
| NPC248427 | nan | low_reactive_alert | none_detected | standard phase I/II screen | standard metabolite prediction before wet-lab package |
| NPC273019 | nan | low_reactive_alert | none_detected | standard phase I/II screen | standard metabolite prediction before wet-lab package |
| NPC168128 | nan | low_reactive_alert | none_detected | standard phase I/II screen | standard metabolite prediction before wet-lab package |
| NPC254230 | nan | low_reactive_alert | none_detected | standard phase I/II screen | standard metabolite prediction before wet-lab package |
| NPC189862 | nan | low_reactive_alert | none_detected | standard phase I/II screen | standard metabolite prediction before wet-lab package |
| NPC120104 | nan | low_reactive_alert | none_detected | standard phase I/II screen | standard metabolite prediction before wet-lab package |
| NPC23134 | nan | low_reactive_alert | none_detected | standard phase I/II screen | standard metabolite prediction before wet-lab package |
| NPC20938 | nan | low_reactive_alert | none_detected | standard phase I/II screen | standard metabolite prediction before wet-lab package |
| NPC256808 | nan | low_reactive_alert | none_detected | standard phase I/II screen | standard metabolite prediction before wet-lab package |
| NPC296246 | nan | low_reactive_alert | none_detected | standard phase I/II screen | standard metabolite prediction before wet-lab package |
| NPC75037 | nan | low_reactive_alert | none_detected | standard phase I/II screen | standard metabolite prediction before wet-lab package |
| NPC325909 | nan | low_reactive_alert | none_detected | standard phase I/II screen | standard metabolite prediction before wet-lab package |
| NPC196715 | dct | low_reactive_alert | none_detected | standard phase I/II screen | standard metabolite prediction before wet-lab package |
| NPC261839 | dct | low_reactive_alert | none_detected | standard phase I/II screen | standard metabolite prediction before wet-lab package |
| NPC196715 | ctgf | low_reactive_alert | none_detected | standard phase I/II screen | standard metabolite prediction before wet-lab package |

## Curator Rule

- `reactive_metabolite_review`: safety/main lead claim 전에 metabolite prediction 또는 assay caveat를 붙인다.
- `metabolism_caveat`: Phase II/skin metabolism caveat를 논문 limitation에 넣는다.
- `low_reactive_alert`: standard ADMET/MetID follow-up 후보로 유지한다.
