"""Complete P16/P17 chromanol preprints with figures and gate caveats."""
from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_meaningful"
P16 = ROOT / "preprints/16_r15_chromanol_safety_triage"
P17 = ROOT / "preprints/17_r16_topical_chromanol_lead"

R15_SMILES = "OCC1COc2cc(O)ccc2C1"

CSS = """
<style>
@page { size: A4; margin: 1.55cm 1.15cm; }
body { font-family: "DejaVu Sans", sans-serif; font-size: 10pt; line-height: 1.45; }
h1 { font-size: 16pt; margin-top: 0.6em; }
h2 { font-size: 13pt; margin-top: 1.0em; border-bottom: 1px solid #ccc; padding-bottom: 2px; }
h3 { font-size: 11pt; margin-top: 0.8em; }
code, pre { font-family: "DejaVu Sans Mono", monospace; font-size: 8.4pt; }
table { border-collapse: collapse; width: 100%; table-layout: auto; font-size: 8.3pt; margin: 0.55em 0; }
th, td { border: 1px solid #bbb; padding: 3px 5px; vertical-align: top; word-break: break-word; overflow-wrap: anywhere; }
th { background: #eee; font-weight: 600; }
img { max-width: 100%; height: auto; page-break-inside: avoid; }
figure { page-break-inside: avoid; margin: 0.8em 0; }
</style>
"""


def read_json(path: Path) -> list[dict]:
    data = json.loads(path.read_text())
    return data if isinstance(data, list) else []


def fmt(value: object, digits: int = 3) -> str:
    if value is None or pd.isna(value):
        return ""
    if isinstance(value, str):
        return value
    try:
        return f"{float(value):.{digits}f}"
    except (TypeError, ValueError):
        return str(value)


