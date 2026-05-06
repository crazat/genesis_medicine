"""Cost-aware multi-fidelity planner for compute and wet-lab follow-up."""
from __future__ import annotations

import csv
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_meaningful"
DOC = ROOT / "docs/MULTI_FIDELITY_BO_PLANNER.md"
CSV_OUT = OUT / "multi_fidelity_bo_plan.csv"

FIDELITIES = {
    "descriptor_surrogate": {"cost": 1, "purpose": "triage very large candidate pools"},
    "Boltz-2 cofold": {"cost": 8, "purpose": "target-specific structure/affinity"},
    "PoseBusters gate": {"cost": 2, "purpose": "raw pose physical sanity"},
    "30 ns MD": {"cost": 30, "purpose": "short stability validation"},
    "60-100 ns MD": {"cost": 90, "purpose": "paper-strength robustness"},
    "single-point wet-lab": {"cost": 250, "purpose": "phenotype or biochemical confirmation"},
    "dose-response/IVPT": {"cost": 900, "purpose": "lead-quality quantitative validation"},
}


def json_rows(path: Path) -> list[dict[str, object]]:
    if not path.exists():
        return []
    try:
        rows = json.loads(path.read_text())
    except Exception:
        return []
    return rows if isinstance(rows, list) else []


def md_status() -> dict[tuple[str, str], dict[str, object]]:
    out: dict[tuple[str, str], dict[str, object]] = {}
    for path in [
        ROOT / "pilot/md_r15_chromanol_top3_30ns/summary.json",
        ROOT / "pilot/md_r16_chromanol_topical_priority_30ns/summary.json",
        ROOT / "pilot/md_r16_chromanol_topical_tgfb1_top6_60ns/summary.json",
        ROOT / "pilot/md_r16_chromanol_topical_pigment_representative_60ns/summary.json",
        ROOT / "pilot/md_r16_chromanol_anchor_triad_100ns/summary.json",
    ]:
        for row in json_rows(path):
            target = str(row.get("target", "")).lower()
            compound = str(row.get("analog_id") or row.get("compound") or row.get("name") or "")
            if not target or not compound:
                continue
            out[(compound, target)] = row
            if "__r15_chromanol" in str(row.get("name", "")).lower():
                out[("R15_chromanol", target)] = row
    return out


def clean_text(value: object) -> str:
    if value is None:
        return ""
    try:
        if pd.isna(value):
            return ""
    except TypeError:
        pass
    text = str(value)
    return "" if text.lower() in {"nan", "none", "null"} else text


def boolish(value: object) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes"}


def build_plan() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    md = md_status()
    active = OUT / "active_learning_next_candidates.csv"
    if active.exists() and active.stat().st_size > 0:
        df = pd.read_csv(active).head(80)
        for _, row in df.iterrows():
            candidate = clean_text(row.get("candidate_id", ""))
            target = clean_text(row.get("target", "")).lower()
            if not candidate or not target:
                continue
            acq = float(row.get("acquisition_score", 0) or 0)
            if boolish(row.get("already_labeled_pair", False)):
                next_fid = "30 ns MD"
                cost = FIDELITIES[next_fid]["cost"]
            else:
                next_fid = "Boltz-2 cofold"
                cost = FIDELITIES[next_fid]["cost"]
            rows.append(
                {
                    "candidate_id": candidate,
                    "target": target,
                    "source": row.get("source", ""),
                    "current_best_fidelity": "descriptor_surrogate",
                    "recommended_next_fidelity": next_fid,
                    "estimated_cost_units": cost,
                    "expected_value": round(acq, 4),
                    "value_per_cost": round(acq / max(cost, 1), 5),
                    "reason": "active-learning acquisition from local surrogate",
                }
            )

    for path, source in [
        (OUT / "r16_chromanol_topical_cofold.csv", "r16_cofold"),
        (OUT / "r15_chromanol_cofold_14targets.csv", "r15_cofold"),
    ]:
        if not path.exists():
            continue
        df = pd.read_csv(path)
        for _, row in df.iterrows():
            candidate = clean_text(row.get("analog_id", "")) or clean_text(row.get("compound", ""))
            target = clean_text(row.get("target", "")).lower()
            if not candidate or not target:
                continue
            aff = float(row.get("affinity_probability_binary", 0) or 0)
            m = md.get((candidate, target))
            if m and m.get("status") == "ok":
                max_r = float(m.get("rmsd_max_A", 99))
                last = float(m.get("rmsd_last_third_A", 99))
                if max_r <= 1.5 and last <= 1.0:
                    next_fid = "single-point wet-lab"
                    reason = "stable MD pair; buy phenotype/biochemical evidence"
                else:
                    next_fid = "60-100 ns MD"
                    reason = "MD exists but stability margin is not paper-strong"
            else:
                next_fid = "30 ns MD" if aff >= 0.50 else "PoseBusters gate"
                reason = "cofold affinity present; needs physical/MD validation"
            cost = FIDELITIES[next_fid]["cost"]
            value = aff + (0.08 if source == "r16_cofold" else 0.0)
            rows.append(
                {
                    "candidate_id": candidate,
                    "target": target,
                    "source": source,
                    "current_best_fidelity": "Boltz-2 cofold",
                    "recommended_next_fidelity": next_fid,
                    "estimated_cost_units": cost,
                    "expected_value": round(value, 4),
                    "value_per_cost": round(value / max(cost, 1), 5),
                    "reason": reason,
                }
            )
    rows.sort(key=lambda r: (str(r["recommended_next_fidelity"]) != "single-point wet-lab", -float(r["value_per_cost"])))
    return rows


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    now = datetime.now(ZoneInfo("Asia/Seoul")).isoformat(timespec="seconds")
    rows = build_plan()
    if rows:
        with CSV_OUT.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
    else:
        CSV_OUT.write_text("", encoding="utf-8")
    lines = [
        "# Multi-fidelity BO Planner",
        "",
        f"- timestamp: `{now}`",
        f"- plan_rows: `{len(rows)}`",
        "- purpose: 다음 action을 무작정 GPU/CPU로 고르지 않고 cost 대비 정보가 큰 fidelity로 선택한다.",
        "",
        "## Fidelity Ladder",
        "",
        "| fidelity | cost units | purpose |",
        "|---|---:|---|",
    ]
    for name, meta in FIDELITIES.items():
        lines.append(f"| {name} | {meta['cost']} | {meta['purpose']} |")
    lines.extend(["", "## Top Actions", "", "| rank | candidate | target | next fidelity | value/cost | reason |", "|---:|---|---|---|---:|---|"])
    for i, row in enumerate(rows[:30], 1):
        lines.append(
            f"| {i} | {row['candidate_id']} | {row['target']} | {row['recommended_next_fidelity']} | {row['value_per_cost']} | {row['reason']} |"
        )
    lines.extend(
        [
            "",
            "## Curator Use",
            "",
            "- CPU/GPU가 비면 `value_per_cost`가 높은 compute action부터 큐잉한다.",
            "- wet-lab action은 계산 큐가 아니라 CRO/RFQ 후보로 보낸다.",
            "- high-fidelity 결과가 생기면 이 파일을 다시 생성해 lower-fidelity surrogate를 보정한다.",
            "",
        ]
    )
    DOC.write_text("\n".join(lines), encoding="utf-8")
    print(f"Saved {CSV_OUT.relative_to(ROOT)}")
    print(f"Saved {DOC.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
