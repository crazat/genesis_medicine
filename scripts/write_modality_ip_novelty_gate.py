"""Write modality and local novelty gates for current candidates."""
from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd
from rdkit import Chem, DataStructs, RDLogger
from rdkit.Chem import AllChem


RDLogger.DisableLog("rdApp.*")

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_meaningful"
DOC = ROOT / "docs/MODALITY_IP_NOVELTY_GATE.md"
MODALITY_CSV = OUT / "target_modality_matrix.csv"
NOVELTY_CSV = OUT / "candidate_local_novelty_gate.csv"


def fp(smiles: str):
    mol = Chem.MolFromSmiles(str(smiles))
    if mol is None:
        return None
    return AllChem.GetMorganFingerprintAsBitVect(mol, 2, 2048)


def canonical(smiles: str) -> str:
    mol = Chem.MolFromSmiles(str(smiles))
    return Chem.MolToSmiles(mol, canonical=True) if mol else str(smiles)


def target_modality_rows() -> list[dict[str, object]]:
    gate = OUT / "target_evidence_gate.csv"
    if not gate.exists():
        return []
    rows = []
    df = pd.read_csv(gate)
    for _, row in df.iterrows():
        mode = str(row.get("modes", "")).lower()
        target = str(row.get("target", ""))
        if "inhibitor" in mode or "antagonist" in mode:
            primary = "small_molecule_topical"
        elif "agonist" in mode or "activator" in mode:
            primary = "pathway_modulator_or_biologic"
        elif "preserve" in mode or "support" in mode or "suppressor" in mode:
            primary = "phenotype_assay_first"
        else:
            primary = "evidence_first"
        degrader = "possible_low_priority" if target in {"AR", "NR3C1", "PTGS2", "SIRT1"} else "not_primary"
        biologic = "possible" if target in {"TGFB1", "CTGF", "VEGFA", "FGF2"} else "not_primary"
        rows.append(
            {
                "target": target,
                "diseases": row.get("diseases", ""),
                "gate": row.get("gate", ""),
                "primary_modality": primary,
                "degrader_or_glue": degrader,
                "biologic_or_peptide": biologic,
                "topical_formulation_fit": "high" if row.get("gate") in {"green", "yellow"} else "low",
                "note": row.get("next_action", ""),
            }
        )
    return rows


def collect_candidates() -> pd.DataFrame:
    frames = []
    r15 = OUT / "r15_chromanol_cofold_14targets.csv"
    if r15.exists():
        df = pd.read_csv(r15)
        frames.append(
            pd.DataFrame(
                {
                    "candidate_id": df.get("compound", "R15_chromanol"),
                    "target": df.get("target", ""),
                    "smiles": df.get("smiles", ""),
                    "source": "r15_chromanol_cofold",
                    "score": df.get("affinity_probability_binary", ""),
                }
            )
        )
    r16 = OUT / "r16_chromanol_topical_cofold.csv"
    if r16.exists():
        df = pd.read_csv(r16)
        frames.append(
            pd.DataFrame(
                {
                    "candidate_id": df.get("analog_id", ""),
                    "target": df.get("target", ""),
                    "smiles": df.get("smiles", ""),
                    "source": "r16_chromanol_topical_cofold",
                    "score": df.get("affinity_probability_binary", ""),
                }
            )
        )
    npass = OUT / "npass_xtb_refine_best_candidates.csv"
    if npass.exists():
        df = pd.read_csv(npass)
        smiles_col = "smiles" if "smiles" in df.columns else df.columns[0]
        frames.append(
            pd.DataFrame(
                {
                    "candidate_id": df["np_id"] if "np_id" in df.columns else df.get("compound_id", df.index.astype(str)),
                    "target": df.get("target", ""),
                    "smiles": df.get(smiles_col, ""),
                    "source": "npass_xtb_best",
                    "score": df.get("score", ""),
                }
            )
        )
    return pd.concat(frames, ignore_index=True).dropna(subset=["smiles"]) if frames else pd.DataFrame()


