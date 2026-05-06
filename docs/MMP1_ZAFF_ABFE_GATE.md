# MMP-1 ZAFF ABFE Gate

- timestamp: `2026-05-06T12:46:32+09:00`
- gate: `MMP1_ZAFF_ABFE_MUST_PASS`
- status: `blocked_zaff_not_integrated`
- current receptor: `pilot/scaffold_hop/abfe_emb3_mmp1/receptor.pdb`
- explicit Zn atoms in current receptor: `0`
- current Python openmmtools importable: `False`
- `MCPB.py` available in `genesis-md`: `True`
- `tleap` available in `genesis-md`: `True`
- `antechamber` available in `genesis-md`: `True`
- `parmchk2` available in `genesis-md`: `True`

## Verdict

Current MMP-1 free-energy evidence is not sufficient for a zinc-coordination binding claim.
Legacy EMB-3/Embelin MMP-1 values are negative decoupling estimates, but they are rejected for this gate because the receptor file does not carry an explicit catalytic Zn atom and no ZAFF/MCPB-style metal-center model is recorded.

## Existing Negative Values Not Accepted For This Gate

| system | method | delta_g_decoupling_kcal_mol | uncertainty | reason |
|---|---|---:|---:|---|
| EMB-3_MMP1 | openmmtools_alchemical_replica_exchange_full | -32.896930532116244 | 0.30388534184283544 | decoupling-only legacy result; receptor lacks explicit ZN and ZAFF/MCPB metal-center model |
| Embelin_MMP1 | openmmtools_alchemical_replica_exchange_full | -21.424185752466048 | 0.8625987921883563 | decoupling-only legacy result; receptor lacks explicit ZN and ZAFF/MCPB metal-center model |
| EMB-3_MMP1 | openmmtools_alchemical_replica_exchange | -32.212068538268745 | 1.5154767507080111 | decoupling-only legacy result; receptor lacks explicit ZN and ZAFF/MCPB metal-center model |

## Required Pass Criteria

- Rebuild a holo MMP-1 active-site model retaining catalytic `Zn2+` and coordinating residues.
- Parameterize the Zn center with `ZAFF` or `MCPB.py` bonded/nonbonded parameters and record the generated parameter files.
- Pass a short restrained complex sanity MD with stable Zn coordination geometry before alchemical production.
- Report Zn-ligand distance, Zn-His/Glu coordination distances, and a reference-geometry deviation score from a holo MMP-1 template; do not use a single ideal `109.5 deg` tetrahedral angle as the only pass/fail criterion because metalloprotease active sites can be distorted or ligand-dependent.
- Report restraint-corrected standard-state `DeltaG_bind`, not decoupling-only `DeltaG_decoupling`.
- The computational binding claim is allowed only if `DeltaG_bind < 0 kcal/mol`; strict pass requires the uncertainty upper bound to remain below zero.
- Treat any pre-run ZAFF correction magnitude such as `-8 kcal/mol` as a hypothesis, not evidence. The manuscript may report only measured production outputs.

## Adjacent Metrics To Track Separately

- Hydration/skin-permeability terms belong to the topical formulation/PBPK gate, not to the MMP-1 binding gate. They should support R15/R16 topical-delivery ranking, while ZAFF ABFE supports target engagement.
- A useful topical thermodynamic decomposition is `DeltaG_perm = DeltaG_partition + DeltaG_diffusion`; report it as delivery evidence, not as proof of MMP-1 binding.

## Claim Rule

Until this gate passes, manuscripts must phrase MMP-1 evidence as Boltz/MD-supported and zinc-model-limited, not as ZAFF-corrected ABFE-confirmed binding.
