"""NSCLC + Parkinson top 타겟의 AFDB 구조 확보.

Stage 2 실런 — 각 질병별 top 5 타겟에 대해 AlphaFold DB에서 CIF 가져오기.
Boltz-2 co-folding을 바로 돌릴 수 있는 준비.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd


def main() -> int:
    from genesis_medicine.structure.alphafold_db_adapter import AlphaFoldDBAdapter

    base = Path(__file__).parent
    results = base / "results"
    out_struct = base / "structures"
    out_struct.mkdir(parents=True, exist_ok=True)

    afdb = AlphaFoldDBAdapter(cache_dir=out_struct)

    summary = []
    for key in ["nsclc", "parkinson"]:
        df = pd.read_parquet(results / f"{key}_targets.parquet")
        print(f"\n=== {key}: AFDB 조회 top 5 ===")
        for row in df.head(5).itertuples():
            hit = afdb.lookup(row.uniprot)
            if hit is None:
                print(f"  ❌ {row.uniprot} ({row.symbol}): AFDB 미커버")
                summary.append({
                    "disease": key, "uniprot": row.uniprot,
                    "symbol": row.symbol, "status": "miss",
                    "cif": None, "plddt": 0.0,
                })
            else:
                size_kb = hit.cif_path.stat().st_size / 1024 if hit.cif_path.exists() else 0
                print(f"  ✅ {row.uniprot} ({row.symbol}): plddt={hit.plddt_mean:.1f}, {size_kb:.0f} KB")
                summary.append({
                    "disease": key, "uniprot": row.uniprot, "symbol": row.symbol,
                    "status": "ok", "cif": str(hit.cif_path), "plddt": hit.plddt_mean,
                })

    out = pd.DataFrame(summary)
    out.to_csv(out_struct / "summary.csv", index=False)
    print(f"\n✅ 요약: {out_struct / 'summary.csv'}")
    print(f"   총 {(out['status']=='ok').sum()}/{len(out)} 타겟 AFDB 커버")
    return 0


if __name__ == "__main__":
    sys.exit(main())
