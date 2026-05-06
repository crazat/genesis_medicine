"""Applicability-domain and uncertainty gate for local molecular surrogates."""
from __future__ import annotations

import csv
import json
import math
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd
from rdkit import Chem, RDLogger
from rdkit.Chem.Scaffolds import MurckoScaffold


RDLogger.DisableLog("rdApp.*")

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_meaningful"
DOC = ROOT / "docs/MODEL_VALIDATION_UNCERTAINTY_GATE.md"
CSV_OUT = OUT / "model_validation_uncertainty_gate.csv"
SUMMARY_OUT = OUT / "model_validation_uncertainty_summary.json"


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()


def scaffold(smiles: str) -> str:
    mol = Chem.MolFromSmiles(str(smiles))
    if mol is None:
        return "invalid"
    scaff = MurckoScaffold.GetScaffoldForMol(mol)
    if scaff is None or scaff.GetNumAtoms() == 0:
        return "acyclic"
    return Chem.MolToSmiles(scaff, canonical=True)


def training_data() -> pd.DataFrame:
    frames = []
    for path, source, id_col in [
        (OUT / "r15_chromanol_cofold_14targets.csv", "r15", "compound"),
        (OUT / "r16_chromanol_topical_cofold.csv", "r16", "analog_id"),
    ]:
        df = read_csv(path)
        if df.empty or "smiles" not in df.columns:
            continue
        frames.append(
            pd.DataFrame(
                {
                    "candidate_id": df.get(id_col, ""),
                    "target": df.get("target", ""),
                    "smiles": df["smiles"],
                    "source": source,
                    "observed_score": pd.to_numeric(df.get("affinity_probability_binary", 0), errors="coerce").fillna(0),
                }
            )
        )
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    now = datetime.now(ZoneInfo("Asia/Seoul")).isoformat(timespec="seconds")
    train = training_data()
    active = read_csv(OUT / "active_learning_next_candidates.csv")
    if train.empty or active.empty:
        CSV_OUT.write_text("", encoding="utf-8")
        SUMMARY_OUT.write_text(json.dumps({"timestamp": now, "status": "insufficient_data"}, indent=2), encoding="utf-8")
        DOC.write_text("# Model Validation and Uncertainty Gate\n\ninsufficient data\n", encoding="utf-8")
        return 0
    train["scaffold"] = train["smiles"].astype(str).map(scaffold)
    active["scaffold"] = active["smiles"].astype(str).map(scaffold)
    train_scaffolds = set(train["scaffold"])
    score_by_scaffold = train.groupby("scaffold")["observed_score"].agg(["min", "max", "count"]).to_dict("index")
    rows = []
    for _, row in active.iterrows():
        scaf = str(row.get("scaffold", "invalid"))
        pred = float(row.get("predicted_score", 0) or 0)
        unc = float(row.get("uncertainty", 0) or 0)
        seen = scaf in train_scaffolds
        stats = score_by_scaffold.get(scaf, {})
        cliff_range = float(stats.get("max", 0) or 0) - float(stats.get("min", 0) or 0)
        conformal_half_width = max(0.12, 1.64 * unc + (0.08 if not seen else 0.0) + (0.08 if cliff_range >= 0.20 else 0.0))
        if not seen:
            domain = "novel_scaffold"
        elif cliff_range >= 0.25:
            domain = "activity_cliff_risk"
        elif unc >= 0.08:
            domain = "high_model_uncertainty"
        else:
            domain = "inside_domain"
        rows.append(
            {
                "candidate_id": row.get("candidate_id", ""),
                "target": row.get("target", ""),
                "source": row.get("source", ""),
                "scaffold": scaf,
                "scaffold_seen_in_training": seen,
                "predicted_score": round(pred, 4),
                "uncertainty": round(unc, 4),
                "prediction_interval_low": round(max(0.0, pred - conformal_half_width), 4),
                "prediction_interval_high": round(min(1.0, pred + conformal_half_width), 4),
                "training_scaffold_score_range": round(cliff_range, 4),
                "applicability_domain": domain,
                "next_action": "require direct Boltz/pose validation before claim" if domain != "inside_domain" else "surrogate-supported triage only",
            }
        )
    rows.sort(key=lambda r: (str(r["applicability_domain"]) != "inside_domain", -float(r["predicted_score"])))
    with CSV_OUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    counts = {d: sum(1 for r in rows if r["applicability_domain"] == d) for d in ["inside_domain", "novel_scaffold", "activity_cliff_risk", "high_model_uncertainty"]}
    summary = {
        "timestamp": now,
        "training_rows": len(train),
        "active_rows": len(active),
        "training_scaffold_count": len(train_scaffolds),
        "domain_counts": counts,
        "csv": str(CSV_OUT.relative_to(ROOT)),
    }
    SUMMARY_OUT.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    lines = [
        "# Model Validation and Uncertainty Gate",
        "",
        f"- timestamp: `{now}`",
        f"- training_rows: `{len(train)}`",
        f"- active_rows: `{len(active)}`",
        f"- training_scaffold_count: `{len(train_scaffolds)}`",
        f"- domain_counts: `{counts}`",
        "- purpose: active-learning surrogate 추천을 scaffold/applicability-domain/conformal-style interval로 제한한다.",
        "",
        "## Top Rows",
        "",
        "| candidate | target | domain | predicted | interval | scaffold | next |",
        "|---|---|---|---:|---|---|---|",
    ]
    for row in rows[:30]:
        interval = f"{row['prediction_interval_low']}-{row['prediction_interval_high']}"
        lines.append(
            f"| {row['candidate_id']} | {row['target']} | {row['applicability_domain']} | {row['predicted_score']} | {interval} | {row['scaffold']} | {row['next_action']} |"
        )
    lines.extend(
        [
            "",
            "## Curator Rule",
            "",
            "- `inside_domain`도 manuscript claim이 아니라 triage 근거로만 쓴다.",
            "- `novel_scaffold`와 `activity_cliff_risk`는 direct cofold/pose/MD 없이 paper table에 올리지 않는다.",
            "- 외부 benchmark는 MoleculeNet/TDC/FS-Mol/scaffold split을 다음 방법론 보강 후보로 둔다.",
            "",
        ]
    )
    DOC.write_text("\n".join(lines), encoding="utf-8")
    print(f"Saved {CSV_OUT.relative_to(ROOT)}")
    print(f"Saved {DOC.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
