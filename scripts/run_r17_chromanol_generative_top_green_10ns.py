"""R17 generative chromanol top green-target 10 ns MD screen.

This is a lightweight follow-up after the 128-row R17 Boltz-2 generative
atlas. It prioritizes target-evidence green DCT/TYR pairs and includes one
photosafety-green single-F comparator, while keeping aryl-halogen review
candidates caveated for manuscript use.

Output:
  pilot/md_r17_chromanol_generative_top_green_10ns/summary.json
  pilot/md_r17_chromanol_generative_top_green_10ns/summary.csv
"""
from __future__ import annotations

import glob
import importlib.util
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
CPU_OUT = ROOT / "pilot/cpu_meaningful"
OUT = ROOT / "pilot/md_r17_chromanol_generative_top_green_10ns"
OUT.mkdir(parents=True, exist_ok=True)

TARGETS = {"dct", "tyr"}


def load_runner():
    path = ROOT / "scripts/run_r16_chromanol_topical_top3_md.py"
    spec = importlib.util.spec_from_file_location("r16_md_runner", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.OUT = OUT
    mod.OUT.mkdir(parents=True, exist_ok=True)
    return mod


def existing_ok() -> dict[str, dict[str, object]]:
    path = OUT / "summary.json"
    if not path.exists():
        return {}
    try:
        rows = json.loads(path.read_text())
    except Exception:
        return {}
    return {
        str(row.get("job_id")): row
        for row in rows
        if row.get("status") == "ok" and row.get("job_id")
    }


def prediction_cif(row: pd.Series) -> Path:
    tag = Path(str(row["source_file"])).name
    tag = tag.replace("r17_chromanol_generative_", "").replace("_cofold.csv", "")
    job_id = str(row["job_id"])
    return (
        CPU_OUT
        / f"output_r17_chromanol_generative_{tag}"
        / f"boltz_results_inputs_r17_chromanol_generative_{tag}"
        / "predictions"
        / job_id
        / f"{job_id}_model_0.cif"
    )


def select_rows(df: pd.DataFrame) -> pd.DataFrame:
    green_target = df[df["target"].str.lower().isin(TARGETS)].copy()
    ranked = green_target.sort_values("affinity_probability_binary", ascending=False)

    selected: list[pd.Series] = []
    for target in ["tyr", "dct"]:
        subset = ranked[ranked["target"].str.lower().eq(target)]
        if not subset.empty:
            selected.append(subset.iloc[0])

    safety_green = ranked[
        ranked["photosafety_proxy"].fillna("").eq("none_detected")
        & ~ranked["job_id"].isin([row["job_id"] for row in selected])
    ]
    if not safety_green.empty:
        selected.append(safety_green.iloc[0])

    return pd.DataFrame(selected)


def build_jobs(runner) -> list[dict[str, object]]:
    files = sorted(glob.glob(str(CPU_OUT / "r17_chromanol_generative_batch*_cofold.csv")))
    if not files:
        return []
    df = pd.concat(
        [pd.read_csv(path).assign(source_file=path) for path in files],
        ignore_index=True,
    )
    top = select_rows(df)
    jobs: list[dict[str, object]] = []
    for _, row in top.iterrows():
        job_id = str(row["job_id"])
        design_id = str(row["design_id"])
        target = str(row["target"]).lower()
        cif = prediction_cif(row)
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
    runner = load_runner()
    jobs = build_jobs(runner)
    done = existing_ok()
    results: list[dict[str, object]] = list(done.values())

    print("R17 generative chromanol top green-target 10 ns MD")
    if not jobs:
        print("No R17 cofold jobs found.")
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
    print("\nFinal R17 generative chromanol top green-target 10 ns summary:")
    print(df.to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
