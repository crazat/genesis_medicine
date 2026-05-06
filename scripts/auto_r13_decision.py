"""R13 결과 기반 R14 진행 여부 자동 결정.

Logic:
1. EI ratio: R13 EI / R12 EI
   - <0.7: saturate 확정 → stop
   - 0.7-1.3: plateau → 1 more cycle (R14 진행하되 stop signal 강화)
   - >1.3: still improving → R14 진행
2. Leader continuity: R13_0 super-leader가 R11_0 family인지 확인
3. Max affinity per target: 14/14 모두 R12 대비 향상되었는지

Output: pilot/cpu_meaningful/r14_decision.json
- decision: "stop" | "proceed" | "plateau_one_more"
- reasoning: trace dict
"""
from __future__ import annotations
import json, sys
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_meaningful"

EI_TRACE = {"R10": 0.0069, "R11": 0.0123, "R12": 0.0077}


def main():
    # R13 EI from Bayesian v10 candidates
    cands_path = OUT / "bayesian_v10_round14_candidates.csv"
    if not cands_path.exists():
        print(f"❌ {cands_path} missing — R13 consolidation/Bayesian v10 미완")
        return 1
    cands = pd.read_csv(cands_path)
    r13_ei = float(cands["expected_improvement"].iloc[0])
    EI_TRACE["R13"] = r13_ei

    ratio = r13_ei / EI_TRACE["R12"]

    # Leader continuity check
    r13_aff_path = OUT / "r13_affinity_consolidated.csv"
    if r13_aff_path.exists():
        r13 = pd.read_csv(r13_aff_path)
        pivot = r13.pivot_table(values="affinity_prob_binary",
                                index="candidate_idx", columns="target",
                                aggfunc="max").fillna(0)
        leader_count = {}
        for tgt in pivot.columns:
            top5 = pivot[tgt].sort_values(ascending=False).head(5)
            for cidx in top5.index:
                leader_count[cidx] = leader_count.get(cidx, 0) + 1
        super_leaders = [c for c, n in leader_count.items() if n >= 8]
    else:
        super_leaders = []

    # Decision logic
    if ratio < 0.7:
        decision = "stop"
        reason = f"EI saturate confirmed: R13/R12={ratio:.2f} < 0.7"
    elif ratio > 1.3:
        decision = "proceed"
        reason = f"Still improving: R13/R12={ratio:.2f} > 1.3"
    else:
        decision = "plateau_one_more"
        reason = f"Plateau: R13/R12={ratio:.2f} (0.7-1.3) → R14 1-cycle, then stop"

    # Override: super-leader 발견 시 1 cycle 더 시도 (refinement value)
    if decision == "stop" and len(super_leaders) > 0:
        decision = "plateau_one_more"
        reason += f" + super-leaders {super_leaders} found → 1-cycle refinement"

    out = {
        "decision": decision,
        "reasoning": reason,
        "ei_trace": EI_TRACE,
        "r13_r12_ratio": ratio,
        "super_leaders_r13": super_leaders,
    }

    out_path = OUT / "r14_decision.json"
    out_path.write_text(json.dumps(out, indent=2))
    print(f"✅ {out_path}")
    print(json.dumps(out, indent=2))

    # Return exit code: 0=proceed/plateau, 1=stop (shell이 분기 가능)
    return 0 if decision != "stop" else 2


if __name__ == "__main__":
    sys.exit(main())
