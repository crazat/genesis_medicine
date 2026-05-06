"""Generate figures 1-3 for paper #A (ZAFF-AMBER ABFE limitations).

Reads dG_bind.json from each compound's abfe_production_mss/ subdir and
the manifest for IC50/scaffold metadata, then emits:

  fig1_replicate_scatter.png   per-compound replicate values vs experiment
  fig2_repdisp_vs_accuracy.png Δrep (max replicate dispersion) vs
                                |mean(rep) − dG_exp|; the headline plot
                                showing reproducibility decoupled from
                                accuracy
  fig3_potency_residuals.png   residual = mean(rep) − dG_exp vs pIC50,
                                error bars = std across replicates,
                                shaded chemical-accuracy band ±2 kcal/mol

All artifacts go to preprints/paper_A_zaff_abfe_limitations/figures/.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path("/home/crazat/genesis_medicine")
BASE = ROOT / "pilot/abfe_benchmark_chembl"
OUT = ROOT / "preprints/paper_A_zaff_abfe_limitations/figures"
OUT.mkdir(parents=True, exist_ok=True)

# --- short labels for the seven benchmark compounds ---
SHORT = {
    "CHEMBL415":     "Batimastat",
    "CHEMBL443684":  "Marimastat",
    "CHEMBL94487":   "RS-130830",
    "CHEMBL257077":  "prinomastat-l",
    "CHEMBL301236":  "fluoro-aryl HX",
    "CHEMBL292707":  "Ilomastat",
    "CHEMBL2105729": "weak ctrl",
}
# scaffold class for color coding
CLASS = {
    "CHEMBL415":     "hydroxamate",
    "CHEMBL443684":  "hydroxamate",
    "CHEMBL94487":   "hydroxamate",
    "CHEMBL257077":  "hydroxamate",
    "CHEMBL301236":  "sulfonamide-HX",
    "CHEMBL292707":  "hydroxamate",
    "CHEMBL2105729": "hydroxamate",
}
CLASS_COLOR = {
    "hydroxamate":     "#1f77b4",
    "sulfonamide-HX":  "#d62728",
    "carboxylate":     "#2ca02c",
    "thiol":           "#ff7f0e",
}


def load_results():
    """Return dict[chembl_id] = {rep1: dG, rep2: dG, rep3: dG, ic50_nm: ..., dG_exp: ...}."""
    manifest = json.loads((BASE / "manifest.json").read_text())
    exp = {c["chembl_id"]: c for c in manifest["compounds"]}
    out = {}
    for d in sorted(BASE.iterdir()):
        if not d.is_dir() or not d.name.startswith("CHEMBL"):
            continue
        if "_rep" in d.name:
            cid, rep_n = d.name.rsplit("_rep", 1)
            rep_label = f"rep{rep_n}"
        else:
            cid, rep_label = d.name, "rep1"
        if cid not in SHORT:
            continue
        dg_path = d / "abfe_production_mss" / "dG_bind.json"
        if not dg_path.exists():
            continue
        try:
            data = json.loads(dg_path.read_text())
        except Exception:
            continue
        if cid not in out:
            ic50 = exp[cid]["ic50_nm"]
            dG_exp = 0.616 * math.log(ic50 * 1e-9)
            out[cid] = {"ic50_nm": ic50, "dG_exp": dG_exp,
                        "pIC50": -math.log10(ic50 * 1e-9), "reps": {}}
        out[cid]["reps"][rep_label] = (data.get("dG_bind_kcal_mol"),
                                       data.get("dG_bind_err_kcal_mol", 0.0))
    return out


def fig1_replicate_scatter(R: dict):
    """Per-compound horizontal layout: each row a compound, replicates as dots,
    experimental dG_exp as vertical green tick. x-axis: dG (kcal/mol)."""
    cids = sorted(R, key=lambda c: R[c]["dG_exp"])  # most negative (strongest) first
    fig, ax = plt.subplots(figsize=(8, 4.5))
    rep_markers = {"rep1": "o", "rep2": "s", "rep3": "^"}
    for i, cid in enumerate(cids):
        y = i
        d = R[cid]
        ax.axvline(d["dG_exp"], ymin=(i - 0.3) / len(cids), ymax=(i + 0.3) / len(cids),
                   color="tab:green", alpha=0)
        ax.plot([d["dG_exp"]], [y], marker="|", color="tab:green",
                markersize=18, mew=2.5, label="$\\Delta G_{\\mathrm{exp}}$" if i == 0 else "")
        for rep_label in ("rep1", "rep2", "rep3"):
            if rep_label in d["reps"]:
                val, err = d["reps"][rep_label]
                if val is None:
                    continue
                ax.errorbar([val], [y], xerr=[err], fmt=rep_markers[rep_label],
                            color=CLASS_COLOR.get(CLASS[cid], "gray"),
                            ecolor="black", alpha=0.85, capsize=3,
                            label=rep_label if i == 0 else "")
        # mean
        vals = [v for v, _ in d["reps"].values() if v is not None]
        if len(vals) >= 2:
            ax.plot([np.mean(vals)], [y], marker="D", color="black",
                    markersize=8, mfc="none", mew=1.6,
                    label=r"$\langle\Delta G\rangle$" if i == 0 else "")
    ax.set_yticks(range(len(cids)))
    ax.set_yticklabels([f"{SHORT[c]} ({R[c]['ic50_nm']:.0f} nM)" for c in cids])
    ax.set_xlabel(r"$\Delta G_{\mathrm{bind}}$ (kcal mol$^{-1}$)")
    ax.set_xlim(-25, 12)
    ax.axvspan(-2, 2, color="tab:gray", alpha=0.08)  # near-zero band
    ax.axvline(0, color="gray", lw=0.6, alpha=0.5)
    ax.grid(axis="x", alpha=0.3)
    ax.legend(loc="lower right", fontsize=8, ncol=2, frameon=True)
    ax.set_title("ABFE replicate values vs experimental binding free energy")
    fig.tight_layout()
    fig.savefig(OUT / "fig1_replicate_scatter.png", dpi=200)
    plt.close(fig)
    print(f"  wrote {OUT / 'fig1_replicate_scatter.png'}")


def fig2_repdisp_vs_accuracy(R: dict):
    """Headline: replicate dispersion (max - min) on x, |mean - exp| on y."""
    cids = sorted(R, key=lambda c: R[c]["dG_exp"])
    xs, ys, labels, colors = [], [], [], []
    for cid in cids:
        d = R[cid]
        vals = [v for v, _ in d["reps"].values() if v is not None]
        if len(vals) < 2:
            # Single rep — plot only an arrow?  Skip for clarity.
            continue
        delta_rep = max(vals) - min(vals)
        delta_exp = abs(np.mean(vals) - d["dG_exp"])
        xs.append(delta_rep)
        ys.append(delta_exp)
        labels.append(SHORT[cid])
        colors.append(CLASS_COLOR.get(CLASS[cid], "gray"))

    fig, ax = plt.subplots(figsize=(7, 5))
    for x, y, lbl, c in zip(xs, ys, labels, colors):
        ax.scatter(x, y, color=c, s=110, edgecolor="black", lw=0.8, zorder=3)
        ax.annotate(lbl, (x, y), xytext=(7, 5), textcoords="offset points",
                    fontsize=9)
    # diagonal reference: where Δrep == ΔdGexp
    lim = max(max(xs), max(ys)) * 1.15
    ax.plot([0, lim], [0, lim], "k--", lw=0.7, alpha=0.5,
            label=r"$|\Delta_{\mathrm{exp}}| = \Delta_{\mathrm{rep}}$")
    ax.axhline(2, color="tab:green", lw=0.7, alpha=0.6,
               label=r"chemical-accuracy band ($\pm$ 2 kcal mol$^{-1}$)")
    ax.axhspan(0, 2, color="tab:green", alpha=0.06)
    ax.set_xlabel(r"replicate dispersion $\Delta_{\mathrm{rep}}$ "
                  r"(kcal mol$^{-1}$)")
    ax.set_ylabel(r"accuracy gap $|\langle\Delta G\rangle - \Delta G_{\mathrm{exp}}|$ "
                  r"(kcal mol$^{-1}$)")
    ax.set_xlim(0, lim)
    ax.set_ylim(0, lim)
    ax.set_title("Reproducibility is decoupled from accuracy")
    ax.grid(alpha=0.3)
    ax.legend(loc="upper left", fontsize=9)
    fig.tight_layout()
    fig.savefig(OUT / "fig2_repdisp_vs_accuracy.png", dpi=200)
    plt.close(fig)
    print(f"  wrote {OUT / 'fig2_repdisp_vs_accuracy.png'}")


def fig3_potency_residuals(R: dict):
    """Residual = mean(rep) - dG_exp on y, pIC50 on x, error bars = std."""
    cids = sorted(R, key=lambda c: R[c]["pIC50"], reverse=True)
    xs, ys, errs, labels, colors = [], [], [], [], []
    for cid in cids:
        d = R[cid]
        vals = [v for v, _ in d["reps"].values() if v is not None]
        if not vals:
            continue
        mean = np.mean(vals)
        std = np.std(vals, ddof=0) if len(vals) >= 2 else 0.0
        xs.append(d["pIC50"])
        ys.append(mean - d["dG_exp"])
        errs.append(std)
        labels.append(SHORT[cid])
        colors.append(CLASS_COLOR.get(CLASS[cid], "gray"))

    fig, ax = plt.subplots(figsize=(7.5, 5))
    for x, y, e, lbl, c in zip(xs, ys, errs, labels, colors):
        ax.errorbar(x, y, yerr=e, fmt="o", color=c, ecolor="black",
                    capsize=4, markersize=10, mec="black", mew=0.7)
        ax.annotate(lbl, (x, y), xytext=(7, 5), textcoords="offset points",
                    fontsize=9)
    ax.axhline(0, color="tab:green", lw=1.2, label=r"$\Delta G_{\mathrm{exp}}$ (perfect)")
    ax.axhspan(-2, 2, color="tab:green", alpha=0.10,
               label=r"chemical-accuracy band ($\pm$ 2 kcal mol$^{-1}$)")
    ax.set_xlabel("pIC$_{50}$ (= -log$_{10}$ IC$_{50,\\mathrm{M}}$)")
    ax.set_ylabel(r"residual $\langle\Delta G\rangle - \Delta G_{\mathrm{exp}}$ "
                  r"(kcal mol$^{-1}$)")
    ax.set_title("ABFE residual vs experimental potency")
    ax.grid(alpha=0.3)
    ax.invert_xaxis()  # strongest binders on the left, weakest right
    ax.legend(loc="upper right", fontsize=9)
    fig.tight_layout()
    fig.savefig(OUT / "fig3_potency_residuals.png", dpi=200)
    plt.close(fig)
    print(f"  wrote {OUT / 'fig3_potency_residuals.png'}")


def main():
    R = load_results()
    print(f"loaded {len(R)} compounds")
    for cid, d in R.items():
        print(f"  {cid}: reps={list(d['reps'].keys())} dG_exp={d['dG_exp']:+.2f}")
    fig1_replicate_scatter(R)
    fig2_repdisp_vs_accuracy(R)
    fig3_potency_residuals(R)


if __name__ == "__main__":
    main()
