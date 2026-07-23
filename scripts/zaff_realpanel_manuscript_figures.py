#!/usr/bin/env python3
"""paper_A_zaff finalization: warhead classification (SMARTS, data-derived — NOT remembered),
live re-computation of accuracy stats, and manuscript figures, all from the REAL 14-compound panel.
Inputs:  pilot/abfe_realpanel_mmp1/abfe_realpanel_results.csv (+ abfe_subset.csv for SMILES,
         data/mmp1_panel_pubchem.csv for formula)
Outputs: manuscript figures (fig_accuracy_scatter.png, fig_potency_residual.png) +
         a printed table/classification/stats block for the manuscript text.
Every number the manuscript cites is recomputed here from the CSVs; nothing is hand-transcribed.
"""
import csv, math, json
from pathlib import Path

GM = Path("/home/crazat/genesis_medicine")
D = GM / "pilot/abfe_realpanel_mmp1"
FIGDIR = GM / "preprints/paper_A_zaff_abfe_limitations/figures"
FIGDIR.mkdir(parents=True, exist_ok=True)

# --- load results + smiles + formula ---
res = {}
with open(D / "abfe_realpanel_results.csv") as f:
    for row in csv.DictReader(f):
        res[row["cid"]] = row
smi = {}
with open(D / "abfe_subset.csv") as f:
    for row in csv.DictReader(f):
        smi[row["cid"]] = row["smiles"]
formula = {}
with open(GM / "data/mmp1_panel_pubchem.csv") as f:
    for row in csv.DictReader(f):
        formula["cid" + row["pubchem_cid"].strip()] = row["formula"]

# --- warhead classification via RDKit SMARTS (data-derived) ---
from rdkit import Chem
WARHEADS = [
    ("hydroxamate", "[CX3](=[OX1])[NX3][OX2H1,OX1-]"),
    ("carboxylate", "[CX3](=[OX1])[OX2H1,OX1-]"),
    ("sulfonamide", "[SX4](=[OX1])(=[OX1])[NX3]"),
    ("sulfonate",   "[SX4](=[OX1])(=[OX1])[OX2H1,OX1-]"),
    ("thiol",       "[SX2H,SX1-]"),
    ("phosphonate", "[PX4](=[OX1])([OX2H1,OX1-])[OX2H1,OX1-]"),
]
patts = [(n, Chem.MolFromSmarts(s)) for n, s in WARHEADS]

def classify(sml):
    m = Chem.MolFromSmiles(sml)
    if m is None:
        return "unparsed"
    hits = [n for n, p in patts if p is not None and m.HasSubstructMatch(p)]
    # priority: hydroxamate/thiol are strong Zn chelators; report the strongest chelator present
    for strong in ("hydroxamate", "thiol", "phosphonate"):
        if strong in hits:
            return strong
    return hits[0] if hits else "other"

rows = []
for cid, r in res.items():
    rows.append({
        "cid": cid,
        "formula": formula.get(cid, "?"),
        "warhead": classify(smi[cid]),
        "ic50_nm": float(r["ic50_nm"]),
        "pIC50": float(r["pIC50"]),
        "dGexp": float(r["dG_exp"]),
        "dGabfe": float(r["dG_abfe"]),
        "err": float(r["dG_abfe_err"]),
        "dev": float(r["dev"]),
    })
rows.sort(key=lambda x: x["ic50_nm"])

# --- live stats recompute (do not trust summary.json blindly) ---
def spearman(a, b):
    def rank(x):
        order = sorted(range(len(x)), key=lambda i: x[i])
        rr = [0]*len(x)
        i = 0
        while i < len(x):
            j = i
            while j+1 < len(x) and x[order[j+1]] == x[order[i]]:
                j += 1
            avg = (i+j)/2.0 + 1
            for k in range(i, j+1):
                rr[order[k]] = avg
            i = j+1
        return rr
    ra, rb = rank(a), rank(b)
    return pearson(ra, rb)

def pearson(a, b):
    n = len(a); ma = sum(a)/n; mb = sum(b)/n
    cov = sum((x-ma)*(y-mb) for x, y in zip(a, b))
    va = math.sqrt(sum((x-ma)**2 for x in a)); vb = math.sqrt(sum((y-mb)**2 for y in b))
    return cov/(va*vb) if va*vb else float("nan")

dGexp = [r["dGexp"] for r in rows]
dGabfe = [r["dGabfe"] for r in rows]
rho = spearman(dGabfe, dGexp)
r_p = pearson(dGabfe, dGexp)
sign_flips = sum(1 for r in rows if (r["dGabfe"] > 0))  # exp always <0 (all bind); flip = predicted non-binding
over = [r for r in rows if r["dev"] < 0]

def strata(rows):
    strong = [r for r in rows if r["ic50_nm"] <= 10]
    mid = [r for r in rows if 10 < r["ic50_nm"] <= 10000]
    weak = [r for r in rows if r["ic50_nm"] > 10000]
    def mdev(g): return (len(g), (sum(x["dev"] for x in g)/len(g)) if g else float("nan"))
    return {"strong(<=10nM)": mdev(strong), "mid(10nM-10uM)": mdev(mid), "weak(>10uM)": mdev(weak)}

