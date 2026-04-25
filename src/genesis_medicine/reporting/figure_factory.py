"""학술 figure 자동 생성 (matplotlib 기반).

각 함수는 Path를 반환 (PNG + PDF 듀얼 저장).
대시보드용이 아니라 **출판용 figure** 품질 (벡터 PDF, 폰트 통일, DPI ≥ 300).
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # headless
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# 학술 figure 표준
plt.rcParams.update({
    "font.size": 9,
    "font.family": "DejaVu Sans",
    "axes.labelsize": 9,
    "axes.titlesize": 10,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
    "legend.fontsize": 8,
    "savefig.bbox": "tight",
    "savefig.dpi": 300,
    "pdf.fonttype": 42,        # editable text in vector
    "ps.fonttype": 42,
})


def _save_dual(fig: plt.Figure, out_dir: Path, basename: str) -> list[Path]:
    """PNG + PDF 듀얼 저장."""
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for ext in ("png", "pdf"):
        p = out_dir / f"{basename}.{ext}"
        fig.savefig(p)
        paths.append(p)
    plt.close(fig)
    return paths


# ----------------------------------------------------------------------------
def consensus_heatmap(
    consensus_df: pd.DataFrame,
    *,
    out_dir: Path,
    basename: str = "fig1_consensus_heatmap",
    score_col: str = "consensus_score",
    title: str = "Multi-target affinity probability",
    cmap: str = "viridis",
    figsize: tuple[float, float] = (7.0, 5.0),
) -> list[Path]:
    """consensus_df: index=compound, columns=targets + 'consensus_score'."""
    if consensus_df is None or consensus_df.empty:
        return []
    df = consensus_df.copy()
    cols = [c for c in df.columns if c != score_col]
    score_col_present = score_col in df.columns
    if score_col_present:
        df = df.sort_values(score_col, ascending=False)
    matrix = df[cols].astype(float).values

    fig, ax = plt.subplots(figsize=figsize)
    im = ax.imshow(matrix, aspect="auto", cmap=cmap, vmin=0, vmax=1)
    ax.set_yticks(range(len(df.index)))
    ax.set_yticklabels([str(s)[:30] for s in df.index])
    ax.set_xticks(range(len(cols)))
    ax.set_xticklabels(cols, rotation=45, ha="right")
    ax.set_title(title)
    cbar = fig.colorbar(im, ax=ax, fraction=0.04, pad=0.04)
    cbar.set_label("affinity_probability_binary")

    # 셀 안에 값 표기
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            v = matrix[i, j]
            if np.isnan(v):
                continue
            color = "white" if v < 0.5 else "black"
            ax.text(j, i, f"{v:.2f}", ha="center", va="center",
                    fontsize=6.5, color=color)

    return _save_dual(fig, out_dir, basename)


# ----------------------------------------------------------------------------
def distribution_plot(
    full_df: pd.DataFrame,
    *,
    out_dir: Path,
    basename: str = "fig2_distribution",
    score_col: str = "affinity_probability_binary",
    group_col: str = "target",
    title: str = "Affinity probability distribution by target",
    figsize: tuple[float, float] = (6.5, 4.0),
) -> list[Path]:
    """타겟별 score 분포 (boxplot + strip)."""
    if full_df is None or full_df.empty:
        return []

    df = full_df[[group_col, score_col]].dropna()
    groups = df[group_col].unique().tolist()
    data = [df.loc[df[group_col] == g, score_col].values for g in groups]

    fig, ax = plt.subplots(figsize=figsize)
    bp = ax.boxplot(data, tick_labels=groups, showfliers=False, patch_artist=True)
    for patch in bp["boxes"]:
        patch.set_facecolor("#D6E4FF")
        patch.set_edgecolor("#1F4E79")
    # strip plot — 개별 점
    rng = np.random.default_rng(0)
    for i, vals in enumerate(data):
        x = rng.normal(i + 1, 0.05, size=len(vals))
        ax.scatter(x, vals, s=10, color="#1F4E79", alpha=0.6, zorder=3)

    ax.set_ylabel(score_col)
    ax.set_xlabel(group_col)
    ax.set_title(title)
    ax.set_ylim(-0.02, 1.02)
    ax.axhline(0.5, color="gray", linestyle="--", linewidth=0.8, alpha=0.6)

    return _save_dual(fig, out_dir, basename)


# ----------------------------------------------------------------------------
def lipinski_radar(
    compounds_df: pd.DataFrame,
    *,
    top_n: int = 6,
    out_dir: Path,
    basename: str = "fig3_lipinski_radar",
    title: str = "Drug-likeness profile (top compounds)",
    figsize: tuple[float, float] = (6.0, 6.0),
) -> list[Path]:
    """Lipinski 5 변수 radar — top N compounds.

    compounds_df는 ['name', 'mw', 'logp', 'hbd', 'hba', 'tpsa']를 가져야 함.
    """
    needed = ["name", "mw", "logp", "hbd", "hba", "tpsa"]
    if compounds_df is None or any(c not in compounds_df.columns for c in needed):
        return []
    df = compounds_df.copy().head(top_n)
    if df.empty:
        return []

    # 정규화 (Lipinski 한계로)
    norm_axes = ["MW (≤500)", "logP (≤5)", "HBD (≤5)", "HBA (≤10)", "TPSA (≤140)"]
    limits = [500, 5, 5, 10, 140]
    angles = np.linspace(0, 2 * np.pi, len(norm_axes), endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=figsize, subplot_kw={"projection": "polar"})
    cmap = plt.get_cmap("tab10")

    for i, (_, r) in enumerate(df.iterrows()):
        try:
            vals = [
                float(r["mw"]) / limits[0],
                float(r["logp"]) / limits[1],
                float(r["hbd"]) / limits[2],
                float(r["hba"]) / limits[3],
                float(r["tpsa"]) / limits[4],
            ]
        except Exception:
            continue
        vals += vals[:1]
        ax.plot(angles, vals, "-", linewidth=1.5, label=str(r["name"])[:25],
                color=cmap(i % 10))
        ax.fill(angles, vals, alpha=0.08, color=cmap(i % 10))

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(norm_axes, fontsize=8)
    ax.set_yticks([0.5, 1.0, 1.5])
    ax.set_yticklabels(["½", "limit", "1.5×"])
    ax.set_ylim(0, 1.5)
    ax.set_title(title, pad=20)
    ax.legend(loc="upper right", bbox_to_anchor=(1.35, 1.05), fontsize=7)

    return _save_dual(fig, out_dir, basename)


# ----------------------------------------------------------------------------
def top_hits_table(
    consensus_df: pd.DataFrame,
    *,
    out_dir: Path,
    basename: str = "table1_top_hits",
    top_n: int = 10,
    score_col: str = "consensus_score",
) -> list[Path]:
    """학술 표 (CSV + LaTeX booktabs)."""
    if consensus_df is None or consensus_df.empty:
        return []

    out_dir.mkdir(parents=True, exist_ok=True)
    df = consensus_df.copy()
    if score_col in df.columns:
        df = df.sort_values(score_col, ascending=False)
    df = df.head(top_n).round(3)

    csv = out_dir / f"{basename}.csv"
    df.to_csv(csv)

    # LaTeX (booktabs)
    tex = out_dir / f"{basename}.tex"
    try:
        latex = df.to_latex(index=True, float_format="%.3f", longtable=False,
                            caption="Top compounds ranked by consensus affinity probability.",
                            label=f"tab:{basename}")
        # \toprule ↔ \hline 자동 변환 (booktabs)
        tex.write_text(latex)
    except Exception:
        # to_latex가 jinja2 미설치로 실패할 수 있음 — 단순 fallback
        tex.write_text("% LaTeX export requires jinja2 — see CSV instead\n")

    return [csv, tex]


# ----------------------------------------------------------------------------
def roc_curve_plot(
    actives: list[float],
    decoys: list[float],
    *,
    out_dir: Path,
    basename: str = "fig4_roc",
    title: str = "ROC: actives vs decoys",
    figsize: tuple[float, float] = (5.0, 4.0),
) -> list[Path]:
    """단순 ROC (sklearn 없이도 동작)."""
    if not actives or not decoys:
        return []

    scores = np.concatenate([np.array(actives), np.array(decoys)])
    labels = np.concatenate([np.ones(len(actives)), np.zeros(len(decoys))])
    order = np.argsort(-scores)
    scores = scores[order]
    labels = labels[order]
    tpr, fpr = [0.0], [0.0]
    n_pos, n_neg = labels.sum(), (1 - labels).sum()
    cum_pos, cum_neg = 0, 0
    for lab in labels:
        if lab == 1:
            cum_pos += 1
        else:
            cum_neg += 1
        tpr.append(cum_pos / max(n_pos, 1))
        fpr.append(cum_neg / max(n_neg, 1))
    auc = float(np.trapz(tpr, fpr))

    fig, ax = plt.subplots(figsize=figsize)
    ax.plot(fpr, tpr, color="#C0392B", linewidth=2, label=f"AUC = {auc:.3f}")
    ax.plot([0, 1], [0, 1], color="gray", linestyle="--", linewidth=1)
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    ax.set_title(title)
    ax.legend(loc="lower right")
    ax.grid(alpha=0.3)

    return _save_dual(fig, out_dir, basename)
