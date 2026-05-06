"""Plan RBFE/ABFE validation for the most defensible chromanol leads.

This generator is intentionally lightweight. It does not launch OpenFE or MD;
it turns current Boltz/PoseBusters/MD evidence into a cost-aware free-energy
follow-up plan.
"""
from __future__ import annotations

import csv
import importlib.util
import json
import shutil
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_meaningful"
DOC = ROOT / "docs/FREE_ENERGY_VALIDATION_PLAN.md"
CSV_OUT = OUT / "free_energy_validation_plan.csv"
ZAFF_DOC = ROOT / "docs/MMP1_ZAFF_ABFE_GATE.md"
ZAFF_CSV = OUT / "mmp1_zaff_abfe_gate.csv"

MMP1_ABFE_DIR = ROOT / "pilot/scaffold_hop/abfe_emb3_mmp1"
MMP1_RECEPTOR = MMP1_ABFE_DIR / "receptor.pdb"
MMP1_EXISTING_RESULTS = [
    MMP1_ABFE_DIR / "openmmtools_full/result.json",
    MMP1_ABFE_DIR / "openmmtools_full_embelin/result.json",
    MMP1_ABFE_DIR / "openmmtools_run/result.json",
]
GENESIS_MD_BIN = Path("/home/crazat/miniforge3/envs/genesis-md/bin")


def csv_rows(path: Path) -> pd.DataFrame:
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


def md_index() -> dict[tuple[str, str], dict[str, object]]:
    idx: dict[tuple[str, str], dict[str, object]] = {}
    for path in [
        ROOT / "pilot/md_r15_chromanol_top3_30ns/summary.json",
        ROOT / "pilot/md_r16_chromanol_topical_priority_30ns/summary.json",
        ROOT / "pilot/md_r16_chromanol_topical_tgfb1_top6_60ns/summary.json",
        ROOT / "pilot/md_r16_chromanol_topical_pigment_representative_60ns/summary.json",
        ROOT / "pilot/md_r16_chromanol_anchor_triad_100ns/summary.json",
    ]:
        for row in json_rows(path):
            target = str(row.get("target", "") or "").lower()
            compound = str(row.get("analog_id") or row.get("compound") or "")
            name = str(row.get("name") or "")
            if compound and target:
                idx[(compound, target)] = row
            if "__r15_chromanol" in name.lower() and target:
                idx[("R15_chromanol", target)] = row
    return idx


def openfe_status() -> str:
    if importlib.util.find_spec("openfe"):
        return "openfe_importable"
    return "openfe_missing_install_or_env"


def read_json(path: Path) -> dict[str, object]:
    if not path.exists() or path.stat().st_size == 0:
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def count_zn_atoms(path: Path) -> int:
    if not path.exists():
        return 0
    count = 0
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        atom_name = line[12:16].strip().upper() if len(line) >= 16 else ""
        element = line[76:78].strip().upper() if len(line) >= 78 else ""
        resname = line[17:20].strip().upper() if len(line) >= 20 else ""
        if line.startswith(("ATOM", "HETATM")) and (atom_name == "ZN" or element == "ZN" or resname == "ZN"):
            count += 1
    return count


def tool_available(name: str) -> bool:
    local = GENESIS_MD_BIN / name
    return local.exists() or shutil.which(name) is not None


def existing_mmp1_abfe_results() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for path in MMP1_EXISTING_RESULTS:
        data = read_json(path)
        if not data:
            continue
        rows.append(
            {
                "path": str(path.relative_to(ROOT)),
                "system": data.get("system", ""),
                "method": data.get("method", ""),
                "delta_g_decoupling_kcal_mol": data.get("delta_g_decoupling_kcal_mol", ""),
                "delta_g_uncertainty_kcal_mol": data.get("delta_g_uncertainty_kcal_mol", ""),
                "accepted_for_zaff_gate": "no",
                "reason": "decoupling-only legacy result; receptor lacks explicit ZN and ZAFF/MCPB metal-center model",
            }
        )
    return rows


