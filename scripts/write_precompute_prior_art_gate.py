"""Build a pre-compute prior-art gate for candidate queue decisions.

This is not a legal FTO opinion. It creates technical triage rows that say
which candidates can receive cheap compute and which should pause before
expensive MD/RBFE/ABFE/synthesis spend until patent-professional review.
"""
from __future__ import annotations

import argparse
import csv
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Iterable
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

import pandas as pd
from rdkit import Chem, RDLogger
from rdkit.Chem import inchi
from rdkit.Chem.Scaffolds import MurckoScaffold


RDLogger.DisableLog("rdApp.*")

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_meaningful"
DOC = ROOT / "docs/PRECOMPUTE_PRIOR_ART_GATE.md"
CSV_OUT = OUT / "precompute_prior_art_gate.csv"
CACHE = OUT / "precompute_prior_art_pubchem_cache.json"

KNOWN_PUBCHEM_OVERRIDES = {
    # Public PUG-REST exact hit for the R15 chromanol parent:
    # OCC1COc2cc(O)ccc2C1 -> CID 105438602,
    # InChIKey UGTWTNDJVXXXQG-UHFFFAOYSA-N.
    "OCC1COc2cc(O)ccc2C1": {
        "pubchem_exact_status": "hit",
        "pubchem_exact_cids": "105438602",
        "pubchem_same_connectivity_status": "hit",
        "pubchem_same_connectivity_cids": "105438602",
    },
}

PUBLIC_PRIOR_ART_SOURCES = [
    "PubChem PUG-REST exact/same-connectivity",
    "SureChEMBL compound-patent associations",
    "WIPO PATENTSCOPE exact/substructure/Markush",
    "Google Patents text/family search",
    "Lens patent/scholarly API",
    "EPO OPS family/legal-status API",
    "USPTO Patent Public Search/PatentsView",
    "OpenAlex/Crossref/PubMed scholarly search",
]

PROFESSIONAL_REVIEW_SOURCES = [
    "CAS REGISTRY/MARPAT/STNext or CAS IP Finder",
    "Derwent Innovation/DWPI + chemistry resource",
    "Reaxys/SciFinder-n literature and synthesis search",
    "patent attorney claim chart and legal-status opinion",
]


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()


def first_col(row: pd.Series, names: Iterable[str], default: str = "") -> str:
    for name in names:
        if name in row and pd.notna(row[name]):
            value = str(row[name]).strip()
            if value:
                return value
    return default


def canonical(smiles: str) -> str:
    mol = Chem.MolFromSmiles(str(smiles))
    return Chem.MolToSmiles(mol, canonical=True) if mol else str(smiles)


def scaffold(smiles: str) -> str:
    mol = Chem.MolFromSmiles(str(smiles))
    if mol is None:
        return ""
    scaf = MurckoScaffold.GetScaffoldForMol(mol)
    if scaf is None or scaf.GetNumAtoms() == 0:
        return "acyclic"
    return Chem.MolToSmiles(scaf, canonical=True)


def inchi_key(smiles: str) -> str:
    mol = Chem.MolFromSmiles(str(smiles))
    if mol is None:
        return ""
    try:
        return inchi.MolToInchiKey(mol)
    except Exception:
        return ""


