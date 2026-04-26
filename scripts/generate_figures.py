"""Publication figures for Genesis_Medicine preprints v0.2.

Generates per-preprint figures (PNG, 300 DPI) from real data CSVs:
- Chemical structures via RDKit
- Affinity heatmaps + bar charts via matplotlib
- ADMET scatter plots
- Pipeline / architecture diagrams
- 자오류주 24-hour clock
- Cross-disease overlap visualization

Output: preprints/<NN_dir>/figures/*.png
"""

from __future__ import annotations

import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, Rectangle, Circle
from matplotlib.lines import Line2D

warnings.filterwarnings("ignore")
plt.rcParams.update({
    "font.family": ["NanumGothic", "DejaVu Sans"],
    "font.size": 10,
    "axes.titlesize": 12,
    "axes.labelsize": 10,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "legend.fontsize": 9,
    "figure.dpi": 100,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
})

ROOT = Path(__file__).resolve().parents[1]
PREPRINTS = ROOT / "preprints"


def fig_dir(num_dir: str) -> Path:
    p = PREPRINTS / num_dir / "figures"
    p.mkdir(parents=True, exist_ok=True)
    return p


# ===========================================================================
# Helper: structure rendering via RDKit
# ===========================================================================

def render_structures(smiles_dict: dict, out_path: Path,
                       cols: int = 3, mol_size=(300, 300)) -> Path:
    """Render multiple molecules via RDKit + matplotlib (Korean-text-safe legends)."""
    from rdkit import Chem
    from rdkit.Chem import Draw

    items = []
    for name, smi in smiles_dict.items():
        m = Chem.MolFromSmiles(smi)
        if m is not None:
            img = Draw.MolToImage(m, size=mol_size)
            items.append((name, img))

    n = len(items)
    rows = (n + cols - 1) // cols
    fig, axes = plt.subplots(rows, cols,
                               figsize=(cols * 3.2, rows * 3.5))
    axes = np.atleast_2d(axes)
    for i, (name, img) in enumerate(items):
        r, c = divmod(i, cols)
        ax = axes[r, c]
        ax.imshow(img)
        ax.set_title(name, fontsize=10, pad=4)
        ax.axis("off")
    # Hide unused
    for i in range(n, rows * cols):
        r, c = divmod(i, cols)
        axes[r, c].axis("off")
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()
    return out_path


# ===========================================================================
# Preprint #3 — EMB-3 case study figures
# ===========================================================================

def fig_03_emb3_structures():
    out = fig_dir("03_emb3_scar_case_study") / "fig1_emb3_structures.png"
    render_structures({
        "Embelin (parent, C11)": "CCCCCCCCCCCC1=C(C(=O)C=C(C1=O)O)O",
        "EMB-3 (this work, C6+Me)": "CCCCCC1=C(O)C(=O)C(O)=C(C)C1=O",
        "Rapanone (C13)": "CCCCCCCCCCCCCC1=C(O)C(=O)C(=O)C=C1O",
        "5-O-methyl-Embelin": "CCCCCCCCCCCC1=C(C(=O)C=C(C1=O)OC)O",
        "Marimastat (reference)": "CC(C)CC(NC(=O)C(NC(=O)C(O)CC(C)C)C(C)(C)C)C(=O)NC",
        "Lawsone (naphthoquinone control)": "O=C1C=CC(=O)c2c1cccc2O",
    }, out, cols=3)
    print(f"  ✅ {out}")


