# Genesis Storage Operations Plan

- timestamp: `2026-05-02T19:50:01+09:00`
- storage status: `ok`
- WSL root free: `401.1 GB`
- Windows C free: `465.2 GB`
- Windows D free: `1228.9 GB`

## Operating Policy

1. Keep active Boltz/OpenMM/xTB work on native WSL ext4. `/mnt/d` is acceptable for
   archive files, but it is slower for many small files.
2. Use D: as the heavy-output archive target: `/mnt/d/genesis_archive`.
3. The best long-term fix is moving the Ubuntu WSL distro to D: with
   `wsl --export` and `wsl --import`, after active jobs are paused and backed up.
4. Do not move `pilot/cpu_meaningful` or currently active output directories while
   queue workers are running.
5. If Windows C or WSL root free space drops below `80 GB`,
   the queue planner should hold new large tasks until space is recovered.
6. When validating archives on `/mnt/d`, ignore Unix ownership/permission bits
   (`--no-perms --no-owner --no-group --modify-window=2`) because DrvFS/NTFS can
   otherwise report permission-only differences after a complete copy.

## Largest Project Directories

| path | GB |
|---|---:|
| `pilot` | 252.96 |
| `.venv` | 17.74 |
| `.cache` | 7.9 |
| `external` | 1.29 |
| `external_tools` | 0.16 |
| `.git` | 0.1 |
| `scripts` | 0.06 |
| `data` | 0.04 |
| `ner_results.csv` | 0.04 |
| `preprints` | 0.03 |
| `Genesis_Medicine.code-workspace` | 0.0 |
| `Dockerfile` | 0.0 |
| `co_occurring_genes_cleaned.png` | 0.0 |
| `.claude` | 0.0 |
| `requirements.txt` | 0.0 |
| `README.md` | 0.0 |
| `conf` | 0.0 |
| `proteins` | 0.0 |
| `dvc.yaml` | 0.0 |
| `pyproject.toml` | 0.0 |

## Largest Pilot Directories

| path | GB |
|---|---:|
| `pilot/md_r16_chromanol_anchor_triad_200ns` | 25.47 |
| `pilot/md_r16_chromanol_anchor_triad_100ns` | 12.74 |
| `pilot/md_r16_chromanol_topical_tgfb1_top6_60ns` | 12.64 |
| `pilot/cpu_meaningful` | 12.21 |
| `pilot/md_pains_free_4leaders` | 11.14 |
| `pilot/md_r13_13_full14` | 8.58 |
| `pilot/md_r12_11_full14` | 8.38 |
| `pilot/md_r12_23_full14` | 8.34 |
| `pilot/md_r17_chromanol_generative_expanded_green_60ns` | 8.32 |
| `pilot/md_r17_chromanol_generative_top_green_60ns` | 8.32 |
| `pilot/md_r16_chromanol_topical_dimethyl_pigment_30ns` | 8.31 |
| `pilot/md_r17_chromanol_generative_next_green_60ns` | 8.29 |
| `pilot/md_r16_chromanol_topical_pigment_representative_60ns` | 8.29 |
| `pilot/md_extended_30ns` | 7.97 |
| `pilot/md_r14_5_full14` | 7.12 |
| `pilot/md_r12_4_full14` | 7.07 |
| `pilot/scaffold_hop` | 6.95 |
| `pilot/md_r12_super_leaders` | 6.55 |
| `pilot/md_r14_5_r13_13` | 6.22 |
| `pilot/md_r16_chromanol_topical_chloro_pigment_30ns` | 5.54 |
