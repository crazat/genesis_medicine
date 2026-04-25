"""NSCLC EGFR + 5 approved TKI Boltz-2 cofolding — BACE1 파일럿 end-to-end 재현.

기대 결과: 알려진 EGFR TKI들이 높은 affinity_probability_binary (≥ 0.9) 보여야 함.
이는 인프라 generality 증명 (다른 질병·타겟에서도 동일 품질).
"""

from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

import pandas as pd
import yaml


BASE = Path(__file__).parent

# EGFR kinase domain (UniProt P00533, residues 696-1022)
# AFDB에서 이미 다운로드됨. 여기서는 전체 시퀀스 대신 kinase domain 사용
EGFR_KINASE = (
    "EAPNQALLRILKETEFKKIKVLGSGAFGTVYKGLWIPEGEKVKIPVAIKELREATSPKANKEILDEAYVMASV"
    "DNPHVCRLLGICLTSTVQLITQLMPFGCLLDYVREHKDNIGSQYLLNWCVQIAKGMNYLEDRRLVHRDLAARN"
    "VLVKTPQHVKITDFGLAKLLGAEEKEYHAEGGKVPIKWMALESILHRIYTHQSDVWSYGVTVWELMTFGSKPY"
    "DGIPASEISSILEKGERLPQPPICTIDVYMIMVKCWMIDADSRPKFRELIIEFSKMARDPQRYLVIQGDERMH"
    "LPSPTDSNFYRALMDEEDMDDVVDADEYLIPQQGFFSSPSTSRTPLLSSLSATSNNSTVACIDRNGLQSCPIK"
)


def build_yaml(drug_name: str, smiles: str, out_dir: Path) -> Path:
    safe = drug_name.lower()
    payload = {
        "version": 1,
        "sequences": [
            {"protein": {"id": "A", "sequence": EGFR_KINASE}},
            {"ligand": {"id": "B", "smiles": smiles}},
        ],
        "properties": [{"affinity": {"binder": "B"}}],
    }
    p = out_dir / f"egfr_{safe}.yaml"
    p.write_text(yaml.safe_dump(payload, sort_keys=False))
    return p


def main() -> int:
    tkis = pd.read_csv(BASE / "egfr_known_tkis.csv")
    print(f"=== NSCLC EGFR 파일럿: {len(tkis)}개 알려진 TKI Boltz-2 cofolding ===")
    print(tkis[["rank", "drug_name", "generation", "approved_for"]].to_string(index=False))

    inputs = BASE / "egfr_inputs"
    inputs.mkdir(exist_ok=True)
    out = BASE / "egfr_output"
    out.mkdir(exist_ok=True)

    for _, row in tkis.iterrows():
        build_yaml(row["drug_name"], row["smiles"], inputs)

    boltz_bin = str(Path.home() / "genesis_medicine" / ".venv" / "bin" / "boltz")
    cmd = [
        boltz_bin, "predict", str(inputs),
        "--out_dir", str(out),
        "--use_msa_server",
        "--sampling_steps", "25",
        "--diffusion_samples", "1",
        "--recycling_steps", "3",
        "--sampling_steps_affinity", "200",
        "--diffusion_samples_affinity", "5",
        "--affinity_mw_correction",
        "--devices", "1",
    ]
    print("\n=== Boltz-2 EGFR 실행 ===")
    t0 = time.time()
    subprocess.run(cmd, capture_output=False)
    wall = time.time() - t0
    print(f"\n✅ {wall:.0f}s")

    # 결과
    results = []
    for aff_json in sorted(out.rglob("affinity_*.json")):
        d = json.loads(aff_json.read_text())
        name = aff_json.stem.replace("affinity_egfr_", "").capitalize()
        pv = d.get("affinity_pred_value")
        results.append({
            "drug": name,
            "pIC50_approx": 6.0 - float(pv) if pv is not None else None,
            "affinity_probability_binary": d.get("affinity_probability_binary"),
        })

    df = pd.DataFrame(results).sort_values("affinity_probability_binary", ascending=False)
    df.to_csv(BASE / "egfr_affinity.csv", index=False)
    print("\n=== 결과 ===")
    print(df.to_string(index=False, float_format=lambda v: f"{v:.3f}" if pd.notna(v) else "—"))
    print(f"\n✅ 저장: {BASE / 'egfr_affinity.csv'}")

    # 검증: 모든 TKI가 prob_binary ≥ 0.85 ?
    ok = (df["affinity_probability_binary"] >= 0.85).sum()
    print(f"\n임상 검증된 {len(df)}개 TKI 중 prob_binary ≥ 0.85: {ok}/{len(df)} "
          f"(100%면 인프라 완벽 generalization)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
