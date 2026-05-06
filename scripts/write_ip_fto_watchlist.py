"""Create a manual IP/FTO watchlist for current candidate scaffolds."""
from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd
from rdkit import Chem, RDLogger
from rdkit.Chem.Scaffolds import MurckoScaffold


RDLogger.DisableLog("rdApp.*")

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_meaningful"
DATA = ROOT / "data"
DOC = ROOT / "docs/IP_FTO_WATCHLIST.md"
CSV_OUT = OUT / "ip_fto_watchlist.csv"
TEMPLATE = DATA / "ip_fto_manual_review_template.csv"

TEMPLATE_COLUMNS = [
    "review_id",
    "date",
    "candidate_id",
    "smiles",
    "jurisdiction",
    "database",
    "query",
    "top_hit_publication",
    "assignee",
    "claim_scope_note",
    "risk_flag",
    "reviewer",
    "notes",
]


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()


def col(df: pd.DataFrame, names: list[str], default: object = "") -> pd.Series:
    for name in names:
        if name in df.columns:
            return df[name]
    return pd.Series([default] * len(df), index=df.index)


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


def collect_candidates() -> pd.DataFrame:
    frames = []
    novelty = read_csv(OUT / "candidate_local_novelty_gate.csv")
    if not novelty.empty and "smiles" in novelty.columns:
        frames.append(
            pd.DataFrame(
                {
                    "candidate_id": col(novelty, ["candidate_id"]),
                    "target": col(novelty, ["target"]),
                    "smiles": col(novelty, ["smiles"]),
                    "source": col(novelty, ["source"], "novelty_gate"),
                    "novelty_gate": col(novelty, ["novelty_gate"], ""),
                    "best_local_tanimoto": pd.to_numeric(col(novelty, ["best_local_tanimoto"], 0), errors="coerce").fillna(0),
                }
            )
        )
    for path, source, id_cols in [
        (OUT / "r16_chromanol_topical_cofold.csv", "r16_chromanol", ["analog_id"]),
        (OUT / "r15_chromanol_cofold_14targets.csv", "r15_chromanol", ["compound"]),
        (OUT / "active_learning_next_candidates.csv", "active_learning", ["candidate_id"]),
    ]:
        df = read_csv(path)
        if df.empty or "smiles" not in df.columns:
            continue
        frames.append(
            pd.DataFrame(
                {
                    "candidate_id": col(df, id_cols),
                    "target": col(df, ["target"]),
                    "smiles": col(df, ["smiles"]),
                    "source": source,
                    "novelty_gate": "",
                    "best_local_tanimoto": 0.0,
                }
            )
        )
    if not frames:
        return pd.DataFrame()
    out = pd.concat(frames, ignore_index=True)
    out["smiles"] = out["smiles"].fillna("").astype(str).map(canonical)
    out["target"] = out["target"].fillna("").astype(str).str.lower()
    out["candidate_id"] = out["candidate_id"].fillna("").astype(str)
    return out[out["smiles"].ne("")].drop_duplicates(subset=["candidate_id", "target", "smiles"])


