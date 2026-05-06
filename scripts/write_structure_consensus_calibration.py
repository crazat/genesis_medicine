"""Structure/affinity confidence calibration across Boltz, pose gate and MD."""
from __future__ import annotations

import csv
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_meaningful"
DOC = ROOT / "docs/STRUCTURE_CONSENSUS_CALIBRATION.md"
CSV_OUT = OUT / "structure_consensus_calibration.csv"


def json_rows(path: Path) -> list[dict[str, object]]:
    if not path.exists():
        return []
    try:
        rows = json.loads(path.read_text())
    except Exception:
        return []
    return rows if isinstance(rows, list) else []


def md_index() -> dict[str, dict[str, object]]:
    idx: dict[str, dict[str, object]] = {}
    for path in [
        ROOT / "pilot/md_r15_chromanol_top3_30ns/summary.json",
        ROOT / "pilot/md_r16_chromanol_topical_priority_30ns/summary.json",
        ROOT / "pilot/md_r16_chromanol_topical_tgfb1_top6_60ns/summary.json",
        ROOT / "pilot/md_r16_chromanol_topical_pigment_representative_60ns/summary.json",
        ROOT / "pilot/md_r16_chromanol_anchor_triad_100ns/summary.json",
    ]:
        for row in json_rows(path):
            keys: set[str] = set()
            for key in ["job_id", "name"]:
                value = row.get(key)
                if value:
                    keys.add(str(value))
            target = str(row.get("target", "") or "").lower()
            analog = str(row.get("analog_id", row.get("compound", "")) or "")
            if target and analog:
                keys.add(f"{target}__{analog.lower()}")
            name = str(row.get("name", "") or "").lower()
            if target and "__r15_chromanol" in name:
                keys.add(f"r15_chrom_{target}")
            for key in keys:
                idx[key] = row
    return idx


def clean(value: object) -> str:
    if value is None:
        return ""
    try:
        if pd.isna(value):
            return ""
    except TypeError:
        pass
    return str(value)


def first_nonempty(row: pd.Series, names: list[str]) -> str:
    for name in names:
        value = clean(row.get(name, ""))
        if value:
            return value
    return ""


def infer_job_id(row: pd.Series) -> str:
    raw = clean(row.get("job_id", ""))
    if raw:
        return raw
    prediction_dir = clean(row.get("prediction_dir", ""))
    if prediction_dir:
        return Path(prediction_dir).name
    source = clean(row.get("source", ""))
    target = clean(row.get("target", "")).lower()
    if source == "r15" and target:
        return f"r15_chrom_{target}"
    return ""


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    now = datetime.now(ZoneInfo("Asia/Seoul")).isoformat(timespec="seconds")
    frames = []
    for path, source in [
        (OUT / "r15_chromanol_cofold_14targets.csv", "r15"),
        (OUT / "r16_chromanol_topical_cofold.csv", "r16"),
    ]:
        if not path.exists():
            continue
        df = pd.read_csv(path)
        df["source"] = source
        frames.append(df)
    cofold = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
    pose = pd.read_csv(OUT / "chromanol_pose_sanity_gate.csv") if (OUT / "chromanol_pose_sanity_gate.csv").exists() else pd.DataFrame()
    md = md_index()
    rows = []
    for _, row in cofold.iterrows():
        job_id = infer_job_id(row)
        target = clean(row.get("target", "")).lower()
        compound = first_nonempty(row, ["analog_id", "compound"])
        affinity = float(row.get("affinity_probability_binary", 0) or 0)
        confidence = float(row.get("confidence_score", 0) or 0)
        plddt = float(row.get("complex_plddt", 0) or 0)
        psub = pose[pose["job_id"].astype(str).eq(job_id)] if not pose.empty and "job_id" in pose.columns else pd.DataFrame()
        pose_gate = str(psub.iloc[0].get("gate_status", "missing")) if not psub.empty else "missing"
        pose_rate = float(psub.iloc[0].get("posebusters_pass_rate", 0.0)) if not psub.empty else 0.0
        m = md.get(job_id) or md.get(f"{target}__{compound.lower()}")
        md_state = "missing"
        md_score = 0.0
        if m and m.get("status") == "ok":
            max_r = float(m.get("rmsd_max_A", 99))
            last = float(m.get("rmsd_last_third_A", 99))
            if max_r <= 1.5 and last <= 1.0:
                md_state = "strong_stable"
                md_score = 1.0
            elif max_r <= 2.0 and last <= 1.5:
                md_state = "stable"
                md_score = 0.75
            else:
                md_state = "drift_review"
                md_score = 0.2
        model_score = 0.45 * affinity + 0.20 * confidence + 0.10 * min(plddt, 1.0)
        pose_score = 0.15 * pose_rate
        total = model_score + pose_score + 0.10 * md_score
        if total >= 0.68 and pose_gate == "pass" and md_state in {"stable", "strong_stable"}:
            cls = "high_confidence"
        elif total >= 0.52 and pose_gate in {"pass", "review"}:
            cls = "usable_with_caveat"
        else:
            cls = "review_before_claim"
        rows.append(
            {
                "job_id": job_id,
                "source": row.get("source", ""),
                "target": target,
                "compound": compound,
                "affinity_probability_binary": round(affinity, 4),
                "confidence_score": round(confidence, 4),
                "complex_plddt": round(plddt, 4),
                "pose_gate": pose_gate,
                "posebusters_pass_rate": round(pose_rate, 4),
                "md_state": md_state,
                "consensus_score": round(total, 4),
                "consensus_class": cls,
                "missing_consensus_models": "Chai-1;AlphaFold3;NeuralPLexer3",
                "next_action": "cross-model consensus or wet-lab before strong claim" if cls != "high_confidence" else "paper table eligible with in-silico caveat",
            }
        )
    rows.sort(key=lambda r: float(r["consensus_score"]), reverse=True)
    if rows:
        with CSV_OUT.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
    else:
        CSV_OUT.write_text("", encoding="utf-8")
    counts = {c: sum(1 for r in rows if r["consensus_class"] == c) for c in ["high_confidence", "usable_with_caveat", "review_before_claim"]}
    lines = [
        "# Structure Consensus Calibration",
        "",
        f"- timestamp: `{now}`",
        f"- rows: `{len(rows)}`",
        f"- class_counts: `{counts}`",
        "- purpose: Boltz affinity만으로 claim하지 않고 pose sanity와 MD 안정성을 합쳐 confidence를 보정한다.",
        "",
        "## Top Calibrated Pairs",
        "",
        "| job | target | compound | class | score | pose | MD |",
        "|---|---|---|---|---:|---|---|",
    ]
    for row in rows[:25]:
        lines.append(
            f"| {row['job_id']} | {row['target']} | {row['compound']} | {row['consensus_class']} | {row['consensus_score']} | {row['pose_gate']} | {row['md_state']} |"
        )
    lines.extend(
        [
            "",
            "## Curator Use",
            "",
            "- `high_confidence`는 manuscript main table에 넣을 수 있다.",
            "- `usable_with_caveat`는 raw pose/MD caveat와 함께 보조 표 또는 discussion에 둔다.",
            "- `review_before_claim`은 cross-model consensus 또는 wet-lab 전까지 강한 lead claim을 피한다.",
            "",
        ]
    )
    DOC.write_text("\n".join(lines), encoding="utf-8")
    print(f"Saved {CSV_OUT.relative_to(ROOT)}")
    print(f"Saved {DOC.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
