# Genesis Medicine Live Status

- timestamp: `2026-05-06T12:48:55+09:00`
- note: 채팅창으로 선제 푸시 보고는 불가하므로, 이 파일을 주기 갱신하는 heartbeat로 사용합니다.

## Compute

- GPU: `2 %, 16559 MiB, 32607 MiB`
- CPU/load: `12:48:56 up 7 days,  2:43,  1 user,  load average: 2.91, 2.91, 2.21`
- CPU vmstat sample: `0  0   8012 10531892  99172 3882480    0    0     0    76 20366 48078  0  3 97  0  0  0`
- active xTB refine process count: `0`
- protected NPASS process count: `0`

## Storage

```text
Filesystem     Type  Size  Used Avail Use% Mounted on
/dev/sdf       ext4  1.8T  442G  1.3T  27% /
C:\            9p    1.9T  1.5T  450G  77% /mnt/c
D:\            9p    1.9T  691G  1.2T  38% /mnt/d
```

```json
{
    "timestamp": "2026-05-02T19:50:01+09:00",
    "status": "ok",
    "thresholds": {
        "warn_free_gb": 200.0,
        "hard_hold_free_gb": 80.0
    },
    "disks": {
        "wsl_root": {
            "path": "/",
            "exists": true,
            "total_gb": 1006.9,
            "used_gb": 554.5,
            "free_gb": 401.1,
            "used_pct": 55.1
        },
        "windows_c": {
            "path": "/mnt/c",
            "exists": true,
            "total_gb": 1906.9,
            "used_gb": 1441.6,
            "free_gb": 465.2,
            "used_pct": 75.6
        },
        "windows_d": {
            "path": "/mnt/d",
            "exists": true,
            "total_gb": 1863.0,
            "used_gb": 634.2,
            "free_gb": 1228.9,
            "used_pct": 34.0
        }
    },
    "project_top": [
        {
            "path": "pilot",
            "gb": 252.96
        },
        {
            "path": ".venv",
            "gb": 17.74
        },
        {
            "path": ".cache",
            "gb": 7.9
        },
        {
            "path": "external",
            "gb": 1.29
        },
        {
            "path": "external_tools",
            "gb": 0.16
        },
        {
            "path": ".git",
            "gb": 0.1
        },
        {
            "path": "scripts",
            "gb": 0.06
        },
        {
            "path": "data",
            "gb": 0.04
        },
        {
            "path": "ner_results.csv",
            "gb": 0.04
        },
        {
            "path": "preprints",
            "gb": 0.03
        },
        {
            "path": "Genesis_Medicine.code-workspace",
            "gb": 0.0
        },
        {
            "path": "Dockerfile",
            "gb": 0.0
        },
        {
            "path": "co_occurring_genes_cleaned.png",
            "gb": 0.0
        },
        {
            "path": ".claude",
            "gb": 0.0
        },
        {
            "path": "requirements.txt",
            "gb": 0.0
        },
        {
            "path": "README.md",
            "gb": 0.0
        },
        {
            "path": "conf",
            "gb": 0.0
        },
        {
            "path": "proteins",
            "gb": 0.0
        },
        {
            "path": "dvc.yaml",
            "gb": 0.0
        },
        {
            "path": "pyproject.toml",
            "gb": 0.0
        }
    ],
    "pilot_top": [
        {
            "path": "pilot/md_r16_chromanol_anchor_triad_200ns",
            "gb": 25.47
        },
```

## Active GPU Jobs

```text
(none)
```

## Active Queue Processes

```text
77583 bash /home/crazat/genesis_medicine/scripts/monitor_supervisor.sh
77605 bash /home/crazat/genesis_medicine/scripts/codex_curator_loop.sh
2512206 bash /home/crazat/genesis_medicine/scripts/auto_queue_cpu_gpu_daemon.sh
```

## R16 MD Summaries

