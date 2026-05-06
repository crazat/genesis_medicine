"""Write AI/model governance registry and lightweight model cards."""
from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_meaningful"
DOC = ROOT / "docs/MODEL_GOVERNANCE_REGISTRY.md"
CSV_OUT = OUT / "ai_model_governance_registry.csv"
CARD_DIR = ROOT / "docs/model_cards"

MODELS = [
    {
        "model_id": "boltz2_cofold",
        "component": "Boltz-2 cofold affinity/confidence",
        "context_of_use": "protein-ligand cofold triage for skin target hypotheses",
        "decision_influence": "high",
        "decision_consequence": "medium",
        "risk_tier": "tier2",
        "validation_status": "local calibration and PoseBusters/MD cross-check required",
        "uncertainty_controls": "confidence_score, ligand_iptm, replicate affinity heads, pose sanity gate",
        "allowed_claim": "in silico prioritization only; no binding or efficacy claim",
    },
    {
        "model_id": "openmm_md",
        "component": "OpenMM molecular dynamics",
        "context_of_use": "pose stability and drift/failure-mode assessment",
        "decision_influence": "high",
        "decision_consequence": "medium",
        "risk_tier": "tier2",
        "validation_status": "trajectory RMSD summaries; force-field and timescale caveats remain",
        "uncertainty_controls": "replicate/extension MD, last-third RMSD, drift caveat",
        "allowed_claim": "short-timescale stability support only",
    },
    {
        "model_id": "admet_ai",
        "component": "ADMET-AI predictors",
        "context_of_use": "AMES/hERG/DILI/skin reaction prefiltering",
        "decision_influence": "medium",
        "decision_consequence": "medium",
        "risk_tier": "tier2",
        "validation_status": "external model; no local wet-lab validation yet",
        "uncertainty_controls": "orthogonal counterscreen and dermal regulatory gate",
        "allowed_claim": "predicted safety risk only",
    },
    {
        "model_id": "rdkit_descriptors",
        "component": "RDKit physicochemical descriptors",
        "context_of_use": "skin-window, CMC, novelty, scaffold and formulation heuristics",
        "decision_influence": "medium",
        "decision_consequence": "low",
        "risk_tier": "tier1",
        "validation_status": "deterministic cheminformatics; salt/tautomer review needed",
        "uncertainty_controls": "canonicalization, duplicate checks, manual review",
        "allowed_claim": "descriptor-based heuristic only",
    },
    {
        "model_id": "active_learning_rf",
        "component": "RandomForest active-learning surrogate",
        "context_of_use": "next cofold/docking candidate acquisition",
        "decision_influence": "medium",
        "decision_consequence": "low",
        "risk_tier": "tier1",
        "validation_status": "local scaffold-domain gate and leave-one-out MAE",
        "uncertainty_controls": "tree ensemble variance, applicability-domain gate",
        "allowed_claim": "queue selection heuristic only",
    },
    {
        "model_id": "xtb_gfn2",
        "component": "xTB GFN2/ALPB refinement",
        "context_of_use": "conformer and quantum descriptor refinement for NPASS candidates",
        "decision_influence": "medium",
        "decision_consequence": "low",
        "risk_tier": "tier1",
        "validation_status": "methodology/atlas support; not direct activity evidence",
        "uncertainty_controls": "conformer ladder stability and source tracking",
        "allowed_claim": "quantum descriptor prioritization only",
    },
    {
        "model_id": "open_targets_evidence",
        "component": "Open Targets / evidence gates",
        "context_of_use": "target prioritization and claim strength limitation",
        "decision_influence": "high",
        "decision_consequence": "medium",
        "risk_tier": "tier2",
        "validation_status": "API-derived evidence with manual biological interpretation",
        "uncertainty_controls": "green/yellow/red gate and disease-context notes",
        "allowed_claim": "target evidence support only",
    },
    {
        "model_id": "codex_curator_loop",
        "component": "Codex autonomous curator",
        "context_of_use": "compute queueing, paper queueing, and decision documentation",
        "decision_influence": "high",
        "decision_consequence": "medium",
        "risk_tier": "tier2",
        "validation_status": "human-supervised automation; logs/provenance required",
        "uncertainty_controls": "protected PID rules, no duplicate outputs, provenance manifest, action log",
        "allowed_claim": "automation workflow support only",
    },
]


def card_name(model_id: str) -> str:
    return model_id.lower().replace("/", "_").replace(" ", "_") + ".md"


def write_cards(now: str) -> None:
    CARD_DIR.mkdir(parents=True, exist_ok=True)
    for model in MODELS:
        lines = [
            f"# Model Card: {model['model_id']}",
            "",
            f"- timestamp: `{now}`",
            f"- component: `{model['component']}`",
            f"- context_of_use: `{model['context_of_use']}`",
            f"- decision_influence: `{model['decision_influence']}`",
            f"- decision_consequence: `{model['decision_consequence']}`",
            f"- risk_tier: `{model['risk_tier']}`",
            f"- validation_status: `{model['validation_status']}`",
            f"- uncertainty_controls: `{model['uncertainty_controls']}`",
            f"- allowed_claim: `{model['allowed_claim']}`",
            "",
            "## Required Controls",
            "",
            "- Record input/output file paths in `docs/RUN_PROVENANCE_MANIFEST.md`.",
            "- Do not use this component as standalone evidence for clinical or wet-lab efficacy.",
            "- If output conflicts with orthogonal evidence, downgrade manuscript claim strength.",
            "",
        ]
        (CARD_DIR / card_name(str(model["model_id"]))).write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    now = datetime.now(ZoneInfo("Asia/Seoul")).isoformat(timespec="seconds")
    with CSV_OUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(MODELS[0].keys()))
        writer.writeheader()
        writer.writerows(MODELS)
    write_cards(now)

    lines = [
        "# Model Governance Registry",
        "",
        f"- timestamp: `{now}`",
        f"- registry_csv: `{CSV_OUT.relative_to(ROOT)}`",
        f"- model_cards: `{CARD_DIR.relative_to(ROOT)}`",
        "- purpose: FDA-style context-of-use, risk, validation, monitoring 관점으로 AI/ML/automation component를 관리한다.",
        "",
        "## Registry",
        "",
        "| model | risk | context of use | validation status | allowed claim |",
        "|---|---|---|---|---|",
    ]
    for model in MODELS:
        lines.append(
            f"| {model['model_id']} | {model['risk_tier']} | {model['context_of_use']} | {model['validation_status']} | {model['allowed_claim']} |"
        )
    lines.extend(
        [
            "",
            "## Curator Rule",
            "",
            "- `tier2` component가 paper main claim에 영향을 주면 orthogonal check 또는 명확한 limitation이 필요하다.",
            "- model card가 없는 새 predictor/agent는 manuscript evidence로 쓰지 않는다.",
            "- retraining, prompt update, version change가 있으면 registry와 provenance manifest를 같이 갱신한다.",
            "",
        ]
    )
    DOC.write_text("\n".join(lines), encoding="utf-8")
    print(f"Saved {CSV_OUT.relative_to(ROOT)}")
    print(f"Saved {DOC.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
