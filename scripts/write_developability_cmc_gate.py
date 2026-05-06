"""Developability and CMC pre-gate for topical/systemic lead triage."""
from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd
from rdkit import Chem, RDLogger
from rdkit.Chem import Crippen, Descriptors, Lipinski, rdMolDescriptors


RDLogger.DisableLog("rdApp.*")

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_meaningful"
DOC = ROOT / "docs/DEVELOPABILITY_CMC_GATE.md"
CSV_OUT = OUT / "developability_cmc_gate.csv"

ALERT_SMARTS = {
    "catechol_or_resorcinol": "c(O)cc(O)",
    "phenol": "c[OX2H]",
    "aldehyde": "[CX3H1](=O)[#6]",
    "michael_acceptor": "C=CC=O",
    "nitro": "[NX3](=O)=O",
    "ester_hydrolysis": "C(=O)O[#6]",
    "aryl_halogen": "c[Cl,Br,I]",
}


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()


def col(df: pd.DataFrame, names: list[str], default: object = "") -> pd.Series:
    for name in names:
        if name in df.columns:
            return df[name]
    return pd.Series([default] * len(df), index=df.index)


def canonical(smiles: str) -> str:
    mol = Chem.MolFromSmiles(str(smiles))
    return Chem.MolToSmiles(mol, canonical=True) if mol else str(smiles)


def collect_candidates() -> pd.DataFrame:
    frames = []
    for path, source, id_cols in [
        (OUT / "r16_chromanol_topical_cofold.csv", "r16_chromanol", ["analog_id"]),
        (OUT / "r15_chromanol_cofold_14targets.csv", "r15_chromanol", ["compound"]),
        (OUT / "r15_master_triage.csv", "r15_triage", ["leader_seed"]),
        (OUT / "npass_xtb_refine_best_candidates.csv", "npass_xtb", ["np_id"]),
        (OUT / "topical_formulation_bo_plan.csv", "formulation_bo", ["compound_id"]),
    ]:
        df = read_csv(path)
        if df.empty or "smiles" not in df.columns:
            continue
        frames.append(
            pd.DataFrame(
                {
                    "candidate_id": col(df, id_cols),
                    "target": col(df, ["target"]),
                    "smiles": col(df, ["smiles", "derivative_smiles"]),
                    "source": source,
                    "score": pd.to_numeric(
                        col(df, ["affinity_probability_binary", "score", "topical_xtb_priority"], 0),
                        errors="coerce",
                    ).fillna(0),
                }
            )
        )
    if not frames:
        return pd.DataFrame()
    out = pd.concat(frames, ignore_index=True)
    out["smiles"] = out["smiles"].fillna("").astype(str).map(canonical)
    out["target"] = out["target"].fillna("").astype(str).str.lower().replace({"nan": ""})
    out["candidate_id"] = out["candidate_id"].fillna("").astype(str)
    return out[out["smiles"].ne("")].drop_duplicates(subset=["candidate_id", "target", "smiles"])


def aromatic_proportion(mol: Chem.Mol) -> float:
    heavy = max(1, mol.GetNumHeavyAtoms())
    aromatic = sum(1 for atom in mol.GetAtoms() if atom.GetIsAromatic())
    return aromatic / heavy


def esol_proxy(mol: Chem.Mol, logp: float, mw: float, rotb: int) -> float:
    return 0.16 - 0.63 * logp - 0.0062 * mw + 0.066 * rotb - 0.74 * aromatic_proportion(mol)


def alerts(mol: Chem.Mol) -> list[str]:
    hits = []
    for name, smarts in ALERT_SMARTS.items():
        patt = Chem.MolFromSmarts(smarts)
        if patt is not None and mol.HasSubstructMatch(patt):
            hits.append(name)
    return hits