def write_mmp1_zaff_gate(now: str) -> dict[str, object]:
    zn_atoms = count_zn_atoms(MMP1_RECEPTOR)
    existing = existing_mmp1_abfe_results()
    current_python_openmmtools = importlib.util.find_spec("openmmtools") is not None
    mcpb_available = tool_available("MCPB.py")
    tleap_available = tool_available("tleap")
    antechamber_available = tool_available("antechamber")
    parmchk2_available = tool_available("parmchk2")
    gate_status = "blocked_zaff_not_integrated"
    if zn_atoms > 0 and current_python_openmmtools:
        gate_status = "ready_for_zaff_parameterization"
    if zn_atoms > 0 and mcpb_available and tleap_available:
        gate_status = "ready_for_zaff_parameterization"

    row = {
        "gate": "MMP1_ZAFF_ABFE_MUST_PASS",
        "status": gate_status,
        "target": "mmp1",
        "required_model": "ZAFF_or_MCPB_bonded_Zn_model",
        "required_value": "restraint_corrected_delta_g_bind_kcal_mol < 0",
        "strict_pass": "upper_uncertainty_bound_below_0_kcal_mol",
        "current_receptor": str(MMP1_RECEPTOR.relative_to(ROOT)),
        "current_receptor_zn_atoms": zn_atoms,
        "legacy_negative_decoupling_results": len(existing),
        "current_python_openmmtools": current_python_openmmtools,
        "genesis_md_mcpb_py": mcpb_available,
        "genesis_md_tleap": tleap_available,
        "genesis_md_antechamber": antechamber_available,
        "genesis_md_parmchk2": parmchk2_available,
        "next_action": "rebuild holo MMP-1 with catalytic Zn, parameterize Zn site with ZAFF/MCPB, then run restraint-corrected ABFE/CBFE replicate",
    }
    with ZAFF_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(row.keys()))
        writer.writeheader()
        writer.writerow(row)

    lines = [
        "# MMP-1 ZAFF ABFE Gate",
        "",
        f"- timestamp: `{now}`",
        "- gate: `MMP1_ZAFF_ABFE_MUST_PASS`",
        f"- status: `{gate_status}`",
        f"- current receptor: `{MMP1_RECEPTOR.relative_to(ROOT)}`",
        f"- explicit Zn atoms in current receptor: `{zn_atoms}`",
        f"- current Python openmmtools importable: `{current_python_openmmtools}`",
        f"- `MCPB.py` available in `genesis-md`: `{mcpb_available}`",
        f"- `tleap` available in `genesis-md`: `{tleap_available}`",
        f"- `antechamber` available in `genesis-md`: `{antechamber_available}`",
        f"- `parmchk2` available in `genesis-md`: `{parmchk2_available}`",
        "",
        "## Verdict",
        "",
        "Current MMP-1 free-energy evidence is not sufficient for a zinc-coordination binding claim.",
        "Legacy EMB-3/Embelin MMP-1 values are negative decoupling estimates, but they are rejected for this gate because the receptor file does not carry an explicit catalytic Zn atom and no ZAFF/MCPB-style metal-center model is recorded.",
        "",
        "## Existing Negative Values Not Accepted For This Gate",
        "",
        "| system | method | delta_g_decoupling_kcal_mol | uncertainty | reason |",
        "|---|---|---:|---:|---|",
    ]
    if existing:
        for item in existing:
            lines.append(
                f"| {item['system']} | {item['method']} | {item['delta_g_decoupling_kcal_mol']} | {item['delta_g_uncertainty_kcal_mol']} | {item['reason']} |"
            )
    else:
        lines.append("| none | none |  |  | no existing ABFE result found |")
    lines.extend(
        [
            "",
            "## Required Pass Criteria",
            "",
            "- Rebuild a holo MMP-1 active-site model retaining catalytic `Zn2+` and coordinating residues.",
            "- Parameterize the Zn center with `ZAFF` or `MCPB.py` bonded/nonbonded parameters and record the generated parameter files.",
            "- Pass a short restrained complex sanity MD with stable Zn coordination geometry before alchemical production.",
            "- Report Zn-ligand distance, Zn-His/Glu coordination distances, and a reference-geometry deviation score from a holo MMP-1 template; do not use a single ideal `109.5 deg` tetrahedral angle as the only pass/fail criterion because metalloprotease active sites can be distorted or ligand-dependent.",
            "- Report restraint-corrected standard-state `DeltaG_bind`, not decoupling-only `DeltaG_decoupling`.",
            "- The computational binding claim is allowed only if `DeltaG_bind < 0 kcal/mol`; strict pass requires the uncertainty upper bound to remain below zero.",
            "- Treat any pre-run ZAFF correction magnitude such as `-8 kcal/mol` as a hypothesis, not evidence. The manuscript may report only measured production outputs.",
            "",
            "## Adjacent Metrics To Track Separately",
            "",
            "- Hydration/skin-permeability terms belong to the topical formulation/PBPK gate, not to the MMP-1 binding gate. They should support R15/R16 topical-delivery ranking, while ZAFF ABFE supports target engagement.",
            "- A useful topical thermodynamic decomposition is `DeltaG_perm = DeltaG_partition + DeltaG_diffusion`; report it as delivery evidence, not as proof of MMP-1 binding.",
            "",
            "## Claim Rule",
            "",
            "Until this gate passes, manuscripts must phrase MMP-1 evidence as Boltz/MD-supported and zinc-model-limited, not as ZAFF-corrected ABFE-confirmed binding.",
            "",
        ]
    )
    ZAFF_DOC.write_text("\n".join(lines), encoding="utf-8")
    return row


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    now = datetime.now(ZoneInfo("Asia/Seoul")).isoformat(timespec="seconds")
    consensus = csv_rows(OUT / "structure_consensus_calibration.csv")
    rbfe_edges = csv_rows(OUT / "rbfe_r16_edge_plan.csv")
    md = md_index()
    zaff_gate = write_mmp1_zaff_gate(now)
    rows: list[dict[str, object]] = []

    if not consensus.empty:
        for _, row in consensus.iterrows():
            job_id = str(row.get("job_id", ""))
            target = str(row.get("target", "")).lower()
            compound = str(row.get("compound", ""))
            cls = str(row.get("consensus_class", ""))
            score = float(row.get("consensus_score", 0) or 0)
            pose = str(row.get("pose_gate", "missing"))
            md_row = md.get((compound, target), {})
            ns = float(md_row.get("ns_simulated", 0) or 0)
            stable = str(row.get("md_state", "missing")) in {"stable", "strong_stable"}
            if cls == "high_confidence" and stable:
                method = "RBFE_network" if compound.startswith("R15_chromanol_") else "ABFE_scout"
                priority = score + (0.08 if ns >= 60 else 0.02) + (0.04 if pose == "pass" else 0.0)
                next_action = "prepare OpenFE edge map; run short solvent/complex sanity first"
            elif cls == "usable_with_caveat" and stable:
                method = "ABFE_or_CBFE_scout"
                priority = score + (0.02 if ns >= 30 else 0.0)
                next_action = "fix pose caveat or run replicate MD before production FE"
            else:
                method = "defer"
                priority = score * 0.5
                next_action = "do not spend FE budget until pose/MD/target caveat improves"
            rows.append(
                {
                    "job_id": job_id,
                    "target": target,
                    "compound": compound,
                    "consensus_class": cls,
                    "pose_gate": pose,
                    "md_state": row.get("md_state", ""),
                    "ns_simulated": ns,
                    "recommended_fe_method": method,
                    "priority_score": round(priority, 4),
                    "openfe_status": openfe_status(),
                    "next_action": next_action,
                }
            )

    rows.sort(key=lambda r: float(r["priority_score"]), reverse=True)
    if rows:
        with CSV_OUT.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
    else:
        CSV_OUT.write_text("", encoding="utf-8")

    edge_count = len(rbfe_edges) if not rbfe_edges.empty else 0
    method_counts = {m: sum(1 for r in rows if r["recommended_fe_method"] == m) for m in ["RBFE_network", "ABFE_scout", "ABFE_or_CBFE_scout", "defer"]}
    lines = [
        "# Free-energy Validation Plan",
        "",
        f"- timestamp: `{now}`",
        f"- rows: `{len(rows)}`",
        f"- existing_rbfe_edge_rows: `{edge_count}`",
        f"- method_counts: `{method_counts}`",
        f"- OpenFE status: `{openfe_status()}`",
        "- purpose: Boltz/MD 후보를 논문용 claim 전에 RBFE/ABFE/CBFE follow-up으로 올릴지 결정한다.",
        "",
        "## Priority FE Follow-ups",
        "",
        "| rank | target | compound | method | priority | consensus | pose | MD | next |",
        "|---:|---|---|---|---:|---|---|---|---|",
    ]
    for i, row in enumerate(rows[:25], 1):
        lines.append(
            f"| {i} | {row['target']} | {row['compound']} | {row['recommended_fe_method']} | {row['priority_score']} | {row['consensus_class']} | {row['pose_gate']} | {row['md_state']} | {row['next_action']} |"
        )
    lines.extend(
        [
            "",
            "## Hard Blocker: MMP-1 Zinc/ZAFF ABFE",
            "",
            f"- gate: `{zaff_gate['gate']}`",
            f"- status: `{zaff_gate['status']}`",
            f"- current receptor Zn atoms: `{zaff_gate['current_receptor_zn_atoms']}`",
            f"- required value: `{zaff_gate['required_value']}`",
            f"- strict pass: `{zaff_gate['strict_pass']}`",
            f"- details: `{ZAFF_DOC.relative_to(ROOT)}`",
            "- Until this gate passes, MMP-1 claims remain zinc-model-limited and cannot be described as ZAFF-corrected ABFE-confirmed binding.",
            "",
            "## Curator Rule",
            "",
            "- MMP-1 zinc/ZAFF ABFE is a hard blocker for any statement stronger than Boltz/MD-supported MMP-1 engagement.",
            "- GPU가 바쁠 때는 이 plan을 생성만 하고 FE production은 큐잉하지 않는다.",
            "- `RBFE_network`는 같은 target의 R16 chloro/dimethyl analog series에 우선 적용한다.",
            "- `ABFE_or_CBFE_scout`는 paper claim 보강용 소규모 validation으로만 사용한다.",
            "- `openfe_missing_install_or_env`이면 설치/환경 점검 문서화만 하고 heavy FE를 실행하지 않는다.",
            "",
        ]
    )
    DOC.write_text("\n".join(lines), encoding="utf-8")
    print(f"Saved {CSV_OUT.relative_to(ROOT)}")
    print(f"Saved {ZAFF_CSV.relative_to(ROOT)}")
    print(f"Saved {ZAFF_DOC.relative_to(ROOT)}")
    print(f"Saved {DOC.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