def classify(row: pd.Series) -> dict[str, object]:
    smi = str(row["smiles"])
    mol = Chem.MolFromSmiles(smi)
    scaf = scaffold(smi)
    novelty = str(row.get("novelty_gate", "") or "")
    candidate = str(row.get("candidate_id", ""))
    target = str(row.get("target", "")).lower()
    text = f"{candidate} {smi} {scaf}".lower()
    keywords = []
    if "chromanol" in text or "c1coc" in text or "c1coc2" in text:
        keywords.extend(["chromanol", "benzopyran", "topical dermatology"])
    if mol is not None and any(atom.GetSymbol() in {"Cl", "Br", "I"} for atom in mol.GetAtoms()):
        keywords.append("halogenated analog Markush")
    if target in {"tyr", "dct", "tyrp1", "mitf"}:
        keywords.extend(["melanin", "tyrosinase", "hyperpigmentation"])
    if target in {"tgfb1", "ctgf", "mmp1", "lox"}:
        keywords.extend(["scar", "fibrosis", "collagen", "TGF beta"])
    if target in {"srd5a1", "srd5a2", "ar"}:
        keywords.extend(["androgen", "alopecia", "5 alpha reductase"])
    if not keywords:
        keywords.append("skin topical small molecule")

    if novelty == "known_or_close_analog":
        risk = "high_review"
    elif novelty == "close_series":
        risk = "medium_review"
    elif "halogenated analog Markush" in keywords:
        risk = "medium_review"
    else:
        risk = "baseline_watch"
    query = " OR ".join(dict.fromkeys([candidate, scaf, *keywords]))
    return {
        "candidate_id": candidate,
        "target": target,
        "source": row.get("source", ""),
        "smiles": smi,
        "murcko_scaffold": scaf,
        "novelty_gate": novelty if novelty else "not_scored",
        "best_local_tanimoto": round(float(row.get("best_local_tanimoto", 0) or 0), 3),
        "ip_fto_risk": risk,
        "manual_search_databases": "Google Patents; WIPO PATENTSCOPE; PubChem patent links; SureChEMBL; Lens",
        "manual_query_terms": query,
        "claim_scope_to_review": "composition of matter; topical dermatology use; formulation/vehicle; target/pathway use; Markush scaffold",
        "next_action": "manual patent landscape/FTO screen before novelty or commercial claim",
    }


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    DATA.mkdir(parents=True, exist_ok=True)
    now = datetime.now(ZoneInfo("Asia/Seoul")).isoformat(timespec="seconds")
    rows = [classify(row) for _, row in collect_candidates().iterrows()]
    rows.sort(key=lambda r: ({"high_review": 0, "medium_review": 1, "baseline_watch": 2}.get(str(r["ip_fto_risk"]), 9), -float(r["best_local_tanimoto"])))

    if rows:
        with CSV_OUT.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
    else:
        CSV_OUT.write_text("", encoding="utf-8")

    if not TEMPLATE.exists():
        with TEMPLATE.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=TEMPLATE_COLUMNS)
            writer.writeheader()

    counts = {risk: sum(1 for row in rows if row["ip_fto_risk"] == risk) for risk in ["high_review", "medium_review", "baseline_watch"]}
    lines = [
        "# IP FTO Watchlist",
        "",
        f"- timestamp: `{now}`",
        f"- rows: `{len(rows)}`",
        f"- risk_counts: `{counts}`",
        f"- manual_review_template: `{TEMPLATE.relative_to(ROOT)}`",
        "- purpose: local Tanimoto novelty와 실제 patent/FTO 검토를 분리해, 신규성/상업성 claim을 과장하지 않는다.",
        "",
        "## Review Queue",
        "",
        "| candidate | target | risk | novelty | scaffold | query terms |",
        "|---|---|---|---|---|---|",
    ]
    for row in rows[:35]:
        lines.append(
            f"| {row['candidate_id']} | {row['target']} | {row['ip_fto_risk']} | {row['novelty_gate']} | {row['murcko_scaffold']} | {row['manual_query_terms']} |"
        )
    lines.extend(
        [
            "",
            "## Curator Rule",
            "",
            "- `high_review`: patent/FTO 검토 전에는 novelty, freedom-to-operate, commercial differentiation claim을 금지한다.",
            "- `medium_review`: manuscript에는 local novelty까지만 쓰고 외부 patent search pending을 명시한다.",
            "- `baseline_watch`: follow-up 가능하지만 composition/use/formulation claim은 수동 검토 후에만 쓴다.",
            "",
        ]
    )
    DOC.write_text("\n".join(lines), encoding="utf-8")
    print(f"Saved {CSV_OUT.relative_to(ROOT)}")
    print(f"Saved {DOC.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
