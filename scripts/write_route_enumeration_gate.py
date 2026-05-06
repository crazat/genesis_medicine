"""Route-enumeration pre-gate for chromanol and NPASS candidates."""
from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd
from rdkit import Chem, RDLogger
from rdkit.Chem import Descriptors, Lipinski, rdMolDescriptors


RDLogger.DisableLog("rdApp.*")

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_meaningful"
CSV_OUT = OUT / "route_enumeration_gate.csv"
DOC = ROOT / "docs/ROUTE_ENUMERATION_GATE.md"


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
        (OUT / "synthesis_retrosynthesis_gate.csv", "synthesis_gate", "candidate_id", "upstream_score"),
        (OUT / "active_learning_next_candidates.csv", "active_learning", "candidate_id", "acquisition_score"),
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
                    "upstream_score": df.get(score_col, 0),
                }
            )
        )
    if not frames:
        return pd.DataFrame()
    out = pd.concat(frames, ignore_index=True)
    out["smiles"] = out["smiles"].astype(str).map(canonical)
    out = out[out["smiles"].ne("")]
    return out.drop_duplicates(subset=["candidate_id", "target", "smiles"])


def classify_route(smiles: str, candidate_id: str) -> dict[str, object]:
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return {
            "route_gate": "red",
            "route_family": "invalid",
            "estimated_steps": 99,
            "route_confidence": 0.0,
            "route_risk": "invalid_smiles",
            "route_next_action": "fix structure",
        }
    mw = Descriptors.MolWt(mol)
    logp = Descriptors.MolLogP(mol)
    rotb = Lipinski.NumRotatableBonds(mol)
    rings = rdMolDescriptors.CalcNumRings(mol)
    aromatic = rdMolDescriptors.CalcNumAromaticRings(mol)
    hetero = sum(1 for atom in mol.GetAtoms() if atom.GetSymbol() not in {"C", "H"})
    halogens = sum(1 for atom in mol.GetAtoms() if atom.GetSymbol() in {"F", "Cl", "Br", "I"})
    has_chromanol = bool(mol.HasSubstructMatch(Chem.MolFromSmarts("c1ccc2c(c1)OCCC2")))
    if has_chromanol:
        route_family = "chromanol_core_late_stage_substitution"
        steps = 3 + min(2, halogens) + (1 if "OMe" in candidate_id or "OH" in candidate_id else 0)
        confidence = 0.82
    elif mw <= 350 and rings <= 3 and hetero <= 8:
        route_family = "medchem_small_molecule_route_search"
        steps = 4 + max(0, rings - 1)
        confidence = 0.62
    else:
        route_family = "natural_product_or_complex_route"
        steps = 7 + max(0, rings - 3)
        confidence = 0.38
    risk: list[str] = []
    if mw > 500:
        risk.append("high_MW")
    if rotb > 8:
        risk.append("high_flexibility")
    if rings >= 5:
        risk.append("polycyclic_complexity")
    if halogens >= 3:
        risk.append("multi_halogenation_regioselectivity")
    if logp > 4.0:
        risk.append("lipophilic_impurity_risk")
    if not risk and confidence >= 0.75:
        gate = "route_ready"
    elif confidence >= 0.55 and len(risk) <= 1:
        gate = "route_review"
    else:
        gate = "route_hard"
    return {
        "route_gate": gate,
        "route_family": route_family,
        "estimated_steps": steps,
        "route_confidence": round(confidence - 0.06 * len(risk), 3),
        "route_risk": ";".join(risk) if risk else "no_major_route_risk",
        "route_next_action": (
            "ASKCOS/AiZynthFinder route enumeration and vendor precursor search"
            if gate == "route_ready"
            else "manual retrosynthesis review before GPU expansion"
            if gate == "route_review"
            else "do not prioritize until route is solved"
        ),
    }


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    now = datetime.now(ZoneInfo("Asia/Seoul")).isoformat(timespec="seconds")
    candidates = collect_candidates()
    rows: list[dict[str, object]] = []
    for _, row in candidates.iterrows():
        route = classify_route(str(row["smiles"]), str(row["candidate_id"]))
        rows.append({**row.to_dict(), **route})
    rows.sort(key=lambda r: ({"route_ready": 0, "route_review": 1, "route_hard": 2, "red": 3}.get(str(r["route_gate"]), 9), -float(r.get("upstream_score", 0) or 0)))
    if rows:
        with CSV_OUT.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
    else:
        CSV_OUT.write_text("", encoding="utf-8")
    counts = {k: sum(1 for r in rows if r["route_gate"] == k) for k in ["route_ready", "route_review", "route_hard", "red"]}
    lines = [
        "# Route Enumeration Gate",
        "",
        f"- timestamp: `{now}`",
        f"- rows: `{len(rows)}`",
        f"- gate_counts: `{counts}`",
        "- purpose: SA score를 넘어서 실제 route enumeration이 필요한 후보와 바로 vendor/precursor search로 갈 후보를 분리한다.",
        "",
        "## Top Route-Ready/Review Rows",
        "",
        "| candidate | target | gate | family | steps | confidence | risk | next |",
        "|---|---|---|---|---:|---:|---|---|",
    ]
    for item in rows[:35]:
        lines.append(
            f"| {item['candidate_id']} | {item['target']} | {item['route_gate']} | {item['route_family']} | {item['estimated_steps']} | {item['route_confidence']} | {item['route_risk']} | {item['route_next_action']} |"
        )
    lines.extend(
        [
            "",
            "## Curator Rule",
            "",
            "- `route_ready`: GPU cofold/MD 확장 또는 CRO RFQ 후보로 유지한다.",
            "- `route_review`: ASKCOS/AiZynthFinder/manual route 전까지 대규모 GPU 확장은 보류한다.",
            "- `route_hard`: atlas/methodology paper에는 가능하지만 lead paper main table에는 올리지 않는다.",
            "",
        ]
    )
    DOC.write_text("\n".join(lines), encoding="utf-8")
    print(f"Saved {CSV_OUT.relative_to(ROOT)}")
    print(f"Saved {DOC.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
