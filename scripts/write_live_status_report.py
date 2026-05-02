"""Write a concise Korean live status report for Genesis automation."""
from __future__ import annotations

import csv
import json
import subprocess
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
PILOT = ROOT / "pilot"
CPU_OUT = PILOT / "cpu_meaningful"
OUT = PILOT / "live_status_report.md"


def run(cmd: list[str]) -> str:
    try:
        proc = subprocess.run(
            cmd,
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
    except Exception as exc:
        return f"error: {exc}"
    text = (proc.stdout or proc.stderr or "").strip()
    return text if text else "(no output)"


def pgrep(pattern: str) -> list[str]:
    out = run(["pgrep", "-af", pattern])
    if out == "(no output)" or out.startswith("error:"):
        return []
    return [line for line in out.splitlines() if "pgrep -af" not in line]


def read_json(path: Path) -> list[dict[str, object]]:
    if not path.exists():
        return []
    try:
        rows = json.loads(path.read_text())
    except Exception:
        return []
    return rows if isinstance(rows, list) else []


def csv_rows(path: Path) -> int:
    if not path.exists() or path.stat().st_size == 0:
        return 0
    try:
        with path.open(newline="", encoding="utf-8") as handle:
            return max(sum(1 for _ in csv.reader(handle)) - 1, 0)
    except Exception:
        return 0


EXPECTED_MD_TOTALS = {
    "md_r16_chromanol_topical_pigment_representative_60ns": 3,
    "md_r15_chromanol_top3_30ns": 3,
    "md_r16_chromanol_topical_tgfb1_top6_60ns": 6,
    "md_r16_chromanol_topical_dimethyl_pigment_30ns": 6,
    "md_r16_chromanol_topical_chloro_pigment_30ns": 4,
    "md_r16_chromanol_topical_chloro_tgfb1_30ns": 2,
    "md_r16_chromanol_topical_tgfb1_extra_30ns": 3,
    "md_r16_chromanol_topical_priority_30ns": 3,
}


def ok_count(path: Path) -> tuple[int, int]:
    rows = read_json(path)
    expected = EXPECTED_MD_TOTALS.get(path.parent.name, 0)
    return sum(1 for row in rows if row.get("status") == "ok"), max(len(rows), expected)


def latest_lines(path: Path, n: int) -> list[str]:
    if not path.exists():
        return []
    try:
        return path.read_text().splitlines()[-n:]
    except Exception:
        return []


def main() -> int:
    now = datetime.now(ZoneInfo("Asia/Seoul")).isoformat(timespec="seconds")
    gpu = run(
        [
            "nvidia-smi",
            "--query-gpu=utilization.gpu,memory.used,memory.total",
            "--format=csv,noheader",
        ]
    )
    gpu_apps = pgrep(
        "run_r16|run_extended|run_r15|boltz predict|openmm|chromanol"
    )
    cpu_sample = run(["bash", "-lc", "vmstat 1 2 | tail -1"])
    load = run(["uptime"])
    top_cpu = run(["bash", "-lc", "ps aux --sort=-%cpu | head -8"])
    storage_df = run(["df", "-hT", "/", "/mnt/c", "/mnt/d"])
    storage_report = run(
        ["bash", "-lc", "python3 -m json.tool pilot/storage_pressure_report.json 2>/dev/null | head -120"]
    )

    queue_lines = pgrep(
        "monitor_supervisor|auto_queue_cpu_gpu_daemon|morning_queue_guard|codex_curator_loop|cpu_xtb_npass_top_refine|cpu_5000"
    )
    xtb_count = run(["pgrep", "-fc", "scripts/cpu_xtb_npass_top_refine.py"])
    protected_count = run(
        [
            "pgrep",
            "-fc",
            "cpu_5000_conf_npass_rank1k_2k.py|cpu_5000_conformers_npass_top500_round2.py",
        ]
    )

    md_paths = [
        PILOT / "md_r16_chromanol_topical_pigment_representative_60ns/summary.json",
        PILOT / "md_r15_chromanol_top3_30ns/summary.json",
        PILOT / "md_r16_chromanol_topical_tgfb1_top6_60ns/summary.json",
        PILOT / "md_r16_chromanol_topical_dimethyl_pigment_30ns/summary.json",
        PILOT / "md_r16_chromanol_topical_chloro_pigment_30ns/summary.json",
        PILOT / "md_r16_chromanol_topical_chloro_tgfb1_30ns/summary.json",
        PILOT / "md_r16_chromanol_topical_tgfb1_extra_30ns/summary.json",
        PILOT / "md_r16_chromanol_topical_priority_30ns/summary.json",
    ]
    md_summary = []
    for path in md_paths:
        ok, total = ok_count(path)
        label = path.parent.name
        md_summary.append(f"- `{label}`: ok `{ok}/{total}`")

    latest_xtb = run(
        [
            "bash",
            "-lc",
            "ls -lt pilot/cpu_meaningful/xtb_npass_top*_refine_*conf.csv 2>/dev/null | head -8",
        ]
    )
    planner = run(
        ["bash", "-lc", "python3 scripts/auto_result_planner.py --slot all --field json 2>/dev/null"]
    )
    world_policy = run(
        ["bash", "-lc", "python3 -m json.tool pilot/auto_queue_decision_policy.json 2>/dev/null | head -120"]
    )
    creative_rows = csv_rows(CPU_OUT / "creative_discovery_gap_matrix.csv")
    creative_policy = run(
        ["bash", "-lc", "python3 -m json.tool pilot/creative_discovery_queue_policy.json 2>/dev/null | head -120"]
    )
    active_learning_cofold_rows = sum(
        csv_rows(path)
        for path in CPU_OUT.glob("active_learning_next_cofold_batch*.csv")
        if not path.stem.endswith("_manifest")
    )
    active_learning_manifest_rows = sum(
        csv_rows(path) for path in CPU_OUT.glob("active_learning_next_cofold_batch*_manifest.csv")
    )
    actions = latest_lines(PILOT / "codex_curator_actions.log", 8)

    report = [
        "# Genesis Medicine Live Status",
        "",
        f"- timestamp: `{now}`",
        "- note: 채팅창으로 선제 푸시 보고는 불가하므로, 이 파일을 주기 갱신하는 heartbeat로 사용합니다.",
        "",
        "## Compute",
        "",
        f"- GPU: `{gpu}`",
        f"- CPU/load: `{load}`",
        f"- CPU vmstat sample: `{cpu_sample}`",
        f"- active xTB refine process count: `{xtb_count}`",
        f"- protected NPASS process count: `{protected_count}`",
        "",
        "## Storage",
        "",
        "```text",
        storage_df,
        "```",
        "",
        "```json",
        storage_report,
        "```",
        "",
        "## Active GPU Jobs",
        "",
        "```text",
        "\n".join(gpu_apps[:20]) if gpu_apps else "(none)",
        "```",
        "",
        "## Active Queue Processes",
        "",
        "```text",
        "\n".join(queue_lines[:60]) if queue_lines else "(none)",
        "```",
        "",
        "## R16 MD Summaries",
        "",
        *md_summary,
        "",
        "## Latest xTB Outputs",
        "",
        "```text",
        latest_xtb,
        "```",
        "",
        "## Planner",
        "",
        "```json",
        planner,
        "```",
        "",
        "## Creative Discovery",
        "",
        f"- creative gap rows: `{creative_rows}`",
        f"- active-learning short-cofold manifest rows: `{active_learning_manifest_rows}`",
        f"- active-learning completed short-cofold rows: `{active_learning_cofold_rows}`",
        "",
        "```json",
        creative_policy,
        "```",
        "",
        "## World-Class Queue Policy",
        "",
        "```json",
        world_policy,
        "```",
        "",
        "## Recent Curator Actions",
        "",
        "```text",
        "\n".join(actions) if actions else "(none)",
        "```",
        "",
        "## Top CPU",
        "",
        "```text",
        top_cpu,
        "```",
        "",
    ]
    OUT.write_text("\n".join(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
