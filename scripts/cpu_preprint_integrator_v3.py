"""Preprint integrator v3 — inject Open Targets reverse evidence into preprints."""
import sys
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PREPRINTS = ROOT / "preprints"
OUT = ROOT / "pilot/cpu_meaningful"


TARGET_TO_PREPRINT = {
    "ar": "05_alopecia_screening",
    "srd5a2": "05_alopecia_screening",
    "mmp1": "03_emb3_scar_case_study",
    "ctgf": "03_emb3_scar_case_study",
    "tgfb1": "03_emb3_scar_case_study",
    "tyr": "04_pigmentation_screening",
    "tyrp1": "04_pigmentation_screening",
    "mitf": "04_pigmentation_screening",
    "dct": "04_pigmentation_screening",
    "ptgs2": "06_acne_microbiome",
    "jun": "07_photoaging_egcg",
    "sirt1": "07_photoaging_egcg",
    "lox": "07_photoaging_egcg",
    "pdgfrb": "09_cross_disease_ipf",
}


def main():
    ot = pd.read_csv(OUT / "open_targets_reverse.csv")
    print(f"OT rows: {len(ot)}")

    sections_per_preprint: dict[str, list] = {}
    for tgt, sub in ot.groupby("target"):
        pp = TARGET_TO_PREPRINT.get(tgt)
        if not pp:
            continue
        sections_per_preprint.setdefault(pp, []).append((tgt, sub))

    for pp, items in sections_per_preprint.items():
        path = PREPRINTS / pp / "manuscript.md"
        if not path.exists():
            print(f"  missing: {path}")
            continue

        section_lines = ["", "## R12 §5 — Open Targets reverse evidence", "",
                          "External validation via Open Targets Platform "
                          "(api.platform.opentargets.org/v4) reverse association",
                          "queries for skin-relevant diseases:", "",
                          "| Target | Disease | OT score |",
                          "|---|---|---|"]
        for tgt, sub in items:
            skin = sub[sub["category"] == "skin"]
            for _, r in skin.iterrows():
                section_lines.append(
                    f"| {r['approved_symbol']} | {r['disease']} | {r['ot_score']:.3f} |"
                )

        section_lines.extend([
            "",
            "These scores represent disease-target associations integrated",
            "from genetic association, pathway, drug, RNA expression, and",
            "animal model evidence streams in the Open Targets Platform.",
            "",
        ])
        section = "\n".join(section_lines)

        existing = path.read_text(encoding="utf-8")
        marker = "## R12 §5 — Open Targets reverse evidence"
        if marker in existing:
            start = existing.index(marker)
            next_h = existing.find("\n## ", start + len(marker))
            end = next_h if next_h != -1 else len(existing)
            existing = existing[:start] + section.lstrip() + "\n" + existing[end:]
        else:
            existing += "\n" + section
        path.write_text(existing, encoding="utf-8")
        print(f"  ✅ {pp}/manuscript.md updated with §5 OT evidence ({len(items)} targets)")


if __name__ == "__main__":
    sys.exit(main())
