"""CMS-19 combined MD ensemble figure (8 jobs, 7 paper-tier)."""
from __future__ import annotations
import sys, json
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl

ROOT = Path(__file__).resolve().parents[1]
mpl.rcParams["figure.dpi"] = 300
mpl.rcParams["savefig.bbox"] = "tight"
mpl.rcParams["font.family"] = "DejaVu Sans"


def main():
    md1 = json.loads((ROOT / "pilot/md_cms19/summary.json").read_text())
    md2 = json.loads((ROOT / "pilot/md_cms19_extended/summary.json").read_text())
    all_results = md1 + md2

    valid = [r for r in all_results if r.get("status") == "ok"]
    df = pd.DataFrame(valid)
    df["target"] = df["name"].apply(lambda n: n.split("__")[0].upper().replace("_RETRY", ""))

    # Group by disease
    disease_map = {
        "SRD5A1": "alopecia / acne",
        "SREBP1": "acne",
        "TGFB1": "scar",
        "CTGF": "scar",
        "MMP1": "scar",
        "MITF": "pigmentation",
        "TYR": "pigmentation",
        "TYRP1": "pigmentation",
    }
    df["disease"] = df["target"].map(disease_map)
    print(df[["target", "disease", "rmsd_mean_A", "rmsd_max_A"]].to_string(index=False))

    fig_dir = ROOT / "preprints/03_emb3_scar_case_study/figures"
    fig_dir.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(11, 6))
    df_sorted = df.sort_values("rmsd_mean_A")
    targets = df_sorted["target"].tolist()
    rmsd_means = df_sorted["rmsd_mean_A"].tolist()
    rmsd_maxes = df_sorted["rmsd_max_A"].tolist()
    diseases = df_sorted["disease"].tolist()

    color_map = {"alopecia / acne": "#2ca02c", "scar": "#1f77b4",
                  "pigmentation": "#ff7f0e"}
    colors = [color_map.get(d, "#888") for d in diseases]

    x = np.arange(len(targets))
    w = 0.4
    bars1 = ax.bar(x - w/2, rmsd_means, w, color=colors,
                     edgecolor="black", label="RMSD mean")
    bars2 = ax.bar(x + w/2, rmsd_maxes, w, color=colors, alpha=0.5,
                     edgecolor="black", label="RMSD max")
    ax.axhline(2.0, color="red", linestyle="--", linewidth=1.5,
                 label="paper-tier (RMSD<2Å)")

    ax.set_xticks(x)
    ax.set_xticklabels([f"{t}\n({d.split('/')[0].strip()})"
                          for t, d in zip(targets, diseases)],
                         fontsize=10, rotation=0)
    ax.set_ylabel("Ligand RMSD (Å)", fontsize=12)
    ax.set_title("CMS-19 MD ensemble — 7/8 paper-tier across 3 disease verticals\n"
                  "(OpenMM 8 + GAFF-2.11 + AM1-BCC, 10 ns each, RTX 5090)",
                  fontsize=12)
    ax.legend(fontsize=10)
    ax.grid(axis="y", alpha=0.3)

    for b, v in zip(bars1, rmsd_means):
        ax.text(b.get_x() + b.get_width()/2, v + 0.04,
                  f"{v:.2f}", ha="center", fontsize=8)
    for b, v in zip(bars2, rmsd_maxes):
        ax.text(b.get_x() + b.get_width()/2, v + 0.04,
                  f"{v:.2f}", ha="center", fontsize=8)

    # Disease colored legend
    from matplotlib.patches import Patch
    handles = [Patch(facecolor=c, edgecolor="black", label=d)
                for d, c in color_map.items()]
    handles.append(plt.Line2D([0], [0], color="red", linestyle="--",
                                  label="paper-tier"))
    ax.legend(handles=handles, fontsize=9, loc="upper left")

    out = fig_dir / "fig_cms19_md_ensemble_combined.png"
    fig.savefig(out, dpi=300)
    plt.close(fig)
    print(f"\n✅ {out}")

    # Summary stats
    paper_tier = sum(1 for r in valid if r["rmsd_mean_A"] < 2.0)
    failed = sum(1 for r in all_results if r.get("status", "").startswith("runtime"))
    print(f"\n[Summary]")
    print(f"  Total jobs: {len(all_results)}")
    print(f"  Paper-tier (RMSD<2Å): {paper_tier}/{len(valid)}")
    print(f"  Failed (NaN crash): {failed}")
    print(f"  Disease coverage: 3 (alopecia, scar, pigmentation)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
