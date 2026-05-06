"""Dermal PBPK and IVRT/IVPT readiness gate."""
from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd
from rdkit import Chem, RDLogger
from rdkit.Chem import Descriptors, rdMolDescriptors


RDLogger.DisableLog("rdApp.*")

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_meaningful"
CSV_OUT = OUT / "dermal_pbpk_ivpt_gate.csv"
DOC = ROOT / "docs/DERMAL_PBPK_IVPT_GATE.md"


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()


def canonical(smiles: str) -> str:
    mol = Chem.MolFromSmiles(str(smiles))
    return Chem.MolToSmiles(mol, canonical=True) if mol else str(smiles)


def collect_candidates() -> pd.DataFrame:
    frames = []
    for path, source, id_col in [
        (OUT / "dermal_regulatory_safety_gate.csv", "dermal_gate", "candidate_id"),
        (OUT / "photosafety_sensitization_v2.csv", "photosafety_v2", "candidate_id"),
        (OUT / "chromanol_generative_optimizer.csv", "chromanol_generator", "design_id"),
        (OUT / "structure_consensus_v2.csv", "structure_consensus", "compound"),
    ]:
        df = read_csv(path)
        if df.empty or "smiles" not in df.columns:
            continue
        frames.append(pd.DataFrame({"candidate_id": df.get(id_col, ""), "target": df.get("target", ""), "smiles": df["smiles"], "source": source}))
    if not frames:
        return pd.DataFrame()
    out = pd.concat(frames, ignore_index=True)
    out["smiles"] = out["smiles"].astype(str).map(canonical)
    out["target"] = out["target"].fillna("").astype(str).str.lower().replace({"nan": ""})
    return out[out["smiles"].ne("")].drop_duplicates(subset=["candidate_id", "target", "smiles"])


def classify(smiles: str) -> dict[str, object]:
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return {"dermal_pbpk_gate": "structure_fix", "next_action": "fix structure before IVPT/PBPK planning"}
    mw = Descriptors.MolWt(mol)
    logp = Descriptors.MolLogP(mol)
    tpsa = rdMolDescriptors.CalcTPSA(mol)
    logkp = -2.72 + 0.71 * logp - 0.0061 * mw
    retention = "skin_retention_favored" if -4.5 <= logkp <= -2.5 and 1.0 <= logp <= 3.5 else "permeation_or_delivery_review"
    receptor = "aqueous_with_solubilizer_review" if logp > 3.0 else "standard_buffer_candidate"
    if 150 <= mw <= 500 and 1.0 <= logp <= 3.5 and tpsa <= 120:
        gate = "ivpt_pbpk_ready"
        action = "build finite-dose IVRT/IVPT table and PBPK parameter sheet"
    elif mw <= 500 and tpsa <= 140:
        gate = "formulation_rescue_needed"
        action = "optimize vehicle/solubilizer and define retention vs permeation endpoint"
    else:
        gate = "pbpk_low_confidence"
        action = "do not use as topical exposure lead without formulation and solubility data"
    return {
        "MW": round(mw, 3),
        "cLogP": round(logp, 3),
        "TPSA": round(tpsa, 3),
        "potts_guy_logKp_cm_h": round(logkp, 3),
        "exposure_objective": retention,
        "receptor_medium_hint": receptor,
        "finite_dose_ivpt_inputs_needed": "dose_per_area;vehicle;donor_skin;receptor_medium;sampling_times;skin_retention_fraction",
        "pbpk_inputs_needed": "solubility;pKa;fraction_unbound;stratum_corneum_partition;viable_epidermis_partition;clearance_or_sink_condition",
        "dermal_pbpk_gate": gate,
        "next_action": action,
    }


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    now = datetime.now(ZoneInfo("Asia/Seoul")).isoformat(timespec="seconds")
    candidates = collect_candidates()
    rows = []
    for _, row in candidates.iterrows():
        rows.append({**row.to_dict(), **classify(str(row["smiles"]))})
    rows.sort(key=lambda r: {"ivpt_pbpk_ready": 0, "formulation_rescue_needed": 1, "pbpk_low_confidence": 2, "structure_fix": 3}.get(str(r["dermal_pbpk_gate"]), 9))
    if rows:
        with CSV_OUT.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
    else:
        CSV_OUT.write_text("", encoding="utf-8")
    counts = {g: sum(1 for r in rows if r["dermal_pbpk_gate"] == g) for g in ["ivpt_pbpk_ready", "formulation_rescue_needed", "pbpk_low_confidence", "structure_fix"]}
    lines = [
        "# Dermal PBPK IVPT Gate",
        "",
        f"- timestamp: `{now}`",
        f"- rows: `{len(rows)}`",
        f"- gate_counts: `{counts}`",
        "- purpose: topical lead를 FDA/EMA IVRT/IVPT 및 mechanistic dermal PBPK 입력 표로 연결한다.",
        "",
        "## IVPT/PBPK Rows",
        "",
        "| candidate | target | gate | logKp | objective | receptor | next |",
        "|---|---|---|---:|---|---|---|",
    ]
    for row in rows[:45]:
        lines.append(
            f"| {row['candidate_id']} | {row['target']} | {row['dermal_pbpk_gate']} | {row.get('potts_guy_logKp_cm_h', '')} | {row.get('exposure_objective', '')} | {row.get('receptor_medium_hint', '')} | {row['next_action']} |"
        )
    lines.extend(
        [
            "",
            "## Curator Rule",
            "",
            "- `ivpt_pbpk_ready`: P29/P32 및 CRO RFQ에 finite-dose IVRT/IVPT parameter table을 추가한다.",
            "- `formulation_rescue_needed`: 계산 확장보다 vehicle/formulation BO를 우선한다.",
            "- `pbpk_low_confidence`: topical exposure claim을 제한한다.",
            "",
        ]
    )
    DOC.write_text("\n".join(lines), encoding="utf-8")
    print(f"Saved {CSV_OUT.relative_to(ROOT)}")
    print(f"Saved {DOC.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
