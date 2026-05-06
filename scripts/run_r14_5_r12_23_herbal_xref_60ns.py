"""R14_5 + R12_23 60 ns MD against herbal-cross-reference priority targets.

Drives the molecular-dynamics validation layer for preprint #19 (Korean Pharmacopoeia
herbal scaffold cross-reference). The four (leader, target) pairs are chosen to
align with the strongest ECFP6 Tanimoto concordances reported in
pilot/universal_scaffold_admet/tanimoto_korean_herbal.csv:

  - R14_5 x TGFB1 — ferulic acid concordance (Tanimoto 0.415, 당귀/천궁,
    scar/photoaging axis); TGFB1 is the canonical scar/fibrosis master switch.
  - R14_5 x MMP1  — ferulic acid + curcumin concordance; MMP1 is the photoaging /
    matrix-remodeling axis. Note 30 ns prior run exists; extending to 60 ns
    consolidates the last-third stability window.
  - R12_23 x MMP1 — EGCG concordance (Tanimoto 0.338, 녹차, MMP1/MITF/JAK).
  - R12_23 x TYR  — EGCG concordance (pigmentation axis); TYRP1/DCT prior data
    exists in 10 ns, TYR specifically extended here.

Output:
  pilot/md_r14_5_r12_23_herbal_xref_60ns/summary.json
  pilot/md_r14_5_r12_23_herbal_xref_60ns/summary.csv

Pipeline reuses run_r14_5_full14_md.run_md() as the per-job MD runner; only the
JOBS list and ns target are different.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/md_r14_5_r12_23_herbal_xref_60ns"
OUT.mkdir(parents=True, exist_ok=True)

R14_5_SMI = "COc1cc(C=CC2COc3cc(O)ccc3C2)ccc1O"
R12_23_SMI = "COC(=O)C1Cc2c(O)cc(O)cc2OC1C1COc2cc(O)ccc2C1"

JOBS = [
    {
        "name": "tgfb1__r14_5_60ns",
        "leader": "r14_5",
        "smiles": R14_5_SMI,
        "cif_glob": "pilot/cpu_meaningful/output_r14_tgfb1/boltz_results_inputs_r14_tgfb1/predictions/r14_tgfb1_5/r14_tgfb1_5_model_0.cif",
        "herbal_anchor": "ferulic_acid (Angelica gigas, Cnidium officinale; Tanimoto 0.415, scar/photoaging)",
    },
    {
        "name": "mmp1__r14_5_60ns",
        "leader": "r14_5",
        "smiles": R14_5_SMI,
        "cif_glob": "pilot/cpu_meaningful/output_r14_mmp1/boltz_results_inputs_r14_mmp1/predictions/r14_mmp1_5/r14_mmp1_5_model_0.cif",
        "herbal_anchor": "ferulic_acid (0.415) + curcumin (0.407, Curcuma longa); MMP1 photoaging/scar",
    },
    {
        "name": "mmp1__r12_23_60ns",
        "leader": "r12_23",
        "smiles": R12_23_SMI,
        "cif_glob": "pilot/cpu_meaningful/output_r12_mmp1/boltz_results_inputs_r12_mmp1/predictions/r12_mmp1_23/r12_mmp1_23_model_0.cif",
        "herbal_anchor": "EGCG (Camellia sinensis 녹차; Tanimoto 0.338, MMP1/MITF/JAK)",
    },
    {
        "name": "tyr__r12_23_60ns",
        "leader": "r12_23",
        "smiles": R12_23_SMI,
        "cif_glob": "pilot/cpu_meaningful/output_r12_tyr/boltz_results_inputs_r12_tyr/predictions/r12_tyr_23/r12_tyr_23_model_0.cif",
        "herbal_anchor": "EGCG + glabridin (Glycyrrhiza glabra 감초; Tanimoto 0.280, TYR pigmentation)",
    },
]


def load_md_runner():
    path = ROOT / "scripts/run_r14_5_full14_md.py"
    spec = importlib.util.spec_from_file_location("r14_5_md_runner", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.OUT = OUT
    mod.OUT.mkdir(parents=True, exist_ok=True)
    return mod


def existing_ok() -> dict[str, dict]:
    path = OUT / "summary.json"
    if not path.exists():
        return {}
    try:
        rows = json.loads(path.read_text())
    except Exception:
        return {}
    return {r["name"]: r for r in rows if r.get("status") == "ok"}


def main() -> int:
    print("R14_5 + R12_23 60 ns herbal cross-reference MD (preprint #19 evidence layer)")
    runner = load_md_runner()
    done = existing_ok()
    results: list[dict] = []

    for job in JOBS:
        if job["name"] in done:
            print(f"  [skip] {job['name']} already ok in summary.json")
            results.append(done[job["name"]])
            continue

        cif_path = ROOT / job["cif_glob"]
        if not cif_path.exists():
            print(f"  [missing_cif] {job['name']} expected at {job['cif_glob']}")
            results.append({
                "name": job["name"],
                "status": "missing_cif",
                "cif": str(job["cif_glob"]),
                "leader": job["leader"],
                "herbal_anchor": job["herbal_anchor"],
            })
            with (OUT / "summary.json").open("w") as f:
                json.dump(results, f, indent=2)
            continue

        print(f"\n=== {job['name']} ({job['herbal_anchor']}) ===")
        r = runner.run_md(job["name"], job["cif_glob"], job["smiles"], ns=60.0)
        r["leader"] = job["leader"]
        r["herbal_anchor"] = job["herbal_anchor"]
        results.append(r)

        with (OUT / "summary.json").open("w") as f:
            json.dump(results, f, indent=2)

    df = pd.DataFrame(results)
    df.to_csv(OUT / "summary.csv", index=False)

    if "rmsd_mean_A" in df.columns:
        cols = ["name", "status", "rmsd_mean_A", "rmsd_max_A", "wall_min"]
        cols = [c for c in cols if c in df.columns]
        print("\n" + df[cols].to_string(index=False))

    print(f"\nDone. Output dir: {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
