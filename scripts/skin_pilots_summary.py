"""5개 피부 파일럿 종합 비교 — 흉터/기미/탈모/여드름/광노화.

각 파일럿의 외용제 Top 5 + system novelty 통합 표.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

PILOTS = [
    ("scar (skin_scar v2)",   "skin_scar/results_v2",   "scar"),
    ("pigment (skin_pigment v1)", "skin_pigment/results_v1", "pigment"),
    ("alopecia (skin_alopecia v1)", "skin_alopecia/results_v1", "alopecia"),
    ("acne (skin_acne v1)",  "skin_acne/results_v1",   "acne"),
    ("photoaging (skin_photoaging v1)", "skin_photoaging/results_v1", "photoaging"),
]


def main() -> int:
    print("=" * 100)
    print("5개 피부 파일럿 종합 비교 (Genesis_Medicine v3)")
    print("=" * 100)

    rows = []
    for label, sub, key in PILOTS:
        rep_path = ROOT / "pilot" / sub / f"{key}_full_report.csv"
        if not rep_path.exists():
            # scar v2는 다른 파일명
            alt = ROOT / "pilot" / sub / "scar_full_report.csv"
            rep_path = alt if alt.exists() else rep_path
        if not rep_path.exists():
            print(f"  ⚠️ {label}: report 없음 → {rep_path}")
            continue
        df = pd.read_csv(rep_path)
        top5 = df.head(5)["compound"].tolist()

        # system novelty
        sys_md = ROOT / "pilot" / sub / "manuscript" / "system_novelty.md"
        sys_score, sys_class = "?", "?"
        if sys_md.exists():
            txt = sys_md.read_text()
            import re
            m = re.search(r"composite system-novelty = ([\d.]+)", txt)
            if m:
                sys_score = float(m.group(1))
                if sys_score >= 0.7: sys_class = "🆕 blue ocean"
                elif sys_score >= 0.4: sys_class = "🟡 competitive"
                else: sys_class = "📚 red ocean"

        rows.append({
            "pilot": label,
            "n_compounds": int(df["compound"].nunique()),
            "n_topical_pass": int(df.get("topical_friendly", pd.Series()).sum() if "topical_friendly" in df.columns else 0),
            "top1": top5[0] if top5 else "-",
            "top2": top5[1] if len(top5) > 1 else "-",
            "top3": top5[2] if len(top5) > 2 else "-",
            "top4": top5[3] if len(top5) > 3 else "-",
            "top5": top5[4] if len(top5) > 4 else "-",
            "system_novelty": sys_score,
            "novelty_class": sys_class,
        })

    summary = pd.DataFrame(rows)
    out = ROOT / "pilot" / "skin_pilots_summary.csv"
    summary.to_csv(out, index=False)

    print("\n=== 외용제 Top 5 + System Novelty ===\n")
    for _, r in summary.iterrows():
        print(f"  {r['pilot']:45s}  novelty={r['system_novelty']}  ({r['novelty_class']})")
        print(f"    Top: {r['top1']} → {r['top2']} → {r['top3']} → {r['top4']} → {r['top5']}")
        print()

    print(f"✅ 저장: {out}")

    # 각 manuscript 정보
    print("\n=== Manuscript 패키지 ===")
    for label, sub, _ in PILOTS:
        m_dir = ROOT / "pilot" / sub / "manuscript"
        if not m_dir.exists():
            continue
        files = list(m_dir.glob("manuscript.*"))
        n_figs = len(list((m_dir / "figures").glob("*.pdf"))) if (m_dir / "figures").exists() else 0
        n_tabs = len(list((m_dir / "tables").glob("*.csv"))) if (m_dir / "tables").exists() else 0
        formats = sorted([f.suffix for f in files])
        print(f"  {label:45s}  formats={formats}  figs={n_figs}  tables={n_tabs}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