- `md_r16_chromanol_topical_pigment_representative_60ns`: ok `3/3`
- `md_r15_chromanol_top3_30ns`: ok `3/3`
- `md_r16_chromanol_topical_tgfb1_top6_60ns`: ok `6/6`
- `md_r16_chromanol_topical_dimethyl_pigment_30ns`: ok `6/6`
- `md_r16_chromanol_topical_chloro_pigment_30ns`: ok `4/4`
- `md_r16_chromanol_topical_chloro_tgfb1_30ns`: ok `2/2`
- `md_r16_chromanol_topical_tgfb1_extra_30ns`: ok `3/3`
- `md_r16_chromanol_topical_priority_30ns`: ok `3/3`

## Latest xTB Outputs

```text
-rw-r--r-- 1 crazat crazat   18917 May  6 07:50 pilot/cpu_meaningful/xtb_npass_top9997_hetero10_refine_672conf.csv
-rw-r--r-- 1 crazat crazat  281632 May  6 05:33 pilot/cpu_meaningful/xtb_npass_top9997_hetero10_refine_576conf.csv
-rw-r--r-- 1 crazat crazat  281662 May  6 03:18 pilot/cpu_meaningful/xtb_npass_top9997_hetero10_refine_480conf.csv
-rw-r--r-- 1 crazat crazat  289514 May  6 01:49 pilot/cpu_meaningful/xtb_npass_top9997_hetero10_refine_816conf.csv
-rw-r--r-- 1 crazat crazat  281663 May  6 00:49 pilot/cpu_meaningful/xtb_npass_top9997_hetero10_refine_528conf.csv
-rw-r--r-- 1 crazat crazat  284702 May  5 19:09 pilot/cpu_meaningful/xtb_npass_top9997_hetero10_refine_720conf.csv
-rw-r--r-- 1 crazat crazat  284745 May  5 15:48 pilot/cpu_meaningful/xtb_npass_top9997_hetero10_refine_624conf.csv
-rw-r--r-- 1 crazat crazat  289422 May  5 12:47 pilot/cpu_meaningful/xtb_npass_top9997_hetero10_refine_432conf.csv
```

## Planner

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

## Creative Discovery

- creative gap rows: `10`
- active-learning short-cofold manifest rows: `496`
- active-learning completed short-cofold rows: `480`

