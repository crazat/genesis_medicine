"""Second-pass structure consensus and claim-readiness gate.

This stays lightweight: it does not run a new structure model.  It turns the
current Boltz/PoseBusters/MD evidence into an explicit cross-model validation
plan so manuscript claims do not silently depend on one cofolding model.
"""
from __future__ import annotations

import csv
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_meaningful"
DOC = ROOT / "docs/STRUCTURE_CONSENSUS_V2.md"
CSV_OUT = OUT / "structure_consensus_v2.csv"


def clean(value: object) -> str:
    if value is None:
        return ""
    try:
        if pd.isna(value):
            return ""
    except TypeError:
        pass
    return str(value)


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()


def json_rows(path: Path) -> list[dict[str, object]]:
    if not path.exists() or path.stat().st_size == 0:
        return []
    try:
        obj = json.loads(path.read_text())
    except Exception:
        return []
    return obj if isinstance(obj, list) else []


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
            keys = {clean(row.get("job_id")), clean(row.get("name"))}
            target = clean(row.get("target")).lower()
            analog = clean(row.get("analog_id", row.get("compound"))).lower()
            if target and analog:
                keys.add(f"{target}__{analog}")
            for key in keys:
                if key:
                    idx[key] = row
    return idx


def infer_job_id(row: pd.Series) -> str:
    job_id = clean(row.get("job_id"))
    if job_id:
        return job_id
    target = clean(row.get("target")).lower()
    source = clean(row.get("source"))
    if source == "r15" and target:
        return f"r15_chrom_{target}"
    prediction_dir = clean(row.get("prediction_dir"))
    return Path(prediction_dir).name if prediction_dir else ""


def collect_cofold() -> pd.DataFrame:
    frames = []
    for path, source in [
        (OUT / "r15_chromanol_cofold_14targets.csv", "r15"),
        (OUT / "r16_chromanol_topical_cofold.csv", "r16"),
    ]:
        df = read_csv(path)
        if df.empty:
            continue
        df["source"] = source
        frames.append(df)
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def md_state(row: dict[str, object] | None) -> tuple[str, float]:
    if not row or row.get("status") != "ok":
        return "missing", 0.0
    max_r = float(row.get("rmsd_max_A", 99) or 99)
    last = float(row.get("rmsd_last_third_A", 99) or 99)
    ns = float(row.get("ns_simulated", 0) or 0)
    if ns >= 60 and max_r <= 1.5 and last <= 1.0:
        return "long_stable", 1.0
    if max_r <= 1.5 and last <= 1.0:
        return "stable", 0.85
    if max_r <= 2.0 and last <= 1.5:
        return "borderline_stable", 0.55
    return "drift_review", 0.15


