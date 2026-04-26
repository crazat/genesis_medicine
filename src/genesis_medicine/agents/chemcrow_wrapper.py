"""ChemCrow-style LLM agent — Genesis_Medicine v3 자연어 wrapper.

ChemCrow (Bran et al. 2024 Nat MI)의 18 chemistry tools 패턴을 우리 14단계
파이프라인에 적용. Anthropic Claude API + tool definitions로 자연어 요청을
파이프라인 자율 실행으로 변환.

예시 요청:
  "EMB-3와 비슷한 hERG 더 낮은 후보 30개 만들어서 TGFB1 affinity 검증"
  → tool_calls: [
      generate_scaffold_hop("EMB-3", n=30, target_endpoints=["hERG_lower"]),
      filter_admet(...),
      cofold_boltz2(targets=["TGFB1"]),
      summarize()
    ]

라이선스: 우리 시스템(Apache-2.0/MIT)에 ChemCrow 패턴만 차용 (라이선스 무관).
LLM API key는 .env (ANTHROPIC_API_KEY).
"""

from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

from .._env import load_dotenv_once

ROOT = Path(__file__).resolve().parents[3]


@dataclass
class Tool:
    """단일 파이프라인 도구."""

    name: str
    description: str
    input_schema: dict
    func: Callable[..., dict]
    license_profile: str = "commercial"   # research | commercial


@dataclass
class AgentSession:
    """LLM agent 실행 세션."""

    user_query: str
    tool_calls: list = field(default_factory=list)
    tool_results: list = field(default_factory=list)
    final_summary: str = ""
    total_tokens: int = 0


# ═══════════════════════════════════════════════════════════════════════════
# Genesis_Medicine v3 Tool Catalog (14단계 파이프라인 매핑)
# ═══════════════════════════════════════════════════════════════════════════


def _tool_target_discovery(disease: str, n_targets: int = 5) -> dict:
    """Stage 1: 질환 → Open Targets로 타겟 후보 발굴."""
    try:
        from ..external_apis.open_targets import OT_ENDPOINT
        # 간소화 — 실제 구현은 io/open_targets.py
        return {
            "stage": 1,
            "disease": disease,
            "targets": ["TGFB1", "MMP1", "CTGF"][:n_targets],
            "note": "stub — 실제 호출 시 io/open_targets.fetch_associated_targets()",
        }
    except ImportError:
        return {"error": "open_targets 모듈 미로드"}


def _tool_cryptic_scan(target_uniprot: str) -> dict:
    """Stage 2.5: Fpocket으로 cryptic site 스캔."""
    summary_csv = ROOT / "pilot/scaffold_hop/cryptic_scan/summary.csv"
    if summary_csv.exists():
        import pandas as pd
        df = pd.read_csv(summary_csv)
        return {"stage": 2.5, "uniprot": target_uniprot,
                "scan_results": df.to_dict("records")}
    return {"error": "cryptic_scan 결과 없음 — scripts/run_cryptic_scan.py 먼저"}


def _tool_scaffold_hop(seed_smiles: str, n: int = 100) -> dict:
    """Stage 5: REINVENT 4 mol2mol scaffold hopping."""
    return {
        "stage": 5, "seed": seed_smiles, "n_requested": n,
        "instruction": ("scripts/run_scaffold_hop.py 또는 round2 실행. "
                         "seed SMILES를 reinvent_inputs/seed.smi에 저장 후 cli."),
    }


def _tool_filter_admet(smiles_list: list[str], rules: dict | None = None) -> dict:
    """Stage 6: ADMET-AI + logKp + topical safety filter."""
    return {
        "stage": 6, "n_input": len(smiles_list),
        "rules": rules or {"hERG": "≤ 0.3", "Skin_Reaction": "≤ 0.3",
                            "logP": "1.5-3.5", "logKp": "≥ -2 (외용)"},
        "instruction": "scripts/analyze_scaffold_hop.py + logkp_model.pkl 사용",
    }


def _tool_cofold_boltz2(smiles: str, targets: list[str]) -> dict:
    """Stage 4: Boltz-2 cofold + affinity."""
    return {"stage": 4, "smiles": smiles, "targets": targets,
            "instruction": "scripts/run_scaffold_hop_cofold.py 패턴",
            "note": "각 cofold ~30s GPU"}


def _tool_md_validate(cif_path: str, smiles: str, ns: float = 10) -> dict:
    """Stage 8: 10 ns MD ligand stability."""
    return {"stage": 8, "ns": ns, "cif": cif_path,
            "instruction": "genesis-md env에서 OpenMM + AMBER ff14SB",
            "note": "~7분/run RTX 5090"}


