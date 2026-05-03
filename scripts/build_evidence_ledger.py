#!/usr/bin/env python3
"""Build pilot/evidence_ledger.csv joining all axes per (compound, target).

Inputs (graceful — missing files are skipped):
  - pilot/cpu_meaningful/active_learning_next_cofold_batch*.csv  → Boltz-2 cofold
  - pilot/cpu_meaningful/r15_chromanol_cofold_14targets.csv      → Boltz-2 R15
  - pilot/cpu_meaningful/r16_chromanol_topical_cofold.csv        → Boltz-2 R16
  - pilot/cpu_meaningful/r17_chromanol_generative_batch*_cofold.csv → Boltz-2 R17
  - pilot/cpu_meaningful/r15_admet_only.csv                      → ADMET (compound-only)
  - pilot/cpu_meaningful/r15_xtb_only.csv                        → xTB gap
  - pilot/cpu_meaningful/r15_master_triage.csv                   → joined R15 master
  - pilot/md_*/summary.json                                      → MD RMSD per (compound, target)
  - pilot/abfe_*/summary.json or status                          → ABFE status
  - pilot/scientific_gates.yaml                                  → gate flags
  - pilot/scientific_negatives.csv                               → negative ledger
  - pilot/codex_curator_directives.yaml or claude_curator_directives.yaml
                                                                   → pin/retire/gate

Outputs:
  - pilot/evidence_ledger.csv     (wide, one row per (compound_key, target))
  - pilot/evidence_ledger_meta.json (column legend + source manifest)

Key design rules:
  - Compound key = RDKit canonical SMILES if RDKit is importable, else raw SMILES.
  - Target key = upper-cased UniProt-style symbol (TGFB1, MMP1, ...).
  - Joins are LEFT-OUTER on (compound_key, target). Compound-only axes
    (ADMET, xTB) propagate to every (this compound, target) pair via a
    left-outer join after target axis is established.
  - Gate columns are calculated last and never block ledger creation.

This script is deliberately read-only to existing files. It only writes
pilot/evidence_ledger.csv + pilot/evidence_ledger_meta.json.

Run:
  /home/crazat/genesis_medicine/.venv/bin/python scripts/build_evidence_ledger.py
"""
from __future__ import annotations

import csv
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
PILOT = ROOT / "pilot"
CPU_OUT = PILOT / "cpu_meaningful"
LEDGER_PATH = PILOT / "evidence_ledger.csv"
META_PATH = PILOT / "evidence_ledger_meta.json"
GATES_PATH = PILOT / "scientific_gates.yaml"
NEGATIVES_PATH = PILOT / "scientific_negatives.csv"
DIRECTIVES_PATHS = [
    PILOT / "claude_curator_directives.yaml",
    PILOT / "codex_curator_directives.yaml",
    PILOT / "curator_directives_canonical.yaml",
]

try:
    from rdkit import Chem, RDLogger  # type: ignore
    RDLogger.DisableLog("rdApp.error")
    RDLogger.DisableLog("rdApp.warning")

    def canon_smiles(s: str) -> str:
        if not s:
            return ""
        # Skip obvious non-SMILES aliases (no parens / brackets / valid atoms).
        if re.match(r"^[A-Z][A-Z0-9_-]*$", s) and not re.search(r"[\[\]\(\)=#@/\\]", s):
            return s
        try:
            mol = Chem.MolFromSmiles(s)
            if mol is None:
                return s
            return Chem.MolToSmiles(mol, canonical=True)
        except Exception:
            return s
except Exception:
    def canon_smiles(s: str) -> str:
        return s or ""


def upper_target(t: str) -> str:
    if not t:
        return ""
    return re.sub(r"[^A-Z0-9]", "", t.upper())


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists() or path.stat().st_size == 0:
        return []
    try:
        with path.open(newline="") as fh:
            return list(csv.DictReader(fh))
    except Exception:
        return []


