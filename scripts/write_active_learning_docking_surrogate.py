"""Train a lightweight active-learning surrogate for next cofold/docking picks."""
from __future__ import annotations

import csv
import json
import math
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
from rdkit import Chem, RDLogger
from rdkit.Chem import Descriptors, Lipinski, QED, rdMolDescriptors
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import LeaveOneOut, cross_val_predict


RDLogger.DisableLog("rdApp.*")

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_meaningful"
DOC = ROOT / "docs/ACTIVE_LEARNING_DOCKING_SURROGATE.md"
CSV_OUT = OUT / "active_learning_next_candidates.csv"
SUMMARY_OUT = OUT / "active_learning_surrogate_summary.json"


def canonical(smiles: str) -> str:
    mol = Chem.MolFromSmiles(str(smiles))
    return Chem.MolToSmiles(mol, canonical=True) if mol else str(smiles)


def desc(smiles: str) -> list[float] | None:
    mol = Chem.MolFromSmiles(str(smiles))
    if mol is None:
        return None
    return [
        Descriptors.MolWt(mol),
        Descriptors.MolLogP(mol),
        rdMolDescriptors.CalcTPSA(mol),
        Lipinski.NumHDonors(mol),
        Lipinski.NumHAcceptors(mol),
        Lipinski.NumRotatableBonds(mol),
        rdMolDescriptors.CalcNumRings(mol),
        rdMolDescriptors.CalcNumAromaticRings(mol),
        len(Chem.FindMolChiralCenters(mol, includeUnassigned=True)),
        QED.qed(mol),
    ]


def load_json_rows(path: Path) -> list[dict[str, object]]:
    if not path.exists():
        return []
    try:
        rows = json.loads(path.read_text())
    except Exception:
        return []
    return rows if isinstance(rows, list) else []


def md_bonus_by_job() -> dict[str, float]:
    bonus: dict[str, float] = {}
    for path in [
        ROOT / "pilot/md_r15_chromanol_top3_30ns/summary.json",
        ROOT / "pilot/md_r16_chromanol_topical_priority_30ns/summary.json",
        ROOT / "pilot/md_r16_chromanol_topical_tgfb1_top6_60ns/summary.json",
        ROOT / "pilot/md_r16_chromanol_topical_pigment_representative_60ns/summary.json",
        ROOT / "pilot/md_r16_chromanol_anchor_triad_100ns/summary.json",
    ]:
        for row in load_json_rows(path):
            if row.get("status") != "ok" or not row.get("job_id"):
                continue
            max_r = float(row.get("rmsd_max_A", 99))
            last = float(row.get("rmsd_last_third_A", 99))
            stable = max_r <= 2.0 and last <= 1.5
            bonus[str(row["job_id"])] = 0.12 if stable else -0.18
    return bonus


def training_rows() -> pd.DataFrame:
    frames = []
    md_bonus = md_bonus_by_job()
    for path, source, id_col in [
        (OUT / "r15_chromanol_cofold_14targets.csv", "r15", "compound"),
        (OUT / "r16_chromanol_topical_cofold.csv", "r16", "analog_id"),
    ]:
        if not path.exists():
            continue
        df = pd.read_csv(path)
        if "smiles" not in df.columns or "target" not in df.columns:
            continue
        score = pd.to_numeric(df.get("affinity_probability_binary", 0), errors="coerce").fillna(0)
        job_ids = df.get("job_id", pd.Series([""] * len(df))).astype(str)
        y = score + job_ids.map(lambda j: md_bonus.get(j, 0.0)).astype(float)
        frames.append(
            pd.DataFrame(
                {
                    "candidate_id": df.get(id_col, ""),
                    "job_id": job_ids,
                    "target": df["target"].astype(str).str.lower(),
                    "smiles": df["smiles"].astype(str).map(canonical),
                    "source": source,
                    "observed_score": y.clip(0, 1),
                }
            )
        )
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def target_list() -> list[str]:
    path = OUT / "target_evidence_gate.csv"
    if not path.exists():
        return ["tgfb1", "mmp1", "tyr", "dct"]
    df = pd.read_csv(path)
    green = df[df["gate"].eq("green")]["target"].astype(str).str.lower().tolist()
    return green[:14] or ["tgfb1", "mmp1", "tyr", "dct"]


def candidate_pool() -> pd.DataFrame:
    frames = []
    syn = OUT / "synthesis_retrosynthesis_gate.csv"
    if syn.exists():
        df = pd.read_csv(syn)
        keep = df[df["synthesis_gate"].isin(["green", "yellow"])].copy()
        frames.append(
            pd.DataFrame(
                {
                    "candidate_id": keep.get("candidate_id", ""),
                    "target": keep.get("target", ""),
                    "smiles": keep.get("smiles", ""),
                    "source": keep.get("source", "synthesis_gate"),
                    "synthesis_score": keep.get("synthesis_score", 0.5),
                    "synthesis_gate": keep.get("synthesis_gate", ""),
                }
            )
        )
    npass = OUT / "npass_xtb_refine_best_candidates.csv"
    if npass.exists():
        df = pd.read_csv(npass).head(80)
        expanded = []
        for _, row in df.iterrows():
            for target in target_list()[:8]:
                expanded.append(
                    {
                        "candidate_id": row.get("np_id", ""),
                        "target": target,
                        "smiles": canonical(str(row.get("smiles", ""))),
                        "source": "npass_xtb_best_cross_target",
                        "synthesis_score": 0.55,
                        "synthesis_gate": "yellow",
                    }
                )
        frames.append(pd.DataFrame(expanded))
    pool = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
    if pool.empty:
        return pool
    pool["smiles"] = pool["smiles"].astype(str).map(canonical)
    pool["target"] = pool["target"].fillna("").astype(str).str.lower()
    pool.loc[pool["target"].isin(["", "nan", "none", "null"]), "target"] = ""
    missing_target = pool["target"].eq("")
    if missing_target.any():
        expanded = []
        for _, row in pool[missing_target].iterrows():
            for target in target_list()[:8]:
                new_row = row.to_dict()
                new_row["target"] = target
                new_row["source"] = f"{new_row.get('source', 'candidate_pool')}_cross_target"
                expanded.append(new_row)
        pool = pd.concat([pool[~missing_target], pd.DataFrame(expanded)], ignore_index=True)
    pool = pool[pool["smiles"].ne("")]
    return pool.drop_duplicates(subset=["candidate_id", "target", "smiles"])


