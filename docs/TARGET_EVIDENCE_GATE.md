# Target Evidence Gate

- timestamp: `2026-05-06T12:46:04+09:00`
- targets: `31`
- gate_counts: `{'green': 13, 'red': 8, 'yellow': 10}`
- purpose: 계산 큐를 질병/피부 근거, tractability, modality에 연결해 무의미한 docking 확장을 줄인다.

## Gate Meaning

- `green`: disease/skin evidence와 small-molecule 또는 topical modality가 비교적 직접적이다.
- `yellow`: 계산은 가능하지만 phenotype, cell atlas, wet-lab endpoint 또는 modality caveat가 필요하다.
- `red`: 현재 근거만으로는 추가 GPU/CPU 확장 우선순위가 낮다.

## Green Targets

| target | diseases | OT max skin | modality | next action |
|---|---|---:|---|---|
| CTGF | scar_regeneration | skin 0.0 / translational 0.329 | small_molecule_or_topical_inhibitor+biologic_possible | broad anti-fibrotic evidence supports scar-program follow-up; avoid skin-specific overclaim |
| LOX | scar_regeneration | skin 0.409 / translational 0.0 | small_molecule_or_topical_inhibitor | skin-evidence supported; prioritize assay endpoint definition |
| MMP1 | photoaging;scar_regeneration | skin 0.612 / translational 0.0 | small_molecule_or_topical_inhibitor | skin-evidence supported; prioritize assay endpoint definition |
| DCT | pigmentation_melasma | skin 0.747 / translational 0.0 | small_molecule_or_topical_inhibitor | cofold/MD or wet-lab endpoint can be prioritized |
| MC1R | pigmentation_melasma | skin 0.717 / translational 0.0 | small_molecule_or_topical_inhibitor | cofold/MD or wet-lab endpoint can be prioritized |
| NR3C1 | pigmentation_melasma | skin 0.604 / translational 0.0 | agonist_or_pathway_modulator | skin-evidence supported; prioritize assay endpoint definition |
| TYR | pigmentation_melasma | skin 0.858 / translational 0.0 | small_molecule_or_topical_inhibitor | cofold/MD or wet-lab endpoint can be prioritized |
| TYRP1 | pigmentation_melasma | skin 0.803 / translational 0.0 | small_molecule_or_topical_inhibitor | cofold/MD or wet-lab endpoint can be prioritized |
| AR | acne_vulgaris;androgenetic_alopecia | skin 0.582 / translational 0.0 | small_molecule_or_topical_inhibitor | cofold/MD or wet-lab endpoint can be prioritized |
| PIEZO1 | androgenetic_alopecia | skin 0.353 / translational 0.0 | small_molecule_or_topical_inhibitor | skin-evidence supported; prioritize assay endpoint definition |
| SRD5A1 | androgenetic_alopecia | skin 0.481 / translational 0.0 | small_molecule_or_topical_inhibitor | cofold/MD or wet-lab endpoint can be prioritized |
| SRD5A2 | acne_vulgaris;androgenetic_alopecia | skin 0.702 / translational 0.0 | small_molecule_or_topical_inhibitor | cofold/MD or wet-lab endpoint can be prioritized |
| RARG | acne_vulgaris | skin 0.609 / translational 0.0 | agonist_or_pathway_modulator | skin-evidence supported; prioritize assay endpoint definition |

## Yellow Targets

| target | diseases | reason | next action |
|---|---|---|---|
| CTNNB1 | androgenetic_alopecia;scar_regeneration | OT skin=0.0; tractability=hard_or_indirect | keep, but require phenotype/cell evidence before strong claims |
| FGF2 | scar_regeneration | OT skin=0.094; tractability=context_dependent | keep, but require phenotype/cell evidence before strong claims |
| TGFB1 | scar_regeneration | OT skin=0.0; tractability=direct | keep, but require phenotype/cell evidence before strong claims |
| VEGFA | scar_regeneration | OT skin=0.0; tractability=context_dependent | keep, but require phenotype/cell evidence before strong claims |
| F2RL1 | pigmentation_melasma | OT skin=0.0; tractability=direct | keep, but require phenotype/cell evidence before strong claims |
| MITF | pigmentation_melasma | OT skin=0.757; tractability=hard_or_indirect | keep, but require phenotype/cell evidence before strong claims |
| MYLK | androgenetic_alopecia | OT skin=0.0; tractability=direct | keep, but require phenotype/cell evidence before strong claims |
| COL1A1 | photoaging | OT skin=0.542; tractability=hard_or_indirect | keep, but require phenotype/cell evidence before strong claims |
| JUN | photoaging | OT skin=0.372; tractability=hard_or_indirect | keep, but require phenotype/cell evidence before strong claims |
| SIRT1 | photoaging | OT skin=0.109; tractability=context_dependent | keep, but require phenotype/cell evidence before strong claims |

## Red Targets

| target | diseases | reason |
|---|---|---|
| PTGDR2 | androgenetic_alopecia | OT skin=0.0; error= |
| WNT10B | androgenetic_alopecia | OT skin=0.038; error= |
| NLRP3 | acne_vulgaris | OT skin=0.0; error= |
| PTGS2 | acne_vulgaris | OT skin=0.0; error= |
| SREBF1 | acne_vulgaris | OT skin=0.0; error= |
| TLR2 | acne_vulgaris | OT skin=0.0; error= |
| MMP3 | photoaging | OT skin=0.0; error= |
| MMP9 | photoaging | OT skin=0.0; error= |

## Curator Use

- GPU cofold/MD 신규 큐는 `green`을 우선한다.
- `yellow`는 phenotype assay, cell-type evidence, 또는 modality 전환 계획이 같이 있어야 논문 claim에 올린다.
- `red`는 atlas/method paper의 negative-control 또는 future-work로만 사용한다.
