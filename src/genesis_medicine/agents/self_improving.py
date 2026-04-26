"""AlphaProof-style Self-Improving Agent for chemistry discovery.

Genesis_Medicine v3 ChemCrow wrapper의 다음 단계:
  1. Hypothesis 자동 생성 (LLM)
  2. 자동 검증 (cofold/MD/ABFE 호출)
  3. 결과 학습 (memory + reward)
  4. Hypothesis 갱신 (다음 라운드)

AlphaProof (Nature 2025) 핵심 원리:
  - 자체 generated experience로 학습
  - RL on auto-formalized problems
  - Self-improvement loop

Walters insight (2025):
  - "wet-lab autonomy is not text problem" — instrument actions/constraints/costs/rewards
  - 우리는 in silico autonomy (1단계). wet-lab autonomy (Strateos 등)는 다음.

라이선스: 우리 자체 구현. Anthropic API 사용.
"""

from __future__ import annotations

import json
import os
import warnings
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

warnings.filterwarnings("ignore")

from .._env import load_dotenv_once

ROOT = Path(__file__).resolve().parents[3]
MEMORY_DIR = ROOT / ".cache/agent_memory"
MEMORY_DIR.mkdir(parents=True, exist_ok=True)


@dataclass
class Hypothesis:
    """단일 가설."""

    id: str = ""
    statement: str = ""           # "EMB-3가 LPA1에도 ≥0.5 affinity로 결합한다"
    expected_outcome: str = ""
    test_method: str = ""         # "cofold_boltz2(emb3, ['LPAR1'])"
    priority: float = 1.0
    parent_hypothesis: str = ""   # 어떤 가설에서 파생


@dataclass
class TestResult:
    """가설 검증 결과."""

    hypothesis_id: str = ""
    success: bool = False
    measured_value: float | dict = 0.0
    expected_value: float | dict = 0.0
    delta: float = 0.0
    interpretation: str = ""
    timestamp: str = ""


@dataclass
class AgentMemory:
    """누적 메모리 (장기 학습)."""

    hypotheses: list = field(default_factory=list)
    results: list = field(default_factory=list)
    learned_patterns: list = field(default_factory=list)
    iteration: int = 0


def load_memory() -> AgentMemory:
    p = MEMORY_DIR / "memory.json"
    if not p.exists():
        return AgentMemory()
    d = json.loads(p.read_text())
    return AgentMemory(
        hypotheses=[Hypothesis(**h) for h in d.get("hypotheses", [])],
        results=[TestResult(**r) for r in d.get("results", [])],
        learned_patterns=d.get("learned_patterns", []),
        iteration=d.get("iteration", 0),
    )


def save_memory(memory: AgentMemory) -> None:
    p = MEMORY_DIR / "memory.json"
    p.write_text(json.dumps({
        "hypotheses": [h.__dict__ for h in memory.hypotheses],
        "results": [r.__dict__ for r in memory.results],
        "learned_patterns": memory.learned_patterns,
        "iteration": memory.iteration,
    }, indent=2, default=str, ensure_ascii=False))


# ════════════════════════════════════════════════════════════════════════
# 가설 생성기 — LLM call
# ════════════════════════════════════════════════════════════════════════

DEFAULT_HYPOTHESIS_PROMPT = """\
You are a self-improving drug discovery agent for Genesis_Medicine v3.
Project: 한약·피부재생 신약 (EMB-3 lead, IPF cross-disease).

Past results in memory:
{past_results_summary}

Available pipeline tools:
- cofold_boltz2(smiles, targets) — affinity prediction
- md_validate(cif, smiles, ns) — 10ns ligand RMSD
- abfe_quantitative — kcal/mol ΔG (6h GPU)
- cross_disease_score — Open Targets fibrosis indication
- cryptic_pocket_scan — Fpocket allosteric site
- ddi_predict — TCM herb interaction
- pbpk_simulate — topical 3-comp PBPK

Generate **5 NEW hypotheses** that:
1. Build on past results (do not repeat)
2. Have clear test method (specific tool call)
3. If successful, advance paper or sales pitch
4. Prioritize testable in <1 hour GPU

Output JSON list:
[
  {{
    "statement": "...",
    "expected_outcome": "...",
    "test_method": "tool_name(args)",
    "priority": 0-1
  }},
  ...
]
"""


def generate_hypotheses(memory: AgentMemory, n: int = 5) -> list[Hypothesis]:
    """LLM으로 새 hypothesis 생성."""
    load_dotenv_once()
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        # Fallback: heuristic hypothesis
        return _heuristic_hypotheses(memory, n)

    try:
        from anthropic import Anthropic
    except ImportError:
        return _heuristic_hypotheses(memory, n)

    summary = "\n".join(
        f"- {r.hypothesis_id}: {'✅' if r.success else '❌'} {r.interpretation[:80]}"
        for r in memory.results[-10:]
    ) or "(empty)"

    client = Anthropic(api_key=api_key)
    response = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=2048,
        messages=[{
            "role": "user",
            "content": DEFAULT_HYPOTHESIS_PROMPT.format(
                past_results_summary=summary,
            ),
        }],
    )

    text = "".join(b.text for b in response.content if b.type == "text")
    try:
        # JSON 파싱 — markdown ``` 처리
        text = text.strip()
        if "```" in text:
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
            text = text.strip()
        items = json.loads(text)
        hypotheses = []
        for i, item in enumerate(items[:n]):
            hypotheses.append(Hypothesis(
                id=f"H{memory.iteration}-{i+1}",
                statement=item.get("statement", ""),
                expected_outcome=item.get("expected_outcome", ""),
                test_method=item.get("test_method", ""),
                priority=float(item.get("priority", 0.5)),
            ))
        return hypotheses
    except (json.JSONDecodeError, KeyError, IndexError) as e:
        return _heuristic_hypotheses(memory, n)


