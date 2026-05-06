"""Build a target evidence gate for the skin discovery program.

This script is intentionally CPU-light and deterministic. It combines local
target YAML rationale with current Open Targets disease associations when the
API is reachable, then writes a gate table used by the curator and manuscripts.
"""
from __future__ import annotations

import csv
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import requests
import yaml


ROOT = Path(__file__).resolve().parents[1]
CONF_DIR = ROOT / "conf/skin_targets"
OUT = ROOT / "pilot/cpu_meaningful"
DOC = ROOT / "docs/TARGET_EVIDENCE_GATE.md"
CSV_OUT = OUT / "target_evidence_gate.csv"
JSON_OUT = OUT / "target_evidence_gate_summary.json"

OT_URL = "https://api.platform.opentargets.org/api/v4/graphql"

TARGET_ENSG = {
    "AR": "ENSG00000169083",
    "COL1A1": "ENSG00000108821",
    "CTGF": "ENSG00000118523",
    "CTNNB1": "ENSG00000168036",
    "DCT": "ENSG00000080166",
    "F2RL1": "ENSG00000164251",
    "FGF2": "ENSG00000138685",
    "JUN": "ENSG00000177606",
    "LOX": "ENSG00000113083",
    "MC1R": "ENSG00000258839",
    "MITF": "ENSG00000187098",
    "MMP1": "ENSG00000196611",
    "MMP3": "ENSG00000149968",
    "MMP9": "ENSG00000100985",
    "MYLK": "ENSG00000065534",
    "NLRP3": "ENSG00000162711",
    "NR3C1": "ENSG00000113580",
    "PIEZO1": "ENSG00000103335",
    "PTGDR2": "ENSG00000183134",
    "PTGS2": "ENSG00000073756",
    "RARG": "ENSG00000172819",
    "SIRT1": "ENSG00000096717",
    "SRD5A1": "ENSG00000145545",
    "SRD5A2": "ENSG00000277893",
    "SREBF1": "ENSG00000072310",
    "TGFB1": "ENSG00000105329",
    "TLR2": "ENSG00000137462",
    "TYR": "ENSG00000077498",
    "TYRP1": "ENSG00000107165",
    "VEGFA": "ENSG00000112715",
    "WNT10B": "ENSG00000169884",
}

DISEASE_TERMS = {
    "scar_regeneration": ["scar", "keloid", "wound", "scleroderma", "cutaneous fibrosis", "skin fibrosis"],
    "pigmentation_melasma": ["pigment", "melan", "albin", "melasma"],
    "androgenetic_alopecia": ["alopec", "hair", "pilosebaceous"],
    "acne_vulgaris": ["acne", "seborr", "hidradenitis"],
    "photoaging": ["photoaging", "skin aging", "wrinkle", "collagen", "dermat"],
}

SKIN_TERMS = sorted({term for terms in DISEASE_TERMS.values() for term in terms} | {"skin"})
TRANSLATIONAL_TERMS = {
    "scar_regeneration": ["fibrosis"],
}


def read_targets() -> list[dict[str, object]]:
    by_key: dict[str, dict[str, object]] = {}
    for path in sorted(CONF_DIR.glob("*.yaml")):
        data = yaml.safe_load(path.read_text()) or {}
        category = str(data.get("category", path.stem))
        tier = int(data.get("priority_tier", 9))
        for target in data.get("targets", []) or []:
            key = str(target.get("key", "")).upper()
            if not key:
                continue
            row = by_key.setdefault(
                key,
                {
                    "target": key,
                    "uniprot": target.get("uniprot", ""),
                    "display": target.get("display", key),
                    "modes": set(),
                    "diseases": set(),
                    "priority_tiers": [],
                    "novel_target": False,
                    "known_inhibitor_count": 0,
                    "rationales": [],
                },
            )
            row["modes"].add(str(target.get("mode", "")))
            row["diseases"].add(category)
            row["priority_tiers"].append(tier)
            row["novel_target"] = bool(row["novel_target"] or target.get("novel_target", False))
            row["known_inhibitor_count"] = int(row["known_inhibitor_count"]) + len(
                target.get("known_inhibitors", []) or target.get("known_activators", []) or []
            )
            rationale = target.get("rationale", "")
            if rationale:
                row["rationales"].append(" ".join(str(rationale).split())[:180])
    rows = []
    for row in by_key.values():
        row["modes"] = sorted(row["modes"])
        row["diseases"] = sorted(row["diseases"])
        row["priority_tier_min"] = min(row["priority_tiers"]) if row["priority_tiers"] else 9
        row["disease_terms"] = sorted(
            {
                term
                for disease in row["diseases"]
                for term in DISEASE_TERMS.get(str(disease), [])
            }
        )
        rows.append(row)
    return sorted(rows, key=lambda r: (r["priority_tier_min"], str(r["target"])))


