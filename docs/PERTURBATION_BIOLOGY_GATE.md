# Perturbation Biology Gate

- timestamp: `2026-05-06T12:46:32+09:00`
- target_rows: `32`
- priority_counts: `{'high': 2, 'review': 12, 'low': 18}`
- purpose: direct binding 후보를 실제 피부 cell phenotype/perturbation evidence와 연결할 수 있는지 평가한다.

## Priority Targets

| target | priority | cells | target gate | high-confidence pairs | next |
|---|---|---|---|---:|---|
| dct | high | melanocyte | green | 2 | connect candidate to LINCS/Geneformer/scGPT or wet-lab phenotype endpoint |
| tyr | high | melanocyte | green | 2 | connect candidate to LINCS/Geneformer/scGPT or wet-lab phenotype endpoint |
| ar | review | dermal_papilla_cell;hair_follicle_keratinocyte;immune_cell;keratinocyte;sebocyte | green | 0 | collect cell-type perturbation evidence before strong target claim |
| ctgf | review | dermal_fibroblast | green | 0 | collect cell-type perturbation evidence before strong target claim |
| lox | review | dermal_fibroblast | green | 0 | collect cell-type perturbation evidence before strong target claim |
| mc1r | review | melanocyte | green | 0 | collect cell-type perturbation evidence before strong target claim |
| mmp1 | review | dermal_fibroblast;keratinocyte | green | 0 | collect cell-type perturbation evidence before strong target claim |
| nr3c1 | review | melanocyte | green | 0 | collect cell-type perturbation evidence before strong target claim |
| piezo1 | review | dermal_papilla_cell;hair_follicle_keratinocyte | green | 0 | collect cell-type perturbation evidence before strong target claim |
| rarg | review | immune_cell;keratinocyte;sebocyte | green | 0 | collect cell-type perturbation evidence before strong target claim |
| srd5a1 | review | dermal_papilla_cell;hair_follicle_keratinocyte | green | 0 | collect cell-type perturbation evidence before strong target claim |
| srd5a2 | review | dermal_papilla_cell;hair_follicle_keratinocyte;immune_cell;keratinocyte;sebocyte | green | 0 | collect cell-type perturbation evidence before strong target claim |
| tgfb1 | review | dermal_fibroblast | yellow | 2 | collect cell-type perturbation evidence before strong target claim |
| tyrp1 | review | melanocyte | green | 0 | collect cell-type perturbation evidence before strong target claim |
| col1a1 | low | dermal_fibroblast;keratinocyte | yellow | 0 | do not prioritize virtual-cell follow-up yet |
| ctnnb1 | low | dermal_fibroblast;dermal_papilla_cell;hair_follicle_keratinocyte | yellow | 0 | do not prioritize virtual-cell follow-up yet |
| f2rl1 | low | melanocyte | yellow | 0 | do not prioritize virtual-cell follow-up yet |
| fgf2 | low | dermal_fibroblast | yellow | 0 | do not prioritize virtual-cell follow-up yet |
| jun | low | dermal_fibroblast;keratinocyte | yellow | 0 | do not prioritize virtual-cell follow-up yet |
| mitf | low | melanocyte | yellow | 0 | do not prioritize virtual-cell follow-up yet |
| mmp3 | low | dermal_fibroblast;keratinocyte | red | 0 | do not prioritize virtual-cell follow-up yet |
| mmp9 | low | dermal_fibroblast;keratinocyte | red | 0 | do not prioritize virtual-cell follow-up yet |
| mylk | low | dermal_papilla_cell;hair_follicle_keratinocyte | yellow | 0 | do not prioritize virtual-cell follow-up yet |
| nlrp3 | low | immune_cell;keratinocyte;sebocyte | red | 0 | do not prioritize virtual-cell follow-up yet |
| ptgdr2 | low | dermal_papilla_cell;hair_follicle_keratinocyte | red | 0 | do not prioritize virtual-cell follow-up yet |

## Curator Rule

- `high` target은 cofold/MD 결과를 wet-lab phenotype 또는 perturbation signature plan과 연결한다.
- `review` target은 direct binding claim보다 hypothesis 수준으로 낮춘다.
- `low` target은 heavy compute보다 target evidence 보강이 먼저다.
