#!/usr/bin/env python3
"""Validate + canonicalize curator directives.

Reads pilot/claude_curator_directives.yaml (or codex_curator_directives.yaml,
or any --input path), validates against schema 1, and writes
pilot/curator_directives_canonical.yaml — the single source of truth that
scripts/auto_result_planner.py reads.

Behavior:
  - Drops directives with unknown actions (logs to actions_log).
  - Auto-expires directives where expires_at < now.
  - Merges with existing canonical doc so directives from earlier ticks
    survive across LLM calls until they expire or are explicitly retired.
  - Appends one decision_graph row per accepted directive.
  - Never launches compute (--no-launch is default; --launch-novel-modality
    triggers scripts/novel_modality_slot.sh once per accepted promote_modality).

CLI:
  scripts/apply_curator_directives.py
  scripts/apply_curator_directives.py --input pilot/claude_curator_directives.yaml --no-launch
  scripts/apply_curator_directives.py --launch-novel-modality
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PILOT = ROOT / "pilot"
CANONICAL = PILOT / "curator_directives_canonical.yaml"
DEFAULT_INPUTS = [
    PILOT / "claude_curator_directives.yaml",
    PILOT / "codex_curator_directives.yaml",
]
ACTIONS_LOG = PILOT / "claude_curator_actions.log"
DECISION_GRAPH = ROOT / "scripts/decision_graph_log.py"
NOVEL_MODALITY = ROOT / "scripts/novel_modality_slot.sh"

ALLOWED_ACTIONS = {
    "pin_high", "pin_low", "retire_until", "gate_with_reason",
    "promote_modality", "hold_modality",
}


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        import yaml  # type: ignore

        data = yaml.safe_load(path.read_text())
        return data if isinstance(data, dict) else {}
    except Exception as exc:
        print(f"# load_yaml failed for {path}: {exc}", file=sys.stderr)
        return {}


def dump_yaml(data: dict[str, Any], path: Path) -> None:
    try:
        import yaml  # type: ignore

        path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False))
        return
    except Exception:
        # Last-resort fallback: minimal YAML emitter for top-level + directives.
        out = []
        out.append(f"schema_version: {data.get('schema_version', 1)}")
        out.append(f"generated_at: \"{data.get('generated_at')}\"")
        out.append(f"applied_at: \"{data.get('applied_at')}\"")
        out.append("directives:")
        for d in data.get("directives", []):
            out.append("  - action: " + str(d.get("action", "")))
            for k in ("reason", "expires_at", "source", "tick_id"):
                if d.get(k) is not None:
                    out.append(f"    {k}: {json.dumps(d[k], ensure_ascii=False)}")
            for col in ("compounds", "targets", "scaffolds", "modalities", "scope"):
                if d.get(col):
                    out.append(f"    {col}: {json.dumps(d[col], ensure_ascii=False)}")
        path.write_text("\n".join(out) + "\n")


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def is_expired(d: dict[str, Any]) -> bool:
    exp = d.get("expires_at")
    if not exp:
        return False
    try:
        if exp.endswith("Z"):
            exp = exp[:-1] + "+00:00"
        return datetime.fromisoformat(exp) < datetime.now(timezone.utc)
    except Exception:
        return False


def normalize(d: dict[str, Any]) -> dict[str, Any] | None:
    action = (d.get("action") or "").strip()
    if action not in ALLOWED_ACTIONS:
        return None
    out: dict[str, Any] = {
        "action": action,
        "reason": (d.get("reason") or "").strip() or None,
        "expires_at": d.get("expires_at"),
    }
    for col in ("compounds", "targets", "scaffolds", "modalities", "scope"):
        v = d.get(col)
        if isinstance(v, list) and v:
            out[col] = [str(x) for x in v]
    return out


def append_action(line: str) -> None:
    ACTIONS_LOG.parent.mkdir(parents=True, exist_ok=True)
    with ACTIONS_LOG.open("a") as fh:
        fh.write(f"{now_iso()} {line}\n")


def emit_decision_event(payload: dict[str, Any]) -> None:
    if not DECISION_GRAPH.exists():
        return
    try:
        subprocess.run(
            [
                str(ROOT / ".venv/bin/python"),
                str(DECISION_GRAPH),
                "event=directive_apply",
                "source=apply_curator_directives",
                f"payload={json.dumps(payload, ensure_ascii=False)}",
            ],
            check=False,
            stdout=subprocess.DEVNULL,
        )
    except Exception:
        pass


def merge(existing: list[dict[str, Any]], incoming: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Keep non-expired existing + add incoming. Dedup by (action, scope-key tuple)."""
    def key(d: dict[str, Any]) -> tuple:
        return (
            d.get("action"),
            tuple(sorted(d.get("compounds", []) or [])),
            tuple(sorted(d.get("targets", []) or [])),
            tuple(sorted(d.get("scaffolds", []) or [])),
            tuple(sorted(d.get("modalities", []) or [])),
        )

    survivors: dict[tuple, dict[str, Any]] = {}
    for d in existing or []:
        if is_expired(d):
            continue
        k = key(d)
        survivors[k] = d
    for d in incoming or []:
        k = key(d)
        survivors[k] = d  # incoming overrides existing for same key
    return list(survivors.values())


