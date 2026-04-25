"""NSCLC + Parkinson Open Targets 타겟 발굴 (NEXT ACTIONS #4).

인프라 generality 검증 — BACE1 파일럿과 동일 로직으로 다른 질병도 end-to-end.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
import yaml


def fetch_for_disease(disease_cfg: dict, size: int = 100) -> pd.DataFrame:
    from genesis_medicine.io.open_targets import fetch_associated_targets, to_uniprot_list

    efo = disease_cfg["efo_id"]
    print(f"\n=== {disease_cfg['display_name']} ({efo}) ===")
    rows = fetch_associated_targets(efo, size=size)
    targets = to_uniprot_list(rows)
    df = pd.DataFrame(targets).sort_values("score", ascending=False).reset_index(drop=True)
    print(f"상위 {len(df)} 타겟 발굴")
    return df


def main() -> int:
    base = Path(__file__).parent
    conf_dir = Path.home() / "genesis_medicine" / "conf" / "disease"
    out_dir = base / "results"
    out_dir.mkdir(parents=True, exist_ok=True)

    disease_keys = ["nsclc", "parkinson"]
    seed_checks = {}

    for key in disease_keys:
        cfg = yaml.safe_load((conf_dir / f"{key}.yaml").read_text())
        df = fetch_for_disease(cfg, size=100)
        df.to_parquet(out_dir / f"{key}_targets.parquet", index=False)
        df.to_csv(out_dir / f"{key}_targets.csv", index=False)
        print(f"  → {out_dir / f'{key}_targets.parquet'}")

        # 시드 타겟이 Open Targets 상위에 있는지 확인
        seed_uniprots = {t["uniprot"] for t in cfg["known_targets_seed"]}
        top50 = set(df.head(50)["uniprot"])
        hit = seed_uniprots & top50
        miss = seed_uniprots - top50
        seed_checks[key] = {
            "n_seed": len(seed_uniprots),
            "hit_in_top50": sorted(hit),
            "missed": sorted(miss),
        }
        print(f"  시드 타겟 {len(seed_uniprots)}개 중 top 50 hit: {sorted(hit)}")
        if miss:
            print(f"  miss: {sorted(miss)}")

    # 요약
    summary_path = out_dir / "summary.json"
    summary_path.write_text(json.dumps(seed_checks, indent=2, ensure_ascii=False))
    print(f"\n✅ 요약: {summary_path}")

    # 상위 5 타겟 비교 표
    print("\n" + "=" * 80)
    print(f"{'disease':<15s} {'rank':<5s} {'uniprot':<10s} {'symbol':<10s} {'score':>7s}  name")
    print("=" * 80)
    for key in disease_keys:
        df = pd.read_parquet(out_dir / f"{key}_targets.parquet")
        for i, row in df.head(5).iterrows():
            print(f"{key:<15s} {i:<5d} {row['uniprot']:<10s} {row['symbol']:<10s} "
                  f"{row['score']:>7.3f}  {row['name'][:40]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