def fig_03_sar_scatter():
    """7-compound SAR scatter: logP vs hERG, MW colored, mean-affinity sized."""
    df = pd.read_csv(ROOT / "pilot/sar_panel/panel_validated.csv")

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # logP vs hERG
    sc = axes[0].scatter(df["logP"], df["admet_hERG"],
                          s=80, c=df["MW"], cmap="viridis",
                          edgecolors="black", linewidth=0.7)
    axes[0].axvspan(1.5, 3.5, alpha=0.12, color="green",
                     label="topical sweet spot")
    axes[0].axhline(0.30, color="red", linestyle="--", alpha=0.5,
                     label="hERG concern (>0.3)")
    for _, r in df.iterrows():
        offset = (5, 5)
        if r["compound"] == "EMB-3":
            offset = (10, 10)
        axes[0].annotate(r["compound"][:10], (r["logP"], r["admet_hERG"]),
                          fontsize=8, xytext=offset, textcoords="offset points")
    axes[0].set_xlabel("logP (calc.)")
    axes[0].set_ylabel("ADMET-AI hERG probability")
    axes[0].set_title("(A) Topical sweet spot + cardiac safety")
    axes[0].legend(loc="upper left", fontsize=8)
    plt.colorbar(sc, ax=axes[0], label="MW (Da)")

    # Skin reaction vs AMES
    sc2 = axes[1].scatter(df["admet_Skin_Reaction"], df["admet_AMES"],
                           s=80, c=df["logP"], cmap="coolwarm",
                           edgecolors="black", linewidth=0.7)
    for _, r in df.iterrows():
        axes[1].annotate(r["compound"][:10],
                          (r["admet_Skin_Reaction"], r["admet_AMES"]),
                          fontsize=8, xytext=(5, 5), textcoords="offset points")
    axes[1].set_xlabel("ADMET-AI Skin Reaction probability")
    axes[1].set_ylabel("ADMET-AI AMES probability")
    axes[1].set_title("(B) Skin irritation × mutagenicity")
    plt.colorbar(sc2, ax=axes[1], label="logP")
    axes[1].set_xlim(0.3, 1.0)

    plt.suptitle("Embelin scaffold-hop SAR panel (real ADMET-AI data, 2026-04-26)",
                  y=1.02)
    out = fig_dir("03_emb3_scar_case_study") / "fig2_sar_scatter.png"
    plt.savefig(out)
    plt.close()
    print(f"  ✅ {out}")


def fig_03_round_progress():
    """Round 1-3 generative progression."""
    rounds_data = {
        "Round 1": {"n_candidates": 1, "best_mean": 0.711, "compound": "EMB-3"},
        "Round 2": {"n_candidates": 3, "best_mean": 0.567, "compound": "r2_1"},
        "Round 3": {"n_candidates": 15, "best_mean": 0.650, "compound": "r3_6 (=EMB-3)"},
    }
    fig, ax = plt.subplots(figsize=(8, 5))
    x = list(rounds_data.keys())
    means = [d["best_mean"] for d in rounds_data.values()]
    bars = ax.bar(x, means, color=["green", "orange", "tab:gray"], edgecolor="black")
    ax.axhline(0.711, color="green", linestyle="--", alpha=0.6,
                label="EMB-3 baseline (Round 1, mean 0.711)")
    for bar, (k, d) in zip(bars, rounds_data.items()):
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, h + 0.01,
                 f"{d['best_mean']:.3f}\n{d['compound']}\n(n={d['n_candidates']})",
                 ha="center", fontsize=9)
    ax.set_ylabel("Best mean Boltz-2 affinity (TGFB1 + MMP1)")
    ax.set_title("Generative scaffold-hop rounds — EMB-3 local optimum")
    ax.set_ylim(0, 0.85)
    ax.legend(loc="lower right")
    out = fig_dir("03_emb3_scar_case_study") / "fig3_round_progression.png"
    plt.savefig(out)
    plt.close()
    print(f"  ✅ {out}")


# ===========================================================================
# Disease-screen heatmaps (#4-#7)
# ===========================================================================

def fig_disease_heatmap(disease_dir: str, results_csv: Path,
                         target_cols: list[str], title: str, top_n: int = 12):
    df = pd.read_csv(results_csv)
    # Sort by mean_affinity if present
    sort_col = "mean_affinity" if "mean_affinity" in df.columns else target_cols[0]
    df = df.sort_values(sort_col, ascending=False).head(top_n)

    # Heatmap
    matrix = df[target_cols].values.astype(float)
    fig, ax = plt.subplots(figsize=(8, max(6, top_n * 0.5)))
    im = ax.imshow(matrix, cmap="YlOrRd", aspect="auto", vmin=0.2, vmax=0.85)
    ax.set_xticks(range(len(target_cols)))
    ax.set_xticklabels(target_cols, rotation=45, ha="right")
    ax.set_yticks(range(len(df)))
    ax.set_yticklabels(df["compound"].tolist(), fontsize=9)
    for i in range(len(df)):
        for j in range(len(target_cols)):
            v = matrix[i, j]
            if np.isnan(v):
                text = "—"
                color = "gray"
            else:
                text = f"{v:.2f}"
                color = "white" if v > 0.6 else "black"
            ax.text(j, i, text, ha="center", va="center",
                     color=color, fontsize=9, fontweight="bold")
    plt.colorbar(im, ax=ax, label="Boltz-2 affinity_probability_binary")
    ax.set_title(title)
    out = fig_dir(disease_dir) / "fig1_affinity_heatmap.png"
    plt.savefig(out)
    plt.close()
    print(f"  ✅ {out}")


