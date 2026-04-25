"""Regression detector — 우리 hypothesis가 새 paper로 부정되는지 감지."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date

from ..monitoring import semantic_scholar_search


@dataclass
class Hypothesis:
    """우리 시스템의 단일 가설."""
    name: str
    statement: str
    keywords: list[str] = field(default_factory=list)   # 검색 키워드
    expected_direction: str = "positive"   # "positive" | "negative"


@dataclass
class HypothesisCheck:
    hypothesis: Hypothesis
    n_supporting: int = 0
    n_contradicting: int = 0
    n_neutral: int = 0
    sample_papers: list[dict] = field(default_factory=list)
    alert_level: str = "ok"   # "ok" | "warning" | "critical"
    notes: str = ""


# 부정적 keywords
NEGATIVE_KW = [
    "no effect", "not effective", "fails to", "ineffective",
    "no significant", "abolish", "no inhibition", "no binding",
    "antagonist of efficacy", "trial failure",
]
POSITIVE_KW = [
    "inhibits", "binds", "reduces", "ameliorates", "improves",
    "effective", "promotes", "anti-fibrotic", "regenerative",
]


def _classify_paper(text: str) -> str:
    text_lower = text.lower()
    n_neg = sum(1 for kw in NEGATIVE_KW if kw in text_lower)
    n_pos = sum(1 for kw in POSITIVE_KW if kw in text_lower)
    if n_neg > n_pos:
        return "contradicting"
    if n_pos > n_neg:
        return "supporting"
    return "neutral"


def check_against_papers(h: Hypothesis, max_papers: int = 20) -> HypothesisCheck:
    """Semantic Scholar에서 hypothesis 키워드 검색 → support/contradict 분류."""
    query = " ".join(h.keywords)
    s2 = semantic_scholar_search(query, limit=max_papers, year_min=2024)
    papers = s2.get("data", [])

    chk = HypothesisCheck(hypothesis=h)
    for p in papers:
        text = (p.get("title") or "") + " " + (p.get("abstract") or "")
        cls = _classify_paper(text)
        if cls == "contradicting":
            chk.n_contradicting += 1
        elif cls == "supporting":
            chk.n_supporting += 1
        else:
            chk.n_neutral += 1
        if len(chk.sample_papers) < 5:
            chk.sample_papers.append({
                "title": (p.get("title") or "")[:160],
                "year": p.get("year"),
                "venue": p.get("venue"),
                "doi": (p.get("externalIds") or {}).get("DOI"),
                "classification": cls,
            })

    # alert level 결정
    n_total = chk.n_supporting + chk.n_contradicting + chk.n_neutral
    if n_total == 0:
        chk.alert_level = "ok"
        chk.notes = "관련 paper 없음 (계속 novel)"
    else:
        contradict_ratio = chk.n_contradicting / n_total
        if contradict_ratio >= 0.5:
            chk.alert_level = "critical"
            chk.notes = f"⚠️ 부정 보고가 다수 ({chk.n_contradicting}/{n_total}). 가설 재검토 필요."
        elif contradict_ratio >= 0.2:
            chk.alert_level = "warning"
            chk.notes = f"부정 보고 일부 ({chk.n_contradicting}/{n_total}). 차별점 명시."
        else:
            chk.alert_level = "ok"
            chk.notes = f"지지 보고 우세 ({chk.n_supporting}/{n_total})."
    return chk


# 우리 시스템의 핵심 가설들 (추가/수정 자유)
MAIN_HYPOTHESES = [
    Hypothesis(
        name="Embelin × TGF-β1 anti-fibrotic",
        statement="Embelin은 TGF-β1에 결합하여 흉터 섬유화를 억제할 가능성이 있다",
        keywords=["embelin", "TGF-beta", "fibrosis"],
    ),
    Hypothesis(
        name="Acetylshikonin (자운고) anti-scar",
        statement="자운고의 acetylshikonin이 scar regeneration에 기여",
        keywords=["acetylshikonin", "scar", "wound"],
    ),
    Hypothesis(
        name="EGCG multi-skin",
        statement="EGCG가 모든 5 피부 질환에 분자 결합 가능",
        keywords=["EGCG", "skin", "dermatology"],
    ),
    Hypothesis(
        name="Spirulina phycocyanin × scar",
        statement="Spirulina-derived phycocyanin이 hypertrophic scar에 효능 (paper 0건 → 새 가설)",
        keywords=["phycocyanin", "scar", "fibrosis"],
    ),
]


def monitor_main_hypotheses() -> list[HypothesisCheck]:
    """우리 핵심 가설 일괄 검사."""
    out = []
    for h in MAIN_HYPOTHESES:
        chk = check_against_papers(h)
        out.append(chk)
    return out


def render_conflict_report(checks: list[HypothesisCheck]) -> str:
    """markdown 리포트."""
    md = ["# Conflict Detector Report", "",
          f"생성: {date.today().isoformat()}",
          f"가설 검사 수: {len(checks)}", ""]
    md.append("| Hypothesis | Support | Contradict | Neutral | Alert |")
    md.append("|------------|--------:|-----------:|--------:|-------|")
    for c in checks:
        emoji = {"ok": "✅", "warning": "🟡", "critical": "🔴"}.get(c.alert_level, "?")
        md.append(f"| {c.hypothesis.name} | {c.n_supporting} | "
                  f"{c.n_contradicting} | {c.n_neutral} | {emoji} {c.alert_level} |")
    md.append("")
    for c in checks:
        if c.alert_level != "ok":
            md.append(f"## ⚠️ {c.hypothesis.name}")
            md.append(f"- {c.notes}")
            for p in c.sample_papers[:3]:
                md.append(f"  - [{p['classification']}] {p['title']} "
                          f"({p['year']}, DOI: {p['doi']})")
            md.append("")
    return "\n".join(md)
