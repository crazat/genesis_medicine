"""Write a creative-discovery gap matrix for autonomous molecular design.

This script is intentionally lightweight. It launches no compute, imports no
TensorFlow/ADMET-AI, and only summarizes local evidence so the curator loop can
decide which creative-discovery technologies are ready, partial, or blocked.
"""
from __future__ import annotations

import csv
import json
import shutil
from collections import Counter
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd
import yaml


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_meaningful"
DOC = ROOT / "docs/CREATIVE_DISCOVERY_GAP_MATRIX.md"
CSV_OUT = OUT / "creative_discovery_gap_matrix.csv"
POLICY_OUT = ROOT / "pilot/creative_discovery_queue_policy.json"
ACTIVE_LEARNING = OUT / "active_learning_next_candidates.csv"
MSA_DIR = ROOT / "data/msa"


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()


def csv_rows(path: Path) -> int:
    if not path.exists() or path.stat().st_size == 0:
        return 0
    try:
        with path.open(newline="", encoding="utf-8") as handle:
            return max(sum(1 for _ in csv.reader(handle)) - 1, 0)
    except Exception:
        return 0


def cofold_result_paths() -> list[Path]:
    return [
        path
        for path in sorted(OUT.glob("active_learning_next_cofold_batch*.csv"))
        if not path.stem.endswith("_manifest")
    ]


def cofold_manifest_paths() -> list[Path]:
    return sorted(OUT.glob("active_learning_next_cofold_batch*_manifest.csv"))


def normalized_bool(series: pd.Series) -> pd.Series:
    return series.fillna("").astype(str).str.strip().str.lower().isin({"true", "1", "yes", "y"})


def completed_pairs() -> set[tuple[str, str]]:
    done: set[tuple[str, str]] = set()
    for path in cofold_result_paths():
        df = read_csv(path)
        if df.empty:
            continue
        for row in df.itertuples(index=False):
            candidate_id = str(getattr(row, "candidate_id", "")).strip()
            target = str(getattr(row, "target", "")).strip().lower()
            if candidate_id and target:
                done.add((candidate_id, target))
    return done


def active_learning_stats() -> dict[str, object]:
    df = read_csv(ACTIVE_LEARNING)
    if df.empty:
        return {
            "rows": 0,
            "pending_short_cofold_pairs": 0,
            "result_rows": 0,
            "manifest_rows": 0,
            "target_counts": {},
        }
    required = {"candidate_id", "target", "recommended_next_fidelity", "already_labeled_pair", "synthesis_gate"}
    if not required.issubset(df.columns):
        return {
            "rows": len(df),
            "pending_short_cofold_pairs": 0,
            "result_rows": sum(csv_rows(path) for path in cofold_result_paths()),
            "manifest_rows": sum(csv_rows(path) for path in cofold_manifest_paths()),
            "target_counts": {},
        }
    work = df.copy()
    work["target"] = work["target"].fillna("").astype(str).str.lower()
    work["candidate_id"] = work["candidate_id"].fillna("").astype(str)
    already_labeled = normalized_bool(work["already_labeled_pair"])
    done = completed_pairs()
    mask = (
        work["recommended_next_fidelity"].fillna("").astype(str).eq("Boltz-2 cofold")
        & ~already_labeled
        & work["synthesis_gate"].fillna("").astype(str).str.lower().ne("red")
        & work["target"].ne("mmp1")
    )
    pending = work.loc[mask].copy()
    if not pending.empty:
        pending = pending[
            ~pending.apply(lambda row: (str(row["candidate_id"]), str(row["target"]).lower()) in done, axis=1)
        ]
    if pending.empty:
        runnable = pending
        blocked_missing_msa = pending
    else:
        runnable_mask = pending["target"].map(lambda target: (MSA_DIR / f"{target}.a3m").exists())
        runnable = pending.loc[runnable_mask].copy()
        blocked_missing_msa = pending.loc[~runnable_mask].copy()
    target_counts = Counter(runnable["target"].tolist()) if not runnable.empty else Counter()
    blocked_target_counts = Counter(blocked_missing_msa["target"].tolist()) if not blocked_missing_msa.empty else Counter()
    return {
        "rows": len(df),
        "pending_short_cofold_pairs": int(len(pending)),
        "runnable_short_cofold_pairs": int(len(runnable)),
        "blocked_missing_msa_pairs": int(len(blocked_missing_msa)),
        "result_rows": int(sum(csv_rows(path) for path in cofold_result_paths())),
        "manifest_rows": int(sum(csv_rows(path) for path in cofold_manifest_paths())),
        "target_counts": dict(target_counts),
        "blocked_target_counts": dict(blocked_target_counts),
        "result_files": [str(path.relative_to(ROOT)) for path in cofold_result_paths()],
        "manifest_files": [str(path.relative_to(ROOT)) for path in cofold_manifest_paths()],
    }


