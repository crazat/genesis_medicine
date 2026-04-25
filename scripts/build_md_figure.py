"""MD 9 결과 → manuscript figure 자동 생성.

흉터 manuscript에 통합할 RMSD heatmap + 시간 축 plot.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
MD_DIR = ROOT / "pilot/skin_scar/md_top_hits"
OUT_FIG = ROOT / "pilot/skin_scar/results_v2/manuscript/figures"
OUT_FIG.mkdir(parents=True, exist_ok=True)


def main() -> int:
    summary = json.loads((MD_DIR / "summary.json").read_text())
    df = pd.DataFrame(summary)
    print(df.to_string(index=False))

    # ---- Figure 5: RMSD heatmap ----
    pivot_mean = df.pivot(index="compound", columns="target", values="rmsd_mean_A")
    pivot_max = df.pivot(index="compound", columns="target", values="rmsd_max_A")

    fig, axes = plt.subplots(1, 2, figsize=(10, 3.5))
    for ax, pivot, title in [
        (axes[0], pivot_mean, "Mean ligand RMSD (Å)"),
        (axes[1], pivot_max,  "Max ligand RMSD (Å)"),
    ]:
        im = ax.imshow(pivot.values, cmap="RdYlGn_r", vmin=0.5, vmax=3.5,
                       aspect="auto")
        ax.set_xticks(range(len(pivot.columns)))
        ax.set_xticklabels([c.upper() for c in pivot.columns])
        ax.set_yticks(range(len(pivot.index)))
        ax.set_yticklabels([c.title() for c in pivot.index])
        ax.set_title(title)
        for i in range(pivot.shape[0]):
            for j in range(pivot.shape[1]):
                v = pivot.values[i, j]
                ax.text(j, i, f"{v:.2f}", ha="center", va="center",
                        color="white" if v > 2.5 else "black", fontsize=9)
        plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    fig.tight_layout()
    p_png = OUT_FIG / "fig5_md_rmsd_heatmap.png"
    p_pdf = OUT_FIG / "fig5_md_rmsd_heatmap.pdf"
    fig.savefig(p_png, dpi=300, bbox_inches="tight")
    fig.savefig(p_pdf, bbox_inches="tight")
    plt.close(fig)
    print(f"  ✅ {p_png}")

    # ---- Figure 6: RMSD over time (개별 trajectory) ----
    fig, axes = plt.subplots(3, 3, figsize=(11, 7), sharex=True, sharey=True)
    compounds = ["embelin", "egcg", "curcumin"]
    targets = ["tgfb1", "mmp1", "ctgf"]

    for i, comp in enumerate(compounds):
        for j, tgt in enumerate(targets):
            ax = axes[i, j]
            log = MD_DIR / f"{tgt}__{comp}" / "log.csv"
            if log.exists():
                # log.csv: # "Step","Potential Energy","Kinetic Energy","Temperature"
                ldf = pd.read_csv(log)
                if "Step" in ldf.columns:
                    ax.plot(ldf["Step"]/500_000, ldf.get("Potential Energy (kJ/mole)", []),
                            color="#2E5077", linewidth=0.8)
                    ax.set_ylabel("PE (kJ/mol)" if j == 0 else "")
            ax.set_title(f"{comp.title()} × {tgt.upper()}", fontsize=9)
            if i == 2:
                ax.set_xlabel("Time (ns)")
            ax.grid(alpha=0.3)
    fig.suptitle("Potential energy over 10 ns MD (9 ligand × target combinations)",
                 fontsize=11)
    fig.tight_layout()
    p2_png = OUT_FIG / "fig6_md_pe_traces.png"
    p2_pdf = OUT_FIG / "fig6_md_pe_traces.pdf"
    fig.savefig(p2_png, dpi=300, bbox_inches="tight")
    fig.savefig(p2_pdf, bbox_inches="tight")
    plt.close(fig)
    print(f"  ✅ {p2_png}")

    # ---- 통계 요약 ----
    print(f"\n=== MD 종합 ===")
    print(f"  9 (compound × target) 평균 RMSD: {df['rmsd_mean_A'].mean():.2f} Å")
    print(f"  최저: {df['rmsd_mean_A'].min():.2f} Å ("
          f"{df.loc[df['rmsd_mean_A'].idxmin(), 'compound']} × "
          f"{df.loc[df['rmsd_mean_A'].idxmin(), 'target'].upper()})")
    print(f"  최고: {df['rmsd_mean_A'].max():.2f} Å")
    print(f"  9개 모두 < 2 Å: {(df['rmsd_mean_A'] < 2).all()}")
    print(f"  EGCG 평균: {df[df['compound']=='egcg']['rmsd_mean_A'].mean():.2f} Å")
    return 0


if __name__ == "__main__":
    sys.exit(main())
