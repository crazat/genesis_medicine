# paper_B data index — six-way cofold protocol evaluation

*Manuscript: `../manuscript.md` (v0.1, 2026-05-12)*

This file lists every data asset that backs the six-way `--use_potentials` evaluation. All paths absolute. All CSV row counts include header.

---

## 1. Cofold PDB outputs (Boltz-2)

| Condition | Engine | Flag | PDB directory | n PDB |
|---|---|---|---|---|
| v15 | standard Boltz-2 | (none) | `/home/crazat/genesis_medicine/pilot/round13_overnight/results/boltz_15_100_v15/boltz_results_boltz_input_full15/predictions/` | 1500 (15 lig × 100) |
| v16 | standard Boltz-2x | `--use_potentials` | `/home/crazat/genesis_medicine/pilot/round13_overnight/results/boltz_15_100_v16/boltz_results_boltz_input_full15/predictions/` | 1500 |
| v17 | standard Boltz-2x | `--use_potentials` | `/home/crazat/genesis_medicine/pilot/round13_overnight/results/boltz_15_100_v17/boltz_results_boltz_input_full15/predictions/` | 1500 |
| v18 | standard Boltz-2x | `--use_potentials` | `/home/crazat/genesis_medicine/pilot/round24/boltz_chembl94487_v18/` (15 lig × 100; placeholder — verify) | 1500 |
| retro | boltz-community fork | (none) | `/home/crazat/genesis_medicine/pilot/round24/boltz_chembl94487_retro_v0/boltz_results_boltz_input_chembl94487/predictions/mmp1_CHEMBL94487/` | 100 (canary only) |
| fork+pot | boltz-community fork | `--use_potentials` | `/home/crazat/genesis_medicine/pilot/round24/boltz_chembl94487_fork_potflag_v0/boltz_results_boltz_input_chembl94487/predictions/mmp1_CHEMBL94487/` | 100 (canary only) |

Total cofold PDB poses analysed: **6700** (4500 across full cohort under v15-v18, 200 canary under fork ± flag).

---

## 2. xTB GFN2 single-point CSVs (the primary readout)

| Condition | CSV path | Rows (header + data) |
|---|---|---|
| v15 SP | `/home/crazat/genesis_medicine/pilot/round17_cpu_burn/xtb_v15_results.csv` | 1501 |
| v16 SP | `/home/crazat/genesis_medicine/pilot/round17_cpu_burn/xtb_v16_sp_results.csv` | 1501 |
| v17 SP | `/home/crazat/genesis_medicine/pilot/round17_cpu_burn/xtb_v17_sp_results.csv` | 1501 |
| v18 SP | `/home/crazat/genesis_medicine/pilot/round24/xtb_v18_sp/xtb_v18_sp_results.csv` | 1501 |
| retro SP (canary) | `/home/crazat/genesis_medicine/pilot/round24/xtb_retro_94487/retro_xtb_sp.csv` | (~101) |
| fork+pot SP (canary) | `/home/crazat/genesis_medicine/pilot/round24/xtb_fork_potflag_94487/fork_potflag_xtb_sp.csv` | 101 |
| v15 OPT (paper-A cross-check) | `/home/crazat/genesis_medicine/pilot/round17_cpu_burn/xtb_v15_opt_results.csv` | 451 |

CSV schema: `pdb, E_eh, rc[, natoms]` where `E_eh` is GFN2 single-point total electronic energy in hartree and `rc` is the xtb return code (0 = success).

---

## 3. Launch and analysis scripts

| Purpose | Script |
|---|---|
| v15 / v16 / v17 standard Boltz-2 cofold | (master overnight scripts at `scripts/round13_overnight/`) |
| v18 standard Boltz-2x cofold | `/home/crazat/genesis_medicine/scripts/round24_paperB/cpu_xtb_v18_sp.py` (xtb side) |
| retro arm launcher | `/home/crazat/genesis_medicine/scripts/round24_paperB/launch_chembl94487_retro_boltz_community.sh` |
| fork+pot launcher | `/home/crazat/genesis_medicine/scripts/round24_paperB/launch_chembl94487_fork_with_potentials.sh` |
| v15 SP / v16 SP pool | `/home/crazat/genesis_medicine/scripts/round17_pipeline/cpu_heavy_xtb_pool.py` |
| v15 SP+OPT / v16 SP pool (combined) | `/home/crazat/genesis_medicine/scripts/round17_pipeline/cpu_heavy_xtb_v16_and_opt.py` |
| six-way σ comparison (Figure 1 source) | `/home/crazat/genesis_medicine/manuscripts/paper_B_v9/figures/fig_6way_xtb_sigma_chembl94487.py` (regenerable) |

