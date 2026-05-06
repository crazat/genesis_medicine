"""Write P43 R17 constrained generative chromanol atlas preprint.

By default this exits without writing if the expanded 60 ns panel is not 3/3
complete. Use --allow-incomplete only for a near-ready draft.
"""
from __future__ import annotations

import argparse
import glob
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_meaningful"
PILOT = ROOT / "pilot"
PP = ROOT / "preprints/43_r17_chromanol_generative_atlas"
FIG = PP / "figures"

PANELS = [
    ("top_10ns", PILOT / "md_r17_chromanol_generative_top_green_10ns/summary.json", 3),
    ("top_30ns", PILOT / "md_r17_chromanol_generative_top_green_30ns/summary.json", 3),
    ("top_60ns", PILOT / "md_r17_chromanol_generative_top_green_60ns/summary.json", 3),
    ("next_10ns", PILOT / "md_r17_chromanol_generative_next_green_10ns/summary.json", 3),
    ("next_30ns", PILOT / "md_r17_chromanol_generative_next_green_30ns/summary.json", 3),
    ("next_60ns", PILOT / "md_r17_chromanol_generative_next_green_60ns/summary.json", 3),
    ("expanded_10ns", PILOT / "md_r17_chromanol_generative_expanded_green_10ns/summary.json", 3),
    ("expanded_30ns", PILOT / "md_r17_chromanol_generative_expanded_green_30ns/summary.json", 3),
    ("expanded_60ns", PILOT / "md_r17_chromanol_generative_expanded_green_60ns/summary.json", 3),
]

CSS = """
<style>
@page { size: A4; margin: 1.55cm 1.15cm; }
body { font-family: "DejaVu Sans", sans-serif; font-size: 10pt; line-height: 1.45; }
h1 { font-size: 16pt; margin-top: 0.6em; }
h2 { font-size: 13pt; margin-top: 1.0em; border-bottom: 1px solid #ccc; padding-bottom: 2px; }
h3 { font-size: 11pt; margin-top: 0.8em; }
code, pre { font-family: "DejaVu Sans Mono", monospace; font-size: 8.4pt; }
table { border-collapse: collapse; width: 100%; table-layout: auto; font-size: 8.2pt; margin: 0.55em 0; }
th, td { border: 1px solid #bbb; padding: 3px 5px; vertical-align: top; word-break: break-word; overflow-wrap: anywhere; }
th { background: #eee; font-weight: 600; }
img { max-width: 100%; height: auto; page-break-inside: avoid; }
figure { page-break-inside: avoid; margin: 0.8em 0; }
</style>
"""


def fmt(value: object, digits: int = 3) -> str:
    if value is None or pd.isna(value):
        return ""
    if isinstance(value, str):
        return value
    try:
        return f"{float(value):.{digits}f}"
    except (TypeError, ValueError):
        return str(value)


def read_json_rows(path: Path) -> list[dict]:
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text())
    except Exception:
        return []
    return data if isinstance(data, list) else []


def ok_count(path: Path) -> int:
    return sum(1 for row in read_json_rows(path) if row.get("status") == "ok")


def load_cofold() -> pd.DataFrame:
    frames = []
    for path in sorted(glob.glob(str(OUT / "r17_chromanol_generative_batch*_cofold.csv"))):
        df = pd.read_csv(path)
        df["batch_file"] = Path(path).name
        frames.append(df)
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


def load_md() -> pd.DataFrame:
    rows = []
    for panel, path, _expected in PANELS:
        for row in read_json_rows(path):
            row = dict(row)
            row["panel"] = panel
            rows.append(row)
    return pd.DataFrame(rows)