def query_open_targets(ensg: str) -> dict[str, object]:
    query = """
    query target($ensgId: String!) {
      target(ensemblId: $ensgId) {
        id
        approvedSymbol
        biotype
        associatedDiseases {
          count
          rows {
            disease { id name }
            score
          }
        }
      }
    }
    """
    response = requests.post(
        OT_URL,
        json={"query": query, "variables": {"ensgId": ensg}},
        timeout=25,
    )
    response.raise_for_status()
    data = response.json().get("data", {}).get("target")
    if not data:
        return {"error": "no Open Targets target"}
    return data


def fetch_ot_cache(targets: list[dict[str, object]]) -> dict[str, dict[str, object]]:
    cache: dict[str, dict[str, object]] = {}
    for row in targets:
        key = str(row["target"])
        ensg = TARGET_ENSG.get(key, "")
        if not ensg:
            cache[key] = {"error": "missing ENSG mapping"}
            continue
        try:
            cache[key] = query_open_targets(ensg)
        except Exception as exc:
            cache[key] = {"error": str(exc)[:160]}
    return cache


def classify_modality(modes: list[str], display: str) -> tuple[str, str]:
    mode_text = " ".join(modes).lower()
    display_text = display.lower()
    if any(token in mode_text for token in ["inhibitor", "antagonist"]):
        modality = "small_molecule_or_topical_inhibitor"
        feasibility = "direct"
    elif any(token in mode_text for token in ["agonist", "activator", "stabilizer"]):
        modality = "agonist_or_pathway_modulator"
        feasibility = "context_dependent"
    elif any(token in mode_text for token in ["preserve", "support", "suppressor"]):
        modality = "phenotype_or_expression_modulator"
        feasibility = "indirect"
    else:
        modality = "target_or_phenotype_followup"
        feasibility = "unknown"
    if any(token in display_text for token in ["mitf", "jun", "catenin", "col1a1"]):
        feasibility = "hard_or_indirect"
    if any(token in display_text for token in ["fgf", "vegf", "tgf", "ctgf"]):
        modality = f"{modality}+biologic_possible"
    return modality, feasibility


def score_gate(row: dict[str, object], ot: dict[str, object]) -> dict[str, object]:
    disease_terms = [str(term).lower() for term in row.get("disease_terms", [])] or SKIN_TERMS
    translational_terms = sorted(
        {
            term
            for disease in row.get("diseases", [])
            for term in TRANSLATIONAL_TERMS.get(str(disease), [])
        }
    )
    all_skin_terms = sorted(set(disease_terms + SKIN_TERMS))
    associated = (ot.get("associatedDiseases", {}) or {}) if "error" not in ot else {}
    diseases = associated.get("rows", []) or []
    top_overall = []
    skin_hits = []
    disease_hits = []
    translational_hits = []
    for item in diseases:
        disease = item.get("disease", {}) or {}
        name = str(disease.get("name", ""))
        lname = name.lower()
        score = float(item.get("score") or 0.0)
        if len(top_overall) < 5:
            top_overall.append(f"{name}:{score:.3f}")
        if any(term in lname for term in all_skin_terms):
            skin_hits.append((name, score))
        if any(term in lname for term in disease_terms):
            disease_hits.append((name, score))
        for term in translational_terms:
            if term in lname:
                if term == "fibrosis" and "cystic fibrosis" in lname:
                    continue
                translational_hits.append((name, score))
                break
    max_skin = max([score for _, score in skin_hits], default=0.0)
    max_disease = max([score for _, score in disease_hits], default=0.0)
    max_translational = max([score for _, score in translational_hits], default=0.0)
    modality, feasibility = classify_modality(list(row["modes"]), str(row["display"]))
    has_local_strength = int(row["priority_tier_min"]) <= 2 or bool(row["novel_target"])
    has_known_ligands = int(row["known_inhibitor_count"]) > 0
    direct = feasibility == "direct"

    if max_disease >= 0.30 and direct:
        gate = "green"
        next_action = "cofold/MD or wet-lab endpoint can be prioritized"
    elif max_skin >= 0.20 and feasibility in {"direct", "context_dependent"}:
        gate = "green"
        next_action = "skin-evidence supported; prioritize assay endpoint definition"
    elif max_translational >= 0.30 and direct and int(row["priority_tier_min"]) <= 1:
        gate = "green"
        next_action = "broad anti-fibrotic evidence supports scar-program follow-up; avoid skin-specific overclaim"
    elif max_skin >= 0.10 or has_local_strength or has_known_ligands:
        gate = "yellow"
        next_action = "keep, but require phenotype/cell evidence before strong claims"
    else:
        gate = "red"
        next_action = "do not expand compute until stronger disease/cell evidence exists"

    if feasibility in {"hard_or_indirect", "indirect"} and gate == "green":
        gate = "yellow"
        next_action = "shift to phenotype assay or biologic/modality plan before docking claims"

    return {
        "target": row["target"],
        "display": row["display"],
        "uniprot": row["uniprot"],
        "ensg": TARGET_ENSG.get(str(row["target"]), ""),
        "diseases": ";".join(row["diseases"]),
        "priority_tier_min": row["priority_tier_min"],
        "modes": ";".join(row["modes"]),
        "novel_target": row["novel_target"],
        "known_inhibitor_count": row["known_inhibitor_count"],
        "ot_status": "error" if "error" in ot else "ok",
        "ot_error": ot.get("error", ""),
        "ot_total_disease_count": associated.get("count", 0) if associated else 0,
        "ot_skin_hit_count": len(skin_hits),
        "ot_max_skin_score": round(max_skin, 3),
        "ot_max_local_disease_score": round(max_disease, 3),
        "ot_translational_hit_count": len(translational_hits),
        "ot_max_translational_score": round(max_translational, 3),
        "ot_top_skin_hits": "; ".join(f"{name}:{score:.3f}" for name, score in skin_hits[:5]),
        "ot_top_translational_hits": "; ".join(f"{name}:{score:.3f}" for name, score in translational_hits[:5]),
        "ot_top_overall": "; ".join(top_overall),
        "recommended_modality": modality,
        "tractability_class": feasibility,
        "gate": gate,
        "next_action": next_action,
    }


