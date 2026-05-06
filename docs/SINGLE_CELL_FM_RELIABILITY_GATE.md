# Single-Cell FM Reliability Gate

- timestamp: `2026-05-06T12:46:31+09:00`
- rows: `32`
- gate_counts: `{'fm_supported_with_controls': 2, 'zero_shot_reliability_review': 12, 'fm_not_actionable': 18}`
- purpose: scGPT/Geneformer/virtual-cell style evidence를 zero-shot limitation과 baseline-control 요구사항으로 제한한다.

## FM Reliability Rows

| target | gate | cells | perturbation | spatial | controls | next |
|---|---|---|---|---|---|---|
| dct | fm_supported_with_controls | melanocyte | high | spatially_anchorable | zero-shot baseline;cell-type proximity;batch/domain check;simpler model comparison;wet-lab endpoint caveat | allow virtual-cell/phenomics hypothesis with simple-baseline and wet-lab caveat |
| tyr | fm_supported_with_controls | melanocyte | high | spatially_anchorable | zero-shot baseline;cell-type proximity;batch/domain check;simpler model comparison;wet-lab endpoint caveat | allow virtual-cell/phenomics hypothesis with simple-baseline and wet-lab caveat |
| ar | zero_shot_reliability_review | dermal_papilla_cell;hair_follicle_keratinocyte;immune_cell;keratinocyte;sebocyte | review | atlas_review | zero-shot baseline;cell-type proximity;batch/domain check;simpler model comparison;wet-lab endpoint caveat | require cell-type match, fine-tuning/proximity check, and simpler-baseline comparison |
| ctgf | zero_shot_reliability_review | dermal_fibroblast | review | atlas_review | zero-shot baseline;cell-type proximity;batch/domain check;simpler model comparison;wet-lab endpoint caveat | require cell-type match, fine-tuning/proximity check, and simpler-baseline comparison |
| lox | zero_shot_reliability_review | dermal_fibroblast | review | atlas_review | zero-shot baseline;cell-type proximity;batch/domain check;simpler model comparison;wet-lab endpoint caveat | require cell-type match, fine-tuning/proximity check, and simpler-baseline comparison |
| mc1r | zero_shot_reliability_review | melanocyte | review | atlas_review | zero-shot baseline;cell-type proximity;batch/domain check;simpler model comparison;wet-lab endpoint caveat | require cell-type match, fine-tuning/proximity check, and simpler-baseline comparison |
| mmp1 | zero_shot_reliability_review | dermal_fibroblast;keratinocyte | review | atlas_review | zero-shot baseline;cell-type proximity;batch/domain check;simpler model comparison;wet-lab endpoint caveat | require cell-type match, fine-tuning/proximity check, and simpler-baseline comparison |
| nr3c1 | zero_shot_reliability_review | melanocyte | review | atlas_review | zero-shot baseline;cell-type proximity;batch/domain check;simpler model comparison;wet-lab endpoint caveat | require cell-type match, fine-tuning/proximity check, and simpler-baseline comparison |
| piezo1 | zero_shot_reliability_review | dermal_papilla_cell;hair_follicle_keratinocyte | review | spatial_context_missing | zero-shot baseline;cell-type proximity;batch/domain check;simpler model comparison;wet-lab endpoint caveat | require cell-type match, fine-tuning/proximity check, and simpler-baseline comparison |
| rarg | zero_shot_reliability_review | immune_cell;keratinocyte;sebocyte | review | spatial_context_missing | zero-shot baseline;cell-type proximity;batch/domain check;simpler model comparison;wet-lab endpoint caveat | require cell-type match, fine-tuning/proximity check, and simpler-baseline comparison |
| srd5a1 | zero_shot_reliability_review | dermal_papilla_cell;hair_follicle_keratinocyte | review | spatial_context_missing | zero-shot baseline;cell-type proximity;batch/domain check;simpler model comparison;wet-lab endpoint caveat | require cell-type match, fine-tuning/proximity check, and simpler-baseline comparison |
| srd5a2 | zero_shot_reliability_review | dermal_papilla_cell;hair_follicle_keratinocyte;immune_cell;keratinocyte;sebocyte | review | spatial_context_missing | zero-shot baseline;cell-type proximity;batch/domain check;simpler model comparison;wet-lab endpoint caveat | require cell-type match, fine-tuning/proximity check, and simpler-baseline comparison |
| tgfb1 | zero_shot_reliability_review | dermal_fibroblast | review | atlas_review | zero-shot baseline;cell-type proximity;batch/domain check;simpler model comparison;wet-lab endpoint caveat | require cell-type match, fine-tuning/proximity check, and simpler-baseline comparison |
| tyrp1 | zero_shot_reliability_review | melanocyte | review | atlas_review | zero-shot baseline;cell-type proximity;batch/domain check;simpler model comparison;wet-lab endpoint caveat | require cell-type match, fine-tuning/proximity check, and simpler-baseline comparison |
| col1a1 | fm_not_actionable | dermal_fibroblast;keratinocyte | low | spatial_context_missing | zero-shot baseline;cell-type proximity;batch/domain check;simpler model comparison;wet-lab endpoint caveat | do not use single-cell FM for target claim yet |
| ctnnb1 | fm_not_actionable | dermal_fibroblast;dermal_papilla_cell;hair_follicle_keratinocyte | low | spatial_context_missing | zero-shot baseline;cell-type proximity;batch/domain check;simpler model comparison;wet-lab endpoint caveat | do not use single-cell FM for target claim yet |
| f2rl1 | fm_not_actionable | melanocyte | low | spatial_context_missing | zero-shot baseline;cell-type proximity;batch/domain check;simpler model comparison;wet-lab endpoint caveat | do not use single-cell FM for target claim yet |
| fgf2 | fm_not_actionable | dermal_fibroblast | low | spatial_context_missing | zero-shot baseline;cell-type proximity;batch/domain check;simpler model comparison;wet-lab endpoint caveat | do not use single-cell FM for target claim yet |
| jun | fm_not_actionable | dermal_fibroblast;keratinocyte | low | spatial_context_missing | zero-shot baseline;cell-type proximity;batch/domain check;simpler model comparison;wet-lab endpoint caveat | do not use single-cell FM for target claim yet |
| mitf | fm_not_actionable | melanocyte | low | spatial_context_missing | zero-shot baseline;cell-type proximity;batch/domain check;simpler model comparison;wet-lab endpoint caveat | do not use single-cell FM for target claim yet |
| mmp3 | fm_not_actionable | dermal_fibroblast;keratinocyte | low | spatial_context_missing | zero-shot baseline;cell-type proximity;batch/domain check;simpler model comparison;wet-lab endpoint caveat | do not use single-cell FM for target claim yet |
| mmp9 | fm_not_actionable | dermal_fibroblast;keratinocyte | low | spatial_context_missing | zero-shot baseline;cell-type proximity;batch/domain check;simpler model comparison;wet-lab endpoint caveat | do not use single-cell FM for target claim yet |
| mylk | fm_not_actionable | dermal_papilla_cell;hair_follicle_keratinocyte | low | spatial_context_missing | zero-shot baseline;cell-type proximity;batch/domain check;simpler model comparison;wet-lab endpoint caveat | do not use single-cell FM for target claim yet |
| nlrp3 | fm_not_actionable | immune_cell;keratinocyte;sebocyte | low | spatial_context_missing | zero-shot baseline;cell-type proximity;batch/domain check;simpler model comparison;wet-lab endpoint caveat | do not use single-cell FM for target claim yet |
| ptgdr2 | fm_not_actionable | dermal_papilla_cell;hair_follicle_keratinocyte | low | spatial_context_missing | zero-shot baseline;cell-type proximity;batch/domain check;simpler model comparison;wet-lab endpoint caveat | do not use single-cell FM for target claim yet |
| ptgs2 | fm_not_actionable | immune_cell;keratinocyte;sebocyte | low | atlas_review | zero-shot baseline;cell-type proximity;batch/domain check;simpler model comparison;wet-lab endpoint caveat | do not use single-cell FM for target claim yet |
| sirt1 | fm_not_actionable | dermal_fibroblast;keratinocyte | low | spatial_context_missing | zero-shot baseline;cell-type proximity;batch/domain check;simpler model comparison;wet-lab endpoint caveat | do not use single-cell FM for target claim yet |
| srebf1 | fm_not_actionable | immune_cell;keratinocyte;sebocyte | low | spatial_context_missing | zero-shot baseline;cell-type proximity;batch/domain check;simpler model comparison;wet-lab endpoint caveat | do not use single-cell FM for target claim yet |
| srebp1 | fm_not_actionable | missing | low | spatial_context_missing | zero-shot baseline;cell-type proximity;batch/domain check;simpler model comparison;wet-lab endpoint caveat | do not use single-cell FM for target claim yet |
| tlr2 | fm_not_actionable | immune_cell;keratinocyte;sebocyte | low | spatial_context_missing | zero-shot baseline;cell-type proximity;batch/domain check;simpler model comparison;wet-lab endpoint caveat | do not use single-cell FM for target claim yet |
| vegfa | fm_not_actionable | dermal_fibroblast | low | spatial_context_missing | zero-shot baseline;cell-type proximity;batch/domain check;simpler model comparison;wet-lab endpoint caveat | do not use single-cell FM for target claim yet |
| wnt10b | fm_not_actionable | dermal_papilla_cell;hair_follicle_keratinocyte | low | spatial_context_missing | zero-shot baseline;cell-type proximity;batch/domain check;simpler model comparison;wet-lab endpoint caveat | do not use single-cell FM for target claim yet |

## Curator Rule

- `fm_supported_with_controls`: virtual-cell claim은 hypothesis로만 쓰고 baseline-control을 명시한다.
- `zero_shot_reliability_review`: fine-tuning/proximity/simple baseline 없이는 manuscript main claim 금지.
- `fm_not_actionable`: 추가 docking보다 target/cell evidence 보강이 먼저다.