def _tool_abfe_quantitative(cif_path: str, smiles: str) -> dict:
    """Stage 11: ABFE 정량 ΔG."""
    return {"stage": 11,
            "instruction": "scripts/run_emb3_abfe_full.py 패턴",
            "note": "16 windows × 5 ns × 17 replicas, ~6h GPU"}


def _tool_cross_disease(target_list: list[str], affinities: dict[str, float]) -> dict:
    """Stage 4.5: Open Targets cross-disease 매핑."""
    return {"stage": 4.5,
            "instruction": "scripts/run_cross_disease.py",
            "note": "fibrosis non-skin indication ranking"}


def _tool_herb_mapping(smiles: str) -> dict:
    """Stage 7: 한방 처방 매핑."""
    return {"stage": 7,
            "instruction": "scripts/run_emb3_herb_mapping.py",
            "note": "1,4-benzoquinone scaffold → 자운고/활혈거어탕 등"}


def _tool_cro_quote(compound_name: str, disease: str = "scar") -> dict:
    """Stage 13: CRO 견적 자동 생성."""
    return {"stage": 13,
            "instruction": "scripts/run_emb3_cro_quote.py",
            "note": "Tier 1 ₩1,560만 / 6-10주"}


def _tool_manuscript_build(template: str = "j-cheminformatics") -> dict:
    """Stage 14: Pandoc + CSL → HTML/DOCX/PDF."""
    return {"stage": 14,
            "instruction": "scripts/build_emb3_manuscript.py + manuscript_to_pdf.sh",
            "templates": ["nature", "phytomedicine", "j-cheminformatics"]}


# 도구 카탈로그 — Anthropic tools 형식
TOOLS: list[Tool] = [
    Tool(
        name="target_discovery",
        description="질환명을 받아서 Open Targets로 단백질 표적 후보 발굴.",
        input_schema={"type": "object",
                      "properties": {"disease": {"type": "string"},
                                     "n_targets": {"type": "integer",
                                                    "default": 5}},
                      "required": ["disease"]},
        func=_tool_target_discovery,
    ),
    Tool(
        name="cryptic_pocket_scan",
        description="단백질에 Fpocket으로 cryptic site (canonical 외 결합 가능 부위) 식별.",
        input_schema={"type": "object",
                      "properties": {"target_uniprot": {"type": "string"}},
                      "required": ["target_uniprot"]},
        func=_tool_cryptic_scan,
    ),
    Tool(
        name="scaffold_hop",
        description="seed 분자에서 mol2mol_medium_similarity로 변형 분자 생성.",
        input_schema={"type": "object",
                      "properties": {"seed_smiles": {"type": "string"},
                                     "n": {"type": "integer", "default": 100}},
                      "required": ["seed_smiles"]},
        func=_tool_scaffold_hop,
    ),
    Tool(
        name="filter_admet",
        description="ADMET-AI + 자체 logKp + 외용 안전성 게이트로 필터링.",
        input_schema={"type": "object",
                      "properties": {"smiles_list": {"type": "array",
                                                       "items": {"type": "string"}},
                                     "rules": {"type": "object"}},
                      "required": ["smiles_list"]},
        func=_tool_filter_admet,
    ),
    Tool(
        name="cofold_boltz2",
        description="Boltz-2로 단백질·리간드 cofold + affinity_probability_binary 예측.",
        input_schema={"type": "object",
                      "properties": {"smiles": {"type": "string"},
                                     "targets": {"type": "array",
                                                  "items": {"type": "string"}}},
                      "required": ["smiles", "targets"]},
        func=_tool_cofold_boltz2,
    ),
    Tool(
        name="md_validate",
        description="OpenMM 8.5 + AMBER ff14SB로 10 ns MD ligand RMSD 검증.",
        input_schema={"type": "object",
                      "properties": {"cif_path": {"type": "string"},
                                     "smiles": {"type": "string"},
                                     "ns": {"type": "number", "default": 10}},
                      "required": ["cif_path", "smiles"]},
        func=_tool_md_validate,
    ),
    Tool(
        name="abfe_quantitative",
        description="openmmtools alchemical RE로 정량 ΔG (kcal/mol) 계산. ~6h GPU.",
        input_schema={"type": "object",
                      "properties": {"cif_path": {"type": "string"},
                                     "smiles": {"type": "string"}},
                      "required": ["cif_path", "smiles"]},
        func=_tool_abfe_quantitative,
    ),
    Tool(
        name="cross_disease_score",
        description="Open Targets로 affinity-weighted cross-disease 적용성 평가.",
        input_schema={"type": "object",
                      "properties": {"target_list": {"type": "array",
                                                      "items": {"type": "string"}},
                                     "affinities": {"type": "object"}},
                      "required": ["target_list", "affinities"]},
        func=_tool_cross_disease,
    ),
    Tool(
        name="herb_mapping",
        description="천연물 SMILES이 함유된 한방 처방 매핑 (자운고 등).",
        input_schema={"type": "object",
                      "properties": {"smiles": {"type": "string"}},
                      "required": ["smiles"]},
        func=_tool_herb_mapping,
    ),
    Tool(
        name="cro_quote",
        description="EMB-3 등 lead 화합물의 한국 CRO 견적 자동 생성.",
        input_schema={"type": "object",
                      "properties": {"compound_name": {"type": "string"},
                                     "disease": {"type": "string",
                                                  "default": "scar"}},
                      "required": ["compound_name"]},
        func=_tool_cro_quote,
    ),
    Tool(
        name="build_manuscript",
        description="결과 통합 → manuscript.md + Pandoc + CSL → PDF.",
        input_schema={"type": "object",
                      "properties": {"template": {"type": "string",
                                                    "default": "j-cheminformatics"}}},
        func=_tool_manuscript_build,
    ),
]


