"""Write a storage pressure snapshot for Genesis compute operations.

This report is intentionally separate from the queue daemon. It can run on
demand without changing active jobs, while the planner uses a lightweight df
check to avoid starting large work when host free space becomes unsafe.
"""
from __future__ import annotations

import json
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
PILOT = ROOT / "pilot"
DOC = ROOT / "docs/STORAGE_OPERATIONS_PLAN.md"
OUT = PILOT / "storage_pressure_report.json"

WARN_FREE_GB = 200.0
HARD_HOLD_FREE_GB = 80.0


def disk_usage(path: Path) -> dict[str, object]:
    if not path.exists():
        return {"path": str(path), "exists": False}
    total, used, free = shutil.disk_usage(path)
    gb = 1024**3
    return {
        "path": str(path),
        "exists": True,
        "total_gb": round(total / gb, 1),
        "used_gb": round(used / gb, 1),
        "free_gb": round(free / gb, 1),
        "used_pct": round((used / total) * 100, 1) if total else None,
    }


def du_kib(path: Path) -> int:
    try:
        proc = subprocess.run(
            ["du", "-sk", str(path)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
    except Exception:
        return -1
    if proc.returncode != 0:
        return -1
    try:
        return int(proc.stdout.split()[0])
    except Exception:
        return -1


def child_sizes(path: Path, limit: int = 20) -> list[dict[str, object]]:
    if not path.exists():
        return []
    rows: list[dict[str, object]] = []
    for child in path.iterdir():
        size = du_kib(child)
        if size < 0:
            continue
        rows.append(
            {
                "path": str(child.relative_to(ROOT)),
                "gb": round(size / 1024 / 1024, 2),
            }
        )
    rows.sort(key=lambda row: float(row["gb"]), reverse=True)
    return rows[:limit]


def pressure_label(free_gb: float) -> str:
    if free_gb < HARD_HOLD_FREE_GB:
        return "hard_hold"
    if free_gb < WARN_FREE_GB:
        return "warn"
    return "ok"


def main() -> int:
    now = datetime.now(ZoneInfo("Asia/Seoul")).isoformat(timespec="seconds")
    disks = {
        "wsl_root": disk_usage(Path("/")),
        "windows_c": disk_usage(Path("/mnt/c")),
        "windows_d": disk_usage(Path("/mnt/d")),
    }
    c_free = float(disks["windows_c"].get("free_gb", 0.0) or 0.0)
    root_free = float(disks["wsl_root"].get("free_gb", 0.0) or 0.0)
    status = {
        "timestamp": now,
        "status": pressure_label(min(c_free, root_free)),
        "thresholds": {
            "warn_free_gb": WARN_FREE_GB,
            "hard_hold_free_gb": HARD_HOLD_FREE_GB,
        },
        "disks": disks,
        "project_top": child_sizes(ROOT),
        "pilot_top": child_sizes(PILOT),
        "policy": {
            "active_compute": "keep on native WSL ext4 for Boltz/OpenMM/xTB performance",
            "archive_target": "/mnt/d/genesis_archive for completed heavy outputs",
            "best_long_term_fix": "export/import the Ubuntu WSL distro to D: so ext4.vhdx grows on D: instead of C:",
            "do_not_move_while_running": [
                "pilot/cpu_meaningful",
                "currently active MD/cofold output directories",
                "protected NPASS queue outputs",
            ],
        },
    }
    OUT.write_text(json.dumps(status, indent=2))

    pilot_rows = "\n".join(
        f"| `{row['path']}` | {row['gb']} |" for row in status["pilot_top"]
    )
    project_rows = "\n".join(
        f"| `{row['path']}` | {row['gb']} |" for row in status["project_top"]
    )
    doc = f"""# Genesis Storage Operations Plan

- timestamp: `{now}`
- storage status: `{status['status']}`
- WSL root free: `{root_free:.1f} GB`
- Windows C free: `{c_free:.1f} GB`
- Windows D free: `{float(disks['windows_d'].get('free_gb', 0.0) or 0.0):.1f} GB`

## Operating Policy

1. Keep active Boltz/OpenMM/xTB work on native WSL ext4. `/mnt/d` is acceptable for
   archive files, but it is slower for many small files.
2. Use D: as the heavy-output archive target: `/mnt/d/genesis_archive`.
3. The best long-term fix is moving the Ubuntu WSL distro to D: with
   `wsl --export` and `wsl --import`, after active jobs are paused and backed up.
4. Do not move `pilot/cpu_meaningful` or currently active output directories while
   queue workers are running.
5. If Windows C or WSL root free space drops below `{HARD_HOLD_FREE_GB:.0f} GB`,
   the queue planner should hold new large tasks until space is recovered.

## Largest Project Directories

| path | GB |
|---|---:|
{project_rows}

## Largest Pilot Directories

| path | GB |
|---|---:|
{pilot_rows}
"""
    DOC.write_text(doc)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
