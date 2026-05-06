"""Generate a local chromanol analog design queue.

This is a constrained, chemistry-light generator around the R15/R16 chromanol
core.  It does not claim de novo novelty or activity; it produces valid RDKit
structures and a ranked queue for later Boltz/MD or wet-lab triage.
"""
from __future__ import annotations

import csv
from itertools import combinations, product
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from rdkit import Chem, DataStructs, RDLogger
from rdkit.Chem import Descriptors, Lipinski, rdFingerprintGenerator, rdMolDescriptors


RDLogger.DisableLog("rdApp.*")

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_meaningful"
CSV_OUT = OUT / "chromanol_generative_optimizer.csv"
DOC = ROOT / "docs/CHROMANOL_GENERATIVE_OPTIMIZER.md"

BASE_SMILES = "OCC1COc2cc(O)ccc2C1"
SUBSTITUENTS = {
    "F": "F",
    "Cl": "Cl",
    "Me": "C",
    "OMe": "OC",
    "OH": "O",
    "CN": "C#N",
}
TARGET_BIASES = {
    "tgfb1": 1.00,
    "dct": 0.86,
    "tyr": 0.84,
    "mmp1": 0.74,
    "ptgs2": 0.68,
}


def canonical(smiles: str) -> str:
    mol = Chem.MolFromSmiles(smiles)
    return Chem.MolToSmiles(mol, canonical=True) if mol else ""


def aromatic_h_positions(mol: Chem.Mol) -> list[int]:
    return [
        atom.GetIdx()
        for atom in mol.GetAtoms()
        if atom.GetSymbol() == "C" and atom.GetIsAromatic() and atom.GetTotalNumHs() > 0
    ]


def attach(mol: Chem.Mol, atom_idx: int, subst_smiles: str) -> Chem.Mol | None:
    frag = Chem.MolFromSmiles(subst_smiles)
    if frag is None:
        return None
    combo = Chem.CombineMols(mol, frag)
    rw = Chem.RWMol(combo)
    rw.AddBond(atom_idx, mol.GetNumAtoms(), Chem.BondType.SINGLE)
    out = rw.GetMol()
    try:
        Chem.SanitizeMol(out)
    except Exception:
        return None
    return out


def apply_design(base: Chem.Mol, design: list[tuple[int, str]]) -> Chem.Mol | None:
    mol = Chem.Mol(base)
    for atom_idx, sub_name in design:
        # Original heavy-atom indices are stable because new atoms are appended.
        mol = attach(mol, atom_idx, SUBSTITUENTS[sub_name])
        if mol is None:
            return None
    return mol


def morgan(mol: Chem.Mol):
    generator = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=2048)
    return generator.GetFingerprint(mol)


def descriptors(mol: Chem.Mol) -> dict[str, object]:
    return {
        "MW": round(Descriptors.MolWt(mol), 3),
        "cLogP": round(Descriptors.MolLogP(mol), 3),
        "TPSA": round(rdMolDescriptors.CalcTPSA(mol), 3),
        "HBD": Lipinski.NumHDonors(mol),
        "HBA": Lipinski.NumHAcceptors(mol),
        "rotb": Lipinski.NumRotatableBonds(mol),
        "aromatic_rings": rdMolDescriptors.CalcNumAromaticRings(mol),
        "QED": round(float(Descriptors.qed(mol)), 3),
    }


def topical_score(d: dict[str, object]) -> float:
    logp = float(d["cLogP"])
    mw = float(d["MW"])
    tpsa = float(d["TPSA"])
    hbd = int(d["HBD"])
    hba = int(d["HBA"])
    score = 0.0
    score += max(0.0, 1.0 - abs(logp - 2.1) / 2.2) * 0.34
    score += (1.0 if mw <= 300 else max(0.0, 1.0 - (mw - 300) / 200)) * 0.18
    score += max(0.0, 1.0 - abs(tpsa - 55) / 90) * 0.18
    score += (1.0 if hbd <= 3 else 0.4) * 0.12
    score += (1.0 if hba <= 6 else 0.4) * 0.10
    score += float(d["QED"]) * 0.08
    return round(score, 4)