def to_anthropic_tools() -> list[dict]:
    """Anthropic tools 형식으로 변환."""
    return [{"name": t.name, "description": t.description,
             "input_schema": t.input_schema} for t in TOOLS]


def execute_tool(name: str, args: dict) -> dict:
    """Tool 호출 라우팅."""
    for t in TOOLS:
        if t.name == name:
            try:
                return t.func(**args)
            except Exception as e:
                return {"error": f"{type(e).__name__}: {e}"}
    return {"error": f"unknown tool: {name}"}


def run_agent(user_query: str, max_iter: int = 5) -> AgentSession:
    """Anthropic API로 자율 agent 실행.

    Args:
        user_query: 자연어 요청 (예: "EMB-3 hERG 더 낮은 후보 30개 만들기")
        max_iter: 최대 tool call 수

    Returns:
        AgentSession with tool_calls, tool_results, final_summary.
    """
    load_dotenv_once()
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return AgentSession(
            user_query=user_query, final_summary=(
                "❌ ANTHROPIC_API_KEY 미설정. .env에 추가하거나 환경변수 export."
            ),
        )

    try:
        from anthropic import Anthropic
    except ImportError:
        return AgentSession(
            user_query=user_query, final_summary=(
                "❌ anthropic 패키지 미설치. uv pip install anthropic"
            ),
        )

    client = Anthropic(api_key=api_key)
    session = AgentSession(user_query=user_query)

    system_prompt = (
        "You are Genesis_Medicine v3, a 한약·피부재생 신약 개발 파이프라인 agent. "
        "당신은 14단계 in silico drug discovery pipeline에 접근할 수 있다. "
        "사용자 요청을 분석해 적절한 tool을 순차/병렬 호출하고, 결과를 종합 보고하라. "
        "각 tool은 stage 번호를 가진 파이프라인 단계에 매핑된다. "
        "응답은 한국어로 하라. 라이선스 — commercial 빌드만 사용 (Apache/MIT/BSD)."
    )

    messages = [{"role": "user", "content": user_query}]

    for iter_idx in range(max_iter):
        response = client.messages.create(
            model="claude-opus-4-7",   # 또는 claude-sonnet-4-6
            max_tokens=4096,
            system=system_prompt,
            tools=to_anthropic_tools(),
            messages=messages,
        )
        session.total_tokens += (response.usage.input_tokens
                                  + response.usage.output_tokens)

        # tool_use 추출
        tool_uses = [b for b in response.content if b.type == "tool_use"]
        text_parts = [b.text for b in response.content if b.type == "text"]

        if not tool_uses:
            # 최종 답변
            session.final_summary = "\n".join(text_parts)
            break

        # 각 tool 실행
        tool_results = []
        for tu in tool_uses:
            result = execute_tool(tu.name, tu.input)
            session.tool_calls.append({"name": tu.name, "input": tu.input})
            session.tool_results.append(result)
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": tu.id,
                "content": json.dumps(result, default=str, ensure_ascii=False),
            })

        # 대화 이어가기
        messages.append({"role": "assistant", "content": response.content})
        messages.append({"role": "user", "content": tool_results})

    return session
