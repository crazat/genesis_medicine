# Multi-fidelity BO Planner

- timestamp: `2026-05-06T12:46:10+09:00`
- plan_rows: `112`
- purpose: 다음 action을 무작정 GPU/CPU로 고르지 않고 cost 대비 정보가 큰 fidelity로 선택한다.

## Fidelity Ladder

| fidelity | cost units | purpose |
|---|---:|---|
| descriptor_surrogate | 1 | triage very large candidate pools |
| Boltz-2 cofold | 8 | target-specific structure/affinity |
| PoseBusters gate | 2 | raw pose physical sanity |
| 30 ns MD | 30 | short stability validation |
| 60-100 ns MD | 90 | paper-strength robustness |
| single-point wet-lab | 250 | phenotype or biochemical confirmation |
| dose-response/IVPT | 900 | lead-quality quantitative validation |

## Top Actions

| rank | candidate | target | next fidelity | value/cost | reason |
|---:|---|---|---|---:|---|
| 1 | R15_chromanol_Cl_pos9 | tgfb1 | single-point wet-lab | 0.00305 | stable MD pair; buy phenotype/biochemical evidence |
| 2 | R15_chromanol_Me6_Me9 | tgfb1 | single-point wet-lab | 0.00287 | stable MD pair; buy phenotype/biochemical evidence |
| 3 | R15_chromanol_Me6_Me10 | tgfb1 | single-point wet-lab | 0.00278 | stable MD pair; buy phenotype/biochemical evidence |
| 4 | R15_chromanol_Me9_Me10 | tgfb1 | single-point wet-lab | 0.00278 | stable MD pair; buy phenotype/biochemical evidence |
| 5 | R15_chromanol_Cl_pos6 | tgfb1 | single-point wet-lab | 0.00277 | stable MD pair; buy phenotype/biochemical evidence |
| 6 | R15_chromanol_Cl_pos10 | tgfb1 | single-point wet-lab | 0.00267 | stable MD pair; buy phenotype/biochemical evidence |
| 7 | R15_chromanol_Cl_pos9 | dct | single-point wet-lab | 0.00251 | stable MD pair; buy phenotype/biochemical evidence |
| 8 | R15_chromanol_Cl_pos6 | dct | single-point wet-lab | 0.00246 | stable MD pair; buy phenotype/biochemical evidence |
| 9 | R15_chromanol_Cl_pos6 | tyr | single-point wet-lab | 0.00242 | stable MD pair; buy phenotype/biochemical evidence |
| 10 | R15_chromanol | tgfb1 | single-point wet-lab | 0.00238 | stable MD pair; buy phenotype/biochemical evidence |
| 11 | R15_chromanol | tyr | single-point wet-lab | 0.00214 | stable MD pair; buy phenotype/biochemical evidence |
| 12 | R15_chromanol | dct | single-point wet-lab | 0.00201 | stable MD pair; buy phenotype/biochemical evidence |
| 13 | R15_chromanol_Cl_pos9 | tyr | PoseBusters gate | 0.28673 | cofold affinity present; needs physical/MD validation |
| 14 | R15_chromanol_Cl_pos10 | tyr | PoseBusters gate | 0.27999 | cofold affinity present; needs physical/MD validation |
| 15 | R15_chromanol_Me9_Me10 | tyr | PoseBusters gate | 0.25481 | cofold affinity present; needs physical/MD validation |
| 16 | R15_chromanol_Me6_Me9 | tyr | PoseBusters gate | 0.25108 | cofold affinity present; needs physical/MD validation |
| 17 | R15_chromanol_Me6_Me9 | dct | PoseBusters gate | 0.2504 | cofold affinity present; needs physical/MD validation |
| 18 | R15_chromanol_Me9_Me10 | dct | PoseBusters gate | 0.24983 | cofold affinity present; needs physical/MD validation |
| 19 | R15_chromanol | ptgs2 | PoseBusters gate | 0.247 | cofold affinity present; needs physical/MD validation |
| 20 | R15_chromanol | sirt1 | PoseBusters gate | 0.23145 | cofold affinity present; needs physical/MD validation |
| 21 | R15_chromanol | tyrp1 | PoseBusters gate | 0.2302 | cofold affinity present; needs physical/MD validation |
| 22 | R15_chromanol_Me6_Me10 | tyr | PoseBusters gate | 0.21551 | cofold affinity present; needs physical/MD validation |
| 23 | R15_chromanol_Me6_Me10 | dct | PoseBusters gate | 0.20466 | cofold affinity present; needs physical/MD validation |
| 24 | R15_chromanol | ar | PoseBusters gate | 0.19788 | cofold affinity present; needs physical/MD validation |
| 25 | R15_chromanol | mmp1 | PoseBusters gate | 0.19665 | cofold affinity present; needs physical/MD validation |
| 26 | R15_chromanol | srebp1 | PoseBusters gate | 0.19377 | cofold affinity present; needs physical/MD validation |
| 27 | R15_chromanol | mitf | PoseBusters gate | 0.19019 | cofold affinity present; needs physical/MD validation |
| 28 | R15_chromanol | lox | PoseBusters gate | 0.16413 | cofold affinity present; needs physical/MD validation |
| 29 | R15_chromanol | srd5a1 | PoseBusters gate | 0.15624 | cofold affinity present; needs physical/MD validation |
| 30 | R15_chromanol | ctgf | PoseBusters gate | 0.14712 | cofold affinity present; needs physical/MD validation |

## Curator Use

- CPU/GPU가 비면 `value_per_cost`가 높은 compute action부터 큐잉한다.
- wet-lab action은 계산 큐가 아니라 CRO/RFQ 후보로 보낸다.
- high-fidelity 결과가 생기면 이 파일을 다시 생성해 lower-fidelity surrogate를 보정한다.
