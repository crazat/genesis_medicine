"""Result-aware queue planner for Genesis_Medicine automation.

This is deliberately deterministic. It does not call an LLM; it turns the
current result files into the next GPU/CPU queue decision and records the
reasoning in pilot/auto_result_planner_latest.json.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_meaningful"
PLAN_PATH = ROOT / "pilot/auto_result_planner_latest.json"
QUEUE_POLICY_PATH = ROOT / "pilot/auto_queue_decision_policy.json"
ACTIVE_LEARNING_NEXT = OUT / "active_learning_next_candidates.csv"
MSA_DIR = ROOT / "data/msa"

GPU_PRIORITY = ROOT / "pilot/md_r16_chromanol_topical_priority_30ns/summary.json"
GPU_TGFB1_EXTRA = ROOT / "pilot/md_r16_chromanol_topical_tgfb1_extra_30ns/summary.json"
GPU_CHLORO_TGFB1 = ROOT / "pilot/md_r16_chromanol_topical_chloro_tgfb1_30ns/summary.json"
GPU_CHLORO_PIGMENT = ROOT / "pilot/md_r16_chromanol_topical_chloro_pigment_30ns/summary.json"
GPU_DIMETHYL_PIGMENT = ROOT / "pilot/md_r16_chromanol_topical_dimethyl_pigment_30ns/summary.json"
GPU_R16_TGFB1_TOP6_60 = ROOT / "pilot/md_r16_chromanol_topical_tgfb1_top6_60ns/summary.json"
GPU_R15_TOP3_30 = ROOT / "pilot/md_r15_chromanol_top3_30ns/summary.json"
GPU_R16_PIGMENT_REP_60 = ROOT / "pilot/md_r16_chromanol_topical_pigment_representative_60ns/summary.json"
GPU_R16_ANCHOR_TRIAD_100 = ROOT / "pilot/md_r16_chromanol_anchor_triad_100ns/summary.json"
GPU_R16_ANCHOR_TRIAD_200 = ROOT / "pilot/md_r16_chromanol_anchor_triad_200ns/summary.json"
GPU_R17_TOP_GREEN_10 = ROOT / "pilot/md_r17_chromanol_generative_top_green_10ns/summary.json"
GPU_R17_TOP_GREEN_30 = ROOT / "pilot/md_r17_chromanol_generative_top_green_30ns/summary.json"
GPU_R17_TOP_GREEN_60 = ROOT / "pilot/md_r17_chromanol_generative_top_green_60ns/summary.json"
GPU_R17_NEXT_GREEN_10 = ROOT / "pilot/md_r17_chromanol_generative_next_green_10ns/summary.json"
GPU_R17_NEXT_GREEN_30 = ROOT / "pilot/md_r17_chromanol_generative_next_green_30ns/summary.json"
GPU_R17_NEXT_GREEN_60 = ROOT / "pilot/md_r17_chromanol_generative_next_green_60ns/summary.json"
GPU_R17_EXPANDED_GREEN_10 = ROOT / "pilot/md_r17_chromanol_generative_expanded_green_10ns/summary.json"
GPU_R17_EXPANDED_GREEN_30 = ROOT / "pilot/md_r17_chromanol_generative_expanded_green_30ns/summary.json"
GPU_R17_EXPANDED_GREEN_60 = ROOT / "pilot/md_r17_chromanol_generative_expanded_green_60ns/summary.json"
GPU_R17_GENERATIVE_TARGET_ROWS = int(os.environ.get("GENESIS_R17_GENERATIVE_TARGET_ROWS", "240"))

CPU_TIERS = [
    (500, 2),
    (1000, 3),
    (3000, 5),
    (3000, 8),
    (7000, 7),
    (9000, 9),
    (9997, 10),
]
DEFAULT_CPU_CONF_LADDER = [36, 48, 72, 96, 120, 144, 168, 192, 240, 288, 336, 384]
CPU_WORKERS = int(os.environ.get("GENESIS_CPU_XTB_WORKERS", "12"))
MIN_FREE_GB = float(os.environ.get("GENESIS_MIN_FREE_GB", "80"))
WARN_FREE_GB = float(os.environ.get("GENESIS_WARN_FREE_GB", "200"))


def parse_conf_ladder() -> list[int]:
    raw = os.environ.get("GENESIS_CPU_CONF_LADDER", "")
    if not raw.strip():
        return DEFAULT_CPU_CONF_LADDER
    values: list[int] = []
    for token in raw.replace(",", " ").split():
        try:
            value = int(token)
        except ValueError:
            continue
        if value > 0 and value not in values:
            values.append(value)
    return values or DEFAULT_CPU_CONF_LADDER


def build_cpu_tasks() -> list[tuple[int, int, int, int, str]]:
    tasks: list[tuple[int, int, int, int, str]] = []
    for confs in parse_conf_ladder():
        for topn, hetero in CPU_TIERS:
            out = f"xtb_npass_top{topn}_hetero{hetero}_refine_{confs}conf.csv"
            tasks.append((topn, hetero, confs, CPU_WORKERS, out))
    return tasks


CPU_TASKS = build_cpu_tasks()


def load_rows(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    try:
        rows = json.loads(path.read_text())
    except Exception:
        return []
    return rows if isinstance(rows, list) else []


def ok_rows(path: Path) -> list[dict[str, Any]]:
    return [row for row in load_rows(path) if row.get("status") == "ok"]


def csv_row_count(path: Path) -> int:
    if not path.exists() or path.stat().st_size == 0:
        return 0
    try:
        with path.open() as handle:
            return max(sum(1 for _ in handle) - 1, 0)
    except Exception:
        return 0


def r17_generative_rows() -> int:
    return sum(csv_row_count(path) for path in OUT.glob("r17_chromanol_generative_batch*_cofold.csv"))


def active_learning_completed_pairs() -> set[tuple[str, str]]:
    done: set[tuple[str, str]] = set()
    for path in OUT.glob("active_learning_next_cofold_batch*.csv"):
        if path.stem.endswith("_manifest"):
            continue
        if not path.exists() or path.stat().st_size == 0:
            continue
        try:
            with path.open(newline="") as handle:
                for row in csv.DictReader(handle):
                    candidate_id = str(row.get("candidate_id", "")).strip()
                    target = str(row.get("target", "")).strip().lower()
                    if candidate_id and target:
                        done.add((candidate_id, target))
        except Exception:
            continue
    return done


def active_learning_pending_count() -> int:
    if not ACTIVE_LEARNING_NEXT.exists() or ACTIVE_LEARNING_NEXT.stat().st_size == 0:
        return 0
    done = active_learning_completed_pairs()
    count = 0
    try:
        with ACTIVE_LEARNING_NEXT.open(newline="") as handle:
            for row in csv.DictReader(handle):
                candidate_id = str(row.get("candidate_id", "")).strip()
                target = str(row.get("target", "")).strip().lower()
                if not candidate_id or not target:
                    continue
                if target == "mmp1":
                    continue
                if not (MSA_DIR / f"{target}.a3m").exists():
                    continue
                if (candidate_id, target) in done:
                    continue
                if str(row.get("recommended_next_fidelity", "")) != "Boltz-2 cofold":
                    continue
                if str(row.get("already_labeled_pair", "")).lower() == "true":
                    continue
                if str(row.get("synthesis_gate", "")).lower() == "red":
                    continue
                count += 1
    except Exception:
        return 0
    return count


def stability(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not rows:
        return {"stable": False, "reason": "no ok rows"}
    max_rmsd = max(float(row.get("rmsd_max_A", 99.0)) for row in rows)
    max_last = max(float(row.get("rmsd_last_third_A", 99.0)) for row in rows)
    return {
        "stable": max_rmsd <= 2.0 and max_last <= 1.5,
        "max_rmsd_A": round(max_rmsd, 3),
        "max_last_third_A": round(max_last, 3),
        "reason": f"max RMSD {max_rmsd:.2f} A, max last-third {max_last:.2f} A",
    }


def process_running(pattern: str) -> bool:
    proc = subprocess.run(
        ["pgrep", "-f", pattern],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return proc.returncode == 0


def disk_snapshot(path: str) -> dict[str, Any]:
    target = Path(path)
    if not target.exists():
        return {"path": path, "exists": False}
    try:
        total, used, free = shutil.disk_usage(target)
    except Exception as exc:
        return {"path": path, "exists": True, "error": str(exc)}
    gb = 1024**3
    return {
        "path": path,
        "exists": True,
        "total_gb": round(total / gb, 1),
        "used_gb": round(used / gb, 1),
        "free_gb": round(free / gb, 1),
        "used_pct": round((used / total) * 100, 1) if total else None,
    }


def storage_pressure() -> dict[str, Any]:
    disks = {
        "wsl_root": disk_snapshot("/"),
        "windows_c": disk_snapshot("/mnt/c"),
        "windows_d": disk_snapshot("/mnt/d"),
    }
    free_values = [
        float(disk.get("free_gb", 0.0))
        for key, disk in disks.items()
        if key in {"wsl_root", "windows_c"} and disk.get("exists")
    ]
    min_free = min(free_values) if free_values else 0.0
    return {
        "status": "hard_hold" if min_free < MIN_FREE_GB else "warn" if min_free < WARN_FREE_GB else "ok",
        "min_free_gb": round(min_free, 1),
        "min_free_gb_required": MIN_FREE_GB,
        "warn_free_gb": WARN_FREE_GB,
        "disks": disks,
        "note": (
            "Active compute should stay on WSL ext4; completed heavy outputs should be archived to D:."
        ),
    }


def gpu_task(task: str, reason: str, script: str, log_file: str, **extra: Any) -> dict[str, Any]:
    return {
        "task": task,
        "reason": reason,
        "script": script,
        "log_file": log_file,
        **extra,
    }


def plan_gpu() -> dict[str, Any]:
    priority = ok_rows(GPU_PRIORITY)
    if len(priority) < 3:
        return gpu_task(
            "r16_priority_30ns",
            f"priority 30 ns incomplete: {len(priority)}/3 ok",
            "scripts/run_r16_chromanol_topical_priority_30ns.py",
            "pilot/md_r16_chromanol_topical_priority_30ns_auto.log",
        )

    priority_stability = stability(priority)
    if not priority_stability["stable"]:
        return {
            "task": "none",
            "reason": "priority 30 ns has drift; do not auto-extend before review",
            "stability": priority_stability,
        }

    extra = ok_rows(GPU_TGFB1_EXTRA)
    if len(extra) < 3:
        return gpu_task(
            "r16_tgfb1_extra_30ns",
            f"priority 30 ns stable; TGFB1 extra incomplete: {len(extra)}/3 ok",
            "scripts/run_r16_chromanol_topical_tgfb1_extra_30ns.py",
            "pilot/md_r16_chromanol_topical_tgfb1_extra_30ns_auto.log",
            stability=priority_stability,
        )

    extra_stability = stability(extra)
    if not extra_stability["stable"]:
        return {
            "task": "none",
            "reason": "TGFB1 extra 30 ns has drift; do not auto-extend before review",
            "stability": {"priority": priority_stability, "tgfb1_extra": extra_stability},
            "paper_candidate": "manual_review_r16_tgfb1_extra",
        }

    chloro_tgfb1 = ok_rows(GPU_CHLORO_TGFB1)
    if len(chloro_tgfb1) < 2:
        return gpu_task(
            "r16_chloro_tgfb1_30ns",
            f"R16 TGFB1 extra stable; chloro TGFB1 positional check incomplete: {len(chloro_tgfb1)}/2 ok",
            "scripts/run_r16_chromanol_topical_chloro_tgfb1_30ns.py",
            "pilot/md_r16_chromanol_topical_chloro_tgfb1_30ns_auto.log",
            stability={"priority": priority_stability, "tgfb1_extra": extra_stability},
        )

    chloro_tgfb1_stability = stability(chloro_tgfb1)
    if not chloro_tgfb1_stability["stable"]:
        return {
            "task": "none",
            "reason": "chloro TGFB1 positional check has drift; do not auto-extend before review",
            "stability": {
                "priority": priority_stability,
                "tgfb1_extra": extra_stability,
                "chloro_tgfb1": chloro_tgfb1_stability,
            },
            "paper_candidate": "manual_review_r16_chloro_tgfb1",
        }

    chloro_pigment = ok_rows(GPU_CHLORO_PIGMENT)
    if len(chloro_pigment) < 4:
        return gpu_task(
            "r16_chloro_pigment_30ns",
            f"chloro TGFB1 positional check stable; chloro pigment positional check incomplete: {len(chloro_pigment)}/4 ok",
            "scripts/run_r16_chromanol_topical_chloro_pigment_30ns.py",
            "pilot/md_r16_chromanol_topical_chloro_pigment_30ns_auto.log",
            stability={
                "priority": priority_stability,
                "tgfb1_extra": extra_stability,
                "chloro_tgfb1": chloro_tgfb1_stability,
            },
        )

    chloro_pigment_stability = stability(chloro_pigment)
    if not chloro_pigment_stability["stable"]:
        return {
            "task": "none",
            "reason": "chloro pigment positional check has drift; do not auto-extend before review",
            "stability": {
                "priority": priority_stability,
                "tgfb1_extra": extra_stability,
                "chloro_tgfb1": chloro_tgfb1_stability,
                "chloro_pigment": chloro_pigment_stability,
            },
            "paper_candidate": "manual_review_r16_chloro_pigment",
        }

    dimethyl_pigment = ok_rows(GPU_DIMETHYL_PIGMENT)
    if len(dimethyl_pigment) < 6:
        return gpu_task(
            "r16_dimethyl_pigment_30ns",
            f"chloro pigment positional check stable; dimethyl pigment completion incomplete: {len(dimethyl_pigment)}/6 ok",
            "scripts/run_r16_chromanol_topical_dimethyl_pigment_30ns.py",
            "pilot/md_r16_chromanol_topical_dimethyl_pigment_30ns_auto.log",
            stability={
                "priority": priority_stability,
                "tgfb1_extra": extra_stability,
                "chloro_tgfb1": chloro_tgfb1_stability,
                "chloro_pigment": chloro_pigment_stability,
            },
        )

    dimethyl_pigment_stability = stability(dimethyl_pigment)
    if not dimethyl_pigment_stability["stable"]:
        r15_top3_30 = ok_rows(GPU_R15_TOP3_30)
        if len(r15_top3_30) < 3:
            return gpu_task(
                "r15_chromanol_top3_30ns",
                "dimethyl pigment completion shows drift; pivoting to independent R15 triple-safe/systemic 30 ns follow-up",
                "scripts/run_r15_chromanol_top3_30ns.py",
                "pilot/md_r15_chromanol_top3_30ns_auto.log",
                stability={
                    "priority": priority_stability,
                    "tgfb1_extra": extra_stability,
                    "chloro_tgfb1": chloro_tgfb1_stability,
                    "chloro_pigment": chloro_pigment_stability,
                    "dimethyl_pigment": dimethyl_pigment_stability,
                },
                paper_candidate="manual_review_r16_dimethyl_pigment",
            )
        return {
            "task": "none",
            "reason": "dimethyl pigment completion has drift; do not auto-extend before review",
            "stability": {
                "priority": priority_stability,
                "tgfb1_extra": extra_stability,
                "chloro_tgfb1": chloro_tgfb1_stability,
                "chloro_pigment": chloro_pigment_stability,
                "dimethyl_pigment": dimethyl_pigment_stability,
            },
            "paper_candidate": "manual_review_r16_dimethyl_pigment",
        }

    tgfb1_top6_60 = ok_rows(GPU_R16_TGFB1_TOP6_60)
    if len(tgfb1_top6_60) < 6:
        return gpu_task(
            "r16_tgfb1_top6_60ns",
            f"full 18-pair 30 ns matrix stable; TGFB1 top-6 60 ns robustness incomplete: {len(tgfb1_top6_60)}/6 ok",
            "scripts/run_r16_chromanol_topical_tgfb1_top6_60ns.py",
            "pilot/md_r16_chromanol_topical_tgfb1_top6_60ns_auto.log",
            stability={
                "priority": priority_stability,
                "tgfb1_extra": extra_stability,
                "chloro_tgfb1": chloro_tgfb1_stability,
                "chloro_pigment": chloro_pigment_stability,
                "dimethyl_pigment": dimethyl_pigment_stability,
            },
        )

    tgfb1_top6_60_stability = stability(tgfb1_top6_60)
    if not tgfb1_top6_60_stability["stable"]:
        r15_top3_30 = ok_rows(GPU_R15_TOP3_30)
        if len(r15_top3_30) < 3:
            return gpu_task(
                "r15_chromanol_top3_30ns",
                "TGFB1 top-6 60 ns shows drift; pivoting to independent R15 triple-safe/systemic 30 ns follow-up",
                "scripts/run_r15_chromanol_top3_30ns.py",
                "pilot/md_r15_chromanol_top3_30ns_auto.log",
                stability={
                    "r16_dimethyl_pigment": dimethyl_pigment_stability,
                    "r16_tgfb1_top6_60ns": tgfb1_top6_60_stability,
                },
                paper_candidate="manual_review_r16_tgfb1_top6_60ns",
            )
        return {
            "task": "none",
            "reason": "TGFB1 top-6 60 ns robustness panel has drift; do not auto-extend before review",
            "stability": {
                "priority": priority_stability,
                "tgfb1_extra": extra_stability,
                "chloro_tgfb1": chloro_tgfb1_stability,
                "chloro_pigment": chloro_pigment_stability,
                "dimethyl_pigment": dimethyl_pigment_stability,
                "tgfb1_top6_60ns": tgfb1_top6_60_stability,
            },
            "paper_candidate": "manual_review_r16_tgfb1_top6_60ns",
        }

    r15_top3_30 = ok_rows(GPU_R15_TOP3_30)
    if len(r15_top3_30) < 3:
        return gpu_task(
            "r15_chromanol_top3_30ns",
            f"R16 overnight robustness queued; R15 triple-safe/systemic top-3 30 ns incomplete: {len(r15_top3_30)}/3 ok",
            "scripts/run_r15_chromanol_top3_30ns.py",
            "pilot/md_r15_chromanol_top3_30ns_auto.log",
            stability={
                "r16_dimethyl_pigment": dimethyl_pigment_stability,
                "r16_tgfb1_top6_60ns": tgfb1_top6_60_stability,
            },
        )

    r15_top3_30_stability = stability(r15_top3_30)
    if not r15_top3_30_stability["stable"]:
        pigment_rep_60 = ok_rows(GPU_R16_PIGMENT_REP_60)
        if len(pigment_rep_60) < 3:
            return gpu_task(
                "r16_pigment_representative_60ns",
                "R15 top-3 30 ns shows drift; pivoting to independent R16 pigment representative 60 ns fallback",
                "scripts/run_r16_chromanol_topical_pigment_representative_60ns.py",
                "pilot/md_r16_chromanol_topical_pigment_representative_60ns_auto.log",
                stability={
                    "r16_dimethyl_pigment": dimethyl_pigment_stability,
                    "r16_tgfb1_top6_60ns": tgfb1_top6_60_stability,
                    "r15_top3_30ns": r15_top3_30_stability,
                },
                paper_candidate="manual_review_r15_top3_30ns",
            )
        return {
            "task": "none",
            "reason": "R15 top-3 30 ns has drift; do not auto-extend before review",
            "stability": {
                "r16_dimethyl_pigment": dimethyl_pigment_stability,
                "r16_tgfb1_top6_60ns": tgfb1_top6_60_stability,
                "r15_top3_30ns": r15_top3_30_stability,
            },
            "paper_candidate": "manual_review_r15_top3_30ns",
        }

    pigment_rep_60 = ok_rows(GPU_R16_PIGMENT_REP_60)
    if len(pigment_rep_60) < 3:
        return gpu_task(
            "r16_pigment_representative_60ns",
            f"R16 TGFB1 and R15 top-3 follow-ups stable; pigment representative 60 ns fallback incomplete: {len(pigment_rep_60)}/3 ok",
            "scripts/run_r16_chromanol_topical_pigment_representative_60ns.py",
            "pilot/md_r16_chromanol_topical_pigment_representative_60ns_auto.log",
            stability={
                "r16_dimethyl_pigment": dimethyl_pigment_stability,
                "r16_tgfb1_top6_60ns": tgfb1_top6_60_stability,
                "r15_top3_30ns": r15_top3_30_stability,
            },
        )

    pigment_rep_60_stability = stability(pigment_rep_60)
    if not pigment_rep_60_stability["stable"]:
        return {
            "task": "none",
            "reason": "pigment representative 60 ns has drift; do not auto-extend before review",
            "stability": {
                "r16_dimethyl_pigment": dimethyl_pigment_stability,
                "r16_tgfb1_top6_60ns": tgfb1_top6_60_stability,
                "r15_top3_30ns": r15_top3_30_stability,
                "pigment_representative_60ns": pigment_rep_60_stability,
            },
            "paper_candidate": "manual_review_r16_pigment_representative_60ns",
        }

    anchor_triad_100 = ok_rows(GPU_R16_ANCHOR_TRIAD_100)
    if len(anchor_triad_100) < 3:
        return gpu_task(
            "r16_anchor_triad_100ns",
            f"R16 30/60 ns panels stable; paper-strength TGFB1/DCT/TYR anchor 100 ns incomplete: {len(anchor_triad_100)}/3 ok",
            "scripts/run_r16_chromanol_anchor_triad_100ns.py",
            "pilot/md_r16_chromanol_anchor_triad_100ns_auto.log",
            stability={
                "r16_dimethyl_pigment": dimethyl_pigment_stability,
                "r16_tgfb1_top6_60ns": tgfb1_top6_60_stability,
                "r15_top3_30ns": r15_top3_30_stability,
                "pigment_representative_60ns": pigment_rep_60_stability,
            },
        )

    anchor_triad_100_stability = stability(anchor_triad_100)
    if not anchor_triad_100_stability["stable"]:
        return {
            "task": "none",
            "reason": "R16 anchor triad 100 ns has drift; do not auto-extend to 200 ns before review",
            "stability": {
                "priority": priority_stability,
                "tgfb1_extra": extra_stability,
                "chloro_tgfb1": chloro_tgfb1_stability,
                "chloro_pigment": chloro_pigment_stability,
                "dimethyl_pigment": dimethyl_pigment_stability,
                "tgfb1_top6_60ns": tgfb1_top6_60_stability,
                "r15_top3_30ns": r15_top3_30_stability,
                "pigment_representative_60ns": pigment_rep_60_stability,
                "anchor_triad_100ns": anchor_triad_100_stability,
            },
            "paper_candidate": "manual_review_r16_anchor_triad_100ns",
        }

    anchor_triad_200 = ok_rows(GPU_R16_ANCHOR_TRIAD_200)
    if len(anchor_triad_200) < 3:
        return gpu_task(
            "r16_anchor_triad_200ns",
            f"R16 anchor triad 100 ns stable; 200 ns long-horizon confirmation incomplete: {len(anchor_triad_200)}/3 ok",
            "scripts/run_r16_chromanol_anchor_triad_200ns.py",
            "pilot/md_r16_chromanol_anchor_triad_200ns_auto.log",
            stability={
                "r16_dimethyl_pigment": dimethyl_pigment_stability,
                "r16_tgfb1_top6_60ns": tgfb1_top6_60_stability,
                "r15_top3_30ns": r15_top3_30_stability,
                "pigment_representative_60ns": pigment_rep_60_stability,
                "anchor_triad_100ns": anchor_triad_100_stability,
            },
            paper_candidate="r16_chromanol_topical_long_horizon",
        )

    anchor_triad_200_stability = stability(anchor_triad_200)
    r17_rows = r17_generative_rows()
    if anchor_triad_200_stability["stable"] and r17_rows < GPU_R17_GENERATIVE_TARGET_ROWS:
        return gpu_task(
            "r17_chromanol_generative_next32_cofold",
            f"R16 200 ns anchor triad stable; R17 generative chromanol Boltz-2 atlas incomplete: {r17_rows}/{GPU_R17_GENERATIVE_TARGET_ROWS} rows",
            "scripts/run_r17_chromanol_generative_next32_cofold.py",
            "pilot/r17_chromanol_generative_next32_cofold_auto.log",
            stability={
                "r16_dimethyl_pigment": dimethyl_pigment_stability,
                "r16_tgfb1_top6_60ns": tgfb1_top6_60_stability,
                "r15_top3_30ns": r15_top3_30_stability,
                "pigment_representative_60ns": pigment_rep_60_stability,
                "anchor_triad_100ns": anchor_triad_100_stability,
                "anchor_triad_200ns": anchor_triad_200_stability,
            },
            paper_candidate="r17_chromanol_generative_atlas",
            completed_rows=r17_rows,
            target_rows=GPU_R17_GENERATIVE_TARGET_ROWS,
        )

    if anchor_triad_200_stability["stable"] and r17_rows >= GPU_R17_GENERATIVE_TARGET_ROWS:
        r17_top_green_10 = ok_rows(GPU_R17_TOP_GREEN_10)
        if len(r17_top_green_10) < 3:
            return gpu_task(
                "r17_chromanol_generative_top_green_10ns",
                f"R17 generative atlas complete; top green-target 10 ns screen incomplete: {len(r17_top_green_10)}/3 ok",
                "scripts/run_r17_chromanol_generative_top_green_10ns.py",
                "pilot/md_r17_chromanol_generative_top_green_10ns_auto.log",
                stability={
                    "anchor_triad_200ns": anchor_triad_200_stability,
                },
                paper_candidate="r17_chromanol_generative_atlas",
                completed_rows=r17_rows,
                target_rows=GPU_R17_GENERATIVE_TARGET_ROWS,
            )

        r17_top_green_10_stability = stability(r17_top_green_10)
        if not r17_top_green_10_stability["stable"]:
            return {
                "task": "none",
                "reason": "R17 top green-target 10 ns screen has drift; do not auto-extend before review",
                "stability": {
                    "anchor_triad_200ns": anchor_triad_200_stability,
                    "r17_top_green_10ns": r17_top_green_10_stability,
                },
                "paper_candidate": "manual_review_r17_top_green_10ns",
            }

        r17_top_green_30 = ok_rows(GPU_R17_TOP_GREEN_30)
        if len(r17_top_green_30) < 3:
            return gpu_task(
                "r17_chromanol_generative_top_green_30ns",
                f"R17 top green-target 10 ns screen stable; 30 ns follow-up incomplete: {len(r17_top_green_30)}/3 ok",
                "scripts/run_r17_chromanol_generative_top_green_30ns.py",
                "pilot/md_r17_chromanol_generative_top_green_30ns_auto.log",
                stability={
                    "anchor_triad_200ns": anchor_triad_200_stability,
                    "r17_top_green_10ns": r17_top_green_10_stability,
                },
                paper_candidate="r17_chromanol_generative_atlas",
                completed_rows=r17_rows,
                target_rows=GPU_R17_GENERATIVE_TARGET_ROWS,
            )

        r17_top_green_30_stability = stability(r17_top_green_30)
        if not r17_top_green_30_stability["stable"]:
            return {
                "task": "none",
                "reason": "R17 top green-target 30 ns follow-up has drift; do not auto-extend before review",
                "stability": {
                    "anchor_triad_200ns": anchor_triad_200_stability,
                    "r17_top_green_10ns": r17_top_green_10_stability,
                    "r17_top_green_30ns": r17_top_green_30_stability,
                },
                "paper_candidate": "manual_review_r17_top_green_30ns",
            }

        r17_top_green_60 = ok_rows(GPU_R17_TOP_GREEN_60)
        if len(r17_top_green_60) < 3:
            return gpu_task(
                "r17_chromanol_generative_top_green_60ns",
                f"R17 top green-target 30 ns follow-up stable; 60 ns robustness incomplete: {len(r17_top_green_60)}/3 ok",
                "scripts/run_r17_chromanol_generative_top_green_60ns.py",
                "pilot/md_r17_chromanol_generative_top_green_60ns_auto.log",
                stability={
                    "anchor_triad_200ns": anchor_triad_200_stability,
                    "r17_top_green_10ns": r17_top_green_10_stability,
                    "r17_top_green_30ns": r17_top_green_30_stability,
                },
                paper_candidate="r17_chromanol_generative_atlas",
                completed_rows=r17_rows,
                target_rows=GPU_R17_GENERATIVE_TARGET_ROWS,
            )

        r17_top_green_60_stability = stability(r17_top_green_60)
        if not r17_top_green_60_stability["stable"]:
            return {
                "task": "none",
                "reason": "R17 top green-target 60 ns robustness panel has drift; do not auto-extend before review",
                "stability": {
                    "anchor_triad_200ns": anchor_triad_200_stability,
                    "r17_top_green_10ns": r17_top_green_10_stability,
                    "r17_top_green_30ns": r17_top_green_30_stability,
                    "r17_top_green_60ns": r17_top_green_60_stability,
                },
                "paper_candidate": "manual_review_r17_top_green_60ns",
            }

        r17_next_green_10 = ok_rows(GPU_R17_NEXT_GREEN_10)
        if len(r17_next_green_10) < 3:
            return gpu_task(
                "r17_chromanol_generative_next_green_10ns",
                f"R17 top green-target 60 ns stable; next non-duplicate DCT/TYR 10 ns screen incomplete: {len(r17_next_green_10)}/3 ok",
                "scripts/run_r17_chromanol_generative_next_green_10ns.py",
                "pilot/md_r17_chromanol_generative_next_green_10ns_auto.log",
                stability={
                    "anchor_triad_200ns": anchor_triad_200_stability,
                    "r17_top_green_10ns": r17_top_green_10_stability,
                    "r17_top_green_30ns": r17_top_green_30_stability,
                    "r17_top_green_60ns": r17_top_green_60_stability,
                },
                paper_candidate="r17_chromanol_generative_atlas",
                completed_rows=r17_rows,
                target_rows=GPU_R17_GENERATIVE_TARGET_ROWS,
            )

        r17_next_green_10_stability = stability(r17_next_green_10)
        if not r17_next_green_10_stability["stable"]:
            return {
                "task": "none",
                "reason": "R17 next green-target 10 ns screen has drift; do not auto-extend before review",
                "stability": {
                    "anchor_triad_200ns": anchor_triad_200_stability,
                    "r17_top_green_10ns": r17_top_green_10_stability,
                    "r17_top_green_30ns": r17_top_green_30_stability,
                    "r17_top_green_60ns": r17_top_green_60_stability,
                    "r17_next_green_10ns": r17_next_green_10_stability,
                },
                "paper_candidate": "manual_review_r17_next_green_10ns",
            }

        r17_next_green_30 = ok_rows(GPU_R17_NEXT_GREEN_30)
        if len(r17_next_green_30) < 3:
            return gpu_task(
                "r17_chromanol_generative_next_green_30ns",
                f"R17 next green-target 10 ns stable; 30 ns follow-up incomplete: {len(r17_next_green_30)}/3 ok",
                "scripts/run_r17_chromanol_generative_next_green_30ns.py",
                "pilot/md_r17_chromanol_generative_next_green_30ns_auto.log",
                stability={
                    "anchor_triad_200ns": anchor_triad_200_stability,
                    "r17_top_green_10ns": r17_top_green_10_stability,
                    "r17_top_green_30ns": r17_top_green_30_stability,
                    "r17_top_green_60ns": r17_top_green_60_stability,
                    "r17_next_green_10ns": r17_next_green_10_stability,
                },
                paper_candidate="r17_chromanol_generative_atlas",
                completed_rows=r17_rows,
                target_rows=GPU_R17_GENERATIVE_TARGET_ROWS,
            )

        r17_next_green_30_stability = stability(r17_next_green_30)
        if not r17_next_green_30_stability["stable"]:
            return {
                "task": "none",
                "reason": "R17 next green-target 30 ns follow-up has drift; do not auto-extend before review",
                "stability": {
                    "anchor_triad_200ns": anchor_triad_200_stability,
                    "r17_top_green_10ns": r17_top_green_10_stability,
                    "r17_top_green_30ns": r17_top_green_30_stability,
                    "r17_top_green_60ns": r17_top_green_60_stability,
                    "r17_next_green_10ns": r17_next_green_10_stability,
                    "r17_next_green_30ns": r17_next_green_30_stability,
                },
                "paper_candidate": "manual_review_r17_next_green_30ns",
            }

        r17_next_green_60 = ok_rows(GPU_R17_NEXT_GREEN_60)
        if len(r17_next_green_60) < 3:
            return gpu_task(
                "r17_chromanol_generative_next_green_60ns",
                f"R17 next green-target 30 ns stable; 60 ns follow-up incomplete: {len(r17_next_green_60)}/3 ok",
                "scripts/run_r17_chromanol_generative_next_green_60ns.py",
                "pilot/md_r17_chromanol_generative_next_green_60ns_auto.log",
                stability={
                    "anchor_triad_200ns": anchor_triad_200_stability,
                    "r17_top_green_10ns": r17_top_green_10_stability,
                    "r17_top_green_30ns": r17_top_green_30_stability,
                    "r17_top_green_60ns": r17_top_green_60_stability,
                    "r17_next_green_10ns": r17_next_green_10_stability,
                    "r17_next_green_30ns": r17_next_green_30_stability,
                },
                paper_candidate="r17_chromanol_generative_atlas",
                completed_rows=r17_rows,
                target_rows=GPU_R17_GENERATIVE_TARGET_ROWS,
            )

        r17_next_green_60_stability = stability(r17_next_green_60)
        if not r17_next_green_60_stability["stable"]:
            return {
                "task": "none",
                "reason": "R17 next green-target 60 ns robustness panel has drift; do not auto-extend before review",
                "stability": {
                    "anchor_triad_200ns": anchor_triad_200_stability,
                    "r17_top_green_10ns": r17_top_green_10_stability,
                    "r17_top_green_30ns": r17_top_green_30_stability,
                    "r17_top_green_60ns": r17_top_green_60_stability,
                    "r17_next_green_10ns": r17_next_green_10_stability,
                    "r17_next_green_30ns": r17_next_green_30_stability,
                    "r17_next_green_60ns": r17_next_green_60_stability,
                },
                "paper_candidate": "manual_review_r17_next_green_60ns",
            }

        r17_expanded_green_10 = ok_rows(GPU_R17_EXPANDED_GREEN_10)
        if len(r17_expanded_green_10) < 3:
            return gpu_task(
                "r17_chromanol_generative_expanded_green_10ns",
                f"R17 top/next green-target 60 ns panels stable; expanded safety-green 10 ns screen incomplete: {len(r17_expanded_green_10)}/3 ok",
                "scripts/run_r17_chromanol_generative_expanded_green_10ns.py",
                "pilot/md_r17_chromanol_generative_expanded_green_10ns_auto.log",
                stability={
                    "anchor_triad_200ns": anchor_triad_200_stability,
                    "r17_top_green_10ns": r17_top_green_10_stability,
                    "r17_top_green_30ns": r17_top_green_30_stability,
                    "r17_top_green_60ns": r17_top_green_60_stability,
                    "r17_next_green_10ns": r17_next_green_10_stability,
                    "r17_next_green_30ns": r17_next_green_30_stability,
                    "r17_next_green_60ns": r17_next_green_60_stability,
                },
                paper_candidate="r17_chromanol_generative_atlas",
                completed_rows=r17_rows,
                target_rows=GPU_R17_GENERATIVE_TARGET_ROWS,
            )

        r17_expanded_green_10_stability = stability(r17_expanded_green_10)
        if not r17_expanded_green_10_stability["stable"]:
            return {
                "task": "none",
                "reason": "R17 expanded green-target 10 ns screen has drift; do not auto-extend before review",
                "stability": {
                    "anchor_triad_200ns": anchor_triad_200_stability,
                    "r17_top_green_10ns": r17_top_green_10_stability,
                    "r17_top_green_30ns": r17_top_green_30_stability,
                    "r17_top_green_60ns": r17_top_green_60_stability,
                    "r17_next_green_10ns": r17_next_green_10_stability,
                    "r17_next_green_30ns": r17_next_green_30_stability,
                    "r17_next_green_60ns": r17_next_green_60_stability,
                    "r17_expanded_green_10ns": r17_expanded_green_10_stability,
                },
                "paper_candidate": "manual_review_r17_expanded_green_10ns",
            }

        r17_expanded_green_30 = ok_rows(GPU_R17_EXPANDED_GREEN_30)
        if len(r17_expanded_green_30) < 3:
            return gpu_task(
                "r17_chromanol_generative_expanded_green_30ns",
                f"R17 expanded green-target 10 ns screen stable; 30 ns follow-up incomplete: {len(r17_expanded_green_30)}/3 ok",
                "scripts/run_r17_chromanol_generative_expanded_green_30ns.py",
                "pilot/md_r17_chromanol_generative_expanded_green_30ns_auto.log",
                stability={
                    "anchor_triad_200ns": anchor_triad_200_stability,
                    "r17_top_green_10ns": r17_top_green_10_stability,
                    "r17_top_green_30ns": r17_top_green_30_stability,
                    "r17_top_green_60ns": r17_top_green_60_stability,
                    "r17_next_green_10ns": r17_next_green_10_stability,
                    "r17_next_green_30ns": r17_next_green_30_stability,
                    "r17_next_green_60ns": r17_next_green_60_stability,
                    "r17_expanded_green_10ns": r17_expanded_green_10_stability,
                },
                paper_candidate="r17_chromanol_generative_atlas",
                completed_rows=r17_rows,
                target_rows=GPU_R17_GENERATIVE_TARGET_ROWS,
            )

        r17_expanded_green_30_stability = stability(r17_expanded_green_30)
        if not r17_expanded_green_30_stability["stable"]:
            return {
                "task": "none",
                "reason": "R17 expanded green-target 30 ns follow-up has drift; do not auto-extend before review",
                "stability": {
                    "anchor_triad_200ns": anchor_triad_200_stability,
                    "r17_top_green_10ns": r17_top_green_10_stability,
                    "r17_top_green_30ns": r17_top_green_30_stability,
                    "r17_top_green_60ns": r17_top_green_60_stability,
                    "r17_next_green_10ns": r17_next_green_10_stability,
                    "r17_next_green_30ns": r17_next_green_30_stability,
                    "r17_next_green_60ns": r17_next_green_60_stability,
                    "r17_expanded_green_10ns": r17_expanded_green_10_stability,
                    "r17_expanded_green_30ns": r17_expanded_green_30_stability,
                },
                "paper_candidate": "manual_review_r17_expanded_green_30ns",
            }

        r17_expanded_green_60 = ok_rows(GPU_R17_EXPANDED_GREEN_60)
        if len(r17_expanded_green_60) < 3:
            return gpu_task(
                "r17_chromanol_generative_expanded_green_60ns",
                f"R17 expanded green-target 30 ns follow-up stable; 60 ns follow-up incomplete: {len(r17_expanded_green_60)}/3 ok",
                "scripts/run_r17_chromanol_generative_expanded_green_60ns.py",
                "pilot/md_r17_chromanol_generative_expanded_green_60ns_auto.log",
                stability={
                    "anchor_triad_200ns": anchor_triad_200_stability,
                    "r17_top_green_10ns": r17_top_green_10_stability,
                    "r17_top_green_30ns": r17_top_green_30_stability,
                    "r17_top_green_60ns": r17_top_green_60_stability,
                    "r17_next_green_10ns": r17_next_green_10_stability,
                    "r17_next_green_30ns": r17_next_green_30_stability,
                    "r17_next_green_60ns": r17_next_green_60_stability,
                    "r17_expanded_green_10ns": r17_expanded_green_10_stability,
                    "r17_expanded_green_30ns": r17_expanded_green_30_stability,
                },
                paper_candidate="r17_chromanol_generative_atlas",
                completed_rows=r17_rows,
                target_rows=GPU_R17_GENERATIVE_TARGET_ROWS,
            )

    r17_status: dict[str, Any] = {}
    if r17_rows >= GPU_R17_GENERATIVE_TARGET_ROWS:
        r17_top_green_10 = ok_rows(GPU_R17_TOP_GREEN_10)
        r17_top_green_30 = ok_rows(GPU_R17_TOP_GREEN_30)
        r17_top_green_60 = ok_rows(GPU_R17_TOP_GREEN_60)
        r17_next_green_10 = ok_rows(GPU_R17_NEXT_GREEN_10)
        r17_next_green_30 = ok_rows(GPU_R17_NEXT_GREEN_30)
        r17_next_green_60 = ok_rows(GPU_R17_NEXT_GREEN_60)
        r17_expanded_green_10 = ok_rows(GPU_R17_EXPANDED_GREEN_10)
        r17_expanded_green_30 = ok_rows(GPU_R17_EXPANDED_GREEN_30)
        r17_expanded_green_60 = ok_rows(GPU_R17_EXPANDED_GREEN_60)
        if len(r17_top_green_10) >= 3:
            r17_status["r17_top_green_10ns"] = stability(r17_top_green_10)
        if len(r17_top_green_30) >= 3:
            r17_status["r17_top_green_30ns"] = stability(r17_top_green_30)
        if len(r17_top_green_60) >= 3:
            r17_status["r17_top_green_60ns"] = stability(r17_top_green_60)
        if len(r17_next_green_10) >= 3:
            r17_status["r17_next_green_10ns"] = stability(r17_next_green_10)
        if len(r17_next_green_30) >= 3:
            r17_status["r17_next_green_30ns"] = stability(r17_next_green_30)
        if len(r17_next_green_60) >= 3:
            r17_status["r17_next_green_60ns"] = stability(r17_next_green_60)
        if len(r17_expanded_green_10) >= 3:
            r17_status["r17_expanded_green_10ns"] = stability(r17_expanded_green_10)
        if len(r17_expanded_green_30) >= 3:
            r17_status["r17_expanded_green_30ns"] = stability(r17_expanded_green_30)
        if len(r17_expanded_green_60) >= 3:
            r17_status["r17_expanded_green_60ns"] = stability(r17_expanded_green_60)

    paper_ready = bool(extra_stability["stable"])
    final_reason = "GPU validation queue complete through R16 anchor triad 200 ns for current chromanol plan"
    if r17_status.get("r17_expanded_green_60ns", {}).get("stable"):
        final_reason = (
            "GPU validation queue complete through R16 anchor triad 200 ns and "
            "R17 generative top/next/expanded green-target 10/30/60 ns panels"
        )
    elif r17_status.get("r17_next_green_60ns", {}).get("stable"):
        final_reason = (
            "GPU validation queue complete through R16 anchor triad 200 ns and "
            "R17 generative top/next green-target 10/30/60 ns panels"
        )
    final_stability = {
        "priority": priority_stability,
        "tgfb1_extra": extra_stability,
        "chloro_tgfb1": chloro_tgfb1_stability,
        "chloro_pigment": chloro_pigment_stability,
        "dimethyl_pigment": dimethyl_pigment_stability,
        "tgfb1_top6_60ns": tgfb1_top6_60_stability,
        "r15_top3_30ns": r15_top3_30_stability,
        "pigment_representative_60ns": pigment_rep_60_stability,
        "anchor_triad_100ns": anchor_triad_100_stability,
        "anchor_triad_200ns": anchor_triad_200_stability,
        **r17_status,
    }
    active_learning_pending = active_learning_pending_count()
    if active_learning_pending > 0:
        return gpu_task(
            "active_learning_next_boltz2_cofold",
            (
                f"{final_reason}; active-learning has {active_learning_pending} "
                "unlabeled non-MMP1 short-triage pairs pending"
            ),
            "scripts/run_active_learning_next_cofold.py",
            "pilot/active_learning_next_cofold_auto.log",
            stability=final_stability,
            paper_candidate="active_learning_np_assay_atlas",
            pending_pairs=active_learning_pending,
        )
    return {
        "task": "none",
        "reason": final_reason,
        "stability": final_stability,
        "paper_candidate": "r17_chromanol_generative_atlas"
        if r17_status.get("r17_next_green_60ns", {}).get("stable")
        else "r16_chromanol_topical"
        if paper_ready and anchor_triad_200_stability["stable"]
        else "manual_review_overnight_chromanol",
        "completed_rows": r17_rows,
        "target_rows": GPU_R17_GENERATIVE_TARGET_ROWS,
    }


def plan_cpu() -> dict[str, Any]:
    for topn, hetero, confs, workers, out in CPU_TASKS:
        out_path = OUT / out
        if out_path.exists() and out_path.stat().st_size > 0:
            continue
        if process_running(f"cpu_xtb_npass_top_refine.py .*--out {out}"):
            continue
        return {
            "task": "xtb_refine",
            "spec": f"{topn} {hetero} {confs} {workers} {out}",
            "reason": f"next missing xTB refinement: {out}",
        }
    return {
        "task": "none",
        "spec": "none",
        "reason": f"all configured xTB refinement outputs exist or are running through {max(parse_conf_ladder())}conf",
    }


def build_plan() -> dict[str, Any]:
    queue_policy: dict[str, Any] = {}
    if QUEUE_POLICY_PATH.exists():
        try:
            data = json.loads(QUEUE_POLICY_PATH.read_text())
            if isinstance(data, dict):
                queue_policy = data
        except Exception:
            queue_policy = {"error": "failed_to_read_auto_queue_decision_policy"}
    storage = storage_pressure()
    if storage["status"] == "hard_hold":
        gpu = {
            "task": "none",
            "reason": f"storage hard hold: min free {storage['min_free_gb']} GB < {MIN_FREE_GB} GB",
        }
        cpu = {
            "task": "none",
            "spec": "none",
            "reason": f"storage hard hold: min free {storage['min_free_gb']} GB < {MIN_FREE_GB} GB",
        }
    else:
        gpu = plan_gpu()
        cpu = plan_cpu()

    plan = {
        "gpu": gpu,
        "cpu": cpu,
        "storage_pressure": storage,
        "world_class_queue_policy": queue_policy.get("global_queue_policy", {}),
        "world_class_readiness_counts": queue_policy.get("readiness_counts", {}),
        "world_class_heavy_compute_permission_counts": queue_policy.get("heavy_compute_permission_counts", {}),
        "notes": [
            "This planner is deterministic and result-aware; it is not an LLM process.",
            "LLM-level reprioritization is handled by scripts/codex_curator_loop.sh when enabled.",
            "World-class gap closure decisions are summarized in pilot/auto_queue_decision_policy.json and docs/WORLD_CLASS_GAP_CLOSURE.md.",
            "Storage hard-hold blocks new large launches when Windows C: or WSL root free space is below GENESIS_MIN_FREE_GB.",
        ],
    }
    PLAN_PATH.write_text(json.dumps(plan, indent=2))
    return plan


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--slot", choices=["gpu", "cpu", "all"], default="all")
    parser.add_argument("--field", choices=["json", "task", "reason", "spec", "script", "log_file"], default="json")
    args = parser.parse_args()

    plan = build_plan()
    obj: Any = plan if args.slot == "all" else plan[args.slot]
    if args.field == "json":
        print(json.dumps(obj, indent=2))
    else:
        print(obj.get(args.field, "none"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
