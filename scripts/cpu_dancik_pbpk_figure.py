"""Dancik PBPK 102-compound figure for preprint #14 v0.2.

Figures:
1. Per-vehicle bioavailability comparison (boxplot)
2. logKp distribution by category (centella, embelin, etc.)
3. Top 20 compounds (cumulative dose) bar chart with vehicle stacks
"""
from __future__ import annotations
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl

ROOT = Path(__file__).resolve().parents[1]
mpl.rcParams["figure.dpi"] = 300
mpl.rcParams["savefig.bbox"] = "tight"
mpl.rcParams["font.family"] = "DejaVu Sans"


def main() -> int:
    csv = ROOT / "pilot/cpu_meaningful/dancik_pbpk_102.csv"
    df = pd.read_csv(csv)
    df = df.dropna(subset=["log_kp_cm_s"])
    print(f"Loaded {len(df)} Dancik PBPK rows")

    fig_dir = ROOT / "preprints/14_topical_pbpk_methodology/figures"
    fig_dir.mkdir(parents=True, exist_ok=True)

    # --- Figure 1: vehicle comparison boxplot --------------------------------
    fig, ax = plt.subplots(figsize=(8, 5))
    vehicles = ["aqueous", "gel", "cream", "ointment"]
    data = [df[df["vehicle"] == v]["flux_ss_ug_cm2_h"].clip(upper=5e4) for v in vehicles]
    bp = ax.boxplot(data, labels=vehicles, patch_artist=True,
                     showfliers=False, widths=0.6)
    colors = ["#cce5ff", "#b3d9ff", "#80bfff", "#3399ff"]
    for patch, c in zip(bp["boxes"], colors):
        patch.set_facecolor(c)
    ax.set_yscale("log")
    ax.set_ylabel("Steady-state flux (μg/cm²/h)", fontsize=12)
    ax.set_xlabel("Vehicle", fontsize=12)
    ax.set_title("Vehicle effect on transdermal flux\n(Dancik 4-layer PBPK, n=102 compounds)",
                  fontsize=12)
    ax.grid(axis="y", alpha=0.3)
    fig.savefig(fig_dir / "fig1_vehicle_flux_comparison.png", dpi=300)
    plt.close(fig)
    print(f"  ✅ fig1_vehicle_flux_comparison.png")

    # --- Figure 2: logKp distribution histogram + topical-suitable threshold -
    fig, ax = plt.subplots(figsize=(8, 5))
    oint = df[df["vehicle"] == "ointment"]
    ax.hist(oint["log_kp_cm_s"], bins=30, color="#3399ff", edgecolor="black", alpha=0.85)
    ax.axvline(-5.0, color="red", linestyle="--", linewidth=1.5,
                 label="Topical-suitable threshold (logKp > -5)")
    ax.axvline(-3.5, color="orange", linestyle="--", linewidth=1.5,
                 label="High permeability (logKp > -3.5)")
    ax.set_xlabel("log Kp (cm/s)", fontsize=12)
    ax.set_ylabel("# compounds", fontsize=12)
    ax.set_title("Skin permeability distribution — 102 curated natural products\n"
                  "(Dancik PBPK + Potts-Guy fallback)",
                  fontsize=12)
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    fig.savefig(fig_dir / "fig2_logkp_distribution.png", dpi=300)
    plt.close(fig)
    print(f"  ✅ fig2_logkp_distribution.png")

    # --- Figure 3: Top 20 compounds bar chart --------------------------------
    top = oint.nlargest(20, "cum_24h_ug_cm2").sort_values("cum_24h_ug_cm2")
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.barh(top["name"], top["cum_24h_ug_cm2"] / 1000, color="#3399ff",
              edgecolor="black", height=0.7)
    ax.set_xlabel("24h cumulative dose (mg/cm², ointment, occluded)", fontsize=12)
    ax.set_title("Top 20 compounds by topical bioavailability\n"
                  "(Dancik 4-layer PBPK, ointment vehicle)",
                  fontsize=12)
    ax.set_xscale("log")
    ax.grid(axis="x", alpha=0.3)
    for i, (_, row) in enumerate(top.iterrows()):
        ax.text(row["cum_24h_ug_cm2"] / 1000 * 1.05, i,
                  f"logKp={row['log_kp_cm_s']:.2f}", fontsize=8, va="center")
    fig.savefig(fig_dir / "fig3_top20_topical_bioavailability.png", dpi=300)
    plt.close(fig)
    print(f"  ✅ fig3_top20_topical_bioavailability.png")

    print(f"\n3 figures written to {fig_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
