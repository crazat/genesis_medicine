"""5 파일럿의 14 타겟에 대한 외부 데이터 종합 검증.

각 타겟에 대해:
- GTEx: 피부 발현 확인
- BindingDB: 알려진 ligand 수
- STRING: PPI 파트너 top 5
- InterPro: 도메인 분류

다중 타겟 종합:
- Reactome pathway enrichment
- STRING functional enrichment
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot" / "external_validation"
OUT.mkdir(parents=True, exist_ok=True)


# 5 파일럿의 14 타겟
TARGETS = [
    {"key": "TGFB1", "uniprot": "P01137", "disease": "scar"},
    {"key": "MMP1",  "uniprot": "P03956", "disease": "scar+photoaging"},
    {"key": "CTGF",  "uniprot": "P29279", "disease": "scar"},
    {"key": "TYR",   "uniprot": "P14679", "disease": "pigment"},
    {"key": "TYRP1", "uniprot": "P17643", "disease": "pigment"},
    {"key": "DCT",   "uniprot": "P40126", "disease": "pigment"},
    {"key": "SRD5A2","uniprot": "P31213", "disease": "alopecia+acne"},
    {"key": "AR",    "uniprot": "P10275", "disease": "alopecia+acne"},
    {"key": "CTNNB1","uniprot": "P35222", "disease": "alopecia"},
    {"key": "PTGS2", "uniprot": "P35354", "disease": "acne"},
    {"key": "SIRT1", "uniprot": "Q96EB6", "disease": "photoaging"},
    {"key": "JUN",   "uniprot": "P05412", "disease": "photoaging"},
]


def main() -> int:
    from genesis_medicine.external_apis import (
        gtex_skin_expression, bindingdb_search, string_partners, interpro_domains,
        reactome_pathways_for_targets, string_enrichment,
    )

    rows = []
    print("=" * 100)
    print(f"{len(TARGETS)} 타겟 외부 데이터 종합 검증")
    print("=" * 100)

    for t in TARGETS:
        print(f"\n--- {t['key']} ({t['uniprot']}) — {t['disease']} ---")
        # GTEx
        gtex = gtex_skin_expression(t["key"])
        skin_tpm = gtex.get("skin_tpm_max", 0)
        skin_interpret = gtex.get("interpretation", "?")
        # BindingDB
        bdb = bindingdb_search(t["uniprot"])
        n_lig = bdb.get("n_ligands", 0)
        # STRING
        st = string_partners(t["key"], n_partners=5)
        partners = [p["gene"] for p in st.get("partners", [])][:5]
        # InterPro
        ip = interpro_domains(t["uniprot"])
        domains = []
        for items in ip.get("by_type", {}).values():
            for e in items[:2]:
                n = e.get("name") or "?"
                domains.append(n)
        domains = [d for d in dict.fromkeys(domains) if d][:3]

        rows.append({
            "target": t["key"],
            "uniprot": t["uniprot"],
            "disease": t["disease"],
            "gtex_skin_tpm_max": round(skin_tpm, 2) if isinstance(skin_tpm, (int, float)) else 0,
            "gtex_interpretation": skin_interpret,
            "bindingdb_n_ligands": n_lig,
            "string_top_partners": ", ".join(partners),
            "interpro_domains": ", ".join(str(d)[:30] for d in domains if d),
        })
        print(f"  GTEx skin TPM max: {skin_tpm} → {skin_interpret}")
        print(f"  BindingDB ligands: {n_lig}")
        print(f"  STRING partners: {partners}")
        print(f"  InterPro: {domains}")

    df = pd.DataFrame(rows)
    df.to_csv(OUT / "target_external_validation.csv", index=False)
    print(f"\n✅ {OUT}/target_external_validation.csv")

    # Reactome multi-target enrichment
    print("\n" + "=" * 100)
    print("Reactome pathway enrichment (14 타겟 종합)")
    print("=" * 100)
    uniprots = [t["uniprot"] for t in TARGETS]
    reactome = reactome_pathways_for_targets(uniprots)
    if "top_pathways" in reactome:
        print(f"  {len(reactome['top_pathways'])} pathways enriched (top 10):")
        pw_rows = []
        for p in reactome["top_pathways"][:10]:
            print(f"    [{p.get('fdr', 0):.3e}] {p.get('name', '?')} "
                  f"({p.get('n_found', 0)}/{p.get('n_total', 0)} found)")
            pw_rows.append(p)
        pd.DataFrame(pw_rows).to_csv(OUT / "reactome_pathways.csv", index=False)
        print(f"  ✅ {OUT}/reactome_pathways.csv")
    else:
        print(f"  ⚠️  {reactome.get('error', '?')}")

    # STRING functional enrichment
    print("\n" + "=" * 100)
    print("STRING functional enrichment")
    print("=" * 100)
    gene_syms = [t["key"] for t in TARGETS]
    str_enr = string_enrichment(gene_syms)
    if "by_category" in str_enr:
        print(f"  카테고리: {list(str_enr['by_category'].keys())}")
        for cat, items in list(str_enr["by_category"].items())[:5]:
            if items:
                top = items[0]
                print(f"    {cat:25s} top: {top.get('description','?')[:60]} "
                      f"(FDR {top.get('fdr', 1):.2e})")
    else:
        print(f"  ⚠️ {str_enr.get('error', '?')}")
    Path(OUT / "string_enrichment.json").write_text(json.dumps(str_enr, default=str))
    print(f"  ✅ {OUT}/string_enrichment.json")

    return 0


if __name__ == "__main__":
    sys.exit(main())
