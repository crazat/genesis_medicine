# Modality and IP/Novelty Gate

- timestamp: `2026-05-06T12:46:35+09:00`
- modality_targets: `31`
- candidate_rows: `112`
- purpose: small-molecule docking 일변도에서 벗어나 target별 적합 modality와 local novelty risk를 분리한다.

## Target Modality Matrix

| target | gate | primary modality | degrader/glue | biologic |
|---|---|---|---|---|
| CTGF | green | small_molecule_topical | not_primary | possible |
| CTNNB1 | yellow | phenotype_assay_first | not_primary | not_primary |
| FGF2 | yellow | pathway_modulator_or_biologic | not_primary | possible |
| LOX | green | small_molecule_topical | not_primary | not_primary |
| MMP1 | green | small_molecule_topical | not_primary | not_primary |
| TGFB1 | yellow | small_molecule_topical | not_primary | possible |
| VEGFA | yellow | pathway_modulator_or_biologic | not_primary | possible |
| DCT | green | small_molecule_topical | not_primary | not_primary |
| F2RL1 | yellow | small_molecule_topical | not_primary | not_primary |
| MC1R | green | small_molecule_topical | not_primary | not_primary |
| MITF | yellow | phenotype_assay_first | not_primary | not_primary |
| NR3C1 | green | pathway_modulator_or_biologic | possible_low_priority | not_primary |
| TYR | green | small_molecule_topical | not_primary | not_primary |
| TYRP1 | green | small_molecule_topical | not_primary | not_primary |
| AR | green | small_molecule_topical | possible_low_priority | not_primary |
| MYLK | yellow | small_molecule_topical | not_primary | not_primary |
| PIEZO1 | green | small_molecule_topical | not_primary | not_primary |
| PTGDR2 | red | small_molecule_topical | not_primary | not_primary |
| SRD5A1 | green | small_molecule_topical | not_primary | not_primary |
| SRD5A2 | green | small_molecule_topical | not_primary | not_primary |
| WNT10B | red | pathway_modulator_or_biologic | not_primary | not_primary |
| NLRP3 | red | small_molecule_topical | not_primary | not_primary |
| PTGS2 | red | small_molecule_topical | possible_low_priority | not_primary |
| RARG | green | pathway_modulator_or_biologic | not_primary | not_primary |
| SREBF1 | red | phenotype_assay_first | not_primary | not_primary |
| TLR2 | red | small_molecule_topical | not_primary | not_primary |
| COL1A1 | yellow | phenotype_assay_first | not_primary | not_primary |
| JUN | yellow | phenotype_assay_first | not_primary | not_primary |
| MMP3 | red | small_molecule_topical | not_primary | not_primary |
| MMP9 | red | small_molecule_topical | not_primary | not_primary |
| SIRT1 | yellow | pathway_modulator_or_biologic | possible_low_priority | not_primary |

## Most Locally Distinct Current Candidates

| candidate | target | source | best local T | novelty gate |
|---|---|---|---:|---|
| NPC321400 |  | npass_xtb_best | 0.115 | locally_distinct |
| NPC57078 |  | npass_xtb_best | 0.13 | locally_distinct |
| NPC301586 |  | npass_xtb_best | 0.13 | locally_distinct |
| NPC184593 |  | npass_xtb_best | 0.138 | locally_distinct |
| NPC237965 |  | npass_xtb_best | 0.138 | locally_distinct |
| NPC328835 |  | npass_xtb_best | 0.147 | locally_distinct |
| NPC314289 |  | npass_xtb_best | 0.148 | locally_distinct |
| NPC325909 |  | npass_xtb_best | 0.148 | locally_distinct |
| NPC248427 |  | npass_xtb_best | 0.153 | locally_distinct |
| NPC88887 |  | npass_xtb_best | 0.154 | locally_distinct |
| NPC157340 |  | npass_xtb_best | 0.154 | locally_distinct |
| NPC280090 |  | npass_xtb_best | 0.158 | locally_distinct |

## Curator Use

- `known_or_close_analog`는 benchmark 또는 validation control로 쓰고 신규성 claim을 피한다.
- `locally_distinct`라도 외부 patent/PubChem/ChEMBL 검색 전에는 IP claim을 하지 않는다.
- hard/indirect target은 docking paper가 아니라 phenotype 또는 modality paper로 전환한다.