def collect_candidates() -> pd.DataFrame:
    frames: list[pd.DataFrame] = []

    for path in [
        OUT / "ip_fto_watchlist.csv",
        OUT / "candidate_local_novelty_gate.csv",
        OUT / "r15_chromanol_cofold_14targets.csv",
        OUT / "r16_chromanol_topical_cofold.csv",
        OUT / "chromanol_generative_optimizer.csv",
    ]:
        df = read_csv(path)
        if df.empty or "smiles" not in df.columns:
            continue
        rows = []
        for _, row in df.iterrows():
            rows.append(
                {
                    "candidate_id": first_col(row, ["candidate_id", "analog_id", "compound", "design_id", "job_id"]),
                    "target": first_col(row, ["target"]),
                    "smiles": first_col(row, ["smiles"]),
                    "source": path.name,
                    "novelty_gate": first_col(row, ["novelty_gate"], "not_scored"),
                    "best_local_tanimoto": first_col(row, ["best_local_tanimoto"], "0"),
                    "ip_fto_risk": first_col(row, ["ip_fto_risk"], ""),
                    "score": first_col(row, ["affinity_probability_binary", "score", "local_design_priority"], ""),
                }
            )
        frames.append(pd.DataFrame(rows))

    for path in sorted(OUT.glob("r17_chromanol_generative_batch*_cofold.csv")):
        df = read_csv(path)
        if df.empty or "smiles" not in df.columns:
            continue
        rows = []
        for _, row in df.iterrows():
            rows.append(
                {
                    "candidate_id": first_col(row, ["job_id", "design_id", "candidate_id"]),
                    "target": first_col(row, ["target"]),
                    "smiles": first_col(row, ["smiles"]),
                    "source": path.name,
                    "novelty_gate": "not_scored",
                    "best_local_tanimoto": "0",
                    "ip_fto_risk": "",
                    "score": first_col(row, ["affinity_probability_binary", "local_design_priority"], ""),
                }
            )
        frames.append(pd.DataFrame(rows))

    if not frames:
        return pd.DataFrame()
    out = pd.concat(frames, ignore_index=True)
    out = out[out["smiles"].fillna("").astype(str).str.len() > 0].copy()
    out["canonical_smiles"] = out["smiles"].map(canonical)
    out["target"] = out["target"].fillna("").astype(str).str.lower()
    out["candidate_id"] = out["candidate_id"].fillna("").astype(str)
    out = out.drop_duplicates(subset=["candidate_id", "target", "canonical_smiles"])
    return out


