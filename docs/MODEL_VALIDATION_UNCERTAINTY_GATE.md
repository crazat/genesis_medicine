# Model Validation and Uncertainty Gate

- timestamp: `2026-05-06T12:46:33+09:00`
- training_rows: `32`
- active_rows: `672`
- training_scaffold_count: `1`
- domain_counts: `{'inside_domain': 0, 'novel_scaffold': 640, 'activity_cliff_risk': 32, 'high_model_uncertainty': 0}`
- purpose: active-learning surrogate 추천을 scaffold/applicability-domain/conformal-style interval로 제한한다.

## Top Rows

| candidate | target | domain | predicted | interval | scaffold | next |
|---|---|---|---:|---|---|---|
| R15_chromanol_Cl_pos9 | tgfb1 | activity_cliff_risk | 0.7344 | 0.6055-0.8633 | c1ccc2c(c1)CCCO2 | require direct Boltz/pose validation before claim |
| R15_chromanol_Cl_pos6 | tgfb1 | activity_cliff_risk | 0.7344 | 0.6055-0.8633 | c1ccc2c(c1)CCCO2 | require direct Boltz/pose validation before claim |
| R15_chromanol_Cl_pos10 | tgfb1 | activity_cliff_risk | 0.7344 | 0.6055-0.8633 | c1ccc2c(c1)CCCO2 | require direct Boltz/pose validation before claim |
| R15_chromanol_Me6_Me9 | tgfb1 | activity_cliff_risk | 0.6883 | 0.4738-0.9028 | c1ccc2c(c1)CCCO2 | require direct Boltz/pose validation before claim |
| R15_chromanol_Me6_Me10 | tgfb1 | activity_cliff_risk | 0.6883 | 0.4738-0.9028 | c1ccc2c(c1)CCCO2 | require direct Boltz/pose validation before claim |
| R15_chromanol_Me9_Me10 | tgfb1 | activity_cliff_risk | 0.6883 | 0.4738-0.9028 | c1ccc2c(c1)CCCO2 | require direct Boltz/pose validation before claim |
| R15_chromanol | tgfb1 | activity_cliff_risk | 0.6812 | 0.4365-0.9259 | c1ccc2c(c1)CCCO2 | require direct Boltz/pose validation before claim |
| NPC243469 | dct | novel_scaffold | 0.5925 | 0.4335-0.7515 | C1CC[C@H]2CC[C@]34CC[C@H](CC[C@H]3C2C1)C4 | require direct Boltz/pose validation before claim |
| NPC194985 | dct | novel_scaffold | 0.5925 | 0.4335-0.7515 | C1CC[C@H]2CC[C@]34CC[C@H](CC[C@H]3C2C1)C4 | require direct Boltz/pose validation before claim |
| NPC196715 | dct | novel_scaffold | 0.5925 | 0.4335-0.7515 | C1C[C@H]2[C@H](C1)C1CCC[C@H]2O1 | require direct Boltz/pose validation before claim |
| NPC261839 | dct | novel_scaffold | 0.5925 | 0.4335-0.7515 | C1CC[C@@H]2CCC3COC[C@@H]3C2C1 | require direct Boltz/pose validation before claim |
| NPC469970 | dct | novel_scaffold | 0.5925 | 0.4335-0.7515 | C1CCC2C(C1)CC[C@H]1[C@@H]3CCCC3CC[C@H]21 | require direct Boltz/pose validation before claim |
| R15_chromanol_Cl_pos9 | dct | activity_cliff_risk | 0.5925 | 0.4335-0.7515 | c1ccc2c(c1)CCCO2 | require direct Boltz/pose validation before claim |
| R15_chromanol_Cl_pos6 | dct | activity_cliff_risk | 0.5925 | 0.4335-0.7515 | c1ccc2c(c1)CCCO2 | require direct Boltz/pose validation before claim |
| R15_chromanol_Cl_pos10 | dct | activity_cliff_risk | 0.5925 | 0.4335-0.7515 | c1ccc2c(c1)CCCO2 | require direct Boltz/pose validation before claim |
| NPC243469 | ctgf | novel_scaffold | 0.5713 | 0.3862-0.7564 | C1CC[C@H]2CC[C@]34CC[C@H](CC[C@H]3C2C1)C4 | require direct Boltz/pose validation before claim |
| NPC243469 | lox | novel_scaffold | 0.5713 | 0.3862-0.7564 | C1CC[C@H]2CC[C@]34CC[C@H](CC[C@H]3C2C1)C4 | require direct Boltz/pose validation before claim |
| NPC243469 | mmp1 | novel_scaffold | 0.5713 | 0.3862-0.7564 | C1CC[C@H]2CC[C@]34CC[C@H](CC[C@H]3C2C1)C4 | require direct Boltz/pose validation before claim |
| NPC243469 | mc1r | novel_scaffold | 0.5713 | 0.3862-0.7564 | C1CC[C@H]2CC[C@]34CC[C@H](CC[C@H]3C2C1)C4 | require direct Boltz/pose validation before claim |
| NPC243469 | nr3c1 | novel_scaffold | 0.5713 | 0.3862-0.7564 | C1CC[C@H]2CC[C@]34CC[C@H](CC[C@H]3C2C1)C4 | require direct Boltz/pose validation before claim |
| NPC243469 | tyrp1 | novel_scaffold | 0.5713 | 0.3862-0.7564 | C1CC[C@H]2CC[C@]34CC[C@H](CC[C@H]3C2C1)C4 | require direct Boltz/pose validation before claim |
| NPC194985 | ctgf | novel_scaffold | 0.5713 | 0.3862-0.7564 | C1CC[C@H]2CC[C@]34CC[C@H](CC[C@H]3C2C1)C4 | require direct Boltz/pose validation before claim |
| NPC194985 | lox | novel_scaffold | 0.5713 | 0.3862-0.7564 | C1CC[C@H]2CC[C@]34CC[C@H](CC[C@H]3C2C1)C4 | require direct Boltz/pose validation before claim |
| NPC194985 | mmp1 | novel_scaffold | 0.5713 | 0.3862-0.7564 | C1CC[C@H]2CC[C@]34CC[C@H](CC[C@H]3C2C1)C4 | require direct Boltz/pose validation before claim |
| NPC194985 | mc1r | novel_scaffold | 0.5713 | 0.3862-0.7564 | C1CC[C@H]2CC[C@]34CC[C@H](CC[C@H]3C2C1)C4 | require direct Boltz/pose validation before claim |
| NPC194985 | nr3c1 | novel_scaffold | 0.5713 | 0.3862-0.7564 | C1CC[C@H]2CC[C@]34CC[C@H](CC[C@H]3C2C1)C4 | require direct Boltz/pose validation before claim |
| NPC194985 | tyrp1 | novel_scaffold | 0.5713 | 0.3862-0.7564 | C1CC[C@H]2CC[C@]34CC[C@H](CC[C@H]3C2C1)C4 | require direct Boltz/pose validation before claim |
| NPC196715 | ctgf | novel_scaffold | 0.5713 | 0.3862-0.7564 | C1C[C@H]2[C@H](C1)C1CCC[C@H]2O1 | require direct Boltz/pose validation before claim |
| NPC196715 | lox | novel_scaffold | 0.5713 | 0.3862-0.7564 | C1C[C@H]2[C@H](C1)C1CCC[C@H]2O1 | require direct Boltz/pose validation before claim |
| NPC196715 | mmp1 | novel_scaffold | 0.5713 | 0.3862-0.7564 | C1C[C@H]2[C@H](C1)C1CCC[C@H]2O1 | require direct Boltz/pose validation before claim |

## Curator Rule

- `inside_domain`도 manuscript claim이 아니라 triage 근거로만 쓴다.
- `novel_scaffold`와 `activity_cliff_risk`는 direct cofold/pose/MD 없이 paper table에 올리지 않는다.
- 외부 benchmark는 MoleculeNet/TDC/FS-Mol/scaffold split을 다음 방법론 보강 후보로 둔다.