def read_yaml_simple(path: Path) -> dict[str, Any]:
    """Minimal YAML reader (avoid PyYAML dep). Supports our flat schema."""
    if not path.exists():
        return {}
    try:
        import yaml  # type: ignore

        with path.open() as fh:
            data = yaml.safe_load(fh)
            return data if isinstance(data, dict) else {}
    except Exception:
        # very narrow fallback: only top-level scalar keys
        out: dict[str, Any] = {}
        try:
            for line in path.read_text().splitlines():
                m = re.match(r"^([A-Za-z_][A-Za-z0-9_]*):\s*(.*)$", line)
                if m and m.group(2):
                    out[m.group(1)] = m.group(2).strip().strip('"').strip("'")
            return out
        except Exception:
            return {}


def collect_boltz2(rows_acc: dict[tuple[str, str], dict[str, Any]]) -> int:
    """Boltz-2 cofold + active learning aggregations."""
    sources = []
    sources.extend(sorted(CPU_OUT.glob("active_learning_next_cofold_batch[0-9]*.csv")))
    sources.extend([
        CPU_OUT / "r15_chromanol_cofold_14targets.csv",
        CPU_OUT / "r16_chromanol_topical_cofold.csv",
    ])
    sources.extend(sorted(CPU_OUT.glob("r17_chromanol_generative_batch*_cofold.csv")))

    n = 0
    for path in sources:
        for row in read_csv(path):
            sm = row.get("smiles") or row.get("SMILES") or row.get("canonical_smiles")
            tg = row.get("target") or row.get("target_symbol")
            if not sm or not tg:
                continue
            ck = canon_smiles(sm)
            tk = upper_target(tg)
            if not ck or not tk:
                continue
            entry = rows_acc.setdefault(
                (ck, tk),
                {"compound_key": ck, "target": tk, "raw_smiles": sm},
            )
            for col_in, col_out in (
                ("affinity_probability_binary", "boltz2_aff_prob_bin"),
                ("affinity_pred_value", "boltz2_aff_value"),
                ("affinity_probability", "boltz2_aff_prob"),
                ("complex_plddt", "boltz2_complex_plddt"),
                ("ptm", "boltz2_ptm"),
                ("iptm", "boltz2_iptm"),
                ("ligand_iptm", "boltz2_ligand_iptm"),
                ("predicted_score", "active_pred_score"),
                ("uncertainty", "active_uncertainty"),
                ("acquisition_score", "active_acquisition"),
                ("synthesis_gate", "synthesis_gate"),
                ("synthesis_score", "synthesis_score"),
            ):
                if row.get(col_in) and not entry.get(col_out):
                    entry[col_out] = row[col_in]
            entry.setdefault("boltz2_source_files", set()).add(path.name)
            n += 1
    return n