def fig_disease_safety_quadrant(disease_dir: str, results_csv: Path,
                                  title: str):
    df = pd.read_csv(results_csv)
    if "mean_affinity" not in df.columns:
        return
    df = df.dropna(subset=["mean_affinity"])

    fig, ax = plt.subplots(figsize=(9, 6))
    sc = ax.scatter(df["admet_hERG"], df["mean_affinity"],
                     s=df["MW"]/4, c=df["logP"], cmap="coolwarm",
                     edgecolors="black", linewidth=0.7, alpha=0.8)
    ax.axvspan(0, 0.30, alpha=0.10, color="green", label="hERG safe (<0.30)")
    ax.axvspan(0.50, 1.0, alpha=0.10, color="red", label="hERG risk (>0.50)")
    ax.axhline(0.55, color="black", linestyle="--", alpha=0.4,
                label="moderate engagement (0.55)")

    # Annotate top 8
    df_sorted = df.sort_values("mean_affinity", ascending=False).head(8)
    for _, r in df_sorted.iterrows():
        ax.annotate(r["compound"][:14],
                     (r["admet_hERG"], r["mean_affinity"]),
                     fontsize=8, xytext=(5, 5), textcoords="offset points")

    ax.set_xlabel("ADMET-AI hERG probability")
    ax.set_ylabel("Mean Boltz-2 affinity_probability_binary")
    ax.set_title(title)
    ax.legend(loc="lower right", fontsize=9)
    plt.colorbar(sc, ax=ax, label="logP")
    out = fig_dir(disease_dir) / "fig2_safety_affinity_quadrant.png"
    plt.savefig(out)
    plt.close()
    print(f"  ✅ {out}")


# ===========================================================================
# Preprint #9 — Cross-disease Open Targets visualization
# ===========================================================================

def fig_09_emb3_target_profile():
    """EMB-3 multi-target affinity bar chart."""
    targets = ["TGFB1", "MMP1", "CTGF", "SMAD3", "PDGFRB", "LOX",
                "VEGFA", "JUN", "FGF2"]
    affinities = [0.749, 0.674, 0.678, 0.649, 0.640, 0.579,
                   0.563, 0.497, 0.484]
    colors = ["tab:blue" if a >= 0.55 else "lightgray" for a in affinities]

    fig, ax = plt.subplots(figsize=(9, 5))
    bars = ax.bar(targets, affinities, color=colors, edgecolor="black")
    ax.axhline(0.55, color="red", linestyle="--", alpha=0.5,
                label="moderate engagement threshold (0.55)")
    for bar, a in zip(bars, affinities):
        ax.text(bar.get_x() + bar.get_width()/2, a + 0.005,
                 f"{a:.3f}", ha="center", fontsize=9)
    ax.set_ylabel("Boltz-2 affinity_probability_binary")
    ax.set_title("EMB-3 multi-target predicted affinity profile (real Round-1 data)")
    ax.set_ylim(0, 0.85)
    ax.legend()
    out = fig_dir("09_cross_disease_ipf") / "fig1_emb3_target_profile.png"
    plt.savefig(out)
    plt.close()
    print(f"  ✅ {out}")