def collect_known_smiles() -> set[str]:
    known: set[str] = set()
    for path in [
        OUT / "r15_chromanol_cofold_14targets.csv",
        OUT / "r16_chromanol_topical_cofold.csv",
        OUT / "synthesis_retrosynthesis_gate.csv",
    ]:
        if not path.exists() or path.stat().st_size == 0:
            continue
        with path.open(newline="", encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                smi = canonical(row.get("smiles", ""))
                if smi:
                    known.add(smi)
    known.add(canonical(BASE_SMILES))
    return known


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    now = datetime.now(ZoneInfo("Asia/Seoul")).isoformat(timespec="seconds")
    base = Chem.MolFromSmiles(BASE_SMILES)
    if base is None:
        raise RuntimeError("base chromanol SMILES failed")
    base_fp = morgan(base)
    positions = aromatic_h_positions(base)
    known = collect_known_smiles()

    designs: list[list[tuple[int, str]]] = []
    for pos in positions:
        for sub in SUBSTITUENTS:
            designs.append([(pos, sub)])
    for pos_pair in combinations(positions, 2):
        for sub_pair in product(["F", "Cl", "Me", "OMe"], repeat=2):
            designs.append([(pos_pair[0], sub_pair[0]), (pos_pair[1], sub_pair[1])])

    seen: set[str] = set()
    rows: list[dict[str, object]] = []
    for design in designs:
        mol = apply_design(base, design)
        if mol is None:
            continue
        smi = Chem.MolToSmiles(mol, canonical=True)
        if smi in seen:
            continue
        seen.add(smi)
        d = descriptors(mol)
        fp = morgan(mol)
        sim = DataStructs.TanimotoSimilarity(base_fp, fp)
        topo = topical_score(d)
        sub_names = "+".join(s for _, s in design)
        pos_names = "+".join(f"arom{p}" for p, _ in design)
        halogen = any(s in {"Cl", "F"} for _, s in design)
        photo_caution = "aryl_halogen_review" if any(s == "Cl" for _, s in design) else "none_detected"
        synthesis = "route_ready" if all(s in {"F", "Cl", "Me", "OMe", "OH"} for _, s in design) else "route_review"
        novelty = "known_or_precomputed" if smi in known else "new_local_design"
        for target, bias in TARGET_BIASES.items():
            priority = topo * 0.46 + sim * 0.18 + bias * 0.16 + float(d["QED"]) * 0.10
            priority += 0.05 if synthesis == "route_ready" else -0.02
            priority += -0.03 if photo_caution != "none_detected" and target in {"dct", "tyr"} else 0.0
            queue = (
                "Boltz-2_next_when_GPU_free"
                if priority >= 0.70 and novelty == "new_local_design" and synthesis == "route_ready"
                else "keep_for_route_or_safety_review"
                if priority >= 0.62
                else "archive_low_priority"
            )
            rows.append(
                {
                    "design_id": f"chromanol_{pos_names}_{sub_names}_{target}",
                    "target": target,
                    "smiles": smi,
                    "substituents": sub_names,
                    "positions": pos_names,
                    **d,
                    "base_tanimoto": round(sim, 4),
                    "topical_window_score": topo,
                    "target_bias": bias,
                    "local_design_priority": round(priority, 4),
                    "novelty_status": novelty,
                    "synthesis_route_proxy": synthesis,
                    "photosafety_proxy": photo_caution if halogen else "none_detected",
                    "recommended_next_action": queue,
                }
            )

    rows.sort(key=lambda r: float(r["local_design_priority"]), reverse=True)
    with CSV_OUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()) if rows else ["design_id"])
        writer.writeheader()
        writer.writerows(rows)

    counts = {}
    for row in rows:
        key = str(row["recommended_next_action"])
        counts[key] = counts.get(key, 0) + 1
    lines = [
        "# Chromanol Generative Optimizer",
        "",
        f"- timestamp: `{now}`",
        f"- rows: `{len(rows)}`",
        f"- action_counts: `{counts}`",
        "- purpose: R15/R16 chromanol core 주변에서 valid RDKit analog를 만들어 다음 Boltz/route/safety 큐 후보를 넓힌다.",
        "",
        "## Top Local Designs",
        "",
        "| design | target | priority | cLogP | TPSA | novelty | route | photosafety | action |",
        "|---|---|---:|---:|---:|---|---|---|---|",
    ]
    for row in rows[:35]:
        lines.append(
            f"| {row['design_id']} | {row['target']} | {row['local_design_priority']} | {row['cLogP']} | {row['TPSA']} | {row['novelty_status']} | {row['synthesis_route_proxy']} | {row['photosafety_proxy']} | {row['recommended_next_action']} |"
        )
    lines.extend(
        [
            "",
            "## Curator Rule",
            "",
            "- `Boltz-2_next_when_GPU_free`는 GPU가 비고 현재 R16 100 ns가 끝난 뒤 cofold 후보로 올린다.",
            "- `known_or_precomputed`는 중복 계산하지 않고 기존 R15/R16 evidence에 합친다.",
            "- `aryl_halogen_review`는 pigment target에서 photosafety gate를 먼저 본다.",
            "",
        ]
    )
    DOC.write_text("\n".join(lines), encoding="utf-8")
    print(f"Saved {CSV_OUT.relative_to(ROOT)}")
    print(f"Saved {DOC.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
