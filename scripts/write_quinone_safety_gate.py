"""Write an explicit quinone/reactive-scaffold safety gate.

This complements the general metabolite and photosafety gates by pinning
EMB-3, Embelin, and quinone-like generated analogs into every curator tick.
It is intentionally RDKit-only and lightweight.
"""
from __future__ import annotations

import csv
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd
from rdkit import Chem, RDLogger
from rdkit.Chem import Descriptors, FilterCatalog


RDLogger.DisableLog("rdApp.*")

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_meaningful"
CSV_OUT = OUT / "quinone_safety_gate.csv"
SUMMARY_OUT = OUT / "quinone_safety_gate_summary.json"
DOC = ROOT / "docs/QUINONE_SAFETY_GATE.md"

REFERENCE_PANEL = [
    {
        "candidate_id": "EMB-3",
        "source": "explicit_embelin_scaffold_reference",
        "smiles": "CCCCCC1=C(O)C(=O)C(O)=C(C)C1=O",
        "note": "primary EMB-3 topical lead hypothesis",
    },
    {
        "candidate_id": "Embelin_parent",
        "source": "explicit_embelin_scaffold_reference",
        "smiles": "CCCCCCCCCCCC1=C(C(=O)C=C(C1=O)O)O",
        "note": "parent natural product comparator",
    },
    {
        "candidate_id": "Lawsone_control",
        "source": "explicit_quinone_reference",
        "smiles": "O=C1C(O)=CC(=O)c2ccccc12",
        "note": "naphthoquinone AMES/sensitization control",
    },
    {
        "candidate_id": "Shikonin_control",
        "source": "explicit_quinone_reference",
        "smiles": "CC(C)=CC(O)C1C(=O)c2ccccc2C(=O)C1O",
        "note": "naphthoquinone herbal control",
    },
]

CATALOGS = {}
for name, catalog in [
    ("PAINS_A", FilterCatalog.FilterCatalogParams.FilterCatalogs.PAINS_A),
    ("PAINS_B", FilterCatalog.FilterCatalogParams.FilterCatalogs.PAINS_B),
    ("PAINS_C", FilterCatalog.FilterCatalogParams.FilterCatalogs.PAINS_C),
    ("Brenk", FilterCatalog.FilterCatalogParams.FilterCatalogs.BRENK),
    ("NIH", FilterCatalog.FilterCatalogParams.FilterCatalogs.NIH),
    ("ZINC", FilterCatalog.FilterCatalogParams.FilterCatalogs.ZINC),
]:
    params = FilterCatalog.FilterCatalogParams()
    params.AddCatalog(catalog)
    CATALOGS[name] = FilterCatalog.FilterCatalog(params)