```json
{
    "timestamp": "2026-05-06T12:46:36+09:00",
    "matrix_csv": "pilot/cpu_meaningful/creative_discovery_gap_matrix.csv",
    "matrix_doc": "docs/CREATIVE_DISCOVERY_GAP_MATRIX.md",
    "active_learning_short_cofold": {
        "rows": 672,
        "pending_short_cofold_pairs": 160,
        "runnable_short_cofold_pairs": 0,
        "blocked_missing_msa_pairs": 160,
        "result_rows": 480,
        "manifest_rows": 496,
        "target_counts": {},
        "blocked_target_counts": {
            "mc1r": 80,
            "nr3c1": 80
        },
        "result_files": [
            "pilot/cpu_meaningful/active_learning_next_cofold_batch01.csv",
            "pilot/cpu_meaningful/active_learning_next_cofold_batch02.csv",
            "pilot/cpu_meaningful/active_learning_next_cofold_batch03.csv",
            "pilot/cpu_meaningful/active_learning_next_cofold_batch04.csv",
            "pilot/cpu_meaningful/active_learning_next_cofold_batch05.csv",
            "pilot/cpu_meaningful/active_learning_next_cofold_batch06.csv",
            "pilot/cpu_meaningful/active_learning_next_cofold_batch07.csv",
            "pilot/cpu_meaningful/active_learning_next_cofold_batch08.csv",
            "pilot/cpu_meaningful/active_learning_next_cofold_batch09.csv",
            "pilot/cpu_meaningful/active_learning_next_cofold_batch10.csv",
            "pilot/cpu_meaningful/active_learning_next_cofold_batch11.csv",
            "pilot/cpu_meaningful/active_learning_next_cofold_batch12.csv",
            "pilot/cpu_meaningful/active_learning_next_cofold_batch13.csv",
            "pilot/cpu_meaningful/active_learning_next_cofold_batch14.csv",
            "pilot/cpu_meaningful/active_learning_next_cofold_batch15.csv",
            "pilot/cpu_meaningful/active_learning_next_cofold_batch16.csv",
            "pilot/cpu_meaningful/active_learning_next_cofold_batch17.csv",
            "pilot/cpu_meaningful/active_learning_next_cofold_batch18.csv",
            "pilot/cpu_meaningful/active_learning_next_cofold_batch19.csv",
            "pilot/cpu_meaningful/active_learning_next_cofold_batch21.csv",
            "pilot/cpu_meaningful/active_learning_next_cofold_batch22.csv",
            "pilot/cpu_meaningful/active_learning_next_cofold_batch23.csv",
            "pilot/cpu_meaningful/active_learning_next_cofold_batch24.csv",
            "pilot/cpu_meaningful/active_learning_next_cofold_batch25.csv",
            "pilot/cpu_meaningful/active_learning_next_cofold_batch26.csv",
            "pilot/cpu_meaningful/active_learning_next_cofold_batch27.csv",
            "pilot/cpu_meaningful/active_learning_next_cofold_batch28.csv",
            "pilot/cpu_meaningful/active_learning_next_cofold_batch29.csv",
            "pilot/cpu_meaningful/active_learning_next_cofold_batch30.csv",
            "pilot/cpu_meaningful/active_learning_next_cofold_batch31.csv",
            "pilot/cpu_meaningful/active_learning_next_cofold_batch32.csv",
            "pilot/cpu_meaningful/active_learning_next_cofold_batch33.csv"
        ],
        "manifest_files": [
            "pilot/cpu_meaningful/active_learning_next_cofold_batch01_manifest.csv",
            "pilot/cpu_meaningful/active_learning_next_cofold_batch02_manifest.csv",
            "pilot/cpu_meaningful/active_learning_next_cofold_batch03_manifest.csv",
            "pilot/cpu_meaningful/active_learning_next_cofold_batch04_manifest.csv",
            "pilot/cpu_meaningful/active_learning_next_cofold_batch05_manifest.csv",
            "pilot/cpu_meaningful/active_learning_next_cofold_batch06_manifest.csv",
            "pilot/cpu_meaningful/active_learning_next_cofold_batch07_manifest.csv",
            "pilot/cpu_meaningful/active_learning_next_cofold_batch08_manifest.csv",
            "pilot/cpu_meaningful/active_learning_next_cofold_batch09_manifest.csv",
            "pilot/cpu_meaningful/active_learning_next_cofold_batch10_manifest.csv",
            "pilot/cpu_meaningful/active_learning_next_cofold_batch11_manifest.csv",
            "pilot/cpu_meaningful/active_learning_next_cofold_batch12_manifest.csv",
            "pilot/cpu_meaningful/active_learning_next_cofold_batch13_manifest.csv",
            "pilot/cpu_meaningful/active_learning_next_cofold_batch14_manifest.csv",
            "pilot/cpu_meaningful/active_learning_next_cofold_batch15_manifest.csv",
            "pilot/cpu_meaningful/active_learning_next_cofold_batch16_manifest.csv",
            "pilot/cpu_meaningful/active_learning_next_cofold_batch17_manifest.csv",
            "pilot/cpu_meaningful/active_learning_next_cofold_batch18_manifest.csv",
            "pilot/cpu_meaningful/active_learning_next_cofold_batch19_manifest.csv",
            "pilot/cpu_meaningful/active_learning_next_cofold_batch20_manifest.csv",
            "pilot/cpu_meaningful/active_learning_next_cofold_batch21_manifest.csv",
            "pilot/cpu_meaningful/active_learning_next_cofold_batch22_manifest.csv",
            "pilot/cpu_meaningful/active_learning_next_cofold_batch23_manifest.csv",
            "pilot/cpu_meaningful/active_learning_next_cofold_batch24_manifest.csv",
            "pilot/cpu_meaningful/active_learning_next_cofold_batch25_manifest.csv",
            "pilot/cpu_meaningful/active_learning_next_cofold_batch26_manifest.csv",
            "pilot/cpu_meaningful/active_learning_next_cofold_batch27_manifest.csv",
            "pilot/cpu_meaningful/active_learning_next_cofold_batch28_manifest.csv",
            "pilot/cpu_meaningful/active_learning_next_cofold_batch29_manifest.csv",
            "pilot/cpu_meaningful/active_learning_next_cofold_batch30_manifest.csv",
            "pilot/cpu_meaningful/active_learning_next_cofold_batch31_manifest.csv",
            "pilot/cpu_meaningful/active_learning_next_cofold_batch32_manifest.csv",
            "pilot/cpu_meaningful/active_learning_next_cofold_batch33_manifest.csv"
        ]
    },
    "target_cache": {
        "target_count": 31,
        "available_a3m_count": 17,
        "missing_a3m_count": 14,
        "missing_a3m": [
            "col1a1",
            "f2rl1",
            "mc1r",
            "mmp3",
            "mmp9",
            "mylk",
            "nlrp3",
            "nr3c1",
            "piezo1",
            "ptgdr2",
            "rarg",
            "srebf1",
            "tlr2",
            "wnt10b"
        ],
        "missing_sequence_count": 16,
        "missing_sequence": [
            "col1a1",
            "f2rl1",
            "mc1r",
            "mitf",
            "mmp3",
            "mmp9",
            "mylk",
            "nlrp3",
            "nr3c1",
            "piezo1",
            "ptgdr2",
            "rarg",
```

