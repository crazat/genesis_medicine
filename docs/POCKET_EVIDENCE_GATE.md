# Pocket Evidence Gate

- timestamp: `2026-05-06T12:46:10+09:00`
- targets: `31`
- priority_counts: `{'high': 12, 'review': 11, 'low': 8}`
- purpose: 정적 cofold/docking을 target tractability와 pocket evidence에 맞춰 제한한다.

## High-priority Direct-pocket Targets

| target | diseases | class | next action |
|---|---|---|---|
| AR | acne_vulgaris;androgenetic_alopecia | direct_pocket_plausible | cofold/docking/MD allowed if target gate is green |
| DCT | pigmentation_melasma | direct_pocket_plausible | cofold/docking/MD allowed if target gate is green |
| LOX | scar_regeneration | direct_pocket_plausible | cofold/docking/MD allowed if target gate is green |
| MC1R | pigmentation_melasma | direct_pocket_plausible | cofold/docking/MD allowed if target gate is green |
| MMP1 | photoaging;scar_regeneration | direct_pocket_plausible | cofold/docking/MD allowed if target gate is green |
| NR3C1 | pigmentation_melasma | direct_pocket_plausible | cofold/docking/MD allowed if target gate is green |
| PIEZO1 | androgenetic_alopecia | direct_pocket_plausible | cofold/docking/MD allowed if target gate is green |
| RARG | acne_vulgaris | direct_pocket_plausible | cofold/docking/MD allowed if target gate is green |
| SRD5A1 | androgenetic_alopecia | direct_pocket_plausible | cofold/docking/MD allowed if target gate is green |
| SRD5A2 | acne_vulgaris;androgenetic_alopecia | direct_pocket_plausible | cofold/docking/MD allowed if target gate is green |
| TYR | pigmentation_melasma | direct_pocket_plausible | cofold/docking/MD allowed if target gate is green |
| TYRP1 | pigmentation_melasma | direct_pocket_plausible | cofold/docking/MD allowed if target gate is green |

## Review/Low Targets

| target | target gate | class | risk |
|---|---|---|---|
| COL1A1 | yellow | hard_or_indirect | small-molecule pocket claim weak |
| CTGF | green | interface_or_biologic | secreted/interface target, small pocket may be noncanonical |
| CTNNB1 | yellow | hard_or_indirect | small-molecule pocket claim weak |
| F2RL1 | yellow | direct_pocket_plausible | standard pose and MD validation still required |
| FGF2 | yellow | interface_or_biologic | secreted/interface target, small pocket may be noncanonical |
| JUN | yellow | hard_or_indirect | small-molecule pocket claim weak |
| MITF | yellow | hard_or_indirect | small-molecule pocket claim weak |
| MMP3 | red | direct_pocket_plausible | standard pose and MD validation still required |
| MMP9 | red | direct_pocket_plausible | standard pose and MD validation still required |
| MYLK | yellow | direct_pocket_plausible | standard pose and MD validation still required |
| NLRP3 | red | direct_pocket_plausible | standard pose and MD validation still required |
| PTGDR2 | red | unknown | binding site not established |
| PTGS2 | red | direct_pocket_plausible | standard pose and MD validation still required |
| SIRT1 | yellow | unknown | binding site not established |
| SREBF1 | red | hard_or_indirect | small-molecule pocket claim weak |
| TGFB1 | yellow | interface_or_biologic | secreted/interface target, small pocket may be noncanonical |
| TLR2 | red | direct_pocket_plausible | standard pose and MD validation still required |
| VEGFA | yellow | interface_or_biologic | secreted/interface target, small pocket may be noncanonical |
| WNT10B | red | hard_or_indirect | small-molecule pocket claim weak |

## Curator Use

- `high`만 신규 blind cofold/MD 확장을 우선한다.
- `interface_or_biologic`은 small-molecule docking claim을 약하게 쓰고 wet-lab phenotype 또는 biologic modality로 연결한다.
- `hard_or_indirect`은 virtual-cell/Cell Painting/endpoint assay 쪽으로 전환한다.
