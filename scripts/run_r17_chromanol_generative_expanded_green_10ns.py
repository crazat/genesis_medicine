"""R17 expanded green-target 10 ns MD follow-up.

This adds a non-duplicate DCT/TYR safety-green panel after the initial
top/next R17 green-target MD sets. It is intentionally written to a separate
output directory so the original top/next 10/30/60 ns panels remain unchanged.

Output:
  pilot/md_r17_chromanol_generative_expanded_green_10ns/summary.json
  pilot/md_r17_chromanol_generative_expanded_green_10ns/summary.csv
"""
from __future__ import annotations

import glob
import importlib.util
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
CPU_OUT = ROOT / "pilot/cpu_meaningful"
OUT = ROOT / "pilot/md_r17_chromanol_generative_expanded_green_10ns"
OUT.mkdir(parents=True, exist_ok=True)

TARGETS = {"dct", "tyr"}
PRIOR_MD_DIRS = [
    ROOT / "pilot/md_r17_chromanol_generative_top_green_10ns",
    ROOT / "pilot/md_r17_chromanol_generative_top_green_30ns",
    ROOT / "pilot/md_r17_chromanol_generative_top_green_60ns",
    ROOT / "pilot/md_r17_chromanol_generative_next_green_10ns",
    ROOT / "pilot/md_r17_chromanol_generative_next_green_30ns",
    ROOT / "pilot/md_r17_chromanol_generative_next_green_60ns",
    OUT,
]


def load_base():
    path = ROOT / "scripts/run_r17_chromanol_generative_top_green_10ns.py"
    spec = importlib.util.spec_from_file_location("r17_green_10ns", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.OUT = OUT
    mod.OUT.mkdir(parents=True, exist_ok=True)
    return mod


def existing_md_job_ids() -> set[str]:
    ids: set[str] = set()
    for directory in PRIOR_MD_DIRS:
        path = directory / "summary.json"
        if not path.exists():
            continue
        try:
            rows = json.loads(path.read_text())
        except Exception:
            continue
        if not isinstance(rows, list):
            continue
        for row in rows:
            if row.get("status") == "ok" and row.get("job_id"):
                ids.add(str(row["job_id"]))
    return ids


def select_rows(df: pd.DataFrame, already_done: set[str]) -> pd.DataFrame:
    green = df[df["target"].str.lower().isin(TARGETS)].copy()
    green = green[~green["job_id"].astype(str).isin(already_done)]
    if green.empty:
        return green

    green["safety_rank"] = green["photosafety_proxy"].fillna("").ne("none_detected").astype(int)
    ranked = green.sort_values(
        ["safety_rank", "affinity_probability_binary", "local_design_priority"],
        ascending=[True, False, False],
    )

    selected: list[pd.Series] = []
    selected_ids: set[str] = set()
    for target in ["tyr", "dct"]:
        subset = ranked[ranked["target"].str.lower().eq(target)]
        if not subset.empty:
            row = subset.iloc[0]
            selected.append(row)
            selected_ids.add(str(row["job_id"]))

    for _, row in ranked.iterrows():
        if len(selected) >= 3:
            break
        job_id = str(row["job_id"])
        if job_id in selected_ids:
            continue
        selected.append(row)
        selected_ids.add(job_id)

    return pd.DataFrame(selected[:3])


def build_jobs(base) -> list[dict[str, object]]:
    files = sorted(glob.glob(str(CPU_OUT / "r17_chromanol_generative_batch*_cofold.csv")))
    if not files:
        return []
    df = pd.concat(
        [pd.read_csv(path).assign(source_file=path) for path in files],
        ignore_index=True,
    )
    top = select_rows(df, existing_md_job_ids())
    jobs: list[dict[str, object]] = []
    runner = base.load_runner()
    for _, row in top.iterrows():
        job_id = str(row["job_id"])
        design_id = str(row["design_id"])
        target = str(row["target"]).lower()
        cif = base.prediction_cif(row)
        jobs.append(
            {
                "name": f"{job_id}__{runner.clean_name(design_id)}__10ns",
                "job_id": job_id,
                "analog_id": design_id,
                "target": target,
                "cif": str(cif.relative_to(ROOT)),
                "smiles": str(row["smiles"]),
                "topical_followup_score": row.get("topical_window_score"),
                "logP": row.get("cLogP"),
                "QED": row.get("QED"),
                "gap_eV": None,
                "affinity_probability_binary": row.get("affinity_probability_binary"),
                "affinity_pred_value": row.get("affinity_pred_value"),
                "photosafety_proxy": row.get("photosafety_proxy"),
                "local_design_priority": row.get("local_design_priority"),
            }
        )
    return jobs


def main() -> int:
    base = load_base()
    runner = base.load_runner()
    jobs = build_jobs(base)
    done = base.existing_ok()
    results: list[dict[str, object]] = list(done.values())

    print("R17 expanded green-target 10 ns MD")
    if not jobs:
        print("No non-duplicate R17 expanded green-target cofold jobs found.")
        return 0
    print(
        pd.DataFrame(jobs)[
            [
                "job_id",
                "analog_id",
                "target",
                "affinity_probability_binary",
                "photosafety_proxy",
                "cif",
            ]
        ].to_string(index=False)
    )

    for job in jobs:
        if str(job["job_id"]) in done:
            print(f"skip existing ok: {job['job_id']}")
            continue
        try:
            result = runner.run_md(job, ns=10.0)
            result["photosafety_proxy"] = job.get("photosafety_proxy")
            result["local_design_priority"] = job.get("local_design_priority")
        except Exception as exc:
            import traceback

            traceback.print_exc()
            result = {
                "name": job["name"],
                "job_id": job["job_id"],
                "analog_id": job["analog_id"],
                "target": job["target"],
                "status": f"error:{str(exc)[:200]}",
                "photosafety_proxy": job.get("photosafety_proxy"),
            }
        results = [row for row in results if row.get("job_id") != result.get("job_id")]
        results.append(result)
        (OUT / "summary.json").write_text(json.dumps(results, indent=2))

    df = pd.DataFrame(results)
    df.to_csv(OUT / "summary.csv", index=False)
    print("\nFinal R17 expanded green-target 10 ns summary:")
    print(df.to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
