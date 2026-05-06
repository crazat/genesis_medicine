"""AEMS/FAERS-style pharmacovigilance signal pre-gate."""
from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd
from rdkit import Chem, RDLogger
from rdkit.Chem import Descriptors


RDLogger.DisableLog("rdApp.*")

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_meaningful"
CSV_OUT = OUT / "pharmacovigilance_signal_gate.csv"
DOC = ROOT / "docs/PHARMACOVIGILANCE_SIGNAL_GATE.md"

TARGET_CLASS_SIGNALS = {
    "ar": "antiandrogen/endocrine class: libido, teratogenicity, systemic endocrine effects",
    "nr3c1": "corticosteroid class: skin atrophy, HPA-axis suppression, infection risk",
    "ptgs2": "NSAID/COX class: GI, renal, hypersensitivity, cardiovascular warning",
    "tyr": "depigmenting agent class: irritation, ochronosis-like, photosensitivity review",
    "dct": "pigmentation pathway class: pigment alteration and photosensitivity review",
    "tgfb1": "anti-fibrotic pathway: wound-healing delay and immune modulation review",
    "mmp1": "matrix remodeling class: wound remodeling and irritation review",
}


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()


def canonical(smiles: str) -> str:
    mol = Chem.MolFromSmiles(str(smiles))
    return Chem.MolToSmiles(mol, canonical=True) if mol else str(smiles)


def collect_candidates() -> pd.DataFrame:
    frames = []
    for path, source, id_col in [
        (OUT / "structure_consensus_v2.csv", "structure_consensus", "compound"),
        (OUT / "dermal_regulatory_safety_gate.csv", "dermal_gate", "candidate_id"),
        (OUT / "chromanol_generative_optimizer.csv", "chromanol_generator", "design_id"),
    ]:
        df = read_csv(path)
        if df.empty or "smiles" not in df.columns:
            continue
        frames.append(pd.DataFrame({"candidate_id": df.get(id_col, ""), "target": df.get("target", ""), "smiles": df["smiles"], "source": source}))
    if not frames:
        return pd.DataFrame()
    out = pd.concat(frames, ignore_index=True)
    out["smiles"] = out["smiles"].astype(str).map(canonical)
    return out[out["smiles"].ne("")].drop_duplicates(subset=["candidate_id", "target", "smiles"])


def r15_hERG_lookup() -> dict[str, float]:
    df = read_csv(OUT / "r15_master_triage.csv")
    out: dict[str, float] = {}
    if df.empty:
        return out
    for _, row in df.iterrows():
        smi = canonical(str(row.get("derivative_smiles", "")))
        try:
            out[smi] = float(row.get("hERG", 0) or 0)
        except Exception:
            pass
    return out


def classify(target: str, smiles: str, herg: float | None) -> dict[str, object]:
    mol = Chem.MolFromSmiles(smiles)
    logp = Descriptors.MolLogP(mol) if mol else 0.0
    class_signal = TARGET_CLASS_SIGNALS.get(str(target).lower(), "no close approved-drug class signal mapped")
    warning_terms = []
    if herg is not None and herg >= 0.5:
        warning_terms.append("hERG_signal_review")
    if str(target).lower() in {"tyr", "dct", "tyrp1", "mc1r"}:
        warning_terms.append("photosensitivity_or_pigment_AE_review")
    if logp > 3.5:
        warning_terms.append("systemic_absorption_or_accumulation_review")
    if str(target).lower() in {"ar", "nr3c1", "ptgs2"}:
        warning_terms.append("known_systemic_class_warning")
    if "no close" in class_signal and not warning_terms:
        gate = "pv_signal_not_mapped"
        action = "keep as limitation; do not infer absence of safety signal"
    elif warning_terms:
        gate = "pv_signal_review"
        action = "query AEMS/FAERS or literature class safety before systemic or topical safety claim"
    else:
        gate = "pv_class_caveat"
        action = "include class-signal caveat; use only as safety signal, not causation"
    return {
        "class_signal_context": class_signal,
        "hERG_proxy": "" if herg is None else round(herg, 4),
        "pv_warning_terms": ";".join(warning_terms) if warning_terms else "none_mapped",
        "pharmacovigilance_gate": gate,
        "external_query_needed": "FDA AEMS/FAERS public dashboard or quarterly files;MedDRA signal terms;class analog literature",
        "next_action": action,
    }


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    now = datetime.now(ZoneInfo("Asia/Seoul")).isoformat(timespec="seconds")
    candidates = collect_candidates()
    herg = r15_hERG_lookup()
    rows = []
    for _, row in candidates.iterrows():
        smi = str(row["smiles"])
        rows.append({**row.to_dict(), **classify(str(row.get("target", "")), smi, herg.get(smi))})
    rows.sort(key=lambda r: {"pv_signal_review": 0, "pv_class_caveat": 1, "pv_signal_not_mapped": 2}.get(str(r["pharmacovigilance_gate"]), 9))
    if rows:
        with CSV_OUT.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
    else:
        CSV_OUT.write_text("", encoding="utf-8")
    counts = {g: sum(1 for r in rows if r["pharmacovigilance_gate"] == g) for g in ["pv_signal_review", "pv_class_caveat", "pv_signal_not_mapped"]}
    lines = [
        "# Pharmacovigilance Signal Gate",
        "",
        f"- timestamp: `{now}`",
        f"- rows: `{len(rows)}`",
        f"- gate_counts: `{counts}`",
        "- purpose: FDA AEMS/FAERS 또는 class analog safety signal을 논문 safety caveat와 systemic/topical path 분리에 연결한다.",
        "",
        "## PV Rows",
        "",
        "| candidate | target | gate | warning terms | class context | next |",
        "|---|---|---|---|---|---|",
    ]
    for row in rows[:45]:
        lines.append(
            f"| {row['candidate_id']} | {row['target']} | {row['pharmacovigilance_gate']} | {row['pv_warning_terms']} | {row['class_signal_context']} | {row['next_action']} |"
        )
    lines.extend(
        [
            "",
            "## Curator Rule",
            "",
            "- `pv_signal_review`: AEMS/FAERS/literature class safety query 전까지 safety-positive 표현 금지.",
            "- `pv_class_caveat`: 신호는 causation이 아니며 manuscript limitation으로만 사용한다.",
            "- `pv_signal_not_mapped`: 안전하다는 뜻이 아니라 데이터 미연결 상태다.",
            "",
        ]
    )
    DOC.write_text("\n".join(lines), encoding="utf-8")
    print(f"Saved {CSV_OUT.relative_to(ROOT)}")
    print(f"Saved {DOC.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