def collect_admet(rows_acc: dict[tuple[str, str], dict[str, Any]]) -> int:
    """ADMET/xTB master triage — compound-only axes propagated to every target."""
    n = 0
    candidates = [
        CPU_OUT / "r15_master_triage.csv",
        CPU_OUT / "r15_admet_only.csv",
        CPU_OUT / "r15_xtb_only.csv",
    ]
    compound_axes: dict[str, dict[str, Any]] = {}
    for path in candidates:
        for row in read_csv(path):
            sm = row.get("derivative_smiles") or row.get("smiles") or row.get("SMILES")
            if not sm:
                continue
            ck = canon_smiles(sm)
            if not ck:
                continue
            slot = compound_axes.setdefault(ck, {})
            for col_in, col_out in (
                ("MW", "mw"),
                ("logP", "logp"),
                ("HBD", "hbd"),
                ("HBA", "hba"),
                ("TPSA", "tpsa"),
                ("rotb", "rotb"),
                ("QED", "qed"),
                ("skin_window", "skin_window"),
                ("lipinski_viol", "lipinski_viol"),
                ("AMES", "admet_ames"),
                ("hERG", "admet_herg"),
                ("DILI", "admet_dili"),
                ("BBB_Martins", "admet_bbb"),
                ("HIA_Hou", "admet_hia"),
                ("Lipophilicity_AstraZeneca", "admet_lipo"),
                ("Solubility_AqSolDB", "admet_sol"),
                ("ClinTox", "admet_clintox"),
                ("Carcinogens_Lagunin", "admet_carc"),
                ("Skin_Reaction", "admet_skin_reaction"),
                ("CYP3A4_Veith", "admet_cyp3a4"),
                ("CYP2C9_Veith", "admet_cyp2c9"),
                ("CYP2D6_Veith", "admet_cyp2d6"),
                ("HOMO_eV", "xtb_homo_eV"),
                ("LUMO_eV", "xtb_lumo_eV"),
                ("gap_eV", "xtb_gap_eV"),
                ("energy_au", "xtb_energy_au"),
                ("score", "master_triage_score"),
                ("leader_seed", "leader_seed"),
            ):
                if row.get(col_in) and not slot.get(col_out):
                    slot[col_out] = row[col_in]
    if not compound_axes:
        return 0
    # Fan-out compound axes onto all (compound, target) entries in the ledger.
    for (ck, _tk), entry in rows_acc.items():
        slot = compound_axes.get(ck)
        if not slot:
            continue
        for k, v in slot.items():
            entry.setdefault(k, v)
        n += 1
    # Compound rows that have no target attached yet → emit with target=ANY
    # so the ledger captures them for later target-axis joins.
    for ck, slot in compound_axes.items():
        if any(k_ck == ck for (k_ck, _t) in rows_acc.keys()):
            continue
        rows_acc[(ck, "ANY")] = {
            "compound_key": ck,
            "target": "ANY",
            **slot,
        }
        n += 1
    return n


def collect_md_rmsd(rows_acc: dict[tuple[str, str], dict[str, Any]]) -> int:
    """Walk pilot/md_*/summary.json and write rmsd_mean / last_third / stable flag."""
    n = 0
    for summary in PILOT.glob("md_*/summary.json"):
        try:
            data = json.loads(summary.read_text())
        except Exception:
            continue
        rows = data if isinstance(data, list) else data.get("rows") if isinstance(data, dict) else None
        if not isinstance(rows, list):
            continue
        for row in rows:
            sm = row.get("smiles") or row.get("ligand_smiles") or row.get("ligand")
            tg = row.get("target") or row.get("target_symbol")
            if not sm or not tg:
                continue
            ck = canon_smiles(sm)
            tk = upper_target(tg)
            if not ck or not tk:
                continue
            entry = rows_acc.setdefault(
                (ck, tk),
                {"compound_key": ck, "target": tk, "raw_smiles": sm},
            )
            for col_in, col_out in (
                ("rmsd_mean_A", "md_rmsd_mean_A"),
                ("rmsd_last_third_A", "md_rmsd_last_third_A"),
                ("rmsd_max_A", "md_rmsd_max_A"),
                ("ns", "md_total_ns"),
                ("status", "md_status"),
            ):
                val = row.get(col_in)
                if val in (None, ""):
                    continue
                col_full = f"{summary.parent.name}__{col_out}"
                entry[col_full] = val
                # Also keep canonical "best ns / lowest mean" rollup.
                try:
                    candidate = float(val) if col_in.endswith("_A") else None
                except Exception:
                    candidate = None
                if col_in == "rmsd_mean_A" and candidate is not None:
                    cur = entry.get("md_rmsd_mean_A_best")
                    if cur in (None, "") or float(cur) > candidate:
                        entry["md_rmsd_mean_A_best"] = candidate
                        entry["md_rmsd_mean_A_best_run"] = summary.parent.name
            n += 1
    return n