def claim_class(score: float, pose_gate: str, md_label: str, affinity: float) -> tuple[str, str]:
    if score >= 0.76 and pose_gate == "pass" and md_label in {"stable", "long_stable"}:
        return "claim_ready_in_silico", "main table allowed with explicit in-silico and orthogonal-model caveat"
    if score >= 0.64 and pose_gate in {"pass", "review"} and md_label in {"stable", "long_stable", "borderline_stable"}:
        return "claim_with_caveat", "supplement/main-candidate table; request cross-model consensus before strong claim"
    if affinity >= 0.50 and pose_gate in {"pass", "review"}:
        return "needs_cross_model", "run Chai-1/DiffDock/Vina or PLIF/negative-control check before manuscript lead claim"
    return "triage_only", "keep as queue candidate or negative-control/failure-mode evidence"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    now = datetime.now(ZoneInfo("Asia/Seoul")).isoformat(timespec="seconds")

    cofold = collect_cofold()
    pose = read_csv(OUT / "chromanol_pose_sanity_gate.csv")
    pocket = read_csv(OUT / "pocket_evidence_gate.csv")
    uncertainty = read_csv(OUT / "model_validation_uncertainty_gate.csv")
    md = md_index()
    rows: list[dict[str, object]] = []

    for _, row in cofold.iterrows():
        job_id = infer_job_id(row)
        target = clean(row.get("target")).lower()
        compound = clean(row.get("analog_id")) or clean(row.get("compound"))
        affinity = float(row.get("affinity_probability_binary", 0) or 0)
        confidence = float(row.get("confidence_score", 0) or 0)
        plddt = float(row.get("complex_plddt", 0) or 0)

        psub = pose[pose["job_id"].astype(str).eq(job_id)] if not pose.empty and "job_id" in pose.columns else pd.DataFrame()
        pose_gate = clean(psub.iloc[0].get("gate_status")) if not psub.empty else "missing"
        pose_pass_rate = float(psub.iloc[0].get("posebusters_pass_rate", 0) or 0) if not psub.empty else 0.0
        failed_checks = clean(psub.iloc[0].get("failed_checks")) if not psub.empty else "missing"

        m = md.get(job_id) or md.get(f"{target}__{compound.lower()}")
        md_label, md_score = md_state(m)

        pocket_sub = pocket[pocket["target"].astype(str).str.lower().eq(target)] if not pocket.empty and "target" in pocket.columns else pd.DataFrame()
        pocket_gate = clean(pocket_sub.iloc[0].get("pocket_claim_gate")) if not pocket_sub.empty else ""
        if not pocket_gate and not pocket_sub.empty:
            pocket_gate = clean(pocket_sub.iloc[0].get("pocket_class"))
        pocket_gate = pocket_gate or "missing"
        pocket_score = 1.0 if pocket_gate in {"direct_pocket_supported", "plausible_pocket", "direct_pocket_plausible"} else 0.45 if pocket_gate != "missing" else 0.2

        usub = uncertainty[
            uncertainty["candidate_id"].astype(str).eq(compound) & uncertainty["target"].astype(str).str.lower().eq(target)
        ] if not uncertainty.empty and {"candidate_id", "target"}.issubset(uncertainty.columns) else pd.DataFrame()
        applicability = clean(usub.iloc[0].get("applicability_domain")) if not usub.empty else "missing"
        uncertainty_penalty = 0.08 if applicability in {"activity_cliff_risk", "novel_scaffold"} else 0.0

        consensus_score = (
            0.34 * affinity
            + 0.16 * confidence
            + 0.10 * min(plddt, 1.0)
            + 0.18 * pose_pass_rate
            + 0.14 * md_score
            + 0.08 * pocket_score
            - uncertainty_penalty
        )
        cls, action = claim_class(consensus_score, pose_gate, md_label, affinity)
        rows.append(
            {
                "job_id": job_id,
                "source": clean(row.get("source")),
                "target": target,
                "compound": compound,
                "smiles": clean(row.get("smiles")),
                "affinity_probability_binary": round(affinity, 4),
                "confidence_score": round(confidence, 4),
                "complex_plddt": round(plddt, 4),
                "pose_gate": pose_gate,
                "posebusters_pass_rate": round(pose_pass_rate, 4),
                "failed_pose_checks": failed_checks,
                "md_state": md_label,
                "pocket_gate": pocket_gate,
                "applicability_domain": applicability,
                "consensus_v2_score": round(consensus_score, 4),
                "claim_readiness": cls,
                "missing_orthogonal_models": "Chai-1;AlphaFold3_or_server;DiffDock_or_Vina;PLIF_similarity",
                "negative_control_required": "target_shuffle_and_decoy_ligand",
                "next_action": action,
            }
        )

    rows.sort(key=lambda r: float(r["consensus_v2_score"]), reverse=True)
    if rows:
        with CSV_OUT.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
    else:
        CSV_OUT.write_text("", encoding="utf-8")

    counts = {k: sum(1 for r in rows if r["claim_readiness"] == k) for k in ["claim_ready_in_silico", "claim_with_caveat", "needs_cross_model", "triage_only"]}
    lines = [
        "# Structure Consensus V2",
        "",
        f"- timestamp: `{now}`",
        f"- rows: `{len(rows)}`",
        f"- claim_counts: `{counts}`",
        "- purpose: single-model Boltz claim을 피하고, PoseBusters/MD/pocket/applicability-domain을 합쳐 orthogonal validation priority를 정한다.",
        "",
        "## Top Claim-Readiness Rows",
        "",
        "| job | target | compound | readiness | score | pose | MD | pocket | next |",
        "|---|---|---|---|---:|---|---|---|---|",
    ]
    for item in rows[:30]:
        lines.append(
            f"| {item['job_id']} | {item['target']} | {item['compound']} | {item['claim_readiness']} | {item['consensus_v2_score']} | {item['pose_gate']} | {item['md_state']} | {item['pocket_gate']} | {item['next_action']} |"
        )
    lines.extend(
        [
            "",
            "## Curator Rule",
            "",
            "- `claim_ready_in_silico`: 논문 main table 가능. 단, `in silico`와 orthogonal-model 미실행 caveat를 유지한다.",
            "- `claim_with_caveat`: 보조 표 또는 제한적 main candidate. cross-model 또는 wet-lab 전까지 binding-confirmed 표현 금지.",
            "- `needs_cross_model`: Chai-1/DiffDock/Vina/PLIF/negative-control 중 하나 이상을 먼저 큐잉한다.",
            "- `triage_only`: 후보 탐색 또는 failure-mode paper에만 사용한다.",
            "",
        ]
    )
    DOC.write_text("\n".join(lines), encoding="utf-8")
    print(f"Saved {CSV_OUT.relative_to(ROOT)}")
    print(f"Saved {DOC.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