ELECTROPHILE_SMARTS = {
    "michael_acceptor": "[C,c]=[C,c]-[C,S](=O)",
    "aldehyde": "[CX3H1](=O)[#6]",
    "epoxide": "C1OC1",
    "acid_halide": "C(=O)[Cl,Br,I,F]",
    "sulfonyl_halide": "S(=O)(=O)[Cl,Br,I,F]",
    "anhydride": "C(=O)OC(=O)",
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


def ring_carbonyl_atoms(mol: Chem.Mol, ring: tuple[int, ...]) -> list[int]:
    ring_set = set(ring)
    hits: list[int] = []
    for idx in ring:
        atom = mol.GetAtomWithIdx(idx)
        if atom.GetAtomicNum() != 6:
            continue
        for bond in atom.GetBonds():
            other = bond.GetOtherAtom(atom)
            if other.GetIdx() in ring_set:
                continue
            if other.GetAtomicNum() == 8 and bond.GetBondType() == Chem.BondType.DOUBLE:
                hits.append(idx)
                break
    return hits


def ring_hydroxy_atoms(mol: Chem.Mol, ring: tuple[int, ...]) -> list[int]:
    ring_set = set(ring)
    hits: list[int] = []
    for idx in ring:
        atom = mol.GetAtomWithIdx(idx)
        if atom.GetAtomicNum() != 6:
            continue
        for bond in atom.GetBonds():
            other = bond.GetOtherAtom(atom)
            if other.GetIdx() in ring_set:
                continue
            if other.GetAtomicNum() == 8 and bond.GetBondType() == Chem.BondType.SINGLE and other.GetTotalNumHs() > 0:
                hits.append(idx)
                break
    return hits


def ring_unsaturation_count(mol: Chem.Mol, ring: tuple[int, ...]) -> int:
    ring_set = set(ring)
    count = 0
    for bond in mol.GetBonds():
        a = bond.GetBeginAtomIdx()
        b = bond.GetEndAtomIdx()
        if a in ring_set and b in ring_set and bond.GetBondType() == Chem.BondType.DOUBLE:
            count += 1
    return count


def has_adjacent_hydroxy_carbonyl(mol: Chem.Mol, ring: tuple[int, ...]) -> bool:
    carbonyls = set(ring_carbonyl_atoms(mol, ring))
    hydroxys = set(ring_hydroxy_atoms(mol, ring))
    for c_idx in carbonyls:
        for h_idx in hydroxys:
            if mol.GetBondBetweenAtoms(c_idx, h_idx) is not None:
                return True
    return False


def quinone_features(mol: Chem.Mol) -> dict[str, object]:
    best = {
        "quinone_core": False,
        "dihydroxy_quinone_like": False,
        "n_ring_carbonyl": 0,
        "n_ring_hydroxy": 0,
        "n_ring_double": 0,
        "metal_chelation_motif": False,
    }
    for ring in mol.GetRingInfo().AtomRings():
        if len(ring) not in {5, 6}:
            continue
        carbonyls = ring_carbonyl_atoms(mol, ring)
        hydroxys = ring_hydroxy_atoms(mol, ring)
        double_count = ring_unsaturation_count(mol, ring)
        is_quinone = len(carbonyls) >= 2 and double_count >= 1
        is_dihydroxy = is_quinone and len(hydroxys) >= 2
        if len(carbonyls) > int(best["n_ring_carbonyl"]):
            best["n_ring_carbonyl"] = len(carbonyls)
            best["n_ring_hydroxy"] = len(hydroxys)
            best["n_ring_double"] = double_count
        best["quinone_core"] = bool(best["quinone_core"] or is_quinone)
        best["dihydroxy_quinone_like"] = bool(best["dihydroxy_quinone_like"] or is_dihydroxy)
        best["metal_chelation_motif"] = bool(best["metal_chelation_motif"] or has_adjacent_hydroxy_carbonyl(mol, ring))
    return best


def filter_hits(mol: Chem.Mol) -> dict[str, object]:
    out: dict[str, object] = {}
    descriptions: list[str] = []
    for name, catalog in CATALOGS.items():
        matches = catalog.GetMatches(mol)
        out[f"{name}_match"] = bool(matches)
        if matches:
            descriptions.extend(f"{name}:{match.GetDescription()}" for match in matches[:3])
    out["filter_descriptions"] = ";".join(descriptions) if descriptions else "none_detected"
    return out


def electrophile_hits(mol: Chem.Mol) -> list[str]:
    hits = []
    for name, smarts in ELECTROPHILE_SMARTS.items():
        patt = Chem.MolFromSmarts(smarts)
        if patt is not None and mol.HasSubstructMatch(patt):
            hits.append(name)
    return hits


def collect_from_smiles_csv(path: Path, source: str) -> list[dict[str, str]]:
    df = read_csv(path)
    if df.empty or "smiles" not in df.columns:
        return []
    id_col = next((col for col in ["candidate_id", "design_id", "compound", "analog_id", "name"] if col in df.columns), None)
    target_col = "target" if "target" in df.columns else None
    rows = []
    for i, row in df.iterrows():
        candidate_id = str(row[id_col]) if id_col else f"{source}_{i + 1}"
        target = str(row[target_col]) if target_col else ""
        smi = canonical(str(row["smiles"]))
        if smi:
            rows.append({"candidate_id": candidate_id, "target": target, "source": source, "smiles": smi, "note": ""})
    return rows


def collect_candidates() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    rows.extend({**row, "target": "", "smiles": canonical(row["smiles"])} for row in REFERENCE_PANEL)
    for path, source in [
        (OUT / "pains_full_audit.csv", "pains_full_audit"),
        (OUT / "metabolite_reactive_risk_gate.csv", "metabolite_reactive_gate"),
        (OUT / "photosafety_sensitization_v2.csv", "photosafety_gate"),
        (OUT / "dermal_regulatory_safety_gate.csv", "dermal_regulatory_gate"),
        (OUT / "route_enumeration_gate.csv", "route_gate"),
        (OUT / "chromanol_generative_optimizer.csv", "chromanol_generator"),
        (OUT / "structure_consensus_v2.csv", "structure_consensus_v2"),
    ]:
        rows.extend(collect_from_smiles_csv(path, source))

    merged: dict[str, dict[str, str]] = {}
    sources: defaultdict[str, set[str]] = defaultdict(set)
    ids: defaultdict[str, set[str]] = defaultdict(set)
    targets: defaultdict[str, set[str]] = defaultdict(set)
    notes: defaultdict[str, set[str]] = defaultdict(set)
    for row in rows:
        smi = canonical(row.get("smiles", ""))
        if not smi:
            continue
        mol = Chem.MolFromSmiles(smi)
        if mol is None:
            continue
        qfeat = quinone_features(mol)
        fdesc = filter_hits(mol).get("filter_descriptions", "")
        is_reference = row.get("source", "").startswith("explicit_")
        is_filter_quinone = "quinone" in str(fdesc).lower() or bool(qfeat["dihydroxy_quinone_like"])
        if not (is_reference or qfeat["quinone_core"] or is_filter_quinone):
            continue
        merged.setdefault(smi, {"smiles": smi})
        sources[smi].add(row.get("source", "unknown"))
        ids[smi].add(row.get("candidate_id", "unknown"))
        target = row.get("target", "")
        if target and target.lower() != "nan":
            targets[smi].add(target)
        note = row.get("note", "")
        if note:
            notes[smi].add(note)
    out = []
    for smi, base in merged.items():
        out.append(
            {
                **base,
                "candidate_id": ";".join(sorted(ids[smi]))[:240],
                "target": ";".join(sorted(targets[smi]))[:160],
                "source": ";".join(sorted(sources[smi]))[:240],
                "note": ";".join(sorted(notes[smi]))[:240],
            }
        )
    return out


def classify(row: dict[str, str]) -> dict[str, object]:
    mol = Chem.MolFromSmiles(row["smiles"])
    if mol is None:
        return {"quinone_safety_gate": "structure_fix", "alerts": "invalid_smiles", "next_action": "fix structure"}
    qfeat = quinone_features(mol)
    filters = filter_hits(mol)
    filter_text = str(filters["filter_descriptions"]).lower()
    electrophiles = electrophile_hits(mol)
    alerts: list[str] = []
    if qfeat["quinone_core"]:
        alerts.append("quinone_core")
    if qfeat["dihydroxy_quinone_like"]:
        alerts.append("dihydroxy_quinone_like")
    if qfeat["metal_chelation_motif"]:
        alerts.append("hydroxy_carbonyl_metal_chelation_motif")
    alerts.extend(electrophiles)
    if str(filters["filter_descriptions"]) != "none_detected":
        alerts.extend(str(filters["filter_descriptions"]).split(";")[:4])

    if any(hit in electrophiles for hit in ["acid_halide", "sulfonyl_halide", "anhydride"]):
        gate = "redesign_before_use"
    elif qfeat["quinone_core"] or "quinone_a" in filter_text or "chinone" in filter_text or electrophiles:
        gate = "quinone_reactivity_review"
    elif "hydroquinone" in filter_text or "catechol" in filter_text:
        gate = "redox_polyphenol_review"
    elif filters.get("PAINS_A_match") or filters.get("Brenk_match"):
        gate = "reactivity_review"
    else:
        gate = "quinone_reference_review"

    assay = "GSH/NAC trapping LC-MS; DPRA/KeratinoSens/h-CLAT; ROS/redox cycling; ICH S10 photostability; skin S9/metabolite screen"
    claim = "No safety-positive claim before quinone reactivity and sensitization assays; use pulse/formulation-controlled topical framing only."
    return {
        "MW": round(Descriptors.MolWt(mol), 3),
        "cLogP": round(Descriptors.MolLogP(mol), 3),
        **qfeat,
        **filters,
        "electrophile_alerts": ";".join(electrophiles) if electrophiles else "none_detected",
        "alerts": ";".join(dict.fromkeys(alerts)) if alerts else "none_detected",
        "quinone_safety_gate": gate,
        "assay_package": assay,
        "claim_rule": claim,
        "next_action": "prioritize wet-lab reactivity/sensitization package before stronger EMB-3 or quinone lead claims",
    }


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    now = datetime.now(ZoneInfo("Asia/Seoul")).isoformat(timespec="seconds")
    rows = [{**row, **classify(row)} for row in collect_candidates()]
    gate_order = {
        "redesign_before_use": 0,
        "quinone_reactivity_review": 1,
        "redox_polyphenol_review": 2,
        "reactivity_review": 3,
        "quinone_reference_review": 4,
        "structure_fix": 5,
    }
    rows.sort(key=lambda r: (gate_order.get(str(r["quinone_safety_gate"]), 9), 0 if "EMB-3" in str(r["candidate_id"]) else 1, str(r["candidate_id"])))

    if rows:
        with CSV_OUT.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
    else:
        CSV_OUT.write_text("", encoding="utf-8")

    counts = {gate: sum(1 for row in rows if row["quinone_safety_gate"] == gate) for gate in gate_order}
    summary = {
        "timestamp": now,
        "rows": len(rows),
        "gate_counts": counts,
        "emb3_present": any("EMB-3" in str(row["candidate_id"]) for row in rows),
        "primary_blocker": "quinone reactivity and sensitization wet-lab package is required before safety-positive EMB-3 claims",
    }
    SUMMARY_OUT.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "# Quinone Safety Gate",
        "",
        f"- timestamp: `{now}`",
        f"- rows: `{len(rows)}`",
        f"- gate_counts: `{counts}`",
        f"- EMB-3 included: `{summary['emb3_present']}`",
        "- purpose: EMB-3/Embelin/quinone-like analogs를 일반 ADMET 점수와 분리해 redox cycling, Michael acceptor, metal chelation, skin sensitization, photosafety 리스크로 상시 제한한다.",
        "",
        "## Gate Rule",
        "",
        "- `quinone_reactivity_review`: GSH/NAC trapping, DPRA/KeratinoSens/h-CLAT, ROS/redox cycling, ICH S10 photostability, skin S9/metabolite screen 전까지 safety-positive 표현을 금지한다.",
        "- `redox_polyphenol_review`: catechol/hydroquinone류 redox/skin-metabolism caveat로, quinone core는 아니지만 같은 wet-lab 패키지의 보조 우선순위로 둔다.",
        "- `reactivity_review`: PAINS/Brenk reactive alert가 있어 lead claim 전에 원인별 보강을 요구한다.",
        "- `redesign_before_use`: hard electrophile 또는 과도한 reactive alert가 있어 lead claim보다 구조 수정/대조군으로 둔다.",
        "- EMB-3는 hERG/logP가 개선되어도 quinone/sensitization risk가 사라진 것이 아니므로 topical formulation/pulse-use 가설로만 쓴다.",
        "",
        "## Top Quinone Safety Rows",
        "",
        "| candidate | source | gate | cLogP | alerts | required package |",
        "|---|---|---|---:|---|---|",
    ]
    for row in rows[:40]:
        lines.append(
            f"| {row['candidate_id']} | {row['source']} | {row['quinone_safety_gate']} | {row.get('cLogP', '')} | {row['alerts']} | {row['assay_package']} |"
        )
    lines.extend(
        [
            "",
            "## Manuscript Claim Discipline",
            "",
            "- EMB-3/quinone 계열은 `topical-friendly ADMET window`와 `quinone reactivity risk`를 동시에 표기한다.",
            "- `컴퓨터상 safety가 깨끗하다` 또는 `완전 안전하다`는 표현은 금지한다.",
            "- 적합한 표현: `in-silico topical property improved, but quinone reactivity/sensitization remains a required wet-lab gate`.",
            "",
        ]
    )
    DOC.write_text("\n".join(lines), encoding="utf-8")
    print(f"Saved {CSV_OUT.relative_to(ROOT)}")
    print(f"Saved {SUMMARY_OUT.relative_to(ROOT)}")
    print(f"Saved {DOC.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