def collect_abfe_status(rows_acc: dict[tuple[str, str], dict[str, Any]]) -> int:
    n = 0
    for summary in PILOT.glob("abfe_*/summary.json"):
        try:
            data = json.loads(summary.read_text())
        except Exception:
            continue
        rows = data if isinstance(data, list) else data.get("rows") if isinstance(data, dict) else []
        if not isinstance(rows, list):
            continue
        for row in rows:
            sm = row.get("smiles") or row.get("ligand")
            tg = row.get("target") or row.get("target_symbol")
            if not sm or not tg:
                continue
            ck = canon_smiles(sm)
            tk = upper_target(tg)
            if not ck or not tk:
                continue
            entry = rows_acc.setdefault(
                (ck, tk),
                {"compound_key": ck, "target": tk, "raw_smiles": sm},
            )
            for col_in, col_out in (
                ("dG_kcal_per_mol", "abfe_dG_kcal_per_mol"),
                ("dG_uncertainty", "abfe_dG_uncertainty"),
                ("status", "abfe_status"),
                ("nan_fraction", "abfe_nan_fraction"),
            ):
                val = row.get(col_in)
                if val not in (None, ""):
                    col_full = f"{summary.parent.name}__{col_out}"
                    entry[col_full] = val
            n += 1
    return n


def collect_gates(rows_acc: dict[tuple[str, str], dict[str, Any]]) -> dict[str, Any]:
    gates_doc = read_yaml_simple(GATES_PATH)
    gates = gates_doc.get("gates") or [] if isinstance(gates_doc, dict) else []
    if not isinstance(gates, list):
        gates = []
    # Build per-compound + per-target gate flag bitmasks.
    by_compound: dict[str, list[str]] = {}
    by_target: dict[str, list[str]] = {}
    by_scaffold: dict[str, list[str]] = {}
    for g in gates:
        if not isinstance(g, dict):
            continue
        gid = g.get("id") or "unknown_gate"
        action = g.get("action") or "flag"
        for sm in g.get("compounds") or []:
            ck = canon_smiles(sm)
            by_compound.setdefault(ck, []).append(f"{gid}:{action}")
        for tg in g.get("targets") or []:
            tk = upper_target(tg)
            by_target.setdefault(tk, []).append(f"{gid}:{action}")
        for sc in g.get("scaffolds") or []:
            by_scaffold.setdefault(str(sc), []).append(f"{gid}:{action}")

    # Apply to ledger rows.
    for (ck, tk), entry in rows_acc.items():
        flags: list[str] = []
        flags.extend(by_compound.get(ck, []))
        flags.extend(by_target.get(tk, []))
        leader = entry.get("leader_seed")
        if leader and leader in by_scaffold:
            flags.extend(by_scaffold[leader])
        if flags:
            entry["gate_flags"] = ";".join(sorted(set(flags)))
            actions = sorted({f.split(":", 1)[1] for f in flags if ":" in f})
            entry["gate_action_aggregate"] = ";".join(actions)

    # Negatives ledger -> per-compound / per-target row count.
    neg_rows = read_csv(NEGATIVES_PATH)
    neg_by_compound: dict[str, int] = {}
    neg_by_target: dict[str, int] = {}
    for row in neg_rows:
        if row.get("status", "active") != "active":
            continue
        sid = row.get("subject_id") or ""
        tg = row.get("target") or ""
        if row.get("subject_type") == "compound" and sid:
            neg_by_compound[canon_smiles(sid)] = neg_by_compound.get(canon_smiles(sid), 0) + 1
        if tg and tg != "*":
            neg_by_target[upper_target(tg)] = neg_by_target.get(upper_target(tg), 0) + 1
    for (ck, tk), entry in rows_acc.items():
        nc = neg_by_compound.get(ck, 0)
        nt = neg_by_target.get(tk, 0)
        if nc:
            entry["negative_ledger_compound_hits"] = nc
        if nt:
            entry["negative_ledger_target_hits"] = nt

    return {"gate_count": len(gates), "negative_count": len(neg_rows)}


def collect_directives(rows_acc: dict[tuple[str, str], dict[str, Any]]) -> dict[str, Any]:
    """Apply curator pin/retire/gate directives onto the ledger."""
    for path in DIRECTIVES_PATHS:
        if not path.exists():
            continue
        try:
            doc = read_yaml_simple(path)
        except Exception:
            continue
        directives = doc.get("directives") if isinstance(doc, dict) else None
        if not isinstance(directives, list):
            continue
        for d in directives:
            if not isinstance(d, dict):
                continue
            action = (d.get("action") or "").lower()
            for sm in d.get("compounds") or []:
                ck = canon_smiles(sm)
                for tk in (d.get("targets") or [None]):
                    key = (ck, upper_target(tk) if tk else "ANY")
                    entry = rows_acc.get(key)
                    if entry is None:
                        continue
                    entry.setdefault("curator_directive", []).append(action)
                    if d.get("reason"):
                        entry.setdefault("curator_directive_reason", []).append(str(d["reason"]))
        return {"loaded_from": str(path), "directive_count": len(directives)}
    return {}