Logs:

* `/home/crazat/genesis_medicine/scripts/round24_paperB/retro_boltz_community.log`
* `/home/crazat/genesis_medicine/scripts/round24_paperB/fork_potflag.log`
* `/home/crazat/genesis_medicine/scripts/round24_paperB/fork_potflag_outer.log`
* `/home/crazat/genesis_medicine/scripts/round24_paperB/xtb_v18_sp.log`

---

## 4. Figures

| Figure | Path |
|---|---|
| Figure 1 — 6-way σ comparison on CHEMBL94487 (3-panel) | `/home/crazat/genesis_medicine/manuscripts/paper_B_v9/figures/fig_6way_xtb_sigma_chembl94487.png` (141 KB, dpi=200) |
| Figure 1 — same, vector | `/home/crazat/genesis_medicine/manuscripts/paper_B_v9/figures/fig_6way_xtb_sigma_chembl94487.pdf` (32 KB) |

To copy these into the preprint folder, run:

```
cp /home/crazat/genesis_medicine/manuscripts/paper_B_v9/figures/fig_6way_xtb_sigma_chembl94487.* \
   /home/crazat/genesis_medicine/preprints/21_paper_B_boltz_cofold_use_potentials_protocol/figures/
```

---

## 5. Reference memory snapshots

Memory files that codify the headline numbers used in the manuscript (located at `/home/crazat/.claude/projects/-mnt-d/memory/`):

* `project_paper_b_retro_xtb_2026_05_09.md` — six-way σ comparison table (Table 2 in manuscript).
* `project_paper_a_b_xtb_v15v16_combined_2026_05_09.md` — combined v15/v16 xtb SP + OPT on 3000 + 450 poses; per-ligand σ table (Supplementary Table S1 source); paper_A ΔE_relax cross-check.
* `project_boltz2x_steering_quantified_2026_05_09.md` — Boltz-2x mean iptm / pLDDT impact on the same 1500+1500 cohort (mean Δiptm = -0.22%, "no accuracy loss" claim).

---

## 6. Ligand cohort

The 15 ChEMBL MMP-1 zinc-hydroxamate / carboxylate active-site ligands used in every condition:

```
CHEMBL98, CHEMBL406, CHEMBL412, CHEMBL415, CHEMBL1207, CHEMBL3036,
CHEMBL57058, CHEMBL93146, CHEMBL94487, CHEMBL257077, CHEMBL259829,
CHEMBL292707, CHEMBL301236, CHEMBL443684, CHEMBL2105729
```

Input YAML cache: `/home/crazat/genesis_medicine/pilot/round24/boltz_input_chembl94487/` (canary only) and parent full-15 YAML at `/home/crazat/genesis_medicine/pilot/round13_overnight/boltz_input_full15/`.

MSA cache reused across all 6 conditions (paired-server Boltz MSA hits):
`/home/crazat/genesis_medicine/pilot/round13_overnight/results/boltz_15_100_v17/boltz_results_boltz_input_full15/msa/`

---

## 7. Headline numbers (for cross-checking with manuscript text)

* Catastrophic outlier rate, no-flag (v15 + retro): 3 / 1600 = 0.188%
* Catastrophic outlier rate, flag on (v16 + v17 + v18): 1 / 4500 = 0.022%
* Ratio: 8.5× reduction
* σ_filt on CHEMBL94487:
  * v15: 4.03 kcal mol⁻¹
  * v16 / v17 / v18: 4.29 / 3.28 / 3.18 kcal mol⁻¹
  * retro: 6.66 kcal mol⁻¹
  * fork+pot: 6.98 kcal mol⁻¹
* Worst σ_raw observed: 32 813 kcal mol⁻¹ (retro arm, CHEMBL94487)
* Two ligands (CHEMBL94487, CHEMBL1207) account for 100% of v15+v17 catastrophic outliers; the other 13 ligands of the cohort show σ ≤ 0.09 hartree under both engines.
* Mean ΔE_relax (paper-A cross-check, v15 top-30 ipTM per ligand × 15 ligands × xtb crude OPT): -0.804 hartree = -504 kcal mol⁻¹.

---

*End of data index. Last updated 2026-05-12 alongside manuscript v0.1.*
