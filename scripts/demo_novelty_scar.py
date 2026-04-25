"""흉터 파일럿 결과의 Top 10 화합물 novelty 분석 시연.

실 PubMed/Europe PMC/ChEMBL/ClinicalTrials/Patent 호출.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    from genesis_medicine.novelty import (
        NoveltyContext, batch_novelty_analysis,
    )
    from genesis_medicine.novelty.novelty_score import to_dataframe
    from genesis_medicine.novelty.prior_art_table import render_novelty_section

    consensus = pd.read_csv(
        ROOT / "pilot/skin_scar/results_v2/scar_consensus.csv",
        index_col=0,
    )
    top_10 = consensus.head(10).index.tolist()
    print(f"=== 흉터 파일럿 Top 10 화합물 novelty 분석 ===")
    print(f"대상: {top_10}\n")

    contexts = [
        NoveltyContext(
            compound_name=name,
            disease="hypertrophic scar",
            disease_synonyms=["keloid", "scar", "fibrosis"],
            target_uniprot="P01137",
            target_gene="TGFB1",
            target_synonyms=["TGF-beta1"],
        )
        for name in top_10
    ]

    scores = batch_novelty_analysis(contexts)
    df = to_dataframe(scores)
    out = ROOT / "pilot/skin_scar/results_v2/novelty_top10.csv"
    df.to_csv(out, index=False)

    print("\n" + "=" * 100)
    print("흉터 Top 10 — Novelty 분석 결과")
    print("=" * 100)
    print(df.to_string(index=False))

    # 통계
    n_novel = (df["classification"] == "novel").sum()
    n_partial = (df["classification"] == "partially_novel").sum()
    n_known = (df["classification"] == "known").sum()
    print(f"\n분류: {n_novel} novel | {n_partial} partial | {n_known} known")

    # markdown 섹션
    md_path = ROOT / "pilot/skin_scar/results_v2/novelty_section.md"
    md_path.write_text(render_novelty_section(scores, disease="hypertrophic scar"))
    print(f"\n✅ {out}")
    print(f"✅ {md_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