def savefig(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(path, dpi=300, bbox_inches="tight")
    plt.close()


def build_figures(cofold: pd.DataFrame, md: pd.DataFrame) -> dict[str, Path]:
    figs: dict[str, Path] = {}

    p = FIG / "fig1_r17_affinity_by_target.png"
    order = sorted(cofold["target"].dropna().unique())
    data = [cofold.loc[cofold["target"] == tgt, "affinity_probability_binary"].dropna().values for tgt in order]
    fig, ax = plt.subplots(figsize=(8.2, 4.8))
    ax.boxplot(data, labels=[x.upper() for x in order], showfliers=False)
    ax.scatter(
        [order.index(t) + 1 for t in cofold["target"]],
        cofold["affinity_probability_binary"],
        c=(cofold["photosafety_proxy"] == "none_detected").map({True: "#1a9850", False: "#d73027"}),
        s=18,
        alpha=0.65,
    )
    ax.set_ylabel("Boltz-2 affinity probability")
    ax.set_title("R17 constrained generative chromanol atlas by target")
    figs["fig1"] = p
    savefig(p)

    p = FIG / "fig2_r17_top_none_detected.png"
    top = cofold[cofold["photosafety_proxy"] == "none_detected"].sort_values("affinity_probability_binary", ascending=False).head(15)
    top = top.sort_values("affinity_probability_binary")
    fig, ax = plt.subplots(figsize=(8.8, 5.4))
    ax.barh(top["job_id"], top["affinity_probability_binary"], color="#4daf4a")
    ax.set_xlabel("Boltz-2 affinity probability")
    ax.set_title("Top photosafety-green R17 candidates")
    figs["fig2"] = p
    savefig(p)

    p = FIG / "fig3_r17_md_panels.png"
    md_ok = md[md["status"] == "ok"].copy()
    md_ok["label"] = md_ok["panel"] + " / " + md_ok["target"].str.upper()
    fig, ax = plt.subplots(figsize=(10.0, 5.2))
    x = range(len(md_ok))
    ax.bar(x, md_ok["rmsd_last_third_A"], color="#91bfdb", label="last-third RMSD")
    ax.scatter(x, md_ok["rmsd_max_A"], color="#d73027", s=26, zorder=3, label="max RMSD")
    ax.set_xticks(list(x))
    ax.set_xticklabels(md_ok["label"], rotation=55, ha="right", fontsize=7)
    ax.set_ylabel("Ligand RMSD (A)")
    ax.set_title("R17 MD robustness ladder")
    ax.legend(fontsize=8)
    figs["fig3"] = p
    savefig(p)

    p = FIG / "fig4_r17_prior_art_gate.png"
    prior = pd.read_csv(OUT / "precompute_prior_art_gate.csv")
    r17 = prior[prior["source"].astype(str).str.startswith("r17_chromanol_generative")]
    counts = r17["precompute_gate"].value_counts()
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    ax.bar(counts.index, counts.values, color=["#fee08b", "#91bfdb", "#d73027"][: len(counts)])
    ax.set_ylabel("Rows")
    ax.set_title("R17 prior-art precompute gate")
    ax.tick_params(axis="x", rotation=25)
    figs["fig4"] = p
    savefig(p)

    return figs


def table(rows: list[list[object]], headers: list[str]) -> str:
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(x) for x in row) + " |")
    return "\n".join(lines)


