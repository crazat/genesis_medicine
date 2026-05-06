"""Pocket, druggability, and modality gate for skin targets."""
from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd
import yaml


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_meaningful"
DOC = ROOT / "docs/POCKET_EVIDENCE_GATE.md"
CSV_OUT = OUT / "pocket_evidence_gate.csv"

HARD_TARGET_TOKENS = ["mitf", "jun", "ctnnb1", "col1a1", "srebf1", "wnt10b"]
BIOLOGIC_TOKENS = ["tgfb", "ctgf", "vegf", "fgf"]
ENZYME_RECEPTOR_TOKENS = ["mmp", "tyr", "dct", "srd5", "ar", "mc1r", "rarg", "ptgs", "lox", "piezo", "mylk", "tlr", "nlrp", "nr3c1", "f2rl1"]


def read_yaml_targets() -> dict[str, dict[str, object]]:
    out: dict[str, dict[str, object]] = {}
    for path in sorted((ROOT / "conf/skin_targets").glob("*.yaml")):
        data = yaml.safe_load(path.read_text()) or {}
        for target in data.get("targets", []) or []:
            key = str(target.get("key", "")).upper()
            if not key:
                continue
            rec = out.setdefault(key, {"diseases": set(), "pocket_hints": [], "modes": set(), "display": target.get("display", key)})
            rec["diseases"].add(data.get("category", path.stem))
            if target.get("pocket_hint"):
                rec["pocket_hints"].append(str(target["pocket_hint"]))
            if target.get("mode"):
                rec["modes"].add(str(target["mode"]))
    return out


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    now = datetime.now(ZoneInfo("Asia/Seoul")).isoformat(timespec="seconds")
    target_info = read_yaml_targets()
    gate_path = OUT / "target_evidence_gate.csv"
    target_gate = pd.read_csv(gate_path) if gate_path.exists() else pd.DataFrame()
    rows = []
    for key, info in sorted(target_info.items()):
        lower = key.lower()
        gate = ""
        if not target_gate.empty and "target" in target_gate.columns:
            sub = target_gate[target_gate["target"].astype(str).str.upper().eq(key)]
            gate = str(sub.iloc[0]["gate"]) if not sub.empty else ""
        hints = list(info["pocket_hints"])
        modes = sorted(info["modes"])
        if any(token in lower for token in HARD_TARGET_TOKENS):
            pocket_class = "hard_or_indirect"
            compute_action = "phenotype/cell evidence before docking expansion"
            risk = "small-molecule pocket claim weak"
        elif any(token in lower for token in BIOLOGIC_TOKENS):
            pocket_class = "interface_or_biologic"
            compute_action = "cofold only with interface caveat; consider biologic/peptide or assay endpoint"
            risk = "secreted/interface target, small pocket may be noncanonical"
        elif hints or any(token in lower for token in ENZYME_RECEPTOR_TOKENS):
            pocket_class = "direct_pocket_plausible"
            compute_action = "cofold/docking/MD allowed if target gate is green"
            risk = "standard pose and MD validation still required"
        else:
            pocket_class = "unknown"
            compute_action = "run druggability or pocket prediction before heavy compute"
            risk = "binding site not established"
        priority = "high" if gate == "green" and pocket_class == "direct_pocket_plausible" else "review"
        if gate == "red":
            priority = "low"
        rows.append(
            {
                "target": key,
                "display": info["display"],
                "diseases": ";".join(sorted(info["diseases"])),
                "target_gate": gate,
                "modes": ";".join(modes),
                "pocket_hint_present": bool(hints),
                "pocket_hints": "; ".join(hints),
                "pocket_class": pocket_class,
                "compute_priority": priority,
                "next_action": compute_action,
                "risk_note": risk,
            }
        )
    with CSV_OUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    counts = {p: sum(1 for r in rows if r["compute_priority"] == p) for p in ["high", "review", "low"]}
    lines = [
        "# Pocket Evidence Gate",
        "",
        f"- timestamp: `{now}`",
        f"- targets: `{len(rows)}`",
        f"- priority_counts: `{counts}`",
        "- purpose: 정적 cofold/docking을 target tractability와 pocket evidence에 맞춰 제한한다.",
        "",
        "## High-priority Direct-pocket Targets",
        "",
        "| target | diseases | class | next action |",
        "|---|---|---|---|",
    ]
    for row in rows:
        if row["compute_priority"] == "high":
            lines.append(f"| {row['target']} | {row['diseases']} | {row['pocket_class']} | {row['next_action']} |")
    lines.extend(["", "## Review/Low Targets", "", "| target | target gate | class | risk |", "|---|---|---|---|"])
    for row in rows:
        if row["compute_priority"] != "high":
            lines.append(f"| {row['target']} | {row['target_gate']} | {row['pocket_class']} | {row['risk_note']} |")
    lines.extend(
        [
            "",
            "## Curator Use",
            "",
            "- `high`만 신규 blind cofold/MD 확장을 우선한다.",
            "- `interface_or_biologic`은 small-molecule docking claim을 약하게 쓰고 wet-lab phenotype 또는 biologic modality로 연결한다.",
            "- `hard_or_indirect`은 virtual-cell/Cell Painting/endpoint assay 쪽으로 전환한다.",
            "",
        ]
    )
    DOC.write_text("\n".join(lines), encoding="utf-8")
    print(f"Saved {CSV_OUT.relative_to(ROOT)}")
    print(f"Saved {DOC.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
