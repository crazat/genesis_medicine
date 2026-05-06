# Topical Formulation BO

- timestamp: `2026-05-06T12:46:31+09:00`
- lead_rows: `60`
- plan_csv: `pilot/cpu_meaningful/topical_formulation_bo_plan.csv`
- experiment_template: `data/topical_formulation_experiment_template.csv`
- purpose: molecule discovery를 실제 외용제 IVRT/IVPT/formulation optimization loop와 연결한다.

## Initial Formulation Plans

| compound | target | archetype | objective | factor ranges |
|---|---|---|---|---|
| NPC42783 |  | hydroalcoholic_gel | maximize skin retention while limiting receptor flux | ethanol 10-30%; propylene glycol 5-20%; polymer screen |
| NPC213764 |  | penetration_enhancer_gel | raise stratum-corneum partitioning without irritation | propylene glycol 10-30%; menthol/limonene 0-3% |
| NPC474914 |  | nanoemulsion_or_lipid_gel | improve release from lipophilic vehicle and avoid surface residue | lipid phase 5-20%; surfactant screen; ethanol 0-15% |
| NPC236761 |  | penetration_enhancer_gel | raise stratum-corneum partitioning without irritation | propylene glycol 10-30%; menthol/limonene 0-3% |
| NPC88887 |  | penetration_enhancer_gel | raise stratum-corneum partitioning without irritation | propylene glycol 10-30%; menthol/limonene 0-3% |
| NPC149567 |  | penetration_enhancer_gel | raise stratum-corneum partitioning without irritation | propylene glycol 10-30%; menthol/limonene 0-3% |
| NPC323980 |  | hydroalcoholic_gel | maximize skin retention while limiting receptor flux | ethanol 10-30%; propylene glycol 5-20%; polymer screen |
| NPC283633 |  | penetration_enhancer_gel | raise stratum-corneum partitioning without irritation | propylene glycol 10-30%; menthol/limonene 0-3% |
| NPC324003 |  | nanoemulsion_or_lipid_gel | improve release from lipophilic vehicle and avoid surface residue | lipid phase 5-20%; surfactant screen; ethanol 0-15% |
| NPC184593 |  | hydroalcoholic_gel | maximize skin retention while limiting receptor flux | ethanol 10-30%; propylene glycol 5-20%; polymer screen |
| NPC479534 |  | nanoemulsion_or_lipid_gel | improve release from lipophilic vehicle and avoid surface residue | lipid phase 5-20%; surfactant screen; ethanol 0-15% |
| NPC249078 |  | hydroalcoholic_gel | maximize skin retention while limiting receptor flux | ethanol 10-30%; propylene glycol 5-20%; polymer screen |
| NPC306277 |  | penetration_enhancer_gel | raise stratum-corneum partitioning without irritation | propylene glycol 10-30%; menthol/limonene 0-3% |
| NPC281540 |  | nanoemulsion_or_lipid_gel | improve release from lipophilic vehicle and avoid surface residue | lipid phase 5-20%; surfactant screen; ethanol 0-15% |
| NPC314289 |  | hydroalcoholic_gel | maximize skin retention while limiting receptor flux | ethanol 10-30%; propylene glycol 5-20%; polymer screen |
| NPC157340 |  | penetration_enhancer_gel | raise stratum-corneum partitioning without irritation | propylene glycol 10-30%; menthol/limonene 0-3% |
| NPC302293 |  | hydroalcoholic_gel | maximize skin retention while limiting receptor flux | ethanol 10-30%; propylene glycol 5-20%; polymer screen |
| NPC244869 |  | penetration_enhancer_gel | raise stratum-corneum partitioning without irritation | propylene glycol 10-30%; menthol/limonene 0-3% |
| NPC321253 |  | penetration_enhancer_gel | raise stratum-corneum partitioning without irritation | propylene glycol 10-30%; menthol/limonene 0-3% |
| NPC327468 |  | nanoemulsion_or_lipid_gel | improve release from lipophilic vehicle and avoid surface residue | lipid phase 5-20%; surfactant screen; ethanol 0-15% |
| NPC36877 |  | penetration_enhancer_gel | raise stratum-corneum partitioning without irritation | propylene glycol 10-30%; menthol/limonene 0-3% |
| NPC193781 |  | hydroalcoholic_gel | maximize skin retention while limiting receptor flux | ethanol 10-30%; propylene glycol 5-20%; polymer screen |
| NPC325130 |  | hydroalcoholic_gel | maximize skin retention while limiting receptor flux | ethanol 10-30%; propylene glycol 5-20%; polymer screen |
| NPC241081 |  | hydroalcoholic_gel | maximize skin retention while limiting receptor flux | ethanol 10-30%; propylene glycol 5-20%; polymer screen |
| NPC251201 |  | nanoemulsion_or_lipid_gel | improve release from lipophilic vehicle and avoid surface residue | lipid phase 5-20%; surfactant screen; ethanol 0-15% |

## BO Decision Rule

- Low-cost formulation readouts: solubility, viscosity, dry-down, IVRT release.
- Medium-cost readouts: IVPT flux, skin retention, receptor compartment exposure.
- High-cost readouts: cell irritation/viability plus disease-relevant phenotype.
- Acquisition objective: maximize local skin retention and phenotype signal while minimizing receptor exposure and irritation.