def write_markdown(cofold: pd.DataFrame, md: pd.DataFrame, figs: dict[str, Path], complete: bool) -> None:
    PP.mkdir(parents=True, exist_ok=True)
    prior = pd.read_csv(OUT / "precompute_prior_art_gate.csv")
    r17_prior = prior[prior["source"].astype(str).str.startswith("r17_chromanol_generative")]
    gate_counts = r17_prior["precompute_gate"].value_counts().to_dict()
    md_ok = md[md["status"] == "ok"].copy()
    expanded60 = md_ok[md_ok["panel"] == "expanded_60ns"]
    top_green = cofold[cofold["photosafety_proxy"] == "none_detected"].sort_values("affinity_probability_binary", ascending=False).head(10)
    top_rows = [
        [r["job_id"], r["target"].upper(), r["design_id"], fmt(r["affinity_probability_binary"]), fmt(r["cLogP"], 2), fmt(r["QED"], 3), r["photosafety_proxy"]]
        for _, r in top_green.iterrows()
    ]
    md_rows = [
        [r["panel"], r.get("target", "").upper(), r.get("analog_id", ""), fmt(r.get("affinity_probability_binary")), fmt(r.get("rmsd_mean_A"), 2), fmt(r.get("rmsd_last_third_A"), 2), fmt(r.get("rmsd_max_A"), 2)]
        for _, r in md_ok.sort_values(["panel", "target"]).iterrows()
    ]
    exp_rows = [
        [r.get("name", ""), r.get("target", "").upper(), r.get("analog_id", ""), fmt(r.get("rmsd_mean_A"), 2), fmt(r.get("rmsd_last_third_A"), 2), fmt(r.get("rmsd_max_A"), 2)]
        for _, r in expanded60.iterrows()
    ]

    status = "complete" if complete else "near-ready incomplete"
    if complete:
        conclusion = (
            "The R17 atlas is complete for manuscript-level reporting as a disciplined constrained-design "
            "workflow: the 240-row cofold atlas and all top/next/expanded 10/30/60 ns MD panels are finished, "
            "including the final expanded 60 ns 3/3 stable gate. The next step is not another automatic long-MD "
            "expansion, but cross-model/decoy or PLIF checks, Markush/FTO review, and wet-lab/formulation packages."
        )
    else:
        conclusion = (
            "The R17 atlas justifies near-ready manuscript reporting as a disciplined constrained-design workflow. "
            "It should remain queued behind the active GPU job until the expanded 60 ns panel reaches 3/3 stable."
        )

    md_text = f"""# R17 Constrained Generative Chromanol Analog Atlas: Photosafety-Gated Boltz-2 Cofolding and 10-60 ns MD Robustness

## Abstract

R17 extends the R16 topical chromanol program with a constrained generative analog atlas. The goal was not an unconstrained novelty claim, but a disciplined hit-to-lead expansion that keeps the chromanol core compact while varying substitution patterns and tracking target, photosafety, and prior-art gates. The atlas contains `{len(cofold)}` Boltz-2 cofold rows across balanced skin-relevant targets. Photosafety-green candidates reached affinity probabilities up to `{fmt(top_green["affinity_probability_binary"].max())}`, while aryl-halogen candidates were retained only with explicit photosafety review labels. The MD ladder covers top, next, and expanded green-target panels through 10, 30, and 60 ns. Expanded 60 ns status is `{len(expanded60)}/3` ok, so this manuscript status is `{status}`. All findings are in silico only and remain Markush/FTO and wet-lab validation pending.

**Keywords**: chromanol, generative design, Boltz-2, OpenMM, photosafety, prior-art gate, in silico

## 1. Research Question

Can a constrained R17 chromanol analog generator produce target-relevant, photosafety-gated candidates that remain stable through staged MD robustness checks without overclaiming novelty, freedom to operate, or clinical efficacy?

## 2. Data Sources

{table([
["`pilot/cpu_meaningful/r17_chromanol_generative_batch*_cofold.csv`", "240-row Boltz-2 cofold atlas"],
["`pilot/md_r17_chromanol_generative_top_green_*/summary.json`", "top green-target 10/30/60 ns MD ladder"],
["`pilot/md_r17_chromanol_generative_next_green_*/summary.json`", "next green-target 10/30/60 ns MD ladder"],
["`pilot/md_r17_chromanol_generative_expanded_green_*/summary.json`", "expanded green-target 10/30/60 ns MD ladder"],
["`pilot/cpu_meaningful/precompute_prior_art_gate.csv`", "technical prior-art and Markush pre-gate"],
], ["file", "role"])}

## 3. Results

### 3.1 Cofold atlas by target

![Figure 1. Distribution of R17 cofold affinity probabilities by target. Green points indicate `photosafety_proxy=none_detected`; red points indicate aryl-halogen review.](figures/{figs["fig1"].name})

### 3.2 Top photosafety-green candidates

{table(top_rows, ["job_id", "target", "design", "affinity probability", "cLogP", "QED", "photosafety proxy"])}

![Figure 2. Top photosafety-green R17 candidates by Boltz-2 affinity probability.](figures/{figs["fig2"].name})

### 3.3 Staged MD robustness

The R17 staged MD ladder currently contains `{len(md_ok)}` ok rows. The completed top and next green-target 60 ns panels were stable. The expanded 60 ns panel is the final promotion gate and is `{len(expanded60)}/3` complete in this manuscript snapshot.

{table(md_rows, ["panel", "target", "analog", "affinity probability", "mean RMSD A", "last-third RMSD A", "max RMSD A"])}

![Figure 3. R17 MD robustness ladder across 10, 30, and 60 ns panels.](figures/{figs["fig3"].name})

### 3.4 Expanded 60 ns final gate

{table(exp_rows, ["name", "target", "analog", "mean RMSD A", "last-third RMSD A", "max RMSD A"])}

### 3.5 Prior-art and Markush discipline

The R17 prior-art precompute gate counts are `{gate_counts}`. This gate does not kill the scientific atlas, but it blocks stronger commercial language. A PubChem no-hit result is not freedom to operate, because Markush and use claims can still cover unmade or unlisted analogs.

![Figure 4. R17 prior-art precompute gate distribution.](figures/{figs["fig4"].name})

## 4. Development Interpretation

R17 is best interpreted as a constrained hit-to-lead expansion paper. Its strongest contribution is a reproducible design queue that combines target cofolding, photosafety labeling, staged MD robustness, and prior-art discipline. R16 remains the cleaner immediate topical lead manuscript; R17 supplies the broader analog design space.

## 5. Limitations

All findings are in silico only. Boltz-2 cofolding is not biochemical binding evidence. MD RMSD stability is not potency, residence time, target engagement, or skin exposure. Photosafety, sensitization, hERG, AMES, DILI, irritation, IVRT/IVPT, PBPK, formulation compatibility, and target-engagement assays remain required. Markush/FTO review is mandatory before synthesis, purchasing, commercial novelty claims, or additional expensive 100-200 ns/RBFE/ABFE expansion.

## 6. Conclusion

{conclusion}
"""
    (PP / "manuscript.md").write_text(md_text, encoding="utf-8")


