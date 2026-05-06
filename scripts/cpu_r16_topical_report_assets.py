"""Build R16 topical chromanol report assets from completed summaries."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_meaningful"
FIG_OUT = ROOT / "preprints/15_universal_scaffold/figures"

MATRIX_CSV = OUT / "r16_topical_chromanol_30ns_matrix_summary.csv"
SUMMARY_60NS = ROOT / "pilot/md_r16_chromanol_topical_tgfb1_top6_60ns/summary.json"

FIG_MATRIX = FIG_OUT / "fig9_r16_topical_chromanol_30ns_matrix.png"
FIG_60NS = FIG_OUT / "fig10_r16_tgfb1_60ns_progress.png"
MD_OUT = OUT / "r16_tgfb1_60ns_partial_summary.md"


def stable_30ns(row: pd.Series) -> bool:
    return (
        str(row.get("stable_30ns", "")).lower() == "true"
        or (float(row.get("rmsd_max_A", 99.0)) <= 2.0 and float(row.get("rmsd_last_third_A", 99.0)) <= 1.5)
    )


def build_matrix_figure() -> None:
    df = pd.read_csv(MATRIX_CSV)
    df["label"] = df["analog_id"].str.replace("R15_chromanol_", "", regex=False)
    pivot = df.pivot_table(index="label", columns="target", values="rmsd_last_third_A", aggfunc="mean")
    pivot = pivot.reindex(sorted(pivot.index), axis=0)
    pivot = pivot.reindex(["tgfb1", "tyr", "dct"], axis=1)

    fig, ax = plt.subplots(figsize=(8.2, 4.8))
    im = ax.imshow(pivot.values, cmap="viridis_r", vmin=0.0, vmax=1.5, aspect="auto")
    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels([c.upper() for c in pivot.columns])
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels(pivot.index)
    ax.set_title("R16 topical chromanol 30 ns matrix: last-third ligand RMSD")
    ax.set_xlabel("Target")
    ax.set_ylabel("Analog")

    for i, label in enumerate(pivot.index):
        for j, target in enumerate(pivot.columns):
            value = pivot.loc[label, target]
            if pd.isna(value):
                continue
            source = df[(df["label"] == label) & (df["target"] == target)].iloc[0]
            color = "white" if value > 0.9 else "black"
            suffix = "*" if stable_30ns(source) else "!"
            ax.text(j, i, f"{value:.2f}{suffix}", ha="center", va="center", color=color, fontsize=9)

    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label("Last-third RMSD (A)")
    fig.tight_layout()
    FIG_OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG_MATRIX, dpi=300)
    plt.close(fig)


def load_60ns_rows() -> list[dict]:
    if not SUMMARY_60NS.exists():
        return []
    rows = json.loads(SUMMARY_60NS.read_text())
    return rows if isinstance(rows, list) else []


def build_60ns_progress_figure(rows: list[dict]) -> None:
    expected_order = [
        "R15_chromanol_Cl_pos9",
        "R15_chromanol_Me6_Me9",
        "R15_chromanol_Me6_Me10",
        "R15_chromanol_Me9_Me10",
        "R15_chromanol_Cl_pos6",
        "R15_chromanol_Cl_pos10",
    ]
    by_analog = {row.get("analog_id"): row for row in rows}
    labels = [name.replace("R15_chromanol_", "") for name in expected_order]
    means = [float(by_analog[name]["rmsd_mean_A"]) if name in by_analog else 0.0 for name in expected_order]
    maxes = [float(by_analog[name]["rmsd_max_A"]) if name in by_analog else 0.0 for name in expected_order]
    colors = ["#2c7fb8" if name in by_analog else "#d9d9d9" for name in expected_order]

    fig, ax = plt.subplots(figsize=(8.8, 4.6))
    x = range(len(expected_order))
    ax.bar(x, means, color=colors, label="mean RMSD")
    ax.scatter(x, maxes, color="#d95f0e", zorder=3, label="max RMSD")
    ax.axhline(2.0, color="#b2182b", linestyle="--", linewidth=1.2, label="paper-tier max threshold")
    ax.set_xticks(list(x))
    ax.set_xticklabels(labels, rotation=35, ha="right")
    ax.set_ylabel("Ligand RMSD (A)")
    ax.set_title(f"R16 TGFB1 top-6 60 ns progress: {len(rows)}/6 complete")
    ax.set_ylim(0, 2.2)
    ax.legend(loc="upper right")
    fig.tight_layout()
    FIG_OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG_60NS, dpi=300)
    plt.close(fig)


def write_partial_summary(rows: list[dict]) -> None:
    ok = [row for row in rows if row.get("status") == "ok"]
    complete = len(ok) >= 6
    title = "Complete Summary" if complete else "Partial Summary"
    interpretation = (
        "6/6 완료 기준의 long-run TGFB1 pose-stability 보강 결과이며, lead 결론은 여전히 in silico 우선순위로 제한한다."
        if complete
        else "완료분만 반영한 중간 점검이며, 6/6 완료 전에는 lead conclusion을 강화하지 않는다."
    )
    lines = [
        f"# R16 TGFB1 Top-6 60 ns {title}",
        "",
        f"- 완료: {len(ok)}/6",
        f"- 해석: {interpretation}",
        "- caveat: OpenMM pose-stability 기반 in silico evidence이며 IC50, permeability, hERG/AMES/DILI wet-lab 검증을 대체하지 않는다.",
        "",
        "| analog_id | affinity_probability_binary | mean_A | last_third_A | max_A | status |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for row in ok:
        lines.append(
            "| "
            + " | ".join(
                [
                    str(row.get("analog_id", "")),
                    f"{float(row.get('affinity_probability_binary', 0.0)):.3f}",
                    f"{float(row.get('rmsd_mean_A', 0.0)):.2f}",
                    f"{float(row.get('rmsd_last_third_A', 0.0)):.2f}",
                    f"{float(row.get('rmsd_max_A', 0.0)):.2f}",
                    str(row.get("status", "")),
                ]
            )
            + " |"
        )
    OUT.mkdir(parents=True, exist_ok=True)
    MD_OUT.write_text("\n".join(lines) + "\n")


def main() -> int:
    if not MATRIX_CSV.exists():
        raise FileNotFoundError(MATRIX_CSV)
    build_matrix_figure()
    rows = load_60ns_rows()
    build_60ns_progress_figure(rows)
    write_partial_summary(rows)
    print(f"wrote {FIG_MATRIX}")
    print(f"wrote {FIG_60NS}")
    print(f"wrote {MD_OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