def reference_smiles() -> list[tuple[str, str]]:
    refs: list[tuple[str, str]] = []
    for path, label in [
        (ROOT / "data/skin_compounds_curated.csv", "curated_skin_compound"),
        (OUT / "full_herbal_xref.csv", "herbal_xref_candidate"),
        (OUT / "chembl_boltz2_calibration.csv", "chembl_calibration"),
    ]:
        if not path.exists():
            continue
        try:
            df = pd.read_csv(path)
        except Exception:
            continue
        if "smiles" not in df.columns:
            continue
        for smi in df["smiles"].dropna().head(5000):
            refs.append((label, str(smi)))
    return refs


def novelty_rows() -> list[dict[str, object]]:
    candidates = collect_candidates()
    if candidates.empty:
        return []
    refs = reference_smiles()
    ref_fps = [(label, smi, fp(smi)) for label, smi in refs]
    ref_fps = [(label, smi, f) for label, smi, f in ref_fps if f is not None]
    rows = []
    seen = set()
    for _, row in candidates.iterrows():
        smi = str(row["smiles"])
        can = canonical(smi)
        key = (str(row["candidate_id"]), str(row["target"]), can)
        if key in seen:
            continue
        seen.add(key)
        qfp = fp(can)
        best_t = 0.0
        best_label = ""
        best_ref = ""
        if qfp is not None and ref_fps:
            sims = DataStructs.BulkTanimotoSimilarity(qfp, [item[2] for item in ref_fps])
            if sims:
                idx = max(range(len(sims)), key=sims.__getitem__)
                best_t = float(sims[idx])
                best_label, best_ref, _ = ref_fps[idx]
        if best_t >= 0.85:
            novelty = "known_or_close_analog"
            action = "use as benchmark or require strong differentiation"
        elif best_t >= 0.60:
            novelty = "close_series"
            action = "keep but run IP/literature check before claim"
        elif best_t > 0:
            novelty = "locally_distinct"
            action = "eligible for follow-up if target evidence and safety pass"
        else:
            novelty = "reference_unavailable"
            action = "run external novelty/IP search before manuscript claim"
        rows.append(
            {
                "candidate_id": row["candidate_id"],
                "target": row["target"],
                "source": row["source"],
                "smiles": can,
                "score": row["score"],
                "best_local_tanimoto": round(best_t, 3),
                "best_reference_source": best_label,
                "best_reference_smiles": canonical(best_ref) if best_ref else "",
                "novelty_gate": novelty,
                "next_action": action,
            }
        )
    return rows


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    now = datetime.now(ZoneInfo("Asia/Seoul")).isoformat(timespec="seconds")
    modality = target_modality_rows()
    novelty = novelty_rows()
    write_csv(MODALITY_CSV, modality)
    write_csv(NOVELTY_CSV, novelty)

    top_novelty = sorted(novelty, key=lambda r: float(r["best_local_tanimoto"]))[:12]
    lines = [
        "# Modality and IP/Novelty Gate",
        "",
        f"- timestamp: `{now}`",
        f"- modality_targets: `{len(modality)}`",
        f"- candidate_rows: `{len(novelty)}`",
        "- purpose: small-molecule docking 일변도에서 벗어나 target별 적합 modality와 local novelty risk를 분리한다.",
        "",
        "## Target Modality Matrix",
        "",
        "| target | gate | primary modality | degrader/glue | biologic |",
        "|---|---|---|---|---|",
    ]
    for row in modality:
        lines.append(
            f"| {row['target']} | {row['gate']} | {row['primary_modality']} | {row['degrader_or_glue']} | {row['biologic_or_peptide']} |"
        )
    lines.extend(
        [
            "",
            "## Most Locally Distinct Current Candidates",
            "",
            "| candidate | target | source | best local T | novelty gate |",
            "|---|---|---|---:|---|",
        ]
    )
    for row in top_novelty:
        lines.append(
            f"| {row['candidate_id']} | {row['target']} | {row['source']} | {row['best_local_tanimoto']} | {row['novelty_gate']} |"
        )
    lines.extend(
        [
            "",
            "## Curator Use",
            "",
            "- `known_or_close_analog`는 benchmark 또는 validation control로 쓰고 신규성 claim을 피한다.",
            "- `locally_distinct`라도 외부 patent/PubChem/ChEMBL 검색 전에는 IP claim을 하지 않는다.",
            "- hard/indirect target은 docking paper가 아니라 phenotype 또는 modality paper로 전환한다.",
            "",
        ]
    )
    DOC.write_text("\n".join(lines), encoding="utf-8")
    print(f"Saved {DOC.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
