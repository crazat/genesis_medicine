"""Synthesis and retrosynthesis readiness gate for current candidates.

This is a local, lightweight gate. It does not claim a true retrosynthesis
solution unless a CASP engine is present; instead it provides a conservative
medicinal-chemistry triage and records which stronger route planner is missing.
"""
from __future__ import annotations

import csv
import importlib.util
import math
import subprocess
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd
from rdkit import Chem, RDLogger
from rdkit.Chem import AllChem, Descriptors, Lipinski, QED, rdMolDescriptors


RDLogger.DisableLog("rdApp.*")

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_meaningful"
DOC = ROOT / "docs/SYNTHESIS_RETROSYNTHESIS_GATE.md"
CSV_OUT = OUT / "synthesis_retrosynthesis_gate.csv"

ALLOWED_ATOMS = {"B", "Br", "C", "Cl", "F", "H", "I", "N", "O", "P", "S", "Si"}


def package_available(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def command_available(name: str) -> bool:
    proc = subprocess.run(["bash", "-lc", f"command -v {name}"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
    return proc.returncode == 0


def canonical(smiles: str) -> str:
    mol = Chem.MolFromSmiles(str(smiles))
    return Chem.MolToSmiles(mol, canonical=True) if mol else str(smiles)


def collect_candidates() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    sources = [
        (OUT / "r15_chromanol_cofold_14targets.csv", "r15_chromanol_cofold", "compound", "target", "affinity_probability_binary"),
        (OUT / "r16_chromanol_topical_cofold.csv", "r16_chromanol_topical_cofold", "analog_id", "target", "affinity_probability_binary"),
        (OUT / "npass_xtb_refine_best_candidates.csv", "npass_xtb_best", "np_id", None, "topical_xtb_priority"),
    ]
    for path, source, id_col, target_col, score_col in sources:
        if not path.exists() or path.stat().st_size == 0:
            continue
        try:
            df = pd.read_csv(path)
        except Exception:
            continue
        if "smiles" not in df.columns:
            continue
        for _, row in df.iterrows():
            smi = row.get("smiles", "")
            if not isinstance(smi, str) or not smi:
                continue
            rows.append(
                {
                    "candidate_id": row.get(id_col, ""),
                    "target": row.get(target_col, "") if target_col else "",
                    "source": source,
                    "smiles": canonical(smi),
                    "upstream_score": row.get(score_col, ""),
                    "logP_input": row.get("logP", ""),
                    "mw_input": row.get("mw", row.get("MW", "")),
                    "skin_window_like": row.get("skin_window_like", row.get("skin_window", "")),
                }
            )
    dedup: dict[tuple[str, str, str], dict[str, object]] = {}
    for row in rows:
        key = (str(row["candidate_id"]), str(row["target"]), str(row["smiles"]))
        dedup[key] = row
    return list(dedup.values())


def complexity_gate(smiles: str) -> dict[str, object]:
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return {"mol_ok": False, "synthesis_score": 0.0, "synthesis_gate": "red", "route_risk_reason": "invalid SMILES"}
    atoms = {atom.GetSymbol() for atom in mol.GetAtoms()}
    mw = Descriptors.MolWt(mol)
    logp = Descriptors.MolLogP(mol)
    tpsa = rdMolDescriptors.CalcTPSA(mol)
    hbd = Lipinski.NumHDonors(mol)
    hba = Lipinski.NumHAcceptors(mol)
    rotb = Lipinski.NumRotatableBonds(mol)
    rings = rdMolDescriptors.CalcNumRings(mol)
    aromatic_rings = rdMolDescriptors.CalcNumAromaticRings(mol)
    chiral = len(Chem.FindMolChiralCenters(mol, includeUnassigned=True))
    bridgeheads = rdMolDescriptors.CalcNumBridgeheadAtoms(mol)
    spiro = rdMolDescriptors.CalcNumSpiroAtoms(mol)
    bertz = Descriptors.BertzCT(mol)
    qed = QED.qed(mol)
    fp_bits = AllChem.GetMorganFingerprintAsBitVect(mol, 2, 2048).GetNumOnBits()

    penalties: list[tuple[str, float]] = []
    rewards: list[tuple[str, float]] = []
    if not atoms.issubset(ALLOWED_ATOMS):
        penalties.append(("unusual atoms", 0.25))
    if mw > 500:
        penalties.append(("MW > 500", min(0.22, (mw - 500) / 900)))
    if rotb > 8:
        penalties.append(("rotatable bonds > 8", min(0.18, (rotb - 8) * 0.025)))
    if rings > 5:
        penalties.append(("ring count > 5", min(0.18, (rings - 5) * 0.04)))
    if chiral > 4:
        penalties.append(("many stereocenters", min(0.2, (chiral - 4) * 0.035)))
    if bridgeheads + spiro > 3:
        penalties.append(("bridged/spiro complexity", min(0.18, (bridgeheads + spiro - 3) * 0.04)))
    if bertz > 900:
        penalties.append(("high graph complexity", min(0.22, (bertz - 900) / 2500)))
    if tpsa > 140:
        penalties.append(("TPSA high", 0.07))
    if hbd > 5 or hba > 10:
        penalties.append(("Lipinski HBD/HBA violation", 0.07))
    if qed >= 0.7:
        rewards.append(("high QED", 0.07))
    if 120 <= mw <= 380 and rotb <= 5 and chiral <= 3:
        rewards.append(("medchem-friendly size/flexibility", 0.10))
    if "OCC1COc2" in smiles or "COc" in smiles:
        rewards.append(("known local chromanol-like chemistry", 0.08))
    if aromatic_rings <= 2 and rings <= 4:
        rewards.append(("moderate ring topology", 0.04))

    score = 0.72 + sum(v for _, v in rewards) - sum(v for _, v in penalties)
    score = max(0.0, min(1.0, score))
    if score >= 0.72:
        gate = "green"
        action = "route request or vendor/building-block search can proceed"
    elif score >= 0.48:
        gate = "yellow"
        action = "run true retrosynthesis or chemist review before expensive follow-up"
    else:
        gate = "red"
        action = "do not promote without synthesis redesign"
    return {
        "mol_ok": True,
        "MW": round(mw, 3),
        "logP": round(logp, 3),
        "TPSA": round(tpsa, 3),
        "HBD": hbd,
        "HBA": hba,
        "rotb": rotb,
        "rings": rings,
        "aromatic_rings": aromatic_rings,
        "chiral_centers": chiral,
        "bridgehead_atoms": bridgeheads,
        "spiro_atoms": spiro,
        "bertz_complexity": round(bertz, 1),
        "QED": round(qed, 3),
        "ecfp_on_bits": fp_bits,
        "synthesis_score": round(score, 3),
        "synthesis_gate": gate,
        "route_risk_reason": "; ".join(reason for reason, _ in penalties) or "no major heuristic route risk",
        "route_positive_reason": "; ".join(reason for reason, _ in rewards) or "no special route reward",
        "next_action": action,
    }


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    now = datetime.now(ZoneInfo("Asia/Seoul")).isoformat(timespec="seconds")
    env = {
        "aizynthfinder_python": package_available("aizynthfinder"),
        "aizynthcli": command_available("aizynthcli"),
        "askcos_cli": command_available("askcos"),
    }
    rows = []
    for row in collect_candidates():
        rows.append({**row, **complexity_gate(str(row["smiles"]))})
    rows.sort(key=lambda r: ({"green": 0, "yellow": 1, "red": 2}.get(str(r.get("synthesis_gate")), 9), -float(r.get("synthesis_score") or 0)))

    fieldnames = list(rows[0].keys()) if rows else ["candidate_id", "target", "source", "smiles"]
    with CSV_OUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    counts = {gate: sum(1 for r in rows if r.get("synthesis_gate") == gate) for gate in ["green", "yellow", "red"]}
    top = rows[:20]
    lines = [
        "# Synthesis and Retrosynthesis Gate",
        "",
        f"- timestamp: `{now}`",
        f"- candidate_rows: `{len(rows)}`",
        f"- gate_counts: `{counts}`",
        f"- CASP availability: `{env}`",
        "- purpose: 계산 후보를 실제 합성 가능성/route risk 관점에서 한 번 더 걸러낸다.",
        "",
        "## Interpretation",
        "",
        "- `green`: 현재 휴리스틱으로는 route risk가 낮다. vendor/building-block 또는 실제 retrosynthesis 확인으로 넘어갈 수 있다.",
        "- `yellow`: 합성 가능할 수 있지만 stereochemistry, size, topology 또는 polarity 때문에 true retrosynthesis 확인이 필요하다.",
        "- `red`: 계산 점수가 높아도 합성/조제 후보로 바로 승격하지 않는다.",
        "- AiZynthFinder/ASKCOS가 설치되지 않은 경우 이 gate는 route solution이 아니라 conservative triage다.",
        "",
        "## Top Candidates",
        "",
        "| candidate | target | source | gate | score | risk |",
        "|---|---|---|---|---:|---|",
    ]
    for row in top:
        lines.append(
            f"| {row['candidate_id']} | {row['target']} | {row['source']} | {row['synthesis_gate']} | {row['synthesis_score']} | {row['route_risk_reason']} |"
        )
    lines.extend(
        [
            "",
            "## Curator Use",
            "",
            "- `green` 후보는 active-learning/Boltz/MD 후속으로 승격 가능하다.",
            "- `yellow` 후보는 true retrosynthesis 또는 chemist review 없이는 논문에서 synthesizable claim을 하지 않는다.",
            "- `red` 후보는 scaffold redesign, building-block replacement, 또는 negative-control로 분류한다.",
            "",
        ]
    )
    DOC.write_text("\n".join(lines), encoding="utf-8")
    print(f"Saved {CSV_OUT.relative_to(ROOT)}")
    print(f"Saved {DOC.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
