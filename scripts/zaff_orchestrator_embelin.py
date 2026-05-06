"""ZAFF orchestrator — auto-trigger Phase 3-5 once 60 ns MD completes.

Polls pilot/md_r14_5_r12_23_herbal_xref_60ns/summary.json every 10 minutes.
When all 4 jobs are status=ok and ns_simulated=60.0, advances through:
  Phase 3 (sanity MD, 5 ns NPT, ~2 h GPU)
  -> Phase 4 (complex builder, 30-45 min CPU)
  -> Phase 5 (ABFE production, 12-18 h GPU)

Each phase produces a state file (PHASE3_PASS, PHASE4_OK, PHASE5_OK or
PHASE5_INCONCLUSIVE) which the next phase checks. Idempotent: re-running
the orchestrator skips already-completed phases.

Run:
  python scripts/zaff_orchestrator.py [--poll-seconds 600] [--skip-60ns-wait]
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOG = ROOT / "pilot/abfe_mmp1_holo_zn_embelin/orchestrator.log"
LOG.parent.mkdir(parents=True, exist_ok=True)

MD60_SUMMARY = ROOT / "pilot/md_r14_5_r12_23_herbal_xref_60ns/summary.json"
PHASE3_SCRIPT = ROOT / "scripts/zaff_phase3_sanity_md.py"
PHASE4_SCRIPT = ROOT / "scripts/zaff_phase4_build_complex_embelin.py"
PHASE5_SCRIPT = ROOT / "scripts/zaff_phase5_abfe_production_embelin.py"

PHASE3_GATE = ROOT / "pilot/abfe_mmp1_holo_zn_embelin/sanity_md/PHASE3_PASS"
PHASE4_GATE = ROOT / "pilot/abfe_mmp1_holo_zn_embelin/complex/PHASE4_OK"
PHASE5A_GATE = ROOT / "pilot/abfe_mmp1_holo_zn_embelin/abfe_production/complex_leg/PHASE5A_OK"
PHASE5B_GATE = ROOT / "pilot/abfe_mmp1_holo_zn_embelin/abfe_production/solvent_leg/PHASE5B_OK"
PHASE5_OK = ROOT / "pilot/abfe_mmp1_holo_zn_embelin/abfe_production/PHASE5_OK"
PHASE5_INCONCLUSIVE = ROOT / "pilot/abfe_mmp1_holo_zn_embelin/abfe_production/PHASE5_INCONCLUSIVE"
PHASE5_LOG_DIR = ROOT / "pilot/abfe_mmp1_holo_zn_embelin/abfe_production"

CONDA_PY = "/home/crazat/miniforge3/envs/genesis-md/bin/python"


def log(msg: str) -> None:
    line = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
    print(line, flush=True)
    with LOG.open("a") as fh:
        fh.write(line + "\n")


def md60_complete() -> bool:
    if not MD60_SUMMARY.exists():
        return False
    try:
        rows = json.loads(MD60_SUMMARY.read_text())
    except Exception:
        return False
    if not isinstance(rows, list) or len(rows) < 4:
        return False
    ok_count = sum(
        1 for r in rows
        if r.get("status") == "ok"
        and float(r.get("ns_simulated", 0.0)) >= 59.0  # tolerate sub-frame round-down
    )
    return ok_count == 4


def run_phase(name: str, script: Path, extra_args: list[str] | None = None) -> int:
    cmd = [CONDA_PY, str(script)] + (extra_args or [])
    log(f"==> launching {name}: {' '.join(cmd)}")
    t0 = time.time()
    proc = subprocess.run(
        cmd,
        cwd=str(ROOT),
        env={**os.environ, "PYTHONUNBUFFERED": "1"},
    )
    rc = proc.returncode
    log(f"<== {name} rc={rc} duration_min={(time.time()-t0)/60:.1f}")
    return rc


def run_phase5_parallel() -> int:
    """Launch complex + solvent legs as concurrent subprocesses, wait both, then combine."""
    PHASE5_LOG_DIR.mkdir(parents=True, exist_ok=True)
    log("==> Phase5 launching complex + solvent legs in parallel")
    t0 = time.time()

    procs: dict[str, subprocess.Popen] = {}
    for leg in ("complex", "solvent"):
        if leg == "complex" and PHASE5A_GATE.exists():
            log(f"  {leg} leg already done — skipping launch")
            continue
        if leg == "solvent" and PHASE5B_GATE.exists():
            log(f"  {leg} leg already done — skipping launch")
            continue
        log_path = PHASE5_LOG_DIR / f"phase5_{leg}.log"
        log(f"  launching {leg} leg, stdout -> {log_path}")
        fh = log_path.open("w")
        p = subprocess.Popen(
            [CONDA_PY, str(PHASE5_SCRIPT), "--leg", leg],
            cwd=str(ROOT),
            stdout=fh, stderr=subprocess.STDOUT,
            env={**os.environ, "PYTHONUNBUFFERED": "1"},
        )
        procs[leg] = p

    rcs: dict[str, int] = {}
    for leg, p in procs.items():
        rc = p.wait()
        rcs[leg] = rc
        log(f"  {leg} leg rc={rc}")

    log(f"<== Phase5 parallel legs duration_min={(time.time()-t0)/60:.1f}")
    if any(rc != 0 for rc in rcs.values()) or not (PHASE5A_GATE.exists() and PHASE5B_GATE.exists()):
        log(f"Phase5 parallel legs FAILED gates A={PHASE5A_GATE.exists()} B={PHASE5B_GATE.exists()} rcs={rcs}")
        return 1

    # Combine
    return run_phase("Phase5 combine", PHASE5_SCRIPT, ["--leg", "combine"])


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--poll-seconds", type=int, default=600,
                   help="poll cadence for 60ns completion (default 600 = 10 min)")
    p.add_argument("--skip-60ns-wait", action="store_true",
                   help="skip the 60ns gate; advance to Phase 3 immediately")
    args = p.parse_args()

    log("=== ZAFF orchestrator started ===")
    log(f"  cwd: {ROOT}")
    log(f"  poll cadence: {args.poll_seconds} s")
    log(f"  skip 60ns wait: {args.skip_60ns_wait}")

    # Step A: wait for 60ns MD to complete
    if not args.skip_60ns_wait:
        log("waiting for 60ns MD to complete...")
        while not md60_complete():
            time.sleep(args.poll_seconds)
        log("60ns MD complete — all 4 systems status=ok")

    # Step B: Phase 3 sanity MD
    if PHASE3_GATE.exists():
        log("Phase 3 already complete (PHASE3_PASS exists) — skipping")
    else:
        rc = run_phase("Phase3 sanity MD", PHASE3_SCRIPT)
        if rc != 0 or not PHASE3_GATE.exists():
            log("Phase 3 FAILED — orchestrator exiting")
            return 3

    # Step C: Phase 4 complex builder
    if PHASE4_GATE.exists():
        log("Phase 4 already complete (PHASE4_OK exists) — skipping")
    else:
        rc = run_phase("Phase4 complex builder", PHASE4_SCRIPT)
        if rc != 0 or not PHASE4_GATE.exists():
            log("Phase 4 FAILED — orchestrator exiting")
            return 4

    # Step D: Phase 5 ABFE production
    if PHASE5_OK.exists():
        log("Phase 5 already complete (PHASE5_OK exists) — orchestrator done")
        return 0
    if PHASE5_INCONCLUSIVE.exists():
        log("Phase 5 ran but dG_bind+err >= 0 (inconclusive); see dG_bind.json")
        return 1

    rc = run_phase5_parallel()
    if rc == 0 and PHASE5_OK.exists():
        log("Phase 5 PASS — ABFE production complete with dG_bind+err < 0")
    elif PHASE5_INCONCLUSIVE.exists():
        log("Phase 5 INCONCLUSIVE — see dG_bind.json")
    else:
        log("Phase 5 FAILED — see logs")
    return rc


if __name__ == "__main__":
    sys.exit(main())