## World-Class Queue Policy

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
```

## Recent Curator Actions

```text
[2026-05-06T12:36:31+09:00] curator failed rc=127
2026-05-06T12:37:58+09:00 CPU_IDLE_GAP_UNRESOLVED idle=96% active_refines=0 planner=none
2026-05-06T12:39:58+09:00 CPU_IDLE_GAP_UNRESOLVED idle=97% active_refines=0 planner=none
2026-05-06T12:41:53+09:00 CPU_IDLE_GAP_UNRESOLVED idle=95% active_refines=0 planner=none
2026-05-06T12:43:58+09:00 CPU_IDLE_GAP_UNRESOLVED idle=95% active_refines=0 planner=none
2026-05-06T12:46:11+09:00 CPU_IDLE_GAP_UNRESOLVED idle=67% active_refines=0 planner=none
[2026-05-06T12:47:02+09:00] curator failed rc=127
2026-05-06T12:48:05+09:00 CPU_IDLE_GAP_UNRESOLVED idle=93% active_refines=0 planner=none
```

## Top CPU

```text
USER         PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
crazat   2949978  3.6  0.8 75552380 511980 pts/6 Sl+  May03 164:23 claude --permission-mode bypassPermissions
crazat   2301360  0.8  0.0  18776 13832 ?        S    12:48   0:00 python3 /home/crazat/genesis_medicine/scripts/write_live_status_report.py
root           1  0.0  0.0  22236  9108 ?        Ss   May02   2:57 /usr/lib/systemd/systemd --system --deserialize=60
crazat   1898638  0.0  0.0   4888  3592 ?        Ss   May05   0:23 /bin/bash -c source /home/crazat/.claude/shell-snapshots/snapshot-bash-1777781873206-74i5b2.sh 2>/dev/null || true && shopt -u extglob 2>/dev/null || true && eval 'until nvidia-smi --query-compute-apps=pid --format=csv,noheader 2>/dev/null | grep -q 1897121; do sleep 3; done; echo "CHEMBL257077 (PID 1897121) GPU에 등록됨"; date '"'"'+%H:%M:%S'"'"'' < /dev/null && pwd -P >| /tmp/claude-84f0-cwd
root     1267412  0.0  0.0  66724 13316 ?        S<s  May03   0:58 /usr/lib/systemd/systemd-journald
message+     204  0.0  0.0   9916  5116 ?        Ss   May02   0:32 @dbus-daemon --system --address=systemd: --nofork --nopidfile --systemd-activation --syslog-only
root     2949302  0.0  0.0   3144  1296 ?        S    May03   0:19 /init
```