# --- figures ---
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

wcolors = {"hydroxamate": "#c0392b", "sulfonamide": "#2980b9", "carboxylate": "#27ae60",
           "thiol": "#8e44ad", "sulfonate": "#16a085", "phosphonate": "#d35400",
           "other": "#7f8c8d", "unparsed": "#000000"}

# fig1: dG_abfe vs dG_exp
fig, ax = plt.subplots(figsize=(5.2, 5.0))
for r in rows:
    ax.errorbar(r["dGexp"], r["dGabfe"], yerr=r["err"], fmt="o", ms=6,
                color=wcolors.get(r["warhead"], "#7f8c8d"), ecolor="#999", capsize=2, zorder=3)
lo, hi = -14, 5
ax.plot([lo, hi], [lo, hi], "--", color="#444", lw=1, label="y = x (perfect accuracy)")
ax.axhline(0, color="#bbb", lw=0.6); ax.axvline(0, color="#bbb", lw=0.6)
ax.set_xlim(lo, hi); ax.set_ylim(-75, hi)
ax.set_xlabel(r"$\Delta G_{\mathrm{exp}}$  (kcal mol$^{-1}$, from IC$_{50}$)")
ax.set_ylabel(r"$\Delta G_{\mathrm{ABFE}}$  (kcal mol$^{-1}$)")
ax.set_title("ZAFF-AMBER ABFE vs experiment (n=14, MMP-1)")
handles = [plt.Line2D([0],[0], marker="o", ls="", color=wcolors[w],
           label=w) for w in sorted(set(r["warhead"] for r in rows))]
handles.append(plt.Line2D([0],[0], ls="--", color="#444", label="y = x"))
ax.legend(handles=handles, fontsize=7, loc="lower left", framealpha=0.9)
fig.tight_layout(); fig.savefig(FIGDIR / "fig_accuracy_scatter.png", dpi=200); plt.close(fig)

# fig2: residual vs pIC50
fig, ax = plt.subplots(figsize=(5.6, 4.4))
for r in rows:
    ax.scatter(r["pIC50"], r["dev"], s=48, color=wcolors.get(r["warhead"], "#7f8c8d"), zorder=3, edgecolor="#333", lw=0.4)
ax.axhline(0, color="#444", lw=1)
ax.axhspan(-2, 2, color="#2ecc71", alpha=0.15, label=r"$\pm 2$ kcal mol$^{-1}$ (chemical accuracy)")
ax.set_xlabel(r"experimental potency  pIC$_{50}$  (strong $\rightarrow$)")
ax.set_ylabel(r"ABFE residual  $\Delta G_{\mathrm{ABFE}}-\Delta G_{\mathrm{exp}}$  (kcal mol$^{-1}$)")
ax.set_title("Over-binding is warhead-driven, not potency-ranked")
# annotate the weak strong-chelator outlier
for r in rows:
    if r["cid"] == "cid10303333":
        ax.annotate("cid10303333\n(50 uM, strong chelator)", (r["pIC50"], r["dev"]),
                    fontsize=6.5, xytext=(r["pIC50"]+0.2, r["dev"]+6),
                    arrowprops=dict(arrowstyle="->", color="#555", lw=0.7))
ax.invert_xaxis()
ax.legend(fontsize=7, loc="lower right")
fig.tight_layout(); fig.savefig(FIGDIR / "fig_potency_residual.png", dpi=200); plt.close(fig)

# --- print manuscript-ready block ---
print("=== WARHEAD CLASSIFICATION + DATA (IC50-sorted) ===")
print(f"{'cid':12} {'formula':12} {'warhead':12} {'IC50_nM':>9} {'pIC50':>5} {'dGexp':>7} {'dGabfe':>8} {'err':>5} {'dev':>7}")
for r in rows:
    print(f"{r['cid']:12} {r['formula']:12} {r['warhead']:12} {r['ic50_nm']:>9.2f} {r['pIC50']:>5.2f} {r['dGexp']:>7.2f} {r['dGabfe']:>8.2f} {r['err']:>5.2f} {r['dev']:>7.2f}")
print()
print("=== LIVE-RECOMPUTED STATS (compare to summary.json) ===")
print(f"  n = {len(rows)}")
print(f"  Spearman(dGabfe,dGexp) = {rho:+.3f}")
print(f"  Pearson(dGabfe,dGexp)  = {r_p:+.3f}")
print(f"  sign_flips (dGabfe>0)  = {sign_flips}")
print(f"  all over-bind (dev<0)  = {len(over)}/{len(rows)}")
print(f"  dev range = {min(r['dev'] for r in rows):+.1f} .. {max(r['dev'] for r in rows):+.1f}")
print(f"  strata mean dev = {json.dumps(strata(rows))}")
print()
print("=== warhead counts ===")
from collections import Counter
print(" ", dict(Counter(r["warhead"] for r in rows)))
print()
print("=== compare to summary.json ===")
s = json.load(open(D / "abfe_realpanel_summary.json"))
print(" ", {k: s[k] for k in ("spearman", "pearson", "sign_flips", "n_complete", "strata") if k in s})
print("figures ->", FIGDIR)
