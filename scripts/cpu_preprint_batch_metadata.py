"""Generate preprint upload metadata for 12+2 papers (Option A — immediate upload).

Output:
  - preprints/_metadata/<NN>_metadata.json
  - preprints/_metadata/upload_plan.csv
  - docs/PREPRINT_UPLOAD_GUIDE.md (updated with current state)
"""
from __future__ import annotations
import json, sys, re
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "preprints/_metadata"
OUT.mkdir(parents=True, exist_ok=True)

# Server assignment per paper (chemistry / biology / clinical)
PAPERS = [
    ("01_embelia_ribes_review", "ChemRxiv", ["chemistry", "natural products", "ethnobotany"]),
    ("02_recover_workflow", "medRxiv", ["medical informatics", "AI", "drug discovery"]),
    ("03_emb3_scar_case_study", "ChemRxiv", ["medicinal chemistry", "scaffold-hopping", "AI"]),
    ("04_pigmentation_screening", "bioRxiv", ["pharmacology", "skin", "AI"]),
    ("05_alopecia_screening", "bioRxiv", ["pharmacology", "skin", "AI"]),
    ("06_acne_microbiome", "bioRxiv", ["microbiology", "skin", "AI"]),
    ("07_photoaging_egcg", "bioRxiv", ["pharmacology", "skin aging", "EGCG"]),
    ("08_abfe_methodology", "ChemRxiv", ["computational chemistry", "FEP", "ABFE"]),
    ("09_cross_disease_ipf", "bioRxiv", ["systems biology", "fibrosis", "IPF"]),
    ("10_chronotherapy_jaoryuju", "bioRxiv", ["chronobiology", "traditional medicine"]),
    ("11_korean_pgx_topical", "medRxiv", ["pharmacogenomics", "Korean medicine"]),
    ("12_open_source_perspective", "ChemRxiv", ["open science", "drug discovery", "AI"]),
    ("13_piezo1_mlck_alopecia", "bioRxiv", ["pharmacology", "alopecia", "mechanotransduction"]),
    ("14_topical_pbpk_methodology", "ChemRxiv", ["pharmacokinetics", "topical", "PBPK"]),
]


def extract_title(md_path: Path) -> str:
    if not md_path.exists():
        return ""
    text = md_path.read_text()
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return ""


def extract_abstract(md_path: Path) -> str:
    if not md_path.exists():
        return ""
    text = md_path.read_text()
    m = re.search(r"##\s*Abstract.*?\n+(.*?)(?=\n##|\n---|\Z)",
                   text, re.DOTALL | re.IGNORECASE)
    if m:
        ab = m.group(1).strip()
        ab = re.sub(r"\*\*", "", ab)
        ab = ab.replace("\n\n", " ").replace("\n", " ")
        return ab[:2500]
    return ""


def main():
    plan_rows = []
    for paper_dir, server, keywords in PAPERS:
        md_path = ROOT / "preprints" / paper_dir / "manuscript.md"
        pdf_path = ROOT / "preprints" / paper_dir / "manuscript.pdf"
        title = extract_title(md_path)
        abstract = extract_abstract(md_path)
        figures = list((ROOT / "preprints" / paper_dir / "figures").glob("*.png"))
        word_count = len(md_path.read_text().split()) if md_path.exists() else 0

        meta = {
            "paper_id": paper_dir,
            "title": title,
            "abstract": abstract,
            "keywords": keywords,
            "target_server": server,
            "authors": [{
                "name": "HanCheongWoo",
                "affiliations": [
                    "Genesis_Medicine Lab, Seoul, Republic of Korea",
                    "HAN PREDICT, Inc. (hanpredict.com)",
                    "Recover Korean Medicine Clinic (recover-clinic.kr)",
                ],
                "orcid": "<USER_FILL_ORCID_iD>",
                "email": "admin@hanpredict.com",
                "corresponding": True,
            }],
            "license": "CC-BY 4.0",
            "code_url": "https://github.com/crazat/genesis_medicine",
            "category": keywords[0] if keywords else "drug discovery",
            "subcategory": keywords[1] if len(keywords) > 1 else None,
            "manuscript_path": str(md_path.relative_to(ROOT)),
            "pdf_path": str(pdf_path.relative_to(ROOT)) if pdf_path.exists() else None,
            "n_figures": len(figures),
            "word_count_md": word_count,
            "disclaimer": ("In silico only. No clinical claim. "
                            "Wet-lab and IRB pending."),
            "funding": "Self-funded by HAN PREDICT, Inc.",
            "competing_interests": ("Author is founder of HAN PREDICT, Inc. and "
                                      "operator of Recover Korean Medicine Clinic. "
                                      "No commercial product is sold based on these results."),
        }
        meta_path = OUT / f"{paper_dir}_metadata.json"
        meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False))

        plan_rows.append({
            "paper_id": paper_dir,
            "server": server,
            "title": title[:80],
            "n_figures": len(figures),
            "word_count": word_count,
            "pdf_ready": pdf_path.exists(),
            "submission_url": {
                "ChemRxiv": "https://chemrxiv.org/engage/chemrxiv/dashboard",
                "bioRxiv":  "https://www.biorxiv.org/submit-a-manuscript",
                "medRxiv":  "https://www.medrxiv.org/submit-a-manuscript",
            }[server],
        })

    plan_csv = OUT / "upload_plan.csv"
    pd.DataFrame(plan_rows).to_csv(plan_csv, index=False)
    print(f"✅ {plan_csv}")

    plan_df = pd.read_csv(plan_csv)
    server_counts = plan_df["server"].value_counts()
    print(f"\n[Server 분배]")
    for s, n in server_counts.items():
        print(f"  {s}: {n}편")
    print(f"\n[준비 상태]")
    print(f"  PDF ready: {plan_df['pdf_ready'].sum()}/{len(plan_df)}")
    print(f"  Total words: {plan_df['word_count'].sum():,}")
    print(f"  Total figures: {plan_df['n_figures'].sum()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