def write_outputs(rows: list[dict[str, object]]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys()) if rows else []
    with CSV_OUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    counts = dict(sorted(defaultdict(int, {g: sum(1 for r in rows if r["gate"] == g) for g in ["green", "yellow", "red"]}).items()))
    summary = {
        "timestamp": datetime.now(ZoneInfo("Asia/Seoul")).isoformat(timespec="seconds"),
        "target_count": len(rows),
        "gate_counts": counts,
        "csv": str(CSV_OUT.relative_to(ROOT)),
        "doc": str(DOC.relative_to(ROOT)),
    }
    JSON_OUT.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    green = [r for r in rows if r["gate"] == "green"]
    yellow = [r for r in rows if r["gate"] == "yellow"]
    red = [r for r in rows if r["gate"] == "red"]
    lines = [
        "# Target Evidence Gate",
        "",
        f"- timestamp: `{summary['timestamp']}`",
        f"- targets: `{len(rows)}`",
        f"- gate_counts: `{counts}`",
        "- purpose: 계산 큐를 질병/피부 근거, tractability, modality에 연결해 무의미한 docking 확장을 줄인다.",
        "",
        "## Gate Meaning",
        "",
        "- `green`: disease/skin evidence와 small-molecule 또는 topical modality가 비교적 직접적이다.",
        "- `yellow`: 계산은 가능하지만 phenotype, cell atlas, wet-lab endpoint 또는 modality caveat가 필요하다.",
        "- `red`: 현재 근거만으로는 추가 GPU/CPU 확장 우선순위가 낮다.",
        "",
        "## Green Targets",
        "",
        "| target | diseases | OT max skin | modality | next action |",
        "|---|---|---:|---|---|",
    ]
    for r in green:
        score_text = f"skin {r['ot_max_skin_score']} / translational {r['ot_max_translational_score']}"
        lines.append(
            f"| {r['target']} | {r['diseases']} | {score_text} | {r['recommended_modality']} | {r['next_action']} |"
        )
    lines.extend(["", "## Yellow Targets", "", "| target | diseases | reason | next action |", "|---|---|---|---|"])
    for r in yellow:
        reason = f"OT skin={r['ot_max_skin_score']}; tractability={r['tractability_class']}"
        lines.append(f"| {r['target']} | {r['diseases']} | {reason} | {r['next_action']} |")
    lines.extend(["", "## Red Targets", "", "| target | diseases | reason |", "|---|---|---|"])
    for r in red:
        reason = f"OT skin={r['ot_max_skin_score']}; error={r['ot_error']}"
        lines.append(f"| {r['target']} | {r['diseases']} | {reason} |")
    lines.extend(
        [
            "",
            "## Curator Use",
            "",
            "- GPU cofold/MD 신규 큐는 `green`을 우선한다.",
            "- `yellow`는 phenotype assay, cell-type evidence, 또는 modality 전환 계획이 같이 있어야 논문 claim에 올린다.",
            "- `red`는 atlas/method paper의 negative-control 또는 future-work로만 사용한다.",
            "",
        ]
    )
    DOC.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    targets = read_targets()
    ot = fetch_ot_cache(targets)
    rows = [score_gate(row, ot.get(str(row["target"]), {})) for row in targets]
    write_outputs(rows)
    print(f"Saved {CSV_OUT.relative_to(ROOT)}")
    print(f"Saved {DOC.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