def fig_09_target_to_disease():
    """Each canonical target → fibrotic disease association heatmap."""
    csv_path = ROOT / "pilot/open_targets/antifibrotic_targets_to_diseases.csv"
    if not csv_path.exists():
        print(f"  ⚠️ {csv_path} missing")
        return
    df = pd.read_csv(csv_path)
    # Pivot
    pivot = df.pivot_table(index="target_symbol", columns="disease_name",
                            values="ot_score", aggfunc="first")
    # All canonical targets (incl. ones with no hits)
    all_targets = ["PDGFRB", "TGFB1", "SMAD3", "MMP1", "MMP3", "MMP9",
                    "CTGF", "LOX", "COL1A1"]
    pivot = pivot.reindex(all_targets, fill_value=np.nan)

    fig, ax = plt.subplots(figsize=(11, 6))
    matrix = pivot.values
    im = ax.imshow(matrix, cmap="RdYlGn", aspect="auto",
                    vmin=0.4, vmax=0.75)
    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels(pivot.columns, rotation=45, ha="right", fontsize=8)
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels(pivot.index, fontsize=10)
    for i in range(len(pivot.index)):
        for j in range(len(pivot.columns)):
            v = matrix[i, j]
            if not np.isnan(v):
                ax.text(j, i, f"{v:.2f}", ha="center", va="center",
                         color="black", fontsize=8, fontweight="bold")
            else:
                ax.text(j, i, "—", ha="center", va="center",
                         color="lightgray", fontsize=8)
    plt.colorbar(im, ax=ax, label="Open Targets association score")
    ax.set_title("Canonical anti-fibrotic targets × fibrotic-spectrum diseases\n"
                  "(Open Targets v4 query, score ≥ 0.4 threshold)")
    out = fig_dir("09_cross_disease_ipf") / "fig2_target_disease_overlap.png"
    plt.savefig(out)
    plt.close()
    print(f"  ✅ {out}")


# ===========================================================================
# Preprint #10 — Chronotherapy 24-hour clock
# ===========================================================================

def fig_10_jaoryuju_clock():
    """24-hour 자오류주 + skin-rhythm clock."""
    meridians_korean = [
        ("담", "23-01"), ("간", "01-03"), ("폐", "03-05"), ("대장", "05-07"),
        ("위", "07-09"), ("비", "09-11"), ("심", "11-13"), ("소장", "13-15"),
        ("방광", "15-17"), ("신", "17-19"), ("심포", "19-21"), ("삼초", "21-23"),
    ]
    skin_rhythms = {
        6.5: ("Keratinocyte\nproliferation", "tab:blue"),
        10.5: ("Sebum rising", "tab:orange"),
        13.5: ("Sebum peak", "tab:red"),
        16.5: ("MMP rising", "tab:purple"),
        19.5: ("Barrier\npermeability", "tab:green"),
        2: ("DNA repair\n+ stem-cell rest", "tab:cyan"),
    }
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw={"projection": "polar"})
    ax.set_theta_zero_location("N")
    ax.set_theta_direction(-1)
    # 12 meridian wedges
    width = 2 * np.pi / 12
    colors = plt.cm.tab20.colors
    for i, (name, hours) in enumerate(meridians_korean):
        theta = i * width + width / 2 - width   # offset so 자(23-01) wraps top
        ax.bar(theta, 1, width=width, bottom=0.7, alpha=0.5,
                color=colors[i % 20], edgecolor="black", linewidth=0.5)
        ax.text(theta, 1.45, name, ha="center", va="center",
                 fontsize=11, fontweight="bold")
        ax.text(theta, 1.85, hours, ha="center", va="center",
                 fontsize=8, color="dimgray")

    # Skin rhythm overlay markers
    for hour, (label, color) in skin_rhythms.items():
        theta = hour / 24 * 2 * np.pi
        ax.plot([theta, theta], [0, 0.65], color=color, linewidth=2.5)
        ax.text(theta, 0.30, label, ha="center", va="center",
                 fontsize=8, color=color, fontweight="bold",
                 bbox=dict(facecolor="white", alpha=0.7,
                            edgecolor=color, boxstyle="round,pad=0.2"))

    ax.set_yticklabels([])
    ax.set_xticks([i * np.pi / 6 for i in range(12)])
    ax.set_xticklabels([f"{(i*2):02d}" for i in range(12)],
                        fontsize=8, color="dimgray")
    ax.set_ylim(0, 2.2)
    plt.title("자오류주 12 meridian × modern skin circadian rhythm\n"
               "(framework integration, hypothesis-level)",
               y=1.05, fontsize=11)
    out = fig_dir("10_chronotherapy_jaoryuju") / "fig1_jaoryuju_clock.png"
    plt.savefig(out)
    plt.close()
    print(f"  ✅ {out}")


