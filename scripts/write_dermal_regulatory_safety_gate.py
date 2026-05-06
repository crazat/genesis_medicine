"""Dermal regulatory safety gate for topical lead prioritization."""
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
DOC = ROOT / "docs/DERMAL_REGULATORY_SAFETY_GATE.md"
CSV_OUT = OUT / "dermal_regulatory_safety_gate.csv"

ALERTS = {
    "aldehyde": "[CX3H1](=O)[#6]",
    "epoxide": "C1OC1",
    "michael_acceptor": "C=CC=O",
    "acid_chloride": "C(=O)Cl",
    "isocyanate": "N=C=O",
    "isothiocyanate": "N=C=S",
    "sulfonyl_chloride": "S(=O)(=O)Cl",
    "anhydride": "C(=O)OC(=O)",
    "nitro_aromatic": "[NX3](=O)=O",
    "quinone_like": "O=C1C=CC(=O)C=C1",
}


def canonical(smiles: str) -> str:
    mol = Chem.MolFromSmiles(str(smiles))
    return Chem.MolToSmiles(mol, canonical=True) if mol else str(smiles)


def collect_candidates() -> pd.DataFrame:
    frames = []
    for path, source, id_col in [
        (OUT / "r16_chromanol_topical_cofold.csv", "r16_chromanol", "analog_id"),
        (OUT / "r15_chromanol_cofold_14targets.csv", "r15_chromanol", "compound"),
        (OUT / "synthesis_retrosynthesis_gate.csv", "synthesis_gate", "candidate_id"),
        (OUT / "topical_formulation_bo_plan.csv", "formulation_bo", "compound_id"),
    ]:
        if not path.exists() or path.stat().st_size == 0:
            continue
        df = pd.read_csv(path)
        if "smiles" not in df.columns:
            continue
        frames.append(
            pd.DataFrame(
                {
                    "candidate_id": df.get(id_col, ""),
                    "target": df.get("target", ""),
                    "smiles": df["smiles"],
                    "source": source,
                }
            )
        )
    if not frames:
        return pd.DataFrame()
    df = pd.concat(frames, ignore_index=True)
    df["smiles"] = df["smiles"].astype(str).map(canonical)
    df["target"] = df["target"].fillna("").astype(str).str.lower().replace({"nan": ""})
    return df[df["smiles"].ne("")].drop_duplicates(subset=["candidate_id", "target", "smiles"])


def match_alerts(mol: Chem.Mol) -> list[str]:
    hits = []
    for name, smarts in ALERTS.items():
        patt = Chem.MolFromSmarts(smarts)
        if patt is not None and mol.HasSubstructMatch(patt):
            hits.append(name)
    return hits


def classify(smiles: str) -> dict[str, object]:
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return {
            "dermal_gate": "red",
            "sensitization_alerts": "invalid_smiles",
            "photosafety_alerts": "invalid_smiles",
            "ivpt_readiness": "not_ready",
            "regulatory_next_action": "fix structure before regulatory triage",
        }
    mw = Descriptors.MolWt(mol)
    logp = Descriptors.MolLogP(mol)
    tpsa = rdMolDescriptors.CalcTPSA(mol)
    hbd = Lipinski.NumHDonors(mol)
    hba = Lipinski.NumHAcceptors(mol)
    aromatic = rdMolDescriptors.CalcNumAromaticRings(mol)
    alerts = match_alerts(mol)
    photo = []
    if aromatic >= 2:
        photo.append("poly_aromatic_uv_absorber_proxy")
    if any(a in alerts for a in ["nitro_aromatic", "quinone_like"]):
        photo.append("photoreactive_alert_proxy")
    if any(atom.GetSymbol() in {"Cl", "Br", "I"} for atom in mol.GetAtoms()) and aromatic >= 1:
        photo.append("aryl_halogen_photosafety_review")
    skin_window = 1.0 <= logp <= 3.5 and mw <= 500 and tpsa <= 120 and hbd <= 4 and hba <= 10
    if alerts:
        gate = "red" if any(a in alerts for a in ["acid_chloride", "isocyanate", "sulfonyl_chloride", "anhydride"]) else "yellow"
    elif photo:
        gate = "yellow"
    elif skin_window:
        gate = "green"
    else:
        gate = "yellow"
    ivpt = "ready_for_IVRT_IVPT_design" if skin_window and gate != "red" else "needs_formulation_or_safety_review"
    return {
        "MW": round(mw, 3),
        "cLogP": round(logp, 3),
        "TPSA": round(tpsa, 3),
        "HBD": hbd,
        "HBA": hba,
        "skin_window_like": skin_window,
        "dermal_gate": gate,
        "sensitization_alerts": ";".join(alerts) if alerts else "none_detected",
        "photosafety_alerts": ";".join(photo) if photo else "none_detected",
        "ivpt_readiness": ivpt,
        "regulatory_next_action": (
            "OECD TG497/DPRA-KeratinoSens-hCLAT and ICH S10 photosafety triage before lead claim"
            if gate == "yellow"
            else "avoid topical lead claim until alert is resolved"
            if gate == "red"
            else "CRO IVRT/IVPT and irritation panel design"
        ),
    }


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    now = datetime.now(ZoneInfo("Asia/Seoul")).isoformat(timespec="seconds")
    candidates = collect_candidates()
    rows = []
    for _, row in candidates.iterrows():
        metrics = classify(str(row["smiles"]))
        rows.append({**row.to_dict(), **metrics})
    rows.sort(key=lambda r: {"green": 0, "yellow": 1, "red": 2}.get(str(r["dermal_gate"]), 9))
    if rows:
        with CSV_OUT.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
    else:
        CSV_OUT.write_text("", encoding="utf-8")
    counts = {g: sum(1 for r in rows if r["dermal_gate"] == g) for g in ["green", "yellow", "red"]}
    lines = [
        "# Dermal Regulatory Safety Gate",
        "",
        f"- timestamp: `{now}`",
        f"- rows: `{len(rows)}`",
        f"- gate_counts: `{counts}`",
        "- purpose: 외용제 후보를 OECD TG497 skin sensitisation, ICH S10 photosafety, FDA IVRT/IVPT 관점의 in-silico pre-gate로 제한한다.",
        "",
        "## Top Green/Yellow Candidates",
        "",
        "| candidate | target | gate | cLogP | MW | alerts | photosafety | IVPT |",
        "|---|---|---|---:|---:|---|---|---|",
    ]
    for row in rows[:30]:
        lines.append(
            f"| {row['candidate_id']} | {row['target']} | {row['dermal_gate']} | {row.get('cLogP', '')} | {row.get('MW', '')} | {row['sensitization_alerts']} | {row['photosafety_alerts']} | {row['ivpt_readiness']} |"
        )
    lines.extend(
        [
            "",
            "## Curator Rule",
            "",
            "- `green`: topical lead paper main table에 둘 수 있지만 여전히 in-silico pre-gate다.",
            "- `yellow`: OECD TG497/ICH S10/CRO assay plan을 같이 적고 강한 safety claim을 피한다.",
            "- `red`: 외용 lead claim에서 제외하거나 구조 수정 후보로만 둔다.",
            "",
        ]
    )
    DOC.write_text("\n".join(lines), encoding="utf-8")
    print(f"Saved {CSV_OUT.relative_to(ROOT)}")
    print(f"Saved {DOC.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