def write_ledger(rows: Iterable[dict[str, Any]]) -> dict[str, Any]:
    rows = list(rows)
    if not rows:
        LEDGER_PATH.write_text("")
        return {"row_count": 0}
    # Stable column ordering: keys + axis families in fixed order.
    canon_cols = [
        "compound_key", "target", "raw_smiles",
        "leader_seed",
        "boltz2_aff_prob_bin", "boltz2_aff_value", "boltz2_aff_prob",
        "boltz2_complex_plddt", "boltz2_ptm", "boltz2_iptm", "boltz2_ligand_iptm",
        "active_pred_score", "active_uncertainty", "active_acquisition",
        "synthesis_gate", "synthesis_score",
        "mw", "logp", "hbd", "hba", "tpsa", "rotb", "qed",
        "skin_window", "lipinski_viol",
        "admet_ames", "admet_herg", "admet_dili",
        "admet_bbb", "admet_hia", "admet_lipo", "admet_sol",
        "admet_clintox", "admet_carc", "admet_skin_reaction",
        "admet_cyp3a4", "admet_cyp2c9", "admet_cyp2d6",
        "xtb_homo_eV", "xtb_lumo_eV", "xtb_gap_eV", "xtb_energy_au",
        "master_triage_score",
        "md_rmsd_mean_A_best", "md_rmsd_mean_A_best_run",
        "gate_flags", "gate_action_aggregate",
        "negative_ledger_compound_hits", "negative_ledger_target_hits",
        "boltz2_source_files",
        "curator_directive", "curator_directive_reason",
    ]
    extra_cols = sorted({k for r in rows for k in r.keys()} - set(canon_cols))
    fieldnames = canon_cols + extra_cols
    with LEDGER_PATH.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for r in rows:
            r2 = {k: v for k, v in r.items()}
            if isinstance(r2.get("boltz2_source_files"), set):
                r2["boltz2_source_files"] = ";".join(sorted(r2["boltz2_source_files"]))
            for col in ("curator_directive", "curator_directive_reason"):
                if isinstance(r2.get(col), list):
                    r2[col] = ";".join(map(str, r2[col]))
            writer.writerow(r2)
    return {"row_count": len(rows), "columns": fieldnames}


def main() -> int:
    started = datetime.utcnow().isoformat() + "Z"
    rows: dict[tuple[str, str], dict[str, Any]] = {}
    counts = {
        "boltz2": collect_boltz2(rows),
        "admet_xtb": collect_admet(rows),
        "md_rmsd": collect_md_rmsd(rows),
        "abfe_status": collect_abfe_status(rows),
    }
    counts["gates_meta"] = collect_gates(rows)
    counts["directives_meta"] = collect_directives(rows)
    write_meta = write_ledger(rows.values())
    META_PATH.write_text(
        json.dumps(
            {
                "started": started,
                "finished": datetime.utcnow().isoformat() + "Z",
                "ledger_path": str(LEDGER_PATH.relative_to(ROOT)),
                "row_count": write_meta.get("row_count", 0),
                "columns": write_meta.get("columns", []),
                "axis_counts": counts,
                "inputs": {
                    "gates": str(GATES_PATH.relative_to(ROOT)),
                    "negatives": str(NEGATIVES_PATH.relative_to(ROOT)),
                    "directives": [
                        str(p.relative_to(ROOT)) for p in DIRECTIVES_PATHS if p.exists()
                    ],
                },
            },
            indent=2,
        )
    )
    print(f"evidence_ledger rows={write_meta.get('row_count', 0)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