# ===========================================================================
# Preprint #2 + #12 — Pipeline architecture diagrams
# ===========================================================================

def fig_02_three_pillar():
    """3-pillar Recover model diagram."""
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5)
    ax.axis("off")

    pillars = [
        (1.5, "HAN PREDICT, Inc.", "tab:blue",
         "AI healthcare platform\n(Clinic CRM, Smart Charts,\nMarketing AI, NutriDocH,\nfacial_dx Station Kit)"),
        (5.0, "Genesis_Medicine Lab", "tab:orange",
         "AI in silico drug discovery R&D\n(REINVENT4 + Boltz-2 +\nADMET-AI + corrected ABFE)"),
        (8.5, "Recover Korean Medicine Clinic", "tab:green",
         "Skin regeneration practice\n강남, 2026-08-15 opening\n(scar / pigment / alopecia /\nacne / photoaging)"),
    ]
    for x, name, color, desc in pillars:
        box = FancyBboxPatch((x - 1.4, 1.7), 2.8, 2.2,
                              boxstyle="round,pad=0.05", linewidth=2,
                              edgecolor=color, facecolor=color, alpha=0.15)
        ax.add_patch(box)
        ax.text(x, 3.6, name, ha="center", va="center",
                 fontsize=11, fontweight="bold", color=color)
        ax.text(x, 2.6, desc, ha="center", va="center",
                 fontsize=8.5, color="black")
    # Connecting arrows
    arrow_props = dict(arrowstyle="->", lw=1.5, color="dimgray")
    ax.annotate("", xy=(3.6, 2.8), xytext=(2.9, 2.8), arrowprops=arrow_props)
    ax.annotate("", xy=(7.1, 2.8), xytext=(6.4, 2.8), arrowprops=arrow_props)
    ax.text(3.25, 3.0, "patient data\n→ molecular Q", ha="center",
             fontsize=8, color="dimgray", style="italic")
    ax.text(6.75, 3.0, "molecular hypothesis\n→ clinical decision", ha="center",
             fontsize=8, color="dimgray", style="italic")

    # Patient layer at bottom
    patient = FancyBboxPatch((4.0, 0.2), 2.0, 1.0, boxstyle="round,pad=0.05",
                              edgecolor="darkblue", facecolor="lightblue",
                              alpha=0.5, linewidth=2)
    ax.add_patch(patient)
    ax.text(5.0, 0.7, "Patient", ha="center", fontsize=12, fontweight="bold")

    # Patient → 3 pillars
    for x, _, _, _ in pillars:
        ax.annotate("", xy=(x, 1.7), xytext=(5.0, 1.2),
                     arrowprops=dict(arrowstyle="->", lw=1, color="lightblue"))

    ax.set_title("Recover 3-pillar institutional integration\n"
                  "(HanCheongWoo, founder)", fontsize=13)
    out = fig_dir("02_recover_workflow") / "fig1_three_pillar.png"
    plt.savefig(out)
    plt.close()
    print(f"  ✅ {out}")


