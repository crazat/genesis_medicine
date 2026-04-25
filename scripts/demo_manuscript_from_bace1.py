"""기존 BACE1 파일럿 결과를 manuscript로 자동 변환 — 시연용.

실 데이터로 manuscript_writer가 어떤 출력물을 만드는지 확인.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    from genesis_medicine.reporting import StudyContext, build_manuscript

    # BACE1 결과 가공 (full_report.csv → consensus 형태)
    full_csv = ROOT / "pilot/bace1_boltz2/bace1_full_report.csv"
    if not full_csv.exists():
        print(f"❌ BACE1 결과 없음: {full_csv}")
        return 1
    full = pd.read_csv(full_csv)

    # consensus 형태 (single target이지만 시연 가능)
    work_dir = ROOT / "pilot/bace1_boltz2/manuscript_demo"
    work_dir.mkdir(parents=True, exist_ok=True)
    cons = full[["chembl_id", "affinity_probability_binary", "QED", "BBB_Martins",
                 "hERG", "DILI", "combined_score"]].copy()
    cons = cons.rename(columns={"chembl_id": "compound",
                                 "affinity_probability_binary": "BACE1"})
    cons = cons.set_index("compound")
    cons["consensus_score"] = cons["BACE1"]
    cons_csv = work_dir / "bace1_consensus.csv"
    cons.to_csv(cons_csv)

    # full_df 구성 (target 컬럼 추가)
    full_long = full[["chembl_id", "affinity_probability_binary"]].copy()
    full_long["target"] = "BACE1"
    full_long = full_long.rename(columns={"chembl_id": "compound"})
    full_csv_out = work_dir / "bace1_full.csv"
    full_long.to_csv(full_csv_out, index=False)

    # compounds metadata (간단히 mock — 실제는 ADMET 결과에서)
    comp_meta = []
    for chembl in full["chembl_id"].tolist():
        row = full[full["chembl_id"] == chembl].iloc[0]
        comp_meta.append({
            "name": chembl,
            "smiles": "",
            "mw": 400.0,
            "logp": 2.5,
            "hbd": 3,
            "hba": 5,
            "tpsa": 80.0,
            "rotbonds": 6,
            "category": "BACE1_inhibitor",
        })
    pd.DataFrame(comp_meta).to_csv(work_dir / "compounds.csv", index=False)

    ctx = StudyContext(
        name="bace1_demo",
        title="In silico binding affinity prediction of BACE1 inhibitors with Boltz-2",
        short_title="Boltz-2 BACE1 demo",
        disease="Alzheimer's disease (BACE1 demonstration)",
        description=(
            "본 연구는 Genesis_Medicine 인프라의 일관성·재현성 검증용 데모로,"
            " 9개 ChEMBL BACE1 inhibitor에 Boltz-2 affinity head를 적용한 결과를 분석한다."
        ),
        results_dir=work_dir,
        consensus_csv=cons_csv,
        full_csv=full_csv_out,
        compounds_csv=work_dir / "compounds.csv",
        targets=[
            {"key": "BACE1", "uniprot": "P56817", "display": "BACE1",
             "mode": "inhibitor"},
        ],
        components_used=["boltz2", "admet_ai", "rdkit", "openmm",
                         "alphafold_db", "pubchem"],
        output_dir=work_dir,
        seed=42,
        license_profile="commercial",
        authors=[{"name": "Recover Clinic Computational Team",
                  "affiliation": "Recover Clinic, Gangnam, Seoul",
                  "orcid": ""}],
        correspondence_email="research@recover-clinic.kr",
    )

    print("=== build_manuscript() 실행 ===")
    result = build_manuscript(ctx)
    print(f"\n✅ manuscript: {result.manuscript_md}")
    print(f"   word_count: {result.word_count}")
    print(f"   figures   : {len(result.figures)} files")
    print(f"   tables    : {len(result.tables)} files")
    print(f"   bib       : {result.references_bib}")
    print(f"   checklist : {result.checklist_md}")

    print("\n--- manuscript.md 첫 60줄 ---")
    print("\n".join(result.manuscript_md.read_text().splitlines()[:60]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
