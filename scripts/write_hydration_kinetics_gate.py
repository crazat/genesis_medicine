"""Hydration and residence-time follow-up gate from existing pose/MD evidence."""
from __future__ import annotations

import csv
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd
from rdkit import Chem, RDLogger
from rdkit.Chem import Lipinski, rdMolDescriptors


RDLogger.DisableLog("rdApp.*")

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_meaningful"
DOC = ROOT / "docs/HYDRATION_KINETICS_GATE.md"
CSV_OUT = OUT / "hydration_kinetics_gate.csv"


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()


def json_rows(path: Path) -> list[dict[str, object]]:
    if not path.exists() or path.stat().st_size == 0:
        return []
    try:
        rows = json.loads(path.read_text())
    except Exception:
        return []
    return rows if isinstance(rows, list) else []


def md_by_key() -> dict[tuple[str, str], dict[str, object]]:
    out: dict[tuple[str, str], dict[str, object]] = {}
    for path in [
        ROOT / "pilot/md_r15_chromanol_top3_30ns/summary.json",
        ROOT / "pilot/md_r16_chromanol_topical_tgfb1_top6_60ns/summary.json",
        ROOT / "pilot/md_r16_chromanol_topical_pigment_representative_60ns/summary.json",
        ROOT / "pilot/md_r16_chromanol_anchor_triad_100ns/summary.json",
    ]:
        for row in json_rows(path):
            target = str(row.get("target", "")).lower()
            compound = str(row.get("analog_id") or row.get("compound") or "")
            name = str(row.get("name") or "").lower()
            if compound and target:
                out[(compound, target)] = row
            if "__r15_chromanol" in name and target:
                out[("R15_chromanol", target)] = row
    return out


def smiles_lookup() -> dict[str, str]:
    out = {}
    for path, id_col in [
        (OUT / "r16_chromanol_topical_cofold.csv", "analog_id"),
        (OUT / "r15_chromanol_cofold_14targets.csv", "compound"),
    ]:
        df = read_csv(path)
        if df.empty or "smiles" not in df.columns:
            continue
        for _, row in df.iterrows():
            cid = str(row.get(id_col, ""))
            if cid and cid != "nan":
                out[cid] = str(row.get("smiles", ""))
    return out


def ligand_features(smiles: str) -> dict[str, object]:
    mol = Chem.MolFromSmiles(str(smiles))
    if mol is None:
        return {"polar_atom_count": 0, "ring_count": 0, "aromatic_ring_count": 0, "hydration_complexity": "unknown"}
    polar = Lipinski.NumHDonors(mol) + Lipinski.NumHAcceptors(mol)
    rings = rdMolDescriptors.CalcNumRings(mol)
    arom = rdMolDescriptors.CalcNumAromaticRings(mol)
    complexity = "high" if polar >= 6 or rings >= 4 else "moderate" if polar >= 3 or rings >= 2 else "low"
    return {"polar_atom_count": polar, "ring_count": rings, "aromatic_ring_count": arom, "hydration_complexity": complexity}


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    now = datetime.now(ZoneInfo("Asia/Seoul")).isoformat(timespec="seconds")
    consensus = read_csv(OUT / "structure_consensus_calibration.csv")
    md = md_by_key()
    smiles = smiles_lookup()
    rows = []
    if not consensus.empty:
        for _, row in consensus.iterrows():
            target = str(row.get("target", "")).lower()
            compound = str(row.get("compound", ""))
            m = md.get((compound, target), {})
            feat = ligand_features(smiles.get(compound, ""))
            max_r = float(m.get("rmsd_max_A", 99) or 99)
            last = float(m.get("rmsd_last_third_A", 99) or 99)
            ns = float(m.get("ns_simulated", 0) or 0)
            pose = str(row.get("pose_gate", "missing"))
            consensus_class = str(row.get("consensus_class", ""))
            if consensus_class == "high_confidence" and max_r <= 1.5 and last <= 1.0:
                residence = "residence_time_proxy_candidate"
            elif max_r <= 2.0 and last <= 1.5:
                residence = "stability_only_candidate"
            else:
                residence = "not_ready"
            hydration = (
                "WaterKit_or_GIST_priority"
                if feat["hydration_complexity"] in {"moderate", "high"} and pose in {"pass", "review"}
                else "low_priority"
            )
            next_action = (
                "run hydration-site map before substituent optimization"
                if hydration == "WaterKit_or_GIST_priority"
                else "keep RMSD-only caveat"
            )
            if residence == "residence_time_proxy_candidate" and ns >= 60:
                next_action = "consider SMD/tauRAMD-style unbinding proxy after 100 ns anchor summary"
            rows.append(
                {
                    "target": target,
                    "compound": compound,
                    "consensus_class": consensus_class,
                    "pose_gate": pose,
                    "ns_simulated": ns,
                    "rmsd_max_A": max_r if max_r < 90 else "",
                    "rmsd_last_third_A": last if last < 90 else "",
                    **feat,
                    "hydration_followup": hydration,
                    "residence_time_followup": residence,
                    "next_action": next_action,
                }
            )
    rows.sort(key=lambda r: (str(r["residence_time_followup"]) != "residence_time_proxy_candidate", str(r["hydration_followup"]) != "WaterKit_or_GIST_priority"))
    if rows:
        with CSV_OUT.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
    else:
        CSV_OUT.write_text("", encoding="utf-8")
    counts = {
        "hydration_priority": sum(1 for r in rows if r["hydration_followup"] == "WaterKit_or_GIST_priority"),
        "residence_proxy": sum(1 for r in rows if r["residence_time_followup"] == "residence_time_proxy_candidate"),
    }
    lines = [
        "# Hydration and Kinetics Gate",
        "",
        f"- timestamp: `{now}`",
        f"- rows: `{len(rows)}`",
        f"- counts: `{counts}`",
        "- purpose: RMSD 안정성만으로는 부족한 water displacement/residence-time follow-up 우선순위를 정한다.",
        "",
        "## Top Follow-ups",
        "",
        "| target | compound | hydration | residence | ns | RMSD max | next |",
        "|---|---|---|---|---:|---:|---|",
    ]
    for row in rows[:25]:
        lines.append(
            f"| {row['target']} | {row['compound']} | {row['hydration_followup']} | {row['residence_time_followup']} | {row['ns_simulated']} | {row['rmsd_max_A']} | {row['next_action']} |"
        )
    lines.extend(
        [
            "",
            "## Curator Rule",
            "",
            "- hydration priority 후보는 substituent optimization 전에 WaterKit/GIST-lite 계층을 고려한다.",
            "- residence proxy 후보는 60-100 ns 안정성 이후에만 SMD/tauRAMD-style 후속으로 올린다.",
            "- 이 파일은 실제 kinetics claim이 아니라 후속 실험/계산 우선순위다.",
            "",
        ]
    )
    DOC.write_text("\n".join(lines), encoding="utf-8")
    print(f"Saved {CSV_OUT.relative_to(ROOT)}")
    print(f"Saved {DOC.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