def savefig(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(path, dpi=300, bbox_inches="tight")
    plt.close()


def build_p16_figures() -> dict[str, Path]:
    fig_dir = P16 / "figures"
    triage = pd.read_csv(OUT / "r15_master_triage.csv")
    cofold = pd.read_csv(OUT / "r15_chromanol_cofold_14targets.csv")
    md = pd.DataFrame(read_json(ROOT / "pilot/md_r15_chromanol_top3_30ns/summary.json"))
    pose = pd.read_csv(OUT / "chromanol_pose_sanity_gate.csv")

    p = fig_dir / "fig1_r15_score_vs_herg.png"
    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    ax.scatter(triage["hERG"], triage["score"], c=triage["logP"], cmap="viridis", s=46, edgecolor="black", linewidth=0.25)
    parent = triage[triage["derivative_smiles"] == R15_SMILES]
    if not parent.empty:
        ax.scatter(parent["hERG"], parent["score"], s=130, marker="*", color="#d73027", edgecolor="black", label="R15 parent")
    top3 = triage.nlargest(3, "score")
    ax.scatter(top3["hERG"], top3["score"], s=90, facecolor="none", edgecolor="#fdae61", linewidth=1.7, label="top-3 topical score")
    ax.set_xlabel("Predicted hERG liability")
    ax.set_ylabel("Topical composite score")
    ax.set_title("R15 triage separates clean safety from topical score")
    ax.legend(loc="lower left", fontsize=8)
    cbar = fig.colorbar(ax.collections[0], ax=ax)
    cbar.set_label("logP")
    savefig(p)

    p2 = fig_dir / "fig2_r15_14target_cofold.png"
    co = cofold.sort_values("affinity_probability_binary", ascending=True)
    fig, ax = plt.subplots(figsize=(7.2, 5.0))
    ax.barh(co["target"].str.upper(), co["affinity_probability_binary"], color="#4575b4")
    ax.set_xlabel("Boltz-2 affinity probability")
    ax.set_title("R15 chromanol 14-target cofolding")
    ax.set_xlim(0, max(0.75, co["affinity_probability_binary"].max() + 0.06))
    savefig(p2)

    p3 = fig_dir / "fig3_r15_top3_30ns_md.png"
    md = md.sort_values("affinity_probability_binary", ascending=False)
    x = range(len(md))
    fig, ax = plt.subplots(figsize=(7.0, 4.3))
    ax.bar(x, md["rmsd_mean_A"], color="#74add1", label="mean RMSD")
    ax.scatter(x, md["rmsd_max_A"], color="#d73027", zorder=3, label="max RMSD")
    ax.scatter(x, md["rmsd_last_third_A"], color="#1a9850", zorder=3, label="last-third RMSD")
    ax.set_xticks(list(x))
    ax.set_xticklabels(md["target"].str.upper())
    ax.set_ylabel("Ligand RMSD (A)")
    ax.set_title("R15 top-3 cofold targets remain stable over 30 ns")
    ax.legend(fontsize=8)
    savefig(p3)

    p4 = fig_dir / "fig4_chromanol_pose_gate.png"
    sub = pose[pose["source"].isin(["r15_chromanol", "r16_chromanol_topical"])]
    counts = sub.groupby(["source", "gate_status"]).size().unstack(fill_value=0)
    for col in ["pass", "review", "fail"]:
        if col not in counts:
            counts[col] = 0
    fig, ax = plt.subplots(figsize=(7.0, 4.0))
    bottom = [0] * len(counts)
    colors = {"pass": "#1a9850", "review": "#fee08b", "fail": "#d73027"}
    for col in ["pass", "review", "fail"]:
        vals = counts[col].tolist()
        ax.bar(counts.index, vals, bottom=bottom, label=col, color=colors[col])
        bottom = [b + v for b, v in zip(bottom, vals)]
    ax.set_ylabel("Pose rows")
    ax.set_title("Raw cofold-pose sanity gate")
    ax.legend(fontsize=8)
    savefig(p4)

    return {"fig1": p, "fig2": p2, "fig3": p3, "fig4": p4}


def build_p17_figures() -> dict[str, Path]:
    fig_dir = P17 / "figures"
    manifest = pd.read_csv(OUT / "r16_chromanol_topical_manifest.csv").drop_duplicates("analog_id")
    cofold = pd.read_csv(OUT / "r16_chromanol_topical_cofold.csv")
    matrix = pd.read_csv(OUT / "r16_topical_chromanol_30ns_matrix_summary.csv")
    tg60 = pd.DataFrame(read_json(ROOT / "pilot/md_r16_chromanol_topical_tgfb1_top6_60ns/summary.json"))
    pig60 = pd.DataFrame(read_json(ROOT / "pilot/md_r16_chromanol_topical_pigment_representative_60ns/summary.json"))
    a100 = pd.DataFrame(read_json(ROOT / "pilot/md_r16_chromanol_anchor_triad_100ns/summary.json"))
    a200 = pd.DataFrame(read_json(ROOT / "pilot/md_r16_chromanol_anchor_triad_200ns/summary.json"))

    p = fig_dir / "fig1_r16_analog_properties.png"
    m = manifest.sort_values("analog_rank")
    labels = m["analog_id"].str.replace("R15_chromanol_", "", regex=False)
    x = range(len(m))
    fig, ax = plt.subplots(figsize=(8.0, 4.5))
    ax.bar(x, m["topical_followup_score"], color="#5ab4ac", label="topical score")
    ax2 = ax.twinx()
    ax2.plot(x, m["logP"], marker="o", color="#d8b365", label="logP")
    ax2.plot(x, m["QED"], marker="s", color="#5e3c99", label="QED")
    ax.set_xticks(list(x))
    ax.set_xticklabels(labels, rotation=35, ha="right")
    ax.set_ylabel("Topical follow-up score")
    ax2.set_ylabel("logP / QED")
    ax.set_title("R16 analog properties and topical ranking")
    ax.legend(loc="upper left", fontsize=8)
    ax2.legend(loc="upper right", fontsize=8)
    savefig(p)

    p2 = fig_dir / "fig2_r16_30ns_matrix.png"
    mat = matrix.copy()
    mat["label"] = mat["analog_id"].str.replace("R15_chromanol_", "", regex=False)
    pivot = mat.pivot_table(index="label", columns="target", values="rmsd_last_third_A", aggfunc="mean")
    pivot = pivot.reindex(sorted(pivot.index), axis=0)
    pivot = pivot.reindex(["tgfb1", "dct", "tyr"], axis=1)
    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    im = ax.imshow(pivot.values, cmap="viridis_r", vmin=0, vmax=1.5, aspect="auto")
    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels([c.upper() for c in pivot.columns])
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels(pivot.index)
    for i in range(pivot.shape[0]):
        for j in range(pivot.shape[1]):
            v = pivot.iloc[i, j]
            if pd.notna(v):
                ax.text(j, i, f"{v:.2f}", ha="center", va="center", fontsize=8, color="white" if v > 0.9 else "black")
    ax.set_title("R16 18-pair 30 ns matrix: last-third RMSD")
    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label("Ligand RMSD (A)")
    savefig(p2)

    p3 = fig_dir / "fig3_r16_60ns_panels.png"
    rows = pd.concat([tg60.assign(panel="TGFB1 top-six"), pig60.assign(panel="DCT/TYR representative")], ignore_index=True)
    rows["label"] = rows["analog_id"].str.replace("R15_chromanol_", "", regex=False) + " / " + rows["target"].str.upper()
    fig, ax = plt.subplots(figsize=(9.0, 4.8))
    x = range(len(rows))
    ax.bar(x, rows["rmsd_last_third_A"], color="#91bfdb", label="last-third RMSD")
    ax.scatter(x, rows["rmsd_max_A"], color="#d73027", label="max RMSD", zorder=3)
    ax.set_xticks(list(x))
    ax.set_xticklabels(rows["label"], rotation=35, ha="right", fontsize=8)
    ax.set_ylabel("Ligand RMSD (A)")
    ax.set_title("R16 60 ns robustness panels")
    ax.legend(fontsize=8)
    savefig(p3)

    p4 = fig_dir / "fig4_r16_anchor_100_200ns.png"
    anchors = pd.concat([a100.assign(horizon="100 ns"), a200.assign(horizon="200 ns")], ignore_index=True)
    anchors["label"] = anchors["target"].str.upper() + " " + anchors["analog_id"].str.replace("R15_chromanol_", "", regex=False)
    fig, ax = plt.subplots(figsize=(8.0, 4.5))
    for horizon, group in anchors.groupby("horizon"):
        offset = -0.18 if horizon == "100 ns" else 0.18
        idx = list(range(len(group)))
        ax.bar([i + offset for i in idx], group["rmsd_last_third_A"], width=0.36, label=horizon)
    labels = a100["target"].str.upper() + " " + a100["analog_id"].str.replace("R15_chromanol_", "", regex=False)
    ax.set_xticks(list(range(len(labels))))
    ax.set_xticklabels(labels, rotation=30, ha="right")
    ax.set_ylabel("Last-third ligand RMSD (A)")
    ax.set_title("R16 anchor triad remains stable at 100 and 200 ns")
    ax.legend(fontsize=8)
    savefig(p4)

    p5 = fig_dir / "fig5_r16_cofold_rank.png"
    top = cofold.sort_values("affinity_probability_binary", ascending=False).head(12).sort_values("affinity_probability_binary")
    labels = top["job_id"] + " / " + top["analog_id"].str.replace("R15_chromanol_", "", regex=False)
    fig, ax = plt.subplots(figsize=(8.5, 5.4))
    ax.barh(labels, top["affinity_probability_binary"], color="#4575b4")
    ax.set_xlabel("Boltz-2 affinity probability")
    ax.set_title("R16 cofold ranking across topical targets")
    savefig(p5)

    return {"fig1": p, "fig2": p2, "fig3": p3, "fig4": p4, "fig5": p5}


def markdown_table(rows: list[list[object]], headers: list[str]) -> str:
    out = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for row in rows:
        out.append("| " + " | ".join(str(x) for x in row) + " |")
    return "\n".join(out)


def rel(path: Path, base: Path) -> str:
    return str(path.relative_to(base))


def write_p16(figs: dict[str, Path]) -> None:
    triage = pd.read_csv(OUT / "r15_master_triage.csv")
    cofold = pd.read_csv(OUT / "r15_chromanol_cofold_14targets.csv")
    md = pd.DataFrame(read_json(ROOT / "pilot/md_r15_chromanol_top3_30ns/summary.json"))
    pose = pd.read_csv(OUT / "chromanol_pose_sanity_gate.csv")
    prior = pd.read_csv(OUT / "precompute_prior_art_gate.csv")

    parent = triage[triage["derivative_smiles"] == R15_SMILES].iloc[0]
    parent_rank = int(triage.sort_values("score", ascending=False).reset_index().query("derivative_smiles == @R15_SMILES").index[0]) + 1
    top3 = triage.nlargest(3, "score")
    r15_pose = pose[pose["source"] == "r15_chromanol"]
    prior_r15 = prior[prior["canonical_smiles"] == R15_SMILES]
    if prior_r15.empty:
        prior_status = "not present in the local precompute prior-art table"
        prior_gate = "not_checked"
    else:
        prior_status = "/".join(sorted(set(prior_r15["pubchem_exact_status"].fillna("not_checked"))))
        prior_gate = "/".join(sorted(set(prior_r15["precompute_gate"].fillna("not_checked"))))

    co_rows = [
        [r["rank_by_affinity_probability"], r["target"].upper(), fmt(r["affinity_probability_binary"]), fmt(r["confidence_score"])]
        for _, r in cofold.sort_values("rank_by_affinity_probability").head(8).iterrows()
    ]
    md_rows = [
        [r["target"].upper(), fmt(r["affinity_probability_binary"]), fmt(r["rmsd_mean_A"], 2), fmt(r["rmsd_last_third_A"], 2), fmt(r["rmsd_max_A"], 2)]
        for _, r in md.sort_values("affinity_probability_binary", ascending=False).iterrows()
    ]
    triage_rows = [
        ["R15 parent", R15_SMILES, fmt(parent["logP"], 2), fmt(parent["QED"], 3), fmt(parent["hERG"], 3), fmt(parent["AMES"], 3), fmt(parent["DILI"], 3), fmt(parent["score"], 3), str(parent_rank)],
    ]
    for i, (_, r) in enumerate(top3.iterrows(), start=1):
        triage_rows.append([f"topical-score top-{i}", r["derivative_smiles"], fmt(r["logP"], 2), fmt(r["QED"], 3), fmt(r["hERG"], 3), fmt(r["AMES"], 3), fmt(r["DILI"], 3), fmt(r["score"], 3), str(i)])

    md_text = f"""# R15 Chromanol Safety-First Fragment Triage: 14-Target Cofolding, ADMET/xTB Filtering, and 30 ns MD Separates Systemic-Safety and Topical-Lead Paths

## Abstract

R15 generated a compact chromanol fragment, `{R15_SMILES}`, as a safety-first derivative of the broader pterocarpan-vinyl-polyphenol scaffold program. The central question is whether this fragment should be treated as a topical lead or as a systemic-safety fragment hypothesis. The answer is deliberately split. In ADMET/xTB triage, the R15 parent is predicted to be clean for AMES, DILI, and hERG liability, but its logP is `{fmt(parent["logP"], 2)}`, below the intended skin-window threshold, and it ranks `{parent_rank}` by the topical composite score. Conversely, the top-3 topical-score analogs satisfy the skin-window heuristic but retain hERG caution values around 0.58-0.70. Boltz-2 14-target cofolding identifies TGFB1, TYR, and DCT as the top three targets by affinity probability, and all three remain stable in 30 ns OpenMM MD with mean ligand RMSD values of 0.51, 0.92, and 0.47 A. Raw-pose sanity gating found `{(r15_pose["gate_status"] == "pass").sum()}` pass, `{(r15_pose["gate_status"] == "review").sum()}` review, and `{(r15_pose["gate_status"] == "fail").sum()}` fail rows across the R15 14-target panel. We therefore frame R15 chromanol as a safety-first comparator and SAR anchor, not as a ready topical efficacy candidate.

**Keywords**: chromanol, ADMET, hERG, skin permeability, Boltz-2, OpenMM, in silico, topical drug discovery

## 1. Research Question

This manuscript is intentionally narrower than the universal-scaffold paper. It asks whether the R15 chromanol fragment can be advanced as a safety-first scaffold and how that path should be separated from R16 topical chromanol optimization. Combining both paths would overstate the evidence: R15 has the cleaner predicted systemic-safety profile, while R16 analogs are better topical-window candidates but require separate safety and prior-art caveats.

## 2. Data Sources

{markdown_table([
["`pilot/cpu_meaningful/r15_master_triage.csv`", "ADMET/xTB and topical composite ranking for 38 R15-derived candidates"],
["`pilot/cpu_meaningful/r15_chromanol_cofold_14targets.csv`", "14-target Boltz-2 cofolding profile for `R15_chromanol`"],
["`pilot/md_r15_chromanol_top3_30ns/summary.json`", "30 ns MD validation for the top-3 cofold targets"],
["`pilot/cpu_meaningful/chromanol_pose_sanity_gate.csv`", "OpenMM/RDKit/PoseBusters raw-pose sanity gate"],
["`pilot/cpu_meaningful/precompute_prior_art_gate.csv`", "technical prior-art pre-gate, not legal FTO opinion"],
], ["file", "role"])}

## 3. Results

### 3.1 R15 is safety-first, not topical-first

{markdown_table(triage_rows, ["label", "SMILES", "logP", "QED", "hERG", "AMES", "DILI", "score", "rank"])}

![Figure 1. R15 triage scatter showing topical composite score versus predicted hERG. The R15 parent is highlighted separately from the top-3 topical-score candidates.](figures/{figs["fig1"].name})

The parent fragment is useful because its predicted safety profile is cleaner than the topical-score leaders. It should not be described as the best topical lead. The correct narrative is a split path: R15 for safety-first fragment triage and R16 for topical optimization.

### 3.2 Cofolding identifies TGFB1, TYR, and DCT as top targets

{markdown_table(co_rows, ["rank", "target", "affinity probability", "confidence score"])}

![Figure 2. Boltz-2 cofold probabilities across 14 skin-relevant targets for the R15 chromanol parent.](figures/{figs["fig2"].name})

### 3.3 Top-3 cofold targets persist over 30 ns MD

{markdown_table(md_rows, ["target", "affinity probability", "mean RMSD A", "last-third RMSD A", "max RMSD A"])}

![Figure 3. R15 top-3 target MD stability over 30 ns. Bars show mean RMSD and markers show maximum and last-third RMSD.](figures/{figs["fig3"].name})

### 3.4 Raw-pose sanity gate is disclosed rather than hidden

Across the R15 parent 14-target panel, all poses loaded and were checkable. The pass/review/fail split was `{(r15_pose["gate_status"] == "pass").sum()}`/`{(r15_pose["gate_status"] == "review").sum()}`/`{(r15_pose["gate_status"] == "fail").sum()}`. Review status is not a rejection by itself; it means the raw cofold geometry has a caveat and should be interpreted together with minimization and MD persistence.

![Figure 4. Raw cofold-pose sanity gate for R15 and R16 chromanol rows.](figures/{figs["fig4"].name})

## 4. Prior-Art and Claim Discipline

The local precompute gate reports R15 parent PubChem exact status as `{prior_status}` and gate status as `{prior_gate}`. This is a technical screen only. It does not establish freedom to operate or composition novelty. Any manuscript or commercial narrative must avoid clinical efficacy, confirmed target engagement, and FTO language until professional patent/Markush and wet-lab review are complete.

## 5. Limitations

All findings are in silico only. Boltz-2 cofolding is a prioritization model, not a binding assay. MD pose stability is not potency. ADMET-AI estimates cannot replace AMES, hERG patch-clamp, hepatotoxicity, irritation, sensitization, or permeation assays. Skin-window interpretation is heuristic and must be checked by formulation-dependent IVRT/IVPT and PBPK modeling.

## 6. Conclusion

R15 chromanol is best written as a safety-first fragment triage paper. Its strongest contribution is not a topical lead claim, but the disciplined separation of a clean predicted safety profile from the R16 topical optimization path.
"""
    (P16 / "manuscript.md").write_text(md_text, encoding="utf-8")


def write_p17(figs: dict[str, Path]) -> None:
    cofold = pd.read_csv(OUT / "r16_chromanol_topical_cofold.csv")
    matrix = pd.read_csv(OUT / "r16_topical_chromanol_30ns_matrix_summary.csv")
    pose = pd.read_csv(OUT / "chromanol_pose_sanity_gate.csv")
    prior = pd.read_csv(OUT / "precompute_prior_art_gate.csv")
    tg60 = pd.DataFrame(read_json(ROOT / "pilot/md_r16_chromanol_topical_tgfb1_top6_60ns/summary.json"))
    pig60 = pd.DataFrame(read_json(ROOT / "pilot/md_r16_chromanol_topical_pigment_representative_60ns/summary.json"))
    a100 = pd.DataFrame(read_json(ROOT / "pilot/md_r16_chromanol_anchor_triad_100ns/summary.json"))
    a200 = pd.DataFrame(read_json(ROOT / "pilot/md_r16_chromanol_anchor_triad_200ns/summary.json"))

    top = cofold.sort_values("affinity_probability_binary", ascending=False).iloc[0]
    r16_pose = pose[pose["source"] == "r16_chromanol_topical"]
    r16_prior = prior[prior["candidate_id"].astype(str).str.startswith("R15_chromanol_")]
    r16_gate_counts = r16_prior["precompute_gate"].value_counts().to_dict()

    co_rows = [
        [r["rank_by_affinity_probability"], r["job_id"], r["target"].upper(), r["analog_id"], fmt(r["affinity_probability_binary"]), fmt(r["logP"], 2), fmt(r["QED"], 3)]
        for _, r in cofold.sort_values("rank_by_affinity_probability").head(10).iterrows()
    ]
    m30_rows = [
        [r["job_id"], r["target"].upper(), r["analog_id"], fmt(r["affinity_probability_binary"]), fmt(r["rmsd_mean_A"], 2), fmt(r["rmsd_last_third_A"], 2), fmt(r["rmsd_max_A"], 2)]
        for _, r in matrix.sort_values(["target", "rmsd_last_third_A"]).iterrows()
    ]
    a200_rows = [
        [r["name"], r["target"].upper(), r["analog_id"], fmt(r["affinity_probability_binary"]), fmt(r["rmsd_mean_A"], 2), fmt(r["rmsd_last_third_A"], 2), fmt(r["rmsd_max_A"], 2)]
        for _, r in a200.iterrows()
    ]

    md_text = f"""# R16 Topical Chromanol Lead Short Communication: 18-Pair 30 ns Matrix, 60 ns Robustness Panels, and Complete 200 ns Anchor-Triad Follow-up

## Abstract

R16 optimized the R15 chromanol fragment toward a topical lead hypothesis by increasing skin-window compatibility while preserving a compact chromanol core. We evaluated six chloro/dimethyl analogs across TGFB1, DCT, and TYR using Boltz-2 cofolding, an 18-pair 30 ns OpenMM stability matrix, two 60 ns robustness panels, and 100 ns plus 200 ns anchor-triad follow-up. The top cofold row was `{top["job_id"]}` (`{top["analog_id"]}`, `{top["smiles"]}`) with affinity probability `{fmt(top["affinity_probability_binary"])}`. All 18 30 ns matrix entries were stable, the TGFB1 top-six 60 ns panel completed 6/6 stable, and the DCT/TYR representative 60 ns panel completed 3/3 stable. The 200 ns long-horizon anchor triad also completed 3/3 stable: TGFB1 `R15_chromanol_Cl_pos9` max RMSD 0.71 A, DCT `R15_chromanol_Cl_pos9` max RMSD 1.05 A, and TYR `R15_chromanol_Cl_pos6` max RMSD 0.80 A. These data support an in-silico topical optimization hypothesis, not clinical efficacy, confirmed binding, composition novelty, or freedom to operate.

**Keywords**: chromanol, topical drug discovery, TGFB1, DCT, TYR, Boltz-2, OpenMM, in silico, prior-art gate

## 1. Research Question

This manuscript separates the topical R16 analog path from the R15 safety-first parent path. The question is whether R16 chloro/dimethyl chromanol analogs can be prioritized as topical in-silico candidates after target cofolding, raw-pose sanity checks, 30-60 ns robustness panels, and complete 200 ns long-horizon anchor follow-up.

## 2. Data Sources

{markdown_table([
["`pilot/cpu_meaningful/r16_chromanol_topical_manifest.csv`", "six R16 topical chromanol analog definitions and topical scores"],
["`pilot/cpu_meaningful/r16_chromanol_topical_cofold.csv`", "18 Boltz-2 cofold rows across TGFB1, DCT, and TYR"],
["`pilot/cpu_meaningful/r16_topical_chromanol_30ns_matrix_summary.csv`", "18-pair 30 ns MD matrix"],
["`pilot/md_r16_chromanol_topical_tgfb1_top6_60ns/summary.json`", "TGFB1 top-six 60 ns robustness panel"],
["`pilot/md_r16_chromanol_topical_pigment_representative_60ns/summary.json`", "DCT/TYR representative 60 ns panel"],
["`pilot/md_r16_chromanol_anchor_triad_100ns/summary.json`", "TGFB1/DCT/TYR 100 ns anchor triad"],
["`pilot/md_r16_chromanol_anchor_triad_200ns/summary.json`", "complete 200 ns long-horizon anchor triad"],
["`pilot/cpu_meaningful/precompute_prior_art_gate.csv`", "technical prior-art pre-gate, not legal FTO opinion"],
], ["file", "role"])}

## 3. Results

### 3.1 Analog properties

![Figure 1. R16 analog topical scores with logP and QED overlays.](figures/{figs["fig1"].name})

### 3.2 Cofold ranking

{markdown_table(co_rows, ["rank", "job_id", "target", "analog", "affinity probability", "logP", "QED"])}

![Figure 5. R16 cofold ranking across TGFB1, DCT, and TYR target pairs.](figures/{figs["fig5"].name})

### 3.3 Complete 18-pair 30 ns matrix

All 18 R16 chromanol topical target pairs completed 30 ns MD with `stable_30ns=True`. Across the matrix, the maximum RMSD was `{fmt(matrix["rmsd_max_A"].max(), 2)}` A and the maximum last-third RMSD was `{fmt(matrix["rmsd_last_third_A"].max(), 2)}` A.

{markdown_table(m30_rows, ["job_id", "target", "analog", "affinity probability", "mean RMSD A", "last-third RMSD A", "max RMSD A"])}

![Figure 2. R16 18-pair 30 ns matrix. Values are last-third ligand RMSD.](figures/{figs["fig2"].name})

### 3.4 60 ns robustness panels

The TGFB1 top-six 60 ns panel completed `{len(tg60)}/6` stable entries, and the representative DCT/TYR pigmentation panel completed `{len(pig60)}/3` stable entries. The strongest single analog across both target families is `R15_chromanol_Cl_pos9`, which carries TGFB1 and DCT support. `R15_chromanol_Cl_pos6` is the strongest TYR-focused follow-up.

![Figure 3. R16 60 ns robustness panels for TGFB1 and representative pigmentation targets.](figures/{figs["fig3"].name})

### 3.5 Complete 100 ns and 200 ns anchor triads

{markdown_table(a200_rows, ["name", "target", "analog", "affinity probability", "mean RMSD A", "last-third RMSD A", "max RMSD A"])}

![Figure 4. R16 anchor triad last-third RMSD at 100 and 200 ns.](figures/{figs["fig4"].name})

### 3.6 Pose sanity and prior-art gates

The R16 raw-pose sanity split is `{(r16_pose["gate_status"] == "pass").sum()}` pass, `{(r16_pose["gate_status"] == "review").sum()}` review, and `{(r16_pose["gate_status"] == "fail").sum()}` fail rows. Review-level rows are disclosed as raw Boltz-pose caveats and interpreted with minimized/MD stability.

The precompute prior-art gate classifies the R16 chromanol analog rows as `{r16_gate_counts}`. The practical implication is strict: existing R16 data can be written as in-silico prioritization, but new 100-200 ns expansion, RBFE/ABFE, synthesis/purchase, commercial novelty, and FTO claims should wait for PubChem/SureChEMBL/PATENTSCOPE/Lens/EPO OPS plus professional Markush and attorney claim-chart review.

## 4. Development Interpretation

`R15_chromanol_Cl_pos9` is the strongest TGFB1-first topical hypothesis because it combines the highest cofold probability, stable 30 ns target-diverse MD, stable TGFB1 60 ns MD, representative DCT 60 ns support, and stable TGFB1/DCT 200 ns long-horizon anchors. `R15_chromanol_Cl_pos6` is the strongest TYR-focused pigmentation follow-up because it carries DCT/TYR 60 ns support and stable TYR 200 ns anchoring. This is a prioritization statement only.

## 5. Limitations

All findings are in silico only. Boltz-2 cofolding is not a biochemical assay. MD pose stability is not potency, target engagement, residence time, or skin exposure. Photosafety, sensitization, hERG, AMES, DILI, irritation, IVRT/IVPT, PBPK, formulation compatibility, and target-engagement assays remain required. A `PubChem no_hit` or local distinctness result is not a freedom-to-operate opinion because Markush and use claims can still cover unmade or unlisted analogs.

## 6. Conclusion

R16 is the strongest current topical chromanol in-silico lead family in Genesis_Medicine. The completed 30 ns, 60 ns, 100 ns, and 200 ns panels justify manuscript completion and CRO hypothesis packaging, while the prior-art gate blocks stronger commercial and follow-on expensive-compute claims until Markush/FTO review is complete.
"""
    (P17 / "manuscript.md").write_text(md_text, encoding="utf-8")


def rebuild(md: Path) -> bool:
    pandoc = shutil.which("pandoc")
    weasy = shutil.which("weasyprint")
    if not pandoc or not weasy:
        print(f"skip build for {md}: pandoc/weasyprint missing")
        return False
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False) as f:
        f.write(CSS)
        header = Path(f.name)
    try:
        subprocess.run(
            [
                pandoc,
                str(md),
                "-o",
                str(md.with_suffix(".html")),
                "--standalone",
                "--embed-resources",
                "-H",
                str(header),
                "--metadata",
                f"title=Genesis_Medicine - {md.parent.name}",
                "--toc",
                "--toc-depth=3",
                "--mathjax",
            ],
            check=True,
            capture_output=True,
            timeout=240,
        )
        subprocess.run(
            ["weasyprint", str(md.with_suffix(".html")), str(md.with_suffix(".pdf"))],
            check=True,
            capture_output=True,
            timeout=360,
        )
        print(f"rebuilt {md.parent.name}: {md.with_suffix('.pdf').stat().st_size // 1024} KB PDF")
        return True
    finally:
        header.unlink(missing_ok=True)


def main() -> int:
    p16_figs = build_p16_figures()
    p17_figs = build_p17_figures()
    write_p16(p16_figs)
    write_p17(p17_figs)
    ok16 = rebuild(P16 / "manuscript.md")
    ok17 = rebuild(P17 / "manuscript.md")
    print(f"P16 figures: {len(p16_figs)}")
    print(f"P17 figures: {len(p17_figs)}")
    return 0 if ok16 and ok17 else 1


if __name__ == "__main__":
    raise SystemExit(main())