def _heuristic_hypotheses(memory: AgentMemory, n: int = 5) -> list[Hypothesis]:
    """LLM 미사용 fallback — 기본 hypothesis 패턴."""
    base_hypotheses = [
        Hypothesis(id=f"H{memory.iteration}-1",
                    statement="EMB-3가 신규 4 mechanotransduction 타겟 (LPA1/αvβ6/YAP1/TAZ)에 ≥0.5 binding",
                    test_method="cofold_boltz2(emb3, ['LPAR1', 'ITGB6', 'YAP1', 'WWTR1'])",
                    priority=0.95),
        Hypothesis(id=f"H{memory.iteration}-2",
                    statement="자운고 + EMB-3 5-component 조합이 CI < 0.85 (synergy)",
                    test_method="evaluate_combination_chou_talalay(...)",
                    priority=0.9),
        Hypothesis(id=f"H{memory.iteration}-3",
                    statement="EMB-3 residence time이 Embelin보다 10× 더 김",
                    test_method="koff_md_simulation(emb3 vs embelin)",
                    priority=0.85),
        Hypothesis(id=f"H{memory.iteration}-4",
                    statement="Recover 한의원 환자 흉터 fibroblast subtype = TGFβ-signaling 우세",
                    test_method="spatial_transcriptomics_analysis(recover_biopsy)",
                    priority=0.7),
        Hypothesis(id=f"H{memory.iteration}-5",
                    statement="Embelin 전체-길이 P01137 (latent LAP) cryptic site에 더 강한 결합",
                    test_method="cryptic_cofold(P01137_full, embelin)",
                    priority=0.8),
    ]
    return base_hypotheses[:n]


def validate_hypothesis(h: Hypothesis) -> TestResult:
    """가설 검증 — 우리 파이프라인 도구 호출 (placeholder).

    실제 운영 시 ChemCrow wrapper의 execute_tool() 호출.
    여기서는 인터페이스만.
    """
    return TestResult(
        hypothesis_id=h.id,
        success=False,   # 실제 호출 후 갱신
        interpretation=(f"검증 stub — 실제 호출은 {h.test_method}, "
                        f"chemcrow_wrapper.execute_tool()에 위임"),
        timestamp=date.today().isoformat(),
    )


def learn_from_results(memory: AgentMemory) -> list[str]:
    """누적 결과에서 패턴 추출 (간이 RL).

    예시 패턴:
      - "neutral 천연물 + ≤500 MW = topical bias 우세"
      - "Quinone family + Cys-rich pocket = 강한 covalent binding"
    """
    patterns = []
    success_count = sum(1 for r in memory.results if r.success)
    total = len(memory.results)
    if total > 0:
        patterns.append(
            f"전체 가설 검증 success rate: {success_count}/{total} "
            f"({success_count/total*100:.0f}%)"
        )

    # 카테고리별 패턴
    by_method = {}
    for r in memory.results:
        method = r.hypothesis_id.split("-")[0] if "-" in r.hypothesis_id else "unknown"
        by_method.setdefault(method, []).append(r.success)
    for method, results in by_method.items():
        if results:
            sr = sum(results) / len(results)
            patterns.append(f"{method} success rate: {sr*100:.0f}%")

    return patterns


def run_self_improvement_iteration(n_hypotheses: int = 5) -> dict:
    """Self-improvement 한 라운드.

    1. Memory load
    2. 새 hypothesis 생성
    3. 각 hypothesis 검증 (실제 도구 호출은 placeholder)
    4. Memory 업데이트
    5. 학습 패턴 추출
    """
    memory = load_memory()
    memory.iteration += 1
    print(f"=== Self-Improvement iteration {memory.iteration} ===\n")

    # 1. 새 hypothesis 생성
    print(f"[1/3] Hypothesis 생성 ({n_hypotheses}개)")
    new_h = generate_hypotheses(memory, n=n_hypotheses)
    for h in new_h:
        print(f"  - [{h.id}] {h.statement[:80]} (priority {h.priority:.2f})")
    memory.hypotheses.extend(new_h)

    # 2. 검증 (placeholder — 실제는 도구 호출)
    print(f"\n[2/3] 검증 (placeholder)")
    new_results = []
    for h in new_h:
        r = validate_hypothesis(h)
        new_results.append(r)
        print(f"  - [{h.id}] {r.interpretation[:80]}")
    memory.results.extend(new_results)

    # 3. 패턴 학습
    print(f"\n[3/3] 패턴 학습")
    memory.learned_patterns = learn_from_results(memory)
    for p in memory.learned_patterns:
        print(f"  • {p}")

    save_memory(memory)
    return {
        "iteration": memory.iteration,
        "n_new_hypotheses": len(new_h),
        "n_total_hypotheses": len(memory.hypotheses),
        "n_results": len(memory.results),
        "patterns": memory.learned_patterns,
    }
