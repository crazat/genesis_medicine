"""TxGNN Top 16 약물 → BACE1 Boltz-2 cofolding + affinity.

BACE1 단일 타겟이 임상에서 막혀도, 재창출 후보가 BACE1에 의미있는 결합 보이면
multi-target 프로파일의 한 축으로 재평가 가능.

이게 zero-shot 재창출 검증의 핵심 단계.
"""

from __future__ import annotations

import csv
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

import pandas as pd
import yaml


BASE = Path(__file__).parent
RESULT = BASE / "results"

# BACE1 시퀀스 (기존 파일럿과 동일, UniProt P56817 propeptide-free domain)
BACE1_SEQ = (
    "MAQALPWLLLWMGAGVLPAHGTQHGIRLPLRSGLGGAPLGLRLPRETDEEPEEPGRRGSFVEMVDNLRGKSGQG"
    "YYVEMTVGSPPQTLNILVDTGSSNFAVGAAPHPFLHRYYQRQLSSTYRDLRKGVYVPYTQGKWEGELGTDLVS"
    "IPHGPNVTVRANIAAITESDKFFINGSNWEGILGLAYAEIARPDDSLEPFFDSLVKQTHVPNLFSLQLCGAGF"
    "PLNQSEVLASVGGSMIIGGIDHSLYTGSLWYTPIRREWYYEVIIVRVEINGQDLKMDCKEYNYDKSIVDSGTT"
    "NLRLPKKVFEAAVKSIKAASSTEKFPDGFWLGEQLVCWQAGTTPWNIFPVISLYLMGEVTNQSFRITILPQQY"
    "LRPVEDVATSQDDCYKFAISQSSTGTVMGAVIMEGFYVVFDRARKRIGFAVSACHVHDEFRTAAVEGPFVTLD"
    "MEDCGYNILQSVFGDRKVEGYSAWKEVHKGTTEPVRHAIQLFDPNGYLMEIVPVELPLF"
)


def build_input_yaml(drug_name: str, smiles: str, out_dir: Path) -> Path:
    safe_name = drug_name.replace(" ", "_").replace(",", "").lower()
    payload = {
        "version": 1,
        "sequences": [
            {"protein": {"id": "A", "sequence": BACE1_SEQ}},
            {"ligand": {"id": "B", "smiles": smiles}},
        ],
        "properties": [{"affinity": {"binder": "B"}}],
    }
    p = out_dir / f"{safe_name}.yaml"
    p.write_text(yaml.safe_dump(payload, sort_keys=False))
    return p


def main() -> int:
    smi_df = pd.read_csv(RESULT / "top20_smiles.csv")
    valid = smi_df[smi_df["smiles"].notna() & (smi_df["smiles"].str.len() < 500)]
    print(f"=== TxGNN Top {len(valid)} → BACE1 Boltz-2 cofolding ===")

    # ligand가 너무 큰 건 제외 (Boltz-2는 작은 분자 최적화)
    valid = valid[valid["smiles"].str.len() < 300]
    print(f"Size 필터 후: {len(valid)} 약물")
    print(valid[["rank", "drug_name", "mw"]].to_string(index=False))

    # YAML 준비
    inputs_dir = RESULT / "boltz2_inputs"
    inputs_dir.mkdir(parents=True, exist_ok=True)
    out_dir = RESULT / "boltz2_output"
    out_dir.mkdir(parents=True, exist_ok=True)

    for _, row in valid.iterrows():
        build_input_yaml(row["drug_name"], row["smiles"], inputs_dir)

    # Boltz-2 실행 (기존 config와 동일)
    boltz_bin = str(Path.home() / "genesis_medicine" / ".venv" / "bin" / "boltz")
    cmd = [
        boltz_bin, "predict", str(inputs_dir),
        "--out_dir", str(out_dir),
        "--use_msa_server",
        "--sampling_steps", "25",
        "--diffusion_samples", "1",
        "--recycling_steps", "3",
        "--sampling_steps_affinity", "200",
        "--diffusion_samples_affinity", "5",
        "--affinity_mw_correction",
        "--devices", "1",
    ]
    print("\n=== Boltz-2 실행 ===")
    print("cmd:", " ".join(cmd[:6]), "...")

    t0 = time.time()
    r = subprocess.run(cmd, capture_output=False)
    wall = time.time() - t0
    print(f"\n✅ Boltz-2 완료 in {wall:.0f}s (exit={r.returncode})")

    # 결과 수집
    summary = []
    for aff_json in sorted(out_dir.rglob("affinity_*.json")):
        d = json.loads(aff_json.read_text())
        name = aff_json.stem.replace("affinity_", "")
        # 해당 SMILES·DrugName 찾기
        pv = d.get("affinity_pred_value")
        pb = d.get("affinity_probability_binary")
        summary.append({
            "safe_name": name,
            "affinity_pred_value": pv,
            "affinity_probability_binary": pb,
            "pIC50_approx": 6.0 - float(pv) if pv is not None else None,
        })

    df = pd.DataFrame(summary)
    # drug_name + rank 복원
    name_map = {r["drug_name"].replace(" ", "_").replace(",", "").lower(): (r["drug_name"], r["rank"])
                for _, r in valid.iterrows()}
    df["drug_name"] = df["safe_name"].map(lambda s: name_map.get(s, (s, None))[0])
    df["txgnn_rank"] = df["safe_name"].map(lambda s: name_map.get(s, (s, None))[1])
    df = df.sort_values("affinity_probability_binary", ascending=False)

    out_csv = RESULT / "boltz2_bace1_affinity.csv"
    df[["txgnn_rank", "drug_name", "pIC50_approx", "affinity_probability_binary",
        "affinity_pred_value"]].to_csv(out_csv, index=False)
    print(f"\n=== 결과 ===")
    print(df[["txgnn_rank", "drug_name", "pIC50_approx", "affinity_probability_binary"]]
          .to_string(index=False, float_format=lambda v: f"{v:.3f}" if pd.notna(v) else "—"))
    print(f"\n✅ 저장: {out_csv}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