def fig_02_patient_workflow():
    """Layer A → B → C patient workflow flowchart."""
    fig, ax = plt.subplots(figsize=(11, 6))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 7)
    ax.axis("off")

    layers = [
        (1.5, 5.5, "Layer A\n3D facial diagnostics", "tab:blue",
         "Morpheus 3D + iPhone TrueDepth\n→ mesh + asymmetry RMS\n→ 23 landmarks\n→ 9-gate Safety Supervisor"),
        (1.5, 2.8, "Layer B\nSmart Charts AI EMR", "tab:orange",
         "Free-text 변증 capture\n+ InBody integration\n+ RAG over 114+ docs\n+ treatment surfaces"),
        (1.5, 0.3, "Layer C\nGenesis_Medicine engine", "tab:green",
         "REINVENT4 + Boltz-2 +\nADMET-AI + MD + ABFE\n→ ranked compound table\nfor clinician review"),
    ]
    for x, y, title, color, desc in layers:
        box = FancyBboxPatch((x - 1.3, y), 2.6, 1.4,
                              boxstyle="round,pad=0.05", linewidth=2,
                              edgecolor=color, facecolor=color, alpha=0.15)
        ax.add_patch(box)
        ax.text(x, y + 1.15, title, ha="center", fontsize=10,
                 fontweight="bold", color=color)
        ax.text(x, y + 0.5, desc, ha="center", fontsize=7.5)

    # Patient flow on right
    flow_steps = [
        (7, 6, "Patient\narrives", "tab:blue"),
        (7, 4.5, "3D capture\n(Morpheus / iPhone)", "tab:cyan"),
        (7, 3.0, "변증 + InBody\nconsultation", "tab:orange"),
        (7, 1.5, "Molecular\nrecommendations", "tab:green"),
        (7, 0.0, "한의사 prescribes\n(advisory AI)", "tab:purple"),
    ]
    for x, y, label, color in flow_steps:
        circ = Circle((x, y + 0.35), 0.55, color=color, alpha=0.5)
        ax.add_patch(circ)
        ax.text(x, y + 0.35, label, ha="center", va="center",
                 fontsize=8, fontweight="bold")
    for i in range(len(flow_steps) - 1):
        ax.annotate("", xy=(7, flow_steps[i+1][1] + 0.95),
                     xytext=(7, flow_steps[i][1] - 0.20),
                     arrowprops=dict(arrowstyle="->", lw=1.2, color="dimgray"))

    # Layer ↔ Patient flow connections
    ax.annotate("", xy=(6.4, 4.85), xytext=(2.85, 6.0),
                 arrowprops=dict(arrowstyle="->", color="tab:blue", lw=1, alpha=0.5))
    ax.annotate("", xy=(6.4, 3.35), xytext=(2.85, 3.3),
                 arrowprops=dict(arrowstyle="->", color="tab:orange", lw=1, alpha=0.5))
    ax.annotate("", xy=(6.4, 1.85), xytext=(2.85, 0.8),
                 arrowprops=dict(arrowstyle="->", color="tab:green", lw=1, alpha=0.5))

    # Output IRB note
    ax.text(10.5, 4, "Outcome capture\n(follow-up 3D, PROs)\n↓ feedback to Layer C",
             ha="center", fontsize=8, style="italic",
             bbox=dict(facecolor="lightyellow", edgecolor="gray",
                        boxstyle="round,pad=0.3"))
    ax.annotate("", xy=(10.5, 2.6), xytext=(7.6, 0.2),
                 arrowprops=dict(arrowstyle="->", color="dimgray", lw=1, alpha=0.6))

    ax.set_title("Recover Korean Medicine Clinic patient workflow\n"
                  "Layer A → B → C integration",
                  fontsize=12)
    out = fig_dir("02_recover_workflow") / "fig2_patient_workflow.png"
    plt.savefig(out)
    plt.close()
    print(f"  ✅ {out}")


# ===========================================================================
# Preprint #1 — Embelin pharmacology overview
# ===========================================================================

def fig_01_embelin_summary():
    out = fig_dir("01_embelia_ribes_review") / "fig1_embelin_structure.png"
    render_structures({
        "Embelin\n(Embelia ribes / 자단)": "CCCCCCCCCCCC1=C(C(=O)C=C(C1=O)O)O",
        "EMB-3\n(this work, scaffold-hop)": "CCCCCC1=C(O)C(=O)C(O)=C(C)C1=O",
        "Shikonin\n(자초 - distinct scaffold!)": "CC(=CCC(O)C1=C(O)C(=O)c2cccc(O)c2C1=O)C",
    }, out, cols=3)
    print(f"  ✅ {out}")


# ===========================================================================
# Preprint #11 — Korean PGx variant frequency
# ===========================================================================