def target_cache_stats() -> dict[str, object]:
    targets: dict[str, str] = {}
    for path in sorted((ROOT / "conf/skin_targets").glob("*.yaml")):
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        except Exception:
            continue
        for row in data.get("targets", []) or []:
            key = str(row.get("key", "")).strip().lower()
            uniprot = str(row.get("uniprot", "")).strip()
            if key:
                targets[key] = uniprot

    missing_a3m: list[str] = []
    missing_sequence: list[str] = []
    available_a3m: list[str] = []
    for key, uniprot in sorted(targets.items()):
        a3m = MSA_DIR / f"{key}.a3m"
        fasta = MSA_DIR / f"{uniprot}.fasta" if uniprot else MSA_DIR / "__missing__.fasta"
        if a3m.exists() and a3m.stat().st_size > 0:
            available_a3m.append(key)
        else:
            missing_a3m.append(key)
        if not fasta.exists() or fasta.stat().st_size == 0:
            missing_sequence.append(key)
    return {
        "target_count": len(targets),
        "available_a3m_count": len(available_a3m),
        "missing_a3m_count": len(missing_a3m),
        "missing_a3m": missing_a3m,
        "missing_sequence_count": len(missing_sequence),
        "missing_sequence": missing_sequence,
    }


def row(
    priority: str,
    layer: str,
    current_status: str,
    evidence: str,
    readiness_gate: str,
    compute_policy: str,
    next_queue_action: str,
) -> dict[str, str]:
    return {
        "priority": priority,
        "layer": layer,
        "current_status": current_status,
        "evidence": evidence,
        "readiness_gate": readiness_gate,
        "compute_policy": compute_policy,
        "next_queue_action": next_queue_action,
    }


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    now = datetime.now(ZoneInfo("Asia/Seoul")).isoformat(timespec="seconds")

    active = active_learning_stats()
    target_cache = target_cache_stats()
    synthesis_rows = csv_rows(OUT / "synthesis_retrosynthesis_gate.csv")
    route_rows = csv_rows(OUT / "route_enumeration_gate.csv")
    chromanol_rows = csv_rows(OUT / "chromanol_generative_optimizer.csv")
    pocket_rows = csv_rows(OUT / "pocket_evidence_gate.csv")
    ultra_rows = csv_rows(OUT / "ultra_large_screening_roadmap.csv")
    benchmark_rows = csv_rows(OUT / "structure_benchmark_decoy_gate.csv")
    phenomics_rows = csv_rows(OUT / "phenomics_signature_gate.csv")
    modality_doc = ROOT / "docs/MODALITY_IP_NOVELTY_GATE.md"
    world_doc = ROOT / "docs/WORLD_CLASS_GAP_CLOSURE.md"

    rows = [
        row(
            "P0",
            "active_learning_gpu_fallback",
            "implemented_running" if active["manifest_rows"] else "implemented_waiting_for_gpu",
            f"active-learning rows={active['rows']}; pending short-cofold pairs={active['pending_short_cofold_pairs']}; runnable={active.get('runnable_short_cofold_pairs', 0)}; blocked missing-MSA pairs={active.get('blocked_missing_msa_pairs', 0)}; manifests={active['manifest_rows']}; completed result rows={active['result_rows']}",
            "short_triage_allowed_only",
            "GPU-free windows may run short Boltz-2 cofold; long MD/FE still require master-gate promotion",
            "continue non-duplicate active-learning cofold batches; send hits back to master gate before MD",
        ),
        row(
            "P0",
            "target_msa_coverage",
            "gap_detected" if target_cache["missing_a3m_count"] else "implemented",
            f"skin target configs={target_cache['target_count']}; available target A3M={target_cache['available_a3m_count']}; missing target A3M={target_cache['missing_a3m_count']}",
            "block_target_specific_cofold_for_missing_msa" if target_cache["missing_a3m_count"] else "cofold_cache_ready",
            "targets without target-key A3M are not eligible for automatic cofold queueing",
            "prepare missing target-key MSA/sequence cache before queueing MC1R/RARG/TLR2/NLRP3-style targets",
        ),
        row(
            "P0",
            "synthesis_native_generation",
            "partial_post_filter_only" if synthesis_rows else "missing",
            f"synthesis gate rows={synthesis_rows}; route enumeration rows={route_rows}; AiZynthFinder installed={bool(shutil.which('aizynthcli'))}; ASKCOS cli installed={bool(shutil.which('askcos'))}",
            "generation_requires_route_or_building_block_guard",
            "generate-first/filter-later is not enough for expensive follow-up",
            "add reaction-template/building-block enumeration lane before expanding non-chromanol designs",
        ),
        row(
            "P0",
            "scaffold_hopping_shape_pharmacophore",
            "partial_chromanol_constrained_only" if chromanol_rows else "missing",
            f"chromanol generator rows={chromanol_rows}; no separate shape/pharmacophore scaffold-hop queue detected",
            "new_scaffold_requires_novelty_synthesis_uncertainty_gate",
            "cheap CPU descriptors/enumeration allowed; heavy GPU requires prior-art and synthesis guard",
            "create scaffold-hop queue around stable R16/R17 pharmacophores instead of only substituent scans",
        ),
        row(
            "P1",
            "cryptic_pocket_dynamic_ensemble",
            "static_pocket_gate_only" if pocket_rows else "missing",
            f"pocket evidence rows={pocket_rows}; no dynamic cryptic-pocket ensemble output detected",
            "ensemble_pocket_required_before_pocket_specific_generation",
            "do not claim cryptic/allosteric binding from static cofold alone",
            "add ensemble pocket scout shortlist; only then launch pocket-specific generation",
        ),
        row(
            "P1",
            "ultra_large_tangible_space",
            "roadmap_only" if ultra_rows else "missing",
            f"ultra-large roadmap rows={ultra_rows}; no licensed library download/stage1 embedding output detected",
            "license_storage_stage1_required",
            "do not brute-force large libraries; use active-learning compression",
            "prepare ZINC/REAL/Enamine subset license/storage checklist, then CPU embedding pre-screen",
        ),
        row(
            "P1",
            "reward_hacking_novelty_benchmark",
            "partial_decoy_gate_only" if benchmark_rows else "missing",
            f"structure benchmark rows={benchmark_rows}; no MolScore/Tartarus-style generative benchmark matrix detected",
            "new_generator_requires_benchmark_and_decoys",
            "affinity-only optimization cannot promote a molecule to lead status",
            "add diversity/novelty/synthesis/decoy benchmark table for every new generator lane",
        ),
        row(
            "P1",
            "phenomics_first_generation",
            "partial_gate_only" if phenomics_rows else "missing",
            f"phenomics rows={phenomics_rows}; generator score still not phenomics-objective-native",
            "phenotype_objective_required_for_moa_claim",
            "Cell Painting/JUMP-style evidence should guide generation when direct pocket evidence is weak",
            "feed disease-cell phenotype priority into next acquisition/generation score",
        ),
        row(
            "P2",
            "new_modality_lanes",
            "planned_gate_only" if modality_doc.exists() else "missing",
            f"modality novelty doc exists={modality_doc.exists()}; covalent/allosteric/glue/macrocycle generator lane not detected",
            "high_risk_modality_requires_separate_safety_ip_gate",
            "do not mix high-risk modality claims into ordinary topical small-molecule queue",
            "keep covalent/allosteric/degrader/glue/macrocycle as separate benchmark or future-work lanes",
        ),
        row(
            "P2",
            "agentic_hypothesis_evolution",
            "partial_deterministic_curator",
            f"world-class master gate exists={world_doc.exists()}; creative matrix now generated",
            "curator_must_read_creative_matrix_each_tick",
            "LLM-style hypothesis generation must remain auditable and gate-bound",
            "use this matrix in curator loop context before choosing the next queue",
        ),
    ]

    with CSV_OUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    policy = {
        "timestamp": now,
        "matrix_csv": str(CSV_OUT.relative_to(ROOT)),
        "matrix_doc": str(DOC.relative_to(ROOT)),
        "active_learning_short_cofold": active,
        "target_cache": target_cache,
        "global_queue_additions": {
            "creative_generation_requires_synthesis_or_prior_art_guard": True,
            "active_learning_short_cofold_fallback_enabled": True,
            "cryptic_pocket_generation_requires_ensemble_pocket_gate": True,
            "phenomics_generation_requires_signature_or_assay_gate": True,
            "target_msa_coverage_gap_blocks_target_queue": bool(target_cache["missing_a3m_count"]),
            "new_scaffold_gpu_followup_requires_uncertainty_and_benchmark_gate": True,
        },
    }
    POLICY_OUT.write_text(json.dumps(policy, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "# Creative Discovery Gap Matrix",
        "",
        f"- timestamp: `{now}`",
        f"- matrix_csv: `{CSV_OUT.relative_to(ROOT)}`",
        f"- queue_policy_json: `{POLICY_OUT.relative_to(ROOT)}`",
        f"- active-learning pending short-cofold pairs: `{active['pending_short_cofold_pairs']}`",
        f"- active-learning runnable short-cofold pairs: `{active.get('runnable_short_cofold_pairs', 0)}`",
        f"- active-learning blocked missing-MSA pairs: `{active.get('blocked_missing_msa_pairs', 0)}`",
        f"- active-learning in-flight manifest rows: `{active['manifest_rows']}`",
        f"- active-learning completed cofold result rows: `{active['result_rows']}`",
        f"- target-key A3M missing: `{target_cache['missing_a3m_count']}` / `{target_cache['target_count']}`",
        "",
        "## Meaning",
        "",
        "이 파일은 창의적 신물질 발굴 기술이 실제 큐 정책에 연결됐는지 보는 상위 점검표다. 점수가 좋은 후보라도 synthesis, prior-art/FTO, novelty/diversity, phenomics, target cache, ensemble-pocket gate가 없으면 long-MD/FE/lead claim으로 자동 승격하지 않는다.",
        "",
        "## Matrix",
        "",
        "| priority | layer | status | evidence | readiness gate | compute policy | next queue action |",
        "|---|---|---|---|---|---|---|",
    ]
    for item in rows:
        lines.append(
            f"| {item['priority']} | {item['layer']} | {item['current_status']} | {item['evidence']} | {item['readiness_gate']} | {item['compute_policy']} | {item['next_queue_action']} |"
        )

    missing = target_cache["missing_a3m"]
    lines.extend(
        [
            "",
            "## Target Cache Gap",
            "",
            "- target-specific Boltz-2 cofold는 `data/msa/{target}.a3m`가 없으면 자동 큐잉하지 않는다.",
            f"- missing target-key A3M examples: `{', '.join(missing[:20]) if missing else 'none'}`",
            "",
            "## Curator Rules",
            "",
            "- GPU가 비면 active-learning short Boltz-2 cofold는 허용한다. 단 결과는 triage이며, master gate 통과 전 long-MD/FE로 올리지 않는다.",
            "- 새 scaffold 생성은 docking/affinity 단일 목적 최적화가 아니라 novelty, synthesis, prior-art, uncertainty, phenomics guard를 동시에 요구한다.",
            "- chromanol 주변 치환체 탐색과 별도로 shape/pharmacophore scaffold-hop lane을 만들어야 한다.",
            "- cryptic/allosteric pocket 주장은 static cofold가 아니라 ensemble pocket scout 이후에만 쓴다.",
            "- phenomics-first 후보는 직접 target binding보다 disease-cell phenotype rescue objective를 우선한다.",
            "",
        ]
    )
    DOC.write_text("\n".join(lines), encoding="utf-8")
    print(f"Saved {CSV_OUT.relative_to(ROOT)} ({len(rows)} rows)")
    print(f"Saved {POLICY_OUT.relative_to(ROOT)}")
    print(f"Saved {DOC.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