def maybe_launch_novel_modality(directives: list[dict[str, Any]]) -> None:
    promotes = [d for d in directives if d.get("action") == "promote_modality"]
    if not promotes:
        return
    if not NOVEL_MODALITY.exists():
        append_action("promote_modality requested but novel_modality_slot.sh missing")
        return
    drain = PILOT / "QUEUE_DRAIN_MODE"
    if drain.exists() and os.environ.get("CLAUDE_CURATOR_DRAIN_OVERRIDE") != "1":
        append_action("promote_modality skipped: QUEUE_DRAIN_MODE present")
        return
    chosen_modality = None
    for d in promotes:
        for m in d.get("modalities") or []:
            chosen_modality = m
            break
        if chosen_modality:
            break
    chosen_modality = chosen_modality or "auto"
    append_action(f"promote_modality launching novel_modality_slot modality={chosen_modality}")
    try:
        env = dict(os.environ)
        env["GENESIS_MODALITY"] = chosen_modality
        subprocess.Popen(
            ["bash", str(NOVEL_MODALITY)],
            cwd=str(ROOT),
            env=env,
            stdout=open(PILOT / "novel_modality_slot.log", "ab"),
            stderr=subprocess.STDOUT,
            stdin=subprocess.DEVNULL,
            start_new_session=True,
        )
    except Exception as exc:
        append_action(f"promote_modality launch failed: {exc}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default=None)
    parser.add_argument(
        "--launch-novel-modality",
        action="store_true",
        help="launch scripts/novel_modality_slot.sh when promote_modality directive accepted",
    )
    parser.add_argument("--no-launch", dest="launch", action="store_false", default=True)
    args = parser.parse_args()
    args.launch = args.launch and args.launch_novel_modality

    inputs = [Path(args.input)] if args.input else DEFAULT_INPUTS
    raw_directives: list[dict[str, Any]] = []
    sources: list[str] = []
    for path in inputs:
        if not path.exists():
            continue
        doc = load_yaml(path)
        block = doc.get("directives") if isinstance(doc, dict) else None
        if not isinstance(block, list):
            continue
        for d in block:
            if not isinstance(d, dict):
                continue
            d.setdefault("source", path.name)
            d.setdefault("tick_id", doc.get("tick_id"))
            raw_directives.append(d)
        sources.append(str(path.relative_to(ROOT)))

    accepted: list[dict[str, Any]] = []
    rejected = 0
    expired = 0
    for d in raw_directives:
        if is_expired(d):
            expired += 1
            continue
        norm = normalize(d)
        if norm is None:
            rejected += 1
            continue
        norm["source"] = d.get("source")
        norm["tick_id"] = d.get("tick_id")
        accepted.append(norm)

    existing_doc = load_yaml(CANONICAL)
    existing = existing_doc.get("directives") or [] if isinstance(existing_doc, dict) else []
    merged = merge(existing, accepted)

    out = {
        "schema_version": 1,
        "generated_at": existing_doc.get("generated_at") or now_iso(),
        "applied_at": now_iso(),
        "sources": sources,
        "stats": {
            "incoming_total": len(raw_directives),
            "accepted": len(accepted),
            "rejected_unknown_action": rejected,
            "expired_at_load": expired,
            "merged_total": len(merged),
        },
        "directives": merged,
    }
    dump_yaml(out, CANONICAL)
    append_action(
        f"directives_apply incoming={len(raw_directives)} "
        f"accepted={len(accepted)} merged={len(merged)} sources={','.join(sources) or 'none'}"
    )
    emit_decision_event({
        "incoming": len(raw_directives),
        "accepted": len(accepted),
        "merged": len(merged),
        "sources": sources,
    })
    if args.launch:
        maybe_launch_novel_modality(accepted)
    print(json.dumps(out["stats"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