def fig_11_pgx_frequencies():
    """Korean vs Caucasian vs Han Chinese variant frequencies."""
    variants = ["CYP2D6*10", "CYP2C19*2/*3", "CYP3A5*3", "UGT1A1*6",
                 "HLA-B*15:02", "HLA-B*58:01", "FLG 3321delA"]
    korean = [50, 40, 75, 10, 0.4, 7, 4]   # %
    caucasian = [3, 15, 15, 1, 0.01, 1, 0.5]
    han_chinese = [50, 40, 25, 12, 12, 9, 0]

    x = np.arange(len(variants))
    width = 0.27

    fig, ax = plt.subplots(figsize=(11, 5.5))
    ax.bar(x - width, korean, width, color="tab:red",
            label="Korean", edgecolor="black")
    ax.bar(x, caucasian, width, color="tab:blue",
            label="Caucasian (CEU)", edgecolor="black")
    ax.bar(x + width, han_chinese, width, color="tab:orange",
            label="Han Chinese", edgecolor="black")
    ax.set_xticks(x)
    ax.set_xticklabels(variants, rotation=30, ha="right")
    ax.set_ylabel("Variant frequency (%)")
    ax.set_title("Korean-population PGx variant frequencies\n"
                  "(literature-cited; for panel design rationale)",
                  fontsize=11)
    ax.legend(loc="upper right")
    ax.grid(axis="y", linestyle=":", alpha=0.5)
    out = fig_dir("11_korean_pgx_topical") / "fig1_pgx_frequencies.png"
    plt.savefig(out)
    plt.close()
    print(f"  ✅ {out}")


# ===========================================================================
# Preprint #12 — 12-tier pipeline architecture
# ===========================================================================

def fig_12_tier_overview():
    """12-tier pipeline overview."""
    tiers = [
        (0, "Foundation", "Boltz-2, REINVENT4, ADMET-AI, OpenMM, openmmtools, MACE-OFF24, RDKit", "tab:blue"),
        (1, "Acceleration / Quality", "Protenix, OpenFold3, AlphaFlow-Lit, CarsiDock-Cov, Boltz-ABFE, DeepRetro, AIMNet2", "tab:cyan"),
        (2, "Skin-specific Adapters", "PanDerm, ChemCrow agent, Stratum corneum MD, Bayesian SAR, ESM3, scFoundation", "tab:green"),
        (3, "Multi-target / Cryptic", "LPA1/αvβ6/YAP1/TAZ, DGAT-DDI, QM/MM ABFE, Spatial-T, mechanotransduction", "tab:olive"),
        (4, "Kinetics / SAR loops", "k_off MD, Chou-Talalay PBPK, self-improvement loop, Enamine REAL, Lunit/VUNO", "tab:orange"),
        (5, "Causal / Stratified", "DoWhy/EconML, papillary-reticular fibroblast, microbiome AI, KEDD, federated-learning", "tab:red"),
        (6, "Korean PGx + niche", "Korean PGx panel, mitochondrial, CellChat, smartphone, OliX siRNA", "tab:purple"),
        (7, "Partnership scaffolds", "ExoCoBio, EZH2 epigenetic, NLRP3, Pro-Hyp, PBM LED", "tab:pink"),
        (8, "Reporting + HE", "TRIPOD-AI, SHAP/Grad-CAM, 동의보감 miner, D+Q senolytic, HIRA QALY", "tab:brown"),
        (9, "Diagnostic + Specialized", "facial_dx integration, PROTAC, chronotherapy, OCT, engineered probiotic, ESG", "lightcoral"),
        (10, "Safety + MLOps + KG", "hallucination guard, MLOps registry, KG completion, PA-EWC, multi-omics fusion", "skyblue"),
        (11, "Frontier / Strategic", "NaFM, Bayesian trial + DTx, KIPRIS+USPTO patent, SkinAge, Chai-1, JUMP-CP, MFDS K-bio", "navajowhite"),
    ]
    fig, ax = plt.subplots(figsize=(13, 8.5))
    ax.set_xlim(0, 12)
    ax.set_ylim(-0.5, len(tiers))
    ax.axis("off")

    for i, (n, name, modules, color) in enumerate(reversed(tiers)):
        y = i
        box = FancyBboxPatch((0.3, y - 0.4), 11.4, 0.85,
                              boxstyle="round,pad=0.02", linewidth=1.5,
                              edgecolor=color, facecolor=color, alpha=0.4)
        ax.add_patch(box)
        ax.text(1.0, y, f"Tier {n}", ha="center", va="center",
                 fontsize=11, fontweight="bold")
        ax.text(2.5, y + 0.13, name, ha="left", va="center",
                 fontsize=10, fontweight="bold")
        ax.text(2.5, y - 0.18, modules, ha="left", va="center", fontsize=7.5)
    ax.set_title("Genesis_Medicine 12-tier pipeline (50+ modules)\n"
                  "Apache-2.0 open-source · github.com/crazat/genesis_medicine",
                  fontsize=12, pad=20)
    out = fig_dir("12_open_source_perspective") / "fig1_12tier_overview.png"
    plt.savefig(out)
    plt.close()
    print(f"  ✅ {out}")