def make_matrix(df: pd.DataFrame, targets: list[str]) -> tuple[np.ndarray, list[int]]:
    rows = []
    valid_idx = []
    for i, row in df.iterrows():
        d = desc(str(row["smiles"]))
        if d is None:
            continue
        target = str(row["target"]).lower()
        one_hot = [1.0 if target == t else 0.0 for t in targets]
        rows.append(d + one_hot)
        valid_idx.append(i)
    return np.asarray(rows, dtype=float), valid_idx


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    now = datetime.now(ZoneInfo("Asia/Seoul")).isoformat(timespec="seconds")
    train = training_rows()
    pool = candidate_pool()
    targets = sorted(set(train.get("target", pd.Series(dtype=str)).astype(str).str.lower().tolist() + target_list()))
    if train.empty or len(train) < 6 or pool.empty:
        CSV_OUT.write_text("", encoding="utf-8")
        SUMMARY_OUT.write_text(json.dumps({"timestamp": now, "status": "insufficient_data"}, indent=2), encoding="utf-8")
        DOC.write_text("# Active-learning Docking Surrogate\n\ninsufficient local data\n", encoding="utf-8")
        print("insufficient data")
        return 0

    X, train_idx = make_matrix(train, targets)
    y = train.loc[train_idx, "observed_score"].astype(float).to_numpy()
    model = RandomForestRegressor(n_estimators=220, min_samples_leaf=2, random_state=17, n_jobs=1)
    if len(y) >= 8:
        pred_cv = cross_val_predict(model, X, y, cv=LeaveOneOut(), n_jobs=1)
        mae = float(mean_absolute_error(y, pred_cv))
    else:
        mae = math.nan
    model.fit(X, y)

    Xp, pool_idx = make_matrix(pool, targets)
    pred_each = np.asarray([tree.predict(Xp) for tree in model.estimators_])
    mean = pred_each.mean(axis=0)
    std = pred_each.std(axis=0)
    labeled = set(zip(train["smiles"], train["target"]))
    rows = []
    for k, idx in enumerate(pool_idx):
        row = pool.loc[idx].to_dict()
        duplicate = (row["smiles"], row["target"]) in labeled
        synth = float(row.get("synthesis_score") or 0.5)
        gate_bonus = 0.04 if row.get("synthesis_gate") == "green" else 0.0
        acquisition = float(mean[k] + 0.35 * std[k] + 0.08 * synth + gate_bonus - (0.08 if duplicate else 0.0))
        rows.append(
            {
                **row,
                "predicted_score": round(float(mean[k]), 4),
                "uncertainty": round(float(std[k]), 4),
                "acquisition_score": round(acquisition, 4),
                "already_labeled_pair": duplicate,
                "recommended_next_fidelity": "Boltz-2 cofold" if not duplicate else "skip_or_MD_if_unvalidated",
            }
        )
    rows.sort(key=lambda r: float(r["acquisition_score"]), reverse=True)
    with CSV_OUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    summary = {
        "timestamp": now,
        "training_rows": len(train),
        "candidate_rows": len(rows),
        "targets": targets,
        "loo_mae": None if math.isnan(mae) else round(mae, 4),
        "csv": str(CSV_OUT.relative_to(ROOT)),
    }
    SUMMARY_OUT.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    lines = [
        "# Active-learning Docking Surrogate",
        "",
        f"- timestamp: `{now}`",
        f"- training_rows: `{len(train)}`",
        f"- candidate_rows: `{len(rows)}`",
        f"- leave-one-out MAE: `{summary['loo_mae']}`",
        "- purpose: 이미 계산한 Boltz/MD 결과에서 다음 cofold 후보를 능동 선택한다.",
        "",
        "## Top Recommendations",
        "",
        "| rank | candidate | target | source | predicted | uncertainty | acquisition | next |",
        "|---:|---|---|---|---:|---:|---:|---|",
    ]
    for i, row in enumerate(rows[:25], 1):
        lines.append(
            f"| {i} | {row['candidate_id']} | {row['target']} | {row['source']} | {row['predicted_score']} | {row['uncertainty']} | {row['acquisition_score']} | {row['recommended_next_fidelity']} |"
        )
    lines.extend(
        [
            "",
            "## Curator Use",
            "",
            "- `acquisition_score` 상위 후보 중 synthesis gate가 `red`가 아닌 것을 우선한다.",
            "- 이미 labeled pair는 중복 cofold하지 말고 MD/pose/consensus 보강 여부만 본다.",
            "- 모델은 local surrogate이므로 논문에는 후보 선택 heuristic으로만 서술한다.",
            "",
        ]
    )
    DOC.write_text("\n".join(lines), encoding="utf-8")
    print(f"Saved {CSV_OUT.relative_to(ROOT)}")
    print(f"Saved {DOC.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
