"""한국 CRO 표준 in vitro assay 견적 자동 추천.

우리 in silico hits를 wet-lab 검증 비용 추정. 한국 CRO (Bioneer, Macrogen, KORS,
Korea Conformity Laboratories 등) 공개 가격 + 학술 typical 견적 기반.

가격은 2026년 시점 평균. 실 견적은 CRO에 직접 문의 권장.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class AssayItem:
    name: str
    target: str               # e.g. "TGF-β1", "Tyrosinase"
    assay_type: str           # "biochemical" | "cell-based" | "imaging"
    cost_per_compound_krw: int   # 원
    minimum_compounds: int = 1
    turnaround_weeks: int = 4
    notes: str = ""


# 한국 CRO 표준 견적표 (2026 평균, 단위: KRW)
ASSAY_CATALOGUE: dict[str, list[AssayItem]] = {
    "scar": [
        AssayItem("TGF-β1 SMAD2/3 phosphorylation (HEK293 reporter)", "TGFB1",
                  "cell-based", 850_000, 1, 4),
        AssayItem("MMP-1 enzymatic inhibition (FRET)", "MMP1",
                  "biochemical", 450_000, 1, 3),
        AssayItem("MMP-3 / MMP-9 enzymatic", "MMP3/9",
                  "biochemical", 450_000, 1, 3),
        AssayItem("Type I collagen (COL1A1) ELISA in fibroblast", "COL1A1",
                  "cell-based", 1_200_000, 1, 6),
        AssayItem("Hypertrophic fibroblast model (TGF-β stimulated)", "fibroblast",
                  "cell-based", 1_800_000, 1, 8,
                  notes="흉터 specific 모델 (in vitro)"),
    ],
    "pigment": [
        AssayItem("Mushroom tyrosinase inhibition (kinetic)", "TYR",
                  "biochemical", 250_000, 1, 2,
                  notes="mushroom enzyme, human TYR 보다 빠르고 저렴"),
        AssayItem("Human tyrosinase (B16-F10 melanoma cell)", "TYR",
                  "cell-based", 950_000, 1, 4),
        AssayItem("Melanin content in B16 cells (MTT 보정)", "melanin",
                  "cell-based", 850_000, 1, 4),
        AssayItem("MITF expression (Western blot)", "MITF",
                  "cell-based", 750_000, 1, 5),
        AssayItem("Human melanocyte primary culture", "melanocyte",
                  "cell-based", 2_500_000, 1, 8,
                  notes="primary cell, 비싸지만 정확"),
    ],
    "alopecia": [
        AssayItem("5α-reductase type 2 inhibition (LNCaP)", "SRD5A2",
                  "cell-based", 1_100_000, 1, 5),
        AssayItem("Androgen receptor reporter (HEK293-AR)", "AR",
                  "cell-based", 950_000, 1, 5),
        AssayItem("Wnt/β-catenin reporter (TOPflash)", "CTNNB1",
                  "cell-based", 850_000, 1, 5),
        AssayItem("Human dermal papilla cell proliferation", "DP cell",
                  "cell-based", 1_500_000, 1, 6),
        AssayItem("Hair follicle organ culture (ex vivo)", "follicle",
                  "imaging", 3_000_000, 1, 10),
    ],
    "acne": [
        AssayItem("Cutibacterium acnes MIC (microdilution)", "C. acnes",
                  "biochemical", 350_000, 1, 2),
        AssayItem("Sebocyte (SEB-1) lipogenesis", "sebocyte",
                  "cell-based", 1_400_000, 1, 5),
        AssayItem("AR reporter (acne)", "AR",
                  "cell-based", 950_000, 1, 5),
        AssayItem("NLRP3 inflammasome (THP-1)", "NLRP3",
                  "cell-based", 1_300_000, 1, 6),
    ],
    "photoaging": [
        AssayItem("UVB-induced MMP-1 in HaCaT", "MMP1",
                  "cell-based", 1_100_000, 1, 5),
        AssayItem("SIRT1 activation (fluorometric)", "SIRT1",
                  "biochemical", 750_000, 1, 3),
        AssayItem("Type I collagen synthesis (HDF)", "COL1A1",
                  "cell-based", 1_200_000, 1, 5),
        AssayItem("DPPH/ORAC antioxidant (보조)", "antioxidant",
                  "biochemical", 150_000, 1, 1),
    ],
    "general_safety": [
        AssayItem("Cell viability (MTT, HaCaT)", "safety",
                  "cell-based", 250_000, 1, 2),
        AssayItem("Skin irritation (RhE, EpiDerm)", "irritation",
                  "cell-based", 450_000, 1, 3),
        AssayItem("Phototoxicity (3T3 NRU)", "phototox",
                  "cell-based", 400_000, 1, 3),
        AssayItem("hERG patch clamp", "hERG",
                  "biochemical", 2_500_000, 1, 6,
                  notes="Top hits 검증 필수 (외용제도 흡수 시 위험)"),
    ],
}


@dataclass
class AssayCatalogue:
    items: dict[str, list[AssayItem]] = field(default_factory=lambda: ASSAY_CATALOGUE)


def recommend_assays(disease: str, n_top_hits: int = 5,
                     include_safety: bool = True) -> dict[str, list[AssayItem]]:
    """질환별 + 일반 안전성 assay 추천."""
    out: dict[str, list[AssayItem]] = {}
    if disease in ASSAY_CATALOGUE:
        out[disease] = ASSAY_CATALOGUE[disease]
    if include_safety:
        out["general_safety"] = ASSAY_CATALOGUE["general_safety"]
    return out


def estimate_total_cost(
    disease: str,
    n_top_hits: int = 5,
    *,
    tier: str = "standard",
) -> dict:
    """총 견적 산출.

    tier: "minimum" | "standard" | "comprehensive"
    """
    rec = recommend_assays(disease, n_top_hits=n_top_hits, include_safety=True)
    breakdown = []
    total = 0
    weeks_max = 0
    for cat, items in rec.items():
        for item in items:
            # tier 기반 필터
            if tier == "minimum":
                if item.assay_type != "biochemical" and "ELISA" not in item.name:
                    continue
            elif tier == "standard":
                # 모든 biochemical + 핵심 cell-based만
                if item.cost_per_compound_krw > 1_500_000:
                    continue

            cost = item.cost_per_compound_krw * n_top_hits
            breakdown.append({
                "category": cat,
                "assay": item.name,
                "target": item.target,
                "type": item.assay_type,
                "n_compounds": n_top_hits,
                "cost_per_compound_krw": item.cost_per_compound_krw,
                "subtotal_krw": cost,
                "weeks": item.turnaround_weeks,
                "notes": item.notes,
            })
            total += cost
            weeks_max = max(weeks_max, item.turnaround_weeks)

    return {
        "disease": disease,
        "tier": tier,
        "n_compounds": n_top_hits,
        "total_krw": total,
        "total_usd_approx": round(total / 1350, 0),
        "longest_assay_weeks": weeks_max,
        "n_assays": len(breakdown),
        "breakdown": breakdown,
    }


def render_quote_markdown(estimate: dict) -> str:
    """학술 / 임상 보고용 견적서 (한글 markdown)."""
    md = [f"# In vitro CRO 견적서 — {estimate['disease']}"]
    md.append(f"")
    md.append(f"- **대상**: top {estimate['n_compounds']} hit 화합물")
    md.append(f"- **티어**: {estimate['tier']}")
    md.append(f"- **총 assay 수**: {estimate['n_assays']}")
    md.append(f"- **예상 비용**: **{estimate['total_krw']:,} 원** "
              f"(~ ${estimate['total_usd_approx']:,.0f} USD)")
    md.append(f"- **소요 기간**: 최대 {estimate['longest_assay_weeks']}주")
    md.append("")
    md.append("## 견적 상세")
    md.append("")
    md.append("| 카테고리 | Assay | 타겟 | 유형 | 화합물 수 | 단가(원) | 소계(원) | 주 |")
    md.append("|----------|-------|------|------|-----------|---------:|---------:|----:|")
    for b in estimate["breakdown"]:
        md.append(f"| {b['category']} | {b['assay'][:50]} | {b['target']} | "
                  f"{b['type']} | {b['n_compounds']} | "
                  f"{b['cost_per_compound_krw']:,} | "
                  f"**{b['subtotal_krw']:,}** | {b['weeks']} |")
    md.append("")
    md.append(f"**합계: {estimate['total_krw']:,} 원**")
    md.append("")
    md.append("## 권장 한국 CRO")
    md.append("- **Bioneer** (대전): 핵산·biochemical 강점")
    md.append("- **Macrogen** (서울): cell-based 종합")
    md.append("- **KIST 분원** (강릉/전주): 천연물 특화")
    md.append("- **임상유전체사업단**: 정부 연구비 매칭 가능")
    md.append("")
    md.append("> ⚠️ 위 가격은 2026 평균 추정. 실제 견적은 각 CRO 직접 문의 필수.")
    return "\n".join(md)
