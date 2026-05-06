# Target Engagement Assay Gate

- timestamp: `2026-05-06T12:46:28+09:00`
- rows: `32`
- gate_counts: `{'engagement_assay_ready': 1, 'cellular_engagement_preferred': 5, 'deconvolution_first': 13, 'assay_materials_review': 13}`
- purpose: in-silico binding hypothesis를 CETSA/TPP/SPR/reporter/phenotype assay로 넘길 수 있는지 평가한다.

## Engagement Rows

| job | target | compound | gate | modality | assays | next |
|---|---|---|---|---|---|---|
| r16_02_tyr | tyr | R15_chromanol_Cl_pos6 | engagement_assay_ready | enzyme_activity | biochemical tyrosinase activity;cellular melanin content | make wet-lab card with biochemical/cellular target engagement endpoint |
| r16_03_dct | dct | R15_chromanol_Cl_pos9 | cellular_engagement_preferred | cellular_target_context | melanocyte DCT/TYR/TYRP1 expression;melanin phenotype;CETSA if antibody works | prioritize cellular CETSA/reporter/phenotype endpoint over more docking |
| r16_02_dct | dct | R15_chromanol_Cl_pos6 | cellular_engagement_preferred | cellular_target_context | melanocyte DCT/TYR/TYRP1 expression;melanin phenotype;CETSA if antibody works | prioritize cellular CETSA/reporter/phenotype endpoint over more docking |
| r15_chrom_tyr | tyr | R15_chromanol | cellular_engagement_preferred | enzyme_activity | biochemical tyrosinase activity;cellular melanin content | prioritize cellular CETSA/reporter/phenotype endpoint over more docking |
| r15_chrom_dct | dct | R15_chromanol | cellular_engagement_preferred | cellular_target_context | melanocyte DCT/TYR/TYRP1 expression;melanin phenotype;CETSA if antibody works | prioritize cellular CETSA/reporter/phenotype endpoint over more docking |
| r16_01_dct | dct | R15_chromanol_Cl_pos10 | cellular_engagement_preferred | cellular_target_context | melanocyte DCT/TYR/TYRP1 expression;melanin phenotype;CETSA if antibody works | prioritize cellular CETSA/reporter/phenotype endpoint over more docking |
| r16_05_tgfb1 | tgfb1 | R15_chromanol_Me6_Me9 | deconvolution_first | pathway_ligand_context | TGF-beta pathway reporter;pSMAD2/3;SPR/BLI only if direct ligand binding is plausible | treat docking as hypothesis and plan TPP/CETSA-MS or phenotype deconvolution |
| r16_02_tgfb1 | tgfb1 | R15_chromanol_Cl_pos6 | deconvolution_first | pathway_ligand_context | TGF-beta pathway reporter;pSMAD2/3;SPR/BLI only if direct ligand binding is plausible | treat docking as hypothesis and plan TPP/CETSA-MS or phenotype deconvolution |
| r16_03_tgfb1 | tgfb1 | R15_chromanol_Cl_pos9 | deconvolution_first | pathway_ligand_context | TGF-beta pathway reporter;pSMAD2/3;SPR/BLI only if direct ligand binding is plausible | treat docking as hypothesis and plan TPP/CETSA-MS or phenotype deconvolution |
| r16_06_tgfb1 | tgfb1 | R15_chromanol_Me9_Me10 | deconvolution_first | pathway_ligand_context | TGF-beta pathway reporter;pSMAD2/3;SPR/BLI only if direct ligand binding is plausible | treat docking as hypothesis and plan TPP/CETSA-MS or phenotype deconvolution |
| r16_04_tgfb1 | tgfb1 | R15_chromanol_Me6_Me10 | deconvolution_first | pathway_ligand_context | TGF-beta pathway reporter;pSMAD2/3;SPR/BLI only if direct ligand binding is plausible | treat docking as hypothesis and plan TPP/CETSA-MS or phenotype deconvolution |
| r16_01_tgfb1 | tgfb1 | R15_chromanol_Cl_pos10 | deconvolution_first | pathway_ligand_context | TGF-beta pathway reporter;pSMAD2/3;SPR/BLI only if direct ligand binding is plausible | treat docking as hypothesis and plan TPP/CETSA-MS or phenotype deconvolution |
| r15_chrom_tgfb1 | tgfb1 | R15_chromanol | deconvolution_first | pathway_ligand_context | TGF-beta pathway reporter;pSMAD2/3;SPR/BLI only if direct ligand binding is plausible | treat docking as hypothesis and plan TPP/CETSA-MS or phenotype deconvolution |
| r15_chrom_srd5a2 | srd5a2 | R15_chromanol | deconvolution_first | phenotype_deconvolution | CETSA/TPP-MS or phenotype-first target deconvolution | treat docking as hypothesis and plan TPP/CETSA-MS or phenotype deconvolution |
| r15_chrom_sirt1 | sirt1 | R15_chromanol | deconvolution_first | phenotype_deconvolution | CETSA/TPP-MS or phenotype-first target deconvolution | treat docking as hypothesis and plan TPP/CETSA-MS or phenotype deconvolution |
| r15_chrom_srd5a1 | srd5a1 | R15_chromanol | deconvolution_first | phenotype_deconvolution | CETSA/TPP-MS or phenotype-first target deconvolution | treat docking as hypothesis and plan TPP/CETSA-MS or phenotype deconvolution |
| r15_chrom_srebp1 | srebp1 | R15_chromanol | deconvolution_first | phenotype_deconvolution | CETSA/TPP-MS or phenotype-first target deconvolution | treat docking as hypothesis and plan TPP/CETSA-MS or phenotype deconvolution |
| r15_chrom_ctgf | ctgf | R15_chromanol | deconvolution_first | secreted_matrix_context | CTGF ELISA;fibroblast activation panel;target deconvolution if phenotype-first | treat docking as hypothesis and plan TPP/CETSA-MS or phenotype deconvolution |
| r15_chrom_mitf | mitf | R15_chromanol | deconvolution_first | phenotype_deconvolution | CETSA/TPP-MS or phenotype-first target deconvolution | treat docking as hypothesis and plan TPP/CETSA-MS or phenotype deconvolution |
| r15_chrom_ptgs2 | ptgs2 | R15_chromanol | assay_materials_review | enzyme_activity | COX-2 enzyme assay;PGE2 release;NSAID positive control | check recombinant protein, antibody, reporter, and disease-cell material availability |
| r16_03_tyr | tyr | R15_chromanol_Cl_pos9 | assay_materials_review | enzyme_activity | biochemical tyrosinase activity;cellular melanin content | check recombinant protein, antibody, reporter, and disease-cell material availability |
| r16_01_tyr | tyr | R15_chromanol_Cl_pos10 | assay_materials_review | enzyme_activity | biochemical tyrosinase activity;cellular melanin content | check recombinant protein, antibody, reporter, and disease-cell material availability |
| r15_chrom_tyrp1 | tyrp1 | R15_chromanol | assay_materials_review | cellular_target_context | melanosome maturation and TYRP1 expression;CETSA if antibody works | check recombinant protein, antibody, reporter, and disease-cell material availability |
| r16_06_tyr | tyr | R15_chromanol_Me9_Me10 | assay_materials_review | enzyme_activity | biochemical tyrosinase activity;cellular melanin content | check recombinant protein, antibody, reporter, and disease-cell material availability |
| r16_05_tyr | tyr | R15_chromanol_Me6_Me9 | assay_materials_review | enzyme_activity | biochemical tyrosinase activity;cellular melanin content | check recombinant protein, antibody, reporter, and disease-cell material availability |
| r16_05_dct | dct | R15_chromanol_Me6_Me9 | assay_materials_review | cellular_target_context | melanocyte DCT/TYR/TYRP1 expression;melanin phenotype;CETSA if antibody works | check recombinant protein, antibody, reporter, and disease-cell material availability |
| r16_06_dct | dct | R15_chromanol_Me9_Me10 | assay_materials_review | cellular_target_context | melanocyte DCT/TYR/TYRP1 expression;melanin phenotype;CETSA if antibody works | check recombinant protein, antibody, reporter, and disease-cell material availability |
| r16_04_tyr | tyr | R15_chromanol_Me6_Me10 | assay_materials_review | enzyme_activity | biochemical tyrosinase activity;cellular melanin content | check recombinant protein, antibody, reporter, and disease-cell material availability |
| r16_04_dct | dct | R15_chromanol_Me6_Me10 | assay_materials_review | cellular_target_context | melanocyte DCT/TYR/TYRP1 expression;melanin phenotype;CETSA if antibody works | check recombinant protein, antibody, reporter, and disease-cell material availability |
| r15_chrom_mmp1 | mmp1 | R15_chromanol | assay_materials_review | enzyme_activity | MMP1 enzymatic assay;collagen degradation;CETSA/MS | check recombinant protein, antibody, reporter, and disease-cell material availability |
| r15_chrom_ar | ar | R15_chromanol | assay_materials_review | nuclear_receptor | androgen receptor reporter;DHT competition;CETSA/nanoBRET if available | check recombinant protein, antibody, reporter, and disease-cell material availability |
| r15_chrom_lox | lox | R15_chromanol | assay_materials_review | enzyme_activity | LOX activity assay;collagen crosslinking readout | check recombinant protein, antibody, reporter, and disease-cell material availability |

## Curator Rule

- `engagement_assay_ready`: DMTL/wet-lab card로 승격한다.
- `cellular_engagement_preferred`: 추가 docking보다 reporter/CETSA/phenotype assay 설계를 우선한다.
- `deconvolution_first`: direct binding claim을 피하고 TPP/CETSA-MS 계획을 붙인다.
