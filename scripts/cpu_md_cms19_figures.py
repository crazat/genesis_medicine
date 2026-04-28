"""CMS-19 MD ensemble RMSD time-series figures for preprint #3 v0.4."""
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


def main():
    md_dir = ROOT / "pilot/md_cms19"
    fig_dir = ROOT / "preprints/03_emb3_scar_case_study/figures"
    fig_dir.mkdir(parents=True, exist_ok=True)

    # Reload trajectories for RMSD time-series
    try:
        import mdtraj as md
    except ImportError:
        print("⚠️  mdtraj unavailable; generating bar-chart only")
        md = None

    jobs = [
        ("srd5a1__cms19", "SRD5A1 (alopecia)", "#2ca02c"),
        ("tgfb1__cms19",  "TGFB1 (scar #1)",   "#1f77b4"),
        ("ctgf__cms19",   "CTGF (scar #2)",    "#ff7f0e"),
    ]

    # Figure 1: RMSD time-series (3 panels)
    if md is not None:
        fig, axes = plt.subplots(1, 3, figsize=(15, 4), sharey=True)
        for ax, (name, title, color) in zip(axes, jobs):
            traj_dcd = md_dir / name / "traj.dcd"
            top_pdb = md_dir / name / "final.pdb"
            if not traj_dcd.exists() or not top_pdb.exists():
                ax.text(0.5, 0.5, "Missing", ha="center", va="center")
                continue
            try:
                t = md.load(str(traj_dcd), top=str(top_pdb))
                lig_idx = t.topology.select("resname UNK and element != H")
                if len(lig_idx) == 0:
                    lig_idx = t.topology.select("(not protein) and element != H")
                rmsd_nm = md.rmsd(t, t, frame=0, atom_indices=lig_idx)
                rmsd_a = rmsd_nm * 10.0   # nm → Å
                time_ns = np.arange(len(rmsd_a)) * 0.001  # 500 steps × 2 fs = 1 ps
                ax.plot(time_ns, rmsd_a, color=color, linewidth=1.0, alpha=0.85)
                ax.axhline(2.0, color="red", linestyle="--", linewidth=1,
                            label="paper-tier threshold")
                ax.set_xlabel("Time (ns)", fontsize=11)
                ax.set_title(f"{title}\nmean={rmsd_a.mean():.2f} Å, max={rmsd_a.max():.2f} Å",
                              fontsize=11)
                ax.grid(alpha=0.3)
                if ax is axes[0]:
                    ax.set_ylabel("Ligand RMSD vs frame 0 (Å)", fontsize=11)
                ax.legend(fontsize=9, loc="upper right")
            except Exception as e:
                ax.text(0.5, 0.5, f"err: {str(e)[:30]}", ha="center", va="center")
        plt.suptitle("CMS-19 MD ensemble — paper-tier ligand binding stability "
                       "(3/4 RMSD < 2 Å, RTX 5090, 10 ns each)",
                       fontsize=12, y=1.02)
        out = fig_dir / "fig_cms19_md_rmsd_timeseries.png"
        fig.savefig(out, dpi=300)
        plt.close(fig)
        print(f"✅ {out}")

    # Figure 2: Summary bar chart
    summary = pd.read_json(md_dir / "summary.json")
    valid = summary[summary["status"] == "ok"]

    fig, ax = plt.subplots(figsize=(9, 5))
    targets = [r["name"].split("__")[0].upper() for _, r in valid.iterrows()]
    rmsd_means = valid["rmsd_mean_A"].tolist()
    rmsd_maxes = valid["rmsd_max_A"].tolist()
    x = np.arange(len(targets))
    w = 0.35
    ax.bar(x - w/2, rmsd_means, w, label="RMSD mean", color="#1f77b4", edgecolor="black")
    ax.bar(x + w/2, rmsd_maxes, w, label="RMSD max", color="#ff7f0e", edgecolor="black")
    ax.axhline(2.0, color="red", linestyle="--", linewidth=1.5,
                label="paper-tier (RMSD<2Å)")
    ax.set_xticks(x)
    ax.set_xticklabels(targets, fontsize=11)
    ax.set_ylabel("RMSD (Å)", fontsize=12)
    ax.set_title("CMS-19 MD ensemble — 10 ns ligand binding stability\n"
                  "3/4 paper-tier (SREBP1 NaN excluded)",
                  fontsize=12)
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    for i, (m, mx) in enumerate(zip(rmsd_means, rmsd_maxes)):
        ax.text(i - w/2, m + 0.05, f"{m:.2f}", ha="center", fontsize=9)
        ax.text(i + w/2, mx + 0.05, f"{mx:.2f}", ha="center", fontsize=9)
    out = fig_dir / "fig_cms19_md_rmsd_summary.png"
    fig.savefig(out, dpi=300)
    plt.close(fig)
    print(f"✅ {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
