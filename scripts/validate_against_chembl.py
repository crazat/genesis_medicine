"""우리 Boltz-2 affinity 예측 vs ChEMBL 실험 IC50 외부 검증.

DiffDock 풀 설치 대신 더 가치 있는 ablation:
- 우리 hits (Embelin, EGCG, Curcumin, Baicalein, Resveratrol 등) 의
  ChEMBL bioactivity (IC50/Ki/Kd) 자동 매핑
- Boltz-2 affinity_probability_binary vs 실험값 상관관계
- paper reviewer 대비: "당신 in silico 예측이 실제와 얼마나 일치?"
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]


def chembl_search_compound(name: str) -> str | None:
    url = "https://www.ebi.ac.uk/chembl/api/data/molecule/search"
    r = requests.get(url, params={"q": name, "format": "json", "limit": 1}, timeout=15)
    if r.status_code != 200:
        return None
    mols = r.json().get("molecules", [])
    return mols[0].get("molecule_chembl_id") if mols else None


def chembl_target_id(uniprot: str) -> str | None:
    url = "https://www.ebi.ac.uk/chembl/api/data/target.json"
    r = requests.get(url, params={"target_components__accession": uniprot,
                                   "limit": 1}, timeout=15)
    if r.status_code != 200:
        return None
    t = r.json().get("targets", [])
    return t[0].get("target_chembl_id") if t else None


def chembl_activities(mol_id: str, target_id: str) -> list[dict]:
    url = "https://www.ebi.ac.uk/chembl/api/data/activity.json"
    r = requests.get(url, params={
        "molecule_chembl_id": mol_id,
        "target_chembl_id": target_id,
        "limit": 50,
    }, timeout=20)
    if r.status_code != 200:
        return []
    return r.json().get("activities", [])


def best_ic50_nm(activities: list[dict]) -> float | None:
    """가장 강한 (작은) IC50/Ki/Kd 추출 (nM)."""
    valid = []
    for a in activities:
        if a.get("standard_type") in ("IC50", "Ki", "Kd"):
            v = a.get("standard_value")
            u = a.get("standard_units")
            if v and u:
                v = float(v)
                if u == "uM":
                    v *= 1000
                elif u == "M":
                    v *= 1e9
                elif u == "mM":
                    v *= 1e6
                valid.append(v)
    return min(valid) if valid else None


def main() -> int:
    # 5 파일럿 통합 매트릭스 로드
    matrix = pd.read_csv(ROOT / "pilot/cross_disease/matrix_affinity.csv", index_col=0)

    # 검증할 (compound, uniprot) 쌍 — 5 파일럿 핵심 hit
    pairs = [
        # 흉터
        ("Embelin",       "P01137", "TGFB1"),
        ("Embelin",       "P03956", "MMP1"),
        ("EGCG",          "P01137", "TGFB1"),
        ("EGCG",          "P03956", "MMP1"),
        ("Curcumin",      "P01137", "TGFB1"),
        ("Curcumin",      "P03956", "MMP1"),
        ("Baicalein",     "P01137", "TGFB1"),
        ("Resveratrol",   "P01137", "TGFB1"),
        # 기미
        ("Resveratrol",   "P14679", "TYR"),
        ("EGCG",          "P14679", "TYR"),
        ("Kojic acid",    "P14679", "TYR"),
        ("Apigenin",      "P14679", "TYR"),
        ("Ellagic acid",  "P14679", "TYR"),
        # 탈모
        ("EGCG",          "P31213", "SRD5A2"),
        ("Embelin",       "P31213", "SRD5A2"),
        # 광노화
        ("Resveratrol",   "Q96EB6", "SIRT1"),
        ("Quercetin",     "Q96EB6", "SIRT1"),
        ("EGCG",          "Q96EB6", "SIRT1"),
    ]

    print(f"=== {len(pairs)}개 (compound, target) ChEMBL 외부 검증 ===\n")
    rows = []
    for name, uniprot, gene in pairs:
        # 우리 예측
        # cross-disease matrix는 disease별이라 직접 사용 어려움.
        # full csv에서 (compound × target) 매트릭스가 더 적합.
        mol_id = chembl_search_compound(name)
        if not mol_id:
            print(f"  ⚠️  {name}: ChEMBL 미등록")
            continue
        target_id = chembl_target_id(uniprot)
        if not target_id:
            print(f"  ⚠️  {gene} ({uniprot}): ChEMBL target 미등록")
            continue
        acts = chembl_activities(mol_id, target_id)
        ic50_nm = best_ic50_nm(acts)
        from math import log10
        pic50 = round(-log10(ic50_nm * 1e-9), 2) if ic50_nm else None
        rows.append({
            "compound": name,
            "target": gene,
            "uniprot": uniprot,
            "chembl_mol": mol_id,
            "chembl_target": target_id,
            "n_assays": len(acts),
            "best_ic50_nm": ic50_nm,
            "pIC50_observed": pic50,
        })
        if ic50_nm:
            print(f"  ✅ {name:15s} × {gene:8s} : IC50 = {ic50_nm:>10.1f} nM, "
                  f"pIC50 = {pic50:.2f} (n_assays={len(acts)})")
        else:
            print(f"  ❌ {name:15s} × {gene:8s} : 알려진 IC50 없음")

    df = pd.DataFrame(rows)
    out = ROOT / "pilot" / "cross_disease" / "chembl_validation.csv"
    df.to_csv(out, index=False)

    # 통계
    n_with_data = df["best_ic50_nm"].notna().sum()
    print(f"\n  알려진 IC50 보유: {n_with_data}/{len(rows)} 쌍")
    if n_with_data > 0:
        valid = df[df["best_ic50_nm"].notna()]
        print(f"  pIC50 범위: {valid['pIC50_observed'].min():.2f} ~ "
              f"{valid['pIC50_observed'].max():.2f}")
        print(f"  pIC50 평균: {valid['pIC50_observed'].mean():.2f}")

    # 우리 예측과 비교 (full.csv 매트릭스 통합)
    print("\n=== 우리 Boltz-2 affinity_probability_binary vs 실험 pIC50 ===")
    # 5 파일럿의 long_form 활용
    long_form = pd.read_csv(ROOT / "pilot/cross_disease/long_form.csv")
    # disease → target 매핑
    disease_targets = {
        "scar": ["TGFB1", "MMP1", "CTGF"],
        "pigment": ["TYR", "TYRP1", "DCT"],
        "alopecia": ["SRD5A2", "AR", "CTNNB1"],
        "acne": ["AR", "SRD5A2", "PTGS2"],
        "photoaging": ["MMP1", "SIRT1", "JUN"],
    }

    # 각 파일럿의 full.csv에서 (compound × target) 직접 추출
    boltz_pairs = {}  # (compound, target) → affinity_probability
    for d, sub_path in [
        ("scar", "skin_scar/results_v2/scar_full.csv"),
        ("pigment", "skin_pigment/results_v1/pigment_full.csv"),
        ("alopecia", "skin_alopecia/results_v1/alopecia_full.csv"),
        ("acne", "skin_acne/results_v1/acne_full.csv"),
        ("photoaging", "skin_photoaging/results_v1/photoaging_full.csv"),
    ]:
        p = ROOT / "pilot" / sub_path
        if not p.exists():
            continue
        f = pd.read_csv(p)
        for _, r in f.iterrows():
            boltz_pairs[(r["compound"], r["target"])] = r["affinity_probability_binary"]

    df["boltz_aff_prob"] = df.apply(
        lambda r: boltz_pairs.get((r["compound"], r["target"])), axis=1
    )

    df.to_csv(out, index=False)
    print(df[["compound", "target", "best_ic50_nm", "pIC50_observed",
              "boltz_aff_prob"]].to_string(index=False,
              float_format=lambda v: f"{v:.3f}" if pd.notna(v) else "—"))

    # 상관관계
    pairs_with_both = df[df["pIC50_observed"].notna() & df["boltz_aff_prob"].notna()]
    if len(pairs_with_both) >= 3:
        from scipy.stats import pearsonr, spearmanr
        r_pear, p_pear = pearsonr(pairs_with_both["pIC50_observed"],
                                   pairs_with_both["boltz_aff_prob"])
        r_spear, p_spear = spearmanr(pairs_with_both["pIC50_observed"],
                                      pairs_with_both["boltz_aff_prob"])
        print(f"\n  Pearson  r = {r_pear:.3f} (p = {p_pear:.3g}, n={len(pairs_with_both)})")
        print(f"  Spearman ρ = {r_spear:.3f} (p = {p_spear:.3g})")
    print(f"\n✅ {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
