"""Target sequence similarity matrix — 14 disease targets cross-comparison.

Uses BLAST-style sequence identity to identify cross-target binding risk
(e.g. AR vs GR vs MR ~50% identity → off-target risk for steroid receptors).
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_meaningful"
FIG_DIR = OUT / "figures_r13"


def seq_identity(s1, s2):
    """Simple alignment-free identity via k-mer overlap."""
    s1 = s1.upper()
    s2 = s2.upper()
    k = 5
    set1 = set(s1[i:i+k] for i in range(len(s1) - k + 1))
    set2 = set(s2[i:i+k] for i in range(len(s2) - k + 1))
    return len(set1 & set2) / max(len(set1 | set2), 1)


def main():
    print("=" * 72)
    print("Target sequence similarity matrix")
    print("=" * 72)

    import yaml
    targets = {}
    for yaml_path in (ROOT / "pilot/cpu_meaningful").rglob("inputs_*/[a-z]*.yaml"):
        try:
            with open(yaml_path) as f:
                data = yaml.safe_load(f)
            target_name = yaml_path.parent.name.replace("inputs_", "")
            for s in data.get("sequences", []):
                if "protein" in s and target_name not in targets:
                    seq = s["protein"]
                    if isinstance(seq, dict):
                        seq = seq.get("sequence", "")
                    if isinstance(seq, str) and len(seq) > 50:
                        targets[target_name] = seq
                        break
        except Exception:
            continue

    # Add additional targets from scaffold_hop yamls
    for yaml_path in (ROOT / "pilot/scaffold_hop").rglob("*.yaml"):
        try:
            with open(yaml_path) as f:
                data = yaml.safe_load(f)
            stem = yaml_path.stem
            if "__" in stem:
                target_name = stem.split("__")[0]
            else:
                target_name = stem
            if target_name in targets:
                continue
            for s in data.get("sequences", []):
                if "protein" in s:
                    seq = s["protein"]
                    if isinstance(seq, dict):
                        seq = seq.get("sequence", "")
                    if isinstance(seq, str) and len(seq) > 50:
                        targets[target_name] = seq
                        break
        except Exception:
            continue

    print(f"Targets found: {len(targets)}")
    print(f"  {list(targets.keys())}")

    if len(targets) < 2:
        print("⚠️ Insufficient targets — exiting")
        return 1

    target_names = sorted(targets.keys())
    n = len(target_names)
    matrix = np.zeros((n, n))
    for i, ti in enumerate(target_names):
        for j, tj in enumerate(target_names):
            if i <= j:
                matrix[i, j] = seq_identity(targets[ti], targets[tj])
                matrix[j, i] = matrix[i, j]

    df = pd.DataFrame(matrix, index=target_names, columns=target_names)
    df.to_csv(OUT / "target_sequence_similarity.csv")
    print(f"\n✅ target_sequence_similarity.csv ({n}×{n})")

    # Plot
    fig, ax = plt.subplots(figsize=(12, 10))
    im = ax.imshow(matrix, cmap="RdYlGn_r", vmin=0, vmax=1, aspect="auto")
    ax.set_xticks(range(n))
    ax.set_yticks(range(n))
    ax.set_xticklabels(target_names, rotation=45, ha="right", fontsize=10)
    ax.set_yticklabels(target_names, fontsize=10)
    for i in range(n):
        for j in range(n):
            ax.text(j, i, f"{matrix[i, j]:.2f}", ha="center", va="center",
                     fontsize=8, color="white" if matrix[i, j] > 0.5 else "black")
    ax.set_title(f"Target sequence similarity matrix — k-mer (k=5) Jaccard\n"
                  f"({n} skin disease + ABFE-validated targets)",
                  fontsize=12, weight="bold")
    plt.colorbar(im, ax=ax, label="Sequence similarity (Jaccard k-mer)")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "target_similarity_matrix.png", dpi=300, bbox_inches="tight")
    plt.close()
    print(f"✅ figures_r13/target_similarity_matrix.png")

    # High-similarity pairs (off-target risk)
    high_pairs = []
    for i in range(n):
        for j in range(i + 1, n):
            if matrix[i, j] > 0.4:
                high_pairs.append({
                    "t1": target_names[i],
                    "t2": target_names[j],
                    "similarity": float(matrix[i, j]),
                })
    high_df = pd.DataFrame(high_pairs).sort_values("similarity", ascending=False)
    high_df.to_csv(OUT / "target_high_similarity_pairs.csv", index=False)
    print(f"\n[Off-target risk pairs (sim > 0.4)]")
    for _, r in high_df.head(10).iterrows():
        print(f"  {r['t1']:8s} × {r['t2']:8s}  sim={r['similarity']:.3f}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