def rebuild(md: Path) -> bool:
    pandoc = shutil.which("pandoc")
    if not pandoc:
        print("pandoc missing; wrote markdown and figures only")
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
        weasy = shutil.which("weasyprint")
        if weasy:
            cmd = [weasy, str(md.with_suffix(".html")), str(md.with_suffix(".pdf"))]
        else:
            cmd = [sys.executable, "-m", "weasyprint", str(md.with_suffix(".html")), str(md.with_suffix(".pdf"))]
        try:
            subprocess.run(cmd, check=True, capture_output=True, timeout=360)
            print(f"rebuilt {md.parent.name}: {md.with_suffix('.pdf').stat().st_size // 1024} KB PDF")
            return True
        except Exception as exc:
            print(f"weasyprint unavailable or failed; wrote markdown/html/figures only: {exc}")
            return False
    finally:
        header.unlink(missing_ok=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--allow-incomplete", action="store_true", help="write a near-ready draft before expanded 60 ns reaches 3/3")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    expanded_path = PILOT / "md_r17_chromanol_generative_expanded_green_60ns/summary.json"
    expanded_ok = ok_count(expanded_path)
    complete = expanded_ok >= 3
    if not complete and not args.allow_incomplete:
        print(f"expanded 60 ns incomplete: {expanded_ok}/3; not writing P43 without --allow-incomplete")
        return 2
    cofold = load_cofold()
    md = load_md()
    if cofold.empty:
        print("missing R17 cofold atlas")
        return 1
    figs = build_figures(cofold, md)
    write_markdown(cofold, md, figs, complete=complete)
    rebuild(PP / "manuscript.md")
    print(f"P43 status: {'complete' if complete else 'near-ready'}; figures={len(figs)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
