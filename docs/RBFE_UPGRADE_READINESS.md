# RBFE / OpenFE Upgrade Readiness

- timestamp: `2026-05-01T10:33:57+09:00`
- purpose: move selected R16 congeneric chromanol series from affinity-classifier + MD stability toward relative binding free-energy ranking.
- status: planning/readiness only; no RBFE production run launched.

## Environment

| Environment check | Available |
|---|---:|
| `current_python_openfe` | `False` |
| `current_python_openmm` | `True` |
| `venv_openfe` | `False` |
| `venv_openmm` | `True` |
| `genesis_md_openfe` | `False` |
| `genesis_md_openmm` | `True` |

## Interpretation

- `openmm` is available in `.venv` and `genesis-md`, but `openfe` is not currently installed.
- RBFE production should not be queued until OpenFE or an equivalent RBFE stack is installed and a one-edge smoke test passes.
- First RBFE candidates should be R16 TGFB1 chromanol analogs because they are a close congeneric series and already have 60 ns MD follow-up.

## R16 RBFE Edge Plan

- edge rows: `15`
- csv: `pilot/cpu_meaningful/rbfe_r16_edge_plan.csv`

| Target | ligand A | ligand B | priority | reason |
|---|---|---|---|---|
| dct | R15_chromanol_Cl_pos9 | R15_chromanol_Cl_pos6 | medium | same small chromanol congeneric series; suitable first RBFE perturbation candidate |
| dct | R15_chromanol_Cl_pos9 | R15_chromanol_Cl_pos10 | medium | same small chromanol congeneric series; suitable first RBFE perturbation candidate |
| dct | R15_chromanol_Cl_pos9 | R15_chromanol_Me6_Me9 | medium | same small chromanol congeneric series; suitable first RBFE perturbation candidate |
| dct | R15_chromanol_Cl_pos9 | R15_chromanol_Me9_Me10 | medium | same small chromanol congeneric series; suitable first RBFE perturbation candidate |
| dct | R15_chromanol_Cl_pos9 | R15_chromanol_Me6_Me10 | medium | same small chromanol congeneric series; suitable first RBFE perturbation candidate |
| tgfb1 | R15_chromanol_Cl_pos9 | R15_chromanol_Me6_Me9 | high | same small chromanol congeneric series; suitable first RBFE perturbation candidate |
| tgfb1 | R15_chromanol_Cl_pos9 | R15_chromanol_Me6_Me10 | high | same small chromanol congeneric series; suitable first RBFE perturbation candidate |
| tgfb1 | R15_chromanol_Cl_pos9 | R15_chromanol_Me9_Me10 | high | same small chromanol congeneric series; suitable first RBFE perturbation candidate |
| tgfb1 | R15_chromanol_Cl_pos9 | R15_chromanol_Cl_pos6 | medium | same small chromanol congeneric series; suitable first RBFE perturbation candidate |
| tgfb1 | R15_chromanol_Cl_pos9 | R15_chromanol_Cl_pos10 | medium | same small chromanol congeneric series; suitable first RBFE perturbation candidate |
| tyr | R15_chromanol_Cl_pos6 | R15_chromanol_Cl_pos9 | medium | same small chromanol congeneric series; suitable first RBFE perturbation candidate |
| tyr | R15_chromanol_Cl_pos6 | R15_chromanol_Cl_pos10 | medium | same small chromanol congeneric series; suitable first RBFE perturbation candidate |
| tyr | R15_chromanol_Cl_pos6 | R15_chromanol_Me9_Me10 | medium | same small chromanol congeneric series; suitable first RBFE perturbation candidate |
| tyr | R15_chromanol_Cl_pos6 | R15_chromanol_Me6_Me9 | medium | same small chromanol congeneric series; suitable first RBFE perturbation candidate |
| tyr | R15_chromanol_Cl_pos6 | R15_chromanol_Me6_Me10 | medium | same small chromanol congeneric series; suitable first RBFE perturbation candidate |

## Next Gate Before Running

1. Install/activate an RBFE-capable environment with `openfe` and `openmm` together.
2. Run one TGFB1 edge smoke test, preferably `R15_chromanol_Cl_pos9` vs `R15_chromanol_Me6_Me9`.
3. Require reproducible setup, mapper sanity, ligand net charge consistency, and stable equilibration before batch RBFE.
4. Keep RBFE claims as ranking support only until wet-lab IC50/SPR exists.
