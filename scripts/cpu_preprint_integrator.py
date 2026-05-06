"""Preprint integrator: append Round 12 paper-tier integration section to
relevant preprints with new top candidates + figures + scaffold safety profile.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PREPRINTS = ROOT / "preprints"
OUT_DIR = ROOT / "pilot/cpu_meaningful"


TARGET_TO_PREPRINT = {
    "mmp1": "03_emb3_scar_case_study",
    "ctgf": "03_emb3_scar_case_study",
    "tgfb1": "03_emb3_scar_case_study",
    "lox": "07_photoaging_egcg",
    "sirt1": "07_photoaging_egcg",
    "tyr": "04_pigmentation_screening",
    "dct": "04_pigmentation_screening",
    "tyrp1": "04_pigmentation_screening",
    "mitf": "04_pigmentation_screening",
    "ar": "05_alopecia_screening",
    "srd5a2": "05_alopecia_screening",
    "ctnnb1": "05_alopecia_screening",
    "ptgs2": "06_acne_microbiome",
    "jun": "07_photoaging_egcg",
}


def render_section(target: str, top: pd.DataFrame, scaffold_safety: pd.DataFrame) -> str:
    """Render a per-target Round 12 section."""
    lines = [
        f"\n## R12 §3.{target.upper()} — Integrated paper-tier ranking",
        "",
        "### Method",
        "Top 100 BRICS-derived candidates were cofolded with Boltz-2",
        "(n=1109 total cofolds, ipTM ≥ 0.7 in 32%) and scored by integrated",
        "paper-tier metric:",
        "",
        "$$\\text{score} = 0.5 \\cdot P(\\text{binder}) + 0.3 \\cdot S - 0.2 \\cdot (1 - N)$$",
        "",
        "where $P$ = Boltz-2 affinity probability, $S$ = composite ADMET safety",
        "$(1 - hERG, 1 - AMES, 1 - Skin\\_Reaction)$, $N$ = Tanimoto novelty",
        "$(1 - \\max\\_Tanimoto)$ vs ChEMBL+DrugBank reference.",
        "",
        f"### Top candidates for {target.upper()}",
        "",
        "| Rank | Compound | Affinity prob. | Safety | Score | SMILES |",
        "|---|---|---|---|---|---|",
    ]

    sub = top[top["target"] == target].head(10)
    for i, (_, r) in enumerate(sub.iterrows(), 1):
        smi = r.get("smiles", "")
        lines.append(
            f"| {i} | {r['compound']} | "
            f"{r.get('affinity_prob_binary', 0):.3f} | "
            f"{r.get('safety_score', 0):.3f} | "
            f"{r.get('paper_tier_score', 0):.3f} | "
            f"`{smi[:50]}{'...' if len(smi) > 50 else ''}` |"
        )

    if len(scaffold_safety) > 0:
        lines.extend([
            "",
            "### Scaffold safety profile (top 5 safest, n ≥ 5)",
            "",
            "| Murcko scaffold | n | logP | hERG | Skin |",
            "|---|---|---|---|---|",
        ])
        for sc, row in scaffold_safety.head(5).iterrows():
            sc_disp = sc[:60] + "..." if len(sc) > 60 else sc
            lines.append(
                f"| `{sc_disp}` | {int(row['n_mol'])} | "
                f"{row['logP']:.2f} | {row['hERG']:.3f} | {row['Skin_Reaction']:.3f} |"
            )

    lines.extend([
        "",
        "### Limitations",
        f"- Boltz-2 affinity_probability_binary is a binary classifier, NOT pIC50.",
        f"  Wet-lab IC50 measurement required for clinical interpretation.",
        f"- ADMET-AI v2 prediction confidence is endpoint-dependent; hERG/AMES",
        f"  validated against ChEMBL but skin permeation logKp uses limited training.",
        f"- Murcko scaffold analysis ignores stereochemistry and 3D conformation.",
        f"- Top candidates require PoseBusters geometric validation (in progress).",
        "",
    ])
    return "\n".join(lines)


def main():
    top = pd.read_csv(OUT_DIR / "integrated_top_candidates_per_target.csv")
    print(f"Top candidates: {len(top)} rows, targets: {top['target'].unique()}")

    sc_safety_path = OUT_DIR / "scaffold_safety_profile.csv"
    scaffold_safety = pd.read_csv(sc_safety_path).set_index("murcko") if sc_safety_path.exists() else pd.DataFrame()

    n_appended = 0
    for target in top["target"].unique():
        preprint_dir_name = TARGET_TO_PREPRINT.get(target)
        if not preprint_dir_name:
            print(f"  no preprint mapping for {target} → skip")
            continue

        preprint_md = PREPRINTS / preprint_dir_name / "manuscript.md"
        if not preprint_md.exists():
            print(f"  preprint missing: {preprint_md}")
            continue

        section = render_section(target, top, scaffold_safety)
        # Append to a "## R12 paper-tier" section (idempotent: replace existing)
        existing = preprint_md.read_text(encoding="utf-8")
        marker = f"## R12 §3.{target.upper()} — Integrated paper-tier ranking"
        if marker in existing:
            # Find and replace existing section
            start = existing.index(marker)
            # Find next section header at same level OR EOF
            next_hash = existing.find("\n## ", start + len(marker))
            if next_hash == -1:
                end = len(existing)
            else:
                end = next_hash
            existing = existing[:start] + section.lstrip() + "\n" + existing[end:]
        else:
            existing += "\n" + section
        preprint_md.write_text(existing, encoding="utf-8")
        n_appended += 1
        print(f"  ✅ {preprint_dir_name}/manuscript.md: appended {target} section")

    print(f"\nIntegration complete: {n_appended} preprints updated")


if __name__ == "__main__":
    sys.exit(main())
