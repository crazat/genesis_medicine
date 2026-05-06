# Skin Cell-State Evidence Gate

- timestamp: `2026-05-06T12:46:12+09:00`
- rows: `32`
- gate_counts: `{'cell_state_anchored': 2, 'phenotype_first': 8, 'target_claim_limited': 22}`
- purpose: target/cofold evidence를 실제 피부 세포 상태와 disease phenotype endpoint에 연결한다.

## Target Cell-State Map

| target | gate | disease | cell states | endpoints | next |
|---|---|---|---|---|---|
| dct | cell_state_anchored | pigment | melanocyte;melanosome_state | melanin content, DCT/TYR/TYRP1 expression | write disease-cell endpoint table and CRO assay card |
| tyr | cell_state_anchored | pigment | melanocyte;melanosome_state | tyrosinase activity, melanin content | write disease-cell endpoint table and CRO assay card |
| ar | phenotype_first | alopecia;acne | dermal_papilla_cell;sebocyte | androgen response, hair-cycle marker, sebum marker | prioritize single-cell/spatial/literature anchor before stronger binding claim |
| ctgf | phenotype_first | scar | activated_dermal_fibroblast | CTGF, collagen deposition, fibroblast activation | prioritize single-cell/spatial/literature anchor before stronger binding claim |
| lox | phenotype_first | scar;photoaging | dermal_fibroblast | collagen crosslinking, matrix stiffness | prioritize single-cell/spatial/literature anchor before stronger binding claim |
| mc1r | phenotype_first | pigment | melanocyte | cAMP response, pigmentation phenotype | prioritize single-cell/spatial/literature anchor before stronger binding claim |
| mmp1 | phenotype_first | scar;photoaging | dermal_fibroblast;photoaged_fibroblast | MMP1, COL1A1 rescue, ECM remodeling | prioritize single-cell/spatial/literature anchor before stronger binding claim |
| nr3c1 | phenotype_first | acne;photoaging | keratinocyte;immune_cell | glucocorticoid-response and barrier markers | prioritize single-cell/spatial/literature anchor before stronger binding claim |
| tgfb1 | phenotype_first | scar | activated_dermal_fibroblast;myofibroblast | collagen I/III, alpha-SMA, CTGF, wound contraction | prioritize single-cell/spatial/literature anchor before stronger binding claim |
| tyrp1 | phenotype_first | pigment | melanocyte;melanosome_state | melanosome maturation, melanin content | prioritize single-cell/spatial/literature anchor before stronger binding claim |
| col1a1 | target_claim_limited | unknown | skin_context_missing | define disease-cell phenotype endpoint | keep as exploratory or negative-control target until cell-state evidence exists |
| ctnnb1 | target_claim_limited | unknown | skin_context_missing | define disease-cell phenotype endpoint | keep as exploratory or negative-control target until cell-state evidence exists |
| f2rl1 | target_claim_limited | unknown | skin_context_missing | define disease-cell phenotype endpoint | keep as exploratory or negative-control target until cell-state evidence exists |
| fgf2 | target_claim_limited | unknown | skin_context_missing | define disease-cell phenotype endpoint | keep as exploratory or negative-control target until cell-state evidence exists |
| jun | target_claim_limited | unknown | skin_context_missing | define disease-cell phenotype endpoint | keep as exploratory or negative-control target until cell-state evidence exists |
| mitf | target_claim_limited | unknown | skin_context_missing | define disease-cell phenotype endpoint | keep as exploratory or negative-control target until cell-state evidence exists |
| mmp3 | target_claim_limited | unknown | skin_context_missing | define disease-cell phenotype endpoint | keep as exploratory or negative-control target until cell-state evidence exists |
| mmp9 | target_claim_limited | unknown | skin_context_missing | define disease-cell phenotype endpoint | keep as exploratory or negative-control target until cell-state evidence exists |
| mylk | target_claim_limited | unknown | skin_context_missing | define disease-cell phenotype endpoint | keep as exploratory or negative-control target until cell-state evidence exists |
| nlrp3 | target_claim_limited | unknown | skin_context_missing | define disease-cell phenotype endpoint | keep as exploratory or negative-control target until cell-state evidence exists |
| piezo1 | target_claim_limited | unknown | skin_context_missing | define disease-cell phenotype endpoint | keep as exploratory or negative-control target until cell-state evidence exists |
| ptgdr2 | target_claim_limited | unknown | skin_context_missing | define disease-cell phenotype endpoint | keep as exploratory or negative-control target until cell-state evidence exists |
| ptgs2 | target_claim_limited | acne;photoaging | keratinocyte;immune_cell;sebocyte | PGE2, inflammatory cytokine panel | keep as exploratory or negative-control target until cell-state evidence exists |
| rarg | target_claim_limited | unknown | skin_context_missing | define disease-cell phenotype endpoint | keep as exploratory or negative-control target until cell-state evidence exists |
| sirt1 | target_claim_limited | unknown | skin_context_missing | define disease-cell phenotype endpoint | keep as exploratory or negative-control target until cell-state evidence exists |
| srd5a1 | target_claim_limited | unknown | skin_context_missing | define disease-cell phenotype endpoint | keep as exploratory or negative-control target until cell-state evidence exists |
| srd5a2 | target_claim_limited | unknown | skin_context_missing | define disease-cell phenotype endpoint | keep as exploratory or negative-control target until cell-state evidence exists |
| srebf1 | target_claim_limited | unknown | skin_context_missing | define disease-cell phenotype endpoint | keep as exploratory or negative-control target until cell-state evidence exists |
| srebp1 | target_claim_limited | unknown | skin_context_missing | define disease-cell phenotype endpoint | keep as exploratory or negative-control target until cell-state evidence exists |
| tlr2 | target_claim_limited | unknown | skin_context_missing | define disease-cell phenotype endpoint | keep as exploratory or negative-control target until cell-state evidence exists |
| vegfa | target_claim_limited | unknown | skin_context_missing | define disease-cell phenotype endpoint | keep as exploratory or negative-control target until cell-state evidence exists |
| wnt10b | target_claim_limited | unknown | skin_context_missing | define disease-cell phenotype endpoint | keep as exploratory or negative-control target until cell-state evidence exists |

## Curator Rule

- `cell_state_anchored`: target-focused 논문과 CRO endpoint table에 바로 반영한다.
- `phenotype_first`: 추가 GPU보다 cell phenotype evidence/assay design을 우선한다.
- `target_claim_limited`: direct target efficacy claim을 피하고 exploratory로 둔다.
