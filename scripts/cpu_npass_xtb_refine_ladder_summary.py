"""Summarize completed NPASS xTB refinement ladder outputs."""
from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_meaningful"
PATTERN = re.compile(
    r"xtb_npass_top(?P<topn>\d+)_hetero(?P<hetero>\d+)_refine_(?P<confs>\d+)conf\.csv$"
)


def load_ladder() -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for path in sorted(OUT.glob("xtb_npass_top*_hetero*_refine_*conf.csv")):
        match = PATTERN.match(path.name)
        if not match or path.stat().st_size == 0:
            continue
        df = pd.read_csv(path)
        df = df[df.get("status", "ok").eq("ok")].copy()
        if df.empty:
            continue
        df["source_file"] = path.name
        df["source_topn"] = int(match.group("topn"))
        df["min_hetero_atoms"] = int(match.group("hetero"))
        df["requested_confs"] = int(match.group("confs"))
        frames.append(df)
    if not frames:
        raise SystemExit("No completed NPASS xTB refinement ladder CSVs found")
    return pd.concat(frames, ignore_index=True)


def main() -> int:
    df = load_ladder()
    latest_mtime = max((OUT / name).stat().st_mtime for name in df["source_file"].unique())
    timestamp_basis = datetime.fromtimestamp(latest_mtime, ZoneInfo("Asia/Seoul")).isoformat(timespec="minutes")
    summary = (
        df.groupby(["source_topn", "min_hetero_atoms", "requested_confs", "source_file"], as_index=False)
        .agg(
            rows=("np_id", "size"),
            median_gap_eV=("gap_eV_mean", "median"),
            max_gap_eV=("gap_eV_mean", "max"),
            median_log_kp=("log_kp_pottsguy", "median"),
            best_np_id=("np_id", lambda s: s.iloc[df.loc[s.index, "gap_eV_mean"].argmax()]),
        )
        .sort_values(["requested_confs", "source_topn", "min_hetero_atoms"])
    )
    summary.to_csv(OUT / "npass_xtb_refine_ladder_summary.csv", index=False)

    df["skin_window_like"] = df["logp"].between(1.0, 4.0) & df["mw"].between(150.0, 500.0)
    df["topical_xtb_priority"] = (
        df["gap_eV_mean"]
        + 0.10 * df["log_kp_pottsguy"]
        - df["mw"].gt(500.0).astype(float) * 0.25
        - (~df["logp"].between(1.0, 4.0)).astype(float) * 0.20
    )
    best = (
        df.sort_values(["requested_confs", "topical_xtb_priority", "gap_eV_mean"], ascending=[False, False, False])
        .drop_duplicates("np_id")
        .sort_values(["topical_xtb_priority", "gap_eV_mean"], ascending=[False, False])
        .head(80)
    )
    keep_cols = [
        "np_id",
        "rank",
        "smiles",
        "source_file",
        "source_topn",
        "min_hetero_atoms",
        "requested_confs",
        "log_kp_pottsguy",
        "logp",
        "mw",
        "skin_window_like",
        "gap_eV_mean",
        "gap_eV_max",
        "HOMO_eV",
        "LUMO_eV",
        "topical_xtb_priority",
    ]
    best[keep_cols].to_csv(OUT / "npass_xtb_refine_best_candidates.csv", index=False)

    top = best[keep_cols].head(12).copy()
    lines = [
        "# NPASS xTB refinement ladder summary",
        "",
        f"- timestamp_basis: completed CSV mtimes through `{timestamp_basis}`",
        f"- ladder_files: `{summary['source_file'].nunique()}`",
        f"- combined_ok_rows: `{len(df)}`",
        f"- unique_np_ids: `{df['np_id'].nunique()}`",
        "- caveat: 이 표는 Potts-Guy logKp proxy, RDKit descriptors, GFN2-xTB conformer summaries만 통합한 in silico triage이다. 생물활성, 피부투과, hERG/AMES/DILI 안전성은 별도 검증 전 claim으로 쓰지 않는다.",
        "",
        "## Best Candidates",
        "",
        "| rank | np_id | source | logKp | logP | MW | gap_mean_eV | skin_window_like |",
        "|---:|---|---|---:|---:|---:|---:|---|",
    ]
    for i, row in enumerate(top.itertuples(index=False), start=1):
        lines.append(
            "| {i} | {np_id} | {source_file} | {logkp:.3f} | {logp:.2f} | {mw:.1f} | {gap:.2f} | {skin} |".format(
                i=i,
                np_id=row.np_id,
                source_file=row.source_file,
                logkp=row.log_kp_pottsguy,
                logp=row.logp,
                mw=row.mw,
                gap=row.gap_eV_mean,
                skin=str(bool(row.skin_window_like)),
            )
        )
    lines.extend(
        [
            "",
            "## Outputs",
            "",
            "- `pilot/cpu_meaningful/npass_xtb_refine_ladder_summary.csv`",
            "- `pilot/cpu_meaningful/npass_xtb_refine_best_candidates.csv`",
        ]
    )
    (OUT / "npass_xtb_refine_ladder_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Saved {OUT / 'npass_xtb_refine_ladder_summary.csv'}")
    print(f"Saved {OUT / 'npass_xtb_refine_best_candidates.csv'}")
    print(f"Saved {OUT / 'npass_xtb_refine_ladder_summary.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
