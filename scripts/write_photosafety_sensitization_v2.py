"""Photosafety and skin-sensitization decision gate."""
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
CSV_OUT = OUT / "photosafety_sensitization_v2.csv"
DOC = ROOT / "docs/PHOTOSAFETY_SENSITIZATION_V2.md"

SENS_ALERTS = {
    "aldehyde": "[CX3H1](=O)[#6]",
    "epoxide": "C1OC1",
    "michael_acceptor": "[C,c]=[C,c]-[C,S](=O)",
    "isocyanate": "N=C=O",
    "acid_halide": "C(=O)[Cl,Br,I,F]",
    "sulfonyl_halide": "S(=O)(=O)[Cl,Br,I,F]",
    "anhydride": "C(=O)OC(=O)",
    "quinone": "O=C1C=CC(=O)C=C1",
}


def canonical(smiles: str) -> str:
    mol = Chem.MolFromSmiles(str(smiles))
    return Chem.MolToSmiles(mol, canonical=True) if mol else ""


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()


def collect_candidates() -> pd.DataFrame:
    frames = []
    for path, source, id_col, score_col in [
        (OUT / "r16_chromanol_topical_cofold.csv", "r16_cofold", "analog_id", "affinity_probability_binary"),
        (OUT / "r15_chromanol_cofold_14targets.csv", "r15_cofold", "compound", "affinity_probability_binary"),
        (OUT / "chromanol_generative_optimizer.csv", "chromanol_generator", "design_id", "local_design_priority"),
        (OUT / "route_enumeration_gate.csv", "route_gate", "candidate_id", "upstream_score"),
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
    return out[out["smiles"].ne("")].drop_duplicates(subset=["candidate_id", "target", "smiles"])


def match_alerts(mol: Chem.Mol) -> list[str]:
    hits = []
    for name, smarts in SENS_ALERTS.items():
        patt = Chem.MolFromSmarts(smarts)
        if patt is not None and mol.HasSubstructMatch(patt):
            hits.append(name)
    return hits


def classify(smiles: str, target: str) -> dict[str, object]:
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return {
            "safety_gate_v2": "red",
            "sensitization_alerts": "invalid_smiles",
            "photosafety_alerts": "invalid_smiles",
            "assay_package": "fix_structure",
            "next_action": "fix structure",
        }
    mw = Descriptors.MolWt(mol)
    logp = Descriptors.MolLogP(mol)
    tpsa = rdMolDescriptors.CalcTPSA(mol)
    hbd = Lipinski.NumHDonors(mol)
    hba = Lipinski.NumHAcceptors(mol)
    arom = rdMolDescriptors.CalcNumAromaticRings(mol)
    halogen_aromatic = any(atom.GetSymbol() in {"Cl", "Br", "I"} for atom in mol.GetAtoms()) and arom >= 1
    alerts = match_alerts(mol)
    photo: list[str] = []
    if arom >= 2:
        photo.append("extended_aromatic_uv_proxy")
    if halogen_aromatic:
        photo.append("aryl_halogen_photosafety_review")
    if any(name in alerts for name in {"quinone"}):
        photo.append("photoreactive_quinone_proxy")
    pigment_target = str(target).lower() in {"dct", "tyr", "tyrp1", "mc1r"}
    skin_window = 1.0 <= logp <= 3.5 and mw <= 500 and tpsa <= 120 and hbd <= 4 and hba <= 10
    if any(a in alerts for a in {"isocyanate", "acid_halide", "sulfonyl_halide", "anhydride"}):
        gate = "red"
    elif alerts or photo or (pigment_target and halogen_aromatic):
        gate = "yellow"
    elif skin_window:
        gate = "green"
    else:
        gate = "yellow"
    assay = (
        "OECD_TG497_DPRA_KeratinoSens_h-CLAT + ICH_S10_3T3_NRU"
        if gate == "yellow"
        else "avoid_or_redesign_before_topical_claim"
        if gate == "red"
        else "baseline_irritation_IVRT_IVPT_panel"
    )
    return {
        "MW": round(mw, 3),
        "cLogP": round(logp, 3),
        "TPSA": round(tpsa, 3),
        "HBD": hbd,
        "HBA": hba,
        "skin_window_like": skin_window,
        "safety_gate_v2": gate,
        "sensitization_alerts": ";".join(alerts) if alerts else "none_detected",
        "photosafety_alerts": ";".join(photo) if photo else "none_detected",
        "assay_package": assay,
        "next_action": (
            "include safety caveat and order OECD/ICH panel before lead claim"
            if gate == "yellow"
            else "exclude from topical lead claim"
            if gate == "red"
            else "eligible for topical lead table with in-silico caveat"
        ),
    }


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    now = datetime.now(ZoneInfo("Asia/Seoul")).isoformat(timespec="seconds")
    candidates = collect_candidates()
    rows: list[dict[str, object]] = []
    for _, row in candidates.iterrows():
        rows.append({**row.to_dict(), **classify(str(row["smiles"]), str(row["target"]))})
    rows.sort(key=lambda r: ({"green": 0, "yellow": 1, "red": 2}.get(str(r["safety_gate_v2"]), 9), -float(r.get("upstream_score", 0) or 0)))
    if rows:
        with CSV_OUT.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
    else:
        CSV_OUT.write_text("", encoding="utf-8")
    counts = {k: sum(1 for r in rows if r["safety_gate_v2"] == k) for k in ["green", "yellow", "red"]}
    lines = [
        "# Photosafety Sensitization V2",
        "",
        f"- timestamp: `{now}`",
        f"- rows: `{len(rows)}`",
        f"- gate_counts: `{counts}`",
        "- purpose: topical lead claim 전에 OECD TG497 skin sensitization과 ICH S10 photosafety 관점의 assay package를 자동 지정한다.",
        "",
        "## Top Safety Rows",
        "",
        "| candidate | target | gate | cLogP | sensitization | photosafety | assay |",
        "|---|---|---|---:|---|---|---|",
    ]
    for row in rows[:35]:
        lines.append(
            f"| {row['candidate_id']} | {row['target']} | {row['safety_gate_v2']} | {row.get('cLogP', '')} | {row['sensitization_alerts']} | {row['photosafety_alerts']} | {row['assay_package']} |"
        )
    lines.extend(
        [
            "",
            "## Curator Rule",
            "",
            "- `green`: lead table 가능하지만 in-silico safety pre-gate로만 표현한다.",
            "- `yellow`: photosafety/sensitization assay package를 논문 limitation과 CRO card에 붙인다.",
            "- `red`: topical lead claim에서 제외한다.",
            "",
        ]
    )
    DOC.write_text("\n".join(lines), encoding="utf-8")
    print(f"Saved {CSV_OUT.relative_to(ROOT)}")
    print(f"Saved {DOC.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
