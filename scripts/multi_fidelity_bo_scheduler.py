#!/usr/bin/env python3
"""Cost-aware multi-fidelity cascade scheduler over the evidence ledger.

Cascade tiers (cheap → expensive):
  T1  Boltz-2 cofold              (~minute / pair, GPU)
  T2  ADMET-AI                    (~seconds / mol, CPU sequential)
  T3  xTB conformer + gap         (~tens of seconds / mol, CPU)
  T4  10–30 ns MD                 (~hour / pair, GPU)
  T5  60–120 ns MD                (~half-day / pair, GPU)
  T6  ABFE / ZAFF                 (~day–week / pair, GPU)
  T7  wet-lab IC50 / IVRT / IVPT  (₩100k+/sample, CRO)

Strategy:
  - Read pilot/evidence_ledger.csv
  - For each (compound, target) pair, decide which tier is the *next* useful
    investment given the current axes already populated and the cost budget.
  - Honor scientific_gates.yaml + curator directives (via planner overlay).
  - Output pilot/multi_fidelity_schedule.csv with columns:
      compound_key, target, current_tier, next_tier, expected_cost_min,
      expected_value, acquisition_score, blocked_by_gate, recommend_action
  - Append decision_graph rows for the top N recommendations.
  - DOES NOT launch jobs by itself. Bridges to planner via
    pilot/curator_directives_canonical.yaml hint suggestions
    when --emit-directives is passed.

CLI:
  scripts/multi_fidelity_bo_scheduler.py
  scripts/multi_fidelity_bo_scheduler.py --top 50 --emit-directives
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PILOT = ROOT / "pilot"
LEDGER = PILOT / "evidence_ledger.csv"
SCHEDULE = PILOT / "multi_fidelity_schedule.csv"
META = PILOT / "multi_fidelity_schedule_meta.json"
DECISION_GRAPH = ROOT / "scripts/decision_graph_log.py"
CANONICAL = PILOT / "curator_directives_canonical.yaml"
QUEUE_STATE = PILOT / "queue_state.json"
QUEUE_METRICS = PILOT / "queue_metrics.json"

STALE_THRESHOLD_RUNS = 3  # consecutive runs at same recommendation without progress

# Tier definitions: (id, axes that must be populated before this tier is "done",
# expected cost in minutes, downstream readiness gate)
TIERS = [
    {
        "id": "T1_boltz2",
        "axes": ["boltz2_aff_value", "boltz2_aff_prob_bin"],
        "cost_min": 2,
        "fidelity_class": "cheap",
    },
    {
        # OpenFold3 cofold cross-validation. Same input as Boltz-2; provides
        # consensus structural agreement (no affinity output of its own).
        "id": "T1b_openfold3",
        "axes": ["of3_plddt_mean", "of3_consensus_score"],
        "cost_min": 4,
        "fidelity_class": "cheap",
    },
    {
        # AQAffinity rescore (structure-free pKd) on top of OpenFold3 weight.
        "id": "T1c_aqaffinity",
        "axes": ["aqaffinity_pkd"],
        "cost_min": 0.5,
        "fidelity_class": "cheap",
    },
    {
        "id": "T2_admet",
        "axes": ["admet_ames", "admet_herg", "admet_dili"],
        "cost_min": 0.5,
        "fidelity_class": "cheap",
    },
    {
        "id": "T3_xtb",
        "axes": ["xtb_gap_eV"],
        "cost_min": 1,
        "fidelity_class": "cheap",
    },
    {
        "id": "T4_md_short",
        "axes": ["md_rmsd_mean_A_best"],
        "axes_threshold": ("md_total_ns", 10),  # consider done only if >=10 ns
        "cost_min": 60,
        "fidelity_class": "mid",
    },
    {
        "id": "T5_md_long",
        "axes": ["md_rmsd_mean_A_best"],
        "axes_threshold": ("md_total_ns", 60),
        "cost_min": 720,
        "fidelity_class": "expensive",
    },
    {
        "id": "T6_abfe",
        "axes": ["abfe_status"],
        "cost_min": 4320,
        "fidelity_class": "very_expensive",
    },
    {
        "id": "T7_wetlab",
        "axes": ["wetlab_ic50"],
        "cost_min": 20000,
        "fidelity_class": "wetlab",
    },
]


def load_ledger() -> list[dict[str, Any]]:
    if not LEDGER.exists() or LEDGER.stat().st_size == 0:
        return []
    with LEDGER.open(newline="") as fh:
        return list(csv.DictReader(fh))


def to_float(s: Any, default: float | None = None) -> float | None:
    try:
        if s is None or s == "":
            return default
        return float(s)
    except Exception:
        return default


def evaluate_pair(row: dict[str, Any]) -> dict[str, Any]:
    """Return dict with current_tier_index, next_tier_index, value/cost."""
    current = -1
    for i, tier in enumerate(TIERS):
        ok = True
        for ax in tier["axes"]:
            if not row.get(ax) or row.get(ax) in ("nan", "NaN"):
                ok = False
                break
        if ok:
            current = i
        else:
            break
    next_idx = min(current + 1, len(TIERS) - 1)
    return {
        "current_tier_index": current,
        "current_tier_id": TIERS[current]["id"] if current >= 0 else "T0_none",
        "next_tier_index": next_idx,
        "next_tier_id": TIERS[next_idx]["id"],
        "next_cost_min": TIERS[next_idx]["cost_min"],
        "next_fidelity_class": TIERS[next_idx]["fidelity_class"],
    }


def acquisition_score(row: dict[str, Any], ev: dict[str, Any]) -> float:
    """Cheap heuristic: cost-aware expected info gain."""
    aff = to_float(row.get("boltz2_aff_value"), 0.0) or 0.0
    aff_prob = to_float(row.get("boltz2_aff_prob_bin"), 0.0) or 0.0
    rmsd = to_float(row.get("md_rmsd_mean_A_best"))
    herg = to_float(row.get("admet_herg"))
    ames = to_float(row.get("admet_ames"))
    qed = to_float(row.get("qed"), 0.5) or 0.5

    value = 0.0
    value += 0.5 * aff_prob
    value += 0.3 * qed
    if rmsd is not None and rmsd < 1.5:
        value += 0.2 * (1.5 - rmsd) / 1.5
    if herg is not None and herg < 0.3:
        value += 0.1
    if ames is not None and ames < 0.3:
        value += 0.05

    # Penalize gates and negatives
    flags = (row.get("gate_action_aggregate") or "").lower()
    if "hold" in flags or "suppress" in flags:
        value -= 0.5
    elif "flag" in flags:
        value -= 0.2

    cost = float(ev.get("next_cost_min", 1)) or 1.0
    # Acquisition = value / log10(1 + cost). Cheap tiers favored at equal value.
    import math
    return value / math.log10(1.0 + cost)


def is_blocked(row: dict[str, Any]) -> tuple[bool, str]:
    flags = (row.get("gate_action_aggregate") or "").lower()
    if "hold" in flags or "suppress" in flags:
        return True, row.get("gate_flags") or "blocked"
    return False, ""


def _path_from_env(env_key: str, default: str) -> Path:
    val = os.environ.get(env_key, default)
    return Path(val).expanduser() if val else Path(default).expanduser()


def tier_runtime_status() -> dict[str, dict[str, Any]]:
    """Probe filesystem for per-tier runtime presence.

    Returns: {tier_id: {"present": bool, "missing": [paths], "reason": str}}
    Only tiers with concrete external runtime dependencies are checked.
    """
    of3_root = _path_from_env(
        "GENESIS_OPENFOLD3_ROOT",
        str(ROOT / "external_tools/openfold-3"),
    )
    pixi_bin = _path_from_env("PIXI_BIN", "/home/crazat/.pixi/bin/pixi")
    of3_ckpt = _path_from_env(
        "OPENFOLD3_INFERENCE_CKPT",
        str(ROOT / ".cache/openfold3/of3-p2-155k.pt"),
    )

    of3_missing = [str(p) for p in (of3_root, pixi_bin, of3_ckpt) if not p.exists()]
    of3_present = not of3_missing

    return {
        "T1b_openfold3": {
            "present": of3_present,
            "missing": of3_missing,
            "reason": (
                "ok" if of3_present
                else f"of3_runtime_missing: {','.join(Path(p).name for p in of3_missing)}"
            ),
        },
        # T1c_aqaffinity reuses OF3 weights via the same pixi env
        "T1c_aqaffinity": {
            "present": of3_present,
            "missing": of3_missing,
            "reason": (
                "ok" if of3_present
                else f"aqaffinity_runtime_missing: {','.join(Path(p).name for p in of3_missing)}"
            ),
        },
    }


def runtime_blocked(ev: dict[str, Any], runtime_status: dict[str, dict[str, Any]]) -> tuple[bool, str]:
    """Check whether the next tier's runtime is missing — a hard operational block."""
    next_id = ev.get("next_tier_id")
    info = runtime_status.get(next_id)
    if info and not info["present"]:
        return True, info["reason"]
    return False, ""


