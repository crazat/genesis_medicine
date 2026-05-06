# Codex Curator Context

timestamp: `2026-05-06T12:46:57+09:00`
root: `/home/crazat/genesis_medicine`
interval_sec: `600`
timeout_sec: `1200`

## System

```text
               total        used        free      shared  buff/cache   available
Mem:            54Gi        41Gi        10Gi        89Mi       3.8Gi        13Gi
Swap:           16Gi       7.8Mi        15Gi
 12:46:57 up 7 days,  2:40,  1 user,  load average: 4.81, 2.95, 2.11

procs -----------memory---------- ---swap-- -----io---- -system-- -------cpu-------
 r  b   swpd   free   buff  cache   si   so    bi    bo   in   cs us sy id wa st gu
 1  0   8012 11197072  98112 3838636    0    0  1189  1597 8542   20 62  5 33  0  0  0
 0  0   8012 11213120  98112 3838644    0    0     0     0 2201 3426  2  3 96  0  0  0
```

## GPU

```text
utilization.gpu [%], memory.used [MiB], memory.total [MiB]
2 %, 25187 MiB, 32607 MiB
658, [Not Found], [N/A]
```

## Top CPU

```text
USER         PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
crazat   2949978  3.6  0.8 75552380 500876 pts/6 Sl+  May03 164:06 claude --permission-mode bypassPermissions
root           1  0.0  0.0  22236  9108 ?        Ss   May02   2:57 /usr/lib/systemd/systemd --system --deserialize=60
crazat   1898638  0.0  0.0   4888  3592 ?        Ss   May05   0:23 /bin/bash -c source /home/crazat/.claude/shell-snapshots/snapshot-bash-1777781873206-74i5b2.sh 2>/dev/null || true && shopt -u extglob 2>/dev/null || true && eval 'until nvidia-smi --query-compute-apps=pid --format=csv,noheader 2>/dev/null | grep -q 1897121; do sleep 3; done; echo "CHEMBL257077 (PID 1897121) GPU에 등록됨"; date '"'"'+%H:%M:%S'"'"'' < /dev/null && pwd -P >| /tmp/claude-84f0-cwd
root     1267412  0.0  0.0  66724 13308 ?        S<s  May03   0:58 /usr/lib/systemd/systemd-journald
message+     204  0.0  0.0   9916  5116 ?        Ss   May02   0:32 @dbus-daemon --system --address=systemd: --nofork --nopidfile --systemd-activation --syslog-only
root     2949302  0.0  0.0   3144  1296 ?        S    May03   0:19 /init
crazat     77605  0.0  0.0   5148  3508 ?        Ss   May02   0:14 bash /home/crazat/genesis_medicine/scripts/codex_curator_loop.sh
syslog   1278317  0.0  0.0 222508  5280 ?        Ssl  May03   0:13 /usr/sbin/rsyslogd -n -iNONE
crazat     77583  0.0  0.0   4884  3204 ?        Ss   May02   0:14 bash /home/crazat/genesis_medicine/scripts/monitor_supervisor.sh
root         201  0.0  0.0  17960  5128 ?        S<s  May02   0:13 /usr/lib/systemd/systemd-logind
root     3275257  0.0  0.0 2199896 9820 ?        Ssl  May03   0:08 /usr/libexec/wsl-pro-service -vv
crazat   2512206  0.0  0.0   5008  3532 ?        Ss   May03   0:08 bash /home/crazat/genesis_medicine/scripts/auto_queue_cpu_gpu_daemon.sh
polkitd  1275756  0.0  0.0 308160  4472 ?        Ssl  May03   0:06 /usr/lib/polkit-1/polkitd --no-debug
systemd+ 1267492  0.0  0.0  91024  5168 ?        Ssl  May03   0:05 /usr/lib/systemd/systemd-timesyncd
root     1267600  0.0  0.0  25256  5000 ?        Ss   May03   0:04 /usr/lib/systemd/systemd-udevd
root           8  0.0  0.0   3208  2128 ?        Sl   May02   0:04 plan9 --control-socket 7 --log-level 4 --server-fd 8 --pipe-fd 10 --log-truncate
crazat       398  0.0  0.0  20264  6304 ?        Ss   May02   0:01 /usr/lib/systemd/systemd --user --deserialize=8
systemd+ 1267686  0.0  0.0  21456  7024 ?        Ss   May03   0:01 /usr/lib/systemd/systemd-resolved
root     2105534  0.0  0.0  19556  7468 ?        Ss   12:00   0:00 (agetty)
```

## Protected And Project Processes

```text
crazat     77583   77542  0 May02 ?        00:00:14 bash /home/crazat/genesis_medicine/scripts/monitor_supervisor.sh
crazat     77605   77542  0 May02 ?        00:00:14 bash /home/crazat/genesis_medicine/scripts/codex_curator_loop.sh
crazat   2512206   77583  0 May03 ?        00:00:08 bash /home/crazat/genesis_medicine/scripts/auto_queue_cpu_gpu_daemon.sh
```

## Triggers

```text
-rw-r--r-- 1 crazat crazat 0 May  3 11:07 /tmp/genesis_auto_queue_enabled
-rw-r--r-- 1 crazat crazat 0 May  3 10:26 /tmp/genesis_codex_curator_enabled
-rw-r--r-- 1 crazat crazat 0 May  3 10:26 /tmp/genesis_monitor_enabled
```

## Planner

### pilot/auto_result_planner_latest.json

```json
{
    "gpu": {
        "task": "none",
        "reason": "GPU validation queue complete through R16 anchor triad 200 ns and R17 generative top/next/expanded green-target 10/30/60 ns panels",
        "stability": {
            "priority": {
                "stable": true,
                "max_rmsd_A": 1.38,
                "max_last_third_A": 1.17,
                "reason": "max RMSD 1.38 A, max last-third 1.17 A"
            },
            "tgfb1_extra": {
                "stable": true,
                "max_rmsd_A": 1.24,
                "max_last_third_A": 1.04,
                "reason": "max RMSD 1.24 A, max last-third 1.04 A"
            },
            "chloro_tgfb1": {
                "stable": true,
                "max_rmsd_A": 0.87,
                "max_last_third_A": 0.67,
                "reason": "max RMSD 0.87 A, max last-third 0.67 A"
            },
            "chloro_pigment": {
                "stable": true,
                "max_rmsd_A": 1.25,
                "max_last_third_A": 1.0,
                "reason": "max RMSD 1.25 A, max last-third 1.00 A"
            },
            "dimethyl_pigment": {
                "stable": true,
                "max_rmsd_A": 0.93,
                "max_last_third_A": 0.59,
                "reason": "max RMSD 0.93 A, max last-third 0.59 A"
            },
            "tgfb1_top6_60ns": {
                "stable": true,
                "max_rmsd_A": 1.22,
                "max_last_third_A": 0.96,
                "reason": "max RMSD 1.22 A, max last-third 0.96 A"
            },
            "r15_top3_30ns": {
                "stable": true,
                "max_rmsd_A": 1.33,
                "max_last_third_A": 1.06,
                "reason": "max RMSD 1.33 A, max last-third 1.06 A"
            },
            "pigment_representative_60ns": {
                "stable": true,
                "max_rmsd_A": 1.1,
                "max_last_third_A": 0.78,
                "reason": "max RMSD 1.10 A, max last-third 0.78 A"
            },
            "anchor_triad_100ns": {
                "stable": true,
                "max_rmsd_A": 1.13,
                "max_last_third_A": 0.51,
                "reason": "max RMSD 1.13 A, max last-third 0.51 A"
            },
            "anchor_triad_200ns": {
                "stable": true,
                "max_rmsd_A": 1.05,
                "max_last_third_A": 0.57,
                "reason": "max RMSD 1.05 A, max last-third 0.57 A"
            },
            "r17_top_green_10ns": {
                "stable": true,
                "max_rmsd_A": 1.05,
                "max_last_third_A": 0.74,
                "reason": "max RMSD 1.05 A, max last-third 0.74 A"
            },
            "r17_top_green_30ns": {
                "stable": true,
                "max_rmsd_A": 0.98,
                "max_last_third_A": 0.73,
                "reason": "max RMSD 0.98 A, max last-third 0.73 A"
            },
            "r17_top_green_60ns": {
                "stable": true,
                "max_rmsd_A": 0.94,
                "max_last_third_A": 0.62,
                "reason": "max RMSD 0.94 A, max last-third 0.62 A"
            },
            "r17_next_green_10ns": {
                "stable": true,
                "max_rmsd_A": 0.87,
                "max_last_third_A": 0.6,
                "reason": "max RMSD 0.87 A, max last-third 0.60 A"
            },
            "r17_next_green_30ns": {
                "stable": true,
                "max_rmsd_A": 0.86,
                "max_last_third_A": 0.54,
                "reason": "max RMSD 0.86 A, max last-third 0.54 A"
            },
            "r17_next_green_60ns": {
                "stable": true,
                "max_rmsd_A": 1.23,
                "max_last_third_A": 0.97,
                "reason": "max RMSD 1.23 A, max last-third 0.97 A"
            },
            "r17_expanded_green_10ns": {
                "stable": true,
                "max_rmsd_A": 1.26,
                "max_last_third_A": 0.59,
                "reason": "max RMSD 1.26 A, max last-third 0.59 A"
            },
            "r17_expanded_green_30ns": {
                "stable": true,
                "max_rmsd_A": 0.83,
                "max_last_third_A": 0.37,
                "reason": "max RMSD 0.83 A, max last-third 0.37 A"
            },
            "r17_expanded_green_60ns": {
                "stable": true,
                "max_rmsd_A": 1.05,
                "max_last_third_A": 0.48,
                "reason": "max RMSD 1.05 A, max last-third 0.48 A"
            }
        },
        "paper_candidate": "r17_chromanol_generative_atlas",
        "completed_rows": 240,
        "target_rows": 240
    },
    "cpu": {
        "task": "none",
        "spec": "none",
        "reason": "all configured xTB refinement outputs exist or are running through 384conf"
    },
    "storage_pressure": {
        "status": "ok",
        "min_free_gb": 450.0,
        "min_free_gb_required": 80.0,
        "warn_free_gb": 200.0,
        "disks": {
            "wsl_root": {
                "path": "/",
                "exists": true,
                "total_gb": 1770.7,
                "used_gb": 441.4,
                "free_gb": 1247.1,
                "used_pct": 24.9
            },
            "windows_c": {
                "path": "/mnt/c",
                "exists": true,
                "total_gb": 1906.9,
                "used_gb": 1456.9,
                "free_gb": 450.0,
                "used_pct": 76.4
            },
            "windows_d": {
                "path": "/mnt/d",
                "exists": true,
                "total_gb": 1863.0,
                "used_gb": 690.8,
                "free_gb": 1172.2,
                "used_pct": 37.1
            }
        },
        "note": "Active compute should stay on WSL ext4; completed heavy outputs should be archived to D:."
    },
    "world_class_queue_policy": {
        "finish_already_running_r17_expanded_60ns": false,
        "allow_cpu_cheap_atlas": true,
        "no_new_chromanol_100_200ns_or_fe_or_synthesis_until_markush_fto": true,
        "no_mmp1_abfe_confirmed_claim_until_zaff_gate_pass": true,
        "emb3_quinone_requires_wetlab_safety_package": true,
        "boltz_only_claims_require_cross_model_decoy_or_plif_before_strong_language": true,
        "wetlab_first_when_dmtl_or_ivpt_ready": true,
        "creative_generation_requires_synthesis_or_prior_art_guard": true,
        "active_learning_short_cofold_fallback_enabled": true,
        "cryptic_pocket_generation_requires_ensemble_pocket_gate": true,
        "phenomics_generation_requires_signature_or_assay_gate": true,
        "target_msa_coverage_gap_blocks_target_queue": true,
        "new_scaffold_gpu_followup_requires_uncertainty_and_benchmark_gate": true
    },
    "world_class_readiness_counts": {
        "cheap_compute_or_paper_with_fto_caveat": 378,
        "triage_accumulating": 1193,
        "hold_or_benchmark_only": 757
    },
    "world_class_heavy_compute_permission_counts": {
        "short_triage_only": 378,
        "cheap_compute_only": 1193,
        "hold": 757
    },
    "notes": [
        "This planner is deterministic and result-aware; it is not an LLM process.",
        "LLM-level reprioritization is handled by scripts/codex_curator_loop.sh when enabled.",
        "World-class gap closure decisions are summarized in pilot/auto_queue_decision_policy.json and docs/WORLD_CLASS_GAP_CLOSURE.md.",
        "Storage hard-hold blocks new large launches when Windows C: or WSL root free space is below GENESIS_MIN_FREE_GB."
    ]
}

```

## MD Summaries

### pilot/md_extended_30ns/summary.json

```json
[
    {
        "name": "mmp1__r14_5_30ns",
        "status": "ok",
        "wall_min": 23.09,
        "rmsd_mean_A": 0.69,
        "rmsd_max_A": 1.11,
        "rmsd_final_A": 0.63,
        "rmsd_last10ns_A": 0.69,
        "ns_simulated": 30.0
    },
    {
        "name": "ctgf__r14_5_30ns",
        "status": "ok",
        "wall_min": 24.14,
        "rmsd_mean_A": 1.34,
        "rmsd_max_A": 2.51,
        "rmsd_final_A": 1.73,
        "rmsd_last10ns_A": 1.76,
        "ns_simulated": 30.0
    },
    {
        "name": "ar__r12_23_30ns",
        "status": "ok",
        "wall_min": 47.95,
        "rmsd_mean_A": 0.77,
        "rmsd_max_A": 1.76,
        "rmsd_final_A": 0.88,
        "rmsd_last10ns_A": 0.85,
        "ns_simulated": 30.0
    },
    {
        "name": "sirt1__r12_23_30ns",
        "status": "ok",
        "wall_min": 35.85,
        "rmsd_mean_A": 0.72,
        "rmsd_max_A": 1.44,
        "rmsd_final_A": 0.78,
        "rmsd_last10ns_A": 0.79,
        "ns_simulated": 30.0
    },
    {
        "name": "ptgs2__r12_23_30ns",
        "status": "ok",
        "wall_min": 29.35,
        "rmsd_mean_A": 1.38,
        "rmsd_max_A": 2.16,
        "rmsd_final_A": 1.72,
        "rmsd_last10ns_A": 1.76,
        "ns_simulated": 30.0
    }
]

```
### pilot/md_extended_30ns_batch2/summary.json

```json
[
    {
        "name": "mmp1__r12_4_30ns",
        "status": "ok",
        "wall_min": 23.24,
        "rmsd_mean_A": 0.67,
        "rmsd_max_A": 1.17,
        "rmsd_final_A": 0.73,
        "rmsd_last10ns_A": 0.65,
        "ns_simulated": 30.0
    },
    {
        "name": "sirt1__r12_4_30ns",
        "status": "ok",
        "wall_min": 37.48,
        "rmsd_mean_A": 0.92,
        "rmsd_max_A": 1.9,
        "rmsd_final_A": 1.48,
        "rmsd_last10ns_A": 1.11,
        "ns_simulated": 30.0
    },
    {
        "name": "srebp1__r12_23_30ns",
        "status": "ok",
        "wall_min": 23.26,
        "rmsd_mean_A": 1.08,
        "rmsd_max_A": 1.61,
        "rmsd_final_A": 1.13,
        "rmsd_last10ns_A": 1.11,
        "ns_simulated": 30.0
    },
    {
        "name": "srebp1__r14_5_30ns",
        "status": "ok",
        "wall_min": 24.49,
        "rmsd_mean_A": 1.94,
        "rmsd_max_A": 2.54,
        "rmsd_final_A": 2.38,
        "rmsd_last10ns_A": 2.08,
        "ns_simulated": 30.0
    },
    {
        "name": "tgfb1__r12_11_30ns",
        "status": "ok",
        "wall_min": 27.05,
        "rmsd_mean_A": 1.44,
        "rmsd_max_A": 2.53,
        "rmsd_final_A": 1.61,
        "rmsd_last10ns_A": 1.15,
        "ns_simulated": 30.0
    }
]

```
### pilot/md_r16_chromanol_topical_priority_30ns/summary.json

```json
[
    {
        "name": "r16_03_tgfb1__R15_chromanol_Cl_pos9__30ns",
        "job_id": "r16_03_tgfb1",
        "analog_id": "R15_chromanol_Cl_pos9",
        "target": "tgfb1",
        "status": "ok",
        "smiles": "OCC1COc2cc(O)c(Cl)cc2C1",
        "topical_followup_score": 0.8750700000000001,
        "logP": 1.589,
        "QED": 0.747,
        "gap_eV": 3.809593876030666,
        "affinity_probability_binary": 0.6822030544281006,
        "affinity_pred_value": 1.2207756042480469,
        "wall_min": 22.68,
        "rmsd_mean_A": 0.81,
        "rmsd_max_A": 1.38,
        "rmsd_final_A": 1.22,
        "rmsd_last_third_A": 1.17,
        "ns_simulated": 30.0
    },
    {
        "name": "r16_03_dct__R15_chromanol_Cl_pos9__30ns",
        "job_id": "r16_03_dct",
        "analog_id": "R15_chromanol_Cl_pos9",
        "target": "dct",
        "status": "ok",
        "smiles": "OCC1COc2cc(O)c(Cl)cc2C1",
        "topical_followup_score": 0.8750700000000001,
        "logP": 1.589,
        "QED": 0.747,
        "gap_eV": 3.809593876030666,
        "affinity_probability_binary": 0.5464680790901184,
        "affinity_pred_value": 0.8821029663085938,
        "wall_min": 24.5,
        "rmsd_mean_A": 0.38,
        "rmsd_max_A": 1.0,
        "rmsd_final_A": 0.64,
        "rmsd_last_third_A": 0.67,
        "ns_simulated": 30.0
    },
    {
        "name": "r16_02_tyr__R15_chromanol_Cl_pos6__30ns",
        "job_id": "r16_02_tyr",
        "analog_id": "R15_chromanol_Cl_pos6",
        "target": "tyr",
        "status": "ok",
        "smiles": "OCC1COc2c(ccc(O)c2Cl)C1",
        "topical_followup_score": 0.8750700000000001,
        "logP": 1.589,
        "QED": 0.747,
        "gap_eV": 3.92941240153,
        "affinity_probability_binary": 0.5249537825584412,
        "affinity_pred_value": 0.8515019416809082,
        "wall_min": 24.35,
        "rmsd_mean_A": 0.69,
        "rmsd_max_A": 0.91,
        "rmsd_final_A": 0.69,
        "rmsd_last_third_A": 0.72,
        "ns_simulated": 30.0
    }
]

```
### pilot/md_r16_chromanol_topical_tgfb1_extra_30ns/summary.json

```json
[
    {
        "name": "r16_05_tgfb1__R15_chromanol_Me6_Me9__30ns",
        "job_id": "r16_05_tgfb1",
        "analog_id": "R15_chromanol_Me6_Me9",
        "target": "tgfb1",
        "status": "ok",
        "smiles": "Cc1cc2c(c(C)c1O)OCC(CO)C2",
        "topical_followup_score": 0.8718849999999999,
        "logP": 1.552,
        "QED": 0.736,
        "gap_eV": 3.9847867644273336,
        "affinity_probability_binary": 0.6364059448242188,
        "affinity_pred_value": 0.6152913570404053,
        "wall_min": 25.57,
        "rmsd_mean_A": 0.68,
        "rmsd_max_A": 0.89,
        "rmsd_final_A": 0.68,
        "rmsd_last_third_A": 0.71,
        "ns_simulated": 30.0
    },
    {
        "name": "r16_04_tgfb1__R15_chromanol_Me6_Me10__30ns",
        "job_id": "r16_04_tgfb1",
        "analog_id": "R15_chromanol_Me6_Me10",
        "target": "tgfb1",
        "status": "ok",
        "smiles": "Cc1cc(O)c(C)c2c1CC(CO)CO2",
        "topical_followup_score": 0.8718849999999999,
        "logP": 1.552,
        "QED": 0.736,
        "gap_eV": 4.138358853282,
        "affinity_probability_binary": 0.6156794428825378,
        "affinity_pred_value": 1.0828746557235718,
        "wall_min": 24.88,
        "rmsd_mean_A": 0.99,
        "rmsd_max_A": 1.24,
        "rmsd_final_A": 1.03,
        "rmsd_last_third_A": 1.04,
        "ns_simulated": 30.0
    },
    {
        "name": "r16_06_tgfb1__R15_chromanol_Me9_Me10__30ns",
        "job_id": "r16_06_tgfb1",
        "analog_id": "R15_chromanol_Me9_Me10",
        "target": "tgfb1",
        "status": "ok",
        "smiles": "Cc1c(O)cc2c(c1C)CC(CO)CO2",
        "topical_followup_score": 0.8718849999999999,
        "logP": 1.552,
        "QED": 0.736,
        "gap_eV": 3.9726410339953335,
        "affinity_probability_binary": 0.6153576970100403,
        "affinity_pred_value": 1.0456148386001587,
        "wall_min": 25.18,
        "rmsd_mean_A": 0.54,
        "rmsd_max_A": 0.81,
        "rmsd_final_A": 0.56,
        "rmsd_last_third_A": 0.53,
        "ns_simulated": 30.0
    }
]

```
### pilot/md_r16_chromanol_topical_top3_10ns/summary.json

```json
[
    {
        "name": "r16_03_tgfb1__R15_chromanol_Cl_pos9__10ns",
        "job_id": "r16_03_tgfb1",
        "analog_id": "R15_chromanol_Cl_pos9",
        "target": "tgfb1",
        "status": "ok",
        "smiles": "OCC1COc2cc(O)c(Cl)cc2C1",
        "topical_followup_score": 0.8750700000000001,
        "logP": 1.589,
        "QED": 0.747,
        "gap_eV": 3.809593876030666,
        "affinity_probability_binary": 0.6822030544281006,
        "affinity_pred_value": 1.2207756042480469,
        "wall_min": 9.32,
        "rmsd_mean_A": 0.32,
        "rmsd_max_A": 0.63,
        "rmsd_final_A": 0.51,
        "rmsd_last_third_A": 0.31,
        "ns_simulated": 10.0
    },
    {
        "name": "r16_05_tgfb1__R15_chromanol_Me6_Me9__10ns",
        "job_id": "r16_05_tgfb1",
        "analog_id": "R15_chromanol_Me6_Me9",
        "target": "tgfb1",
        "status": "ok",
        "smiles": "Cc1cc2c(c(C)c1O)OCC(CO)C2",
        "topical_followup_score": 0.8718849999999999,
        "logP": 1.552,
        "QED": 0.736,
        "gap_eV": 3.9847867644273336,
        "affinity_probability_binary": 0.6364059448242188,
        "affinity_pred_value": 0.6152913570404053,
        "wall_min": 7.91,
        "rmsd_mean_A": 0.42,
        "rmsd_max_A": 0.63,
        "rmsd_final_A": 0.41,
        "rmsd_last_third_A": 0.44,
        "ns_simulated": 10.0
    },
    {
        "name": "r16_04_tgfb1__R15_chromanol_Me6_Me10__10ns",
        "job_id": "r16_04_tgfb1",
        "analog_id": "R15_chromanol_Me6_Me10",
        "target": "tgfb1",
        "status": "ok",
        "smiles": "Cc1cc(O)c(C)c2c1CC(CO)CO2",
        "topical_followup_score": 0.8718849999999999,
        "logP": 1.552,
        "QED": 0.736,
        "gap_eV": 4.138358853282,
        "affinity_probability_binary": 0.6156794428825378,
        "affinity_pred_value": 1.0828746557235718,
        "wall_min": 7.72,
        "rmsd_mean_A": 0.46,
        "rmsd_max_A": 0.6,
        "rmsd_final_A": 0.43,
        "rmsd_last_third_A": 0.46,
        "ns_simulated": 10.0
    }
]

```
### pilot/md_r15_chromanol_top3_10ns/summary.json

```json
[
    {
        "name": "tgfb1__r15_chromanol_10ns",
        "target": "tgfb1",
        "status": "ok",
        "affinity_probability_binary": 0.5939338803291321,
        "affinity_pred_value": 1.3405288457870483,
        "wall_min": 7.54,
        "rmsd_mean_A": 0.76,
        "rmsd_max_A": 1.24,
        "rmsd_final_A": 0.46,
        "rmsd_last_third_A": 0.64,
        "ns_simulated": 10.0
    },
    {
        "name": "tyr__r15_chromanol_10ns",
        "target": "tyr",
        "status": "ok",
        "affinity_probability_binary": 0.536052942276001,
        "affinity_pred_value": 1.4759944677352903,
        "wall_min": 8.29,
        "rmsd_mean_A": 0.62,
        "rmsd_max_A": 0.88,
        "rmsd_final_A": 0.6,
        "rmsd_last_third_A": 0.62,
        "ns_simulated": 10.0
    },
    {
        "name": "dct__r15_chromanol_10ns",
        "target": "dct",
        "status": "ok",
        "affinity_probability_binary": 0.5018967390060425,
        "affinity_pred_value": 1.8747093677520752,
        "wall_min": 8.4,
        "rmsd_mean_A": 0.91,
        "rmsd_max_A": 1.24,
        "rmsd_final_A": 0.9,
        "rmsd_last_third_A": 1.03,
        "ns_simulated": 10.0
    }
]

```
### pilot/md_r15_chromanol_top3_30ns/summary.json

```json
[
    {
        "name": "tgfb1__r15_chromanol_30ns",
        "target": "tgfb1",
        "status": "ok",
        "affinity_probability_binary": 0.5939338803291321,
        "affinity_pred_value": 1.3405288457870483,
        "wall_min": 20.56,
        "rmsd_mean_A": 0.51,
        "rmsd_max_A": 0.91,
        "rmsd_final_A": 0.75,
        "rmsd_last_third_A": 0.72,
        "ns_simulated": 30.0
    },
    {
        "name": "tyr__r15_chromanol_30ns",
        "target": "tyr",
        "status": "ok",
        "affinity_probability_binary": 0.536052942276001,
        "affinity_pred_value": 1.4759944677352903,
        "wall_min": 24.05,
        "rmsd_mean_A": 0.92,
        "rmsd_max_A": 1.33,
        "rmsd_final_A": 1.13,
        "rmsd_last_third_A": 1.06,
        "ns_simulated": 30.0
    },
    {
        "name": "dct__r15_chromanol_30ns",
        "target": "dct",
        "status": "ok",
        "affinity_probability_binary": 0.5018967390060425,
        "affinity_pred_value": 1.8747093677520752,
        "wall_min": 23.78,
        "rmsd_mean_A": 0.47,
        "rmsd_max_A": 0.69,
        "rmsd_final_A": 0.53,
        "rmsd_last_third_A": 0.5,
        "ns_simulated": 30.0
    }
]

```
### pilot/md_r16_chromanol_topical_tgfb1_top6_60ns/summary.json

```json
[
    {
        "name": "r16_03_tgfb1__R15_chromanol_Cl_pos9__60ns",
        "job_id": "r16_03_tgfb1",
        "analog_id": "R15_chromanol_Cl_pos9",
        "target": "tgfb1",
        "status": "ok",
        "smiles": "OCC1COc2cc(O)c(Cl)cc2C1",
        "topical_followup_score": 0.8750700000000001,
        "logP": 1.589,
        "QED": 0.747,
        "gap_eV": 3.809593876030666,
        "affinity_probability_binary": 0.6822030544281006,
        "affinity_pred_value": 1.2207756042480469,
        "wall_min": 43.03,
        "rmsd_mean_A": 0.55,
        "rmsd_max_A": 0.7,
        "rmsd_final_A": 0.59,
        "rmsd_last_third_A": 0.55,
        "ns_simulated": 60.0
    },
    {
        "name": "r16_05_tgfb1__R15_chromanol_Me6_Me9__60ns",
        "job_id": "r16_05_tgfb1",
        "analog_id": "R15_chromanol_Me6_Me9",
        "target": "tgfb1",
        "status": "ok",
        "smiles": "Cc1cc2c(c(C)c1O)OCC(CO)C2",
        "topical_followup_score": 0.8718849999999999,
        "logP": 1.552,
        "QED": 0.736,
        "gap_eV": 3.9847867644273336,
        "affinity_probability_binary": 0.6364059448242188,
        "affinity_pred_value": 0.6152913570404053,
        "wall_min": 43.11,
        "rmsd_mean_A": 0.48,
        "rmsd_max_A": 0.72,
        "rmsd_final_A": 0.44,
        "rmsd_last_third_A": 0.47,
        "ns_simulated": 60.0
    },
    {
        "name": "r16_04_tgfb1__R15_chromanol_Me6_Me10__60ns",
        "job_id": "r16_04_tgfb1",
        "analog_id": "R15_chromanol_Me6_Me10",
        "target": "tgfb1",
        "status": "ok",
        "smiles": "Cc1cc(O)c(C)c2c1CC(CO)CO2",
        "topical_followup_score": 0.8718849999999999,
        "logP": 1.552,
        "QED": 0.736,
        "gap_eV": 4.138358853282,
        "affinity_probability_binary": 0.6156794428825378,
        "affinity_pred_value": 1.0828746557235718,
        "wall_min": 42.23,
        "rmsd_mean_A": 0.5,
        "rmsd_max_A": 1.18,
        "rmsd_final_A": 0.58,
        "rmsd_last_third_A": 0.47,
        "ns_simulated": 60.0
    },
    {
        "name": "r16_06_tgfb1__R15_chromanol_Me9_Me10__60ns",
        "job_id": "r16_06_tgfb1",
        "analog_id": "R15_chromanol_Me9_Me10",
        "target": "tgfb1",
        "status": "ok",
        "smiles": "Cc1c(O)cc2c(c1C)CC(CO)CO2",
        "topical_followup_score": 0.8718849999999999,
        "logP": 1.552,
        "QED": 0.736,
        "gap_eV": 3.9726410339953335,
        "affinity_probability_binary": 0.6153576970100403,
        "affinity_pred_value": 1.0456148386001587,
        "wall_min": 42.16,
        "rmsd_mean_A": 0.52,
        "rmsd_max_A": 0.7,
        "rmsd_final_A": 0.51,
        "rmsd_last_third_A": 0.5,
        "ns_simulated": 60.0
    },
    {
        "name": "r16_02_tgfb1__R15_chromanol_Cl_pos6__60ns",
        "job_id": "r16_02_tgfb1",
        "analog_id": "R15_chromanol_Cl_pos6",
        "target": "tgfb1",
        "status": "ok",
        "smiles": "OCC1COc2c(ccc(O)c2Cl)C1",
        "topical_followup_score": 0.8750700000000001,
        "logP": 1.589,
        "QED": 0.747,
        "gap_eV": 3.92941240153,
        "affinity_probability_binary": 0.611671507358551,
        "affinity_pred_value": 1.319031834602356,
        "wall_min": 41.56,
        "rmsd_mean_A": 0.75,
        "rmsd_max_A": 1.22,
        "rmsd_final_A": 0.94,
        "rmsd_last_third_A": 0.96,
        "ns_simulated": 60.0
    },
    {
        "name": "r16_01_tgfb1__R15_chromanol_Cl_pos10__60ns",
        "job_id": "r16_01_tgfb1",
        "analog_id": "R15_chromanol_Cl_pos10",
        "target": "tgfb1",
        "status": "ok",
        "smiles": "OCC1COc2cc(O)cc(Cl)c2C1",
        "topical_followup_score": 0.8750700000000001,
        "logP": 1.589,
        "QED": 0.747,
        "gap_eV": 3.9600931852715,
        "affinity_probability_binary": 0.5867519378662109,
        "affinity_pred_value": 1.0125867128372192,
        "wall_min": 41.64,
        "rmsd_mean_A": 0.83,
        "rmsd_max_A": 1.21,
        "rmsd_final_A": 0.78,
        "rmsd_last_third_A": 0.75,
        "ns_simulated": 60.0
    }
]

```
### pilot/md_r16_chromanol_topical_pigment_representative_60ns/summary.json

```json
[
    {
        "name": "r16_03_dct__R15_chromanol_Cl_pos9__60ns",
        "job_id": "r16_03_dct",
        "analog_id": "R15_chromanol_Cl_pos9",
        "target": "dct",
        "status": "ok",
        "smiles": "OCC1COc2cc(O)c(Cl)cc2C1",
        "topical_followup_score": 0.8750700000000001,
        "logP": 1.589,
        "QED": 0.747,
        "gap_eV": 3.809593876030666,
        "affinity_probability_binary": 0.5464680790901184,
        "affinity_pred_value": 0.8821029663085938,
        "wall_min": 47.26,
        "rmsd_mean_A": 0.77,
        "rmsd_max_A": 1.1,
        "rmsd_final_A": 0.85,
        "rmsd_last_third_A": 0.78,
        "ns_simulated": 60.0
    },
    {
        "name": "r16_02_dct__R15_chromanol_Cl_pos6__60ns",
        "job_id": "r16_02_dct",
        "analog_id": "R15_chromanol_Cl_pos6",
        "target": "dct",
        "status": "ok",
        "smiles": "OCC1COc2c(ccc(O)c2Cl)C1",
        "topical_followup_score": 0.8750700000000001,
        "logP": 1.589,
        "QED": 0.747,
        "gap_eV": 3.92941240153,
        "affinity_probability_binary": 0.5359718799591064,
        "affinity_pred_value": 1.055057406425476,
        "wall_min": 54.96,
        "rmsd_mean_A": 0.39,
        "rmsd_max_A": 0.72,
        "rmsd_final_A": 0.53,
        "rmsd_last_third_A": 0.51,
        "ns_simulated": 60.0
    },
    {
        "name": "r16_02_tyr__R15_chromanol_Cl_pos6__60ns",
        "job_id": "r16_02_tyr",
        "analog_id": "R15_chromanol_Cl_pos6",
        "target": "tyr",
        "status": "ok",
        "smiles": "OCC1COc2c(ccc(O)c2Cl)C1",
        "topical_followup_score": 0.8750700000000001,
        "logP": 1.589,
        "QED": 0.747,
        "gap_eV": 3.92941240153,
        "affinity_probability_binary": 0.5249537825584412,
        "affinity_pred_value": 0.8515019416809082,
        "wall_min": 55.78,
        "rmsd_mean_A": 0.41,
        "rmsd_max_A": 0.8,
        "rmsd_final_A": 0.23,
        "rmsd_last_third_A": 0.35,
        "ns_simulated": 60.0
    }
]

```
### pilot/md_r16_chromanol_anchor_triad_100ns/summary.json

```json
[
    {
        "name": "r16_03_tgfb1__R15_chromanol_Cl_pos9__100ns",
        "job_id": "r16_03_tgfb1",
        "analog_id": "R15_chromanol_Cl_pos9",
        "target": "tgfb1",
        "status": "ok",
        "smiles": "OCC1COc2cc(O)c(Cl)cc2C1",
        "topical_followup_score": 0.8750700000000001,
        "logP": 1.589,
        "QED": 0.747,
        "gap_eV": 3.809593876030666,
        "affinity_probability_binary": 0.6822030544281006,
        "affinity_pred_value": 1.2207756042480469,
        "wall_min": 95.97,
        "rmsd_mean_A": 0.51,
        "rmsd_max_A": 0.69,
        "rmsd_final_A": 0.5,
        "rmsd_last_third_A": 0.51,
        "ns_simulated": 100.0
    },
    {
        "name": "r16_03_dct__R15_chromanol_Cl_pos9__100ns",
        "job_id": "r16_03_dct",
        "analog_id": "R15_chromanol_Cl_pos9",
        "target": "dct",
        "status": "ok",
        "smiles": "OCC1COc2cc(O)c(Cl)cc2C1",
        "topical_followup_score": 0.8750700000000001,
        "logP": 1.589,
        "QED": 0.747,
        "gap_eV": 3.809593876030666,
        "affinity_probability_binary": 0.5464680790901184,
        "affinity_pred_value": 0.8821029663085938,
        "wall_min": 102.92,
        "rmsd_mean_A": 0.32,
        "rmsd_max_A": 1.13,
        "rmsd_final_A": 0.51,
        "rmsd_last_third_A": 0.22,
        "ns_simulated": 100.0
    },
    {
        "name": "r16_02_tyr__R15_chromanol_Cl_pos6__100ns",
        "job_id": "r16_02_tyr",
        "analog_id": "R15_chromanol_Cl_pos6",
        "target": "tyr",
        "status": "ok",
        "smiles": "OCC1COc2c(ccc(O)c2Cl)C1",
        "topical_followup_score": 0.8750700000000001,
        "logP": 1.589,
        "QED": 0.747,
        "gap_eV": 3.92941240153,
        "affinity_probability_binary": 0.5249537825584412,
        "affinity_pred_value": 0.8515019416809082,
        "wall_min": 106.54,
        "rmsd_mean_A": 0.25,
        "rmsd_max_A": 0.62,
        "rmsd_final_A": 0.18,
        "rmsd_last_third_A": 0.24,
        "ns_simulated": 100.0
    }
]

```
### pilot/md_r16_chromanol_anchor_triad_200ns/summary.json

```json
[
    {
        "name": "r16_03_tgfb1__R15_chromanol_Cl_pos9__200ns",
        "job_id": "r16_03_tgfb1",
        "analog_id": "R15_chromanol_Cl_pos9",
        "target": "tgfb1",
        "status": "ok",
        "smiles": "OCC1COc2cc(O)c(Cl)cc2C1",
        "topical_followup_score": 0.8750700000000001,
        "logP": 1.589,
        "QED": 0.747,
        "gap_eV": 3.809593876030666,
        "affinity_probability_binary": 0.6822030544281006,
        "affinity_pred_value": 1.2207756042480469,
        "wall_min": 184.73,
        "rmsd_mean_A": 0.27,
        "rmsd_max_A": 0.71,
        "rmsd_final_A": 0.22,
        "rmsd_last_third_A": 0.24,
        "ns_simulated": 200.0
    },
    {
        "name": "r16_03_dct__R15_chromanol_Cl_pos9__200ns",
        "job_id": "r16_03_dct",
        "analog_id": "R15_chromanol_Cl_pos9",
        "target": "dct",
        "status": "ok",
        "smiles": "OCC1COc2cc(O)c(Cl)cc2C1",
        "topical_followup_score": 0.8750700000000001,
        "logP": 1.589,
        "QED": 0.747,
        "gap_eV": 3.809593876030666,
        "affinity_probability_binary": 0.5464680790901184,
        "affinity_pred_value": 0.8821029663085938,
        "wall_min": 176.31,
        "rmsd_mean_A": 0.34,
        "rmsd_max_A": 1.05,
        "rmsd_final_A": 0.66,
        "rmsd_last_third_A": 0.43,
        "ns_simulated": 200.0
    },
    {
        "name": "r16_02_tyr__R15_chromanol_Cl_pos6__200ns",
        "job_id": "r16_02_tyr",
        "analog_id": "R15_chromanol_Cl_pos6",
        "target": "tyr",
        "status": "ok",
        "smiles": "OCC1COc2c(ccc(O)c2Cl)C1",
        "topical_followup_score": 0.8750700000000001,
        "logP": 1.589,
        "QED": 0.747,
        "gap_eV": 3.92941240153,
        "affinity_probability_binary": 0.5249537825584412,
        "affinity_pred_value": 0.8515019416809082,
        "wall_min": 178.2,
        "rmsd_mean_A": 0.49,
        "rmsd_max_A": 0.8,
        "rmsd_final_A": 0.61,
        "rmsd_last_third_A": 0.57,
        "ns_simulated": 200.0
    }
]

```
### pilot/cpu_meaningful/target_evidence_gate_summary.json

```json
{
    "timestamp": "2026-05-06T12:46:04+09:00",
    "target_count": 31,
    "gate_counts": {
        "green": 13,
        "red": 8,
        "yellow": 10
    },
    "csv": "pilot/cpu_meaningful/target_evidence_gate.csv",
    "doc": "docs/TARGET_EVIDENCE_GATE.md"
}

```
### pilot/cpu_meaningful/chromanol_pose_sanity_gate_summary.json

```json
{
    "rows": 32,
    "ok_rows": 32,
    "full_pass_rows": 20,
    "full_pass_rate": 0.625,
    "gate_counts": {
        "pass": 20,
        "review": 12
    },
    "by_source": {
        "r15_chromanol": {
            "ok_rows": 14,
            "full_pass_rows": 9,
            "full_pass_rate": 0.6428571428571429,
            "gate_pass_rows": 9,
            "gate_review_rows": 5,
            "gate_fail_rows": 0,
            "mean_posebusters_pass_rate": 0.9772642857142857
        },
        "r16_chromanol_topical": {
            "ok_rows": 18,
            "full_pass_rows": 11,
            "full_pass_rate": 0.6111111111111112,
            "gate_pass_rows": 11,
            "gate_review_rows": 7,
            "gate_fail_rows": 0,
            "mean_posebusters_pass_rate": 0.9722166666666667
        }
    },
    "by_target": {
        "ar": {
            "ok_rows": 1,
            "full_pass_rows": 1,
            "full_pass_rate": 1.0,
            "gate_pass_rows": 1,
            "gate_review_rows": 0,
            "gate_fail_rows": 0,
            "mean_posebusters_pass_rate": 1.0
        },
        "ctgf": {
            "ok_rows": 1,
            "full_pass_rows": 1,
            "full_pass_rate": 1.0,
            "gate_pass_rows": 1,
            "gate_review_rows": 0,
            "gate_fail_rows": 0,
            "mean_posebusters_pass_rate": 1.0
        },
        "dct": {
            "ok_rows": 7,
            "full_pass_rows": 4,
            "full_pass_rate": 0.5714285714285714,
            "gate_pass_rows": 4,
            "gate_review_rows": 3,
            "gate_fail_rows": 0,
            "mean_posebusters_pass_rate": 0.9805
        },
        "lox": {
            "ok_rows": 1,
            "full_pass_rows": 1,
            "full_pass_rate": 1.0,
            "gate_pass_rows": 1,
            "gate_review_rows": 0,
            "gate_fail_rows": 0,
            "mean_posebusters_pass_rate": 1.0
        },
        "mitf": {
            "ok_rows": 1,
            "full_pass_rows": 0,
            "full_pass_rate": 0.0,
            "gate_pass_rows": 0,
            "gate_review_rows": 1,
            "gate_fail_rows": 0,
            "mean_posebusters_pass_rate": 0.9545
        },
        "mmp1": {
            "ok_rows": 1,
            "full_pass_rows": 0,
            "full_pass_rate": 0.0,
            "gate_pass_rows": 0,
            "gate_review_rows": 1,
            "gate_fail_rows": 0,
            "mean_posebusters_pass_rate": 0.9545
        },
        "ptgs2": {
            "ok_rows": 1,
            "full_pass_rows": 1,
            "full_pass_rate": 1.0,
            "gate_pass_rows": 1,
            "gate_review_rows": 0,
            "gate_fail_rows": 0,
            "mean_posebusters_pass_rate": 1.0
        },
        "sirt1": {
            "ok_rows": 1,
            "full_pass_rows": 0,
            "full_pass_rate": 0.0,
            "gate_pass_rows": 0,
            "gate_review_rows": 1,
            "gate_fail_rows": 0,
            "mean_posebusters_pass_rate": 0.9091
        },
        "srd5a1": {
            "ok_rows": 1,
            "full_pass_rows": 1,
            "full_pass_rate": 1.0,
            "gate_pass_rows": 1,
            "gate_review_rows": 0,
            "gate_fail_rows": 0,
            "mean_posebusters_pass_rate": 1.0
        },
        "srd5a2": {
            "ok_rows": 1,
            "full_pass_rows": 1,
            "full_pass_rate": 1.0,
            "gate_pass_rows": 1,
            "gate_review_rows": 0,
            "gate_fail_rows": 0,
            "mean_posebusters_pass_rate": 1.0
        },
        "srebp1": {
            "ok_rows": 1,
            "full_pass_rows": 1,
            "full_pass_rate": 1.0,
            "gate_pass_rows": 1,
            "gate_review_rows": 0,
            "gate_fail_rows": 0,
            "mean_posebusters_pass_rate": 1.0
        },
        "tgfb1": {
            "ok_rows": 7,
            "full_pass_rows": 2,
            "full_pass_rate": 0.2857142857142857,
            "gate_pass_rows": 2,
            "gate_review_rows": 5,
            "gate_fail_rows": 0,
            "mean_posebusters_pass_rate": 0.9350714285714287
        },
        "tyr": {
            "ok_rows": 7,
            "full_pass_rows": 6,
            "full_pass_rate": 0.8571428571428571,
            "gate_pass_rows": 6,
            "gate_review_rows": 1,
            "gate_fail_rows": 0,
            "mean_posebusters_pass_rate": 0.9935
        },
        "tyrp1": {
            "ok_rows": 1,
            "full_pass_rows": 1,
            "full_pass_rate": 1.0,
            "gate_pass_rows": 1,
            "gate_review_rows": 0,
            "gate_fail_rows": 0,
            "mean_posebusters_pass_rate": 1.0
        }
    }
}

```
### pilot/cpu_meaningful/active_learning_surrogate_summary.json

```json
{
    "timestamp": "2026-05-06T12:46:06+09:00",
    "training_rows": 32,
    "candidate_rows": 672,
    "targets": [
        "ar",
        "ctgf",
        "dct",
        "lox",
        "mc1r",
        "mitf",
        "mmp1",
        "nr3c1",
        "piezo1",
        "ptgs2",
        "rarg",
        "sirt1",
        "srd5a1",
        "srd5a2",
        "srebp1",
        "tgfb1",
        "tyr",
        "tyrp1"
    ],
    "loo_mae": 0.0765,
    "csv": "pilot/cpu_meaningful/active_learning_next_candidates.csv"
}

```
### pilot/cpu_meaningful/wetlab_result_ingestor_summary.json

```json
{
    "timestamp": "2026-05-06T12:46:35+09:00",
    "status": "no_wetlab_results_yet",
    "source": "data/wetlab_feedback_results.csv",
    "rows": 0
}

```
### pilot/cpu_meaningful/model_validation_uncertainty_summary.json

```json
{
    "timestamp": "2026-05-06T12:46:33+09:00",
    "training_rows": 32,
    "active_rows": 672,
    "training_scaffold_count": 1,
    "domain_counts": {
        "inside_domain": 0,
        "novel_scaffold": 640,
        "activity_cliff_risk": 32,
        "high_model_uncertainty": 0
    },
    "csv": "pilot/cpu_meaningful/model_validation_uncertainty_gate.csv"
}

```
### pilot/auto_queue_decision_policy.json

```json
{
    "timestamp": "2026-05-06T12:46:37+09:00",
    "matrix_csv": "pilot/cpu_meaningful/world_class_gap_closure_matrix.csv",
    "matrix_doc": "docs/WORLD_CLASS_GAP_CLOSURE.md",
    "readiness_counts": {
        "cheap_compute_or_paper_with_fto_caveat": 378,
        "triage_accumulating": 1193,
        "hold_or_benchmark_only": 757
    },
    "heavy_compute_permission_counts": {
        "short_triage_only": 378,
        "cheap_compute_only": 1193,
        "hold": 757
    },
    "paper_permission_counts": {
        "in_silico_with_fto_caveat": 378,
        "supplement_or_atlas_only": 1193,
        "methods_or_caveated_only": 757
    },
    "mmp1_zaff_status": "blocked_zaff_not_integrated",
    "r17_expanded_green_60ns_ok": 3,
    "r17_expanded_green_60ns_total": 3,
    "creative_discovery_status_counts": {
        "implemented_running": 1,
        "gap_detected": 1,
        "partial_post_filter_only": 1,
        "partial_chromanol_constrained_only": 1,
        "static_pocket_gate_only": 1,
        "roadmap_only": 1,
        "partial_decoy_gate_only": 1,
        "partial_gate_only": 1,
        "planned_gate_only": 1,
        "partial_deterministic_curator": 1
    },
    "creative_discovery_gate_counts": {
        "short_triage_allowed_only": 1,
        "block_target_specific_cofold_for_missing_msa": 1,
        "generation_requires_route_or_building_block_guard": 1,
        "new_scaffold_requires_novelty_synthesis_uncertainty_gate": 1,
        "ensemble_pocket_required_before_pocket_specific_generation": 1,
        "license_storage_stage1_required": 1,
        "new_generator_requires_benchmark_and_decoys": 1,
        "phenotype_objective_required_for_moa_claim": 1,
        "high_risk_modality_requires_separate_safety_ip_gate": 1,
        "curator_must_read_creative_matrix_each_tick": 1
    },
    "target_msa_missing_count": 14,
    "global_queue_policy": {
        "finish_already_running_r17_expanded_60ns": false,
        "allow_cpu_cheap_atlas": true,
        "no_new_chromanol_100_200ns_or_fe_or_synthesis_until_markush_fto": true,
        "no_mmp1_abfe_confirmed_claim_until_zaff_gate_pass": true,
        "emb3_quinone_requires_wetlab_safety_package": true,
        "boltz_only_claims_require_cross_model_decoy_or_plif_before_strong_language": true,
        "wetlab_first_when_dmtl_or_ivpt_ready": true,
        "creative_generation_requires_synthesis_or_prior_art_guard": true,
        "active_learning_short_cofold_fallback_enabled": true,
        "cryptic_pocket_generation_requires_ensemble_pocket_gate": true,
        "phenomics_generation_requires_signature_or_assay_gate": true,
        "target_msa_coverage_gap_blocks_target_queue": true,
        "new_scaffold_gpu_followup_requires_uncertainty_and_benchmark_gate": true
    },
    "top_next_actions": [
        {
            "candidate_id": "R15_chromanol_Cl_pos10",
            "target": "dct",
            "readiness": "cheap_compute_or_paper_with_fto_caveat",
            "heavy_compute_permission": "short_triage_only",
            "next_best_action": "prepare Markush/FTO package; use only completed data for caveated papers"
        },
        {
            "candidate_id": "R15_chromanol_Cl_pos10",
            "target": "tgfb1",
            "readiness": "cheap_compute_or_paper_with_fto_caveat",
            "heavy_compute_permission": "short_triage_only",
            "next_best_action": "prepare Markush/FTO package; use only completed data for caveated papers"
        },
        {
            "candidate_id": "R15_chromanol_Cl_pos10",
            "target": "tyr",
            "readiness": "cheap_compute_or_paper_with_fto_caveat",
            "heavy_compute_permission": "short_triage_only",
            "next_best_action": "prepare Markush/FTO package; use only completed data for caveated papers"
        },
        {
            "candidate_id": "R15_chromanol_Cl_pos6",
            "target": "dct",
            "readiness": "cheap_compute_or_paper_with_fto_caveat",
            "heavy_compute_permission": "short_triage_only",
            "next_best_action": "prepare Markush/FTO package; use only completed data for caveated papers"
        },
        {
            "candidate_id": "R15_chromanol_Cl_pos6",
            "target": "tgfb1",
            "readiness": "cheap_compute_or_paper_with_fto_caveat",
            "heavy_compute_permission": "short_triage_only",
            "next_best_action": "prepare Markush/FTO package; use only completed data for caveated papers"
        },
        {
            "candidate_id": "R15_chromanol_Cl_pos6",
            "target": "tyr",
            "readiness": "cheap_compute_or_paper_with_fto_caveat",
            "heavy_compute_permission": "short_triage_only",
            "next_best_action": "prepare Markush/FTO package; use only completed data for caveated papers"
        },
        {
            "candidate_id": "R15_chromanol_Cl_pos9",
            "target": "dct",
            "readiness": "cheap_compute_or_paper_with_fto_caveat",
            "heavy_compute_permission": "short_triage_only",
            "next_best_action": "prepare Markush/FTO package; use only completed data for caveated papers"
        },
        {
            "candidate_id": "R15_chromanol_Cl_pos9",
            "target": "tgfb1",
            "readiness": "cheap_compute_or_paper_with_fto_caveat",
            "heavy_compute_permission": "short_triage_only",
            "next_best_action": "prepare Markush/FTO package; use only completed data for caveated papers"
        },
        {
            "candidate_id": "R15_chromanol_Cl_pos9",
            "target": "tyr",
            "readiness": "cheap_compute_or_paper_with_fto_caveat",
            "heavy_compute_permission": "short_triage_only",
            "next_best_action": "prepare Markush/FTO package; use only completed data for caveated papers"
        },
        {
            "candidate_id": "R15_chromanol_Me6_Me10",
            "target": "dct",
            "readiness": "cheap_compute_or_paper_with_fto_caveat",
            "heavy_compute_permission": "short_triage_only",
            "next_best_action": "prepare Markush/FTO package; use only completed data for caveated papers"
        },
        {
            "candidate_id": "R15_chromanol_Me6_Me10",
            "target": "tgfb1",
            "readiness": "cheap_compute_or_paper_with_fto_caveat",
            "heavy_compute_permission": "short_triage_only",
            "next_best_action": "prepare Markush/FTO package; use only completed data for caveated papers"
        },
        {
            "candidate_id": "R15_chromanol_Me6_Me10",
            "target": "tyr",
            "readiness": "cheap_compute_or_paper_with_fto_caveat",
            "heavy_compute_permission": "short_triage_only",
            "next_best_action": "prepare Markush/FTO package; use only completed data for caveated papers"
        },
        {
            "candidate_id": "R15_chromanol_Me6_Me9",
            "target": "dct",
            "readiness": "cheap_compute_or_paper_with_fto_caveat",
            "heavy_compute_permission": "short_triage_only",
            "next_best_action": "prepare Markush/FTO package; use only completed data for caveated papers"
        },
        {
            "candidate_id": "R15_chromanol_Me6_Me9",
            "target": "tgfb1",
            "readiness": "cheap_compute_or_paper_with_fto_caveat",
            "heavy_compute_permission": "short_triage_only",
            "next_best_action": "prepare Markush/FTO package; use only completed data for caveated papers"
        },
        {
            "candidate_id": "R15_chromanol_Me6_Me9",
            "target": "tyr",
            "readiness": "cheap_compute_or_paper_with_fto_caveat",
            "heavy_compute_permission": "short_triage_only",
            "next_best_action": "prepare Markush/FTO package; use only completed data for caveated papers"
        },
        {
            "candidate_id": "R15_chromanol_Me9_Me10",
            "target": "dct",
            "readiness": "cheap_compute_or_paper_with_fto_caveat",
            "heavy_compute_permission": "short_triage_only",
            "next_best_action": "prepare Markush/FTO package; use only completed data for caveated papers"
        },
        {
            "candidate_id": "R15_chromanol_Me9_Me10",
            "target": "tgfb1",
            "readiness": "cheap_compute_or_paper_with_fto_caveat",
            "heavy_compute_permission": "short_triage_only",
            "next_best_action": "prepare Markush/FTO package; use only completed data for caveated papers"
        },
        {
            "candidate_id": "R15_chromanol_Me9_Me10",
            "target": "tyr",
            "readiness": "cheap_compute_or_paper_with_fto_caveat",
            "heavy_compute_permission": "short_triage_only",
            "next_best_action": "prepare Markush/FTO package; use only completed data for caveated papers"
        },
        {
            "candidate_id": "chromanol_arom10_CN_dct",
            "target": "dct",
            "readiness": "cheap_compute_or_paper_with_fto_caveat",
            "heavy_compute_permission": "short_triage_only",
            "next_best_action": "prepare Markush/FTO package; use only completed data for caveated papers"
        },
        {
            "candidate_id": "chromanol_arom10_CN_tgfb1",
            "target": "tgfb1",
            "readiness": "cheap_compute_or_paper_with_fto_caveat",
            "heavy_compute_permission": "short_triage_only",
            "next_best_action": "prepare Markush/FTO package; use only completed data for caveated papers"
        }
    ]
}

```

## Latest Result Files

```text
2026-05-02 21:36 3302 pilot/cpu_meaningful/active_learning_next_cofold_batch18.csv
2026-05-02 21:37 2016 pilot/cpu_meaningful/active_learning_next_cofold_batch19_manifest.csv
2026-05-02 21:44 3371 pilot/cpu_meaningful/active_learning_next_cofold_batch19.csv
2026-05-02 22:37 1868 pilot/cpu_meaningful/active_learning_next_cofold_batch20_manifest.csv
2026-05-02 22:41 1868 pilot/cpu_meaningful/active_learning_next_cofold_batch21_manifest.csv
2026-05-02 22:48 3227 pilot/cpu_meaningful/active_learning_next_cofold_batch21.csv
2026-05-02 22:52 2058 pilot/cpu_meaningful/active_learning_next_cofold_batch22_manifest.csv
2026-05-02 22:59 2187 pilot/cpu_meaningful/active_learning_next_cofold_batch23_manifest.csv
2026-05-02 22:59 3429 pilot/cpu_meaningful/active_learning_next_cofold_batch22.csv
2026-05-02 23:01 876236 pilot/cpu_meaningful/xtb_npass_top5000_hetero6_refine_36conf.csv
2026-05-02 23:05 1931 pilot/cpu_meaningful/active_learning_next_cofold_batch24_manifest.csv
2026-05-02 23:05 3548 pilot/cpu_meaningful/active_learning_next_cofold_batch23.csv
2026-05-02 23:11 1964 pilot/cpu_meaningful/active_learning_next_cofold_batch25_manifest.csv
2026-05-02 23:11 3308 pilot/cpu_meaningful/active_learning_next_cofold_batch24.csv
2026-05-02 23:18 1969 pilot/cpu_meaningful/active_learning_next_cofold_batch26_manifest.csv
2026-05-02 23:18 3327 pilot/cpu_meaningful/active_learning_next_cofold_batch25.csv
2026-05-02 23:24 3319 pilot/cpu_meaningful/active_learning_next_cofold_batch26.csv
2026-05-02 23:25 1963 pilot/cpu_meaningful/active_learning_next_cofold_batch27_manifest.csv
2026-05-02 23:30 3327 pilot/cpu_meaningful/active_learning_next_cofold_batch27.csv
2026-05-02 23:30 778 pilot/cpu_meaningful/active_learning_next_cofold_batch28_manifest.csv
2026-05-02 23:35 1286 pilot/cpu_meaningful/active_learning_next_cofold_batch28.csv
2026-05-03 00:03 2531 pilot/cpu_meaningful/active_learning_next_cofold_batch29_manifest.csv
2026-05-03 00:11 3896 pilot/cpu_meaningful/active_learning_next_cofold_batch29.csv
2026-05-03 00:12 2973 pilot/cpu_meaningful/active_learning_next_cofold_batch30_manifest.csv
2026-05-03 00:20 4355 pilot/cpu_meaningful/active_learning_next_cofold_batch30.csv
2026-05-03 00:26 110874 pilot/cpu_meaningful/xtb_npass_top500_hetero2_refine_288conf.csv
2026-05-03 00:37 2840 pilot/cpu_meaningful/active_learning_next_cofold_batch31_manifest.csv
2026-05-03 00:47 4217 pilot/cpu_meaningful/active_learning_next_cofold_batch31.csv
2026-05-03 00:50 2022 pilot/cpu_meaningful/active_learning_next_cofold_batch32_manifest.csv
2026-05-03 00:59 2051 pilot/cpu_meaningful/active_learning_next_cofold_batch33_manifest.csv
2026-05-03 00:59 3384 pilot/cpu_meaningful/active_learning_next_cofold_batch32.csv
2026-05-03 01:09 3414 pilot/cpu_meaningful/active_learning_next_cofold_batch33.csv
2026-05-03 01:33 228692 pilot/cpu_meaningful/xtb_npass_top1000_hetero3_refine_288conf.csv
2026-05-03 05:31 494846 pilot/cpu_meaningful/xtb_npass_top3000_hetero8_refine_288conf.csv
2026-05-03 06:02 728954 pilot/cpu_meaningful/xtb_npass_top3000_hetero5_refine_288conf.csv
2026-05-03 09:03 379742 pilot/cpu_meaningful/xtb_npass_top9000_hetero9_refine_288conf.csv
2026-05-03 09:35 655856 pilot/cpu_meaningful/xtb_npass_top7000_hetero7_refine_288conf.csv
2026-05-03 09:44 111437 pilot/cpu_meaningful/xtb_npass_top500_hetero2_refine_336conf.csv
2026-05-03 10:32 272728 pilot/cpu_meaningful/xtb_npass_top9997_hetero10_refine_288conf.csv
2026-05-03 10:46 228715 pilot/cpu_meaningful/xtb_npass_top1000_hetero3_refine_336conf.csv
2026-05-03 15:42 494892 pilot/cpu_meaningful/xtb_npass_top3000_hetero8_refine_336conf.csv
2026-05-03 17:04 729029 pilot/cpu_meaningful/xtb_npass_top3000_hetero5_refine_336conf.csv
2026-05-03 17:24 7600 pilot/md_r17_chromanol_generative_green_120ns/summary.json
2026-05-03 19:57 379771 pilot/cpu_meaningful/xtb_npass_top9000_hetero9_refine_336conf.csv
2026-05-03 20:41 111450 pilot/cpu_meaningful/xtb_npass_top500_hetero2_refine_384conf.csv
2026-05-03 21:01 655922 pilot/cpu_meaningful/xtb_npass_top7000_hetero7_refine_336conf.csv
2026-05-03 21:54 272757 pilot/cpu_meaningful/xtb_npass_top9997_hetero10_refine_336conf.csv
2026-05-03 21:59 228723 pilot/cpu_meaningful/xtb_npass_top1000_hetero3_refine_384conf.csv
2026-05-04 00:10 1243 pilot/md_r14_5_r12_23_herbal_xref_60ns/summary.json
2026-05-04 00:34 1077 pilot/abfe_mmp1_holo_zn/sanity_md/summary.json
2026-05-04 00:35 482 pilot/abfe_mmp1_holo_zn/complex/summary.json
2026-05-04 03:10 494859 pilot/cpu_meaningful/xtb_npass_top3000_hetero8_refine_384conf.csv
2026-05-04 04:34 729025 pilot/cpu_meaningful/xtb_npass_top3000_hetero5_refine_384conf.csv
2026-05-04 07:43 379746 pilot/cpu_meaningful/xtb_npass_top9000_hetero9_refine_384conf.csv
2026-05-04 08:44 655894 pilot/cpu_meaningful/xtb_npass_top7000_hetero7_refine_384conf.csv
2026-05-04 09:38 272715 pilot/cpu_meaningful/xtb_npass_top9997_hetero10_refine_384conf.csv
2026-05-04 15:13 526 pilot/abfe_mmp1_holo_zn_embelin/complex/summary.json
2026-05-04 16:12 1174265 pilot/cpu_meaningful/xtb_npass_top5000_hetero3_refine_384conf.csv
2026-05-04 16:15 371 pilot/active_learning/round1/summary.json
2026-05-04 17:42 478933 pilot/cpu_meaningful/xtb_npass_top2000_hetero5_refine_256conf.csv
2026-05-04 20:53 404 pilot/boltz2_top500_mmp1/summary.json
2026-05-04 21:06 2009 pilot/of3_aqaff_tier1/summary.json
2026-05-04 22:18 141 pilot/dude_benchmark_mmp1/summary.json
2026-05-04 22:40 329 pilot/active_learning/round2/summary.json
2026-05-05 03:03 553 pilot/mmp1_apo_zn_md_100ns/summary.json
2026-05-05 04:48 82223 pilot/cpu_meaningful/xtb_npass_top500_refine_432conf.csv
2026-05-05 06:33 82272 pilot/cpu_meaningful/xtb_npass_top500_refine_480conf.csv
2026-05-05 08:13 82235 pilot/cpu_meaningful/xtb_npass_top500_refine_528conf.csv
2026-05-05 09:58 82257 pilot/cpu_meaningful/xtb_npass_top500_refine_576conf.csv
2026-05-05 10:39 22109 pilot/cpu_meaningful/xtb_npass_top500_refine_624conf.csv
2026-05-05 12:47 289422 pilot/cpu_meaningful/xtb_npass_top9997_hetero10_refine_432conf.csv
2026-05-05 14:11 1120 pilot/abfe_mmp1_holo_zn_embelin/holo_md_100ns/summary.json
2026-05-05 15:48 284745 pilot/cpu_meaningful/xtb_npass_top9997_hetero10_refine_624conf.csv
2026-05-05 19:09 284702 pilot/cpu_meaningful/xtb_npass_top9997_hetero10_refine_720conf.csv
2026-05-06 00:49 281663 pilot/cpu_meaningful/xtb_npass_top9997_hetero10_refine_528conf.csv
2026-05-06 01:49 289514 pilot/cpu_meaningful/xtb_npass_top9997_hetero10_refine_816conf.csv
2026-05-06 03:18 281662 pilot/cpu_meaningful/xtb_npass_top9997_hetero10_refine_480conf.csv
2026-05-06 05:33 281632 pilot/cpu_meaningful/xtb_npass_top9997_hetero10_refine_576conf.csv
2026-05-06 07:50 18917 pilot/cpu_meaningful/xtb_npass_top9997_hetero10_refine_672conf.csv
2026-05-06 12:46 3646 pilot/cpu_meaningful/creative_discovery_gap_matrix.csv
```

## CSV Snapshots

```text
```

## Recent Logs

### pilot/auto_queue_cpu_gpu_daemon.log tail -120

```text
[2026-05-06T11:47:21+09:00] GPU no pending planner task
[2026-05-06T11:47:22+09:00] CPU planner: spec=none reason=all configured xTB refinement outputs exist or are running through 384conf idle=100%
[2026-05-06T11:47:22+09:00] CPU_IDLE_GAP_UNRESOLVED idle=100% active_refines=0 planner=none
[2026-05-06T11:47:22+09:00] CPU no pending planner task
[2026-05-06T11:49:16+09:00] GPU busy by project jobs: 1
[2026-05-06T11:49:17+09:00] CPU planner: spec=none reason=all configured xTB refinement outputs exist or are running through 384conf idle=99%
[2026-05-06T11:49:17+09:00] CPU_IDLE_GAP_UNRESOLVED idle=99% active_refines=0 planner=none
[2026-05-06T11:49:17+09:00] CPU no pending planner task
[2026-05-06T11:51:10+09:00] GPU busy by project jobs: 1
[2026-05-06T11:51:11+09:00] CPU planner: spec=none reason=all configured xTB refinement outputs exist or are running through 384conf idle=99%
[2026-05-06T11:51:11+09:00] CPU_IDLE_GAP_UNRESOLVED idle=99% active_refines=0 planner=none
[2026-05-06T11:51:11+09:00] CPU no pending planner task
[2026-05-06T11:53:04+09:00] GPU busy by project jobs: 1
[2026-05-06T11:53:05+09:00] CPU planner: spec=none reason=all configured xTB refinement outputs exist or are running through 384conf idle=96%
[2026-05-06T11:53:05+09:00] CPU_IDLE_GAP_UNRESOLVED idle=96% active_refines=0 planner=none
[2026-05-06T11:53:05+09:00] CPU no pending planner task
[2026-05-06T11:54:58+09:00] GPU busy by project jobs: 1
[2026-05-06T11:54:59+09:00] CPU planner: spec=none reason=all configured xTB refinement outputs exist or are running through 384conf idle=100%
[2026-05-06T11:54:59+09:00] CPU_IDLE_GAP_UNRESOLVED idle=100% active_refines=0 planner=none
[2026-05-06T11:54:59+09:00] CPU no pending planner task
[2026-05-06T11:57:12+09:00] GPU busy by project jobs: 1
[2026-05-06T11:57:19+09:00] CPU planner: spec=none reason=all configured xTB refinement outputs exist or are running through 384conf idle=96%
[2026-05-06T11:57:19+09:00] CPU_IDLE_GAP_UNRESOLVED idle=96% active_refines=0 planner=none
[2026-05-06T11:57:19+09:00] CPU no pending planner task
[2026-05-06T11:59:12+09:00] GPU busy by project jobs: 1
[2026-05-06T11:59:13+09:00] CPU planner: spec=none reason=all configured xTB refinement outputs exist or are running through 384conf idle=100%
[2026-05-06T11:59:13+09:00] CPU_IDLE_GAP_UNRESOLVED idle=100% active_refines=0 planner=none
[2026-05-06T11:59:13+09:00] CPU no pending planner task
[2026-05-06T12:01:06+09:00] GPU busy by project jobs: 1
[2026-05-06T12:01:49+09:00] CPU planner: spec=none reason=all configured xTB refinement outputs exist or are running through 384conf idle=95%
[2026-05-06T12:01:49+09:00] CPU_IDLE_GAP_UNRESOLVED idle=95% active_refines=0 planner=none
[2026-05-06T12:01:49+09:00] CPU no pending planner task
[2026-05-06T12:03:42+09:00] GPU busy by project jobs: 1
[2026-05-06T12:03:43+09:00] CPU planner: spec=none reason=all configured xTB refinement outputs exist or are running through 384conf idle=92%
[2026-05-06T12:03:43+09:00] CPU_IDLE_GAP_UNRESOLVED idle=92% active_refines=0 planner=none
[2026-05-06T12:03:43+09:00] CPU no pending planner task
[2026-05-06T12:05:35+09:00] GPU busy by project jobs: 1
[2026-05-06T12:05:36+09:00] CPU planner: spec=none reason=all configured xTB refinement outputs exist or are running through 384conf idle=100%
[2026-05-06T12:05:36+09:00] CPU_IDLE_GAP_UNRESOLVED idle=100% active_refines=0 planner=none
[2026-05-06T12:05:36+09:00] CPU no pending planner task
[2026-05-06T12:07:31+09:00] GPU busy by project jobs: 1
[2026-05-06T12:07:32+09:00] CPU planner: spec=none reason=all configured xTB refinement outputs exist or are running through 384conf idle=100%
[2026-05-06T12:07:32+09:00] CPU_IDLE_GAP_UNRESOLVED idle=100% active_refines=0 planner=none
[2026-05-06T12:07:32+09:00] CPU no pending planner task
[2026-05-06T12:09:24+09:00] GPU busy by project jobs: 1
[2026-05-06T12:09:26+09:00] CPU planner: spec=none reason=all configured xTB refinement outputs exist or are running through 384conf idle=99%
[2026-05-06T12:09:26+09:00] CPU_IDLE_GAP_UNRESOLVED idle=99% active_refines=0 planner=none
[2026-05-06T12:09:26+09:00] CPU no pending planner task
[2026-05-06T12:11:38+09:00] GPU busy by project jobs: 1
[2026-05-06T12:11:39+09:00] CPU planner: spec=none reason=all configured xTB refinement outputs exist or are running through 384conf idle=96%
[2026-05-06T12:11:39+09:00] CPU_IDLE_GAP_UNRESOLVED idle=96% active_refines=0 planner=none
[2026-05-06T12:11:39+09:00] CPU no pending planner task
[2026-05-06T12:13:35+09:00] GPU busy by project jobs: 1
[2026-05-06T12:13:39+09:00] CPU planner: spec=none reason=all configured xTB refinement outputs exist or are running through 384conf idle=95%
[2026-05-06T12:13:39+09:00] CPU_IDLE_GAP_UNRESOLVED idle=95% active_refines=0 planner=none
[2026-05-06T12:13:39+09:00] CPU no pending planner task
[2026-05-06T12:15:48+09:00] GPU busy by project jobs: 1
[2026-05-06T12:15:50+09:00] CPU planner: spec=none reason=all configured xTB refinement outputs exist or are running through 384conf idle=100%
[2026-05-06T12:15:50+09:00] CPU_IDLE_GAP_UNRESOLVED idle=100% active_refines=0 planner=none
[2026-05-06T12:15:50+09:00] CPU no pending planner task
[2026-05-06T12:17:56+09:00] GPU busy by project jobs: 1
[2026-05-06T12:17:59+09:00] CPU planner: spec=none reason=all configured xTB refinement outputs exist or are running through 384conf idle=99%
[2026-05-06T12:17:59+09:00] CPU_IDLE_GAP_UNRESOLVED idle=99% active_refines=0 planner=none
[2026-05-06T12:17:59+09:00] CPU no pending planner task
[2026-05-06T12:19:52+09:00] GPU busy by project jobs: 1
[2026-05-06T12:19:53+09:00] CPU planner: spec=none reason=all configured xTB refinement outputs exist or are running through 384conf idle=94%
[2026-05-06T12:19:53+09:00] CPU_IDLE_GAP_UNRESOLVED idle=94% active_refines=0 planner=none
[2026-05-06T12:19:53+09:00] CPU no pending planner task
[2026-05-06T12:21:57+09:00] GPU busy by project jobs: 1
[2026-05-06T12:22:11+09:00] CPU planner: spec=none reason=all configured xTB refinement outputs exist or are running through 384conf idle=96%
[2026-05-06T12:22:11+09:00] CPU_IDLE_GAP_UNRESOLVED idle=96% active_refines=0 planner=none
[2026-05-06T12:22:11+09:00] CPU no pending planner task
[2026-05-06T12:24:05+09:00] GPU busy by project jobs: 1
[2026-05-06T12:24:10+09:00] CPU planner: spec=none reason=all configured xTB refinement outputs exist or are running through 384conf idle=96%
[2026-05-06T12:24:10+09:00] CPU_IDLE_GAP_UNRESOLVED idle=96% active_refines=0 planner=none
[2026-05-06T12:24:10+09:00] CPU no pending planner task
[2026-05-06T12:26:02+09:00] GPU busy by project jobs: 1
[2026-05-06T12:26:03+09:00] CPU planner: spec=none reason=all configured xTB refinement outputs exist or are running through 384conf idle=99%
[2026-05-06T12:26:03+09:00] CPU_IDLE_GAP_UNRESOLVED idle=99% active_refines=0 planner=none
[2026-05-06T12:26:03+09:00] CPU no pending planner task
[2026-05-06T12:27:58+09:00] GPU busy by project jobs: 1
[2026-05-06T12:27:59+09:00] CPU planner: spec=none reason=all configured xTB refinement outputs exist or are running through 384conf idle=100%
[2026-05-06T12:27:59+09:00] CPU_IDLE_GAP_UNRESOLVED idle=100% active_refines=0 planner=none
[2026-05-06T12:27:59+09:00] CPU no pending planner task
[2026-05-06T12:29:51+09:00] GPU busy by project jobs: 1
[2026-05-06T12:29:53+09:00] CPU planner: spec=none reason=all configured xTB refinement outputs exist or are running through 384conf idle=99%
[2026-05-06T12:29:53+09:00] CPU_IDLE_GAP_UNRESOLVED idle=99% active_refines=0 planner=none
[2026-05-06T12:29:53+09:00] CPU no pending planner task
[2026-05-06T12:31:45+09:00] GPU busy by project jobs: 1
[2026-05-06T12:31:46+09:00] CPU planner: spec=none reason=all configured xTB refinement outputs exist or are running through 384conf idle=100%
[2026-05-06T12:31:46+09:00] CPU_IDLE_GAP_UNRESOLVED idle=100% active_refines=0 planner=none
[2026-05-06T12:31:46+09:00] CPU no pending planner task
[2026-05-06T12:33:39+09:00] GPU busy by project jobs: 1
[2026-05-06T12:33:40+09:00] CPU planner: spec=none reason=all configured xTB refinement outputs exist or are running through 384conf idle=100%
[2026-05-06T12:33:40+09:00] CPU_IDLE_GAP_UNRESOLVED idle=100% active_refines=0 planner=none
[2026-05-06T12:33:40+09:00] CPU no pending planner task
[2026-05-06T12:35:34+09:00] GPU busy by project jobs: 1
[2026-05-06T12:35:35+09:00] CPU planner: spec=none reason=all configured xTB refinement outputs exist or are running through 384conf idle=82%
[2026-05-06T12:35:35+09:00] CPU_IDLE_GAP_UNRESOLVED idle=82% active_refines=0 planner=none
[2026-05-06T12:35:35+09:00] CPU no pending planner task
[2026-05-06T12:37:29+09:00] GPU busy by project jobs: 1
[2026-05-06T12:37:58+09:00] CPU planner: spec=none reason=all configured xTB refinement outputs exist or are running through 384conf idle=96%
[2026-05-06T12:37:58+09:00] CPU_IDLE_GAP_UNRESOLVED idle=96% active_refines=0 planner=none
[2026-05-06T12:37:58+09:00] CPU no pending planner task
[2026-05-06T12:39:54+09:00] GPU busy by project jobs: 1
[2026-05-06T12:39:58+09:00] CPU planner: spec=none reason=all configured xTB refinement outputs exist or are running through 384conf idle=97%
[2026-05-06T12:39:58+09:00] CPU_IDLE_GAP_UNRESOLVED idle=97% active_refines=0 planner=none
[2026-05-06T12:39:58+09:00] CPU no pending planner task
[2026-05-06T12:41:51+09:00] GPU busy by project jobs: 1
[2026-05-06T12:41:53+09:00] CPU planner: spec=none reason=all configured xTB refinement outputs exist or are running through 384conf idle=95%
[2026-05-06T12:41:53+09:00] CPU_IDLE_GAP_UNRESOLVED idle=95% active_refines=0 planner=none
[2026-05-06T12:41:53+09:00] CPU no pending planner task
[2026-05-06T12:43:56+09:00] GPU busy by project jobs: 1
[2026-05-06T12:43:58+09:00] CPU planner: spec=none reason=all configured xTB refinement outputs exist or are running through 384conf idle=95%
[2026-05-06T12:43:58+09:00] CPU_IDLE_GAP_UNRESOLVED idle=95% active_refines=0 planner=none
[2026-05-06T12:43:58+09:00] CPU no pending planner task
[2026-05-06T12:46:10+09:00] GPU busy by project jobs: 1
[2026-05-06T12:46:11+09:00] CPU planner: spec=none reason=all configured xTB refinement outputs exist or are running through 384conf idle=67%
[2026-05-06T12:46:11+09:00] CPU_IDLE_GAP_UNRESOLVED idle=67% active_refines=0 planner=none
[2026-05-06T12:46:11+09:00] CPU no pending planner task

```
### pilot/monitor_supervisor.log tail -80

```text
[2026-04-30T19:46:42+09:00] monitor supervisor start
[2026-04-30T19:58:17+09:00] monitor supervisor start
[2026-04-30T19:58:17+09:00] codex curator missing; starting scripts/codex_curator_loop.sh
[2026-04-30T19:58:17+09:00] codex curator pid=660832
[2026-04-30T20:00:12+09:00] codex curator missing; starting scripts/codex_curator_loop.sh
[2026-04-30T20:00:12+09:00] codex curator pid=664478
[2026-04-30T20:01:27+09:00] monitor supervisor already running; exiting duplicate
[2026-04-30T20:02:26+09:00] monitor supervisor start
[2026-04-30T20:02:26+09:00] queue daemon missing; starting scripts/auto_queue_cpu_gpu_daemon.sh
[2026-04-30T20:02:26+09:00] queue daemon pid=668962
[2026-04-30T20:02:26+09:00] codex curator missing; starting scripts/codex_curator_loop.sh
[2026-04-30T20:02:26+09:00] codex curator pid=668983
[2026-05-01T00:06:47+09:00] monitor supervisor start
[2026-05-02T21:42:21+09:00] QUEUE_DRAIN_MODE enabled; monitor/guard/curator triggers removed
[2026-05-02T21:42:41+09:00] monitor supervisor stopped: trigger removed
[2026-05-02T21:45:20+09:00] monitor supervisor not started: QUEUE_DRAIN_MODE present
[2026-05-03T00:50:17+09:00] monitor supervisor start
[2026-05-03T11:07:32+09:00] queue daemon missing; starting scripts/auto_queue_cpu_gpu_daemon.sh
[2026-05-03T11:07:32+09:00] queue daemon pid=2512206

```
### pilot/codex_curator_actions.log tail -80

```text
2026-05-06T10:34:55+09:00 CPU_IDLE_GAP_UNRESOLVED idle=100% active_refines=0 planner=none
2026-05-06T10:36:49+09:00 CPU_IDLE_GAP_UNRESOLVED idle=100% active_refines=0 planner=none
2026-05-06T10:38:43+09:00 CPU_IDLE_GAP_UNRESOLVED idle=100% active_refines=0 planner=none
2026-05-06T10:40:37+09:00 CPU_IDLE_GAP_UNRESOLVED idle=96% active_refines=0 planner=none
[2026-05-06T10:40:49+09:00] curator failed rc=127
2026-05-06T10:42:33+09:00 CPU_IDLE_GAP_UNRESOLVED idle=100% active_refines=0 planner=none
2026-05-06T10:44:27+09:00 CPU_IDLE_GAP_UNRESOLVED idle=100% active_refines=0 planner=none
2026-05-06T10:46:21+09:00 CPU_IDLE_GAP_UNRESOLVED idle=100% active_refines=0 planner=none
2026-05-06T10:48:15+09:00 CPU_IDLE_GAP_UNRESOLVED idle=100% active_refines=0 planner=none
2026-05-06T10:50:10+09:00 CPU_IDLE_GAP_UNRESOLVED idle=100% active_refines=0 planner=none
[2026-05-06T10:51:16+09:00] curator failed rc=127
2026-05-06T10:52:04+09:00 CPU_IDLE_GAP_UNRESOLVED idle=100% active_refines=0 planner=none
2026-05-06T10:53:58+09:00 CPU_IDLE_GAP_UNRESOLVED idle=100% active_refines=0 planner=none
2026-05-06T10:55:54+09:00 CPU_IDLE_GAP_UNRESOLVED idle=100% active_refines=0 planner=none
2026-05-06T10:57:48+09:00 CPU_IDLE_GAP_UNRESOLVED idle=100% active_refines=0 planner=none
2026-05-06T10:59:42+09:00 CPU_IDLE_GAP_UNRESOLVED idle=100% active_refines=0 planner=none
2026-05-06T11:01:36+09:00 CPU_IDLE_GAP_UNRESOLVED idle=96% active_refines=0 planner=none
[2026-05-06T11:01:41+09:00] curator failed rc=127
2026-05-06T11:03:32+09:00 CPU_IDLE_GAP_UNRESOLVED idle=100% active_refines=0 planner=none
2026-05-06T11:05:26+09:00 CPU_IDLE_GAP_UNRESOLVED idle=99% active_refines=0 planner=none
2026-05-06T11:07:20+09:00 CPU_IDLE_GAP_UNRESOLVED idle=100% active_refines=0 planner=none
2026-05-06T11:09:14+09:00 CPU_IDLE_GAP_UNRESOLVED idle=99% active_refines=0 planner=none
2026-05-06T11:11:10+09:00 CPU_IDLE_GAP_UNRESOLVED idle=100% active_refines=0 planner=none
[2026-05-06T11:12:07+09:00] curator failed rc=127
2026-05-06T11:13:03+09:00 CPU_IDLE_GAP_UNRESOLVED idle=100% active_refines=0 planner=none
2026-05-06T11:14:57+09:00 CPU_IDLE_GAP_UNRESOLVED idle=100% active_refines=0 planner=none
2026-05-06T11:16:51+09:00 CPU_IDLE_GAP_UNRESOLVED idle=99% active_refines=0 planner=none
2026-05-06T11:18:47+09:00 CPU_IDLE_GAP_UNRESOLVED idle=100% active_refines=0 planner=none
2026-05-06T11:20:41+09:00 CPU_IDLE_GAP_UNRESOLVED idle=100% active_refines=0 planner=none
[2026-05-06T11:22:33+09:00] curator failed rc=127
2026-05-06T11:22:35+09:00 CPU_IDLE_GAP_UNRESOLVED idle=100% active_refines=0 planner=none
2026-05-06T11:24:29+09:00 CPU_IDLE_GAP_UNRESOLVED idle=100% active_refines=0 planner=none
2026-05-06T11:26:25+09:00 CPU_IDLE_GAP_UNRESOLVED idle=100% active_refines=0 planner=none
2026-05-06T11:28:19+09:00 CPU_IDLE_GAP_UNRESOLVED idle=100% active_refines=0 planner=none
2026-05-06T11:30:12+09:00 CPU_IDLE_GAP_UNRESOLVED idle=100% active_refines=0 planner=none
2026-05-06T11:32:08+09:00 CPU_IDLE_GAP_UNRESOLVED idle=100% active_refines=0 planner=none
[2026-05-06T11:33:01+09:00] curator failed rc=127
2026-05-06T11:34:02+09:00 CPU_IDLE_GAP_UNRESOLVED idle=100% active_refines=0 planner=none
2026-05-06T11:35:56+09:00 CPU_IDLE_GAP_UNRESOLVED idle=100% active_refines=0 planner=none
2026-05-06T11:37:50+09:00 CPU_IDLE_GAP_UNRESOLVED idle=100% active_refines=0 planner=none
2026-05-06T11:39:46+09:00 CPU_IDLE_GAP_UNRESOLVED idle=100% active_refines=0 planner=none
2026-05-06T11:41:40+09:00 CPU_IDLE_GAP_UNRESOLVED idle=100% active_refines=0 planner=none
[2026-05-06T11:43:27+09:00] curator failed rc=127
2026-05-06T11:43:34+09:00 CPU_IDLE_GAP_UNRESOLVED idle=100% active_refines=0 planner=none
2026-05-06T11:45:28+09:00 CPU_IDLE_GAP_UNRESOLVED idle=100% active_refines=0 planner=none
2026-05-06T11:47:22+09:00 CPU_IDLE_GAP_UNRESOLVED idle=100% active_refines=0 planner=none
2026-05-06T11:49:17+09:00 CPU_IDLE_GAP_UNRESOLVED idle=99% active_refines=0 planner=none
2026-05-06T11:51:11+09:00 CPU_IDLE_GAP_UNRESOLVED idle=99% active_refines=0 planner=none
2026-05-06T11:53:05+09:00 CPU_IDLE_GAP_UNRESOLVED idle=96% active_refines=0 planner=none
[2026-05-06T11:53:56+09:00] curator failed rc=127
2026-05-06T11:54:59+09:00 CPU_IDLE_GAP_UNRESOLVED idle=100% active_refines=0 planner=none
2026-05-06T11:57:19+09:00 CPU_IDLE_GAP_UNRESOLVED idle=96% active_refines=0 planner=none
2026-05-06T11:59:13+09:00 CPU_IDLE_GAP_UNRESOLVED idle=100% active_refines=0 planner=none
2026-05-06T12:01:49+09:00 CPU_IDLE_GAP_UNRESOLVED idle=95% active_refines=0 planner=none
2026-05-06T12:03:43+09:00 CPU_IDLE_GAP_UNRESOLVED idle=92% active_refines=0 planner=none
[2026-05-06T12:04:26+09:00] curator failed rc=127
2026-05-06T12:05:36+09:00 CPU_IDLE_GAP_UNRESOLVED idle=100% active_refines=0 planner=none
2026-05-06T12:07:32+09:00 CPU_IDLE_GAP_UNRESOLVED idle=100% active_refines=0 planner=none
2026-05-06T12:09:26+09:00 CPU_IDLE_GAP_UNRESOLVED idle=99% active_refines=0 planner=none
2026-05-06T12:11:39+09:00 CPU_IDLE_GAP_UNRESOLVED idle=96% active_refines=0 planner=none
2026-05-06T12:13:39+09:00 CPU_IDLE_GAP_UNRESOLVED idle=95% active_refines=0 planner=none
[2026-05-06T12:15:06+09:00] curator failed rc=127
2026-05-06T12:15:50+09:00 CPU_IDLE_GAP_UNRESOLVED idle=100% active_refines=0 planner=none
2026-05-06T12:17:59+09:00 CPU_IDLE_GAP_UNRESOLVED idle=99% active_refines=0 planner=none
2026-05-06T12:19:53+09:00 CPU_IDLE_GAP_UNRESOLVED idle=94% active_refines=0 planner=none
2026-05-06T12:22:11+09:00 CPU_IDLE_GAP_UNRESOLVED idle=96% active_refines=0 planner=none
2026-05-06T12:24:10+09:00 CPU_IDLE_GAP_UNRESOLVED idle=96% active_refines=0 planner=none
[2026-05-06T12:25:40+09:00] curator failed rc=127
2026-05-06T12:26:03+09:00 CPU_IDLE_GAP_UNRESOLVED idle=99% active_refines=0 planner=none
2026-05-06T12:27:59+09:00 CPU_IDLE_GAP_UNRESOLVED idle=100% active_refines=0 planner=none
2026-05-06T12:29:53+09:00 CPU_IDLE_GAP_UNRESOLVED idle=99% active_refines=0 planner=none
2026-05-06T12:31:46+09:00 CPU_IDLE_GAP_UNRESOLVED idle=100% active_refines=0 planner=none
2026-05-06T12:33:40+09:00 CPU_IDLE_GAP_UNRESOLVED idle=100% active_refines=0 planner=none
2026-05-06T12:35:35+09:00 CPU_IDLE_GAP_UNRESOLVED idle=82% active_refines=0 planner=none
[2026-05-06T12:36:31+09:00] curator failed rc=127
2026-05-06T12:37:58+09:00 CPU_IDLE_GAP_UNRESOLVED idle=96% active_refines=0 planner=none
2026-05-06T12:39:58+09:00 CPU_IDLE_GAP_UNRESOLVED idle=97% active_refines=0 planner=none
2026-05-06T12:41:53+09:00 CPU_IDLE_GAP_UNRESOLVED idle=95% active_refines=0 planner=none
2026-05-06T12:43:58+09:00 CPU_IDLE_GAP_UNRESOLVED idle=95% active_refines=0 planner=none
2026-05-06T12:46:11+09:00 CPU_IDLE_GAP_UNRESOLVED idle=67% active_refines=0 planner=none

```
### pilot/md_r16_chromanol_topical_tgfb1_extra_30ns_auto.log tail -120

```text
R16 topical chromanol TGFB1 extra 30 ns MD
      job_id              analog_id target  affinity_probability_binary                                                                                                                                            cif
r16_05_tgfb1  R15_chromanol_Me6_Me9  tgfb1                     0.636406 pilot/cpu_meaningful/output_r16_chromanol_topical/boltz_results_inputs_r16_chromanol_topical/predictions/r16_05_tgfb1/r16_05_tgfb1_model_0.cif
r16_04_tgfb1 R15_chromanol_Me6_Me10  tgfb1                     0.615679 pilot/cpu_meaningful/output_r16_chromanol_topical/boltz_results_inputs_r16_chromanol_topical/predictions/r16_04_tgfb1/r16_04_tgfb1_model_0.cif
r16_06_tgfb1 R15_chromanol_Me9_Me10  tgfb1                     0.615358 pilot/cpu_meaningful/output_r16_chromanol_topical/boltz_results_inputs_r16_chromanol_topical/predictions/r16_06_tgfb1/r16_06_tgfb1_model_0.cif

=== r16_05_tgfb1__R15_chromanol_Me6_Me9__30ns (30 ns R16 topical chromanol MD) ===
  CIF: pilot/cpu_meaningful/output_r16_chromanol_topical/boltz_results_inputs_r16_chromanol_topical/predictions/r16_05_tgfb1/r16_05_tgfb1_model_0.cif
  affinity_probability_binary: 0.6364059448242188
dcdplugin) detected standard 32-bit DCD file of native endianness
dcdplugin) CHARMM format DCD file (also NAMD 2.1 and later)
  ok: mean=0.68 A, last-third=0.71 A, max=0.89 A, wall=25.57 min

=== r16_04_tgfb1__R15_chromanol_Me6_Me10__30ns (30 ns R16 topical chromanol MD) ===
  CIF: pilot/cpu_meaningful/output_r16_chromanol_topical/boltz_results_inputs_r16_chromanol_topical/predictions/r16_04_tgfb1/r16_04_tgfb1_model_0.cif
  affinity_probability_binary: 0.6156794428825378
dcdplugin) detected standard 32-bit DCD file of native endianness
dcdplugin) CHARMM format DCD file (also NAMD 2.1 and later)
  ok: mean=0.99 A, last-third=1.04 A, max=1.24 A, wall=24.88 min

=== r16_06_tgfb1__R15_chromanol_Me9_Me10__30ns (30 ns R16 topical chromanol MD) ===
  CIF: pilot/cpu_meaningful/output_r16_chromanol_topical/boltz_results_inputs_r16_chromanol_topical/predictions/r16_06_tgfb1/r16_06_tgfb1_model_0.cif
  affinity_probability_binary: 0.6153576970100403
dcdplugin) detected standard 32-bit DCD file of native endianness
dcdplugin) CHARMM format DCD file (also NAMD 2.1 and later)
  ok: mean=0.54 A, last-third=0.53 A, max=0.81 A, wall=25.18 min

Final R16 topical chromanol TGFB1 extra 30 ns summary:
                                      name       job_id              analog_id target status                    smiles  topical_followup_score  logP   QED   gap_eV  affinity_probability_binary  affinity_pred_value  wall_min  rmsd_mean_A  rmsd_max_A  rmsd_final_A  rmsd_last_third_A  ns_simulated
 r16_05_tgfb1__R15_chromanol_Me6_Me9__30ns r16_05_tgfb1  R15_chromanol_Me6_Me9  tgfb1     ok Cc1cc2c(c(C)c1O)OCC(CO)C2                0.871885 1.552 0.736 3.984787                     0.636406             0.615291     25.57         0.68        0.89          0.68               0.71          30.0
r16_04_tgfb1__R15_chromanol_Me6_Me10__30ns r16_04_tgfb1 R15_chromanol_Me6_Me10  tgfb1     ok Cc1cc(O)c(C)c2c1CC(CO)CO2                0.871885 1.552 0.736 4.138359                     0.615679             1.082875     24.88         0.99        1.24          1.03               1.04          30.0
r16_06_tgfb1__R15_chromanol_Me9_Me10__30ns r16_06_tgfb1 R15_chromanol_Me9_Me10  tgfb1     ok Cc1c(O)cc2c(c1C)CC(CO)CO2                0.871885 1.552 0.736 3.972641                     0.615358             1.045615     25.18         0.54        0.81          0.56               0.53          30.0

```
### pilot/r16_chromanol_topical_chain.log tail -100

```text
  8 12 20  7 13 20 17  4  4 17 19  3 20 12 17  4  3 12 12  2 16 17  5 17
 16  8 19 12 17 15  5 21 18  9 21 21  3  7 19 12 17  3  9  9  8 11  8  9
 15  3 12 17  2 10  6 17  6  5 17  3  5  4 18 12  7 21  5 11  4  9 15 18
 18  9  3  3  9  5 12  2 18 11 10  9 14  4  3 16 15 12 12 12 14  2 18 16
 12  8  3  2  7 10 12  7 17 17  3 10  3  3  2 12  5 18  4 20  6 15 17 17
 18  8 13  4  6  6 21  3  7 12 20 11  5 15  3 13  5 12  9 19 13 19 11 10
  8 16 13  9 20 10  2  4 15  6 12  9 16  6 16 20 11 19 17 12  5 18  7 20
 17 13 21 12  2 12 20  4  7 10  4 16  9  2 17  2  2 16  6  6 21 16  7  2
 12  8 16 12 16 11 21 20 20 21  9  3 13 16 13 21  8  7 12 17  4 14 11 21
  3 17  6 13  6 17] [ 2 12  5 18  4 20  6 15 17 17 18  8 13  4  6  6 21  3  7 12 20 11  5 15
  3 13  5 12  9 19 13 19 11 10  8 16 13  9 20 10  2  4 15  6 12  9 16  6
 16 20 11 19 17 12  5 18  7 20 17 13 21 12  2 12 20  4  7 10  4 16  9  2
 17  2  2 16  6  6 21 16  7  2 12  8 16 12 16 11 21 20 20 21  9  3 13 16
 13 21  8  7 12 17  4 14 11 21  3 17  6 13  6 17] r16_03_tgfb1
Warning: MSA does not match input sequence, creating dummy. 2 [14 16 16 17  9 12  3 12 12 16 12 12 12 16 12 12 19 12 12 21 12 18 16  9
  3 16  2  2  9 12 17 18  6 13 18 11  5 14  8 12 21 13  3 13  3 11  8  2
 11  3  9  7 11 12 17 13 12  3 12  2 17 16 16 17  7  9  8 21 16 16  9 16
 12 16  8  2 21 12  2 12 20  4 17 18  3  5  3 21  2  9  8 17  2  8 16  8
 16  8 16  8  2  5 20 20  2 13  8 21 18  3 21 12 14 21  8 18 10  4  8 11
 20  5 13 15 13  7 17 18 10 17 11 20 14 15 15  4 18 17  8 12  3  8  2 21
 16  8 16 21 12 12 17  3  2  8 12  3 12 12  3 12 13 12 13 21  8  7 10 21
  8 12 20  7 13 20 17  4  4 17 19  3 20 12 17  4  3 12 12  2 16 17  5 17
 16  8 19 12 17 15  5 21 18  9 21 21  3  7 19 12 17  3  9  9  8 11  8  9
 15  3 12 17  2 10  6 17  6  5 17  3  5  4 18 12  7 21  5 11  4  9 15 18
 18  9  3  3  9  5 12  2 18 11 10  9 14  4  3 16 15 12 12 12 14  2 18 16
 12  8  3  2  7 10 12  7 17 17  3 10  3  3  2 12  5 18  4 20  6 15 17 17
 18  8 13  4  6  6 21  3  7 12 20 11  5 15  3 13  5 12  9 19 13 19 11 10
  8 16 13  9 20 10  2  4 15  6 12  9 16  6 16 20 11 19 17 12  5 18  7 20
 17 13 21 12  2 12 20  4  7 10  4 16  9  2 17  2  2 16  6  6 21 16  7  2
 12  8 16 12 16 11 21 20 20 21  9  3 13 16 13 21  8  7 12 17  4 14 11 21
  3 17  6 13  6 17] [ 2 12  5 18  4 20  6 15 17 17 18  8 13  4  6  6 21  3  7 12 20 11  5 15
  3 13  5 12  9 19 13 19 11 10  8 16 13  9 20 10  2  4 15  6 12  9 16  6
 16 20 11 19 17 12  5 18  7 20 17 13 21 12  2 12 20  4  7 10  4 16  9  2
 17  2  2 16  6  6 21 16  7  2 12  8 16 12 16 11 21 20 20 21  9  3 13 16
 13 21  8  7 12 17  4 14 11 21  3 17  6 13  6 17] r16_02_tgfb1
Warning: MSA does not match input sequence, creating dummy. 2 [14 16 16 17  9 12  3 12 12 16 12 12 12 16 12 12 19 12 12 21 12 18 16  9
  3 16  2  2  9 12 17 18  6 13 18 11  5 14  8 12 21 13  3 13  3 11  8  2
 11  3  9  7 11 12 17 13 12  3 12  2 17 16 16 17  7  9  8 21 16 16  9 16
 12 16  8  2 21 12  2 12 20  4 17 18  3  5  3 21  2  9  8 17  2  8 16  8
 16  8 16  8  2  5 20 20  2 13  8 21 18  3 21 12 14 21  8 18 10  4  8 11
 20  5 13 15 13  7 17 18 10 17 11 20 14 15 15  4 18 17  8 12  3  8  2 21
 16  8 16 21 12 12 17  3  2  8 12  3 12 12  3 12 13 12 13 21  8  7 10 21
  8 12 20  7 13 20 17  4  4 17 19  3 20 12 17  4  3 12 12  2 16 17  5 17
 16  8 19 12 17 15  5 21 18  9 21 21  3  7 19 12 17  3  9  9  8 11  8  9
 15  3 12 17  2 10  6 17  6  5 17  3  5  4 18 12  7 21  5 11  4  9 15 18
 18  9  3  3  9  5 12  2 18 11 10  9 14  4  3 16 15 12 12 12 14  2 18 16
 12  8  3  2  7 10 12  7 17 17  3 10  3  3  2 12  5 18  4 20  6 15 17 17
 18  8 13  4  6  6 21  3  7 12 20 11  5 15  3 13  5 12  9 19 13 19 11 10
  8 16 13  9 20 10  2  4 15  6 12  9 16  6 16 20 11 19 17 12  5 18  7 20
 17 13 21 12  2 12 20  4  7 10  4 16  9  2 17  2  2 16  6  6 21 16  7  2
 12  8 16 12 16 11 21 20 20 21  9  3 13 16 13 21  8  7 12 17  4 14 11 21
  3 17  6 13  6 17] [ 2 12  5 18  4 20  6 15 17 17 18  8 13  4  6  6 21  3  7 12 20 11  5 15
  3 13  5 12  9 19 13 19 11 10  8 16 13  9 20 10  2  4 15  6 12  9 16  6
 16 20 11 19 17 12  5 18  7 20 17 13 21 12  2 12 20  4  7 10  4 16  9  2
 17  2  2 16  6  6 21 16  7  2 12  8 16 12 16 11 21 20 20 21  9  3 13 16
 13 21  8  7 12 17  4 14 11 21  3 17  6 13  6 17] r16_02_tgfb1
Warning: MSA does not match input sequence, creating dummy. 2 [14 16 16 17  9 12  3 12 12 16 12 12 12 16 12 12 19 12 12 21 12 18 16  9
  3 16  2  2  9 12 17 18  6 13 18 11  5 14  8 12 21 13  3 13  3 11  8  2
 11  3  9  7 11 12 17 13 12  3 12  2 17 16 16 17  7  9  8 21 16 16  9 16
 12 16  8  2 21 12  2 12 20  4 17 18  3  5  3 21  2  9  8 17  2  8 16  8
 16  8 16  8  2  5 20 20  2 13  8 21 18  3 21 12 14 21  8 18 10  4  8 11
 20  5 13 15 13  7 17 18 10 17 11 20 14 15 15  4 18 17  8 12  3  8  2 21
 16  8 16 21 12 12 17  3  2  8 12  3 12 12  3 12 13 12 13 21  8  7 10 21
  8 12 20  7 13 20 17  4  4 17 19  3 20 12 17  4  3 12 12  2 16 17  5 17
 16  8 19 12 17 15  5 21 18  9 21 21  3  7 19 12 17  3  9  9  8 11  8  9
 15  3 12 17  2 10  6 17  6  5 17  3  5  4 18 12  7 21  5 11  4  9 15 18
 18  9  3  3  9  5 12  2 18 11 10  9 14  4  3 16 15 12 12 12 14  2 18 16
 12  8  3  2  7 10 12  7 17 17  3 10  3  3  2 12  5 18  4 20  6 15 17 17
 18  8 13  4  6  6 21  3  7 12 20 11  5 15  3 13  5 12  9 19 13 19 11 10
  8 16 13  9 20 10  2  4 15  6 12  9 16  6 16 20 11 19 17 12  5 18  7 20
 17 13 21 12  2 12 20  4  7 10  4 16  9  2 17  2  2 16  6  6 21 16  7  2
 12  8 16 12 16 11 21 20 20 21  9  3 13 16 13 21  8  7 12 17  4 14 11 21
  3 17  6 13  6 17] [ 2 12  5 18  4 20  6 15 17 17 18  8 13  4  6  6 21  3  7 12 20 11  5 15
  3 13  5 12  9 19 13 19 11 10  8 16 13  9 20 10  2  4 15  6 12  9 16  6
 16 20 11 19 17 12  5 18  7 20 17 13 21 12  2 12 20  4  7 10  4 16  9  2
 17  2  2 16  6  6 21 16  7  2 12  8 16 12 16 11 21 20 20 21  9  3 13 16
 13 21  8  7 12 17  4 14 11 21  3 17  6 13  6 17] r16_01_tgfb1
Warning: MSA does not match input sequence, creating dummy. 2 [14 16 16 17  9 12  3 12 12 16 12 12 12 16 12 12 19 12 12 21 12 18 16  9
  3 16  2  2  9 12 17 18  6 13 18 11  5 14  8 12 21 13  3 13  3 11  8  2
 11  3  9  7 11 12 17 13 12  3 12  2 17 16 16 17  7  9  8 21 16 16  9 16
 12 16  8  2 21 12  2 12 20  4 17 18  3  5  3 21  2  9  8 17  2  8 16  8
 16  8 16  8  2  5 20 20  2 13  8 21 18  3 21 12 14 21  8 18 10  4  8 11
 20  5 13 15 13  7 17 18 10 17 11 20 14 15 15  4 18 17  8 12  3  8  2 21
 16  8 16 21 12 12 17  3  2  8 12  3 12 12  3 12 13 12 13 21  8  7 10 21
  8 12 20  7 13 20 17  4  4 17 19  3 20 12 17  4  3 12 12  2 16 17  5 17
 16  8 19 12 17 15  5 21 18  9 21 21  3  7 19 12 17  3  9  9  8 11  8  9
 15  3 12 17  2 10  6 17  6  5 17  3  5  4 18 12  7 21  5 11  4  9 15 18
 18  9  3  3  9  5 12  2 18 11 10  9 14  4  3 16 15 12 12 12 14  2 18 16
 12  8  3  2  7 10 12  7 17 17  3 10  3  3  2 12  5 18  4 20  6 15 17 17
 18  8 13  4  6  6 21  3  7 12 20 11  5 15  3 13  5 12  9 19 13 19 11 10
  8 16 13  9 20 10  2  4 15  6 12  9 16  6 16 20 11 19 17 12  5 18  7 20
 17 13 21 12  2 12 20  4  7 10  4 16  9  2 17  2  2 16  6  6 21 16  7  2
 12  8 16 12 16 11 21 20 20 21  9  3 13 16 13 21  8  7 12 17  4 14 11 21
  3 17  6 13  6 17] [ 2 12  5 18  4 20  6 15 17 17 18  8 13  4  6  6 21  3  7 12 20 11  5 15
  3 13  5 12  9 19 13 19 11 10  8 16 13  9 20 10  2  4 15  6 12  9 16  6
 16 20 11 19 17 12  5 18  7 20 17 13 21 12  2 12 20  4  7 10  4 16  9  2
 17  2  2 16  6  6 21 16  7  2 12  8 16 12 16 11 21 20 20 21  9  3 13 16
 13 21  8  7 12 17  4 14 11 21  3 17  6 13  6 17] r16_01_tgfb1

[2026-04-30 12:38:27] R16 topical chromanol cofold chain complete

```
### pilot/r15_chromanol_chain.log tail -100

```text
  9  5  2 10 15  5  8  5  8  3 19 18  4  4 15  3  8 20  4 12 10  3 21  2
  2 10  8 12  9 10 17 12  9 12 17 10 17 18  5 11  9  2 12 14 20 16 17 20
 18 15 17  9  5 21  7 12  2  7  5  5 11  5  9 11  7  2 11 20  9  3 17  7
  4 16 21  7 16 11  9 16  7 18 16 13  2  6  5 17 13 12 18 15  5  2 11 18
 18 11  3  9  8 21 14 15 15 13  5  3 15 20 14  3 18  4 16 15 20 16  8 21
  8 12  4 15 11 17 21 15 19 16  7 12 16  4  9 12  8  2  2 20  8 15  2  5
  3  5  8 21  3 15 15 13  9  4 13 20 19  2 21  7  9  7  4 21 12 10  9 20
 16 13  5 11 20 17 17 15  9 15 16  3 18 21 13 10 11  5  2  2 12 17  8  8
  4 18  9 13 18 20 15 15 21  2  4 13 20 19  3 20  5  8 20 13  3 17 14  5
 16  9 20 16 13 14 11  2 10  5 15 16  9 11  9 10 13 21  5  2 21 15 14 13
  5  9 15 15 20 15 15 10  9 18  3  7 20 13 15  5 16 13 18 13  3 11 12 18
 12  7 13  2  4 17 19 15  4  6  3 13  4] [12 15  3  8 14 16  9  9 16 21 19  3 13 10 20 11 18 20  3 11  4  4 20 18
 16  5 14  4  3  8  5 21  5 20  2 11  3 13  2 15  7 21 19 17  4 21 18 16
 12 13 15 17 13 11  4 18  9 14  2  5 11 12 21 21 15  2  3  9  2 10  9  5
 15 10  2 15  5  9 13  9  9 11 12  2 10  2 15  9 16  9 17  9 11  9  9  5
  2 10 15  5  8  5  8  3 19 18  4  4 15  3  8 20  4 12 10  3 21  2  2 10
  8 12  9 10 17 12  9 12 17 10 17 18  5 11  9  2 12 14 20 16 17 20 18 15
 17  9  5 21  7 12  2  7  5  5 11  5  9 11  7  2 11 20  9] r15_chrom_mmp1
Warning: MSA does not match input sequence, creating dummy. 2 [14 10 17 15 16 16 12 12 12 12 12 15 19  9 21 21 17 10 17 15 16  2 18 12
  8 18  7  8  7  5 21  5 12 21  7 13 20 12  8 13 20 20  4 12 13  4  5  9
  3  7 21  8 13  3  3  4 17  9 16 21 21  8 13 12 13  7 14  7  8 15 15  9
 12 13 21 18  9 13 16  5  2  8 18 12 13 21 14 13  7 16  3  6  9 21 16  5
 21  2  7 15 21 12 18  8  9  4 16  3 19  8  7 18 10 12 18 20  3 11  8  4
 20 18 16  5 12 16  3  2  5 21  5 10  2 11  8 13  2 15  7 12 19 17  4 21
 18 16 12 18 15 18 13 21 17  8  9  7  2  5 11 14 11 17 15 21  3  9  5 10
  3  5  4 17 16 15  5  9 16  9  9  4 12  2 10  2 15  7 16  9 16  9 11  9
  9  5  2 10 15  5  8  5  8  3 19 18  4  4 15  3  8 20  4 12 10  3 21  2
  2 10  8 12  9 10 17 12  9 12 17 10 17 18  5 11  9  2 12 14 20 16 17 20
 18 15 17  9  5 21  7 12  2  7  5  5 11  5  9 11  7  2 11 20  9  3 17  7
  4 16 21  7 16 11  9 16  7 18 16 13  2  6  5 17 13 12 18 15  5  2 11 18
 18 11  3  9  8 21 14 15 15 13  5  3 15 20 14  3 18  4 16 15 20 16  8 21
  8 12  4 15 11 17 21 15 19 16  7 12 16  4  9 12  8  2  2 20  8 15  2  5
  3  5  8 21  3 15 15 13  9  4 13 20 19  2 21  7  9  7  4 21 12 10  9 20
 16 13  5 11 20 17 17 15  9 15 16  3 18 21 13 10 11  5  2  2 12 17  8  8
  4 18  9 13 18 20 15 15 21  2  4 13 20 19  3 20  5  8 20 13  3 17 14  5
 16  9 20 16 13 14 11  2 10  5 15 16  9 11  9 10 13 21  5  2 21 15 14 13
  5  9 15 15 20 15 15 10  9 18  3  7 20 13 15  5 16 13 18 13  3 11 12 18
 12  7 13  2  4 17 19 15  4  6  3 13  4] [12 15  3  8 14 16  9  9 16 21 19  3 13 10 20 11 18 20  3 11  4  4 20 18
 16  5 14  4  3  8  5 21  5 20  2 11  3 13  2 15  7 21 19 17  4 21 18 16
 12 13 15 17 13 11  4 18  9 14  2  5 11 12 21 21 15  2  3  9  2 10  9  5
 15 10  2 15  5  9 13  9  9 11 12  2 10  2 15  9 16  9 17  9 11  9  9  5
  2 10 15  5  8  5  8  3 19 18  4  4 15  3  8 20  4 12 10  3 21  2  2 10
  8 12  9 10 17 12  9 12 17 10 17 18  5 11  9  2 12 14 20 16 17 20 18 15
 17  9  5 21  7 12  2  7  5  5 11  5  9 11  7  2 11 20  9] r15_chrom_mmp1
Warning: MSA does not match input sequence, creating dummy. 2 [14 18  2  2 17 14  9 16 21  3 21  2 15 21 21 12 12  2 12  6 17  3 16  2
 21  9  7  4  6 17  9 16  6  3  6 16  5  8 16  2 16  3  6 16  2  9 21 17
 12 21 12  5  9  6  9  6  6  3 21  6  2 13  7 12  9  8 12  6 18  8  3  5
 16  6  5 16 10 13  9 12 15  6 10 15  9 17 16  2  4  3 13 11  9 21  6 18
  2 13  5  9  2 16  6 11 15  9  9 18 21 20  3 17  9  8 17 15  7 17 17  6
 13 20  7  6 18  6 12  5  9  2 21  9  6 14 16 12  6 17 14  5 21  3 12 16
 17 16  5  6 16 15 16  3  3 21 13 12 16  9 13  6  6  8  8 19 21  6  5  8
 16 13  5  7 18 21 21  9 16  2 12  2  2 20  3 12  8  5 18 15  9 16  5 16
 18 14 11  3  2  4  6 12 21  7 18 18  8 19 17  2  6 17 13 18  6  9 14  9
 11 17 18  3 21 18  4  5  4  2 17  6  3 12  8 13  7 17  3 12  6 14 21  3
 16  6  8  2  5 12  8  8  4 11 13 13  9 13 13  6 11  3 18 16 13 11 17 13
 16 11 13 15  8 12 17  9  6 18 17 14 13 18 20  3  2 13 15  6  9 21  6 18
  5  9  3  6  6 18 16 10  3 18 18 18 12 16 21  8 15 13  6 16  5  9  8 21
 14 13 13  4 14 14 15 11 13 18  6  2  6 10 20  4  6 16  9  5  4  5 11 15
  8 17 12 20 20  3 13 14 20  9  5 14  2] [14 18  2  2  3 12  2 12 17  6  2  2 12  2  2 12 12 16  9  2 18  2 12 16
  5  9  6  9  6  9  9  3  2 10 19  9  6  9  2 21  9  8  2  6 17  2  2 12
  8 11  9 17 18 21 15  2 17 18 16 18 16 16 17 20  2  2  8 11  3 16  9 12
 16 21  5  7  5 16  6  3 12  3  2 21  6  8 17 15 20 10 16 17 17  2 12  2
  3  7 12 16  3  2  8 16  9 15  4 21  7  5  3  3 12 11 12  2  9  6  9  6
  9  6  7  4  9  6 17  8 16 12  7 16 20 16 12 17 16  6 17 13  7  6  7 16
  9 20  7  6  5  5 17 16 17  6 17  6  7  6 12 16  9  6  2 17  9  2  7  6
  2  7  6  3 16  3 16  8 17  8 17 17  6  3 13  7 17  6 17  6  3  7  7  9
 17 21 10  6  9 20  2 21 13  5  9  9  3  9  6 20  2  9  6 18 17  5 12  5
  7 21  5 15  9  6  6 17 10 13  2 17  4 15  9 17  6 17 17 16 21  3  5  6
  9 20 10 19  9 15 16 16 20 10  7  6  2 17  4 14  9 20 12 12  5 16 12  5
  6  7  6 20 15  4  2 17  9  2  9  2  7 21 15 15  9  9  2  5  6  9 15  2
  4  9  6  4  7  9 17 16 12 17 15] r15_chrom_ctgf
Warning: MSA does not match input sequence, creating dummy. 2 [14 18  2  2 17 14  9 16 21  3 21  2 15 21 21 12 12  2 12  6 17  3 16  2
 21  9  7  4  6 17  9 16  6  3  6 16  5  8 16  2 16  3  6 16  2  9 21 17
 12 21 12  5  9  6  9  6  6  3 21  6  2 13  7 12  9  8 12  6 18  8  3  5
 16  6  5 16 10 13  9 12 15  6 10 15  9 17 16  2  4  3 13 11  9 21  6 18
  2 13  5  9  2 16  6 11 15  9  9 18 21 20  3 17  9  8 17 15  7 17 17  6
 13 20  7  6 18  6 12  5  9  2 21  9  6 14 16 12  6 17 14  5 21  3 12 16
 17 16  5  6 16 15 16  3  3 21 13 12 16  9 13  6  6  8  8 19 21  6  5  8
 16 13  5  7 18 21 21  9 16  2 12  2  2 20  3 12  8  5 18 15  9 16  5 16
 18 14 11  3  2  4  6 12 21  7 18 18  8 19 17  2  6 17 13 18  6  9 14  9
 11 17 18  3 21 18  4  5  4  2 17  6  3 12  8 13  7 17  3 12  6 14 21  3
 16  6  8  2  5 12  8  8  4 11 13 13  9 13 13  6 11  3 18 16 13 11 17 13
 16 11 13 15  8 12 17  9  6 18 17 14 13 18 20  3  2 13 15  6  9 21  6 18
  5  9  3  6  6 18 16 10  3 18 18 18 12 16 21  8 15 13  6 16  5  9  8 21
 14 13 13  4 14 14 15 11 13 18  6  2  6 10 20  4  6 16  9  5  4  5 11 15
  8 17 12 20 20  3 13 14 20  9  5 14  2] [14 18  2  2  3 12  2 12 17  6  2  2 12  2  2 12 12 16  9  2 18  2 12 16
  5  9  6  9  6  9  9  3  2 10 19  9  6  9  2 21  9  8  2  6 17  2  2 12
  8 11  9 17 18 21 15  2 17 18 16 18 16 16 17 20  2  2  8 11  3 16  9 12
 16 21  5  7  5 16  6  3 12  3  2 21  6  8 17 15 20 10 16 17 17  2 12  2
  3  7 12 16  3  2  8 16  9 15  4 21  7  5  3  3 12 11 12  2  9  6  9  6
  9  6  7  4  9  6 17  8 16 12  7 16 20 16 12 17 16  6 17 13  7  6  7 16
  9 20  7  6  5  5 17 16 17  6 17  6  7  6 12 16  9  6  2 17  9  2  7  6
  2  7  6  3 16  3 16  8 17  8 17 17  6  3 13  7 17  6 17  6  3  7  7  9
 17 21 10  6  9 20  2 21 13  5  9  9  3  9  6 20  2  9  6 18 17  5 12  5
  7 21  5 15  9  6  6 17 10 13  2 17  4 15  9 17  6 17 17 16 21  3  5  6
  9 20 10 19  9 15 16 16 20 10  7  6  2 17  4 14  9 20 12 12  5 16 12  5
  6  7  6 20 15  4  2 17  9  2  9  2  7 21 15 15  9  9  2  5  6  9 15  2
  4  9  6  4  7  9 17 16 12 17 15] r15_chrom_ctgf

[Thu Apr 30 11:46:08 KST 2026] === R15 chromanol cofold chain complete ===

```
### pilot/md_r16_chromanol_anchor_triad_100ns_auto.log tail -120

```text
R16 topical chromanol anchor triad 100 ns MD
      job_id             analog_id target  affinity_probability_binary                                                                                                                                            cif
r16_03_tgfb1 R15_chromanol_Cl_pos9  tgfb1                     0.682203 pilot/cpu_meaningful/output_r16_chromanol_topical/boltz_results_inputs_r16_chromanol_topical/predictions/r16_03_tgfb1/r16_03_tgfb1_model_0.cif
  r16_03_dct R15_chromanol_Cl_pos9    dct                     0.546468     pilot/cpu_meaningful/output_r16_chromanol_topical/boltz_results_inputs_r16_chromanol_topical/predictions/r16_03_dct/r16_03_dct_model_0.cif
  r16_02_tyr R15_chromanol_Cl_pos6    tyr                     0.524954     pilot/cpu_meaningful/output_r16_chromanol_topical/boltz_results_inputs_r16_chromanol_topical/predictions/r16_02_tyr/r16_02_tyr_model_0.cif

=== r16_03_tgfb1__R15_chromanol_Cl_pos9__100ns (100 ns R16 topical chromanol MD) ===
  CIF: pilot/cpu_meaningful/output_r16_chromanol_topical/boltz_results_inputs_r16_chromanol_topical/predictions/r16_03_tgfb1/r16_03_tgfb1_model_0.cif
  affinity_probability_binary: 0.6822030544281006
dcdplugin) detected standard 32-bit DCD file of native endianness
dcdplugin) CHARMM format DCD file (also NAMD 2.1 and later)
  ok: mean=0.51 A, last-third=0.51 A, max=0.69 A, wall=95.97 min

=== r16_03_dct__R15_chromanol_Cl_pos9__100ns (100 ns R16 topical chromanol MD) ===
  CIF: pilot/cpu_meaningful/output_r16_chromanol_topical/boltz_results_inputs_r16_chromanol_topical/predictions/r16_03_dct/r16_03_dct_model_0.cif
  affinity_probability_binary: 0.5464680790901184
dcdplugin) detected standard 32-bit DCD file of native endianness
dcdplugin) CHARMM format DCD file (also NAMD 2.1 and later)
  ok: mean=0.32 A, last-third=0.22 A, max=1.13 A, wall=102.92 min

=== r16_02_tyr__R15_chromanol_Cl_pos6__100ns (100 ns R16 topical chromanol MD) ===
  CIF: pilot/cpu_meaningful/output_r16_chromanol_topical/boltz_results_inputs_r16_chromanol_topical/predictions/r16_02_tyr/r16_02_tyr_model_0.cif
  affinity_probability_binary: 0.5249537825584412
dcdplugin) detected standard 32-bit DCD file of native endianness
dcdplugin) CHARMM format DCD file (also NAMD 2.1 and later)
  ok: mean=0.25 A, last-third=0.24 A, max=0.62 A, wall=106.54 min

Final R16 topical chromanol anchor triad 100 ns summary:
                                      name       job_id             analog_id target status                  smiles  topical_followup_score  logP   QED   gap_eV  affinity_probability_binary  affinity_pred_value  wall_min  rmsd_mean_A  rmsd_max_A  rmsd_final_A  rmsd_last_third_A  ns_simulated
r16_03_tgfb1__R15_chromanol_Cl_pos9__100ns r16_03_tgfb1 R15_chromanol_Cl_pos9  tgfb1     ok OCC1COc2cc(O)c(Cl)cc2C1                 0.87507 1.589 0.747 3.809594                     0.682203             1.220776     95.97         0.51        0.69          0.50               0.51         100.0
  r16_03_dct__R15_chromanol_Cl_pos9__100ns   r16_03_dct R15_chromanol_Cl_pos9    dct     ok OCC1COc2cc(O)c(Cl)cc2C1                 0.87507 1.589 0.747 3.809594                     0.546468             0.882103    102.92         0.32        1.13          0.51               0.22         100.0
  r16_02_tyr__R15_chromanol_Cl_pos6__100ns   r16_02_tyr R15_chromanol_Cl_pos6    tyr     ok OCC1COc2c(ccc(O)c2Cl)C1                 0.87507 1.589 0.747 3.929412                     0.524954             0.851502    106.54         0.25        0.62          0.18               0.24         100.0

```
### pilot/md_r16_chromanol_anchor_triad_200ns_auto.log tail -120

```text
R16 topical chromanol anchor triad 200 ns MD
      job_id             analog_id target  affinity_probability_binary                                                                                                                                            cif
r16_03_tgfb1 R15_chromanol_Cl_pos9  tgfb1                     0.682203 pilot/cpu_meaningful/output_r16_chromanol_topical/boltz_results_inputs_r16_chromanol_topical/predictions/r16_03_tgfb1/r16_03_tgfb1_model_0.cif
  r16_03_dct R15_chromanol_Cl_pos9    dct                     0.546468     pilot/cpu_meaningful/output_r16_chromanol_topical/boltz_results_inputs_r16_chromanol_topical/predictions/r16_03_dct/r16_03_dct_model_0.cif
  r16_02_tyr R15_chromanol_Cl_pos6    tyr                     0.524954     pilot/cpu_meaningful/output_r16_chromanol_topical/boltz_results_inputs_r16_chromanol_topical/predictions/r16_02_tyr/r16_02_tyr_model_0.cif

=== r16_03_tgfb1__R15_chromanol_Cl_pos9__200ns (200 ns R16 topical chromanol MD) ===
  CIF: pilot/cpu_meaningful/output_r16_chromanol_topical/boltz_results_inputs_r16_chromanol_topical/predictions/r16_03_tgfb1/r16_03_tgfb1_model_0.cif
  affinity_probability_binary: 0.6822030544281006
dcdplugin) detected standard 32-bit DCD file of native endianness
dcdplugin) CHARMM format DCD file (also NAMD 2.1 and later)
  ok: mean=0.27 A, last-third=0.24 A, max=0.71 A, wall=184.73 min

=== r16_03_dct__R15_chromanol_Cl_pos9__200ns (200 ns R16 topical chromanol MD) ===
  CIF: pilot/cpu_meaningful/output_r16_chromanol_topical/boltz_results_inputs_r16_chromanol_topical/predictions/r16_03_dct/r16_03_dct_model_0.cif
  affinity_probability_binary: 0.5464680790901184
dcdplugin) detected standard 32-bit DCD file of native endianness
dcdplugin) CHARMM format DCD file (also NAMD 2.1 and later)
  ok: mean=0.34 A, last-third=0.43 A, max=1.05 A, wall=176.31 min

=== r16_02_tyr__R15_chromanol_Cl_pos6__200ns (200 ns R16 topical chromanol MD) ===
  CIF: pilot/cpu_meaningful/output_r16_chromanol_topical/boltz_results_inputs_r16_chromanol_topical/predictions/r16_02_tyr/r16_02_tyr_model_0.cif
  affinity_probability_binary: 0.5249537825584412
dcdplugin) detected standard 32-bit DCD file of native endianness
dcdplugin) CHARMM format DCD file (also NAMD 2.1 and later)
  ok: mean=0.49 A, last-third=0.57 A, max=0.8 A, wall=178.2 min

Final R16 topical chromanol anchor triad 200 ns summary:
                                      name       job_id             analog_id target status                  smiles  topical_followup_score  logP   QED   gap_eV  affinity_probability_binary  affinity_pred_value  wall_min  rmsd_mean_A  rmsd_max_A  rmsd_final_A  rmsd_last_third_A  ns_simulated
r16_03_tgfb1__R15_chromanol_Cl_pos9__200ns r16_03_tgfb1 R15_chromanol_Cl_pos9  tgfb1     ok OCC1COc2cc(O)c(Cl)cc2C1                 0.87507 1.589 0.747 3.809594                     0.682203             1.220776    184.73         0.27        0.71          0.22               0.24         200.0
  r16_03_dct__R15_chromanol_Cl_pos9__200ns   r16_03_dct R15_chromanol_Cl_pos9    dct     ok OCC1COc2cc(O)c(Cl)cc2C1                 0.87507 1.589 0.747 3.809594                     0.546468             0.882103    176.31         0.34        1.05          0.66               0.43         200.0
  r16_02_tyr__R15_chromanol_Cl_pos6__200ns   r16_02_tyr R15_chromanol_Cl_pos6    tyr     ok OCC1COc2c(ccc(O)c2Cl)C1                 0.87507 1.589 0.747 3.929412                     0.524954             0.851502    178.20         0.49        0.80          0.61               0.57         200.0

```
### docs/PAPER_FACTORY_QUEUE.md tail -160

```text
# Paper Factory Queue

- timestamp: `2026-05-06T12:46:57+09:00`
- manuscript_md_count: `20`
- manuscript_pdf_count: `19`
- principle: 논문 수를 늘리되, 같은 결과를 과장 반복하지 않는다. 각 paper는 독립 질문, 독립 figure set, 명확한 in silico limitation을 가져야 한다.

## Production Rule

1. 결과가 완료되면 먼저 `summary.json`/CSV를 검증한다.
2. 논문 후보는 `ready`, `near-ready`, `accumulating`, `awaiting more GPU`로 분류한다.
3. `ready` 후보는 원고 초안/figure/table을 만들고, `near-ready` 후보는 마지막 계산 완료 즉시 승격한다.
4. wet-lab claim, clinical claim, efficacy claim은 금지한다. 표현은 `in silico`, `candidate`, `prioritization`, `hypothesis`로 제한한다.

## Current Queue

| ID | Paper candidate | Status | Evidence now | Next action |
|---|---|---|---|---|
| P15 | Universal scaffold family across 14 skin targets | ready/v1.8 | PDF=yes; figures 1-10 integrated; batch2 5/5 | Submit/update preprint; keep only in-silico claims. |
| P16 | R16 topical chromanol lead paper | complete PDF+figures; 200ns complete | R16 cofold rows=18; 30ns matrix=18; TGFB1 60ns=6/6; pigment 60ns=3/3; anchor 100ns=3/3; anchor 200ns=3/3; figures=5; pose gate pass/review/fail=20/12/0 | Submission-ready as an in-silico preprint; next work is CRO/Markush/FTO package, not stronger efficacy or commercial claims. |
| P17 | R15 chromanol safety-first fragment triage | complete PDF+figures; prior-art caveat added | triage rows=38; 14-target cofold rows=14; top3 30ns=3/3; figures=4; pose gate pass/review/fail=20/12/0 | Submission-ready as a safety-first in-silico fragment triage; R15 parent exact PubChem hit keeps composition novelty/commercial claims blocked. |
| P18 | NPASS topical natural-product xTB atlas | accumulating | best candidate rows=80; 96conf ladder partially complete | Refresh ladder summary after each 96/120/144conf tier and select top candidates for Boltz-2 cofold. |
| P19 | Conformer-ladder sensitivity in xTB natural-product triage | accumulating | 12/24/36/48/72conf complete; 96conf running | Compare rank stability by conformer depth; write methodology/results note after 96conf full tier. |
| P20 | Skin PBPK + Potts-Guy permeability methodology | existing preprint; update candidate | preprint #14 exists; NPASS logKp proxy now feeds downstream ranking | Revise with NPASS atlas examples and current Recover topical formulation caveats. |
| P21 | Boltz-2/MD validation methodology and failure modes | existing preprint; update candidate | preprint #8 exists; extended MD drift caveats and chromanol PoseBusters gate now available (pose gate pass/review/fail=20/12/0) | Update with SREBP1 x R14_5 late drift, raw-pose clash review, MD relaxation, and ABFE limitations. |
| P22 | Korean herbal scaffold alignment and Tanimoto evidence | draft candidate | R14_5-ferulic acid 0.42; R12_23-EGCG 0.34; R12_4-EGCG 0.30 | Build herbal-alignment figures and write as translational perspective, not efficacy claim. |
| P23 | Pigmentation-target focused chromanol/pterocarpan paper | outline started | DCT/TYR R16 30ns matrix complete; pigment 60ns=3/3 | Expand outline into manuscript sections and add pigment-focused figures/tables. |
| P24 | Scar/fibrosis TGFB1/MMP1-focused topical lead paper | outline started | R16 TGFB1 top6 60ns complete; MMP1 R12_4/R14_5 extended 30ns strong | Expand outline into manuscript sections and CRO endpoint table. |
| P25 | Target evidence and modality-gated dermatology discovery map | ready for methods/results outline | target gate green/yellow/red=13/10/8; modality rows=31; novelty rows=112 | Write as systems-improvement paper: Open Targets evidence, modality fit, and compute queue gating. |
| P26 | Reproducible autonomous in-silico dermatology workflow | ready for methods update | provenance manifest=yes; wet-lab feedback schema=yes; auto planner/daemon active | Use as methodology paper/update: provenance hashes, wet-lab feedback loop, and queue decision protocol. |
| P27 | Synthesis-aware chromanol/natural-product candidate triage | ready for methods/results outline | synthesis/retrosynthesis gate rows=112; novelty rows=112 | Write as practical candidate-selection paper: availability, analog novelty, SA gate, and no-retrosynthesis caveat. |
| P28 | Active-learning and multi-fidelity autonomous queueing | ready for methods/results outline | active-learning rows=672; BO/action plan rows=112; provenance manifest=yes | Write as systems paper: surrogate acquisition, cost-aware fidelity ladder, and protected queue rules. |
| P29 | Topical formulation BO and IVRT/IVPT feedback workflow | ready for translational-methods outline | formulation BO rows=60; wet-lab schema=yes | Use for CRO-ready translational paper/RFQ appendix: IVRT, IVPT, retention, irritation, stability. |
| P30 | Pocket and structure-consensus calibration for DL cofolding | ready for methodology outline | pocket gate rows=31; structure consensus rows=32; pose gate pass/review/fail=20/12/0 | Write calibration/failure-mode paper around Boltz confidence, PoseBusters, MD, pocket plausibility, and missing cross-model consensus. |
| P31 | Free-energy validation plan for chromanol lead prioritization | ready for methodology outline | FE plan rows=32; RBFE readiness doc=yes | Write as staged validation paper/protocol: Boltz/MD triage to OpenFE RBFE/ABFE/CBFE without overclaiming. |
| P32 | Dermal regulatory safety and topical IVPT pre-gate | ready for translational-methods outline | dermal regulatory rows=112; formulation rows=60 | Use OECD TG497, ICH S10, and FDA IVPT framing for topical lead safety/translation paper. |
| P33 | Perturbation-biology gate for skin target validation | ready for systems-biology outline | perturbation target rows=32; wet-lab schema=yes | Write as virtual-cell/phenotype bridge: target evidence, cell context, and wet-lab endpoint linkage. |
| P34 | Hydration and residence-time follow-up for stable chromanol poses | ready for methodology outline | hydration/kinetics rows=32; structure consensus rows=32 | Write as MD limitation paper: RMSD stability is not kinetics; propose WaterKit/GIST/SMD follow-up. |
| P35 | Ultra-large active-learning screening roadmap for dermatology leads | ready for roadmap/methods outline | ultra-large roadmap rows=50; active-learning rows=672 | Use as scalable discovery systems paper: NPASS to ZINC/REAL/active docking without brute-force overreach. |
| P36 | Model validation, applicability domain, and uncertainty in autonomous triage | ready for methods/results outline | uncertainty rows=672; active-learning rows=672 | Write as rigorous ML validation paper: scaffold domain, activity-cliff risk, and conformal-style intervals. |
| P37 | Cell Painting phenomics bridge for dermatology candidate triage | ready for translational-methods outline | phenomics rows=752; wet-lab schema=yes | Use as phenotype-bridge paper/protocol: JUMP/CPJUMP-style morphology, disease-cell assay anchors, and no-MOA-claim caveat. |
| P38 | Developability and CMC pre-gate for topical chromanol/NPASS leads | ready for translational-methods outline | CMC rows=112; dermal regulatory rows=112; formulation rows=60 | Write as lead-de-risking paper: solubility, pH stability, excipient compatibility, solid-form, and scale-up risk. |
| P39 | Patent/FTO watchlist and claim-discipline workflow | ready for operations/IP outline | IP/FTO rows=752; local novelty rows=112 | Use as internal/commercial-translational methods note; keep legal/FTO conclusions pending manual review. |
| P40 | FAIR assay metadata and CRO feedback ingestion workflow | ready for reproducibility-methods outline | FAIR dictionary rows=33; wet-lab ingested rows=0 | Write as reproducibility/CRO handoff paper: ISA/BAO/RO-Crate-ready metadata and queue feedback rules. |
| P41 | Regulatory-grade AI/model governance registry for autonomous discovery | ready for governance-methods outline | model registry rows=8; provenance manifest=yes | Write as AI governance paper: context-of-use, model cards, risk tiers, validation status, and claim limits. |
| P42 | Cross-model structure consensus and negative-control readiness | ready for methods/results outline | structure consensus v1 rows=32; v2 rows=32; pose gate pass/review/fail=20/12/0 | Write as DL cofolding claim-discipline paper: Boltz/PoseBusters/MD/pocket/applicability-domain plus cross-model gaps. |
| P43 | Constrained generative chromanol analog design queue | complete PDF+figures | generative chromanol rows=330; R17 cofold rows=240/240; R17 top green-target 10ns=3/3; R17 top green-target 30ns=3/3; R17 top green-target 60ns=3/3; R17 next green-target 10ns=3/3; R17 next green-target 30ns=3/3; R17 next green-target 60ns=3/3; R17 expanded green-target 10ns=3/3; R17 expanded green-target 30ns=3/3; R17 expanded green-target 60ns=3/3; figures=4; PDF=yes; route enumeration rows=1082; photosafety v2 rows=1082 | Write as hit-to-lead expansion paper/protocol; keep expanded fluorinated candidates as in-silico, wet-lab-pending examples. |
| P44 | Route-enumerated synthesis planning for chromanol/NPASS leads | ready for translational-methods outline | route enumeration rows=1082; synthesis gate rows=112; CMC rows=112 | Use as synthesis-readiness paper/RFQ appendix; avoid lead expansion for route_review/route_hard candidates. |
| P45 | Skin cell-state anchored dermatology target validation | ready for systems-biology outline | skin cell-state rows=32; perturbation rows=32; phenomics rows=752 | Write as disease-cell endpoint paper: melanocyte/fibroblast/sebocyte/keratinocyte mapping and phenotype-first rules. |
| P46 | Photosafety and skin-sensitization preclinical assay package | ready for translational-safety outline | photosafety v2 rows=1082; dermal regulatory rows=112 | Write as topical-safety gate paper/RFQ appendix using OECD TG497 and ICH S10 caveats. |
| P47 | Design-make-test-learn experiment-card workflow | ready for CRO/wet-lab operations outline | DMTL cards=16; wet-lab ingested rows=0; FAIR dictionary rows=33 | Use as closed-loop operating paper: compute result to CRO assay card to wet-lab feedback ingestion. |
| P48 | Benchmark-grade decoy validation for DL cofolding | ready for validation-methods outline | structure benchmark rows=32; structure consensus v2 rows=32; pose gate pass/review/fail=20/12/0 | Build decoy/cross-model/PLIF protocol paper and keep binding claims caveated until benchmark controls exist. |
| P49 | Human skin spatial-atlas anchored target triage | ready for systems-biology outline | skin spatial rows=32; skin cell-state rows=32; target gate green/yellow/red=13/10/8 | Add site/cell/niche tables to target-focused papers and prioritize atlas anchors over docking-only ranking. |
| P50 | Target engagement and deconvolution assay readiness | ready for DMTL/CRO outline | target engagement rows=32; DMTL cards=16; target gate green/yellow/red=13/10/8 | Write CETSA/TPP/SPR/reporter readiness table and separate direct engagement from phenotype-only claims. |
| P51 | Dermal PBPK and finite-dose IVRT/IVPT workflow | ready for translational-methods outline | dermal PBPK rows=1082; dermal regulatory rows=112; formulation rows=60 | Build finite-dose IVRT/IVPT/PBPK parameter table and CRO RFQ appendix before stronger topical exposure claims. |
| P52 | Genetic causality and direction-of-effect target validation | ready for evidence-methods outline | genetic causality rows=31; target gate green/yellow/red=13/10/8 | Use Open Targets Genetics/MR/pQTL/eQTL or phenotype evidence caveats before direction-of-effect claims. |
| P53 | Metabolism and reactive-metabolite risk gate | ready for safety-methods outline | metabolite risk rows=1082; photosafety v2 rows=1082; quinone safety rows=1006 | Write BioTransformer/FAME-style follow-up plan and block safety-positive language for reactive-alert candidates. |
| P54 | Pharmacovigilance signal and class-safety caveat workflow | ready for safety-surveillance outline | pharmacovigilance rows=442; model registry rows=8 | Draft AEMS/FAERS/literature-signal workflow and state explicitly that signal is not causation. |
| P55 | Single-cell foundation-model reliability for virtual-cell claims | ready for ML-reliability outline | single-cell FM rows=32; perturbation rows=32; phenomics rows=752 | Write zero-shot reliability and simple-baseline control paper before using foundation-model claims as primary evidence. |
| P56 | Quinone reactivity and sensitization gate for EMB-3-class leads | ready for safety-methods outline | quinone safety rows=1006; photosafety v2 rows=1082; metabolite risk rows=1082 | Write as EMB-3/Embelin-class safety caveat paper or appendix: GSH/NAC trapping, DPRA/KeratinoSens/h-CLAT, ROS/redox cycling, ICH S10 photostability, and skin S9 metabolism before safety-positive claims. |
| P57 | World-class gap-closure master gate for autonomous discovery | ready for systems/operations paper | master rows=2328; readiness counts={'cheap_compute_or_paper_with_fto_caveat': 378, 'triage_accumulating': 1193, 'hold_or_benchmark_only': 757}; heavy-compute counts={'short_triage_only': 378, 'cheap_compute_only': 1193, 'hold': 757} | Use as the top-level decision layer tying prior-art/FTO, structure consensus, FE, synthesis, dermal translation, phenotype biology, uncertainty, and governance into one queue policy. |
| P58 | Creative-discovery gap matrix and active-learning fallback | ready for systems/creative-discovery paper | creative gap rows=10; active-learning candidates=672; active cofold manifests=496; completed short-cofold rows=480; pending short-cofold pairs=160; runnable short-cofold pairs=0; blocked missing-MSA pairs=160; missing target A3M=14 | Write as the creative-discovery operating paper: synthesis-native generation, scaffold hopping, target MSA cache, cryptic-pocket, phenomics-first objective, and GPU fallback rules. |

## Immediate Writing Priority

1. P16/P17: R16 topical chromanol lead paper와 R15 safety-first triage paper는 PDF+figures 완료 상태로 유지한다; 다음은 submit/CRO/FTO 패키지다.
2. P43: R17 constrained generative chromanol analog paper는 expanded green-target 60 ns 3/3 완료로 PDF+figures complete 상태다; 다음은 Markush/FTO, cross-model/decoy/PLIF, wet-lab/formulation 패키지다.
3. P18/P19: NPASS xTB atlas/methodology pair. 96conf tier 완료 후 자동 승격한다.
4. P24: scar/fibrosis TGFB1/MMP1 focused paper. CRO RFQ와 직접 연결되는 translational paper로 쓴다.
5. P25/P26: target evidence gate와 provenance/wet-lab feedback schema는 기존 논문들의 방법론 보강 또는 독립 systems paper로 분리 가능하다.
6. P27/P28: synthesis gate와 active-learning/multi-fidelity planner는 계산 큐가 왜 특정 후보를 고르는지 설명하는 독립 방법론 논문으로 바로 작성 가능하다.
7. P29/P30: formulation BO와 structure consensus calibration은 wet-lab/CRO 연결성과 DL cofolding 한계를 보강하는 별도 논문 후보로 유지한다.
8. P31/P32: free-energy validation과 dermal regulatory safety gate는 R16/R15 lead claim의 가장 중요한 보강 축이다.
9. P33-P36: perturbation biology, hydration/kinetics, ultra-large roadmap, ML uncertainty는 글로벌 SOTA 대비 부족한 부분을 메우는 methodology paper 후보로 유지한다.
10. P37-P41: phenomics, CMC, IP/FTO, FAIR assay ingestion, model governance는 compute-only 시스템을 translational operating system으로 확장하는 논문 후보로 유지한다.
11. P42-P47: cross-model consensus, generative chromanol design, route enumeration, skin cell-state, photosafety, DMTL card는 글로벌 SOTA gap-closure 논문 후보로 유지한다.
12. P48-P56: decoy benchmark, spatial atlas, target engagement, dermal PBPK/IVPT, genetic causality, metabolite risk, pharmacovigilance, single-cell FM reliability, quinone safety는 최신 translational SOTA gap-closure 논문 후보로 유지한다.
13. P57: world-class gap-closure master gate는 모든 gate를 하나로 묶는 운영/방법론 paper로 유지하고, 새 GPU/FE/합성 승격 판단의 최상위 근거로 쓴다.
14. P58: creative-discovery gap matrix는 chromanol 주변 최적화에서 벗어나 synthesis-native, scaffold-hop, phenomics-first, cryptic-pocket, target-cache-aware discovery로 확장하는 독립 시스템 논문 후보로 쓴다.

## Compute-to-Paper Decision Logic

- target evidence gate `green` + stable MD/cofold + plausible safety -> compute expansion and target-focused paper 후보.
- synthesis gate `green` + novelty `novel_or_distinct` + active-learning acquisition high -> Boltz-2 또는 MD 후속 후보.
- multi-fidelity BO plan이 `single-point wet-lab`을 추천하면 더 큰 GPU 확장보다 assay/IVRT/IVPT 설계를 우선 고려한다.
- structure consensus `high_confidence`는 main table 후보, `usable_with_caveat`는 보조 표 또는 limitation 후보로 둔다.
- pocket gate가 `hard_or_indirect`인 target은 direct binding claim을 피하고 phenotype/network claim으로 낮춘다.
- formulation BO rows가 생기면 CRO RFQ appendix와 P29 manuscript table에 동시에 반영한다.
- free-energy validation plan이 `RBFE_network`를 추천해도 GPU가 이미 MD에 쓰이면 production FE는 보류하고 protocol/edge plan만 갱신한다.
- dermal regulatory gate `red` 후보는 topical lead claim에서 제외하고, `yellow`는 OECD TG497/ICH S10/FDA IVPT caveat를 붙인다.
- perturbation biology `high` target은 phenotype/LINCS/Geneformer/scGPT 연결 후보로 올리고, `low` target은 direct biology claim을 피한다.
- hydration/kinetics gate의 residence proxy 후보는 60-100 ns 안정성 이후에만 SMD/tauRAMD-style follow-up으로 올린다.
- ultra-large roadmap stage1 이상은 외부 library/storage/license 확인 전에는 실제 download/docking을 큐잉하지 않는다.
- model uncertainty `activity_cliff_risk` 또는 `novel_scaffold`는 direct Boltz/pose/MD 없이 paper main table에 올리지 않는다.
- phenomics gate `priority_cell_painting`은 더 큰 GPU 반복보다 disease-cell phenotype/Cell Painting assay 설계를 우선 고려한다.
- CMC gate `yellow/red` 후보는 lead claim보다 solubility, pH stability, excipient compatibility, solid-form risk 보강으로 돌린다.
- IP/FTO watchlist `high_review` 후보는 patent/FTO 수동 검토 전까지 novelty/commercial claim을 금지한다.
- FAIR assay schema 필수 metadata가 없는 wet-lab row는 논문 main evidence가 아니라 QC 보류로 둔다.
- model governance `tier2` component가 main claim에 영향을 주면 orthogonal check 또는 explicit limitation을 붙인다.
- structure consensus v2 `needs_cross_model`은 Chai-1/DiffDock/Vina/PLIF/negative-control 중 하나 이상을 먼저 요구한다.
- chromanol generative optimizer `Boltz-2_next_when_GPU_free`는 현재 GPU MD가 끝난 뒤 non-duplicate 후보만 큐잉한다.
- route enumeration `route_review/route_hard`는 synthesis route 확인 전 lead expansion에서 제외한다.
- skin cell-state `phenotype_first`는 추가 docking보다 cell assay endpoint 설계를 우선한다.
- photosafety v2 `yellow`는 OECD TG497/ICH S10 assay package를 같이 붙이고, `red`는 topical lead claim에서 제외한다.
- quinone safety `quinone_reactivity_review`는 GSH/NAC trapping, DPRA/KeratinoSens/h-CLAT, ROS/redox cycling, ICH S10 photostability, skin S9 metabolism 전까지 EMB-3/quinone safety-positive claim을 금지한다.
- DMTL `single_point_wetlab_card`는 추가 GPU 반복보다 CRO/wet-lab quote/assay ordering 후보로 승격한다.
- structure benchmark `benchmark_decoys_required_before_strong_claim`은 cross-model/decoy/PLIF control 전까지 direct binding strong claim을 금지한다.
- skin spatial atlas `spatially_anchorable`은 site/cell/niche table을 target paper main evidence로 올리고, `atlas_review`는 docking보다 atlas/literature 확인을 우선한다.
- target engagement `engagement_assay_ready`는 DMTL/wet-lab card로 승격하고, `deconvolution_first`는 direct target engagement claim을 보류한다.
- dermal PBPK/IVPT `ivpt_pbpk_ready`는 finite-dose IVRT/IVPT/PBPK table 후보로 올리고, `formulation_rescue_needed`는 추가 docking보다 formulation BO를 우선한다.
- genetic causality `direction_needs_genetic_or_phenotype_support`는 Open Targets Genetics/MR/pQTL/eQTL 또는 phenotype evidence 없이는 direction-of-effect claim을 금지한다.
- metabolite risk `reactive_metabolite_review`는 BioTransformer/FAME-style follow-up 전까지 safety-positive language를 금지한다.
- pharmacovigilance `pv_signal_review`는 AEMS/FAERS/literature signal check 전까지 class-safety claim을 제한한다.
- single-cell FM `zero_shot_reliability_review`는 simple baseline/fine-tuning/cell-type proximity control 없이는 virtual-cell 결과를 보조 evidence로만 둔다.
- world-class master gate `hold_or_benchmark_only` 또는 `heavy_compute_permission=hold`는 신규 long-MD/FE/합성/상업 claim을 차단한다.
- world-class master gate `wetlab_translation_priority`는 더 큰 GPU 반복보다 CRO/DMTL/IVRT/IVPT/Cell Painting package를 우선한다.
- creative discovery matrix의 `target_msa_coverage` gap은 target-specific cofold를 차단한다. MC1R처럼 target-key A3M이 없으면 cache 준비가 먼저다.
- active-learning short cofold 결과는 GPU 유휴 방지용 triage다. 완료 row는 master gate에 들어가지만 long-MD/FE/lead claim은 synthesis/prior-art/safety/phenomics/uncertainty gate 이후다.
- 새 scaffold 또는 scaffold-hop queue는 synthesis-native generation, novelty/diversity guard, decoy/benchmark guard 없이 paper main lead로 올리지 않는다.
- target evidence gate `yellow` -> phenotype/cell/wet-lab endpoint가 같이 있어야 manuscript claim에 포함한다.
- target evidence gate `red` -> negative-control, limitation, future-work로만 사용한다.
- GPU MD stable + cofold affinity meaningful + ADMET/skin-window plausible -> target-focused paper 후보.
- 대량 CPU screen만 있고 target cofold가 없으면 atlas/methodology paper 후보로 유지한다.
- drift 또는 toxicity caveat가 있으면 failure-mode/methodology paper로 전환한다.
- 같은 molecule/target 결과라도 universal-scaffold paper, topical-lead paper, methodology paper의 질문이 다르면 분리 가능하다.

```
### docs/TARGET_EVIDENCE_GATE.md tail -160

```text
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

```
### docs/ACTIVE_LEARNING_DOCKING_SURROGATE.md tail -120

```text
# Active-learning Docking Surrogate

- timestamp: `2026-05-06T12:46:06+09:00`
- training_rows: `32`
- candidate_rows: `672`
- leave-one-out MAE: `0.0765`
- purpose: 이미 계산한 Boltz/MD 결과에서 다음 cofold 후보를 능동 선택한다.

## Top Recommendations

| rank | candidate | target | source | predicted | uncertainty | acquisition | next |
|---:|---|---|---|---:|---:|---:|---|
| 1 | R15_chromanol_Cl_pos9 | tgfb1 | r16_chromanol_topical_cofold | 0.7344 | 0.0298 | 0.7848 | skip_or_MD_if_unvalidated |
| 2 | R15_chromanol_Cl_pos6 | tgfb1 | r16_chromanol_topical_cofold | 0.7344 | 0.0298 | 0.7848 | skip_or_MD_if_unvalidated |
| 3 | R15_chromanol_Cl_pos10 | tgfb1 | r16_chromanol_topical_cofold | 0.7344 | 0.0298 | 0.7848 | skip_or_MD_if_unvalidated |
| 4 | R15_chromanol | tgfb1 | r15_chromanol_cofold | 0.6812 | 0.1004 | 0.7515 | skip_or_MD_if_unvalidated |
| 5 | R15_chromanol_Me6_Me9 | tgfb1 | r16_chromanol_topical_cofold | 0.6883 | 0.082 | 0.7514 | skip_or_MD_if_unvalidated |
| 6 | R15_chromanol_Me6_Me10 | tgfb1 | r16_chromanol_topical_cofold | 0.6883 | 0.082 | 0.7514 | skip_or_MD_if_unvalidated |
| 7 | R15_chromanol_Me9_Me10 | tgfb1 | r16_chromanol_topical_cofold | 0.6883 | 0.082 | 0.7514 | skip_or_MD_if_unvalidated |
| 8 | NPC243469 | dct | npass_xtb_best_cross_target | 0.5925 | 0.0482 | 0.6534 | Boltz-2 cofold |
| 9 | NPC194985 | dct | npass_xtb_best_cross_target | 0.5925 | 0.0482 | 0.6534 | Boltz-2 cofold |
| 10 | NPC196715 | dct | npass_xtb_best_cross_target | 0.5925 | 0.0482 | 0.6534 | Boltz-2 cofold |
| 11 | NPC261839 | dct | npass_xtb_best_cross_target | 0.5925 | 0.0482 | 0.6534 | Boltz-2 cofold |
| 12 | NPC469970 | dct | npass_xtb_best_cross_target | 0.5925 | 0.0482 | 0.6534 | Boltz-2 cofold |
| 13 | R15_chromanol_Cl_pos9 | dct | r16_chromanol_topical_cofold | 0.5925 | 0.0482 | 0.6494 | skip_or_MD_if_unvalidated |
| 14 | R15_chromanol_Cl_pos6 | dct | r16_chromanol_topical_cofold | 0.5925 | 0.0482 | 0.6494 | skip_or_MD_if_unvalidated |
| 15 | R15_chromanol_Cl_pos10 | dct | r16_chromanol_topical_cofold | 0.5925 | 0.0482 | 0.6494 | skip_or_MD_if_unvalidated |
| 16 | NPC243469 | ctgf | npass_xtb_best_cross_target | 0.5713 | 0.0641 | 0.6378 | Boltz-2 cofold |
| 17 | NPC243469 | lox | npass_xtb_best_cross_target | 0.5713 | 0.0641 | 0.6378 | Boltz-2 cofold |
| 18 | NPC243469 | mmp1 | npass_xtb_best_cross_target | 0.5713 | 0.0641 | 0.6378 | Boltz-2 cofold |
| 19 | NPC243469 | mc1r | npass_xtb_best_cross_target | 0.5713 | 0.0641 | 0.6378 | Boltz-2 cofold |
| 20 | NPC243469 | nr3c1 | npass_xtb_best_cross_target | 0.5713 | 0.0641 | 0.6378 | Boltz-2 cofold |
| 21 | NPC243469 | tyrp1 | npass_xtb_best_cross_target | 0.5713 | 0.0641 | 0.6378 | Boltz-2 cofold |
| 22 | NPC194985 | ctgf | npass_xtb_best_cross_target | 0.5713 | 0.0641 | 0.6378 | Boltz-2 cofold |
| 23 | NPC194985 | lox | npass_xtb_best_cross_target | 0.5713 | 0.0641 | 0.6378 | Boltz-2 cofold |
| 24 | NPC194985 | mmp1 | npass_xtb_best_cross_target | 0.5713 | 0.0641 | 0.6378 | Boltz-2 cofold |
| 25 | NPC194985 | mc1r | npass_xtb_best_cross_target | 0.5713 | 0.0641 | 0.6378 | Boltz-2 cofold |

## Curator Use

- `acquisition_score` 상위 후보 중 synthesis gate가 `red`가 아닌 것을 우선한다.
- 이미 labeled pair는 중복 cofold하지 말고 MD/pose/consensus 보강 여부만 본다.
- 모델은 local surrogate이므로 논문에는 후보 선택 heuristic으로만 서술한다.

```
### docs/MULTI_FIDELITY_BO_PLANNER.md tail -120

```text
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

```
### docs/STRUCTURE_CONSENSUS_CALIBRATION.md tail -120

```text
# Structure Consensus Calibration

- timestamp: `2026-05-06T12:46:10+09:00`
- rows: `32`
- class_counts: `{'high_confidence': 6, 'usable_with_caveat': 18, 'review_before_claim': 8}`
- purpose: Boltz affinity만으로 claim하지 않고 pose sanity와 MD 안정성을 합쳐 confidence를 보정한다.

## Top Calibrated Pairs

| job | target | compound | class | score | pose | MD |
|---|---|---|---|---:|---|---|
| r16_03_dct | dct | R15_chromanol_Cl_pos9 | high_confidence | 0.7593 | pass | strong_stable |
| r15_chrom_tyr | tyr | R15_chromanol | high_confidence | 0.7574 | pass | strong_stable |
| r16_05_tgfb1 | tgfb1 | R15_chromanol_Me6_Me9 | high_confidence | 0.7536 | pass | strong_stable |
| r16_02_dct | dct | R15_chromanol_Cl_pos6 | high_confidence | 0.7514 | pass | strong_stable |
| r16_02_tyr | tyr | R15_chromanol_Cl_pos6 | high_confidence | 0.7492 | pass | strong_stable |
| r16_03_tgfb1 | tgfb1 | R15_chromanol_Cl_pos9 | usable_with_caveat | 0.7435 | review | strong_stable |
| r16_02_tgfb1 | tgfb1 | R15_chromanol_Cl_pos6 | high_confidence | 0.7355 | pass | strong_stable |
| r15_chrom_dct | dct | R15_chromanol | usable_with_caveat | 0.7333 | review | strong_stable |
| r16_06_tgfb1 | tgfb1 | R15_chromanol_Me9_Me10 | usable_with_caveat | 0.7263 | review | strong_stable |
| r15_chrom_tgfb1 | tgfb1 | R15_chromanol | usable_with_caveat | 0.7158 | review | strong_stable |
| r16_04_tgfb1 | tgfb1 | R15_chromanol_Me6_Me10 | usable_with_caveat | 0.7143 | review | strong_stable |
| r16_01_tgfb1 | tgfb1 | R15_chromanol_Cl_pos10 | usable_with_caveat | 0.704 | review | strong_stable |
| r15_chrom_ptgs2 | ptgs2 | R15_chromanol | usable_with_caveat | 0.6475 | pass | missing |
| r16_03_tyr | tyr | R15_chromanol_Cl_pos9 | usable_with_caveat | 0.637 | pass | missing |
| r16_01_dct | dct | R15_chromanol_Cl_pos10 | usable_with_caveat | 0.6307 | review | missing |
| r16_01_tyr | tyr | R15_chromanol_Cl_pos10 | usable_with_caveat | 0.626 | pass | missing |
| r15_chrom_tyrp1 | tyrp1 | R15_chromanol | usable_with_caveat | 0.6248 | pass | missing |
| r16_06_tyr | tyr | R15_chromanol_Me9_Me10 | usable_with_caveat | 0.6062 | pass | missing |
| r16_05_tyr | tyr | R15_chromanol_Me6_Me9 | usable_with_caveat | 0.6045 | pass | missing |
| r16_05_dct | dct | R15_chromanol_Me6_Me9 | usable_with_caveat | 0.5986 | pass | missing |
| r16_06_dct | dct | R15_chromanol_Me9_Me10 | usable_with_caveat | 0.5982 | pass | missing |
| r16_04_tyr | tyr | R15_chromanol_Me6_Me10 | usable_with_caveat | 0.5644 | review | missing |
| r16_04_dct | dct | R15_chromanol_Me6_Me10 | usable_with_caveat | 0.5506 | review | missing |
| r15_chrom_mmp1 | mmp1 | R15_chromanol | usable_with_caveat | 0.5295 | review | missing |
| r15_chrom_sirt1 | sirt1 | R15_chromanol | review_before_claim | 0.5024 | review | missing |

## Curator Use

- `high_confidence`는 manuscript main table에 넣을 수 있다.
- `usable_with_caveat`는 raw pose/MD caveat와 함께 보조 표 또는 discussion에 둔다.
- `review_before_claim`은 cross-model consensus 또는 wet-lab 전까지 강한 lead claim을 피한다.

```
### docs/STRUCTURE_CONSENSUS_V2.md tail -120

```text
# Structure Consensus V2

- timestamp: `2026-05-06T12:46:11+09:00`
- rows: `32`
- claim_counts: `{'claim_ready_in_silico': 0, 'claim_with_caveat': 8, 'needs_cross_model': 5, 'triage_only': 19}`
- purpose: single-model Boltz claim을 피하고, PoseBusters/MD/pocket/applicability-domain을 합쳐 orthogonal validation priority를 정한다.

## Top Claim-Readiness Rows

| job | target | compound | readiness | score | pose | MD | pocket | next |
|---|---|---|---|---:|---|---|---|---|
| r16_03_dct | dct | R15_chromanol_Cl_pos9 | claim_with_caveat | 0.7338 | pass | long_stable | direct_pocket_plausible | supplement/main-candidate table; request cross-model consensus before strong claim |
| r16_02_dct | dct | R15_chromanol_Cl_pos6 | claim_with_caveat | 0.7276 | pass | long_stable | direct_pocket_plausible | supplement/main-candidate table; request cross-model consensus before strong claim |
| r16_02_tyr | tyr | R15_chromanol_Cl_pos6 | claim_with_caveat | 0.7262 | pass | long_stable | direct_pocket_plausible | supplement/main-candidate table; request cross-model consensus before strong claim |
| r16_05_tgfb1 | tgfb1 | R15_chromanol_Me6_Me9 | claim_with_caveat | 0.6803 | pass | long_stable | interface_or_biologic | supplement/main-candidate table; request cross-model consensus before strong claim |
| r16_02_tgfb1 | tgfb1 | R15_chromanol_Cl_pos6 | claim_with_caveat | 0.6661 | pass | long_stable | interface_or_biologic | supplement/main-candidate table; request cross-model consensus before strong claim |
| r16_03_tgfb1 | tgfb1 | R15_chromanol_Cl_pos9 | claim_with_caveat | 0.6657 | review | long_stable | interface_or_biologic | supplement/main-candidate table; request cross-model consensus before strong claim |
| r16_06_tgfb1 | tgfb1 | R15_chromanol_Me9_Me10 | claim_with_caveat | 0.6536 | review | long_stable | interface_or_biologic | supplement/main-candidate table; request cross-model consensus before strong claim |
| r16_04_tgfb1 | tgfb1 | R15_chromanol_Me6_Me10 | claim_with_caveat | 0.6434 | review | long_stable | interface_or_biologic | supplement/main-candidate table; request cross-model consensus before strong claim |
| r16_01_tgfb1 | tgfb1 | R15_chromanol_Cl_pos10 | needs_cross_model | 0.636 | review | long_stable | interface_or_biologic | run Chai-1/DiffDock/Vina or PLIF/negative-control check before manuscript lead claim |
| r15_chrom_tyr | tyr | R15_chromanol | needs_cross_model | 0.5927 | pass | missing | direct_pocket_plausible | run Chai-1/DiffDock/Vina or PLIF/negative-control check before manuscript lead claim |
| r15_chrom_ptgs2 | ptgs2 | R15_chromanol | triage_only | 0.5869 | pass | missing | direct_pocket_plausible | keep as queue candidate or negative-control/failure-mode evidence |
| r16_03_tyr | tyr | R15_chromanol_Cl_pos9 | triage_only | 0.5772 | pass | missing | direct_pocket_plausible | keep as queue candidate or negative-control/failure-mode evidence |
| r15_chrom_dct | dct | R15_chromanol | needs_cross_model | 0.5713 | review | missing | direct_pocket_plausible | run Chai-1/DiffDock/Vina or PLIF/negative-control check before manuscript lead claim |
| r16_01_dct | dct | R15_chromanol_Cl_pos10 | needs_cross_model | 0.569 | review | missing | direct_pocket_plausible | run Chai-1/DiffDock/Vina or PLIF/negative-control check before manuscript lead claim |
| r16_01_tyr | tyr | R15_chromanol_Cl_pos10 | triage_only | 0.5684 | pass | missing | direct_pocket_plausible | keep as queue candidate or negative-control/failure-mode evidence |
| r15_chrom_tyrp1 | tyrp1 | R15_chromanol | triage_only | 0.5683 | pass | missing | direct_pocket_plausible | keep as queue candidate or negative-control/failure-mode evidence |
| r16_06_tyr | tyr | R15_chromanol_Me9_Me10 | triage_only | 0.5537 | pass | missing | direct_pocket_plausible | keep as queue candidate or negative-control/failure-mode evidence |
| r16_05_tyr | tyr | R15_chromanol_Me6_Me9 | triage_only | 0.5527 | pass | missing | direct_pocket_plausible | keep as queue candidate or negative-control/failure-mode evidence |
| r16_05_dct | dct | R15_chromanol_Me6_Me9 | triage_only | 0.5476 | pass | missing | direct_pocket_plausible | keep as queue candidate or negative-control/failure-mode evidence |
| r16_06_dct | dct | R15_chromanol_Me9_Me10 | triage_only | 0.5472 | pass | missing | direct_pocket_plausible | keep as queue candidate or negative-control/failure-mode evidence |
| r16_04_tyr | tyr | R15_chromanol_Me6_Me10 | triage_only | 0.5192 | review | missing | direct_pocket_plausible | keep as queue candidate or negative-control/failure-mode evidence |
| r16_04_dct | dct | R15_chromanol_Me6_Me10 | triage_only | 0.5082 | review | missing | direct_pocket_plausible | keep as queue candidate or negative-control/failure-mode evidence |
| r15_chrom_tgfb1 | tgfb1 | R15_chromanol | needs_cross_model | 0.5054 | review | missing | interface_or_biologic | run Chai-1/DiffDock/Vina or PLIF/negative-control check before manuscript lead claim |
| r15_chrom_mmp1 | mmp1 | R15_chromanol | triage_only | 0.4861 | review | missing | direct_pocket_plausible | keep as queue candidate or negative-control/failure-mode evidence |
| r15_chrom_srd5a2 | srd5a2 | R15_chromanol | triage_only | 0.4742 | pass | missing | direct_pocket_plausible | keep as queue candidate or negative-control/failure-mode evidence |
| r15_chrom_ar | ar | R15_chromanol | triage_only | 0.4543 | pass | missing | direct_pocket_plausible | keep as queue candidate or negative-control/failure-mode evidence |
| r15_chrom_lox | lox | R15_chromanol | triage_only | 0.4508 | pass | missing | direct_pocket_plausible | keep as queue candidate or negative-control/failure-mode evidence |
| r15_chrom_sirt1 | sirt1 | R15_chromanol | triage_only | 0.4141 | review | missing | unknown | keep as queue candidate or negative-control/failure-mode evidence |
| r15_chrom_srd5a1 | srd5a1 | R15_chromanol | triage_only | 0.4003 | pass | missing | direct_pocket_plausible | keep as queue candidate or negative-control/failure-mode evidence |
| r15_chrom_srebp1 | srebp1 | R15_chromanol | triage_only | 0.3939 | pass | missing | missing | keep as queue candidate or negative-control/failure-mode evidence |

## Curator Rule

- `claim_ready_in_silico`: 논문 main table 가능. 단, `in silico`와 orthogonal-model 미실행 caveat를 유지한다.
- `claim_with_caveat`: 보조 표 또는 제한적 main candidate. cross-model 또는 wet-lab 전까지 binding-confirmed 표현 금지.
- `needs_cross_model`: Chai-1/DiffDock/Vina/PLIF/negative-control 중 하나 이상을 먼저 큐잉한다.
- `triage_only`: 후보 탐색 또는 failure-mode paper에만 사용한다.

```
### docs/CHROMANOL_GENERATIVE_OPTIMIZER.md tail -120

```text
# Chromanol Generative Optimizer

- timestamp: `2026-05-06T12:46:11+09:00`
- rows: `330`
- action_counts: `{'Boltz-2_next_when_GPU_free': 240, 'keep_for_route_or_safety_review': 82, 'archive_low_priority': 8}`
- purpose: R15/R16 chromanol core 주변에서 valid RDKit analog를 만들어 다음 Boltz/route/safety 큐 후보를 넓힌다.

## Top Local Designs

| design | target | priority | cLogP | TPSA | novelty | route | photosafety | action |
|---|---|---:|---:|---:|---|---|---|---|
| chromanol_arom9+arom10_Cl+Cl_tgfb1 | tgfb1 | 0.8137 | 2.242 | 49.69 | new_local_design | route_ready | aryl_halogen_review | Boltz-2_next_when_GPU_free |
| chromanol_arom6+arom9_Cl+Cl_tgfb1 | tgfb1 | 0.8117 | 2.242 | 49.69 | new_local_design | route_ready | aryl_halogen_review | Boltz-2_next_when_GPU_free |
| chromanol_arom9_Cl_tgfb1 | tgfb1 | 0.8003 | 1.589 | 49.69 | known_or_precomputed | route_ready | aryl_halogen_review | keep_for_route_or_safety_review |
| chromanol_arom6+arom10_Cl+Cl_tgfb1 | tgfb1 | 0.7999 | 2.242 | 49.69 | new_local_design | route_ready | aryl_halogen_review | Boltz-2_next_when_GPU_free |
| chromanol_arom6+arom9_Cl+Me_tgfb1 | tgfb1 | 0.7995 | 1.897 | 49.69 | new_local_design | route_ready | aryl_halogen_review | Boltz-2_next_when_GPU_free |
| chromanol_arom6+arom9_Me+Cl_tgfb1 | tgfb1 | 0.7995 | 1.897 | 49.69 | new_local_design | route_ready | aryl_halogen_review | Boltz-2_next_when_GPU_free |
| chromanol_arom9+arom10_Cl+Me_tgfb1 | tgfb1 | 0.7995 | 1.897 | 49.69 | new_local_design | route_ready | aryl_halogen_review | Boltz-2_next_when_GPU_free |
| chromanol_arom9+arom10_Me+Cl_tgfb1 | tgfb1 | 0.7995 | 1.897 | 49.69 | new_local_design | route_ready | aryl_halogen_review | Boltz-2_next_when_GPU_free |
| chromanol_arom10_Cl_tgfb1 | tgfb1 | 0.7932 | 1.589 | 49.69 | known_or_precomputed | route_ready | aryl_halogen_review | keep_for_route_or_safety_review |
| chromanol_arom6+arom10_Cl+Me_tgfb1 | tgfb1 | 0.7884 | 1.897 | 49.69 | new_local_design | route_ready | aryl_halogen_review | Boltz-2_next_when_GPU_free |
| chromanol_arom6+arom10_Me+Cl_tgfb1 | tgfb1 | 0.7884 | 1.897 | 49.69 | new_local_design | route_ready | aryl_halogen_review | Boltz-2_next_when_GPU_free |
| chromanol_arom6+arom9_F+Cl_tgfb1 | tgfb1 | 0.7879 | 1.728 | 49.69 | new_local_design | route_ready | aryl_halogen_review | Boltz-2_next_when_GPU_free |
| chromanol_arom6+arom9_Cl+F_tgfb1 | tgfb1 | 0.7879 | 1.728 | 49.69 | new_local_design | route_ready | aryl_halogen_review | Boltz-2_next_when_GPU_free |
| chromanol_arom9+arom10_F+Cl_tgfb1 | tgfb1 | 0.7879 | 1.728 | 49.69 | new_local_design | route_ready | aryl_halogen_review | Boltz-2_next_when_GPU_free |
| chromanol_arom9+arom10_Cl+F_tgfb1 | tgfb1 | 0.7879 | 1.728 | 49.69 | new_local_design | route_ready | aryl_halogen_review | Boltz-2_next_when_GPU_free |
| chromanol_arom9+arom10_OMe+Cl_tgfb1 | tgfb1 | 0.7879 | 1.598 | 58.92 | new_local_design | route_ready | aryl_halogen_review | Boltz-2_next_when_GPU_free |
| chromanol_arom6_Cl_tgfb1 | tgfb1 | 0.7864 | 1.589 | 49.69 | known_or_precomputed | route_ready | aryl_halogen_review | keep_for_route_or_safety_review |
| chromanol_arom6+arom9_Cl+OMe_tgfb1 | tgfb1 | 0.7825 | 1.598 | 58.92 | new_local_design | route_ready | aryl_halogen_review | Boltz-2_next_when_GPU_free |
| chromanol_arom6+arom9_OMe+Cl_tgfb1 | tgfb1 | 0.7825 | 1.598 | 58.92 | new_local_design | route_ready | aryl_halogen_review | Boltz-2_next_when_GPU_free |
| chromanol_arom9+arom10_Cl+OMe_tgfb1 | tgfb1 | 0.7825 | 1.598 | 58.92 | new_local_design | route_ready | aryl_halogen_review | Boltz-2_next_when_GPU_free |
| chromanol_arom6+arom10_F+Cl_tgfb1 | tgfb1 | 0.7783 | 1.728 | 49.69 | new_local_design | route_ready | aryl_halogen_review | Boltz-2_next_when_GPU_free |
| chromanol_arom6+arom10_Cl+F_tgfb1 | tgfb1 | 0.7768 | 1.728 | 49.69 | new_local_design | route_ready | aryl_halogen_review | Boltz-2_next_when_GPU_free |
| chromanol_arom9+arom10_Me+Me_tgfb1 | tgfb1 | 0.7758 | 1.552 | 49.69 | known_or_precomputed | route_ready | none_detected | keep_for_route_or_safety_review |
| chromanol_arom6+arom9_Me+Me_tgfb1 | tgfb1 | 0.7738 | 1.552 | 49.69 | known_or_precomputed | route_ready | none_detected | keep_for_route_or_safety_review |
| chromanol_arom6+arom10_Cl+OMe_tgfb1 | tgfb1 | 0.7723 | 1.598 | 58.92 | new_local_design | route_ready | aryl_halogen_review | Boltz-2_next_when_GPU_free |
| chromanol_arom6+arom10_OMe+Cl_tgfb1 | tgfb1 | 0.7723 | 1.598 | 58.92 | new_local_design | route_ready | aryl_halogen_review | Boltz-2_next_when_GPU_free |
| chromanol_arom9+arom10_Cl+Cl_mmp1 | mmp1 | 0.7721 | 2.242 | 49.69 | new_local_design | route_ready | aryl_halogen_review | Boltz-2_next_when_GPU_free |
| chromanol_arom9_Me_tgfb1 | tgfb1 | 0.7703 | 1.244 | 49.69 | new_local_design | route_ready | none_detected | Boltz-2_next_when_GPU_free |
| chromanol_arom6+arom9_Cl+Cl_mmp1 | mmp1 | 0.7701 | 2.242 | 49.69 | new_local_design | route_ready | aryl_halogen_review | Boltz-2_next_when_GPU_free |
| chromanol_arom10_Me_tgfb1 | tgfb1 | 0.7632 | 1.244 | 49.69 | new_local_design | route_ready | none_detected | Boltz-2_next_when_GPU_free |
| chromanol_arom9+arom10_Cl+Cl_ptgs2 | ptgs2 | 0.7625 | 2.242 | 49.69 | new_local_design | route_ready | aryl_halogen_review | Boltz-2_next_when_GPU_free |
| chromanol_arom6+arom10_Me+Me_tgfb1 | tgfb1 | 0.7621 | 1.552 | 49.69 | known_or_precomputed | route_ready | none_detected | keep_for_route_or_safety_review |
| chromanol_arom9+arom10_Cl+Cl_dct | dct | 0.7613 | 2.242 | 49.69 | new_local_design | route_ready | aryl_halogen_review | Boltz-2_next_when_GPU_free |
| chromanol_arom6+arom9_Cl+Cl_ptgs2 | ptgs2 | 0.7605 | 2.242 | 49.69 | new_local_design | route_ready | aryl_halogen_review | Boltz-2_next_when_GPU_free |
| chromanol_arom6+arom9_Cl+Cl_dct | dct | 0.7593 | 2.242 | 49.69 | new_local_design | route_ready | aryl_halogen_review | Boltz-2_next_when_GPU_free |

## Curator Rule

- `Boltz-2_next_when_GPU_free`는 GPU가 비고 현재 R16 100 ns가 끝난 뒤 cofold 후보로 올린다.
- `known_or_precomputed`는 중복 계산하지 않고 기존 R15/R16 evidence에 합친다.
- `aryl_halogen_review`는 pigment target에서 photosafety gate를 먼저 본다.

```
### docs/ROUTE_ENUMERATION_GATE.md tail -120

```text
# Route Enumeration Gate

- timestamp: `2026-05-06T12:46:11+09:00`
- rows: `1082`
- gate_counts: `{'route_ready': 362, 'route_review': 378, 'route_hard': 342, 'red': 0}`
- purpose: SA score를 넘어서 실제 route enumeration이 필요한 후보와 바로 vendor/precursor search로 갈 후보를 분리한다.

## Top Route-Ready/Review Rows

| candidate | target | gate | family | steps | confidence | risk | next |
|---|---|---|---|---:|---:|---|---|
| chromanol_arom9+arom10_Cl+Cl_tgfb1 | tgfb1 | route_ready | chromanol_core_late_stage_substitution | 5 | 0.82 | no_major_route_risk | ASKCOS/AiZynthFinder route enumeration and vendor precursor search |
| chromanol_arom6+arom9_Cl+Cl_tgfb1 | tgfb1 | route_ready | chromanol_core_late_stage_substitution | 5 | 0.82 | no_major_route_risk | ASKCOS/AiZynthFinder route enumeration and vendor precursor search |
| chromanol_arom9_Cl_tgfb1 | tgfb1 | route_ready | chromanol_core_late_stage_substitution | 4 | 0.82 | no_major_route_risk | ASKCOS/AiZynthFinder route enumeration and vendor precursor search |
| chromanol_arom6+arom10_Cl+Cl_tgfb1 | tgfb1 | route_ready | chromanol_core_late_stage_substitution | 5 | 0.82 | no_major_route_risk | ASKCOS/AiZynthFinder route enumeration and vendor precursor search |
| chromanol_arom6+arom9_Cl+Me_tgfb1 | tgfb1 | route_ready | chromanol_core_late_stage_substitution | 4 | 0.82 | no_major_route_risk | ASKCOS/AiZynthFinder route enumeration and vendor precursor search |
| chromanol_arom6+arom9_Me+Cl_tgfb1 | tgfb1 | route_ready | chromanol_core_late_stage_substitution | 4 | 0.82 | no_major_route_risk | ASKCOS/AiZynthFinder route enumeration and vendor precursor search |
| chromanol_arom9+arom10_Cl+Me_tgfb1 | tgfb1 | route_ready | chromanol_core_late_stage_substitution | 4 | 0.82 | no_major_route_risk | ASKCOS/AiZynthFinder route enumeration and vendor precursor search |
| chromanol_arom9+arom10_Me+Cl_tgfb1 | tgfb1 | route_ready | chromanol_core_late_stage_substitution | 4 | 0.82 | no_major_route_risk | ASKCOS/AiZynthFinder route enumeration and vendor precursor search |
| chromanol_arom10_Cl_tgfb1 | tgfb1 | route_ready | chromanol_core_late_stage_substitution | 4 | 0.82 | no_major_route_risk | ASKCOS/AiZynthFinder route enumeration and vendor precursor search |
| chromanol_arom6+arom10_Cl+Me_tgfb1 | tgfb1 | route_ready | chromanol_core_late_stage_substitution | 4 | 0.82 | no_major_route_risk | ASKCOS/AiZynthFinder route enumeration and vendor precursor search |
| chromanol_arom6+arom10_Me+Cl_tgfb1 | tgfb1 | route_ready | chromanol_core_late_stage_substitution | 4 | 0.82 | no_major_route_risk | ASKCOS/AiZynthFinder route enumeration and vendor precursor search |
| chromanol_arom6+arom9_F+Cl_tgfb1 | tgfb1 | route_ready | chromanol_core_late_stage_substitution | 5 | 0.82 | no_major_route_risk | ASKCOS/AiZynthFinder route enumeration and vendor precursor search |
| chromanol_arom6+arom9_Cl+F_tgfb1 | tgfb1 | route_ready | chromanol_core_late_stage_substitution | 5 | 0.82 | no_major_route_risk | ASKCOS/AiZynthFinder route enumeration and vendor precursor search |
| chromanol_arom9+arom10_F+Cl_tgfb1 | tgfb1 | route_ready | chromanol_core_late_stage_substitution | 5 | 0.82 | no_major_route_risk | ASKCOS/AiZynthFinder route enumeration and vendor precursor search |
| chromanol_arom9+arom10_Cl+F_tgfb1 | tgfb1 | route_ready | chromanol_core_late_stage_substitution | 5 | 0.82 | no_major_route_risk | ASKCOS/AiZynthFinder route enumeration and vendor precursor search |
| chromanol_arom9+arom10_OMe+Cl_tgfb1 | tgfb1 | route_ready | chromanol_core_late_stage_substitution | 5 | 0.82 | no_major_route_risk | ASKCOS/AiZynthFinder route enumeration and vendor precursor search |
| chromanol_arom6_Cl_tgfb1 | tgfb1 | route_ready | chromanol_core_late_stage_substitution | 4 | 0.82 | no_major_route_risk | ASKCOS/AiZynthFinder route enumeration and vendor precursor search |
| chromanol_arom6+arom9_Cl+OMe_tgfb1 | tgfb1 | route_ready | chromanol_core_late_stage_substitution | 5 | 0.82 | no_major_route_risk | ASKCOS/AiZynthFinder route enumeration and vendor precursor search |
| chromanol_arom6+arom9_OMe+Cl_tgfb1 | tgfb1 | route_ready | chromanol_core_late_stage_substitution | 5 | 0.82 | no_major_route_risk | ASKCOS/AiZynthFinder route enumeration and vendor precursor search |
| chromanol_arom9+arom10_Cl+OMe_tgfb1 | tgfb1 | route_ready | chromanol_core_late_stage_substitution | 5 | 0.82 | no_major_route_risk | ASKCOS/AiZynthFinder route enumeration and vendor precursor search |
| chromanol_arom6+arom10_F+Cl_tgfb1 | tgfb1 | route_ready | chromanol_core_late_stage_substitution | 5 | 0.82 | no_major_route_risk | ASKCOS/AiZynthFinder route enumeration and vendor precursor search |
| chromanol_arom6+arom10_Cl+F_tgfb1 | tgfb1 | route_ready | chromanol_core_late_stage_substitution | 5 | 0.82 | no_major_route_risk | ASKCOS/AiZynthFinder route enumeration and vendor precursor search |
| chromanol_arom9+arom10_Me+Me_tgfb1 | tgfb1 | route_ready | chromanol_core_late_stage_substitution | 3 | 0.82 | no_major_route_risk | ASKCOS/AiZynthFinder route enumeration and vendor precursor search |
| chromanol_arom6+arom9_Me+Me_tgfb1 | tgfb1 | route_ready | chromanol_core_late_stage_substitution | 3 | 0.82 | no_major_route_risk | ASKCOS/AiZynthFinder route enumeration and vendor precursor search |
| chromanol_arom6+arom10_Cl+OMe_tgfb1 | tgfb1 | route_ready | chromanol_core_late_stage_substitution | 5 | 0.82 | no_major_route_risk | ASKCOS/AiZynthFinder route enumeration and vendor precursor search |
| chromanol_arom6+arom10_OMe+Cl_tgfb1 | tgfb1 | route_ready | chromanol_core_late_stage_substitution | 5 | 0.82 | no_major_route_risk | ASKCOS/AiZynthFinder route enumeration and vendor precursor search |
| chromanol_arom9+arom10_Cl+Cl_mmp1 | mmp1 | route_ready | chromanol_core_late_stage_substitution | 5 | 0.82 | no_major_route_risk | ASKCOS/AiZynthFinder route enumeration and vendor precursor search |
| chromanol_arom9_Me_tgfb1 | tgfb1 | route_ready | chromanol_core_late_stage_substitution | 3 | 0.82 | no_major_route_risk | ASKCOS/AiZynthFinder route enumeration and vendor precursor search |
| chromanol_arom6+arom9_Cl+Cl_mmp1 | mmp1 | route_ready | chromanol_core_late_stage_substitution | 5 | 0.82 | no_major_route_risk | ASKCOS/AiZynthFinder route enumeration and vendor precursor search |
| chromanol_arom10_Me_tgfb1 | tgfb1 | route_ready | chromanol_core_late_stage_substitution | 3 | 0.82 | no_major_route_risk | ASKCOS/AiZynthFinder route enumeration and vendor precursor search |
| chromanol_arom9+arom10_Cl+Cl_ptgs2 | ptgs2 | route_ready | chromanol_core_late_stage_substitution | 5 | 0.82 | no_major_route_risk | ASKCOS/AiZynthFinder route enumeration and vendor precursor search |
| chromanol_arom6+arom10_Me+Me_tgfb1 | tgfb1 | route_ready | chromanol_core_late_stage_substitution | 3 | 0.82 | no_major_route_risk | ASKCOS/AiZynthFinder route enumeration and vendor precursor search |
| chromanol_arom9+arom10_Cl+Cl_dct | dct | route_ready | chromanol_core_late_stage_substitution | 5 | 0.82 | no_major_route_risk | ASKCOS/AiZynthFinder route enumeration and vendor precursor search |
| chromanol_arom6+arom9_Cl+Cl_ptgs2 | ptgs2 | route_ready | chromanol_core_late_stage_substitution | 5 | 0.82 | no_major_route_risk | ASKCOS/AiZynthFinder route enumeration and vendor precursor search |
| chromanol_arom6+arom9_Cl+Cl_dct | dct | route_ready | chromanol_core_late_stage_substitution | 5 | 0.82 | no_major_route_risk | ASKCOS/AiZynthFinder route enumeration and vendor precursor search |

## Curator Rule

- `route_ready`: GPU cofold/MD 확장 또는 CRO RFQ 후보로 유지한다.
- `route_review`: ASKCOS/AiZynthFinder/manual route 전까지 대규모 GPU 확장은 보류한다.
- `route_hard`: atlas/methodology paper에는 가능하지만 lead paper main table에는 올리지 않는다.

```
### docs/SKIN_CELL_STATE_EVIDENCE_GATE.md tail -120

```text
# Skin Cell-State Evidence Gate

- timestamp: `2026-05-06T12:46:12+09:00`
- rows: `32`
- gate_counts: `{'cell_state_anchored': 2, 'phenotype_first': 8, 'target_claim_limited': 22}`
- purpose: target/cofold evidence를 실제 피부 세포 상태와 disease phenotype endpoint에 연결한다.

## Target Cell-State Map

| target | gate | disease | cell states | endpoints | next |
|---|---|---|---|---|---|
| dct | cell_state_anchored | pigment | melanocyte;melanosome_state | melanin content, DCT/TYR/TYRP1 expression | write disease-cell endpoint table and CRO assay card |
| tyr | cell_state_anchored | pigment | melanocyte;melanosome_state | tyrosinase activity, melanin content | write disease-cell endpoint table and CRO assay card |
| ar | phenotype_first | alopecia;acne | dermal_papilla_cell;sebocyte | androgen response, hair-cycle marker, sebum marker | prioritize single-cell/spatial/literature anchor before stronger binding claim |
| ctgf | phenotype_first | scar | activated_dermal_fibroblast | CTGF, collagen deposition, fibroblast activation | prioritize single-cell/spatial/literature anchor before stronger binding claim |
| lox | phenotype_first | scar;photoaging | dermal_fibroblast | collagen crosslinking, matrix stiffness | prioritize single-cell/spatial/literature anchor before stronger binding claim |
| mc1r | phenotype_first | pigment | melanocyte | cAMP response, pigmentation phenotype | prioritize single-cell/spatial/literature anchor before stronger binding claim |
| mmp1 | phenotype_first | scar;photoaging | dermal_fibroblast;photoaged_fibroblast | MMP1, COL1A1 rescue, ECM remodeling | prioritize single-cell/spatial/literature anchor before stronger binding claim |
| nr3c1 | phenotype_first | acne;photoaging | keratinocyte;immune_cell | glucocorticoid-response and barrier markers | prioritize single-cell/spatial/literature anchor before stronger binding claim |
| tgfb1 | phenotype_first | scar | activated_dermal_fibroblast;myofibroblast | collagen I/III, alpha-SMA, CTGF, wound contraction | prioritize single-cell/spatial/literature anchor before stronger binding claim |
| tyrp1 | phenotype_first | pigment | melanocyte;melanosome_state | melanosome maturation, melanin content | prioritize single-cell/spatial/literature anchor before stronger binding claim |
| col1a1 | target_claim_limited | unknown | skin_context_missing | define disease-cell phenotype endpoint | keep as exploratory or negative-control target until cell-state evidence exists |
| ctnnb1 | target_claim_limited | unknown | skin_context_missing | define disease-cell phenotype endpoint | keep as exploratory or negative-control target until cell-state evidence exists |
| f2rl1 | target_claim_limited | unknown | skin_context_missing | define disease-cell phenotype endpoint | keep as exploratory or negative-control target until cell-state evidence exists |
| fgf2 | target_claim_limited | unknown | skin_context_missing | define disease-cell phenotype endpoint | keep as exploratory or negative-control target until cell-state evidence exists |
| jun | target_claim_limited | unknown | skin_context_missing | define disease-cell phenotype endpoint | keep as exploratory or negative-control target until cell-state evidence exists |
| mitf | target_claim_limited | unknown | skin_context_missing | define disease-cell phenotype endpoint | keep as exploratory or negative-control target until cell-state evidence exists |
| mmp3 | target_claim_limited | unknown | skin_context_missing | define disease-cell phenotype endpoint | keep as exploratory or negative-control target until cell-state evidence exists |
| mmp9 | target_claim_limited | unknown | skin_context_missing | define disease-cell phenotype endpoint | keep as exploratory or negative-control target until cell-state evidence exists |
| mylk | target_claim_limited | unknown | skin_context_missing | define disease-cell phenotype endpoint | keep as exploratory or negative-control target until cell-state evidence exists |
| nlrp3 | target_claim_limited | unknown | skin_context_missing | define disease-cell phenotype endpoint | keep as exploratory or negative-control target until cell-state evidence exists |
| piezo1 | target_claim_limited | unknown | skin_context_missing | define disease-cell phenotype endpoint | keep as exploratory or negative-control target until cell-state evidence exists |
| ptgdr2 | target_claim_limited | unknown | skin_context_missing | define disease-cell phenotype endpoint | keep as exploratory or negative-control target until cell-state evidence exists |
| ptgs2 | target_claim_limited | acne;photoaging | keratinocyte;immune_cell;sebocyte | PGE2, inflammatory cytokine panel | keep as exploratory or negative-control target until cell-state evidence exists |
| rarg | target_claim_limited | unknown | skin_context_missing | define disease-cell phenotype endpoint | keep as exploratory or negative-control target until cell-state evidence exists |
| sirt1 | target_claim_limited | unknown | skin_context_missing | define disease-cell phenotype endpoint | keep as exploratory or negative-control target until cell-state evidence exists |
| srd5a1 | target_claim_limited | unknown | skin_context_missing | define disease-cell phenotype endpoint | keep as exploratory or negative-control target until cell-state evidence exists |
| srd5a2 | target_claim_limited | unknown | skin_context_missing | define disease-cell phenotype endpoint | keep as exploratory or negative-control target until cell-state evidence exists |
| srebf1 | target_claim_limited | unknown | skin_context_missing | define disease-cell phenotype endpoint | keep as exploratory or negative-control target until cell-state evidence exists |
| srebp1 | target_claim_limited | unknown | skin_context_missing | define disease-cell phenotype endpoint | keep as exploratory or negative-control target until cell-state evidence exists |
| tlr2 | target_claim_limited | unknown | skin_context_missing | define disease-cell phenotype endpoint | keep as exploratory or negative-control target until cell-state evidence exists |
| vegfa | target_claim_limited | unknown | skin_context_missing | define disease-cell phenotype endpoint | keep as exploratory or negative-control target until cell-state evidence exists |
| wnt10b | target_claim_limited | unknown | skin_context_missing | define disease-cell phenotype endpoint | keep as exploratory or negative-control target until cell-state evidence exists |

## Curator Rule

- `cell_state_anchored`: target-focused 논문과 CRO endpoint table에 바로 반영한다.
- `phenotype_first`: 추가 GPU보다 cell phenotype evidence/assay design을 우선한다.
- `target_claim_limited`: direct target efficacy claim을 피하고 exploratory로 둔다.

```
### docs/PHOTOSAFETY_SENSITIZATION_V2.md tail -120

```text
# Photosafety Sensitization V2

- timestamp: `2026-05-06T12:46:12+09:00`
- rows: `1082`
- gate_counts: `{'green': 366, 'yellow': 716, 'red': 0}`
- purpose: topical lead claim 전에 OECD TG497 skin sensitization과 ICH S10 photosafety 관점의 assay package를 자동 지정한다.

## Top Safety Rows

| candidate | target | gate | cLogP | sensitization | photosafety | assay |
|---|---|---|---:|---|---|---|
| NPC42783 | nan | green | 2.482 | none_detected | none_detected | baseline_irritation_IVRT_IVPT_panel |
| NPC323980 | nan | green | 2.089 | none_detected | none_detected | baseline_irritation_IVRT_IVPT_panel |
| NPC184593 | nan | green | 1.405 | none_detected | none_detected | baseline_irritation_IVRT_IVPT_panel |
| NPC249078 | nan | green | 2.725 | none_detected | none_detected | baseline_irritation_IVRT_IVPT_panel |
| NPC314289 | nan | green | 1.184 | none_detected | none_detected | baseline_irritation_IVRT_IVPT_panel |
| NPC302293 | nan | green | 1.695 | none_detected | none_detected | baseline_irritation_IVRT_IVPT_panel |
| NPC193781 | nan | green | 1.696 | none_detected | none_detected | baseline_irritation_IVRT_IVPT_panel |
| NPC325130 | nan | green | 1.184 | none_detected | none_detected | baseline_irritation_IVRT_IVPT_panel |
| NPC241081 | nan | green | 2.722 | none_detected | none_detected | baseline_irritation_IVRT_IVPT_panel |
| NPC195282 | nan | green | 2.725 | none_detected | none_detected | baseline_irritation_IVRT_IVPT_panel |
| NPC475968 | nan | green | 1.943 | none_detected | none_detected | baseline_irritation_IVRT_IVPT_panel |
| NPC77156 | nan | green | 1.071 | none_detected | none_detected | baseline_irritation_IVRT_IVPT_panel |
| NPC329253 | nan | green | 2.987 | none_detected | none_detected | baseline_irritation_IVRT_IVPT_panel |
| NPC59871 | nan | green | 2.708 | none_detected | none_detected | baseline_irritation_IVRT_IVPT_panel |
| NPC196715 | nan | green | 2.987 | none_detected | none_detected | baseline_irritation_IVRT_IVPT_panel |
| NPC107271 | nan | green | 1.958 | none_detected | none_detected | baseline_irritation_IVRT_IVPT_panel |
| NPC33067 | nan | green | 1.08 | none_detected | none_detected | baseline_irritation_IVRT_IVPT_panel |
| NPC261839 | nan | green | 2.281 | none_detected | none_detected | baseline_irritation_IVRT_IVPT_panel |
| NPC168128 | nan | green | 1.203 | none_detected | none_detected | baseline_irritation_IVRT_IVPT_panel |
| NPC254230 | nan | green | 1.201 | none_detected | none_detected | baseline_irritation_IVRT_IVPT_panel |
| NPC25947 | nan | green | 3.31 | none_detected | none_detected | baseline_irritation_IVRT_IVPT_panel |
| NPC329473 | nan | green | 2.345 | none_detected | none_detected | baseline_irritation_IVRT_IVPT_panel |
| NPC228980 | nan | green | 2.345 | none_detected | none_detected | baseline_irritation_IVRT_IVPT_panel |
| chromanol_arom9+arom10_Me+Me_tgfb1 | tgfb1 | green | 1.552 | none_detected | none_detected | baseline_irritation_IVRT_IVPT_panel |
| chromanol_arom6+arom9_Me+Me_tgfb1 | tgfb1 | green | 1.552 | none_detected | none_detected | baseline_irritation_IVRT_IVPT_panel |
| chromanol_arom9_Me_tgfb1 | tgfb1 | green | 1.244 | none_detected | none_detected | baseline_irritation_IVRT_IVPT_panel |
| chromanol_arom10_Me_tgfb1 | tgfb1 | green | 1.244 | none_detected | none_detected | baseline_irritation_IVRT_IVPT_panel |
| chromanol_arom6+arom10_Me+Me_tgfb1 | tgfb1 | green | 1.552 | none_detected | none_detected | baseline_irritation_IVRT_IVPT_panel |
| chromanol_arom9_F_tgfb1 | tgfb1 | green | 1.075 | none_detected | none_detected | baseline_irritation_IVRT_IVPT_panel |
| chromanol_arom6+arom9_F+Me_tgfb1 | tgfb1 | green | 1.383 | none_detected | none_detected | baseline_irritation_IVRT_IVPT_panel |
| chromanol_arom6+arom9_Me+F_tgfb1 | tgfb1 | green | 1.383 | none_detected | none_detected | baseline_irritation_IVRT_IVPT_panel |
| chromanol_arom9+arom10_F+Me_tgfb1 | tgfb1 | green | 1.383 | none_detected | none_detected | baseline_irritation_IVRT_IVPT_panel |
| chromanol_arom9+arom10_Me+F_tgfb1 | tgfb1 | green | 1.383 | none_detected | none_detected | baseline_irritation_IVRT_IVPT_panel |
| chromanol_arom6_Me_tgfb1 | tgfb1 | green | 1.244 | none_detected | none_detected | baseline_irritation_IVRT_IVPT_panel |
| chromanol_arom6+arom9_Me+OMe_tgfb1 | tgfb1 | green | 1.253 | none_detected | none_detected | baseline_irritation_IVRT_IVPT_panel |

## Curator Rule

- `green`: lead table 가능하지만 in-silico safety pre-gate로만 표현한다.
- `yellow`: photosafety/sensitization assay package를 논문 limitation과 CRO card에 붙인다.
- `red`: topical lead claim에서 제외한다.

```
### docs/QUINONE_SAFETY_GATE.md tail -120

```text
# Quinone Safety Gate

- timestamp: `2026-05-06T12:46:13+09:00`
- rows: `1006`
- gate_counts: `{'redesign_before_use': 0, 'quinone_reactivity_review': 133, 'redox_polyphenol_review': 872, 'reactivity_review': 1, 'quinone_reference_review': 0, 'structure_fix': 0}`
- EMB-3 included: `True`
- purpose: EMB-3/Embelin/quinone-like analogs를 일반 ADMET 점수와 분리해 redox cycling, Michael acceptor, metal chelation, skin sensitization, photosafety 리스크로 상시 제한한다.

## Gate Rule

- `quinone_reactivity_review`: GSH/NAC trapping, DPRA/KeratinoSens/h-CLAT, ROS/redox cycling, ICH S10 photostability, skin S9/metabolite screen 전까지 safety-positive 표현을 금지한다.
- `redox_polyphenol_review`: catechol/hydroquinone류 redox/skin-metabolism caveat로, quinone core는 아니지만 같은 wet-lab 패키지의 보조 우선순위로 둔다.
- `reactivity_review`: PAINS/Brenk reactive alert가 있어 lead claim 전에 원인별 보강을 요구한다.
- `redesign_before_use`: hard electrophile 또는 과도한 reactive alert가 있어 lead claim보다 구조 수정/대조군으로 둔다.
- EMB-3는 hERG/logP가 개선되어도 quinone/sensitization risk가 사라진 것이 아니므로 topical formulation/pulse-use 가설로만 쓴다.

## Top Quinone Safety Rows

| candidate | source | gate | cLogP | alerts | required package |
|---|---|---|---:|---|---|
| EMB-3 | explicit_embelin_scaffold_reference | quinone_reactivity_review | 2.363 | quinone_core;dihydroxy_quinone_like;hydroxy_carbonyl_metal_chelation_motif;michael_acceptor;PAINS_A:quinone_A(370);Brenk:Aliphatic_long_chain;Brenk:chinone_1;ZINC:Propenals | GSH/NAC trapping LC-MS; DPRA/KeratinoSens/h-CLAT; ROS/redox cycling; ICH S10 photostability; skin S9/metabolite screen |
| Embelin_parent | explicit_embelin_scaffold_reference | quinone_reactivity_review | 4.313 | quinone_core;dihydroxy_quinone_like;hydroxy_carbonyl_metal_chelation_motif;michael_acceptor;PAINS_A:quinone_A(370);Brenk:Aliphatic_long_chain;Brenk:chinone_1;NIH:gte_10_carbon_sb_chain | GSH/NAC trapping LC-MS; DPRA/KeratinoSens/h-CLAT; ROS/redox cycling; ICH S10 photostability; skin S9/metabolite screen |
| Lawsone_control | explicit_quinone_reference | quinone_reactivity_review | 1.508 | quinone_core;hydroxy_carbonyl_metal_chelation_motif;michael_acceptor;PAINS_A:quinone_A(370) | GSH/NAC trapping LC-MS; DPRA/KeratinoSens/h-CLAT; ROS/redox cycling; ICH S10 photostability; skin S9/metabolite screen |
| pains_full_audit_1029 | pains_full_audit | quinone_reactivity_review | 3.211 | quinone_core;hydroxy_carbonyl_metal_chelation_motif;michael_acceptor;PAINS_A:imine_one_A(321);Brenk:Aliphatic_long_chain;Brenk:beta-keto/anhydride;Brenk:diketo_group | GSH/NAC trapping LC-MS; DPRA/KeratinoSens/h-CLAT; ROS/redox cycling; ICH S10 photostability; skin S9/metabolite screen |
| pains_full_audit_1038 | pains_full_audit | quinone_reactivity_review | 3.018 | quinone_core;michael_acceptor;PAINS_A:imine_one_A(321);Brenk:Aliphatic_long_chain;Brenk:beta-keto/anhydride;Brenk:imine_1 | GSH/NAC trapping LC-MS; DPRA/KeratinoSens/h-CLAT; ROS/redox cycling; ICH S10 photostability; skin S9/metabolite screen |
| pains_full_audit_1049 | pains_full_audit | quinone_reactivity_review | 3.583 | quinone_core;michael_acceptor;PAINS_A:quinone_A(370);Brenk:chinone_1;ZINC:Propenals | GSH/NAC trapping LC-MS; DPRA/KeratinoSens/h-CLAT; ROS/redox cycling; ICH S10 photostability; skin S9/metabolite screen |
| pains_full_audit_1076 | pains_full_audit | quinone_reactivity_review | 0.972 | quinone_core;hydroxy_carbonyl_metal_chelation_motif;michael_acceptor;PAINS_A:imine_one_A(321);Brenk:Aliphatic_long_chain;Brenk:beta-keto/anhydride;Brenk:diketo_group | GSH/NAC trapping LC-MS; DPRA/KeratinoSens/h-CLAT; ROS/redox cycling; ICH S10 photostability; skin S9/metabolite screen |
| pains_full_audit_1083 | pains_full_audit | quinone_reactivity_review | 1.858 | quinone_core;dihydroxy_quinone_like;hydroxy_carbonyl_metal_chelation_motif;michael_acceptor;PAINS_A:quinone_A(370);Brenk:Aliphatic_long_chain;Brenk:chinone_1;ZINC:Propenals | GSH/NAC trapping LC-MS; DPRA/KeratinoSens/h-CLAT; ROS/redox cycling; ICH S10 photostability; skin S9/metabolite screen |
| pains_full_audit_1086 | pains_full_audit | quinone_reactivity_review | 3.973 | quinone_core;michael_acceptor;PAINS_A:quinone_A(370);Brenk:chinone_1;ZINC:Propenals | GSH/NAC trapping LC-MS; DPRA/KeratinoSens/h-CLAT; ROS/redox cycling; ICH S10 photostability; skin S9/metabolite screen |
| pains_full_audit_1116 | pains_full_audit | quinone_reactivity_review | 3.601 | quinone_core;hydroxy_carbonyl_metal_chelation_motif;michael_acceptor;PAINS_A:imine_one_A(321);Brenk:Aliphatic_long_chain;Brenk:beta-keto/anhydride;Brenk:diketo_group | GSH/NAC trapping LC-MS; DPRA/KeratinoSens/h-CLAT; ROS/redox cycling; ICH S10 photostability; skin S9/metabolite screen |
| pains_full_audit_1177 | pains_full_audit | quinone_reactivity_review | 1.959 | quinone_core;michael_acceptor;PAINS_A:imine_one_A(321);Brenk:Aliphatic_long_chain;Brenk:beta-keto/anhydride;Brenk:diketo_group | GSH/NAC trapping LC-MS; DPRA/KeratinoSens/h-CLAT; ROS/redox cycling; ICH S10 photostability; skin S9/metabolite screen |
| pains_full_audit_1179 | pains_full_audit | quinone_reactivity_review | 2.149 | quinone_core;dihydroxy_quinone_like;hydroxy_carbonyl_metal_chelation_motif;michael_acceptor;PAINS_A:quinone_A(370);PAINS_B:ene_one_hal(17);Brenk:chinone_1;ZINC:Propenals | GSH/NAC trapping LC-MS; DPRA/KeratinoSens/h-CLAT; ROS/redox cycling; ICH S10 photostability; skin S9/metabolite screen |
| pains_full_audit_1190 | pains_full_audit | quinone_reactivity_review | 1.989 | quinone_core;michael_acceptor;PAINS_A:quinone_A(370);Brenk:chinone_1;ZINC:Propenals | GSH/NAC trapping LC-MS; DPRA/KeratinoSens/h-CLAT; ROS/redox cycling; ICH S10 photostability; skin S9/metabolite screen |
| pains_full_audit_1191 | pains_full_audit | quinone_reactivity_review | 0.851 | quinone_core;dihydroxy_quinone_like;hydroxy_carbonyl_metal_chelation_motif;michael_acceptor;PAINS_A:imine_one_A(321);Brenk:Aliphatic_long_chain;Brenk:beta-keto/anhydride;Brenk:diketo_group | GSH/NAC trapping LC-MS; DPRA/KeratinoSens/h-CLAT; ROS/redox cycling; ICH S10 photostability; skin S9/metabolite screen |
| pains_full_audit_1193 | pains_full_audit | quinone_reactivity_review | 3.058 | quinone_core;hydroxy_carbonyl_metal_chelation_motif;michael_acceptor;PAINS_A:imine_one_A(321);Brenk:Aliphatic_long_chain;Brenk:beta-keto/anhydride;Brenk:diketo_group | GSH/NAC trapping LC-MS; DPRA/KeratinoSens/h-CLAT; ROS/redox cycling; ICH S10 photostability; skin S9/metabolite screen |
| pains_full_audit_1218 | pains_full_audit | quinone_reactivity_review | 4.456 | quinone_core;michael_acceptor;PAINS_A:quinone_A(370);Brenk:chinone_1;ZINC:Propenals | GSH/NAC trapping LC-MS; DPRA/KeratinoSens/h-CLAT; ROS/redox cycling; ICH S10 photostability; skin S9/metabolite screen |
| pains_full_audit_1223 | pains_full_audit | quinone_reactivity_review | 1.806 | quinone_core;hydroxy_carbonyl_metal_chelation_motif;michael_acceptor;PAINS_A:quinone_A(370);Brenk:Aliphatic_long_chain;Brenk:chinone_1;ZINC:Propenals | GSH/NAC trapping LC-MS; DPRA/KeratinoSens/h-CLAT; ROS/redox cycling; ICH S10 photostability; skin S9/metabolite screen |
| pains_full_audit_1263 | pains_full_audit | quinone_reactivity_review | 0.935 | quinone_core;hydroxy_carbonyl_metal_chelation_motif;michael_acceptor;PAINS_A:imine_one_A(321);Brenk:Aliphatic_long_chain;Brenk:beta-keto/anhydride;Brenk:diketo_group | GSH/NAC trapping LC-MS; DPRA/KeratinoSens/h-CLAT; ROS/redox cycling; ICH S10 photostability; skin S9/metabolite screen |
| pains_full_audit_1277 | pains_full_audit | quinone_reactivity_review | 3.043 | quinone_core;hydroxy_carbonyl_metal_chelation_motif;michael_acceptor;PAINS_A:quinone_A(370);PAINS_B:ene_one_hal(17);Brenk:Aliphatic_long_chain;Brenk:chinone_1 | GSH/NAC trapping LC-MS; DPRA/KeratinoSens/h-CLAT; ROS/redox cycling; ICH S10 photostability; skin S9/metabolite screen |
| pains_full_audit_1349 | pains_full_audit | quinone_reactivity_review | 1.828 | quinone_core;hydroxy_carbonyl_metal_chelation_motif;michael_acceptor;PAINS_A:imine_one_A(321);Brenk:Aliphatic_long_chain;Brenk:beta-keto/anhydride;Brenk:diketo_group | GSH/NAC trapping LC-MS; DPRA/KeratinoSens/h-CLAT; ROS/redox cycling; ICH S10 photostability; skin S9/metabolite screen |
| pains_full_audit_1376 | pains_full_audit | quinone_reactivity_review | 3.168 | quinone_core;hydroxy_carbonyl_metal_chelation_motif;michael_acceptor;PAINS_A:quinone_A(370);Brenk:chinone_1;ZINC:Propenals | GSH/NAC trapping LC-MS; DPRA/KeratinoSens/h-CLAT; ROS/redox cycling; ICH S10 photostability; skin S9/metabolite screen |
| pains_full_audit_1411 | pains_full_audit | quinone_reactivity_review | 0.819 | quinone_core;dihydroxy_quinone_like;hydroxy_carbonyl_metal_chelation_motif;michael_acceptor;PAINS_A:quinone_A(370);Brenk:chinone_1;ZINC:Propenals | GSH/NAC trapping LC-MS; DPRA/KeratinoSens/h-CLAT; ROS/redox cycling; ICH S10 photostability; skin S9/metabolite screen |
| pains_full_audit_1437 | pains_full_audit | quinone_reactivity_review | 2.134 | quinone_core;michael_acceptor;PAINS_A:imine_one_A(321);Brenk:Aliphatic_long_chain;Brenk:beta-keto/anhydride;Brenk:diketo_group | GSH/NAC trapping LC-MS; DPRA/KeratinoSens/h-CLAT; ROS/redox cycling; ICH S10 photostability; skin S9/metabolite screen |
| pains_full_audit_1483 | pains_full_audit | quinone_reactivity_review | 2.379 | quinone_core;michael_acceptor;PAINS_A:quinone_A(370);Brenk:chinone_1;ZINC:Propenals | GSH/NAC trapping LC-MS; DPRA/KeratinoSens/h-CLAT; ROS/redox cycling; ICH S10 photostability; skin S9/metabolite screen |
| pains_full_audit_1533 | pains_full_audit | quinone_reactivity_review | 0.545 | quinone_core;hydroxy_carbonyl_metal_chelation_motif;michael_acceptor;PAINS_A:imine_one_A(321);Brenk:Aliphatic_long_chain;Brenk:beta-keto/anhydride;Brenk:diketo_group | GSH/NAC trapping LC-MS; DPRA/KeratinoSens/h-CLAT; ROS/redox cycling; ICH S10 photostability; skin S9/metabolite screen |
| pains_full_audit_1537 | pains_full_audit | quinone_reactivity_review | 0.166 | quinone_core;hydroxy_carbonyl_metal_chelation_motif;michael_acceptor;PAINS_A:imine_one_A(321);Brenk:Aliphatic_long_chain;Brenk:beta-keto/anhydride;Brenk:diketo_group | GSH/NAC trapping LC-MS; DPRA/KeratinoSens/h-CLAT; ROS/redox cycling; ICH S10 photostability; skin S9/metabolite screen |
| pains_full_audit_1544 | pains_full_audit | quinone_reactivity_review | 1.527 | quinone_core;michael_acceptor;PAINS_A:imine_one_A(321);Brenk:Aliphatic_long_chain;Brenk:beta-keto/anhydride;Brenk:diketo_group | GSH/NAC trapping LC-MS; DPRA/KeratinoSens/h-CLAT; ROS/redox cycling; ICH S10 photostability; skin S9/metabolite screen |
| pains_full_audit_1569 | pains_full_audit | quinone_reactivity_review | 2.379 | quinone_core;michael_acceptor;PAINS_A:quinone_A(370);Brenk:Aliphatic_long_chain;Brenk:chinone_1;ZINC:Propenals | GSH/NAC trapping LC-MS; DPRA/KeratinoSens/h-CLAT; ROS/redox cycling; ICH S10 photostability; skin S9/metabolite screen |
| pains_full_audit_1582 | pains_full_audit | quinone_reactivity_review | 1.763 | quinone_core;hydroxy_carbonyl_metal_chelation_motif;michael_acceptor;PAINS_A:quinone_A(370);Brenk:Aliphatic_long_chain;Brenk:chinone_1;ZINC:Propenals | GSH/NAC trapping LC-MS; DPRA/KeratinoSens/h-CLAT; ROS/redox cycling; ICH S10 photostability; skin S9/metabolite screen |
| pains_full_audit_1590 | pains_full_audit | quinone_reactivity_review | 2.864 | michael_acceptor;PAINS_A:quinone_A(370);Brenk:Aliphatic_long_chain;Brenk:chinone_1;Brenk:imine_1 | GSH/NAC trapping LC-MS; DPRA/KeratinoSens/h-CLAT; ROS/redox cycling; ICH S10 photostability; skin S9/metabolite screen |
| pains_full_audit_1610 | pains_full_audit | quinone_reactivity_review | 1.88 | quinone_core;dihydroxy_quinone_like;hydroxy_carbonyl_metal_chelation_motif;michael_acceptor;PAINS_A:quinone_A(370);PAINS_B:ene_one_hal(17);Brenk:chinone_1;ZINC:Propenals | GSH/NAC trapping LC-MS; DPRA/KeratinoSens/h-CLAT; ROS/redox cycling; ICH S10 photostability; skin S9/metabolite screen |
| pains_full_audit_1614 | pains_full_audit | quinone_reactivity_review | 1.917 | quinone_core;michael_acceptor;PAINS_A:imine_one_A(321);Brenk:Aliphatic_long_chain;Brenk:beta-keto/anhydride;Brenk:diketo_group | GSH/NAC trapping LC-MS; DPRA/KeratinoSens/h-CLAT; ROS/redox cycling; ICH S10 photostability; skin S9/metabolite screen |
| pains_full_audit_1638 | pains_full_audit | quinone_reactivity_review | 3.173 | quinone_core;michael_acceptor;PAINS_A:imine_one_A(321);Brenk:Aliphatic_long_chain;Brenk:beta-keto/anhydride;Brenk:diketo_group | GSH/NAC trapping LC-MS; DPRA/KeratinoSens/h-CLAT; ROS/redox cycling; ICH S10 photostability; skin S9/metabolite screen |
| pains_full_audit_1643 | pains_full_audit | quinone_reactivity_review | 0.782 | quinone_core;dihydroxy_quinone_like;hydroxy_carbonyl_metal_chelation_motif;michael_acceptor;PAINS_A:quinone_A(370);Brenk:chinone_1;ZINC:Propenals | GSH/NAC trapping LC-MS; DPRA/KeratinoSens/h-CLAT; ROS/redox cycling; ICH S10 photostability; skin S9/metabolite screen |
| pains_full_audit_165 | pains_full_audit | quinone_reactivity_review | 1.362 | quinone_core;hydroxy_carbonyl_metal_chelation_motif;michael_acceptor;PAINS_A:imine_one_A(321);Brenk:Aliphatic_long_chain;Brenk:beta-keto/anhydride;Brenk:diketo_group | GSH/NAC trapping LC-MS; DPRA/KeratinoSens/h-CLAT; ROS/redox cycling; ICH S10 photostability; skin S9/metabolite screen |
| pains_full_audit_1655 | pains_full_audit | quinone_reactivity_review | 0.782 | quinone_core;dihydroxy_quinone_like;hydroxy_carbonyl_metal_chelation_motif;michael_acceptor;PAINS_A:quinone_A(370);Brenk:Aliphatic_long_chain;Brenk:chinone_1;ZINC:Propenals | GSH/NAC trapping LC-MS; DPRA/KeratinoSens/h-CLAT; ROS/redox cycling; ICH S10 photostability; skin S9/metabolite screen |
| pains_full_audit_1656 | pains_full_audit | quinone_reactivity_review | 0.859 | quinone_core;michael_acceptor;PAINS_A:quinone_A(370);Brenk:chinone_1;ZINC:Propenals | GSH/NAC trapping LC-MS; DPRA/KeratinoSens/h-CLAT; ROS/redox cycling; ICH S10 photostability; skin S9/metabolite screen |
| pains_full_audit_1657 | pains_full_audit | quinone_reactivity_review | 0.171 | quinone_core;dihydroxy_quinone_like;hydroxy_carbonyl_metal_chelation_motif;michael_acceptor;PAINS_A:imine_one_A(321);Brenk:Aliphatic_long_chain;Brenk:beta-keto/anhydride;Brenk:diketo_group | GSH/NAC trapping LC-MS; DPRA/KeratinoSens/h-CLAT; ROS/redox cycling; ICH S10 photostability; skin S9/metabolite screen |
| pains_full_audit_169 | pains_full_audit | quinone_reactivity_review | 2.778 | quinone_core;hydroxy_carbonyl_metal_chelation_motif;michael_acceptor;PAINS_A:quinone_A(370);Brenk:chinone_1;ZINC:Propenals | GSH/NAC trapping LC-MS; DPRA/KeratinoSens/h-CLAT; ROS/redox cycling; ICH S10 photostability; skin S9/metabolite screen |
| pains_full_audit_1732 | pains_full_audit | quinone_reactivity_review | 3.563 | quinone_core;michael_acceptor;PAINS_A:imine_one_A(321);Brenk:Aliphatic_long_chain;Brenk:beta-keto/anhydride;Brenk:diketo_group | GSH/NAC trapping LC-MS; DPRA/KeratinoSens/h-CLAT; ROS/redox cycling; ICH S10 photostability; skin S9/metabolite screen |

## Manuscript Claim Discipline

- EMB-3/quinone 계열은 `topical-friendly ADMET window`와 `quinone reactivity risk`를 동시에 표기한다.
- `컴퓨터상 safety가 깨끗하다` 또는 `완전 안전하다`는 표현은 금지한다.
- 적합한 표현: `in-silico topical property improved, but quinone reactivity/sensitization remains a required wet-lab gate`.

```
### docs/DMTL_EXPERIMENT_CARD_FACTORY.md tail -120

```text
# DMTL Experiment Card Factory

- timestamp: `2026-05-06T12:46:28+09:00`
- rows: `16`
- bucket_counts: `{'single_point_wetlab_card': 10, 'route_or_safety_prerequisite': 2, 'compute_followup_card': 4}`
- purpose: 계산 결과를 바로 CRO/wet-lab이 읽을 수 있는 design-make-test-learn card로 변환한다.

## Cards

| card | candidate | target | priority | bucket | path |
|---|---|---|---:|---|---|
| DMTL_002 | R15_chromanol_Me6_Me9 | tgfb1 | 0.8164 | single_point_wetlab_card | docs/experiment_cards/R15_chromanol_Me6_Me9__tgfb1.md |
| DMTL_001 | R15_chromanol_Cl_pos9 | tgfb1 | 0.8122 | single_point_wetlab_card | docs/experiment_cards/R15_chromanol_Cl_pos9__tgfb1.md |
| DMTL_003 | R15_chromanol_Me6_Me10 | tgfb1 | 0.7957 | single_point_wetlab_card | docs/experiment_cards/R15_chromanol_Me6_Me10__tgfb1.md |
| DMTL_004 | R15_chromanol_Me9_Me10 | tgfb1 | 0.7954 | single_point_wetlab_card | docs/experiment_cards/R15_chromanol_Me9_Me10__tgfb1.md |
| DMTL_005 | R15_chromanol_Cl_pos6 | tgfb1 | 0.7417 | single_point_wetlab_card | docs/experiment_cards/R15_chromanol_Cl_pos6__tgfb1.md |
| DMTL_007 | R15_chromanol_Cl_pos9 | dct | 0.7265 | single_point_wetlab_card | docs/experiment_cards/R15_chromanol_Cl_pos9__dct.md |
| DMTL_006 | R15_chromanol_Cl_pos10 | tgfb1 | 0.7168 | single_point_wetlab_card | docs/experiment_cards/R15_chromanol_Cl_pos10__tgfb1.md |
| DMTL_008 | R15_chromanol_Cl_pos6 | dct | 0.716 | single_point_wetlab_card | docs/experiment_cards/R15_chromanol_Cl_pos6__dct.md |
| DMTL_009 | R15_chromanol_Cl_pos6 | tyr | 0.705 | single_point_wetlab_card | docs/experiment_cards/R15_chromanol_Cl_pos6__tyr.md |
| DMTL_013 | R15_chromanol_Cl_pos9 | tyr | 0.6735 | route_or_safety_prerequisite | docs/experiment_cards/R15_chromanol_Cl_pos9__tyr.md |
| DMTL_014 | R15_chromanol_Cl_pos10 | tyr | 0.66 | route_or_safety_prerequisite | docs/experiment_cards/R15_chromanol_Cl_pos10__tyr.md |
| DMTL_015 | R15_chromanol_Me9_Me10 | tyr | 0.6596 | compute_followup_card | docs/experiment_cards/R15_chromanol_Me9_Me10__tyr.md |
| DMTL_016 | R15_chromanol_Me6_Me9 | tyr | 0.6522 | compute_followup_card | docs/experiment_cards/R15_chromanol_Me6_Me9__tyr.md |
| DMTL_017 | R15_chromanol_Me6_Me9 | dct | 0.6508 | compute_followup_card | docs/experiment_cards/R15_chromanol_Me6_Me9__dct.md |
| DMTL_018 | R15_chromanol_Me9_Me10 | dct | 0.6497 | compute_followup_card | docs/experiment_cards/R15_chromanol_Me9_Me10__dct.md |
| DMTL_010 | R15_chromanol | tgfb1 | 0.6439 | single_point_wetlab_card | docs/experiment_cards/R15_chromanol__tgfb1.md |

## Curator Rule

- `single_point_wetlab_card`: 추가 GPU보다 assay ordering/quote 준비가 우선이다.
- `route_or_safety_prerequisite`: route/safety gate를 먼저 해결한다.
- `compute_followup_card`: GPU/CPU가 비면 cofold/MD/free-energy follow-up 후보로 둔다.

```
### docs/SKIN_SPATIAL_ATLAS_GATE.md tail -120

```text
# Skin Spatial Atlas Gate

- timestamp: `2026-05-06T12:46:28+09:00`
- rows: `32`
- gate_counts: `{'spatially_anchorable': 2, 'atlas_review': 9, 'spatial_context_missing': 21}`
- purpose: 피부 target claim을 세포 상태뿐 아니라 anatomic site, niche, reconstructed model로 연결한다.

## Spatial Anchors

| target | gate | disease | niche | cells | assay model | next |
|---|---|---|---|---|---|---|
| dct | spatially_anchorable | pigment | melanocyte_unit;hair_follicle_pigment_unit | melanocyte;melanosome_state | melanocyte melanin and DCT/TYR/TYRP1 panel | use site/cell/niche table in target-focused manuscript and CRO card |
| tyr | spatially_anchorable | pigment | melanocyte_unit;hair_follicle_pigment_unit | melanocyte;melanosome_state | tyrosinase activity and melanin content | use site/cell/niche table in target-focused manuscript and CRO card |
| ar | atlas_review | alopecia;acne | hair_follicle;sebaceous_gland | dermal_papilla_cell;sebocyte | androgen reporter in DPC/sebocyte context | add human skin atlas or disease-site literature before strong target claim |
| ctgf | atlas_review | scar | reticular_dermis;wound_edge | activated_fibroblast | scar fibroblast or collagen gel contraction | add human skin atlas or disease-site literature before strong target claim |
| lox | atlas_review | scar;photoaging | reticular_dermis;ECM_stroma | dermal_fibroblast | matrix stiffness/collagen crosslinking assay | add human skin atlas or disease-site literature before strong target claim |
| mc1r | atlas_review | pigment | melanocyte_unit | melanocyte | cAMP/pigment response assay | add human skin atlas or disease-site literature before strong target claim |
| mmp1 | atlas_review | photoaging;scar | papillary_dermis;photoexposed_skin | photoaged_fibroblast | UV-aged fibroblast or dermal equivalent | add human skin atlas or disease-site literature before strong target claim |
| nr3c1 | atlas_review | acne;photoaging | epidermis;immune_niche | keratinocyte;immune_cell | glucocorticoid response and barrier marker panel | add human skin atlas or disease-site literature before strong target claim |
| ptgs2 | atlas_review | acne;photoaging | epidermis;sebaceous_unit;immune_niche | keratinocyte;sebocyte;immune_cell | PGE2/cytokine panel | add human skin atlas or disease-site literature before strong target claim |
| tgfb1 | atlas_review | scar;photoaging | reticular_dermis;perivascular_stroma | activated_fibroblast;myofibroblast | scar biopsy or fibroblast-rich reconstructed skin | add human skin atlas or disease-site literature before strong target claim |
| tyrp1 | atlas_review | pigment | melanocyte_unit;hair_follicle_pigment_unit | melanocyte;melanosome_state | melanosome maturation panel | add human skin atlas or disease-site literature before strong target claim |
| col1a1 | spatial_context_missing | unknown | atlas_context_missing | skin_cell_context_missing | define anatomic site and disease-cell model | keep exploratory until target is mapped to skin anatomic niche |
| ctnnb1 | spatial_context_missing | unknown | atlas_context_missing | skin_cell_context_missing | define anatomic site and disease-cell model | keep exploratory until target is mapped to skin anatomic niche |
| f2rl1 | spatial_context_missing | unknown | atlas_context_missing | skin_cell_context_missing | define anatomic site and disease-cell model | keep exploratory until target is mapped to skin anatomic niche |
| fgf2 | spatial_context_missing | unknown | atlas_context_missing | skin_cell_context_missing | define anatomic site and disease-cell model | keep exploratory until target is mapped to skin anatomic niche |
| jun | spatial_context_missing | unknown | atlas_context_missing | skin_cell_context_missing | define anatomic site and disease-cell model | keep exploratory until target is mapped to skin anatomic niche |
| mitf | spatial_context_missing | unknown | atlas_context_missing | skin_cell_context_missing | define anatomic site and disease-cell model | keep exploratory until target is mapped to skin anatomic niche |
| mmp3 | spatial_context_missing | unknown | atlas_context_missing | skin_cell_context_missing | define anatomic site and disease-cell model | keep exploratory until target is mapped to skin anatomic niche |
| mmp9 | spatial_context_missing | unknown | atlas_context_missing | skin_cell_context_missing | define anatomic site and disease-cell model | keep exploratory until target is mapped to skin anatomic niche |
| mylk | spatial_context_missing | unknown | atlas_context_missing | skin_cell_context_missing | define anatomic site and disease-cell model | keep exploratory until target is mapped to skin anatomic niche |
| nlrp3 | spatial_context_missing | unknown | atlas_context_missing | skin_cell_context_missing | define anatomic site and disease-cell model | keep exploratory until target is mapped to skin anatomic niche |
| piezo1 | spatial_context_missing | unknown | atlas_context_missing | skin_cell_context_missing | define anatomic site and disease-cell model | keep exploratory until target is mapped to skin anatomic niche |
| ptgdr2 | spatial_context_missing | unknown | atlas_context_missing | skin_cell_context_missing | define anatomic site and disease-cell model | keep exploratory until target is mapped to skin anatomic niche |
| rarg | spatial_context_missing | unknown | atlas_context_missing | skin_cell_context_missing | define anatomic site and disease-cell model | keep exploratory until target is mapped to skin anatomic niche |
| sirt1 | spatial_context_missing | unknown | atlas_context_missing | skin_cell_context_missing | define anatomic site and disease-cell model | keep exploratory until target is mapped to skin anatomic niche |
| srd5a1 | spatial_context_missing | unknown | atlas_context_missing | skin_cell_context_missing | define anatomic site and disease-cell model | keep exploratory until target is mapped to skin anatomic niche |
| srd5a2 | spatial_context_missing | unknown | atlas_context_missing | skin_cell_context_missing | define anatomic site and disease-cell model | keep exploratory until target is mapped to skin anatomic niche |
| srebf1 | spatial_context_missing | unknown | atlas_context_missing | skin_cell_context_missing | define anatomic site and disease-cell model | keep exploratory until target is mapped to skin anatomic niche |
| srebp1 | spatial_context_missing | unknown | atlas_context_missing | skin_cell_context_missing | define anatomic site and disease-cell model | keep exploratory until target is mapped to skin anatomic niche |
| tlr2 | spatial_context_missing | unknown | atlas_context_missing | skin_cell_context_missing | define anatomic site and disease-cell model | keep exploratory until target is mapped to skin anatomic niche |
| vegfa | spatial_context_missing | unknown | atlas_context_missing | skin_cell_context_missing | define anatomic site and disease-cell model | keep exploratory until target is mapped to skin anatomic niche |
| wnt10b | spatial_context_missing | unknown | atlas_context_missing | skin_cell_context_missing | define anatomic site and disease-cell model | keep exploratory until target is mapped to skin anatomic niche |

## Curator Rule

- `spatially_anchorable`: target-focused paper에 skin site/cell/niche figure 또는 table을 넣는다.
- `atlas_review`: 추가 docking보다 atlas/literature anchor 보강이 우선이다.
- `spatial_context_missing`: direct dermatology target claim을 제한한다.

```
### docs/TARGET_ENGAGEMENT_ASSAY_GATE.md tail -120

```text
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

```
### docs/DERMAL_PBPK_IVPT_GATE.md tail -120

```text
# Dermal PBPK IVPT Gate

- timestamp: `2026-05-06T12:46:29+09:00`
- rows: `1082`
- gate_counts: `{'ivpt_pbpk_ready': 477, 'formulation_rescue_needed': 587, 'pbpk_low_confidence': 18, 'structure_fix': 0}`
- purpose: topical lead를 FDA/EMA IVRT/IVPT 및 mechanistic dermal PBPK 입력 표로 연결한다.

## IVPT/PBPK Rows

| candidate | target | gate | logKp | objective | receptor | next |
|---|---|---|---:|---|---|---|
| R15_chromanol_Me6_Me9 | tgfb1 | ivpt_pbpk_ready | -2.888 | skin_retention_favored | standard_buffer_candidate | build finite-dose IVRT/IVPT table and PBPK parameter sheet |
| R15_chromanol_Me6_Me10 | tgfb1 | ivpt_pbpk_ready | -2.888 | skin_retention_favored | standard_buffer_candidate | build finite-dose IVRT/IVPT table and PBPK parameter sheet |
| R15_chromanol_Me9_Me10 | tgfb1 | ivpt_pbpk_ready | -2.888 | skin_retention_favored | standard_buffer_candidate | build finite-dose IVRT/IVPT table and PBPK parameter sheet |
| R15_chromanol_Me9_Me10 | tyr | ivpt_pbpk_ready | -2.888 | skin_retention_favored | standard_buffer_candidate | build finite-dose IVRT/IVPT table and PBPK parameter sheet |
| R15_chromanol_Me6_Me9 | tyr | ivpt_pbpk_ready | -2.888 | skin_retention_favored | standard_buffer_candidate | build finite-dose IVRT/IVPT table and PBPK parameter sheet |
| R15_chromanol_Me6_Me9 | dct | ivpt_pbpk_ready | -2.888 | skin_retention_favored | standard_buffer_candidate | build finite-dose IVRT/IVPT table and PBPK parameter sheet |
| R15_chromanol_Me9_Me10 | dct | ivpt_pbpk_ready | -2.888 | skin_retention_favored | standard_buffer_candidate | build finite-dose IVRT/IVPT table and PBPK parameter sheet |
| R15_chromanol_Me6_Me10 | tyr | ivpt_pbpk_ready | -2.888 | skin_retention_favored | standard_buffer_candidate | build finite-dose IVRT/IVPT table and PBPK parameter sheet |
| R15_chromanol_Me6_Me10 | dct | ivpt_pbpk_ready | -2.888 | skin_retention_favored | standard_buffer_candidate | build finite-dose IVRT/IVPT table and PBPK parameter sheet |
| NPC323980 |  | ivpt_pbpk_ready | -2.3 | permeation_or_delivery_review | standard_buffer_candidate | build finite-dose IVRT/IVPT table and PBPK parameter sheet |
| NPC77156 |  | ivpt_pbpk_ready | -2.998 | skin_retention_favored | standard_buffer_candidate | build finite-dose IVRT/IVPT table and PBPK parameter sheet |
| NPC475968 |  | ivpt_pbpk_ready | -2.904 | skin_retention_favored | standard_buffer_candidate | build finite-dose IVRT/IVPT table and PBPK parameter sheet |
| NPC329253 |  | ivpt_pbpk_ready | -2.053 | permeation_or_delivery_review | standard_buffer_candidate | build finite-dose IVRT/IVPT table and PBPK parameter sheet |
| NPC196715 |  | ivpt_pbpk_ready | -2.053 | permeation_or_delivery_review | standard_buffer_candidate | build finite-dose IVRT/IVPT table and PBPK parameter sheet |
| NPC261839 |  | ivpt_pbpk_ready | -2.835 | skin_retention_favored | standard_buffer_candidate | build finite-dose IVRT/IVPT table and PBPK parameter sheet |
| NPC168128 |  | ivpt_pbpk_ready | -2.984 | skin_retention_favored | standard_buffer_candidate | build finite-dose IVRT/IVPT table and PBPK parameter sheet |
| NPC329473 |  | ivpt_pbpk_ready | -2.485 | permeation_or_delivery_review | standard_buffer_candidate | build finite-dose IVRT/IVPT table and PBPK parameter sheet |
| NPC228980 |  | ivpt_pbpk_ready | -2.485 | permeation_or_delivery_review | standard_buffer_candidate | build finite-dose IVRT/IVPT table and PBPK parameter sheet |
| NPC249078 |  | ivpt_pbpk_ready | -2.24 | permeation_or_delivery_review | standard_buffer_candidate | build finite-dose IVRT/IVPT table and PBPK parameter sheet |
| NPC302293 |  | ivpt_pbpk_ready | -2.995 | skin_retention_favored | standard_buffer_candidate | build finite-dose IVRT/IVPT table and PBPK parameter sheet |
| NPC195282 |  | ivpt_pbpk_ready | -2.24 | permeation_or_delivery_review | standard_buffer_candidate | build finite-dose IVRT/IVPT table and PBPK parameter sheet |
| NPC254230 |  | ivpt_pbpk_ready | -2.985 | skin_retention_favored | standard_buffer_candidate | build finite-dose IVRT/IVPT table and PBPK parameter sheet |
| NPC42783 |  | ivpt_pbpk_ready | -2.107 | permeation_or_delivery_review | standard_buffer_candidate | build finite-dose IVRT/IVPT table and PBPK parameter sheet |
| NPC193781 |  | ivpt_pbpk_ready | -3.068 | skin_retention_favored | standard_buffer_candidate | build finite-dose IVRT/IVPT table and PBPK parameter sheet |
| NPC107271 |  | ivpt_pbpk_ready | -2.882 | skin_retention_favored | standard_buffer_candidate | build finite-dose IVRT/IVPT table and PBPK parameter sheet |
| NPC241081 |  | ivpt_pbpk_ready | -2.669 | skin_retention_favored | standard_buffer_candidate | build finite-dose IVRT/IVPT table and PBPK parameter sheet |
| NPC59871 |  | ivpt_pbpk_ready | -3.632 | skin_retention_favored | standard_buffer_candidate | build finite-dose IVRT/IVPT table and PBPK parameter sheet |
| NPC25947 |  | ivpt_pbpk_ready | -3.101 | skin_retention_favored | aqueous_with_solubilizer_review | build finite-dose IVRT/IVPT table and PBPK parameter sheet |
| R15_chromanol_Cl_pos9 | tgfb1 | ivpt_pbpk_ready | -2.901 | skin_retention_favored | standard_buffer_candidate | build finite-dose IVRT/IVPT table and PBPK parameter sheet |
| R15_chromanol_Cl_pos6 | tgfb1 | ivpt_pbpk_ready | -2.901 | skin_retention_favored | standard_buffer_candidate | build finite-dose IVRT/IVPT table and PBPK parameter sheet |
| R15_chromanol_Cl_pos10 | tgfb1 | ivpt_pbpk_ready | -2.901 | skin_retention_favored | standard_buffer_candidate | build finite-dose IVRT/IVPT table and PBPK parameter sheet |
| R15_chromanol_Cl_pos9 | dct | ivpt_pbpk_ready | -2.901 | skin_retention_favored | standard_buffer_candidate | build finite-dose IVRT/IVPT table and PBPK parameter sheet |
| R15_chromanol_Cl_pos6 | dct | ivpt_pbpk_ready | -2.901 | skin_retention_favored | standard_buffer_candidate | build finite-dose IVRT/IVPT table and PBPK parameter sheet |
| R15_chromanol_Cl_pos6 | tyr | ivpt_pbpk_ready | -2.901 | skin_retention_favored | standard_buffer_candidate | build finite-dose IVRT/IVPT table and PBPK parameter sheet |
| R15_chromanol_Cl_pos10 | dct | ivpt_pbpk_ready | -2.901 | skin_retention_favored | standard_buffer_candidate | build finite-dose IVRT/IVPT table and PBPK parameter sheet |
| R15_chromanol_Cl_pos9 | tyr | ivpt_pbpk_ready | -2.901 | skin_retention_favored | standard_buffer_candidate | build finite-dose IVRT/IVPT table and PBPK parameter sheet |
| R15_chromanol_Cl_pos10 | tyr | ivpt_pbpk_ready | -2.901 | skin_retention_favored | standard_buffer_candidate | build finite-dose IVRT/IVPT table and PBPK parameter sheet |
| NPC179262 |  | ivpt_pbpk_ready | -3.1 | skin_retention_favored | aqueous_with_solubilizer_review | build finite-dose IVRT/IVPT table and PBPK parameter sheet |
| NPC192944 |  | ivpt_pbpk_ready | -4.134 | skin_retention_favored | standard_buffer_candidate | build finite-dose IVRT/IVPT table and PBPK parameter sheet |
| chromanol_arom9+arom10_Me+Me_tgfb1 | tgfb1 | ivpt_pbpk_ready | -2.888 | skin_retention_favored | standard_buffer_candidate | build finite-dose IVRT/IVPT table and PBPK parameter sheet |
| chromanol_arom6+arom9_Me+Me_tgfb1 | tgfb1 | ivpt_pbpk_ready | -2.888 | skin_retention_favored | standard_buffer_candidate | build finite-dose IVRT/IVPT table and PBPK parameter sheet |
| chromanol_arom9_Me_tgfb1 | tgfb1 | ivpt_pbpk_ready | -3.022 | skin_retention_favored | standard_buffer_candidate | build finite-dose IVRT/IVPT table and PBPK parameter sheet |
| chromanol_arom10_Me_tgfb1 | tgfb1 | ivpt_pbpk_ready | -3.022 | skin_retention_favored | standard_buffer_candidate | build finite-dose IVRT/IVPT table and PBPK parameter sheet |
| chromanol_arom6+arom10_Me+Me_tgfb1 | tgfb1 | ivpt_pbpk_ready | -2.888 | skin_retention_favored | standard_buffer_candidate | build finite-dose IVRT/IVPT table and PBPK parameter sheet |
| chromanol_arom9_F_tgfb1 | tgfb1 | ivpt_pbpk_ready | -3.166 | skin_retention_favored | standard_buffer_candidate | build finite-dose IVRT/IVPT table and PBPK parameter sheet |

## Curator Rule

- `ivpt_pbpk_ready`: P29/P32 및 CRO RFQ에 finite-dose IVRT/IVPT parameter table을 추가한다.
- `formulation_rescue_needed`: 계산 확장보다 vehicle/formulation BO를 우선한다.
- `pbpk_low_confidence`: topical exposure claim을 제한한다.

```
### docs/METABOLITE_REACTIVE_RISK_GATE.md tail -120

```text
# Metabolite Reactive Risk Gate

- timestamp: `2026-05-06T12:46:29+09:00`
- rows: `1082`
- gate_counts: `{'low_reactive_alert': 720, 'metabolism_caveat': 352, 'reactive_metabolite_review': 10, 'structure_fix': 0}`
- purpose: BioTransformer/FAME류 대사체 예측 전 단계로 phenol/redox/quinone/aryl-halogen/reactive-metabolite risk를 표시한다.

## Metabolism Risk Rows

| candidate | target | gate | alerts | metabolism | next |
|---|---|---|---|---|---|
| NPC42783 | nan | low_reactive_alert | none_detected | standard phase I/II screen | standard metabolite prediction before wet-lab package |
| NPC213764 | nan | low_reactive_alert | none_detected | standard phase I/II screen | standard metabolite prediction before wet-lab package |
| NPC236761 | nan | low_reactive_alert | none_detected | standard phase I/II screen | standard metabolite prediction before wet-lab package |
| NPC88887 | nan | low_reactive_alert | none_detected | standard phase I/II screen | standard metabolite prediction before wet-lab package |
| NPC149567 | nan | low_reactive_alert | none_detected | standard phase I/II screen | standard metabolite prediction before wet-lab package |
| NPC323980 | nan | low_reactive_alert | none_detected | standard phase I/II screen | standard metabolite prediction before wet-lab package |
| NPC283633 | nan | low_reactive_alert | none_detected | standard phase I/II screen | standard metabolite prediction before wet-lab package |
| NPC184593 | nan | low_reactive_alert | none_detected | standard phase I/II screen | standard metabolite prediction before wet-lab package |
| NPC249078 | nan | low_reactive_alert | none_detected | standard phase I/II screen | standard metabolite prediction before wet-lab package |
| NPC306277 | nan | low_reactive_alert | none_detected | standard phase I/II screen | standard metabolite prediction before wet-lab package |
| NPC314289 | nan | low_reactive_alert | none_detected | standard phase I/II screen | standard metabolite prediction before wet-lab package |
| NPC157340 | nan | low_reactive_alert | none_detected | standard phase I/II screen | standard metabolite prediction before wet-lab package |
| NPC302293 | nan | low_reactive_alert | none_detected | standard phase I/II screen | standard metabolite prediction before wet-lab package |
| NPC244869 | nan | low_reactive_alert | none_detected | standard phase I/II screen | standard metabolite prediction before wet-lab package |
| NPC321253 | nan | low_reactive_alert | none_detected | standard phase I/II screen | standard metabolite prediction before wet-lab package |
| NPC36877 | nan | low_reactive_alert | none_detected | standard phase I/II screen | standard metabolite prediction before wet-lab package |
| NPC193781 | nan | low_reactive_alert | none_detected | standard phase I/II screen | standard metabolite prediction before wet-lab package |
| NPC325130 | nan | low_reactive_alert | none_detected | standard phase I/II screen | standard metabolite prediction before wet-lab package |
| NPC195282 | nan | low_reactive_alert | none_detected | standard phase I/II screen | standard metabolite prediction before wet-lab package |
| NPC475968 | nan | low_reactive_alert | none_detected | standard phase I/II screen | standard metabolite prediction before wet-lab package |
| NPC321400 | nan | low_reactive_alert | none_detected | standard phase I/II screen | standard metabolite prediction before wet-lab package |
| NPC73764 | nan | low_reactive_alert | none_detected | standard phase I/II screen | standard metabolite prediction before wet-lab package |
| NPC77156 | nan | low_reactive_alert | none_detected | standard phase I/II screen | standard metabolite prediction before wet-lab package |
| NPC57078 | nan | low_reactive_alert | none_detected | standard phase I/II screen | standard metabolite prediction before wet-lab package |
| NPC301586 | nan | low_reactive_alert | none_detected | standard phase I/II screen | standard metabolite prediction before wet-lab package |
| NPC237965 | nan | low_reactive_alert | none_detected | standard phase I/II screen | standard metabolite prediction before wet-lab package |
| NPC196715 | nan | low_reactive_alert | none_detected | standard phase I/II screen | standard metabolite prediction before wet-lab package |
| NPC33067 | nan | low_reactive_alert | none_detected | standard phase I/II screen | standard metabolite prediction before wet-lab package |
| NPC261839 | nan | low_reactive_alert | none_detected | standard phase I/II screen | standard metabolite prediction before wet-lab package |
| NPC328835 | nan | low_reactive_alert | none_detected | standard phase I/II screen | standard metabolite prediction before wet-lab package |
| NPC248427 | nan | low_reactive_alert | none_detected | standard phase I/II screen | standard metabolite prediction before wet-lab package |
| NPC273019 | nan | low_reactive_alert | none_detected | standard phase I/II screen | standard metabolite prediction before wet-lab package |
| NPC168128 | nan | low_reactive_alert | none_detected | standard phase I/II screen | standard metabolite prediction before wet-lab package |
| NPC254230 | nan | low_reactive_alert | none_detected | standard phase I/II screen | standard metabolite prediction before wet-lab package |
| NPC189862 | nan | low_reactive_alert | none_detected | standard phase I/II screen | standard metabolite prediction before wet-lab package |
| NPC120104 | nan | low_reactive_alert | none_detected | standard phase I/II screen | standard metabolite prediction before wet-lab package |
| NPC23134 | nan | low_reactive_alert | none_detected | standard phase I/II screen | standard metabolite prediction before wet-lab package |
| NPC20938 | nan | low_reactive_alert | none_detected | standard phase I/II screen | standard metabolite prediction before wet-lab package |
| NPC256808 | nan | low_reactive_alert | none_detected | standard phase I/II screen | standard metabolite prediction before wet-lab package |
| NPC296246 | nan | low_reactive_alert | none_detected | standard phase I/II screen | standard metabolite prediction before wet-lab package |
| NPC75037 | nan | low_reactive_alert | none_detected | standard phase I/II screen | standard metabolite prediction before wet-lab package |
| NPC325909 | nan | low_reactive_alert | none_detected | standard phase I/II screen | standard metabolite prediction before wet-lab package |
| NPC196715 | dct | low_reactive_alert | none_detected | standard phase I/II screen | standard metabolite prediction before wet-lab package |
| NPC261839 | dct | low_reactive_alert | none_detected | standard phase I/II screen | standard metabolite prediction before wet-lab package |
| NPC196715 | ctgf | low_reactive_alert | none_detected | standard phase I/II screen | standard metabolite prediction before wet-lab package |

## Curator Rule

- `reactive_metabolite_review`: safety/main lead claim 전에 metabolite prediction 또는 assay caveat를 붙인다.
- `metabolism_caveat`: Phase II/skin metabolism caveat를 논문 limitation에 넣는다.
- `low_reactive_alert`: standard ADMET/MetID follow-up 후보로 유지한다.

```
### docs/GENETIC_CAUSALITY_DIRECTION_GATE.md tail -120

```text
# Genetic Causality Direction Gate

- timestamp: `2026-05-06T12:46:30+09:00`
- rows: `31`
- gate_counts: `{'direction_plausible': 9, 'direction_needs_genetic_or_phenotype_support': 1, 'causality_weak_or_unknown': 21}`
- purpose: target evidence를 disease association뿐 아니라 desired direction-of-effect, genetic/MR caveat와 연결한다.

## Direction Rows

| target | gate | desired direction | OT skin | OT translational | next |
|---|---|---|---:|---:|---|
| ctgf | direction_plausible | inhibit_or_reduce_pathway | 0.0 | 0.329 | use target claim with explicit direction-of-effect caveat |
| lox | direction_plausible | inhibit_or_reduce_pathway | 0.409 | 0.0 | use target claim with explicit direction-of-effect caveat |
| mmp1 | direction_plausible | context_dependent_modulate | 0.612 | 0.0 | use target claim with explicit direction-of-effect caveat |
| dct | direction_plausible | context_dependent_pigment_modulate | 0.747 | 0.0 | use target claim with explicit direction-of-effect caveat |
| mc1r | direction_plausible | context_dependent_pigment_modulate | 0.717 | 0.0 | use target claim with explicit direction-of-effect caveat |
| nr3c1 | direction_plausible | agonize_or_modulate_with_barrier_safety_caveat | 0.604 | 0.0 | use target claim with explicit direction-of-effect caveat |
| tyr | direction_plausible | inhibit_for_depigmentation_or_preserve_for_hair_pigment | 0.858 | 0.0 | use target claim with explicit direction-of-effect caveat |
| tyrp1 | direction_plausible | context_dependent_pigment_modulate | 0.803 | 0.0 | use target claim with explicit direction-of-effect caveat |
| ar | direction_plausible | antagonize_in_acne_or_alopecia_context | 0.582 | 0.0 | use target claim with explicit direction-of-effect caveat |
| tgfb1 | direction_needs_genetic_or_phenotype_support | inhibit_or_reduce_pathway | 0.0 | 0.0 | add Open Targets direction/MR/pQTL/eQTL limitation before strong biology claim |
| ctnnb1 | causality_weak_or_unknown | unknown | 0.0 | 0.0 | keep as exploratory target or negative-control until causal evidence improves |
| fgf2 | causality_weak_or_unknown | unknown | 0.094 | 0.0 | keep as exploratory target or negative-control until causal evidence improves |
| vegfa | causality_weak_or_unknown | unknown | 0.0 | 0.0 | keep as exploratory target or negative-control until causal evidence improves |
| f2rl1 | causality_weak_or_unknown | unknown | 0.0 | 0.0 | keep as exploratory target or negative-control until causal evidence improves |
| mitf | causality_weak_or_unknown | unknown | 0.757 | 0.0 | keep as exploratory target or negative-control until causal evidence improves |
| mylk | causality_weak_or_unknown | unknown | 0.0 | 0.0 | keep as exploratory target or negative-control until causal evidence improves |
| piezo1 | causality_weak_or_unknown | unknown | 0.353 | 0.0 | keep as exploratory target or negative-control until causal evidence improves |
| ptgdr2 | causality_weak_or_unknown | unknown | 0.0 | 0.0 | keep as exploratory target or negative-control until causal evidence improves |
| srd5a1 | causality_weak_or_unknown | unknown | 0.481 | 0.0 | keep as exploratory target or negative-control until causal evidence improves |
| srd5a2 | causality_weak_or_unknown | unknown | 0.702 | 0.0 | keep as exploratory target or negative-control until causal evidence improves |
| wnt10b | causality_weak_or_unknown | unknown | 0.038 | 0.0 | keep as exploratory target or negative-control until causal evidence improves |
| nlrp3 | causality_weak_or_unknown | unknown | 0.0 | 0.0 | keep as exploratory target or negative-control until causal evidence improves |
| ptgs2 | causality_weak_or_unknown | inhibit_in_inflammatory_context | 0.0 | 0.0 | keep as exploratory target or negative-control until causal evidence improves |
| rarg | causality_weak_or_unknown | unknown | 0.609 | 0.0 | keep as exploratory target or negative-control until causal evidence improves |
| srebf1 | causality_weak_or_unknown | unknown | 0.0 | 0.0 | keep as exploratory target or negative-control until causal evidence improves |
| tlr2 | causality_weak_or_unknown | unknown | 0.0 | 0.0 | keep as exploratory target or negative-control until causal evidence improves |
| col1a1 | causality_weak_or_unknown | unknown | 0.542 | 0.0 | keep as exploratory target or negative-control until causal evidence improves |
| jun | causality_weak_or_unknown | unknown | 0.372 | 0.0 | keep as exploratory target or negative-control until causal evidence improves |
| mmp3 | causality_weak_or_unknown | unknown | 0.0 | 0.0 | keep as exploratory target or negative-control until causal evidence improves |
| mmp9 | causality_weak_or_unknown | unknown | 0.0 | 0.0 | keep as exploratory target or negative-control until causal evidence improves |
| sirt1 | causality_weak_or_unknown | unknown | 0.109 | 0.0 | keep as exploratory target or negative-control until causal evidence improves |

## Curator Rule

- `direction_plausible`: target-focused narrative 가능하지만 causal proof가 아니라는 caveat를 유지한다.
- `direction_needs_genetic_or_phenotype_support`: phenotype or genetic direction evidence를 먼저 보강한다.
- `causality_weak_or_unknown`: biology claim을 exploratory로 낮춘다.

```
### docs/PHARMACOVIGILANCE_SIGNAL_GATE.md tail -120

```text
# Pharmacovigilance Signal Gate

- timestamp: `2026-05-06T12:46:30+09:00`
- rows: `442`
- gate_counts: `{'pv_signal_review': 240, 'pv_class_caveat': 140, 'pv_signal_not_mapped': 62}`
- purpose: FDA AEMS/FAERS 또는 class analog safety signal을 논문 safety caveat와 systemic/topical path 분리에 연결한다.

## PV Rows

| candidate | target | gate | warning terms | class context | next |
|---|---|---|---|---|---|
| R15_chromanol_Cl_pos9 | dct | pv_signal_review | photosensitivity_or_pigment_AE_review | pigmentation pathway class: pigment alteration and photosensitivity review | query AEMS/FAERS or literature class safety before systemic or topical safety claim |
| R15_chromanol_Cl_pos6 | dct | pv_signal_review | photosensitivity_or_pigment_AE_review | pigmentation pathway class: pigment alteration and photosensitivity review | query AEMS/FAERS or literature class safety before systemic or topical safety claim |
| R15_chromanol_Cl_pos6 | tyr | pv_signal_review | photosensitivity_or_pigment_AE_review | depigmenting agent class: irritation, ochronosis-like, photosensitivity review | query AEMS/FAERS or literature class safety before systemic or topical safety claim |
| R15_chromanol | tyr | pv_signal_review | photosensitivity_or_pigment_AE_review | depigmenting agent class: irritation, ochronosis-like, photosensitivity review | query AEMS/FAERS or literature class safety before systemic or topical safety claim |
| R15_chromanol | ptgs2 | pv_signal_review | known_systemic_class_warning | NSAID/COX class: GI, renal, hypersensitivity, cardiovascular warning | query AEMS/FAERS or literature class safety before systemic or topical safety claim |
| R15_chromanol_Cl_pos9 | tyr | pv_signal_review | photosensitivity_or_pigment_AE_review | depigmenting agent class: irritation, ochronosis-like, photosensitivity review | query AEMS/FAERS or literature class safety before systemic or topical safety claim |
| R15_chromanol | dct | pv_signal_review | photosensitivity_or_pigment_AE_review | pigmentation pathway class: pigment alteration and photosensitivity review | query AEMS/FAERS or literature class safety before systemic or topical safety claim |
| R15_chromanol_Cl_pos10 | dct | pv_signal_review | photosensitivity_or_pigment_AE_review | pigmentation pathway class: pigment alteration and photosensitivity review | query AEMS/FAERS or literature class safety before systemic or topical safety claim |
| R15_chromanol_Cl_pos10 | tyr | pv_signal_review | photosensitivity_or_pigment_AE_review | depigmenting agent class: irritation, ochronosis-like, photosensitivity review | query AEMS/FAERS or literature class safety before systemic or topical safety claim |
| R15_chromanol | tyrp1 | pv_signal_review | photosensitivity_or_pigment_AE_review | no close approved-drug class signal mapped | query AEMS/FAERS or literature class safety before systemic or topical safety claim |
| R15_chromanol_Me9_Me10 | tyr | pv_signal_review | photosensitivity_or_pigment_AE_review | depigmenting agent class: irritation, ochronosis-like, photosensitivity review | query AEMS/FAERS or literature class safety before systemic or topical safety claim |
| R15_chromanol_Me6_Me9 | tyr | pv_signal_review | photosensitivity_or_pigment_AE_review | depigmenting agent class: irritation, ochronosis-like, photosensitivity review | query AEMS/FAERS or literature class safety before systemic or topical safety claim |
| R15_chromanol_Me6_Me9 | dct | pv_signal_review | photosensitivity_or_pigment_AE_review | pigmentation pathway class: pigment alteration and photosensitivity review | query AEMS/FAERS or literature class safety before systemic or topical safety claim |
| R15_chromanol_Me9_Me10 | dct | pv_signal_review | photosensitivity_or_pigment_AE_review | pigmentation pathway class: pigment alteration and photosensitivity review | query AEMS/FAERS or literature class safety before systemic or topical safety claim |
| R15_chromanol_Me6_Me10 | tyr | pv_signal_review | photosensitivity_or_pigment_AE_review | depigmenting agent class: irritation, ochronosis-like, photosensitivity review | query AEMS/FAERS or literature class safety before systemic or topical safety claim |
| R15_chromanol_Me6_Me10 | dct | pv_signal_review | photosensitivity_or_pigment_AE_review | pigmentation pathway class: pigment alteration and photosensitivity review | query AEMS/FAERS or literature class safety before systemic or topical safety claim |
| R15_chromanol | ar | pv_signal_review | known_systemic_class_warning | antiandrogen/endocrine class: libido, teratogenicity, systemic endocrine effects | query AEMS/FAERS or literature class safety before systemic or topical safety claim |
| NPC243469 | nan | pv_signal_review | systemic_absorption_or_accumulation_review | no close approved-drug class signal mapped | query AEMS/FAERS or literature class safety before systemic or topical safety claim |
| NPC194985 | nan | pv_signal_review | systemic_absorption_or_accumulation_review | no close approved-drug class signal mapped | query AEMS/FAERS or literature class safety before systemic or topical safety claim |
| NPC281540 | nan | pv_signal_review | systemic_absorption_or_accumulation_review | no close approved-drug class signal mapped | query AEMS/FAERS or literature class safety before systemic or topical safety claim |
| NPC469970 | nan | pv_signal_review | systemic_absorption_or_accumulation_review | no close approved-drug class signal mapped | query AEMS/FAERS or literature class safety before systemic or topical safety claim |
| NPC84346 | nan | pv_signal_review | systemic_absorption_or_accumulation_review | no close approved-drug class signal mapped | query AEMS/FAERS or literature class safety before systemic or topical safety claim |
| NPC474914 | nan | pv_signal_review | systemic_absorption_or_accumulation_review | no close approved-drug class signal mapped | query AEMS/FAERS or literature class safety before systemic or topical safety claim |
| NPC324003 | nan | pv_signal_review | systemic_absorption_or_accumulation_review | no close approved-drug class signal mapped | query AEMS/FAERS or literature class safety before systemic or topical safety claim |
| NPC479534 | nan | pv_signal_review | systemic_absorption_or_accumulation_review | no close approved-drug class signal mapped | query AEMS/FAERS or literature class safety before systemic or topical safety claim |
| NPC329517 | nan | pv_signal_review | systemic_absorption_or_accumulation_review | no close approved-drug class signal mapped | query AEMS/FAERS or literature class safety before systemic or topical safety claim |
| NPC93630 | nan | pv_signal_review | systemic_absorption_or_accumulation_review | no close approved-drug class signal mapped | query AEMS/FAERS or literature class safety before systemic or topical safety claim |
| NPC327468 | nan | pv_signal_review | systemic_absorption_or_accumulation_review | no close approved-drug class signal mapped | query AEMS/FAERS or literature class safety before systemic or topical safety claim |
| NPC251201 | nan | pv_signal_review | systemic_absorption_or_accumulation_review | no close approved-drug class signal mapped | query AEMS/FAERS or literature class safety before systemic or topical safety claim |
| NPC228994 | nan | pv_signal_review | systemic_absorption_or_accumulation_review | no close approved-drug class signal mapped | query AEMS/FAERS or literature class safety before systemic or topical safety claim |
| NPC196136 | nan | pv_signal_review | systemic_absorption_or_accumulation_review | no close approved-drug class signal mapped | query AEMS/FAERS or literature class safety before systemic or topical safety claim |
| NPC35553 | nan | pv_signal_review | systemic_absorption_or_accumulation_review | no close approved-drug class signal mapped | query AEMS/FAERS or literature class safety before systemic or topical safety claim |
| NPC327424 | nan | pv_signal_review | systemic_absorption_or_accumulation_review | no close approved-drug class signal mapped | query AEMS/FAERS or literature class safety before systemic or topical safety claim |
| NPC257680 | nan | pv_signal_review | systemic_absorption_or_accumulation_review | no close approved-drug class signal mapped | query AEMS/FAERS or literature class safety before systemic or topical safety claim |
| NPC306634 | nan | pv_signal_review | systemic_absorption_or_accumulation_review | no close approved-drug class signal mapped | query AEMS/FAERS or literature class safety before systemic or topical safety claim |
| NPC273290 | nan | pv_signal_review | systemic_absorption_or_accumulation_review | no close approved-drug class signal mapped | query AEMS/FAERS or literature class safety before systemic or topical safety claim |
| NPC157431 | nan | pv_signal_review | systemic_absorption_or_accumulation_review | no close approved-drug class signal mapped | query AEMS/FAERS or literature class safety before systemic or topical safety claim |
| NPC243184 | nan | pv_signal_review | systemic_absorption_or_accumulation_review | no close approved-drug class signal mapped | query AEMS/FAERS or literature class safety before systemic or topical safety claim |
| NPC321984 | nan | pv_signal_review | systemic_absorption_or_accumulation_review | no close approved-drug class signal mapped | query AEMS/FAERS or literature class safety before systemic or topical safety claim |
| NPC58557 | nan | pv_signal_review | systemic_absorption_or_accumulation_review | no close approved-drug class signal mapped | query AEMS/FAERS or literature class safety before systemic or topical safety claim |
| NPC323203 | nan | pv_signal_review | systemic_absorption_or_accumulation_review | no close approved-drug class signal mapped | query AEMS/FAERS or literature class safety before systemic or topical safety claim |
| NPC280090 | nan | pv_signal_review | systemic_absorption_or_accumulation_review | no close approved-drug class signal mapped | query AEMS/FAERS or literature class safety before systemic or topical safety claim |
| chromanol_arom9+arom10_Cl+Cl_ptgs2 | ptgs2 | pv_signal_review | known_systemic_class_warning | NSAID/COX class: GI, renal, hypersensitivity, cardiovascular warning | query AEMS/FAERS or literature class safety before systemic or topical safety claim |
| chromanol_arom9+arom10_Cl+Cl_dct | dct | pv_signal_review | photosensitivity_or_pigment_AE_review | pigmentation pathway class: pigment alteration and photosensitivity review | query AEMS/FAERS or literature class safety before systemic or topical safety claim |
| chromanol_arom6+arom9_Cl+Cl_ptgs2 | ptgs2 | pv_signal_review | known_systemic_class_warning | NSAID/COX class: GI, renal, hypersensitivity, cardiovascular warning | query AEMS/FAERS or literature class safety before systemic or topical safety claim |

## Curator Rule

- `pv_signal_review`: AEMS/FAERS/literature class safety query 전까지 safety-positive 표현 금지.
- `pv_class_caveat`: 신호는 causation이 아니며 manuscript limitation으로만 사용한다.
- `pv_signal_not_mapped`: 안전하다는 뜻이 아니라 데이터 미연결 상태다.

```
### docs/SINGLE_CELL_FM_RELIABILITY_GATE.md tail -120

```text
# Single-Cell FM Reliability Gate

- timestamp: `2026-05-06T12:46:31+09:00`
- rows: `32`
- gate_counts: `{'fm_supported_with_controls': 2, 'zero_shot_reliability_review': 12, 'fm_not_actionable': 18}`
- purpose: scGPT/Geneformer/virtual-cell style evidence를 zero-shot limitation과 baseline-control 요구사항으로 제한한다.

## FM Reliability Rows

| target | gate | cells | perturbation | spatial | controls | next |
|---|---|---|---|---|---|---|
| dct | fm_supported_with_controls | melanocyte | high | spatially_anchorable | zero-shot baseline;cell-type proximity;batch/domain check;simpler model comparison;wet-lab endpoint caveat | allow virtual-cell/phenomics hypothesis with simple-baseline and wet-lab caveat |
| tyr | fm_supported_with_controls | melanocyte | high | spatially_anchorable | zero-shot baseline;cell-type proximity;batch/domain check;simpler model comparison;wet-lab endpoint caveat | allow virtual-cell/phenomics hypothesis with simple-baseline and wet-lab caveat |
| ar | zero_shot_reliability_review | dermal_papilla_cell;hair_follicle_keratinocyte;immune_cell;keratinocyte;sebocyte | review | atlas_review | zero-shot baseline;cell-type proximity;batch/domain check;simpler model comparison;wet-lab endpoint caveat | require cell-type match, fine-tuning/proximity check, and simpler-baseline comparison |
| ctgf | zero_shot_reliability_review | dermal_fibroblast | review | atlas_review | zero-shot baseline;cell-type proximity;batch/domain check;simpler model comparison;wet-lab endpoint caveat | require cell-type match, fine-tuning/proximity check, and simpler-baseline comparison |
| lox | zero_shot_reliability_review | dermal_fibroblast | review | atlas_review | zero-shot baseline;cell-type proximity;batch/domain check;simpler model comparison;wet-lab endpoint caveat | require cell-type match, fine-tuning/proximity check, and simpler-baseline comparison |
| mc1r | zero_shot_reliability_review | melanocyte | review | atlas_review | zero-shot baseline;cell-type proximity;batch/domain check;simpler model comparison;wet-lab endpoint caveat | require cell-type match, fine-tuning/proximity check, and simpler-baseline comparison |
| mmp1 | zero_shot_reliability_review | dermal_fibroblast;keratinocyte | review | atlas_review | zero-shot baseline;cell-type proximity;batch/domain check;simpler model comparison;wet-lab endpoint caveat | require cell-type match, fine-tuning/proximity check, and simpler-baseline comparison |
| nr3c1 | zero_shot_reliability_review | melanocyte | review | atlas_review | zero-shot baseline;cell-type proximity;batch/domain check;simpler model comparison;wet-lab endpoint caveat | require cell-type match, fine-tuning/proximity check, and simpler-baseline comparison |
| piezo1 | zero_shot_reliability_review | dermal_papilla_cell;hair_follicle_keratinocyte | review | spatial_context_missing | zero-shot baseline;cell-type proximity;batch/domain check;simpler model comparison;wet-lab endpoint caveat | require cell-type match, fine-tuning/proximity check, and simpler-baseline comparison |
| rarg | zero_shot_reliability_review | immune_cell;keratinocyte;sebocyte | review | spatial_context_missing | zero-shot baseline;cell-type proximity;batch/domain check;simpler model comparison;wet-lab endpoint caveat | require cell-type match, fine-tuning/proximity check, and simpler-baseline comparison |
| srd5a1 | zero_shot_reliability_review | dermal_papilla_cell;hair_follicle_keratinocyte | review | spatial_context_missing | zero-shot baseline;cell-type proximity;batch/domain check;simpler model comparison;wet-lab endpoint caveat | require cell-type match, fine-tuning/proximity check, and simpler-baseline comparison |
| srd5a2 | zero_shot_reliability_review | dermal_papilla_cell;hair_follicle_keratinocyte;immune_cell;keratinocyte;sebocyte | review | spatial_context_missing | zero-shot baseline;cell-type proximity;batch/domain check;simpler model comparison;wet-lab endpoint caveat | require cell-type match, fine-tuning/proximity check, and simpler-baseline comparison |
| tgfb1 | zero_shot_reliability_review | dermal_fibroblast | review | atlas_review | zero-shot baseline;cell-type proximity;batch/domain check;simpler model comparison;wet-lab endpoint caveat | require cell-type match, fine-tuning/proximity check, and simpler-baseline comparison |
| tyrp1 | zero_shot_reliability_review | melanocyte | review | atlas_review | zero-shot baseline;cell-type proximity;batch/domain check;simpler model comparison;wet-lab endpoint caveat | require cell-type match, fine-tuning/proximity check, and simpler-baseline comparison |
| col1a1 | fm_not_actionable | dermal_fibroblast;keratinocyte | low | spatial_context_missing | zero-shot baseline;cell-type proximity;batch/domain check;simpler model comparison;wet-lab endpoint caveat | do not use single-cell FM for target claim yet |
| ctnnb1 | fm_not_actionable | dermal_fibroblast;dermal_papilla_cell;hair_follicle_keratinocyte | low | spatial_context_missing | zero-shot baseline;cell-type proximity;batch/domain check;simpler model comparison;wet-lab endpoint caveat | do not use single-cell FM for target claim yet |
| f2rl1 | fm_not_actionable | melanocyte | low | spatial_context_missing | zero-shot baseline;cell-type proximity;batch/domain check;simpler model comparison;wet-lab endpoint caveat | do not use single-cell FM for target claim yet |
| fgf2 | fm_not_actionable | dermal_fibroblast | low | spatial_context_missing | zero-shot baseline;cell-type proximity;batch/domain check;simpler model comparison;wet-lab endpoint caveat | do not use single-cell FM for target claim yet |
| jun | fm_not_actionable | dermal_fibroblast;keratinocyte | low | spatial_context_missing | zero-shot baseline;cell-type proximity;batch/domain check;simpler model comparison;wet-lab endpoint caveat | do not use single-cell FM for target claim yet |
| mitf | fm_not_actionable | melanocyte | low | spatial_context_missing | zero-shot baseline;cell-type proximity;batch/domain check;simpler model comparison;wet-lab endpoint caveat | do not use single-cell FM for target claim yet |
| mmp3 | fm_not_actionable | dermal_fibroblast;keratinocyte | low | spatial_context_missing | zero-shot baseline;cell-type proximity;batch/domain check;simpler model comparison;wet-lab endpoint caveat | do not use single-cell FM for target claim yet |
| mmp9 | fm_not_actionable | dermal_fibroblast;keratinocyte | low | spatial_context_missing | zero-shot baseline;cell-type proximity;batch/domain check;simpler model comparison;wet-lab endpoint caveat | do not use single-cell FM for target claim yet |
| mylk | fm_not_actionable | dermal_papilla_cell;hair_follicle_keratinocyte | low | spatial_context_missing | zero-shot baseline;cell-type proximity;batch/domain check;simpler model comparison;wet-lab endpoint caveat | do not use single-cell FM for target claim yet |
| nlrp3 | fm_not_actionable | immune_cell;keratinocyte;sebocyte | low | spatial_context_missing | zero-shot baseline;cell-type proximity;batch/domain check;simpler model comparison;wet-lab endpoint caveat | do not use single-cell FM for target claim yet |
| ptgdr2 | fm_not_actionable | dermal_papilla_cell;hair_follicle_keratinocyte | low | spatial_context_missing | zero-shot baseline;cell-type proximity;batch/domain check;simpler model comparison;wet-lab endpoint caveat | do not use single-cell FM for target claim yet |
| ptgs2 | fm_not_actionable | immune_cell;keratinocyte;sebocyte | low | atlas_review | zero-shot baseline;cell-type proximity;batch/domain check;simpler model comparison;wet-lab endpoint caveat | do not use single-cell FM for target claim yet |
| sirt1 | fm_not_actionable | dermal_fibroblast;keratinocyte | low | spatial_context_missing | zero-shot baseline;cell-type proximity;batch/domain check;simpler model comparison;wet-lab endpoint caveat | do not use single-cell FM for target claim yet |
| srebf1 | fm_not_actionable | immune_cell;keratinocyte;sebocyte | low | spatial_context_missing | zero-shot baseline;cell-type proximity;batch/domain check;simpler model comparison;wet-lab endpoint caveat | do not use single-cell FM for target claim yet |
| srebp1 | fm_not_actionable | missing | low | spatial_context_missing | zero-shot baseline;cell-type proximity;batch/domain check;simpler model comparison;wet-lab endpoint caveat | do not use single-cell FM for target claim yet |
| tlr2 | fm_not_actionable | immune_cell;keratinocyte;sebocyte | low | spatial_context_missing | zero-shot baseline;cell-type proximity;batch/domain check;simpler model comparison;wet-lab endpoint caveat | do not use single-cell FM for target claim yet |
| vegfa | fm_not_actionable | dermal_fibroblast | low | spatial_context_missing | zero-shot baseline;cell-type proximity;batch/domain check;simpler model comparison;wet-lab endpoint caveat | do not use single-cell FM for target claim yet |
| wnt10b | fm_not_actionable | dermal_papilla_cell;hair_follicle_keratinocyte | low | spatial_context_missing | zero-shot baseline;cell-type proximity;batch/domain check;simpler model comparison;wet-lab endpoint caveat | do not use single-cell FM for target claim yet |

## Curator Rule

- `fm_supported_with_controls`: virtual-cell claim은 hypothesis로만 쓰고 baseline-control을 명시한다.
- `zero_shot_reliability_review`: fine-tuning/proximity/simple baseline 없이는 manuscript main claim 금지.
- `fm_not_actionable`: 추가 docking보다 target/cell evidence 보강이 먼저다.

```
### docs/STRUCTURE_BENCHMARK_DECOY_GATE.md tail -120

```text
# Structure Benchmark Decoy Gate

- timestamp: `2026-05-06T12:46:31+09:00`
- rows: `32`
- gate_counts: `{'benchmark_decoys_required_before_strong_claim': 0, 'benchmark_ready_as_caveat': 8, 'cross_model_first': 5, 'benchmark_low_priority': 19}`
- purpose: PoseBench-style claim discipline을 local candidate에 적용해 decoy, negative-control, PLIF, cross-model requirement를 명시한다.

## Benchmark Rows

| job | target | compound | gate | control | benchmark package | next |
|---|---|---|---|---|---|---|
| r16_03_dct | dct | R15_chromanol_Cl_pos9 | benchmark_ready_as_caveat | melanogenesis_reference_compound_and_inactive_decoys | >=20 decoys or available local analogs;candidate beats decoy median;no severe PoseBusters fail;MD stable or cross-model concordant | add matched decoy/enrichment plan to methods; keep caveat wording |
| r16_02_dct | dct | R15_chromanol_Cl_pos6 | benchmark_ready_as_caveat | melanogenesis_reference_compound_and_inactive_decoys | >=20 decoys or available local analogs;candidate beats decoy median;no severe PoseBusters fail;MD stable or cross-model concordant | add matched decoy/enrichment plan to methods; keep caveat wording |
| r16_02_tyr | tyr | R15_chromanol_Cl_pos6 | benchmark_ready_as_caveat | kojic_acid_or_arbutin_positive_control | >=20 decoys or available local analogs;candidate beats decoy median;no severe PoseBusters fail;MD stable or cross-model concordant | add matched decoy/enrichment plan to methods; keep caveat wording |
| r16_05_tgfb1 | tgfb1 | R15_chromanol_Me6_Me9 | benchmark_ready_as_caveat | TGF-beta pathway positive/negative phenotype controls | >=20 decoys or available local analogs;candidate beats decoy median;no severe PoseBusters fail;MD stable or cross-model concordant | add matched decoy/enrichment plan to methods; keep caveat wording |
| r16_02_tgfb1 | tgfb1 | R15_chromanol_Cl_pos6 | benchmark_ready_as_caveat | TGF-beta pathway positive/negative phenotype controls | >=20 decoys or available local analogs;candidate beats decoy median;no severe PoseBusters fail;MD stable or cross-model concordant | add matched decoy/enrichment plan to methods; keep caveat wording |
| r16_03_tgfb1 | tgfb1 | R15_chromanol_Cl_pos9 | benchmark_ready_as_caveat | TGF-beta pathway positive/negative phenotype controls | >=20 decoys or available local analogs;candidate beats decoy median;no severe PoseBusters fail;MD stable or cross-model concordant | add matched decoy/enrichment plan to methods; keep caveat wording |
| r16_06_tgfb1 | tgfb1 | R15_chromanol_Me9_Me10 | benchmark_ready_as_caveat | TGF-beta pathway positive/negative phenotype controls | >=20 decoys or available local analogs;candidate beats decoy median;no severe PoseBusters fail;MD stable or cross-model concordant | add matched decoy/enrichment plan to methods; keep caveat wording |
| r16_04_tgfb1 | tgfb1 | R15_chromanol_Me6_Me10 | benchmark_ready_as_caveat | TGF-beta pathway positive/negative phenotype controls | >=20 decoys or available local analogs;candidate beats decoy median;no severe PoseBusters fail;MD stable or cross-model concordant | add matched decoy/enrichment plan to methods; keep caveat wording |
| r16_01_tgfb1 | tgfb1 | R15_chromanol_Cl_pos10 | cross_model_first | TGF-beta pathway positive/negative phenotype controls | >=20 decoys or available local analogs;candidate beats decoy median;no severe PoseBusters fail;MD stable or cross-model concordant | run Chai-1/DiffDock/Vina/PLIF or target-shuffle before lead table |
| r15_chrom_tyr | tyr | R15_chromanol | cross_model_first | kojic_acid_or_arbutin_positive_control | >=20 decoys or available local analogs;candidate beats decoy median;no severe PoseBusters fail;MD stable or cross-model concordant | run Chai-1/DiffDock/Vina/PLIF or target-shuffle before lead table |
| r15_chrom_dct | dct | R15_chromanol | cross_model_first | melanogenesis_reference_compound_and_inactive_decoys | >=20 decoys or available local analogs;candidate beats decoy median;no severe PoseBusters fail;MD stable or cross-model concordant | run Chai-1/DiffDock/Vina/PLIF or target-shuffle before lead table |
| r16_01_dct | dct | R15_chromanol_Cl_pos10 | cross_model_first | melanogenesis_reference_compound_and_inactive_decoys | >=20 decoys or available local analogs;candidate beats decoy median;no severe PoseBusters fail;MD stable or cross-model concordant | run Chai-1/DiffDock/Vina/PLIF or target-shuffle before lead table |
| r15_chrom_tgfb1 | tgfb1 | R15_chromanol | cross_model_first | TGF-beta pathway positive/negative phenotype controls | >=20 decoys or available local analogs;candidate beats decoy median;no severe PoseBusters fail;MD stable or cross-model concordant | run Chai-1/DiffDock/Vina/PLIF or target-shuffle before lead table |
| r15_chrom_ptgs2 | ptgs2 | R15_chromanol | benchmark_low_priority | celecoxib_or_indomethacin_class_control | >=20 decoys or available local analogs;candidate beats decoy median;no severe PoseBusters fail;MD stable or cross-model concordant | use as exploratory or negative-control row |
| r16_03_tyr | tyr | R15_chromanol_Cl_pos9 | benchmark_low_priority | kojic_acid_or_arbutin_positive_control | >=20 decoys or available local analogs;candidate beats decoy median;no severe PoseBusters fail;MD stable or cross-model concordant | use as exploratory or negative-control row |
| r16_01_tyr | tyr | R15_chromanol_Cl_pos10 | benchmark_low_priority | kojic_acid_or_arbutin_positive_control | >=20 decoys or available local analogs;candidate beats decoy median;no severe PoseBusters fail;MD stable or cross-model concordant | use as exploratory or negative-control row |
| r15_chrom_tyrp1 | tyrp1 | R15_chromanol | benchmark_low_priority | literature ligand or pathway positive control required | >=20 decoys or available local analogs;candidate beats decoy median;no severe PoseBusters fail;MD stable or cross-model concordant | use as exploratory or negative-control row |
| r16_06_tyr | tyr | R15_chromanol_Me9_Me10 | benchmark_low_priority | kojic_acid_or_arbutin_positive_control | >=20 decoys or available local analogs;candidate beats decoy median;no severe PoseBusters fail;MD stable or cross-model concordant | use as exploratory or negative-control row |
| r16_05_tyr | tyr | R15_chromanol_Me6_Me9 | benchmark_low_priority | kojic_acid_or_arbutin_positive_control | >=20 decoys or available local analogs;candidate beats decoy median;no severe PoseBusters fail;MD stable or cross-model concordant | use as exploratory or negative-control row |
| r16_05_dct | dct | R15_chromanol_Me6_Me9 | benchmark_low_priority | melanogenesis_reference_compound_and_inactive_decoys | >=20 decoys or available local analogs;candidate beats decoy median;no severe PoseBusters fail;MD stable or cross-model concordant | use as exploratory or negative-control row |
| r16_06_dct | dct | R15_chromanol_Me9_Me10 | benchmark_low_priority | melanogenesis_reference_compound_and_inactive_decoys | >=20 decoys or available local analogs;candidate beats decoy median;no severe PoseBusters fail;MD stable or cross-model concordant | use as exploratory or negative-control row |
| r16_04_tyr | tyr | R15_chromanol_Me6_Me10 | benchmark_low_priority | kojic_acid_or_arbutin_positive_control | >=20 decoys or available local analogs;candidate beats decoy median;no severe PoseBusters fail;MD stable or cross-model concordant | use as exploratory or negative-control row |
| r16_04_dct | dct | R15_chromanol_Me6_Me10 | benchmark_low_priority | melanogenesis_reference_compound_and_inactive_decoys | >=20 decoys or available local analogs;candidate beats decoy median;no severe PoseBusters fail;MD stable or cross-model concordant | use as exploratory or negative-control row |
| r15_chrom_mmp1 | mmp1 | R15_chromanol | benchmark_low_priority | MMP inhibitor or UV-photoaging control | >=20 decoys or available local analogs;candidate beats decoy median;no severe PoseBusters fail;MD stable or cross-model concordant | use as exploratory or negative-control row |
| r15_chrom_srd5a2 | srd5a2 | R15_chromanol | benchmark_low_priority | literature ligand or pathway positive control required | >=20 decoys or available local analogs;candidate beats decoy median;no severe PoseBusters fail;MD stable or cross-model concordant | use as exploratory or negative-control row |
| r15_chrom_ar | ar | R15_chromanol | benchmark_low_priority | DHT/antiandrogen reporter controls | >=20 decoys or available local analogs;candidate beats decoy median;no severe PoseBusters fail;MD stable or cross-model concordant | use as exploratory or negative-control row |
| r15_chrom_lox | lox | R15_chromanol | benchmark_low_priority | literature ligand or pathway positive control required | >=20 decoys or available local analogs;candidate beats decoy median;no severe PoseBusters fail;MD stable or cross-model concordant | use as exploratory or negative-control row |
| r15_chrom_sirt1 | sirt1 | R15_chromanol | benchmark_low_priority | literature ligand or pathway positive control required | >=20 decoys or available local analogs;candidate beats decoy median;no severe PoseBusters fail;MD stable or cross-model concordant | use as exploratory or negative-control row |
| r15_chrom_srd5a1 | srd5a1 | R15_chromanol | benchmark_low_priority | literature ligand or pathway positive control required | >=20 decoys or available local analogs;candidate beats decoy median;no severe PoseBusters fail;MD stable or cross-model concordant | use as exploratory or negative-control row |
| r15_chrom_srebp1 | srebp1 | R15_chromanol | benchmark_low_priority | literature ligand or pathway positive control required | >=20 decoys or available local analogs;candidate beats decoy median;no severe PoseBusters fail;MD stable or cross-model concordant | use as exploratory or negative-control row |
| r15_chrom_ctgf | ctgf | R15_chromanol | benchmark_low_priority | literature ligand or pathway positive control required | >=20 decoys or available local analogs;candidate beats decoy median;no severe PoseBusters fail;MD stable or cross-model concordant | use as exploratory or negative-control row |
| r15_chrom_mitf | mitf | R15_chromanol | benchmark_low_priority | literature ligand or pathway positive control required | >=20 decoys or available local analogs;candidate beats decoy median;no severe PoseBusters fail;MD stable or cross-model concordant | use as exploratory or negative-control row |

## Curator Rule

- `benchmark_decoys_required_before_strong_claim`: strong binding language 전 decoy/cross-model package 필수.
- `benchmark_ready_as_caveat`: caveat 유지 시 논문 methods에 benchmark plan을 포함한다.
- `cross_model_first`: 다음 GPU-free window에서 cross-model/decoy 중 하나를 우선 큐잉한다.

```
### docs/TOPICAL_FORMULATION_BO.md tail -100

```text
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

```
### docs/FREE_ENERGY_VALIDATION_PLAN.md tail -100

```text
# Free-energy Validation Plan

- timestamp: `2026-05-06T12:46:32+09:00`
- rows: `32`
- existing_rbfe_edge_rows: `15`
- method_counts: `{'RBFE_network': 5, 'ABFE_scout': 1, 'ABFE_or_CBFE_scout': 6, 'defer': 20}`
- OpenFE status: `openfe_missing_install_or_env`
- purpose: Boltz/MD 후보를 논문용 claim 전에 RBFE/ABFE/CBFE follow-up으로 올릴지 결정한다.

## Priority FE Follow-ups

| rank | target | compound | method | priority | consensus | pose | MD | next |
|---:|---|---|---|---:|---|---|---|---|
| 1 | dct | R15_chromanol_Cl_pos9 | RBFE_network | 0.8793 | high_confidence | pass | strong_stable | prepare OpenFE edge map; run short solvent/complex sanity first |
| 2 | tyr | R15_chromanol | ABFE_scout | 0.8774 | high_confidence | pass | strong_stable | prepare OpenFE edge map; run short solvent/complex sanity first |
| 3 | tgfb1 | R15_chromanol_Me6_Me9 | RBFE_network | 0.8736 | high_confidence | pass | strong_stable | prepare OpenFE edge map; run short solvent/complex sanity first |
| 4 | dct | R15_chromanol_Cl_pos6 | RBFE_network | 0.8714 | high_confidence | pass | strong_stable | prepare OpenFE edge map; run short solvent/complex sanity first |
| 5 | tyr | R15_chromanol_Cl_pos6 | RBFE_network | 0.8692 | high_confidence | pass | strong_stable | prepare OpenFE edge map; run short solvent/complex sanity first |
| 6 | tgfb1 | R15_chromanol_Cl_pos6 | RBFE_network | 0.8555 | high_confidence | pass | strong_stable | prepare OpenFE edge map; run short solvent/complex sanity first |
| 7 | tgfb1 | R15_chromanol_Cl_pos9 | ABFE_or_CBFE_scout | 0.7635 | usable_with_caveat | review | strong_stable | fix pose caveat or run replicate MD before production FE |
| 8 | dct | R15_chromanol | ABFE_or_CBFE_scout | 0.7533 | usable_with_caveat | review | strong_stable | fix pose caveat or run replicate MD before production FE |
| 9 | tgfb1 | R15_chromanol_Me9_Me10 | ABFE_or_CBFE_scout | 0.7463 | usable_with_caveat | review | strong_stable | fix pose caveat or run replicate MD before production FE |
| 10 | tgfb1 | R15_chromanol | ABFE_or_CBFE_scout | 0.7358 | usable_with_caveat | review | strong_stable | fix pose caveat or run replicate MD before production FE |
| 11 | tgfb1 | R15_chromanol_Me6_Me10 | ABFE_or_CBFE_scout | 0.7343 | usable_with_caveat | review | strong_stable | fix pose caveat or run replicate MD before production FE |
| 12 | tgfb1 | R15_chromanol_Cl_pos10 | ABFE_or_CBFE_scout | 0.724 | usable_with_caveat | review | strong_stable | fix pose caveat or run replicate MD before production FE |
| 13 | ptgs2 | R15_chromanol | defer | 0.3237 | usable_with_caveat | pass | missing | do not spend FE budget until pose/MD/target caveat improves |
| 14 | tyr | R15_chromanol_Cl_pos9 | defer | 0.3185 | usable_with_caveat | pass | missing | do not spend FE budget until pose/MD/target caveat improves |
| 15 | dct | R15_chromanol_Cl_pos10 | defer | 0.3154 | usable_with_caveat | review | missing | do not spend FE budget until pose/MD/target caveat improves |
| 16 | tyr | R15_chromanol_Cl_pos10 | defer | 0.313 | usable_with_caveat | pass | missing | do not spend FE budget until pose/MD/target caveat improves |
| 17 | tyrp1 | R15_chromanol | defer | 0.3124 | usable_with_caveat | pass | missing | do not spend FE budget until pose/MD/target caveat improves |
| 18 | tyr | R15_chromanol_Me9_Me10 | defer | 0.3031 | usable_with_caveat | pass | missing | do not spend FE budget until pose/MD/target caveat improves |
| 19 | tyr | R15_chromanol_Me6_Me9 | defer | 0.3023 | usable_with_caveat | pass | missing | do not spend FE budget until pose/MD/target caveat improves |
| 20 | dct | R15_chromanol_Me6_Me9 | defer | 0.2993 | usable_with_caveat | pass | missing | do not spend FE budget until pose/MD/target caveat improves |
| 21 | dct | R15_chromanol_Me9_Me10 | defer | 0.2991 | usable_with_caveat | pass | missing | do not spend FE budget until pose/MD/target caveat improves |
| 22 | tyr | R15_chromanol_Me6_Me10 | defer | 0.2822 | usable_with_caveat | review | missing | do not spend FE budget until pose/MD/target caveat improves |
| 23 | dct | R15_chromanol_Me6_Me10 | defer | 0.2753 | usable_with_caveat | review | missing | do not spend FE budget until pose/MD/target caveat improves |
| 24 | mmp1 | R15_chromanol | defer | 0.2647 | usable_with_caveat | review | missing | do not spend FE budget until pose/MD/target caveat improves |
| 25 | sirt1 | R15_chromanol | defer | 0.2512 | review_before_claim | review | missing | do not spend FE budget until pose/MD/target caveat improves |

## Hard Blocker: MMP-1 Zinc/ZAFF ABFE

- gate: `MMP1_ZAFF_ABFE_MUST_PASS`
- status: `blocked_zaff_not_integrated`
- current receptor Zn atoms: `0`
- required value: `restraint_corrected_delta_g_bind_kcal_mol < 0`
- strict pass: `upper_uncertainty_bound_below_0_kcal_mol`
- details: `docs/MMP1_ZAFF_ABFE_GATE.md`
- Until this gate passes, MMP-1 claims remain zinc-model-limited and cannot be described as ZAFF-corrected ABFE-confirmed binding.

## Curator Rule

- MMP-1 zinc/ZAFF ABFE is a hard blocker for any statement stronger than Boltz/MD-supported MMP-1 engagement.
- GPU가 바쁠 때는 이 plan을 생성만 하고 FE production은 큐잉하지 않는다.
- `RBFE_network`는 같은 target의 R16 chloro/dimethyl analog series에 우선 적용한다.
- `ABFE_or_CBFE_scout`는 paper claim 보강용 소규모 validation으로만 사용한다.
- `openfe_missing_install_or_env`이면 설치/환경 점검 문서화만 하고 heavy FE를 실행하지 않는다.

```
### docs/DERMAL_REGULATORY_SAFETY_GATE.md tail -100

```text
# Dermal Regulatory Safety Gate

- timestamp: `2026-05-06T12:46:32+09:00`
- rows: `112`
- gate_counts: `{'green': 32, 'yellow': 80, 'red': 0}`
- purpose: 외용제 후보를 OECD TG497 skin sensitisation, ICH S10 photosafety, FDA IVRT/IVPT 관점의 in-silico pre-gate로 제한한다.

## Top Green/Yellow Candidates

| candidate | target | gate | cLogP | MW | alerts | photosafety | IVPT |
|---|---|---|---:|---:|---|---|---|
| R15_chromanol_Me6_Me9 | tgfb1 | green | 1.552 | 208.257 | none_detected | none_detected | ready_for_IVRT_IVPT_design |
| R15_chromanol_Me6_Me10 | tgfb1 | green | 1.552 | 208.257 | none_detected | none_detected | ready_for_IVRT_IVPT_design |
| R15_chromanol_Me9_Me10 | tgfb1 | green | 1.552 | 208.257 | none_detected | none_detected | ready_for_IVRT_IVPT_design |
| R15_chromanol_Me9_Me10 | tyr | green | 1.552 | 208.257 | none_detected | none_detected | ready_for_IVRT_IVPT_design |
| R15_chromanol_Me6_Me9 | tyr | green | 1.552 | 208.257 | none_detected | none_detected | ready_for_IVRT_IVPT_design |
| R15_chromanol_Me6_Me9 | dct | green | 1.552 | 208.257 | none_detected | none_detected | ready_for_IVRT_IVPT_design |
| R15_chromanol_Me9_Me10 | dct | green | 1.552 | 208.257 | none_detected | none_detected | ready_for_IVRT_IVPT_design |
| R15_chromanol_Me6_Me10 | tyr | green | 1.552 | 208.257 | none_detected | none_detected | ready_for_IVRT_IVPT_design |
| R15_chromanol_Me6_Me10 | dct | green | 1.552 | 208.257 | none_detected | none_detected | ready_for_IVRT_IVPT_design |
| NPC323980 |  | green | 2.089 | 174.284 | none_detected | none_detected | ready_for_IVRT_IVPT_design |
| NPC314289 |  | green | 1.184 | 132.203 | none_detected | none_detected | ready_for_IVRT_IVPT_design |
| NPC325130 |  | green | 1.184 | 144.214 | none_detected | none_detected | ready_for_IVRT_IVPT_design |
| NPC77156 |  | green | 1.071 | 170.208 | none_detected | none_detected | ready_for_IVRT_IVPT_design |
| NPC33067 |  | green | 1.08 | 142.198 | none_detected | none_detected | ready_for_IVRT_IVPT_design |
| NPC475968 |  | green | 1.943 | 256.386 | none_detected | none_detected | ready_for_IVRT_IVPT_design |
| NPC184593 |  | green | 1.405 | 118.176 | none_detected | none_detected | ready_for_IVRT_IVPT_design |
| NPC329253 |  | green | 2.987 | 238.371 | none_detected | none_detected | ready_for_IVRT_IVPT_design |
| NPC196715 |  | green | 2.987 | 238.371 | none_detected | none_detected | ready_for_IVRT_IVPT_design |
| NPC261839 |  | green | 2.281 | 284.396 | none_detected | none_detected | ready_for_IVRT_IVPT_design |
| NPC168128 |  | green | 1.203 | 183.295 | none_detected | none_detected | ready_for_IVRT_IVPT_design |
| NPC329473 |  | green | 2.345 | 234.387 | none_detected | none_detected | ready_for_IVRT_IVPT_design |
| NPC228980 |  | green | 2.345 | 234.387 | none_detected | none_detected | ready_for_IVRT_IVPT_design |
| NPC249078 |  | green | 2.725 | 238.371 | none_detected | none_detected | ready_for_IVRT_IVPT_design |
| NPC302293 |  | green | 1.695 | 242.359 | none_detected | none_detected | ready_for_IVRT_IVPT_design |
| NPC195282 |  | green | 2.725 | 238.371 | none_detected | none_detected | ready_for_IVRT_IVPT_design |
| NPC254230 |  | green | 1.201 | 183.295 | none_detected | none_detected | ready_for_IVRT_IVPT_design |
| NPC42783 |  | green | 2.482 | 188.311 | none_detected | none_detected | ready_for_IVRT_IVPT_design |
| NPC193781 |  | green | 1.696 | 254.37 | none_detected | none_detected | ready_for_IVRT_IVPT_design |
| NPC107271 |  | green | 1.958 | 254.37 | none_detected | none_detected | ready_for_IVRT_IVPT_design |
| NPC241081 |  | green | 2.722 | 308.462 | none_detected | none_detected | ready_for_IVRT_IVPT_design |

## Curator Rule

- `green`: topical lead paper main table에 둘 수 있지만 여전히 in-silico pre-gate다.
- `yellow`: OECD TG497/ICH S10/CRO assay plan을 같이 적고 강한 safety claim을 피한다.
- `red`: 외용 lead claim에서 제외하거나 구조 수정 후보로만 둔다.

```
### docs/PERTURBATION_BIOLOGY_GATE.md tail -100

```text
# Perturbation Biology Gate

- timestamp: `2026-05-06T12:46:32+09:00`
- target_rows: `32`
- priority_counts: `{'high': 2, 'review': 12, 'low': 18}`
- purpose: direct binding 후보를 실제 피부 cell phenotype/perturbation evidence와 연결할 수 있는지 평가한다.

## Priority Targets

| target | priority | cells | target gate | high-confidence pairs | next |
|---|---|---|---|---:|---|
| dct | high | melanocyte | green | 2 | connect candidate to LINCS/Geneformer/scGPT or wet-lab phenotype endpoint |
| tyr | high | melanocyte | green | 2 | connect candidate to LINCS/Geneformer/scGPT or wet-lab phenotype endpoint |
| ar | review | dermal_papilla_cell;hair_follicle_keratinocyte;immune_cell;keratinocyte;sebocyte | green | 0 | collect cell-type perturbation evidence before strong target claim |
| ctgf | review | dermal_fibroblast | green | 0 | collect cell-type perturbation evidence before strong target claim |
| lox | review | dermal_fibroblast | green | 0 | collect cell-type perturbation evidence before strong target claim |
| mc1r | review | melanocyte | green | 0 | collect cell-type perturbation evidence before strong target claim |
| mmp1 | review | dermal_fibroblast;keratinocyte | green | 0 | collect cell-type perturbation evidence before strong target claim |
| nr3c1 | review | melanocyte | green | 0 | collect cell-type perturbation evidence before strong target claim |
| piezo1 | review | dermal_papilla_cell;hair_follicle_keratinocyte | green | 0 | collect cell-type perturbation evidence before strong target claim |
| rarg | review | immune_cell;keratinocyte;sebocyte | green | 0 | collect cell-type perturbation evidence before strong target claim |
| srd5a1 | review | dermal_papilla_cell;hair_follicle_keratinocyte | green | 0 | collect cell-type perturbation evidence before strong target claim |
| srd5a2 | review | dermal_papilla_cell;hair_follicle_keratinocyte;immune_cell;keratinocyte;sebocyte | green | 0 | collect cell-type perturbation evidence before strong target claim |
| tgfb1 | review | dermal_fibroblast | yellow | 2 | collect cell-type perturbation evidence before strong target claim |
| tyrp1 | review | melanocyte | green | 0 | collect cell-type perturbation evidence before strong target claim |
| col1a1 | low | dermal_fibroblast;keratinocyte | yellow | 0 | do not prioritize virtual-cell follow-up yet |
| ctnnb1 | low | dermal_fibroblast;dermal_papilla_cell;hair_follicle_keratinocyte | yellow | 0 | do not prioritize virtual-cell follow-up yet |
| f2rl1 | low | melanocyte | yellow | 0 | do not prioritize virtual-cell follow-up yet |
| fgf2 | low | dermal_fibroblast | yellow | 0 | do not prioritize virtual-cell follow-up yet |
| jun | low | dermal_fibroblast;keratinocyte | yellow | 0 | do not prioritize virtual-cell follow-up yet |
| mitf | low | melanocyte | yellow | 0 | do not prioritize virtual-cell follow-up yet |
| mmp3 | low | dermal_fibroblast;keratinocyte | red | 0 | do not prioritize virtual-cell follow-up yet |
| mmp9 | low | dermal_fibroblast;keratinocyte | red | 0 | do not prioritize virtual-cell follow-up yet |
| mylk | low | dermal_papilla_cell;hair_follicle_keratinocyte | yellow | 0 | do not prioritize virtual-cell follow-up yet |
| nlrp3 | low | immune_cell;keratinocyte;sebocyte | red | 0 | do not prioritize virtual-cell follow-up yet |
| ptgdr2 | low | dermal_papilla_cell;hair_follicle_keratinocyte | red | 0 | do not prioritize virtual-cell follow-up yet |

## Curator Rule

- `high` target은 cofold/MD 결과를 wet-lab phenotype 또는 perturbation signature plan과 연결한다.
- `review` target은 direct binding claim보다 hypothesis 수준으로 낮춘다.
- `low` target은 heavy compute보다 target evidence 보강이 먼저다.

```
### docs/HYDRATION_KINETICS_GATE.md tail -100

```text
# Hydration and Kinetics Gate

- timestamp: `2026-05-06T12:46:33+09:00`
- rows: `32`
- counts: `{'hydration_priority': 32, 'residence_proxy': 6}`
- purpose: RMSD 안정성만으로는 부족한 water displacement/residence-time follow-up 우선순위를 정한다.

## Top Follow-ups

| target | compound | hydration | residence | ns | RMSD max | next |
|---|---|---|---|---:|---:|---|
| dct | R15_chromanol_Cl_pos9 | WaterKit_or_GIST_priority | residence_time_proxy_candidate | 100.0 | 1.13 | consider SMD/tauRAMD-style unbinding proxy after 100 ns anchor summary |
| tyr | R15_chromanol | WaterKit_or_GIST_priority | residence_time_proxy_candidate | 100.0 | 0.62 | consider SMD/tauRAMD-style unbinding proxy after 100 ns anchor summary |
| tgfb1 | R15_chromanol_Me6_Me9 | WaterKit_or_GIST_priority | residence_time_proxy_candidate | 60.0 | 0.72 | consider SMD/tauRAMD-style unbinding proxy after 100 ns anchor summary |
| dct | R15_chromanol_Cl_pos6 | WaterKit_or_GIST_priority | residence_time_proxy_candidate | 60.0 | 0.72 | consider SMD/tauRAMD-style unbinding proxy after 100 ns anchor summary |
| tyr | R15_chromanol_Cl_pos6 | WaterKit_or_GIST_priority | residence_time_proxy_candidate | 100.0 | 0.62 | consider SMD/tauRAMD-style unbinding proxy after 100 ns anchor summary |
| tgfb1 | R15_chromanol_Cl_pos6 | WaterKit_or_GIST_priority | residence_time_proxy_candidate | 60.0 | 1.22 | consider SMD/tauRAMD-style unbinding proxy after 100 ns anchor summary |
| tgfb1 | R15_chromanol_Cl_pos9 | WaterKit_or_GIST_priority | stability_only_candidate | 100.0 | 0.69 | run hydration-site map before substituent optimization |
| dct | R15_chromanol | WaterKit_or_GIST_priority | stability_only_candidate | 100.0 | 1.13 | run hydration-site map before substituent optimization |
| tgfb1 | R15_chromanol_Me9_Me10 | WaterKit_or_GIST_priority | stability_only_candidate | 60.0 | 0.7 | run hydration-site map before substituent optimization |
| tgfb1 | R15_chromanol | WaterKit_or_GIST_priority | stability_only_candidate | 100.0 | 0.69 | run hydration-site map before substituent optimization |
| tgfb1 | R15_chromanol_Me6_Me10 | WaterKit_or_GIST_priority | stability_only_candidate | 60.0 | 1.18 | run hydration-site map before substituent optimization |
| tgfb1 | R15_chromanol_Cl_pos10 | WaterKit_or_GIST_priority | stability_only_candidate | 60.0 | 1.21 | run hydration-site map before substituent optimization |
| ptgs2 | R15_chromanol | WaterKit_or_GIST_priority | not_ready | 0.0 |  | run hydration-site map before substituent optimization |
| tyr | R15_chromanol_Cl_pos9 | WaterKit_or_GIST_priority | not_ready | 0.0 |  | run hydration-site map before substituent optimization |
| dct | R15_chromanol_Cl_pos10 | WaterKit_or_GIST_priority | not_ready | 0.0 |  | run hydration-site map before substituent optimization |
| tyr | R15_chromanol_Cl_pos10 | WaterKit_or_GIST_priority | not_ready | 0.0 |  | run hydration-site map before substituent optimization |
| tyrp1 | R15_chromanol | WaterKit_or_GIST_priority | not_ready | 0.0 |  | run hydration-site map before substituent optimization |
| tyr | R15_chromanol_Me9_Me10 | WaterKit_or_GIST_priority | not_ready | 0.0 |  | run hydration-site map before substituent optimization |
| tyr | R15_chromanol_Me6_Me9 | WaterKit_or_GIST_priority | not_ready | 0.0 |  | run hydration-site map before substituent optimization |
| dct | R15_chromanol_Me6_Me9 | WaterKit_or_GIST_priority | not_ready | 0.0 |  | run hydration-site map before substituent optimization |
| dct | R15_chromanol_Me9_Me10 | WaterKit_or_GIST_priority | not_ready | 0.0 |  | run hydration-site map before substituent optimization |
| tyr | R15_chromanol_Me6_Me10 | WaterKit_or_GIST_priority | not_ready | 0.0 |  | run hydration-site map before substituent optimization |
| dct | R15_chromanol_Me6_Me10 | WaterKit_or_GIST_priority | not_ready | 0.0 |  | run hydration-site map before substituent optimization |
| mmp1 | R15_chromanol | WaterKit_or_GIST_priority | not_ready | 0.0 |  | run hydration-site map before substituent optimization |
| sirt1 | R15_chromanol | WaterKit_or_GIST_priority | not_ready | 0.0 |  | run hydration-site map before substituent optimization |

## Curator Rule

- hydration priority 후보는 substituent optimization 전에 WaterKit/GIST-lite 계층을 고려한다.
- residence proxy 후보는 60-100 ns 안정성 이후에만 SMD/tauRAMD-style 후속으로 올린다.
- 이 파일은 실제 kinetics claim이 아니라 후속 실험/계산 우선순위다.

```
### docs/ULTRA_LARGE_SCREENING_ROADMAP.md tail -100

```text
# Ultra-large Screening Roadmap

- timestamp: `2026-05-06T12:46:33+09:00`
- rows: `50`
- purpose: NPASS-scale local screen을 ZINC/Enamine REAL급 ultra-large active-learning campaign으로 확장하기 위한 단계별 큐다.

## Stages

| stage | target | scope | nominal size | status | queue rule |
|---|---|---|---:|---|---|
| stage0_local_surrogate | ctgf | local NPASS/R15/R16 candidate pool | 672 | already available | refresh active-learning surrogate and remove duplicate labeled pairs |
| stage0_local_surrogate | lox | local NPASS/R15/R16 candidate pool | 672 | already available | refresh active-learning surrogate and remove duplicate labeled pairs |
| stage0_local_surrogate | mmp1 | local NPASS/R15/R16 candidate pool | 672 | already available | refresh active-learning surrogate and remove duplicate labeled pairs |
| stage0_local_surrogate | dct | local NPASS/R15/R16 candidate pool | 672 | already available | refresh active-learning surrogate and remove duplicate labeled pairs |
| stage0_local_surrogate | mc1r | local NPASS/R15/R16 candidate pool | 672 | already available | refresh active-learning surrogate and remove duplicate labeled pairs |
| stage0_local_surrogate | nr3c1 | local NPASS/R15/R16 candidate pool | 672 | already available | refresh active-learning surrogate and remove duplicate labeled pairs |
| stage1_orderable_subset | ctgf | ZINC/Enamine/REAL purchasable subset | 50000 | future lightweight download | screen descriptors and apply synthesis/dermal gates before docking |
| stage1_orderable_subset | lox | ZINC/Enamine/REAL purchasable subset | 50000 | future lightweight download | screen descriptors and apply synthesis/dermal gates before docking |
| stage1_orderable_subset | mmp1 | ZINC/Enamine/REAL purchasable subset | 50000 | future lightweight download | screen descriptors and apply synthesis/dermal gates before docking |
| stage1_orderable_subset | dct | ZINC/Enamine/REAL purchasable subset | 50000 | future lightweight download | screen descriptors and apply synthesis/dermal gates before docking |
| stage1_orderable_subset | mc1r | ZINC/Enamine/REAL purchasable subset | 50000 | future lightweight download | screen descriptors and apply synthesis/dermal gates before docking |
| stage1_orderable_subset | nr3c1 | ZINC/Enamine/REAL purchasable subset | 50000 | future lightweight download | screen descriptors and apply synthesis/dermal gates before docking |
| stage2_active_docking | ctgf | active-learning selected purchasable compounds | 5000 | future CPU/GPU window | dock/cofold only top acquisition batches for green targets |
| stage2_active_docking | lox | active-learning selected purchasable compounds | 5000 | future CPU/GPU window | dock/cofold only top acquisition batches for green targets |
| stage2_active_docking | mmp1 | active-learning selected purchasable compounds | 5000 | future CPU/GPU window | dock/cofold only top acquisition batches for green targets |
| stage2_active_docking | dct | active-learning selected purchasable compounds | 5000 | future CPU/GPU window | dock/cofold only top acquisition batches for green targets |
| stage2_active_docking | mc1r | active-learning selected purchasable compounds | 5000 | future CPU/GPU window | dock/cofold only top acquisition batches for green targets |
| stage2_active_docking | nr3c1 | active-learning selected purchasable compounds | 5000 | future CPU/GPU window | dock/cofold only top acquisition batches for green targets |
| stage3_synthon_space | ctgf | synthon/V-SYNTHES style enumerated space | 1000000 | future design campaign | enumerate analogs around chromanol/pterocarpan motifs |
| stage3_synthon_space | lox | synthon/V-SYNTHES style enumerated space | 1000000 | future design campaign | enumerate analogs around chromanol/pterocarpan motifs |
| stage3_synthon_space | mmp1 | synthon/V-SYNTHES style enumerated space | 1000000 | future design campaign | enumerate analogs around chromanol/pterocarpan motifs |
| stage3_synthon_space | dct | synthon/V-SYNTHES style enumerated space | 1000000 | future design campaign | enumerate analogs around chromanol/pterocarpan motifs |
| stage3_synthon_space | mc1r | synthon/V-SYNTHES style enumerated space | 1000000 | future design campaign | enumerate analogs around chromanol/pterocarpan motifs |
| stage3_synthon_space | nr3c1 | synthon/V-SYNTHES style enumerated space | 1000000 | future design campaign | enumerate analogs around chromanol/pterocarpan motifs |
| stage4_wetlab_shortlist | ctgf | CRO-orderable shortlist | 30 | after cofold/MD/safety | single-point phenotype or IVRT/IVPT confirmation |
| stage4_wetlab_shortlist | lox | CRO-orderable shortlist | 30 | after cofold/MD/safety | single-point phenotype or IVRT/IVPT confirmation |
| stage4_wetlab_shortlist | mmp1 | CRO-orderable shortlist | 30 | after cofold/MD/safety | single-point phenotype or IVRT/IVPT confirmation |
| stage4_wetlab_shortlist | dct | CRO-orderable shortlist | 30 | after cofold/MD/safety | single-point phenotype or IVRT/IVPT confirmation |
| stage4_wetlab_shortlist | mc1r | CRO-orderable shortlist | 30 | after cofold/MD/safety | single-point phenotype or IVRT/IVPT confirmation |
| stage4_wetlab_shortlist | nr3c1 | CRO-orderable shortlist | 30 | after cofold/MD/safety | single-point phenotype or IVRT/IVPT confirmation |
| stage0_top_active_learning_seed | dct | npass_xtb_best_cross_target | 1 | acquisition=0.6534 | seed future purchasable analog search around NPC243469 |
| stage0_top_active_learning_seed | dct | npass_xtb_best_cross_target | 1 | acquisition=0.6534 | seed future purchasable analog search around NPC194985 |
| stage0_top_active_learning_seed | dct | npass_xtb_best_cross_target | 1 | acquisition=0.6534 | seed future purchasable analog search around NPC196715 |
| stage0_top_active_learning_seed | dct | npass_xtb_best_cross_target | 1 | acquisition=0.6534 | seed future purchasable analog search around NPC261839 |
| stage0_top_active_learning_seed | dct | npass_xtb_best_cross_target | 1 | acquisition=0.6534 | seed future purchasable analog search around NPC469970 |
| stage0_top_active_learning_seed | ctgf | npass_xtb_best_cross_target | 1 | acquisition=0.6378 | seed future purchasable analog search around NPC243469 |
| stage0_top_active_learning_seed | lox | npass_xtb_best_cross_target | 1 | acquisition=0.6378 | seed future purchasable analog search around NPC243469 |
| stage0_top_active_learning_seed | mmp1 | npass_xtb_best_cross_target | 1 | acquisition=0.6378 | seed future purchasable analog search around NPC243469 |
| stage0_top_active_learning_seed | mc1r | npass_xtb_best_cross_target | 1 | acquisition=0.6378 | seed future purchasable analog search around NPC243469 |
| stage0_top_active_learning_seed | nr3c1 | npass_xtb_best_cross_target | 1 | acquisition=0.6378 | seed future purchasable analog search around NPC243469 |

## Curator Rule

- 현재 CPU/GPU 포화 상태에서는 stage0 문서화만 수행한다.
- stage1 이상은 외부 library download/라이선스/저장공간을 확인한 뒤 별도 큐로 올린다.
- ultra-large campaign은 full docking이 아니라 active-learning 압축 screen으로만 설계한다.

```
### docs/MODEL_VALIDATION_UNCERTAINTY_GATE.md tail -100

```text
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

```
### docs/PHENOMICS_SIGNATURE_GATE.md tail -100

```text
# Phenomics Signature Gate

- timestamp: `2026-05-06T12:46:34+09:00`
- rows: `752`
- gate_counts: `{'priority_cell_painting': 278, 'phenomics_with_safety_counterscreen': 57, 'reference_signature_lookup': 417, 'hold_safety_first': 0}`
- purpose: docking/MD 후보를 Cell Painting, high-content imaging, disease-cell phenotype 후속으로 연결한다.

## Priority Rows

| candidate | target | gate | disease context | cell model | phenotype anchor | next |
|---|---|---|---|---|---|---|
| R15_chromanol_Cl_pos9 | tgfb1 | priority_cell_painting | scar_fibrosis | primary dermal fibroblast | COL1A1/ACTA2 morphology + Cell Painting | queue CRO/in-house Cell Painting with disease-specific endpoint counter-readout |
| NPC243469 | dct | priority_cell_painting | pigmentation | human melanocyte or B16F10 | melanin content + DCT/TYR pathway imaging | queue CRO/in-house Cell Painting with disease-specific endpoint counter-readout |
| NPC194985 | dct | priority_cell_painting | pigmentation | human melanocyte or B16F10 | melanin content + DCT/TYR pathway imaging | queue CRO/in-house Cell Painting with disease-specific endpoint counter-readout |
| NPC196715 | dct | priority_cell_painting | pigmentation | human melanocyte or B16F10 | melanin content + DCT/TYR pathway imaging | queue CRO/in-house Cell Painting with disease-specific endpoint counter-readout |
| NPC261839 | dct | priority_cell_painting | pigmentation | human melanocyte or B16F10 | melanin content + DCT/TYR pathway imaging | queue CRO/in-house Cell Painting with disease-specific endpoint counter-readout |
| NPC469970 | dct | priority_cell_painting | pigmentation | human melanocyte or B16F10 | melanin content + DCT/TYR pathway imaging | queue CRO/in-house Cell Painting with disease-specific endpoint counter-readout |
| NPC243469 | ctgf | priority_cell_painting | scar_fibrosis | primary dermal fibroblast | ECM-remodeling morphology + Cell Painting | queue CRO/in-house Cell Painting with disease-specific endpoint counter-readout |
| NPC243469 | tyrp1 | priority_cell_painting | pigmentation | human melanocyte or B16F10 | melanin content + organelle morphology | queue CRO/in-house Cell Painting with disease-specific endpoint counter-readout |
| NPC194985 | ctgf | priority_cell_painting | scar_fibrosis | primary dermal fibroblast | ECM-remodeling morphology + Cell Painting | queue CRO/in-house Cell Painting with disease-specific endpoint counter-readout |
| NPC194985 | tyrp1 | priority_cell_painting | pigmentation | human melanocyte or B16F10 | melanin content + organelle morphology | queue CRO/in-house Cell Painting with disease-specific endpoint counter-readout |
| NPC196715 | ctgf | priority_cell_painting | scar_fibrosis | primary dermal fibroblast | ECM-remodeling morphology + Cell Painting | queue CRO/in-house Cell Painting with disease-specific endpoint counter-readout |
| NPC196715 | tyrp1 | priority_cell_painting | pigmentation | human melanocyte or B16F10 | melanin content + organelle morphology | queue CRO/in-house Cell Painting with disease-specific endpoint counter-readout |
| NPC261839 | ctgf | priority_cell_painting | scar_fibrosis | primary dermal fibroblast | ECM-remodeling morphology + Cell Painting | queue CRO/in-house Cell Painting with disease-specific endpoint counter-readout |
| NPC261839 | tyrp1 | priority_cell_painting | pigmentation | human melanocyte or B16F10 | melanin content + organelle morphology | queue CRO/in-house Cell Painting with disease-specific endpoint counter-readout |
| NPC469970 | ctgf | priority_cell_painting | scar_fibrosis | primary dermal fibroblast | ECM-remodeling morphology + Cell Painting | queue CRO/in-house Cell Painting with disease-specific endpoint counter-readout |
| NPC469970 | tyrp1 | priority_cell_painting | pigmentation | human melanocyte or B16F10 | melanin content + organelle morphology | queue CRO/in-house Cell Painting with disease-specific endpoint counter-readout |
| R15_chromanol_Me6_Me9 | tgfb1 | priority_cell_painting | scar_fibrosis | primary dermal fibroblast | COL1A1/ACTA2 morphology + Cell Painting | queue CRO/in-house Cell Painting with disease-specific endpoint counter-readout |
| NPC281540 | dct | priority_cell_painting | pigmentation | human melanocyte or B16F10 | melanin content + DCT/TYR pathway imaging | queue CRO/in-house Cell Painting with disease-specific endpoint counter-readout |
| NPC257680 | dct | priority_cell_painting | pigmentation | human melanocyte or B16F10 | melanin content + DCT/TYR pathway imaging | queue CRO/in-house Cell Painting with disease-specific endpoint counter-readout |
| NPC475968 | dct | priority_cell_painting | pigmentation | human melanocyte or B16F10 | melanin content + DCT/TYR pathway imaging | queue CRO/in-house Cell Painting with disease-specific endpoint counter-readout |
| NPC84346 | dct | priority_cell_painting | pigmentation | human melanocyte or B16F10 | melanin content + DCT/TYR pathway imaging | queue CRO/in-house Cell Painting with disease-specific endpoint counter-readout |
| NPC474914 | dct | priority_cell_painting | pigmentation | human melanocyte or B16F10 | melanin content + DCT/TYR pathway imaging | queue CRO/in-house Cell Painting with disease-specific endpoint counter-readout |
| NPC324003 | dct | priority_cell_painting | pigmentation | human melanocyte or B16F10 | melanin content + DCT/TYR pathway imaging | queue CRO/in-house Cell Painting with disease-specific endpoint counter-readout |
| NPC479534 | dct | priority_cell_painting | pigmentation | human melanocyte or B16F10 | melanin content + DCT/TYR pathway imaging | queue CRO/in-house Cell Painting with disease-specific endpoint counter-readout |
| NPC249078 | dct | priority_cell_painting | pigmentation | human melanocyte or B16F10 | melanin content + DCT/TYR pathway imaging | queue CRO/in-house Cell Painting with disease-specific endpoint counter-readout |
| NPC302293 | dct | priority_cell_painting | pigmentation | human melanocyte or B16F10 | melanin content + DCT/TYR pathway imaging | queue CRO/in-house Cell Painting with disease-specific endpoint counter-readout |
| NPC327468 | dct | priority_cell_painting | pigmentation | human melanocyte or B16F10 | melanin content + DCT/TYR pathway imaging | queue CRO/in-house Cell Painting with disease-specific endpoint counter-readout |
| NPC193781 | dct | priority_cell_painting | pigmentation | human melanocyte or B16F10 | melanin content + DCT/TYR pathway imaging | queue CRO/in-house Cell Painting with disease-specific endpoint counter-readout |
| NPC241081 | dct | priority_cell_painting | pigmentation | human melanocyte or B16F10 | melanin content + DCT/TYR pathway imaging | queue CRO/in-house Cell Painting with disease-specific endpoint counter-readout |
| NPC251201 | dct | priority_cell_painting | pigmentation | human melanocyte or B16F10 | melanin content + DCT/TYR pathway imaging | queue CRO/in-house Cell Painting with disease-specific endpoint counter-readout |
| NPC195282 | dct | priority_cell_painting | pigmentation | human melanocyte or B16F10 | melanin content + DCT/TYR pathway imaging | queue CRO/in-house Cell Painting with disease-specific endpoint counter-readout |
| NPC179262 | dct | priority_cell_painting | pigmentation | human melanocyte or B16F10 | melanin content + DCT/TYR pathway imaging | queue CRO/in-house Cell Painting with disease-specific endpoint counter-readout |
| NPC306634 | dct | priority_cell_painting | pigmentation | human melanocyte or B16F10 | melanin content + DCT/TYR pathway imaging | queue CRO/in-house Cell Painting with disease-specific endpoint counter-readout |
| NPC273290 | dct | priority_cell_painting | pigmentation | human melanocyte or B16F10 | melanin content + DCT/TYR pathway imaging | queue CRO/in-house Cell Painting with disease-specific endpoint counter-readout |
| NPC329253 | dct | priority_cell_painting | pigmentation | human melanocyte or B16F10 | melanin content + DCT/TYR pathway imaging | queue CRO/in-house Cell Painting with disease-specific endpoint counter-readout |

## Curator Rule

- `priority_cell_painting`: 더 큰 GPU 반복보다 CRO/in-house phenotype assay 설계를 우선 고려한다.
- `phenomics_with_safety_counterscreen`: viability, irritation, photosafety counterscreen 없이는 lead claim을 피한다.
- `reference_signature_lookup`: JUMP/CPJUMP/Cell Painting Gallery 유사 signature 확인 전에는 MOA claim을 하지 않는다.
- `hold_safety_first`: 안전성 alert 해결 전에는 phenomics spend를 보류한다.

```
### docs/DEVELOPABILITY_CMC_GATE.md tail -100

```text
# Developability CMC Gate

- timestamp: `2026-05-06T12:46:34+09:00`
- rows: `112`
- gate_counts: `{'green': 34, 'yellow': 78, 'red': 0}`
- purpose: hit/lead 후보를 solubility, stability, excipient compatibility, solid-form risk, scale-up risk 관점으로 조기 제한한다.

## Top Rows

| candidate | target | gate | cLogP | logS proxy | alerts | next |
|---|---|---|---:|---:|---|---|
| NPC42783 |  | green | 2.482 | -1.911 | high_flexibility_impurity_method_watch | advance with solubility, pH stability, and vehicle compatibility screen |
| NPC323980 |  | green | 2.089 | -1.906 | none_detected | advance with solubility, pH stability, and vehicle compatibility screen |
| NPC184593 |  | green | 1.405 | -1.194 | volatile_or_retention_risk | advance with solubility, pH stability, and vehicle compatibility screen |
| NPC249078 |  | green | 2.725 | -3.034 | none_detected | advance with solubility, pH stability, and vehicle compatibility screen |
| NPC314289 |  | green | 1.184 | -1.076 | none_detected | advance with solubility, pH stability, and vehicle compatibility screen |
| NPC302293 |  | green | 1.695 | -2.345 | none_detected | advance with solubility, pH stability, and vehicle compatibility screen |
| NPC193781 |  | green | 1.696 | -2.485 | none_detected | advance with solubility, pH stability, and vehicle compatibility screen |
| NPC325130 |  | green | 1.184 | -1.414 | none_detected | advance with solubility, pH stability, and vehicle compatibility screen |
| NPC241081 |  | green | 2.722 | -3.467 | none_detected | advance with solubility, pH stability, and vehicle compatibility screen |
| NPC195282 |  | green | 2.725 | -3.034 | none_detected | advance with solubility, pH stability, and vehicle compatibility screen |
| NPC475968 |  | green | 1.943 | -2.522 | none_detected | advance with solubility, pH stability, and vehicle compatibility screen |
| NPC179262 |  | green | 3.353 | -4.363 | none_detected | advance with solubility, pH stability, and vehicle compatibility screen |
| NPC77156 |  | green | 1.071 | -1.57 | none_detected | advance with solubility, pH stability, and vehicle compatibility screen |
| NPC329253 |  | green | 2.987 | -3.2 | none_detected | advance with solubility, pH stability, and vehicle compatibility screen |
| NPC59871 |  | green | 2.708 | -4.361 | none_detected | advance with solubility, pH stability, and vehicle compatibility screen |
| NPC196715 |  | green | 2.987 | -3.134 | none_detected | advance with solubility, pH stability, and vehicle compatibility screen |
| NPC107271 |  | green | 1.958 | -2.651 | none_detected | advance with solubility, pH stability, and vehicle compatibility screen |
| NPC33067 |  | green | 1.08 | -1.402 | none_detected | advance with solubility, pH stability, and vehicle compatibility screen |
| NPC261839 |  | green | 2.281 | -2.974 | none_detected | advance with solubility, pH stability, and vehicle compatibility screen |
| NPC168128 |  | green | 1.203 | -1.668 | none_detected | advance with solubility, pH stability, and vehicle compatibility screen |
| NPC192944 |  | green | 1.053 | -2.701 | none_detected | advance with solubility, pH stability, and vehicle compatibility screen |
| NPC254230 |  | green | 1.201 | -1.733 | none_detected | advance with solubility, pH stability, and vehicle compatibility screen |
| NPC25947 |  | green | 3.31 | -4.635 | none_detected | advance with solubility, pH stability, and vehicle compatibility screen |
| NPC329473 |  | green | 2.345 | -2.771 | none_detected | advance with solubility, pH stability, and vehicle compatibility screen |
| NPC228980 |  | green | 2.345 | -2.771 | none_detected | advance with solubility, pH stability, and vehicle compatibility screen |
| R15_chromanol_Me6_Me9 | tgfb1 | green | 1.552 | -2.339 | catechol_or_resorcinol;phenol | advance with solubility, pH stability, and vehicle compatibility screen |
| R15_chromanol_Me6_Me10 | tgfb1 | green | 1.552 | -2.339 | catechol_or_resorcinol;phenol | advance with solubility, pH stability, and vehicle compatibility screen |
| R15_chromanol_Me9_Me10 | tgfb1 | green | 1.552 | -2.339 | catechol_or_resorcinol;phenol | advance with solubility, pH stability, and vehicle compatibility screen |
| R15_chromanol_Me9_Me10 | tyr | green | 1.552 | -2.339 | catechol_or_resorcinol;phenol | advance with solubility, pH stability, and vehicle compatibility screen |
| R15_chromanol_Me6_Me9 | tyr | green | 1.552 | -2.339 | catechol_or_resorcinol;phenol | advance with solubility, pH stability, and vehicle compatibility screen |
| R15_chromanol_Me6_Me9 | dct | green | 1.552 | -2.339 | catechol_or_resorcinol;phenol | advance with solubility, pH stability, and vehicle compatibility screen |
| R15_chromanol_Me9_Me10 | dct | green | 1.552 | -2.339 | catechol_or_resorcinol;phenol | advance with solubility, pH stability, and vehicle compatibility screen |
| R15_chromanol_Me6_Me10 | tyr | green | 1.552 | -2.339 | catechol_or_resorcinol;phenol | advance with solubility, pH stability, and vehicle compatibility screen |
| R15_chromanol_Me6_Me10 | dct | green | 1.552 | -2.339 | catechol_or_resorcinol;phenol | advance with solubility, pH stability, and vehicle compatibility screen |
| NPC213764 |  | yellow | 0.531 | -0.577 | volatile_or_retention_risk | run CMC de-risking before lead claim: kinetic solubility, pH stability, excipient compatibility |

## Curator Rule

- `green`: lead table에 둘 수 있으나 solubility/pH stability/vehicle compatibility는 pending으로 명시한다.
- `yellow`: 더 큰 GPU 확장 전에 CMC de-risking 또는 구조 수정 후보로 보낸다.
- `red`: manuscript lead claim에서 제외하고 failure-mode 또는 redesign 후보로만 쓴다.

```
### docs/IP_FTO_WATCHLIST.md tail -100

```text
# IP FTO Watchlist

- timestamp: `2026-05-06T12:46:35+09:00`
- rows: `752`
- risk_counts: `{'high_review': 0, 'medium_review': 11, 'baseline_watch': 741}`
- manual_review_template: `data/ip_fto_manual_review_template.csv`
- purpose: local Tanimoto novelty와 실제 patent/FTO 검토를 분리해, 신규성/상업성 claim을 과장하지 않는다.

## Review Queue

| candidate | target | risk | novelty | scaffold | query terms |
|---|---|---|---|---|---|
| NPC23134 |  | medium_review | close_series | C1CCOCC1 | NPC23134 OR C1CCOCC1 OR skin topical small molecule |
| NPC306277 |  | medium_review | close_series | acyclic | NPC306277 OR acyclic OR skin topical small molecule |
| R15_chromanol_Cl_pos10 | tgfb1 | medium_review | locally_distinct | c1ccc2c(c1)CCCO2 | R15_chromanol_Cl_pos10 OR c1ccc2c(c1)CCCO2 OR chromanol OR benzopyran OR topical dermatology OR halogenated analog Markush OR scar OR fibrosis OR collagen OR TGF beta |
| R15_chromanol_Cl_pos10 | dct | medium_review | locally_distinct | c1ccc2c(c1)CCCO2 | R15_chromanol_Cl_pos10 OR c1ccc2c(c1)CCCO2 OR chromanol OR benzopyran OR topical dermatology OR halogenated analog Markush OR melanin OR tyrosinase OR hyperpigmentation |
| R15_chromanol_Cl_pos10 | tyr | medium_review | locally_distinct | c1ccc2c(c1)CCCO2 | R15_chromanol_Cl_pos10 OR c1ccc2c(c1)CCCO2 OR chromanol OR benzopyran OR topical dermatology OR halogenated analog Markush OR melanin OR tyrosinase OR hyperpigmentation |
| R15_chromanol_Cl_pos9 | tgfb1 | medium_review | locally_distinct | c1ccc2c(c1)CCCO2 | R15_chromanol_Cl_pos9 OR c1ccc2c(c1)CCCO2 OR chromanol OR benzopyran OR topical dermatology OR halogenated analog Markush OR scar OR fibrosis OR collagen OR TGF beta |
| R15_chromanol_Cl_pos9 | dct | medium_review | locally_distinct | c1ccc2c(c1)CCCO2 | R15_chromanol_Cl_pos9 OR c1ccc2c(c1)CCCO2 OR chromanol OR benzopyran OR topical dermatology OR halogenated analog Markush OR melanin OR tyrosinase OR hyperpigmentation |
| R15_chromanol_Cl_pos9 | tyr | medium_review | locally_distinct | c1ccc2c(c1)CCCO2 | R15_chromanol_Cl_pos9 OR c1ccc2c(c1)CCCO2 OR chromanol OR benzopyran OR topical dermatology OR halogenated analog Markush OR melanin OR tyrosinase OR hyperpigmentation |
| R15_chromanol_Cl_pos6 | tgfb1 | medium_review | locally_distinct | c1ccc2c(c1)CCCO2 | R15_chromanol_Cl_pos6 OR c1ccc2c(c1)CCCO2 OR chromanol OR benzopyran OR topical dermatology OR halogenated analog Markush OR scar OR fibrosis OR collagen OR TGF beta |
| R15_chromanol_Cl_pos6 | dct | medium_review | locally_distinct | c1ccc2c(c1)CCCO2 | R15_chromanol_Cl_pos6 OR c1ccc2c(c1)CCCO2 OR chromanol OR benzopyran OR topical dermatology OR halogenated analog Markush OR melanin OR tyrosinase OR hyperpigmentation |
| R15_chromanol_Cl_pos6 | tyr | medium_review | locally_distinct | c1ccc2c(c1)CCCO2 | R15_chromanol_Cl_pos6 OR c1ccc2c(c1)CCCO2 OR chromanol OR benzopyran OR topical dermatology OR halogenated analog Markush OR melanin OR tyrosinase OR hyperpigmentation |
| R15_chromanol | tgfb1 | baseline_watch | locally_distinct | c1ccc2c(c1)CCCO2 | R15_chromanol OR c1ccc2c(c1)CCCO2 OR chromanol OR benzopyran OR topical dermatology OR scar OR fibrosis OR collagen OR TGF beta |
| R15_chromanol | tyr | baseline_watch | locally_distinct | c1ccc2c(c1)CCCO2 | R15_chromanol OR c1ccc2c(c1)CCCO2 OR chromanol OR benzopyran OR topical dermatology OR melanin OR tyrosinase OR hyperpigmentation |
| R15_chromanol | dct | baseline_watch | locally_distinct | c1ccc2c(c1)CCCO2 | R15_chromanol OR c1ccc2c(c1)CCCO2 OR chromanol OR benzopyran OR topical dermatology OR melanin OR tyrosinase OR hyperpigmentation |
| R15_chromanol | ptgs2 | baseline_watch | locally_distinct | c1ccc2c(c1)CCCO2 | R15_chromanol OR c1ccc2c(c1)CCCO2 OR chromanol OR benzopyran OR topical dermatology |
| R15_chromanol | sirt1 | baseline_watch | locally_distinct | c1ccc2c(c1)CCCO2 | R15_chromanol OR c1ccc2c(c1)CCCO2 OR chromanol OR benzopyran OR topical dermatology |
| R15_chromanol | tyrp1 | baseline_watch | locally_distinct | c1ccc2c(c1)CCCO2 | R15_chromanol OR c1ccc2c(c1)CCCO2 OR chromanol OR benzopyran OR topical dermatology OR melanin OR tyrosinase OR hyperpigmentation |
| R15_chromanol | ar | baseline_watch | locally_distinct | c1ccc2c(c1)CCCO2 | R15_chromanol OR c1ccc2c(c1)CCCO2 OR chromanol OR benzopyran OR topical dermatology OR androgen OR alopecia OR 5 alpha reductase |
| R15_chromanol | mmp1 | baseline_watch | locally_distinct | c1ccc2c(c1)CCCO2 | R15_chromanol OR c1ccc2c(c1)CCCO2 OR chromanol OR benzopyran OR topical dermatology OR scar OR fibrosis OR collagen OR TGF beta |
| R15_chromanol | srebp1 | baseline_watch | locally_distinct | c1ccc2c(c1)CCCO2 | R15_chromanol OR c1ccc2c(c1)CCCO2 OR chromanol OR benzopyran OR topical dermatology |
| R15_chromanol | mitf | baseline_watch | locally_distinct | c1ccc2c(c1)CCCO2 | R15_chromanol OR c1ccc2c(c1)CCCO2 OR chromanol OR benzopyran OR topical dermatology OR melanin OR tyrosinase OR hyperpigmentation |
| R15_chromanol | lox | baseline_watch | locally_distinct | c1ccc2c(c1)CCCO2 | R15_chromanol OR c1ccc2c(c1)CCCO2 OR chromanol OR benzopyran OR topical dermatology OR scar OR fibrosis OR collagen OR TGF beta |
| R15_chromanol | srd5a1 | baseline_watch | locally_distinct | c1ccc2c(c1)CCCO2 | R15_chromanol OR c1ccc2c(c1)CCCO2 OR chromanol OR benzopyran OR topical dermatology OR androgen OR alopecia OR 5 alpha reductase |
| R15_chromanol | ctgf | baseline_watch | locally_distinct | c1ccc2c(c1)CCCO2 | R15_chromanol OR c1ccc2c(c1)CCCO2 OR chromanol OR benzopyran OR topical dermatology OR scar OR fibrosis OR collagen OR TGF beta |
| R15_chromanol | srd5a2 | baseline_watch | locally_distinct | c1ccc2c(c1)CCCO2 | R15_chromanol OR c1ccc2c(c1)CCCO2 OR chromanol OR benzopyran OR topical dermatology OR androgen OR alopecia OR 5 alpha reductase |
| NPC20938 |  | baseline_watch | locally_distinct | C1CCOCC1 | NPC20938 OR C1CCOCC1 OR skin topical small molecule |
| NPC35553 |  | baseline_watch | locally_distinct | C1CCOCC1 | NPC35553 OR C1CCOCC1 OR skin topical small molecule |
| NPC120104 |  | baseline_watch | locally_distinct | C1CCOCC1 | NPC120104 OR C1CCOCC1 OR skin topical small molecule |
| NPC256808 |  | baseline_watch | locally_distinct | C1CC[C@H](O[C@@H]2C[C@@H]3CCC2C3)OC1 | NPC256808 OR C1CC[C@H](O[C@@H]2C[C@@H]3CCC2C3)OC1 OR skin topical small molecule |
| NPC251201 |  | baseline_watch | locally_distinct | C1CC[C@@H]2CC[C@H]3[C@@H]4CCCC4CC[C@@H]3C2C1 | NPC251201 OR C1CC[C@@H]2CC[C@H]3[C@@H]4CCCC4CC[C@@H]3C2C1 OR skin topical small molecule |
| NPC83285 |  | baseline_watch | locally_distinct | C1CCC(O[C@H]2CCCCO2)CC1 | NPC83285 OR C1CCC(O[C@H]2CCCCO2)CC1 OR skin topical small molecule |
| NPC196136 |  | baseline_watch | locally_distinct | C1CCC2C(C1)CC[C@H]1[C@@H]3CCCC3CC[C@H]21 | NPC196136 OR C1CCC2C(C1)CC[C@H]1[C@@H]3CCCC3CC[C@H]21 OR skin topical small molecule |
| NPC228994 |  | baseline_watch | locally_distinct | C1CCC2C(C1)CC[C@H]1[C@@H]3CCCC3CC[C@H]21 | NPC228994 OR C1CCC2C(C1)CC[C@H]1[C@@H]3CCCC3CC[C@H]21 OR skin topical small molecule |
| NPC327468 |  | baseline_watch | locally_distinct | C1CCC2C(C1)CCC1C3CCCC3CCC21 | NPC327468 OR C1CCC2C(C1)CCC1C3CCCC3CCC21 OR skin topical small molecule |
| NPC329253 |  | baseline_watch | locally_distinct | C1CC2CC3CCC(OC3)C2C1 | NPC329253 OR C1CC2CC3CCC(OC3)C2C1 OR skin topical small molecule |

## Curator Rule

- `high_review`: patent/FTO 검토 전에는 novelty, freedom-to-operate, commercial differentiation claim을 금지한다.
- `medium_review`: manuscript에는 local novelty까지만 쓰고 외부 patent search pending을 명시한다.
- `baseline_watch`: follow-up 가능하지만 composition/use/formulation claim은 수동 검토 후에만 쓴다.

```
### docs/FAIR_ASSAY_SCHEMA.md tail -100

```text
# FAIR Assay Schema

- timestamp: `2026-05-06T12:46:35+09:00`
- dictionary_csv: `pilot/cpu_meaningful/fair_assay_dictionary.csv`
- template_csv: `data/fair_assay_metadata_template.csv`
- schema_json: `data/fair_assay_schema.json`
- purpose: wet-lab/CRO 결과를 ISA/BAO/RO-Crate-ready metadata로 받아 compute loop와 논문 provenance에 재사용한다.

## Required Fields

| field | type | description |
|---|---|---|
| investigation_id | string | ISA investigation identifier |
| study_id | string | ISA study identifier or project arm |
| assay_id | string | assay run identifier |
| experiment_date | date | ISO date for experiment start |
| compound_id | string | Genesis candidate identifier |
| smiles | string | canonical or submitted SMILES |
| batch_id | string | compound batch or vendor lot |
| target_or_pathway | string | target, pathway, or phenotype axis |
| disease_context | controlled_string | scar, pigment, acne, alopecia, photoaging, or control |
| assay_type | controlled_string | qPCR, enzyme, Cell Painting, viability, IVRT, IVPT, etc. |
| cell_type_or_model | string | cell line, primary cell, organoid, skin model, or biochemical assay |
| dose | number | dose value |
| dose_unit | controlled_string | dose unit |
| timepoint | string | duration or sampling time |
| endpoint | string | measured endpoint |
| value | number | numeric readout |
| unit | controlled_string | endpoint unit |
| replicate_id | string | biological/technical replicate identifier |
| control_type | controlled_string | vehicle, positive, negative, untreated, reference drug |
| protocol_version | string | protocol or SOP version |
| raw_file | string | path or URI for raw data |
| raw_file_sha256 | sha256 | hash for raw file integrity |
| quality_flag | controlled_string | pass, review, fail |
| interpretation | controlled_string | promote, hold, deprioritize |

## Curator Rule

- raw assay value만 있는 CSV는 논문 근거로 쓰지 않는다. `dose`, `unit`, `replicate_id`, `control_type`, `quality_flag`, `raw_file_sha256`가 필요하다.
- `quality_flag=review/fail`은 음성 결과로 보존하되 lead promotion에는 쓰지 않는다.
- `interpretation=promote` row가 들어오면 active-learning/BO planner가 다음 compute 또는 assay를 승격해야 한다.

```
### docs/WETLAB_RESULT_INGESTOR.md tail -100

```text
# Wet-lab Result Ingestor

- timestamp: `2026-05-06T12:46:35+09:00`
- status: `no_wetlab_results_yet`
- source_file: `data/wetlab_feedback_results.csv`
- result_template: `data/wetlab_feedback_results_template.csv`
- ingested_csv: `pilot/cpu_meaningful/wetlab_feedback_ingested.csv`
- decision_csv: `pilot/cpu_meaningful/wetlab_queue_decisions.csv`
- purpose: CRO/in-house assay 결과가 들어오면 quality/interpretation 기반으로 다음 compute 또는 논문 근거를 자동 분기한다.

## Decision Rules

| input | queue action |
|---|---|
| `quality_flag=pass` and `interpretation=promote` | BO/active-learning update and next fidelity promotion |
| `quality_flag=fail` or `interpretation=deprioritize` | duplicate compute block and negative evidence preservation |
| otherwise | repeat/QC hold before escalation |

## Curator Rule

- `data/wetlab_feedback_results.csv`가 생기면 이 ingestor를 먼저 실행하고, promote row만 후속 GPU/CPU 큐로 승격한다.
- template 파일은 예시용이다. 실제 결과는 `data/wetlab_feedback_results.csv`에 별도 저장한다.

```
### docs/MODEL_GOVERNANCE_REGISTRY.md tail -100

```text
# Model Governance Registry

- timestamp: `2026-05-06T12:46:35+09:00`
- registry_csv: `pilot/cpu_meaningful/ai_model_governance_registry.csv`
- model_cards: `docs/model_cards`
- purpose: FDA-style context-of-use, risk, validation, monitoring 관점으로 AI/ML/automation component를 관리한다.

## Registry

| model | risk | context of use | validation status | allowed claim |
|---|---|---|---|---|
| boltz2_cofold | tier2 | protein-ligand cofold triage for skin target hypotheses | local calibration and PoseBusters/MD cross-check required | in silico prioritization only; no binding or efficacy claim |
| openmm_md | tier2 | pose stability and drift/failure-mode assessment | trajectory RMSD summaries; force-field and timescale caveats remain | short-timescale stability support only |
| admet_ai | tier2 | AMES/hERG/DILI/skin reaction prefiltering | external model; no local wet-lab validation yet | predicted safety risk only |
| rdkit_descriptors | tier1 | skin-window, CMC, novelty, scaffold and formulation heuristics | deterministic cheminformatics; salt/tautomer review needed | descriptor-based heuristic only |
| active_learning_rf | tier1 | next cofold/docking candidate acquisition | local scaffold-domain gate and leave-one-out MAE | queue selection heuristic only |
| xtb_gfn2 | tier1 | conformer and quantum descriptor refinement for NPASS candidates | methodology/atlas support; not direct activity evidence | quantum descriptor prioritization only |
| open_targets_evidence | tier2 | target prioritization and claim strength limitation | API-derived evidence with manual biological interpretation | target evidence support only |
| codex_curator_loop | tier2 | compute queueing, paper queueing, and decision documentation | human-supervised automation; logs/provenance required | automation workflow support only |

## Curator Rule

- `tier2` component가 paper main claim에 영향을 주면 orthogonal check 또는 명확한 limitation이 필요하다.
- model card가 없는 새 predictor/agent는 manuscript evidence로 쓰지 않는다.
- retraining, prompt update, version change가 있으면 registry와 provenance manifest를 같이 갱신한다.

```
### docs/CREATIVE_DISCOVERY_GAP_MATRIX.md tail -120

```text
# Creative Discovery Gap Matrix

- timestamp: `2026-05-06T12:46:36+09:00`
- matrix_csv: `pilot/cpu_meaningful/creative_discovery_gap_matrix.csv`
- queue_policy_json: `pilot/creative_discovery_queue_policy.json`
- active-learning pending short-cofold pairs: `160`
- active-learning runnable short-cofold pairs: `0`
- active-learning blocked missing-MSA pairs: `160`
- active-learning in-flight manifest rows: `496`
- active-learning completed cofold result rows: `480`
- target-key A3M missing: `14` / `31`

## Meaning

이 파일은 창의적 신물질 발굴 기술이 실제 큐 정책에 연결됐는지 보는 상위 점검표다. 점수가 좋은 후보라도 synthesis, prior-art/FTO, novelty/diversity, phenomics, target cache, ensemble-pocket gate가 없으면 long-MD/FE/lead claim으로 자동 승격하지 않는다.

## Matrix

| priority | layer | status | evidence | readiness gate | compute policy | next queue action |
|---|---|---|---|---|---|---|
| P0 | active_learning_gpu_fallback | implemented_running | active-learning rows=672; pending short-cofold pairs=160; runnable=0; blocked missing-MSA pairs=160; manifests=496; completed result rows=480 | short_triage_allowed_only | GPU-free windows may run short Boltz-2 cofold; long MD/FE still require master-gate promotion | continue non-duplicate active-learning cofold batches; send hits back to master gate before MD |
| P0 | target_msa_coverage | gap_detected | skin target configs=31; available target A3M=17; missing target A3M=14 | block_target_specific_cofold_for_missing_msa | targets without target-key A3M are not eligible for automatic cofold queueing | prepare missing target-key MSA/sequence cache before queueing MC1R/RARG/TLR2/NLRP3-style targets |
| P0 | synthesis_native_generation | partial_post_filter_only | synthesis gate rows=112; route enumeration rows=1082; AiZynthFinder installed=False; ASKCOS cli installed=False | generation_requires_route_or_building_block_guard | generate-first/filter-later is not enough for expensive follow-up | add reaction-template/building-block enumeration lane before expanding non-chromanol designs |
| P0 | scaffold_hopping_shape_pharmacophore | partial_chromanol_constrained_only | chromanol generator rows=330; no separate shape/pharmacophore scaffold-hop queue detected | new_scaffold_requires_novelty_synthesis_uncertainty_gate | cheap CPU descriptors/enumeration allowed; heavy GPU requires prior-art and synthesis guard | create scaffold-hop queue around stable R16/R17 pharmacophores instead of only substituent scans |
| P1 | cryptic_pocket_dynamic_ensemble | static_pocket_gate_only | pocket evidence rows=31; no dynamic cryptic-pocket ensemble output detected | ensemble_pocket_required_before_pocket_specific_generation | do not claim cryptic/allosteric binding from static cofold alone | add ensemble pocket scout shortlist; only then launch pocket-specific generation |
| P1 | ultra_large_tangible_space | roadmap_only | ultra-large roadmap rows=50; no licensed library download/stage1 embedding output detected | license_storage_stage1_required | do not brute-force large libraries; use active-learning compression | prepare ZINC/REAL/Enamine subset license/storage checklist, then CPU embedding pre-screen |
| P1 | reward_hacking_novelty_benchmark | partial_decoy_gate_only | structure benchmark rows=32; no MolScore/Tartarus-style generative benchmark matrix detected | new_generator_requires_benchmark_and_decoys | affinity-only optimization cannot promote a molecule to lead status | add diversity/novelty/synthesis/decoy benchmark table for every new generator lane |
| P1 | phenomics_first_generation | partial_gate_only | phenomics rows=752; generator score still not phenomics-objective-native | phenotype_objective_required_for_moa_claim | Cell Painting/JUMP-style evidence should guide generation when direct pocket evidence is weak | feed disease-cell phenotype priority into next acquisition/generation score |
| P2 | new_modality_lanes | planned_gate_only | modality novelty doc exists=True; covalent/allosteric/glue/macrocycle generator lane not detected | high_risk_modality_requires_separate_safety_ip_gate | do not mix high-risk modality claims into ordinary topical small-molecule queue | keep covalent/allosteric/degrader/glue/macrocycle as separate benchmark or future-work lanes |
| P2 | agentic_hypothesis_evolution | partial_deterministic_curator | world-class master gate exists=True; creative matrix now generated | curator_must_read_creative_matrix_each_tick | LLM-style hypothesis generation must remain auditable and gate-bound | use this matrix in curator loop context before choosing the next queue |

## Target Cache Gap

- target-specific Boltz-2 cofold는 `data/msa/{target}.a3m`가 없으면 자동 큐잉하지 않는다.
- missing target-key A3M examples: `col1a1, f2rl1, mc1r, mmp3, mmp9, mylk, nlrp3, nr3c1, piezo1, ptgdr2, rarg, srebf1, tlr2, wnt10b`

## Curator Rules

- GPU가 비면 active-learning short Boltz-2 cofold는 허용한다. 단 결과는 triage이며, master gate 통과 전 long-MD/FE로 올리지 않는다.
- 새 scaffold 생성은 docking/affinity 단일 목적 최적화가 아니라 novelty, synthesis, prior-art, uncertainty, phenomics guard를 동시에 요구한다.
- chromanol 주변 치환체 탐색과 별도로 shape/pharmacophore scaffold-hop lane을 만들어야 한다.
- cryptic/allosteric pocket 주장은 static cofold가 아니라 ensemble pocket scout 이후에만 쓴다.
- phenomics-first 후보는 직접 target binding보다 disease-cell phenotype rescue objective를 우선한다.

```
### docs/WORLD_CLASS_GAP_CLOSURE.md tail -140

```text
# World-Class Drug Discovery Gap Closure

- timestamp: `2026-05-06T12:46:37+09:00`
- candidate_rows: `2328`
- matrix_csv: `pilot/cpu_meaningful/world_class_gap_closure_matrix.csv`
- queue_policy_json: `pilot/auto_queue_decision_policy.json`
- readiness_counts: `{'cheap_compute_or_paper_with_fto_caveat': 378, 'triage_accumulating': 1193, 'hold_or_benchmark_only': 757}`
- heavy_compute_permission_counts: `{'short_triage_only': 378, 'cheap_compute_only': 1193, 'hold': 757}`
- creative_discovery_status_counts: `{'implemented_running': 1, 'gap_detected': 1, 'partial_post_filter_only': 1, 'partial_chromanol_constrained_only': 1, 'static_pocket_gate_only': 1, 'roadmap_only': 1, 'partial_decoy_gate_only': 1, 'partial_gate_only': 1, 'planned_gate_only': 1, 'partial_deterministic_curator': 1}`
- target MSA missing count: `14`
- MMP-1 ZAFF status: `blocked_zaff_not_integrated`

## Meaning

이 파일은 개별 gate를 하나로 합친 master decision layer다. 후보가 좋은 cofold/MD 값을 가져도 prior-art, Markush/FTO, synthesis, safety, target biology, model uncertainty, dermal translation, FE readiness 중 하나가 막히면 비싼 계산이나 강한 claim으로 자동 승격하지 않는다.

## Queue Policy

- R17 expanded green-target 60 ns: `3/3` complete; already-running panel은 완료시킨다.
- 새 chromanol 100-200 ns, RBFE/ABFE, synthesis/purchase, commercial novelty claim은 Markush/FTO review 전까지 보류한다.
- NPASS/xTB/descriptor/atlas 같은 cheap CPU 계산은 계속 허용한다.
- MMP-1 direct-binding 강화 claim은 ZAFF/MCPB holo-Zn ABFE gate 통과 전까지 금지한다.
- EMB-3/quinone류는 GSH/NAC trapping, DPRA/KeratinoSens/h-CLAT, ROS/redox, photostability, skin S9/metabolite package 전까지 safety-positive claim 금지다.
- creative generation은 synthesis/prior-art/novelty/uncertainty/phenomics guard 없이 신규 long-MD/FE/lead claim으로 올리지 않는다.
- active-learning short cofold는 GPU 유휴 방지용 triage로 허용하지만, 결과는 master gate 통과 전까지 보조 evidence다.
- target-key MSA가 없는 target은 cofold queue에서 차단하고 cache 준비를 먼저 한다.
- `wetlab_translation_priority`는 더 큰 GPU 반복보다 CRO/DMTL/IVRT/IVPT/Cell Painting package를 먼저 만든다.

## Readiness By Target

| target | wetlab | paper | FTO-caveated | triage | hold |
|---|---:|---:|---:|---:|---:|
| ar | 0 | 0 | 0 | 0 | 1 |
| ctgf | 0 | 0 | 0 | 40 | 41 |
| dct | 0 | 0 | 125 | 40 | 41 |
| lox | 0 | 0 | 0 | 40 | 41 |
| mc1r | 0 | 0 | 0 | 40 | 40 |
| mitf | 0 | 0 | 0 | 0 | 1 |
| mmp1 | 0 | 0 | 0 | 0 | 190 |
| nr3c1 | 0 | 0 | 0 | 40 | 40 |
| ptgs2 | 0 | 0 | 0 | 0 | 102 |
| sirt1 | 0 | 0 | 0 | 0 | 1 |
| srd5a1 | 0 | 0 | 0 | 0 | 1 |
| srd5a2 | 0 | 0 | 0 | 0 | 1 |
| srebp1 | 0 | 0 | 0 | 0 | 1 |
| tgfb1 | 0 | 0 | 128 | 0 | 1 |
| tyr | 0 | 0 | 125 | 40 | 41 |
| tyrp1 | 0 | 0 | 0 | 40 | 41 |
| untargeted | 0 | 0 | 0 | 913 | 173 |

## Top Action Rows

| candidate | target | readiness | heavy compute | paper | blockers/caveats | next |
|---|---|---|---|---|---|---|
| R15_chromanol_Cl_pos10 | dct | cheap_compute_or_paper_with_fto_caveat | short_triage_only | in_silico_with_fto_caveat | Markush/FTO review required before heavy follow-up; medium IP/FTO/Markush review risk; cross-model/PLIF/negative-control validation required; benchmark decoys or orthogonal structure model required; OECD TG497/ICH S10 safety counterscreen required; CMC/developability yellow gate; model applicability-domain caveat: activity_cliff_risk | prepare Markush/FTO package; use only completed data for caveated papers |
| R15_chromanol_Cl_pos10 | tgfb1 | cheap_compute_or_paper_with_fto_caveat | short_triage_only | in_silico_with_fto_caveat | Markush/FTO review required before heavy follow-up; medium IP/FTO/Markush review risk; target evidence yellow: phenotype/cell context required; cross-model/PLIF/negative-control validation required; benchmark decoys or orthogonal structure model required; OpenFE/RBFE environment missing; OECD TG497/ICH S10 safety counterscreen required; CMC/developability yellow gate; model applicability-domain caveat: activity_cliff_risk | prepare Markush/FTO package; use only completed data for caveated papers |
| R15_chromanol_Cl_pos10 | tyr | cheap_compute_or_paper_with_fto_caveat | short_triage_only | in_silico_with_fto_caveat | Markush/FTO review required before heavy follow-up; medium IP/FTO/Markush review risk; cross-model/PLIF/negative-control validation required; OECD TG497/ICH S10 safety counterscreen required; CMC/developability yellow gate; model applicability-domain caveat: activity_cliff_risk | prepare Markush/FTO package; use only completed data for caveated papers |
| R15_chromanol_Cl_pos6 | dct | cheap_compute_or_paper_with_fto_caveat | short_triage_only | in_silico_with_fto_caveat | Markush/FTO review required before heavy follow-up; medium IP/FTO/Markush review risk; OpenFE/RBFE environment missing; OECD TG497/ICH S10 safety counterscreen required; CMC/developability yellow gate; model applicability-domain caveat: activity_cliff_risk | prepare Markush/FTO package; use only completed data for caveated papers |
| R15_chromanol_Cl_pos6 | tgfb1 | cheap_compute_or_paper_with_fto_caveat | short_triage_only | in_silico_with_fto_caveat | Markush/FTO review required before heavy follow-up; medium IP/FTO/Markush review risk; target evidence yellow: phenotype/cell context required; OpenFE/RBFE environment missing; OECD TG497/ICH S10 safety counterscreen required; CMC/developability yellow gate; model applicability-domain caveat: activity_cliff_risk | prepare Markush/FTO package; use only completed data for caveated papers |
| R15_chromanol_Cl_pos6 | tyr | cheap_compute_or_paper_with_fto_caveat | short_triage_only | in_silico_with_fto_caveat | Markush/FTO review required before heavy follow-up; medium IP/FTO/Markush review risk; OpenFE/RBFE environment missing; OECD TG497/ICH S10 safety counterscreen required; CMC/developability yellow gate; model applicability-domain caveat: activity_cliff_risk | prepare Markush/FTO package; use only completed data for caveated papers |
| R15_chromanol_Cl_pos9 | dct | cheap_compute_or_paper_with_fto_caveat | short_triage_only | in_silico_with_fto_caveat | Markush/FTO review required before heavy follow-up; medium IP/FTO/Markush review risk; OpenFE/RBFE environment missing; OECD TG497/ICH S10 safety counterscreen required; CMC/developability yellow gate; model applicability-domain caveat: activity_cliff_risk | prepare Markush/FTO package; use only completed data for caveated papers |
| R15_chromanol_Cl_pos9 | tgfb1 | cheap_compute_or_paper_with_fto_caveat | short_triage_only | in_silico_with_fto_caveat | Markush/FTO review required before heavy follow-up; medium IP/FTO/Markush review risk; target evidence yellow: phenotype/cell context required; OpenFE/RBFE environment missing; OECD TG497/ICH S10 safety counterscreen required; CMC/developability yellow gate; model applicability-domain caveat: activity_cliff_risk | prepare Markush/FTO package; use only completed data for caveated papers |
| R15_chromanol_Cl_pos9 | tyr | cheap_compute_or_paper_with_fto_caveat | short_triage_only | in_silico_with_fto_caveat | Markush/FTO review required before heavy follow-up; medium IP/FTO/Markush review risk; cross-model/PLIF/negative-control validation required; OECD TG497/ICH S10 safety counterscreen required; CMC/developability yellow gate; model applicability-domain caveat: activity_cliff_risk | prepare Markush/FTO package; use only completed data for caveated papers |
| R15_chromanol_Me6_Me10 | dct | cheap_compute_or_paper_with_fto_caveat | short_triage_only | in_silico_with_fto_caveat | Markush/FTO review required before heavy follow-up; cross-model/PLIF/negative-control validation required; model applicability-domain caveat: activity_cliff_risk | prepare Markush/FTO package; use only completed data for caveated papers |
| R15_chromanol_Me6_Me10 | tgfb1 | cheap_compute_or_paper_with_fto_caveat | short_triage_only | in_silico_with_fto_caveat | Markush/FTO review required before heavy follow-up; target evidence yellow: phenotype/cell context required; OpenFE/RBFE environment missing; model applicability-domain caveat: activity_cliff_risk | prepare Markush/FTO package; use only completed data for caveated papers |
| R15_chromanol_Me6_Me10 | tyr | cheap_compute_or_paper_with_fto_caveat | short_triage_only | in_silico_with_fto_caveat | Markush/FTO review required before heavy follow-up; cross-model/PLIF/negative-control validation required; model applicability-domain caveat: activity_cliff_risk | prepare Markush/FTO package; use only completed data for caveated papers |
| R15_chromanol_Me6_Me9 | dct | cheap_compute_or_paper_with_fto_caveat | short_triage_only | in_silico_with_fto_caveat | Markush/FTO review required before heavy follow-up; cross-model/PLIF/negative-control validation required; model applicability-domain caveat: activity_cliff_risk | prepare Markush/FTO package; use only completed data for caveated papers |
| R15_chromanol_Me6_Me9 | tgfb1 | cheap_compute_or_paper_with_fto_caveat | short_triage_only | in_silico_with_fto_caveat | Markush/FTO review required before heavy follow-up; target evidence yellow: phenotype/cell context required; OpenFE/RBFE environment missing; model applicability-domain caveat: activity_cliff_risk | prepare Markush/FTO package; use only completed data for caveated papers |
| R15_chromanol_Me6_Me9 | tyr | cheap_compute_or_paper_with_fto_caveat | short_triage_only | in_silico_with_fto_caveat | Markush/FTO review required before heavy follow-up; cross-model/PLIF/negative-control validation required; model applicability-domain caveat: activity_cliff_risk | prepare Markush/FTO package; use only completed data for caveated papers |
| R15_chromanol_Me9_Me10 | dct | cheap_compute_or_paper_with_fto_caveat | short_triage_only | in_silico_with_fto_caveat | Markush/FTO review required before heavy follow-up; cross-model/PLIF/negative-control validation required; model applicability-domain caveat: activity_cliff_risk | prepare Markush/FTO package; use only completed data for caveated papers |
| R15_chromanol_Me9_Me10 | tgfb1 | cheap_compute_or_paper_with_fto_caveat | short_triage_only | in_silico_with_fto_caveat | Markush/FTO review required before heavy follow-up; target evidence yellow: phenotype/cell context required; OpenFE/RBFE environment missing; model applicability-domain caveat: activity_cliff_risk | prepare Markush/FTO package; use only completed data for caveated papers |
| R15_chromanol_Me9_Me10 | tyr | cheap_compute_or_paper_with_fto_caveat | short_triage_only | in_silico_with_fto_caveat | Markush/FTO review required before heavy follow-up; cross-model/PLIF/negative-control validation required; model applicability-domain caveat: activity_cliff_risk | prepare Markush/FTO package; use only completed data for caveated papers |
| chromanol_arom10_CN_dct | dct | cheap_compute_or_paper_with_fto_caveat | short_triage_only | in_silico_with_fto_caveat | Markush/FTO review required before heavy follow-up; OECD TG497/ICH S10 safety counterscreen required; formulation rescue before exposure claim | prepare Markush/FTO package; use only completed data for caveated papers |
| chromanol_arom10_CN_tgfb1 | tgfb1 | cheap_compute_or_paper_with_fto_caveat | short_triage_only | in_silico_with_fto_caveat | Markush/FTO review required before heavy follow-up; target evidence yellow: phenotype/cell context required; OECD TG497/ICH S10 safety counterscreen required; formulation rescue before exposure claim | prepare Markush/FTO package; use only completed data for caveated papers |
| chromanol_arom10_CN_tyr | tyr | cheap_compute_or_paper_with_fto_caveat | short_triage_only | in_silico_with_fto_caveat | Markush/FTO review required before heavy follow-up; OECD TG497/ICH S10 safety counterscreen required; formulation rescue before exposure claim | prepare Markush/FTO package; use only completed data for caveated papers |
| chromanol_arom10_Cl_dct | dct | cheap_compute_or_paper_with_fto_caveat | short_triage_only | in_silico_with_fto_caveat | Markush/FTO review required before heavy follow-up; medium IP/FTO/Markush review risk; cross-model/PLIF/negative-control validation required; benchmark decoys or orthogonal structure model required; OECD TG497/ICH S10 safety counterscreen required; CMC/developability yellow gate | prepare Markush/FTO package; use only completed data for caveated papers |
| chromanol_arom10_Cl_tgfb1 | tgfb1 | cheap_compute_or_paper_with_fto_caveat | short_triage_only | in_silico_with_fto_caveat | Markush/FTO review required before heavy follow-up; medium IP/FTO/Markush review risk; target evidence yellow: phenotype/cell context required; cross-model/PLIF/negative-control validation required; benchmark decoys or orthogonal structure model required; OECD TG497/ICH S10 safety counterscreen required; CMC/developability yellow gate | prepare Markush/FTO package; use only completed data for caveated papers |
| chromanol_arom10_Cl_tyr | tyr | cheap_compute_or_paper_with_fto_caveat | short_triage_only | in_silico_with_fto_caveat | Markush/FTO review required before heavy follow-up; medium IP/FTO/Markush review risk; cross-model/PLIF/negative-control validation required; OECD TG497/ICH S10 safety counterscreen required; CMC/developability yellow gate | prepare Markush/FTO package; use only completed data for caveated papers |
| chromanol_arom10_F_dct | dct | cheap_compute_or_paper_with_fto_caveat | short_triage_only | in_silico_with_fto_caveat | Markush/FTO review required before heavy follow-up | prepare Markush/FTO package; use only completed data for caveated papers |
| chromanol_arom10_F_tgfb1 | tgfb1 | cheap_compute_or_paper_with_fto_caveat | short_triage_only | in_silico_with_fto_caveat | Markush/FTO review required before heavy follow-up; target evidence yellow: phenotype/cell context required | prepare Markush/FTO package; use only completed data for caveated papers |
| chromanol_arom10_F_tyr | tyr | cheap_compute_or_paper_with_fto_caveat | short_triage_only | in_silico_with_fto_caveat | Markush/FTO review required before heavy follow-up | prepare Markush/FTO package; use only completed data for caveated papers |
| chromanol_arom10_Me_dct | dct | cheap_compute_or_paper_with_fto_caveat | short_triage_only | in_silico_with_fto_caveat | Markush/FTO review required before heavy follow-up | prepare Markush/FTO package; use only completed data for caveated papers |
| chromanol_arom10_Me_tgfb1 | tgfb1 | cheap_compute_or_paper_with_fto_caveat | short_triage_only | in_silico_with_fto_caveat | Markush/FTO review required before heavy follow-up; target evidence yellow: phenotype/cell context required | prepare Markush/FTO package; use only completed data for caveated papers |
| chromanol_arom10_Me_tyr | tyr | cheap_compute_or_paper_with_fto_caveat | short_triage_only | in_silico_with_fto_caveat | Markush/FTO review required before heavy follow-up | prepare Markush/FTO package; use only completed data for caveated papers |
| chromanol_arom10_OH_dct | dct | cheap_compute_or_paper_with_fto_caveat | short_triage_only | in_silico_with_fto_caveat | Markush/FTO review required before heavy follow-up; OECD TG497/ICH S10 safety counterscreen required; formulation rescue before exposure claim | prepare Markush/FTO package; use only completed data for caveated papers |
| chromanol_arom10_OH_tgfb1 | tgfb1 | cheap_compute_or_paper_with_fto_caveat | short_triage_only | in_silico_with_fto_caveat | Markush/FTO review required before heavy follow-up; target evidence yellow: phenotype/cell context required; OECD TG497/ICH S10 safety counterscreen required; formulation rescue before exposure claim | prepare Markush/FTO package; use only completed data for caveated papers |
| chromanol_arom10_OH_tyr | tyr | cheap_compute_or_paper_with_fto_caveat | short_triage_only | in_silico_with_fto_caveat | Markush/FTO review required before heavy follow-up; OECD TG497/ICH S10 safety counterscreen required; formulation rescue before exposure claim | prepare Markush/FTO package; use only completed data for caveated papers |
| chromanol_arom10_OMe_dct | dct | cheap_compute_or_paper_with_fto_caveat | short_triage_only | in_silico_with_fto_caveat | Markush/FTO review required before heavy follow-up; OECD TG497/ICH S10 safety counterscreen required; formulation rescue before exposure claim | prepare Markush/FTO package; use only completed data for caveated papers |
| chromanol_arom10_OMe_tgfb1 | tgfb1 | cheap_compute_or_paper_with_fto_caveat | short_triage_only | in_silico_with_fto_caveat | Markush/FTO review required before heavy follow-up; target evidence yellow: phenotype/cell context required; OECD TG497/ICH S10 safety counterscreen required; formulation rescue before exposure claim | prepare Markush/FTO package; use only completed data for caveated papers |
| chromanol_arom10_OMe_tyr | tyr | cheap_compute_or_paper_with_fto_caveat | short_triage_only | in_silico_with_fto_caveat | Markush/FTO review required before heavy follow-up; OECD TG497/ICH S10 safety counterscreen required; formulation rescue before exposure claim | prepare Markush/FTO package; use only completed data for caveated papers |
| chromanol_arom6+arom10_Cl+Cl_dct | dct | cheap_compute_or_paper_with_fto_caveat | short_triage_only | in_silico_with_fto_caveat | Markush/FTO review required before heavy follow-up; OECD TG497/ICH S10 safety counterscreen required | prepare Markush/FTO package; use only completed data for caveated papers |
| chromanol_arom6+arom10_Cl+Cl_tgfb1 | tgfb1 | cheap_compute_or_paper_with_fto_caveat | short_triage_only | in_silico_with_fto_caveat | Markush/FTO review required before heavy follow-up; target evidence yellow: phenotype/cell context required; OECD TG497/ICH S10 safety counterscreen required | prepare Markush/FTO package; use only completed data for caveated papers |
| chromanol_arom6+arom10_Cl+Cl_tyr | tyr | cheap_compute_or_paper_with_fto_caveat | short_triage_only | in_silico_with_fto_caveat | Markush/FTO review required before heavy follow-up; OECD TG497/ICH S10 safety counterscreen required | prepare Markush/FTO package; use only completed data for caveated papers |
| chromanol_arom6+arom10_Cl+F_dct | dct | cheap_compute_or_paper_with_fto_caveat | short_triage_only | in_silico_with_fto_caveat | Markush/FTO review required before heavy follow-up; OECD TG497/ICH S10 safety counterscreen required | prepare Markush/FTO package; use only completed data for caveated papers |
| chromanol_arom6+arom10_Cl+F_tgfb1 | tgfb1 | cheap_compute_or_paper_with_fto_caveat | short_triage_only | in_silico_with_fto_caveat | Markush/FTO review required before heavy follow-up; target evidence yellow: phenotype/cell context required; OECD TG497/ICH S10 safety counterscreen required | prepare Markush/FTO package; use only completed data for caveated papers |
| chromanol_arom6+arom10_Cl+F_tyr | tyr | cheap_compute_or_paper_with_fto_caveat | short_triage_only | in_silico_with_fto_caveat | Markush/FTO review required before heavy follow-up; OECD TG497/ICH S10 safety counterscreen required | prepare Markush/FTO package; use only completed data for caveated papers |
| chromanol_arom6+arom10_Cl+Me_dct | dct | cheap_compute_or_paper_with_fto_caveat | short_triage_only | in_silico_with_fto_caveat | Markush/FTO review required before heavy follow-up; OECD TG497/ICH S10 safety counterscreen required | prepare Markush/FTO package; use only completed data for caveated papers |
| chromanol_arom6+arom10_Cl+Me_tgfb1 | tgfb1 | cheap_compute_or_paper_with_fto_caveat | short_triage_only | in_silico_with_fto_caveat | Markush/FTO review required before heavy follow-up; target evidence yellow: phenotype/cell context required; OECD TG497/ICH S10 safety counterscreen required | prepare Markush/FTO package; use only completed data for caveated papers |
| chromanol_arom6+arom10_Cl+Me_tyr | tyr | cheap_compute_or_paper_with_fto_caveat | short_triage_only | in_silico_with_fto_caveat | Markush/FTO review required before heavy follow-up; OECD TG497/ICH S10 safety counterscreen required | prepare Markush/FTO package; use only completed data for caveated papers |
| chromanol_arom6+arom10_Cl+OMe_dct | dct | cheap_compute_or_paper_with_fto_caveat | short_triage_only | in_silico_with_fto_caveat | Markush/FTO review required before heavy follow-up; OECD TG497/ICH S10 safety counterscreen required | prepare Markush/FTO package; use only completed data for caveated papers |
| chromanol_arom6+arom10_Cl+OMe_tgfb1 | tgfb1 | cheap_compute_or_paper_with_fto_caveat | short_triage_only | in_silico_with_fto_caveat | Markush/FTO review required before heavy follow-up; target evidence yellow: phenotype/cell context required; OECD TG497/ICH S10 safety counterscreen required | prepare Markush/FTO package; use only completed data for caveated papers |
| chromanol_arom6+arom10_Cl+OMe_tyr | tyr | cheap_compute_or_paper_with_fto_caveat | short_triage_only | in_silico_with_fto_caveat | Markush/FTO review required before heavy follow-up; OECD TG497/ICH S10 safety counterscreen required | prepare Markush/FTO package; use only completed data for caveated papers |
| chromanol_arom6+arom10_F+Cl_dct | dct | cheap_compute_or_paper_with_fto_caveat | short_triage_only | in_silico_with_fto_caveat | Markush/FTO review required before heavy follow-up; OECD TG497/ICH S10 safety counterscreen required | prepare Markush/FTO package; use only completed data for caveated papers |
| chromanol_arom6+arom10_F+Cl_tgfb1 | tgfb1 | cheap_compute_or_paper_with_fto_caveat | short_triage_only | in_silico_with_fto_caveat | Markush/FTO review required before heavy follow-up; target evidence yellow: phenotype/cell context required; OECD TG497/ICH S10 safety counterscreen required | prepare Markush/FTO package; use only completed data for caveated papers |

## System Gaps Now Covered

- Cross-model/decoy/PLIF gap: `STRUCTURE_CONSENSUS_V2`와 `STRUCTURE_BENCHMARK_DECOY_GATE`를 master gate에 반영한다.
- Free-energy gap: `FREE_ENERGY_VALIDATION_PLAN`, `RBFE_UPGRADE_READINESS`, `MMP1_ZAFF_ABFE_GATE`를 반영한다.
- Prior-art/FTO gap: `PRECOMPUTE_PRIOR_ART_GATE`와 `IP_FTO_WATCHLIST`를 heavy-compute blocker로 반영한다.
- Synthesis/route gap: `SYNTHESIS_RETROSYNTHESIS_GATE`와 `ROUTE_ENUMERATION_GATE`를 반영한다.
- Topical translation gap: dermal regulatory, photosafety, dermal PBPK/IVPT, formulation BO, CMC gate를 반영한다.
- Biology/phenotype gap: target evidence, phenomics, target engagement, DMTL card를 반영한다.
- ML/governance gap: applicability-domain uncertainty와 model governance/provenance caveat를 queue policy에 반영한다.
- Creative discovery gap: active-learning GPU fallback, target MSA coverage, scaffold-hop, synthesis-native generation, cryptic-pocket, ultra-large, reward-benchmark, phenomics-first rules를 반영한다.

## Curator Rule

- `hold_or_benchmark_only`: 비싼 GPU/FE/합성/상업 claim 금지. 논문은 limitation, method, benchmark로만 사용한다.
- `cheap_compute_or_paper_with_fto_caveat`: 이미 끝난 데이터로 caveated in-silico paper는 가능하나 신규 long-MD/FE/synthesis는 보류한다.
- `paper_ready_in_silico`: main table 가능하지만 confirmed binding, clinical efficacy, commercial novelty 표현은 금지한다.
- `wetlab_translation_priority`: 다음 자원 투입은 CRO/wet-lab package가 우선이며, GPU 반복은 보조다.
- active-learning cofold 결과는 완료 즉시 이 matrix에 들어오지만, short triage evidence라 long-MD/FE 승격은 synthesis/prior-art/safety/phenomics/uncertainty gate를 다시 통과해야 한다.
- MC1R/RARG/TLR2/NLRP3처럼 target-key MSA가 없는 target은 cache 준비 전 자동 cofold를 큐잉하지 않는다.

```
