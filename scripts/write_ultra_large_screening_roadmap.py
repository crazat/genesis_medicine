"""Roadmap for active-learning ultra-large virtual screening."""
from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_meaningful"
DOC = ROOT / "docs/ULTRA_LARGE_SCREENING_ROADMAP.md"
CSV_OUT = OUT / "ultra_large_screening_roadmap.csv"


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    now = datetime.now(ZoneInfo("Asia/Seoul")).isoformat(timespec="seconds")
    active = read_csv(OUT / "active_learning_next_candidates.csv")
    target_gate = read_csv(OUT / "target_evidence_gate.csv")
    green_targets = []
    if not target_gate.empty and {"target", "gate"}.issubset(target_gate.columns):
        green_targets = target_gate[target_gate["gate"].eq("green")]["target"].astype(str).str.lower().head(10).tolist()
    if not green_targets:
        green_targets = ["tgfb1", "dct", "tyr", "mmp1"]
    top_active = active[~active.get("already_labeled_pair", pd.Series(dtype=bool)).astype(str).str.lower().eq("true")].head(40) if not active.empty else pd.DataFrame()
    rows = []
    stages = [
        ("stage0_local_surrogate", "local NPASS/R15/R16 candidate pool", 672, "already available", "refresh active-learning surrogate and remove duplicate labeled pairs"),
        ("stage1_orderable_subset", "ZINC/Enamine/REAL purchasable subset", 50000, "future lightweight download", "screen descriptors and apply synthesis/dermal gates before docking"),
        ("stage2_active_docking", "active-learning selected purchasable compounds", 5000, "future CPU/GPU window", "dock/cofold only top acquisition batches for green targets"),
        ("stage3_synthon_space", "synthon/V-SYNTHES style enumerated space", 1000000, "future design campaign", "enumerate analogs around chromanol/pterocarpan motifs"),
        ("stage4_wetlab_shortlist", "CRO-orderable shortlist", 30, "after cofold/MD/safety", "single-point phenotype or IVRT/IVPT confirmation"),
    ]
    for stage, library, size, status, action in stages:
        for target in green_targets[:6]:
            rows.append(
                {
                    "stage": stage,
                    "target": target,
                    "library_scope": library,
                    "nominal_library_size": size,
                    "current_status": status,
                    "queue_rule": action,
                }
            )
    for _, row in top_active.head(20).iterrows():
        rows.append(
            {
                "stage": "stage0_top_active_learning_seed",
                "target": str(row.get("target", "")),
                "library_scope": str(row.get("source", "")),
                "nominal_library_size": 1,
                "current_status": f"acquisition={row.get('acquisition_score', '')}",
                "queue_rule": f"seed future purchasable analog search around {row.get('candidate_id', '')}",
            }
        )
    with CSV_OUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    lines = [
        "# Ultra-large Screening Roadmap",
        "",
        f"- timestamp: `{now}`",
        f"- rows: `{len(rows)}`",
        "- purpose: NPASS-scale local screen을 ZINC/Enamine REAL급 ultra-large active-learning campaign으로 확장하기 위한 단계별 큐다.",
        "",
        "## Stages",
        "",
        "| stage | target | scope | nominal size | status | queue rule |",
        "|---|---|---|---:|---|---|",
    ]
    for row in rows[:40]:
        lines.append(
            f"| {row['stage']} | {row['target']} | {row['library_scope']} | {row['nominal_library_size']} | {row['current_status']} | {row['queue_rule']} |"
        )
    lines.extend(
        [
            "",
            "## Curator Rule",
            "",
            "- 현재 CPU/GPU 포화 상태에서는 stage0 문서화만 수행한다.",
            "- stage1 이상은 외부 library download/라이선스/저장공간을 확인한 뒤 별도 큐로 올린다.",
            "- ultra-large campaign은 full docking이 아니라 active-learning 압축 screen으로만 설계한다.",
            "",
        ]
    )
    DOC.write_text("\n".join(lines), encoding="utf-8")
    print(f"Saved {CSV_OUT.relative_to(ROOT)}")
    print(f"Saved {DOC.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
