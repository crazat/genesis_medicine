"""Write RBFE/OpenFE readiness and R16 congeneric edge plan.

This does not run RBFE. It records whether the current environments can run an
OpenFE-style workflow and lists the most natural R16 chromanol perturbation
edges for later setup.
"""
from __future__ import annotations

import importlib.util
import subprocess
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/RBFE_UPGRADE_READINESS.md"
CPU_OUT = ROOT / "pilot/cpu_meaningful/rbfe_r16_edge_plan.csv"
R16_COFOLD = ROOT / "pilot/cpu_meaningful/r16_chromanol_topical_cofold.csv"


def module_available(module: str, python: str | None = None) -> bool:
    if python is None:
        return importlib.util.find_spec(module) is not None
    code = f"import importlib.util; raise SystemExit(0 if importlib.util.find_spec('{module}') else 1)"
    proc = subprocess.run([python, "-c", code], capture_output=True, text=True, check=False)
    return proc.returncode == 0


def build_edges() -> pd.DataFrame:
    if not R16_COFOLD.exists():
        return pd.DataFrame()
    df = pd.read_csv(R16_COFOLD)
    keep = df[
        [
            "job_id",
            "analog_id",
            "target",
            "smiles",
            "logP",
            "QED",
            "gap_eV",
            "affinity_probability_binary",
        ]
    ].copy()
    keep = keep.sort_values(["target", "affinity_probability_binary"], ascending=[True, False])

    rows: list[dict[str, object]] = []
    for target, sub in keep.groupby("target"):
        top = sub.head(6).reset_index(drop=True)
        if len(top) < 2:
            continue
        anchor = top.iloc[0]
        for idx in range(1, len(top)):
            other = top.iloc[idx]
            rows.append(
                {
                    "target": target,
                    "ligand_a": anchor["analog_id"],
                    "ligand_b": other["analog_id"],
                    "job_a": anchor["job_id"],
                    "job_b": other["job_id"],
                    "smiles_a": anchor["smiles"],
                    "smiles_b": other["smiles"],
                    "affinity_a": anchor["affinity_probability_binary"],
                    "affinity_b": other["affinity_probability_binary"],
                    "delta_affinity_prob_b_minus_a": other["affinity_probability_binary"] - anchor["affinity_probability_binary"],
                    "priority": "high" if target == "tgfb1" and idx <= 3 else "medium",
                    "reason": "same small chromanol congeneric series; suitable first RBFE perturbation candidate",
                }
            )
    return pd.DataFrame(rows)


def main() -> int:
    now = datetime.now(ZoneInfo("Asia/Seoul")).isoformat(timespec="seconds")
    py_cpu = str(ROOT / ".venv/bin/python")
    py_md = "/home/crazat/miniforge3/envs/genesis-md/bin/python"
    availability = {
        "current_python_openfe": module_available("openfe"),
        "current_python_openmm": module_available("openmm"),
        "venv_openfe": module_available("openfe", py_cpu),
        "venv_openmm": module_available("openmm", py_cpu),
        "genesis_md_openfe": module_available("openfe", py_md),
        "genesis_md_openmm": module_available("openmm", py_md),
    }
    edges = build_edges()
    CPU_OUT.parent.mkdir(parents=True, exist_ok=True)
    edges.to_csv(CPU_OUT, index=False)

    lines = [
        "# RBFE / OpenFE Upgrade Readiness",
        "",
        f"- timestamp: `{now}`",
        "- purpose: move selected R16 congeneric chromanol series from affinity-classifier + MD stability toward relative binding free-energy ranking.",
        "- status: planning/readiness only; no RBFE production run launched.",
        "",
        "## Environment",
        "",
        "| Environment check | Available |",
        "|---|---:|",
    ]
    for key, value in availability.items():
        lines.append(f"| `{key}` | `{value}` |")

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- `openmm` is available in `.venv` and `genesis-md`, but `openfe` is not currently installed.",
            "- RBFE production should not be queued until OpenFE or an equivalent RBFE stack is installed and a one-edge smoke test passes.",
            "- First RBFE candidates should be R16 TGFB1 chromanol analogs because they are a close congeneric series and already have 60 ns MD follow-up.",
            "",
            "## R16 RBFE Edge Plan",
            "",
            f"- edge rows: `{len(edges)}`",
            f"- csv: `pilot/cpu_meaningful/rbfe_r16_edge_plan.csv`",
            "",
            "| Target | ligand A | ligand B | priority | reason |",
            "|---|---|---|---|---|",
        ]
    )
    for row in edges.head(20).itertuples(index=False):
        lines.append(
            f"| {row.target} | {row.ligand_a} | {row.ligand_b} | {row.priority} | {row.reason} |"
        )

    lines.extend(
        [
            "",
            "## Next Gate Before Running",
            "",
            "1. Install/activate an RBFE-capable environment with `openfe` and `openmm` together.",
            "2. Run one TGFB1 edge smoke test, preferably `R15_chromanol_Cl_pos9` vs `R15_chromanol_Me6_Me9`.",
            "3. Require reproducible setup, mapper sanity, ligand net charge consistency, and stable equilibration before batch RBFE.",
            "4. Keep RBFE claims as ranking support only until wet-lab IC50/SPR exists.",
            "",
        ]
    )
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Saved {OUT.relative_to(ROOT)}")
    print(f"Saved {CPU_OUT.relative_to(ROOT)} ({len(edges)} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