# ===========================================================================
# Main
# ===========================================================================

def main():
    print("\n=== Generating publication figures from real data ===\n")

    print("[Preprint #1] Embelia ribes review")
    fig_01_embelin_summary()

    print("\n[Preprint #2] Recover workflow")
    fig_02_three_pillar()
    fig_02_patient_workflow()

    print("\n[Preprint #3] EMB-3 case study")
    fig_03_emb3_structures()
    fig_03_sar_scatter()
    fig_03_round_progress()

    print("\n[Preprint #4] Pigmentation")
    fig_disease_heatmap("04_pigmentation_screening",
                          ROOT / "pilot/screen/pigmentation/screen_results.csv",
                          ["TYR", "TYRP1", "DCT"],
                          "Pigmentation screen — TYR + TYRP1 + DCT (real Boltz-2)")
    fig_disease_safety_quadrant("04_pigmentation_screening",
                                  ROOT / "pilot/screen/pigmentation/screen_results.csv",
                                  "Pigmentation screen — affinity × hERG safety")

    print("\n[Preprint #5] Alopecia")
    fig_disease_heatmap("05_alopecia_screening",
                          ROOT / "pilot/screen/alopecia/screen_results.csv",
                          ["SRD5A2", "AR", "CTNNB1"],
                          "Alopecia screen — SRD5A2 + AR + CTNNB1 (real Boltz-2)")
    fig_disease_safety_quadrant("05_alopecia_screening",
                                  ROOT / "pilot/screen/alopecia/screen_results.csv",
                                  "Alopecia screen — affinity × hERG safety")

    print("\n[Preprint #6] Acne")
    fig_disease_heatmap("06_acne_microbiome",
                          ROOT / "pilot/screen/acne/screen_results.csv",
                          ["AR", "SRD5A2"],
                          "Acne screen — SRD5A2 + AR (real Boltz-2; SREBP1 + C. acnes deferred)")
    fig_disease_safety_quadrant("06_acne_microbiome",
                                  ROOT / "pilot/screen/acne/screen_results.csv",
                                  "Acne screen — affinity × hERG safety (Berberine flag)")

    print("\n[Preprint #7] Photoaging")
    fig_disease_heatmap("07_photoaging_egcg",
                          ROOT / "pilot/screen/photoaging/screen_results.csv",
                          ["MMP1", "SIRT1"],
                          "Photoaging screen — MMP-1 + SIRT1 (real Boltz-2)")
    fig_disease_safety_quadrant("07_photoaging_egcg",
                                  ROOT / "pilot/screen/photoaging/screen_results.csv",
                                  "Photoaging screen — affinity × hERG safety")

    print("\n[Preprint #9] Cross-disease IPF")
    fig_09_emb3_target_profile()
    fig_09_target_to_disease()

    print("\n[Preprint #10] Chronotherapy 자오류주")
    fig_10_jaoryuju_clock()

    print("\n[Preprint #11] Korean PGx")
    fig_11_pgx_frequencies()

    print("\n[Preprint #12] Open-source perspective")
    fig_12_tier_overview()

    print("\n" + "=" * 50)
    print("✅ All figures generated.")
    n = sum(1 for _ in (PREPRINTS).rglob("figures/*.png"))
    print(f"   Total: {n} PNG figures across preprints/<num>/figures/")


if __name__ == "__main__":
    main()
