"""Round 5 adapter sweep on full compound library — Snakefile-callable.

Applies PBK Dermal HT + SARA-ICE OECD TG 497-III + CarsiDock-Cov
warhead detection to every compound in our 6 source CSVs.

Output: pilot/round5_application/full_compound_sweep.csv (124 rows × 14 cols)
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
from rdkit import Chem, RDLogger
from rdkit.Chem import Crippen, Descriptors

from genesis_medicine.dermatology import DermalPBKAdapter, SARAICEAdapter
from genesis_medicine.md import CarsiDockCovAdapter

RDLogger.DisableLog("rdApp.*")

ROOT = Path(__file__).resolve().parents[1]
SOURCES = [
    ROOT / "data/skin_compounds_curated.csv",
    ROOT / "data/sar_panel_phase2.csv",
    ROOT / "data/screen_libraries/pigmentation_compounds.csv",
    ROOT / "data/screen_libraries/alopecia_compounds.csv",
    ROOT / "data/screen_libraries/acne_compounds.csv",
    ROOT / "data/screen_libraries/photoaging_compounds.csv",
]


def main():
    all_compounds: dict[str, tuple[str, str]] = {}
    for src in SOURCES:
        if not src.exists():
            continue
        df = pd.read_csv(src)
        if "smiles" not in df.columns:
            continue
        name_col = "compound" if "compound" in df.columns else "name"
        if name_col not in df.columns:
            continue
        for _, r in df.iterrows():
            c = str(r[name_col]).strip()
            s = str(r["smiles"]).strip()
            if c and s and c not in {"nan", ""} and s not in {"nan", ""} and c not in all_compounds:
                all_compounds[c] = (s, src.name)

    pbk = DermalPBKAdapter()
    sara = SARAICEAdapter()
    covd = CarsiDockCovAdapter()

    rows = []
    for comp, (smi, src_name) in all_compounds.items():
        mol = Chem.MolFromSmiles(smi)
        if mol is None:
            continue
        logp = Crippen.MolLogP(mol)
        mw = Descriptors.MolWt(mol)
        logkp = 0.71 * logp - 0.0061 * mw - 6.3
        pbk_r = pbk.simulate(compound=comp, smiles=smi, logkp_cm_h=logkp)
        sara_r = sara.predict(compound=comp, smiles=smi)
        cov_mmp = covd.score(compound=comp, smiles=smi, target="MMP1")
        cov_tyr = covd.score(compound=comp, smiles=smi, target="TYR")
        rows.append({
            "compound": comp, "smiles": smi, "source_csv": src_name,
            "mw": mw, "logp": logp, "logKp": logkp,
            "pbk_cmax_pmol_mL": pbk_r.cmax_dermis_pmol_per_mL,
            "pbk_tmax_h": pbk_r.tmax_h,
            "pbk_F_systemic": pbk_r.bioavailability_systemic,
            "sara_ghs": sara_r.ghs_category,
            "sara_p_strong": sara_r.posterior_strong,
            "sara_alerts": ";".join(sara_r.in_silico_alerts),
            "covalent_warheads": ";".join(cov_mmp.detected_warheads),
            "cys_mmp1": cov_mmp.proposed_residue_cys,
            "cys_tyr": cov_tyr.proposed_residue_cys,
        })

    df = pd.DataFrame(rows).sort_values("pbk_cmax_pmol_mL", ascending=False)
    out = ROOT / "pilot/round5_application/full_compound_sweep.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    print(f"✅ {out} — {len(df)} compounds")


if __name__ == "__main__":
    sys.exit(main())