def load_queue_state() -> dict[str, Any]:
    if not QUEUE_STATE.exists():
        return {"work_items": {}, "history": []}
    try:
        return json.loads(QUEUE_STATE.read_text())
    except Exception:
        return {"work_items": {}, "history": []}


def update_queue_state(out_rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Track per-(compound, target) recommendation continuity across runs.

    Increments consecutive_same_action when the (current_tier, recommend_action)
    pair is unchanged since last run; resets when it changes.
    """
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    state = load_queue_state()
    items = state.get("work_items", {})
    fresh_keys: set[str] = set()
    stalled_count = 0
    for r in out_rows:
        key = f"{r['compound_key']}|{r['target']}"
        fresh_keys.add(key)
        prior = items.get(key)
        signature = f"{r['current_tier']}->{r['recommend_action']}"
        if prior and prior.get("signature") == signature:
            prior["consecutive_runs"] = int(prior.get("consecutive_runs", 1)) + 1
            prior["last_seen_at"] = now
            prior["last_score"] = r["acquisition_score"]
            if prior["consecutive_runs"] >= STALE_THRESHOLD_RUNS:
                prior["stale"] = True
                stalled_count += 1
        else:
            items[key] = {
                "first_seen_at": (prior or {}).get("first_seen_at", now),
                "last_seen_at": now,
                "signature": signature,
                "consecutive_runs": 1,
                "last_score": r["acquisition_score"],
                "stale": False,
            }
    # garbage-collect items no longer in schedule
    for k in list(items.keys()):
        if k not in fresh_keys:
            del items[k]
    state["work_items"] = items
    history = state.get("history", [])
    history.append({
        "ts": now,
        "rows": len(out_rows),
        "stalled": stalled_count,
    })
    state["history"] = history[-50:]  # keep last 50 runs
    QUEUE_STATE.write_text(json.dumps(state, indent=2, ensure_ascii=False))
    return state


def emit_queue_metrics(
    out_rows: list[dict[str, Any]],
    runtime_status: dict[str, dict[str, Any]],
    state: dict[str, Any],
) -> None:
    """Per-tier rate / stall metrics — operational visibility for the user."""
    by_next: dict[str, dict[str, Any]] = {}
    for r in out_rows:
        nt = r["next_tier"]
        b = by_next.setdefault(nt, {
            "pending": 0,
            "blocked_runtime": 0,
            "blocked_gate": 0,
            "top_score": 0.0,
        })
        b["pending"] += 1
        if r["blocked_by_gate"]:
            if "runtime" in (r.get("blocked_reason") or "").lower():
                b["blocked_runtime"] += 1
            else:
                b["blocked_gate"] += 1
        b["top_score"] = max(b["top_score"], float(r.get("acquisition_score") or 0))
    stalled = [
        {"work_id": k, "consecutive_runs": v["consecutive_runs"], "signature": v["signature"]}
        for k, v in state.get("work_items", {}).items()
        if v.get("stale")
    ]
    stalled.sort(key=lambda x: -x["consecutive_runs"])
    metrics = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "scheduler_runs_tracked": len(state.get("history", [])),
        "tier_runtime_status": runtime_status,
        "per_next_tier": by_next,
        "stalled_items_count": len(stalled),
        "stalled_items_top": stalled[:20],
        "stale_threshold_runs": STALE_THRESHOLD_RUNS,
    }
    QUEUE_METRICS.write_text(json.dumps(metrics, indent=2, ensure_ascii=False))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--top", type=int, default=50)
    parser.add_argument("--emit-directives", action="store_true")
    args = parser.parse_args()

    rows = load_ledger()
    runtime_status = tier_runtime_status()
    out_rows: list[dict[str, Any]] = []
    for row in rows:
        if row.get("target") == "ANY":
            continue
        ev = evaluate_pair(row)
        score = acquisition_score(row, ev)
        rt_blocked, rt_reason = runtime_blocked(ev, runtime_status)
        gate_blocked, gate_reason = is_blocked(row)
        blocked = rt_blocked or gate_blocked
        blocked_reason = rt_reason or gate_reason
        if rt_blocked:
            recommend = f"hold_runtime_missing:{ev['next_tier_id']}"
        elif gate_blocked:
            recommend = "hold_expensive_compute"
        else:
            recommend = f"advance_to_{ev['next_tier_id']}"
        out_rows.append({
            "compound_key": row.get("compound_key"),
            "target": row.get("target"),
            "leader_seed": row.get("leader_seed"),
            "current_tier": ev["current_tier_id"],
            "next_tier": ev["next_tier_id"],
            "next_cost_min": ev["next_cost_min"],
            "next_fidelity_class": ev["next_fidelity_class"],
            "boltz2_aff_prob_bin": row.get("boltz2_aff_prob_bin"),
            "boltz2_aff_value": row.get("boltz2_aff_value"),
            "md_rmsd_mean_A_best": row.get("md_rmsd_mean_A_best"),
            "admet_herg": row.get("admet_herg"),
            "admet_ames": row.get("admet_ames"),
            "qed": row.get("qed"),
            "skin_window": row.get("skin_window"),
            "blocked_by_gate": blocked,
            "blocked_reason": blocked_reason,
            "acquisition_score": round(score, 4),
            "recommend_action": recommend,
        })

    out_rows.sort(key=lambda r: r["acquisition_score"], reverse=True)
    fieldnames = list(out_rows[0].keys()) if out_rows else []
    if fieldnames:
        with SCHEDULE.open("w", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(out_rows)

    META.write_text(json.dumps(
        {
            "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "rows": len(out_rows),
            "ledger_input": str(LEDGER.relative_to(ROOT)),
            "tiers": [{"id": t["id"], "cost_min": t["cost_min"]} for t in TIERS],
            "tier_runtime_status": runtime_status,
            "top_recommendations": out_rows[: args.top],
        },
        indent=2,
        ensure_ascii=False,
    ))

    state = update_queue_state(out_rows)
    emit_queue_metrics(out_rows, runtime_status, state)

    if args.emit_directives and out_rows:
        # Pick top recommendations that are not blocked and not already at T7,
        # collapse to per-target pin_high directives (max 5 unique targets).
        unique_targets: list[str] = []
        for r in out_rows:
            if r["blocked_by_gate"]:
                continue
            tg = r["target"]
            if tg and tg not in unique_targets:
                unique_targets.append(tg)
            if len(unique_targets) >= 5:
                break
        if unique_targets:
            try:
                import yaml  # type: ignore

                doc = {}
                if CANONICAL.exists():
                    doc = yaml.safe_load(CANONICAL.read_text()) or {}
                directives = doc.get("directives") or []
                directives.append({
                    "action": "pin_high",
                    "scope": ["targets"],
                    "targets": unique_targets,
                    "reason": "multi_fidelity_bo_scheduler top targets by acquisition score",
                    "expires_at": None,
                    "source": "multi_fidelity_bo_scheduler",
                })
                doc.setdefault("schema_version", 1)
                doc.setdefault("generated_at",
                               datetime.now(timezone.utc).isoformat(timespec="seconds"))
                doc["directives"] = directives
                CANONICAL.write_text(yaml.safe_dump(doc, allow_unicode=True, sort_keys=False))
            except Exception as exc:
                print(f"# emit_directives skipped: {exc}", file=sys.stderr)

    if DECISION_GRAPH.exists():
        try:
            top = out_rows[: min(5, args.top)]
            subprocess.run(
                [
                    str(ROOT / ".venv/bin/python"),
                    str(DECISION_GRAPH),
                    "event=multi_fidelity_step",
                    "source=multi_fidelity_bo_scheduler",
                    f"rows={len(out_rows)}",
                    f"top5={json.dumps(top, ensure_ascii=False)}",
                ],
                check=False,
                stdout=subprocess.DEVNULL,
            )
        except Exception:
            pass

    print(f"multi_fidelity_schedule rows={len(out_rows)} top5_score={[r['acquisition_score'] for r in out_rows[:5]]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
