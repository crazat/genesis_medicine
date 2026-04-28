"""EMB-3 vs CMS-19 head-to-head MD comparison figure (paper #3 v0.6)."""
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
    cms = json.loads((ROOT / "pilot/md_cms19/summary.json").read_text())
    cms_ext = json.loads((ROOT / "pilot/md_cms19_extended/summary.json").read_text())
    emb3 = json.loads((ROOT / "pilot/md_emb3_baseline/md_summary.json").read_text())

    # Combine CMS-19 results
    cms_all = cms + cms_ext
    cms_df = pd.DataFrame([r for r in cms_all if r.get("status") == "ok"])
    cms_df["target"] = cms_df["name"].apply(
        lambda n: n.split("__")[0].upper().replace("_RETRY", ""))
    cms_df = cms_df.drop_duplicates("target")

    emb3_df = pd.DataFrame([r for r in emb3 if r.get("status") == "ok"])
    emb3_df["target"] = emb3_df["name"].apply(lambda n: n.split("__")[0].upper())

    # Merge on target
    merged = pd.merge(
        cms_df[["target", "rmsd_mean_A", "rmsd_max_A"]].rename(
            columns={"rmsd_mean_A": "cms19_mean", "rmsd_max_A": "cms19_max"}),
        emb3_df[["target", "rmsd_mean_A", "rmsd_max_A"]].rename(
            columns={"rmsd_mean_A": "emb3_mean", "rmsd_max_A": "emb3_max"}),
        on="target", how="outer"
    )
    merged["winner"] = merged.apply(
        lambda r: "tie" if abs(r["cms19_mean"] - r["emb3_mean"]) < 0.05
        else ("CMS-19" if r["cms19_mean"] < r["emb3_mean"] else "EMB-3"),
        axis=1
    )
    print(merged.to_string(index=False))

    fig_dir = ROOT / "preprints/03_emb3_scar_case_study/figures"

    # Figure 1: Side-by-side bars per target
    fig, ax = plt.subplots(figsize=(11, 6))
    x = np.arange(len(merged))
    w = 0.4
    ax.bar(x - w/2, merged["emb3_mean"], w, color="#d62728",
              edgecolor="black", label="EMB-3")
    ax.bar(x + w/2, merged["cms19_mean"], w, color="#2ca02c",
              edgecolor="black", label="CMS-19")
    ax.axhline(2.0, color="red", linestyle="--", linewidth=1.5,
                 label="paper-tier (RMSD<2Å)")
    ax.set_xticks(x)
    ax.set_xticklabels(merged["target"], fontsize=11)
    ax.set_ylabel("Ligand RMSD mean (Å)", fontsize=12)
    ax.set_title("EMB-3 vs CMS-19 head-to-head MD ensemble — 7 targets × 10 ns each\n"
                  "Both leads paper-tier; CMS-19 broader-spectrum coverage",
                  fontsize=12)
    ax.legend(fontsize=11)
    ax.grid(axis="y", alpha=0.3)

    # Annotate bars
    for i, row in merged.iterrows():
        ax.text(i - w/2, row["emb3_mean"] + 0.05,
                  f"{row['emb3_mean']:.2f}", ha="center", fontsize=8)
        ax.text(i + w/2, row["cms19_mean"] + 0.05,
                  f"{row['cms19_mean']:.2f}", ha="center", fontsize=8)
        # Winner mark
        ax.text(i, max(row["emb3_mean"], row["cms19_mean"]) + 0.2,
                  "🏆 " + row["winner"][:6], ha="center", fontsize=9, color="navy")

    out = fig_dir / "fig_emb3_vs_cms19_headtohead.png"
    fig.savefig(out, dpi=300)
    plt.close(fig)
    print(f"\n✅ {out}")

    # Save merged CSV
    merged.to_csv(fig_dir.parent / "emb3_vs_cms19_md_comparison.csv", index=False)
    return 0


if __name__ == "__main__":
    sys.exit(main())