def classify(row: pd.Series) -> dict[str, object]:
    smi = str(row["smiles"])
    mol = Chem.MolFromSmiles(smi)
    if mol is None:
        return {
            "candidate_id": row.get("candidate_id", ""),
            "target": row.get("target", ""),
            "source": row.get("source", ""),
            "smiles": smi,
            "developability_gate": "red",
            "cmc_alerts": "invalid_smiles",
            "next_action": "fix structure before developability assessment",
        }
    mw = Descriptors.MolWt(mol)
    logp = Crippen.MolLogP(mol)
    tpsa = rdMolDescriptors.CalcTPSA(mol)
    rotb = Lipinski.NumRotatableBonds(mol)
    hbd = Lipinski.NumHDonors(mol)
    hba = Lipinski.NumHAcceptors(mol)
    rings = rdMolDescriptors.CalcNumRings(mol)
    aromatic = rdMolDescriptors.CalcNumAromaticRings(mol)
    fsp3 = rdMolDescriptors.CalcFractionCSP3(mol)
    log_s = esol_proxy(mol, logp, mw, rotb)
    flags = alerts(mol)
    if log_s < -5:
        flags.append("poor_solubility_proxy")
    if logp > 4.5:
        flags.append("high_lipophilicity_scaleup")
    if aromatic >= 3 and fsp3 < 0.25:
        flags.append("solid_form_polymorph_watch")
    if rotb >= 9:
        flags.append("high_flexibility_impurity_method_watch")
    if mw < 120:
        flags.append("volatile_or_retention_risk")

    topical_fit = 1.0 <= logp <= 3.5 and mw <= 500 and tpsa <= 120 and log_s >= -5.5
    systemic_fit = mw <= 500 and logp <= 5 and hbd <= 5 and hba <= 10 and log_s >= -6
    severe = {"invalid_smiles", "aldehyde", "michael_acceptor", "nitro"}
    if any(flag in severe for flag in flags) or log_s < -6.5:
        gate = "red"
    elif not topical_fit or len(flags) >= 3:
        gate = "yellow"
    else:
        gate = "green"
    if gate == "green":
        action = "advance with solubility, pH stability, and vehicle compatibility screen"
    elif gate == "yellow":
        action = "run CMC de-risking before lead claim: kinetic solubility, pH stability, excipient compatibility"
    else:
        action = "do not promote until reactive/solubility/developability risk is resolved"
    return {
        "candidate_id": row.get("candidate_id", ""),
        "target": row.get("target", ""),
        "source": row.get("source", ""),
        "smiles": smi,
        "score": round(float(row.get("score", 0) or 0), 4),
        "MW": round(mw, 3),
        "cLogP": round(logp, 3),
        "TPSA": round(tpsa, 3),
        "HBD": hbd,
        "HBA": hba,
        "rotatable_bonds": rotb,
        "rings": rings,
        "aromatic_rings": aromatic,
        "fraction_csp3": round(float(fsp3), 3),
        "logS_ESOL_proxy": round(float(log_s), 3),
        "topical_developability_fit": topical_fit,
        "systemic_developability_fit": systemic_fit,
        "cmc_alerts": ";".join(dict.fromkeys(flags)) if flags else "none_detected",
        "developability_gate": gate,
        "next_action": action,
    }


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    now = datetime.now(ZoneInfo("Asia/Seoul")).isoformat(timespec="seconds")
    rows = [classify(row) for _, row in collect_candidates().iterrows()]
    rows.sort(key=lambda r: ({"green": 0, "yellow": 1, "red": 2}.get(str(r["developability_gate"]), 9), -float(r.get("score", 0) or 0)))

    if rows:
        with CSV_OUT.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
    else:
        CSV_OUT.write_text("", encoding="utf-8")

    counts = {gate: sum(1 for row in rows if row["developability_gate"] == gate) for gate in ["green", "yellow", "red"]}
    lines = [
        "# Developability CMC Gate",
        "",
        f"- timestamp: `{now}`",
        f"- rows: `{len(rows)}`",
        f"- gate_counts: `{counts}`",
        "- purpose: hit/lead 후보를 solubility, stability, excipient compatibility, solid-form risk, scale-up risk 관점으로 조기 제한한다.",
        "",
        "## Top Rows",
        "",
        "| candidate | target | gate | cLogP | logS proxy | alerts | next |",
        "|---|---|---|---:|---:|---|---|",
    ]
    for row in rows[:35]:
        lines.append(
            f"| {row['candidate_id']} | {row['target']} | {row['developability_gate']} | {row.get('cLogP','')} | {row.get('logS_ESOL_proxy','')} | {row['cmc_alerts']} | {row['next_action']} |"
        )
    lines.extend(
        [
            "",
            "## Curator Rule",
            "",
            "- `green`: lead table에 둘 수 있으나 solubility/pH stability/vehicle compatibility는 pending으로 명시한다.",
            "- `yellow`: 더 큰 GPU 확장 전에 CMC de-risking 또는 구조 수정 후보로 보낸다.",
            "- `red`: manuscript lead claim에서 제외하고 failure-mode 또는 redesign 후보로만 쓴다.",
            "",
        ]
    )
    DOC.write_text("\n".join(lines), encoding="utf-8")
    print(f"Saved {CSV_OUT.relative_to(ROOT)}")
    print(f"Saved {DOC.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