def load_cache() -> dict[str, dict[str, object]]:
    if not CACHE.exists():
        return {}
    try:
        return json.loads(CACHE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_cache(cache: dict[str, dict[str, object]]) -> None:
    CACHE.write_text(json.dumps(cache, indent=2, sort_keys=True), encoding="utf-8")


def pubchem_query(url: str) -> tuple[str, list[int]]:
    req = Request(url, headers={"User-Agent": "GenesisMedicinePriorArtGate/1.0"})
    try:
        with urlopen(req, timeout=15) as handle:
            data = json.load(handle)
        cids = data.get("IdentifierList", {}).get("CID", [])
        cids = [int(cid) for cid in cids if int(cid) != 0]
        return "hit" if cids else "no_hit", cids
    except HTTPError as exc:
        if exc.code == 404:
            return "no_hit", []
        return f"http_error_{exc.code}", []
    except (URLError, TimeoutError, json.JSONDecodeError) as exc:
        return f"error_{type(exc).__name__}", []


def pubchem_status(smiles: str, network: bool, cache: dict[str, dict[str, object]]) -> dict[str, object]:
    key = canonical(smiles)
    override = KNOWN_PUBCHEM_OVERRIDES.get(key)
    if override:
        cache[key] = override
        save_cache(cache)
        return override
    if key in cache:
        return cache[key]
    if not network:
        return {
            "pubchem_exact_status": "not_checked",
            "pubchem_exact_cids": "",
            "pubchem_same_connectivity_status": "not_checked",
            "pubchem_same_connectivity_cids": "",
        }

    exact_url = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/smiles/" + quote(key, safe="") + "/cids/JSON"
    exact_status, exact_cids = pubchem_query(exact_url)
    time.sleep(0.2)
    same_url = (
        "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/fastidentity/smiles/cids/JSON?"
        + urlencode({"identity_type": "same_connectivity", "smiles": key})
    )
    same_status, same_cids = pubchem_query(same_url)
    result = {
        "pubchem_exact_status": exact_status,
        "pubchem_exact_cids": ";".join(map(str, exact_cids[:10])),
        "pubchem_same_connectivity_status": same_status,
        "pubchem_same_connectivity_cids": ";".join(map(str, same_cids[:10])),
    }
    cache[key] = result
    save_cache(cache)
    time.sleep(0.2)
    return result


def target_keywords(target: str) -> list[str]:
    if target in {"tyr", "dct", "tyrp1", "mitf"}:
        return ["melanin", "tyrosinase", "hyperpigmentation", "skin whitening"]
    if target in {"tgfb1", "ctgf", "mmp1", "lox"}:
        return ["scar", "fibrosis", "collagen", "TGF beta", "photoaging"]
    if target in {"srd5a1", "srd5a2", "ar"}:
        return ["androgen", "alopecia", "5 alpha reductase", "acne"]
    if target in {"ptgs2"}:
        return ["inflammation", "COX-2", "photoaging", "acne"]
    return ["topical dermatology"]


def infer_risk(row: pd.Series, scaf: str) -> str:
    current = str(row.get("ip_fto_risk", "") or "")
    if current:
        return current
    smi = str(row["canonical_smiles"])
    mol = Chem.MolFromSmiles(smi)
    text = f"{row.get('candidate_id', '')} {smi} {scaf}".lower()
    if "known_or_close_analog" in str(row.get("novelty_gate", "")):
        return "high_review"
    if "chromanol" in text or "c1ccc2c(c1)CCCO2".lower() in scaf.lower():
        return "medium_review"
    if mol is not None and any(atom.GetSymbol() in {"Cl", "Br", "I"} for atom in mol.GetAtoms()):
        return "medium_review"
    return "baseline_watch"


def decision(row: pd.Series, pubchem: dict[str, object], risk: str) -> tuple[str, str]:
    try:
        tanimoto = float(row.get("best_local_tanimoto", 0) or 0)
    except Exception:
        tanimoto = 0.0
    novelty = str(row.get("novelty_gate", ""))
    exact_hit = pubchem.get("pubchem_exact_status") == "hit" or pubchem.get("pubchem_same_connectivity_status") == "hit"

    if novelty == "known_or_close_analog" or tanimoto >= 0.85:
        return (
            "deprioritize_or_benchmark_only",
            "known/close local analog; use as benchmark unless a clear new use/formulation claim is attorney-cleared",
        )
    if exact_hit:
        return (
            "hold_expensive_compute_until_prior_art_review",
            "public exact/same-connectivity hit; continue only cheap benchmarking until patent/literature context is reviewed",
        )
    if risk in {"high_review", "medium_review"}:
        return (
            "hold_expensive_compute_until_markush_review",
            "generic scaffold/halogen/use-claim risk; allow cheap triage, hold 60-200ns/RBFE/ABFE/synthesis until Markush and claim chart review",
        )
    return (
        "cheap_compute_allowed_prior_art_pending",
        "no local high-risk signal; allow low-cost ranking but require prior-art review before commercial or composition claim",
    )


def build_rows(network: bool, limit: int) -> list[dict[str, object]]:
    candidates = collect_candidates()
    if candidates.empty:
        return []
    cache = load_cache()
    rows = []
    candidates = candidates.copy()
    candidates["_risk_seed"] = candidates.apply(lambda row: infer_risk(row, scaffold(str(row["canonical_smiles"]))), axis=1)
    order = {"high_review": 0, "medium_review": 1, "baseline_watch": 2}
    candidates = candidates.sort_values(["_risk_seed", "candidate_id"], key=lambda s: s.map(order).fillna(9) if s.name == "_risk_seed" else s)

    checked = 0
    for _, row in candidates.iterrows():
        smi = str(row["canonical_smiles"])
        scaf = scaffold(smi)
        ikey = inchi_key(smi)
        risk = infer_risk(row, scaf)
        do_network = network and checked < limit
        pubchem = pubchem_status(smi, do_network, cache)
        if do_network:
            checked += 1
        gate, reason = decision(row, pubchem, risk)
        target = str(row.get("target", ""))
        keywords = target_keywords(target)
        generic_terms = [scaf, "chromanol" if "CCCO" in scaf or "chromanol" in str(row.get("candidate_id", "")).lower() else "", *keywords]
        generic_terms = [term for term in dict.fromkeys(generic_terms) if term]
        rows.append(
            {
                "candidate_id": row.get("candidate_id", ""),
                "target": target,
                "source": row.get("source", ""),
                "canonical_smiles": smi,
                "inchi_key": ikey,
                "murcko_scaffold": scaf,
                "novelty_gate": row.get("novelty_gate", "not_scored"),
                "best_local_tanimoto": row.get("best_local_tanimoto", 0),
                "ip_fto_risk": risk,
                **pubchem,
                "precompute_gate": gate,
                "gate_reason": reason,
                "cheap_compute": "allow" if gate != "deprioritize_or_benchmark_only" else "benchmark_only",
                "expensive_compute": "hold_for_review" if "hold" in gate or "deprioritize" in gate else "allow_with_caveat",
                "professional_review_required": "yes" if risk in {"high_review", "medium_review"} or "hold" in gate else "before_claims",
                "public_exact_query": f"{ikey} OR {smi}",
                "patent_text_query": " OR ".join(dict.fromkeys([str(row.get("candidate_id", "")), ikey, scaf, *keywords])),
                "markush_query_scope": "substructure/as-drawn Markush search on scaffold + substituent positions; claims/description/images sections",
                "academic_value_check": "OpenAlex/Crossref/PubMed query: " + " OR ".join(dict.fromkeys([scaf, *keywords])),
                "commercial_value_check": "assignee density, active family count, expiry/legal status, use/formulation claim overlap, available differentiation",
            }
        )
    return rows


def write_outputs(rows: list[dict[str, object]], network: bool, limit: int) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    if rows:
        with CSV_OUT.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
    else:
        CSV_OUT.write_text("", encoding="utf-8")

    now = datetime.now(ZoneInfo("Asia/Seoul")).isoformat(timespec="seconds")
    counts = {}
    for row in rows:
        counts[row["precompute_gate"]] = counts.get(row["precompute_gate"], 0) + 1
    top_hold = [row for row in rows if row["expensive_compute"] == "hold_for_review"][:25]
    lines = [
        "# Pre-Compute Prior-Art Gate",
        "",
        f"- timestamp: `{now}`",
        f"- rows: `{len(rows)}`",
        f"- pubchem_network_checked: `{network}`",
        f"- pubchem_network_limit: `{limit}`",
        f"- gate_counts: `{counts}`",
        "- purpose: expensive GPU/CPU/wet-lab spend before public-prior-art, Markush, legal-status, and academic/commercial value review is avoided.",
        "- legal caveat: this is technical triage, not attorney FTO opinion.",
        "",
        "## Source Stack",
        "",
        "| layer | role |",
        "|---|---|",
    ]
    for source in PUBLIC_PRIOR_ART_SOURCES:
        lines.append(f"| public/free | {source} |")
    for source in PROFESSIONAL_REVIEW_SOURCES:
        lines.append(f"| professional/manual | {source} |")
    lines.extend(
        [
            "",
            "## Decision Rule",
            "",
            "- `deprioritize_or_benchmark_only`: known/close analog. Do not spend lead-optimization compute unless it is a benchmark or a clear new-use hypothesis.",
            "- `hold_expensive_compute_until_prior_art_review`: exact/same-connectivity public hit. Cheap ranking may continue, but MD 60-200 ns, RBFE/ABFE, synthesis, and commercial claims wait.",
            "- `hold_expensive_compute_until_markush_review`: scaffold/use/halogen Markush risk. Cheap ranking may continue; professional Markush and claim chart are required before heavy follow-up.",
            "- `cheap_compute_allowed_prior_art_pending`: no current block, but composition/use/formulation claims still require manual/professional review.",
            "",
            "## Current Hold Queue",
            "",
            "| candidate | target | risk | PubChem | gate | reason |",
            "|---|---|---|---|---|---|",
        ]
    )
    for row in top_hold:
        pubchem = f"{row['pubchem_exact_status']}/{row['pubchem_same_connectivity_status']}"
        lines.append(
            f"| {row['candidate_id']} | {row['target']} | {row['ip_fto_risk']} | {pubchem} | {row['precompute_gate']} | {row['gate_reason']} |"
        )
    lines.extend(
        [
            "",
            "## Attorney/Professional DB Package",
            "",
            "For each serious lead, export: canonical SMILES, InChIKey, Murcko scaffold, substituent map, targets/use cases, intended countries, intended launch window, public exact hits, top patent families, claim chart placeholders, and legal-status notes.",
            "",
            "Required searches before expensive compute or commercial claim:",
            "",
            "1. Exact identity and same-connectivity: PubChem, SureChEMBL, Google Patents text, Lens.",
            "2. Similarity/substructure: PubChem fastsimilarity/fastsubstructure, ChEMBL, SureChEMBL.",
            "3. Markush: WIPO PATENTSCOPE logged-in chemical search and CAS MARPAT/STNext/CAS IP Finder.",
            "4. Legal status/family: EPO OPS/INPADOC, PATENTSCOPE family, national registers for intended jurisdictions.",
            "5. Academic value: OpenAlex/Crossref/PubMed + positive/negative control landscape.",
            "6. Commercial value: active assignees, granted/pending family count, expiry, claim overlap, formulation/use differentiation.",
            "",
        ]
    )
    DOC.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--network", action="store_true", help="run capped PubChem exact/same-connectivity checks")
    parser.add_argument("--limit", type=int, default=80, help="maximum rows to query against PubChem when --network is set")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    rows = build_rows(network=bool(args.network), limit=max(0, int(args.limit)))
    write_outputs(rows, network=bool(args.network), limit=max(0, int(args.limit)))
    print(f"Saved {CSV_OUT.relative_to(ROOT)}")
    print(f"Saved {DOC.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
