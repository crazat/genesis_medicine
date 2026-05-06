"""Metabolism and reactive-metabolite risk pre-gate."""
from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd
from rdkit import Chem, RDLogger
from rdkit.Chem import Descriptors


RDLogger.DisableLog("rdApp.*")

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_meaningful"
CSV_OUT = OUT / "metabolite_reactive_risk_gate.csv"
DOC = ROOT / "docs/METABOLITE_REACTIVE_RISK_GATE.md"

ALERTS = {
    "phenol_phaseII_expected": "c[OX2H]",
    "catechol_redox_alert": "c([OX2H])c[OX2H]",
    "hydroquinone_redox_alert": "c1cc([OX2H])ccc1[OX2H]",
    "quinone_like": "O=C1C=CC(=O)C=C1",
    "aniline_like": "c[NH2]",
    "nitro_aromatic": "c[N+](=O)[O-]",
    "aldehyde": "[CX3H1](=O)[#6]",
    "michael_acceptor": "[C,c]=[C,c]-[C,S](=O)",
    "aryl_halogen_metabolism_review": "c[Cl,Br,I]",
}


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()


def canonical(smiles: str) -> str:
    mol = Chem.MolFromSmiles(str(smiles))
    return Chem.MolToSmiles(mol, canonical=True) if mol else ""


def collect_candidates() -> pd.DataFrame:
    frames = []
    for path, source, id_col, score_col in [
        (OUT / "chromanol_generative_optimizer.csv", "chromanol_generator", "design_id", "local_design_priority"),
        (OUT / "route_enumeration_gate.csv", "route_gate", "candidate_id", "upstream_score"),
        (OUT / "structure_consensus_v2.csv", "structure_consensus", "compound", "consensus_v2_score"),
        (OUT / "dermal_regulatory_safety_gate.csv", "dermal_gate", "candidate_id", "cLogP"),
    ]:
        df = read_csv(path)
        if df.empty or "smiles" not in df.columns:
            continue
        frames.append(pd.DataFrame({"candidate_id": df.get(id_col, ""), "target": df.get("target", ""), "smiles": df["smiles"], "source": source, "upstream_score": df.get(score_col, 0)}))
    if not frames:
        return pd.DataFrame()
    out = pd.concat(frames, ignore_index=True)
    out["smiles"] = out["smiles"].astype(str).map(canonical)
    return out[out["smiles"].ne("")].drop_duplicates(subset=["candidate_id", "target", "smiles"])


def classify(smiles: str) -> dict[str, object]:
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return {"metabolite_risk_gate": "structure_fix", "alerts": "invalid_smiles", "next_action": "fix structure"}
    hits = []
    for name, smarts in ALERTS.items():
        patt = Chem.MolFromSmarts(smarts)
        if patt is not None and mol.HasSubstructMatch(patt):
            hits.append(name)
    mw = Descriptors.MolWt(mol)
    logp = Descriptors.MolLogP(mol)
    phase2 = "glucuronidation/sulfation likely" if "phenol_phaseII_expected" in hits else "standard phase I/II screen"
    if any(h in hits for h in ["catechol_redox_alert", "hydroquinone_redox_alert", "quinone_like", "aniline_like", "nitro_aromatic", "michael_acceptor"]):
        gate = "reactive_metabolite_review"
        action = "run BioTransformer/FAME-style metabolite prediction and avoid safety overclaim"
    elif hits:
        gate = "metabolism_caveat"
        action = "add Phase I/II metabolite caveat and queue metabolite ADMET if promoted"
    else:
        gate = "low_reactive_alert"
        action = "standard metabolite prediction before wet-lab package"
    return {
        "MW": round(mw, 3),
        "cLogP": round(logp, 3),
        "alerts": ";".join(hits) if hits else "none_detected",
        "predicted_primary_metabolism": phase2,
        "biotransformer_followup": "custom MultiBio human Phase I/II;skin metabolism literature check",
        "metabolite_risk_gate": gate,
        "next_action": action,
    }


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    now = datetime.now(ZoneInfo("Asia/Seoul")).isoformat(timespec="seconds")
    candidates = collect_candidates()
    rows = [{**row.to_dict(), **classify(str(row["smiles"]))} for _, row in candidates.iterrows()]
    rows.sort(key=lambda r: {"low_reactive_alert": 0, "metabolism_caveat": 1, "reactive_metabolite_review": 2, "structure_fix": 3}.get(str(r["metabolite_risk_gate"]), 9))
    if rows:
        with CSV_OUT.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
    else:
        CSV_OUT.write_text("", encoding="utf-8")
    counts = {g: sum(1 for r in rows if r["metabolite_risk_gate"] == g) for g in ["low_reactive_alert", "metabolism_caveat", "reactive_metabolite_review", "structure_fix"]}
    lines = [
        "# Metabolite Reactive Risk Gate",
        "",
        f"- timestamp: `{now}`",
        f"- rows: `{len(rows)}`",
        f"- gate_counts: `{counts}`",
        "- purpose: BioTransformer/FAME류 대사체 예측 전 단계로 phenol/redox/quinone/aryl-halogen/reactive-metabolite risk를 표시한다.",
        "",
        "## Metabolism Risk Rows",
        "",
        "| candidate | target | gate | alerts | metabolism | next |",
        "|---|---|---|---|---|---|",
    ]
    for row in rows[:45]:
        lines.append(
            f"| {row['candidate_id']} | {row['target']} | {row['metabolite_risk_gate']} | {row['alerts']} | {row['predicted_primary_metabolism']} | {row['next_action']} |"
        )
    lines.extend(
        [
            "",
            "## Curator Rule",
            "",
            "- `reactive_metabolite_review`: safety/main lead claim 전에 metabolite prediction 또는 assay caveat를 붙인다.",
            "- `metabolism_caveat`: Phase II/skin metabolism caveat를 논문 limitation에 넣는다.",
            "- `low_reactive_alert`: standard ADMET/MetID follow-up 후보로 유지한다.",
            "",
        ]
    )
    DOC.write_text("\n".join(lines), encoding="utf-8")
    print(f"Saved {CSV_OUT.relative_to(ROOT)}")
    print(f"Saved {DOC.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
