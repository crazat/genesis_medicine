# Skin Spatial Atlas Gate

- timestamp: `2026-05-06T12:46:28+09:00`
- rows: `32`
- gate_counts: `{'spatially_anchorable': 2, 'atlas_review': 9, 'spatial_context_missing': 21}`
- purpose: 피부 target claim을 세포 상태뿐 아니라 anatomic site, niche, reconstructed model로 연결한다.

## Spatial Anchors

| target | gate | disease | niche | cells | assay model | next |
|---|---|---|---|---|---|---|
| dct | spatially_anchorable | pigment | melanocyte_unit;hair_follicle_pigment_unit | melanocyte;melanosome_state | melanocyte melanin and DCT/TYR/TYRP1 panel | use site/cell/niche table in target-focused manuscript and CRO card |
| tyr | spatially_anchorable | pigment | melanocyte_unit;hair_follicle_pigment_unit | melanocyte;melanosome_state | tyrosinase activity and melanin content | use site/cell/niche table in target-focused manuscript and CRO card |
| ar | atlas_review | alopecia;acne | hair_follicle;sebaceous_gland | dermal_papilla_cell;sebocyte | androgen reporter in DPC/sebocyte context | add human skin atlas or disease-site literature before strong target claim |
| ctgf | atlas_review | scar | reticular_dermis;wound_edge | activated_fibroblast | scar fibroblast or collagen gel contraction | add human skin atlas or disease-site literature before strong target claim |
| lox | atlas_review | scar;photoaging | reticular_dermis;ECM_stroma | dermal_fibroblast | matrix stiffness/collagen crosslinking assay | add human skin atlas or disease-site literature before strong target claim |
| mc1r | atlas_review | pigment | melanocyte_unit | melanocyte | cAMP/pigment response assay | add human skin atlas or disease-site literature before strong target claim |
| mmp1 | atlas_review | photoaging;scar | papillary_dermis;photoexposed_skin | photoaged_fibroblast | UV-aged fibroblast or dermal equivalent | add human skin atlas or disease-site literature before strong target claim |
| nr3c1 | atlas_review | acne;photoaging | epidermis;immune_niche | keratinocyte;immune_cell | glucocorticoid response and barrier marker panel | add human skin atlas or disease-site literature before strong target claim |
| ptgs2 | atlas_review | acne;photoaging | epidermis;sebaceous_unit;immune_niche | keratinocyte;sebocyte;immune_cell | PGE2/cytokine panel | add human skin atlas or disease-site literature before strong target claim |
| tgfb1 | atlas_review | scar;photoaging | reticular_dermis;perivascular_stroma | activated_fibroblast;myofibroblast | scar biopsy or fibroblast-rich reconstructed skin | add human skin atlas or disease-site literature before strong target claim |
| tyrp1 | atlas_review | pigment | melanocyte_unit;hair_follicle_pigment_unit | melanocyte;melanosome_state | melanosome maturation panel | add human skin atlas or disease-site literature before strong target claim |
| col1a1 | spatial_context_missing | unknown | atlas_context_missing | skin_cell_context_missing | define anatomic site and disease-cell model | keep exploratory until target is mapped to skin anatomic niche |
| ctnnb1 | spatial_context_missing | unknown | atlas_context_missing | skin_cell_context_missing | define anatomic site and disease-cell model | keep exploratory until target is mapped to skin anatomic niche |
| f2rl1 | spatial_context_missing | unknown | atlas_context_missing | skin_cell_context_missing | define anatomic site and disease-cell model | keep exploratory until target is mapped to skin anatomic niche |
| fgf2 | spatial_context_missing | unknown | atlas_context_missing | skin_cell_context_missing | define anatomic site and disease-cell model | keep exploratory until target is mapped to skin anatomic niche |
| jun | spatial_context_missing | unknown | atlas_context_missing | skin_cell_context_missing | define anatomic site and disease-cell model | keep exploratory until target is mapped to skin anatomic niche |
| mitf | spatial_context_missing | unknown | atlas_context_missing | skin_cell_context_missing | define anatomic site and disease-cell model | keep exploratory until target is mapped to skin anatomic niche |
| mmp3 | spatial_context_missing | unknown | atlas_context_missing | skin_cell_context_missing | define anatomic site and disease-cell model | keep exploratory until target is mapped to skin anatomic niche |
| mmp9 | spatial_context_missing | unknown | atlas_context_missing | skin_cell_context_missing | define anatomic site and disease-cell model | keep exploratory until target is mapped to skin anatomic niche |
| mylk | spatial_context_missing | unknown | atlas_context_missing | skin_cell_context_missing | define anatomic site and disease-cell model | keep exploratory until target is mapped to skin anatomic niche |
| nlrp3 | spatial_context_missing | unknown | atlas_context_missing | skin_cell_context_missing | define anatomic site and disease-cell model | keep exploratory until target is mapped to skin anatomic niche |
| piezo1 | spatial_context_missing | unknown | atlas_context_missing | skin_cell_context_missing | define anatomic site and disease-cell model | keep exploratory until target is mapped to skin anatomic niche |
| ptgdr2 | spatial_context_missing | unknown | atlas_context_missing | skin_cell_context_missing | define anatomic site and disease-cell model | keep exploratory until target is mapped to skin anatomic niche |
| rarg | spatial_context_missing | unknown | atlas_context_missing | skin_cell_context_missing | define anatomic site and disease-cell model | keep exploratory until target is mapped to skin anatomic niche |
| sirt1 | spatial_context_missing | unknown | atlas_context_missing | skin_cell_context_missing | define anatomic site and disease-cell model | keep exploratory until target is mapped to skin anatomic niche |
| srd5a1 | spatial_context_missing | unknown | atlas_context_missing | skin_cell_context_missing | define anatomic site and disease-cell model | keep exploratory until target is mapped to skin anatomic niche |
| srd5a2 | spatial_context_missing | unknown | atlas_context_missing | skin_cell_context_missing | define anatomic site and disease-cell model | keep exploratory until target is mapped to skin anatomic niche |
| srebf1 | spatial_context_missing | unknown | atlas_context_missing | skin_cell_context_missing | define anatomic site and disease-cell model | keep exploratory until target is mapped to skin anatomic niche |
| srebp1 | spatial_context_missing | unknown | atlas_context_missing | skin_cell_context_missing | define anatomic site and disease-cell model | keep exploratory until target is mapped to skin anatomic niche |
| tlr2 | spatial_context_missing | unknown | atlas_context_missing | skin_cell_context_missing | define anatomic site and disease-cell model | keep exploratory until target is mapped to skin anatomic niche |
| vegfa | spatial_context_missing | unknown | atlas_context_missing | skin_cell_context_missing | define anatomic site and disease-cell model | keep exploratory until target is mapped to skin anatomic niche |
| wnt10b | spatial_context_missing | unknown | atlas_context_missing | skin_cell_context_missing | define anatomic site and disease-cell model | keep exploratory until target is mapped to skin anatomic niche |

## Curator Rule

- `spatially_anchorable`: target-focused paper에 skin site/cell/niche figure 또는 table을 넣는다.
- `atlas_review`: 추가 docking보다 atlas/literature anchor 보강이 우선이다.
- `spatial_context_missing`: direct dermatology target claim을 제한한다.
