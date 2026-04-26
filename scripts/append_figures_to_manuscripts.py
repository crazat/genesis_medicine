"""Append Figures section to each preprint manuscript with embedded images + captions.

Inserts before the '## References' section in each markdown manuscript.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PREPRINTS = ROOT / "preprints"

# Per-preprint figures section content
FIGURES_SECTIONS = {
    "01_embelia_ribes_review": """
## Figures

**Figure 1.** Chemical structures of Embelin (parent natural product from
*Embelia ribes* / 자단), EMB-3 (this work, AI-derived scaffold-hop product),
and Shikonin (the principal pigment of 자초 / *Lithospermum erythrorhizon* —
a structurally distinct 1,4-naphthoquinone scaffold, included to clarify
the chemistry-based distinction between *E. ribes* and 자운고).

![Figure 1: Embelin / EMB-3 / Shikonin structures](figures/fig1_embelin_structure.png)
""",
    "02_recover_workflow": """
## Figures

**Figure 1.** Three-pillar institutional integration: HAN PREDICT, Inc.
(AI healthcare technology), Genesis_Medicine Lab (in silico drug discovery),
and Recover Korean Medicine Clinic (clinical practice). Patient data flows
from Recover via HAN PREDICT (Smart Charts) to Genesis_Medicine for
molecular-level reasoning, and molecular hypotheses return to inform the
prescribing 한의사's decision.

![Figure 1: Three-pillar integration](figures/fig1_three_pillar.png)

**Figure 2.** Patient workflow across Layer A (3D facial diagnostics),
Layer B (Smart Charts AI EMR with RAG over 114+ documents),
and Layer C (Genesis_Medicine molecular prescription engine). All AI
recommendations are advisory; the licensed 한의사 retains full clinical
authority. Outcome data feeds back to Layer C for compound-library
re-prioritization.

![Figure 2: Patient workflow](figures/fig2_patient_workflow.png)
""",
    "03_emb3_scar_case_study": """
## Figures

**Figure 1.** Chemical structures of Embelin and EMB-3 along with chain-length
analogs (Rapanone C13, 5-O-methyl-Embelin) and reference compounds (Marimastat
hydroxamate; Lawsone non-benzoquinone scaffold control). The scaffold-hop
transition Embelin C11 → EMB-3 C6+methyl reduces molecular volume and
lipophilicity into the topical sweet spot while preserving the
1,4-benzoquinone-2,5-diol pharmacophore.

![Figure 1: Embelin scaffold-hop SAR structures](figures/fig1_emb3_structures.png)

**Figure 2.** SAR panel scatter plots (real ADMET-AI data, 2026-04-26):
**(A)** logP × hERG with topical sweet spot (logP 1.5–3.5) and hERG concern
threshold (>0.30) marked. EMB-3 is uniquely positioned in the safe quadrant.
**(B)** Skin Reaction × AMES — illustrates that classical Embelin analogs
share elevated skin-irritation and AMES flags despite chain-length variation.

![Figure 2: SAR scatter](figures/fig2_sar_scatter.png)

**Figure 3.** Generative scaffold-hop round progression. Round 1 produced
EMB-3 (mean affinity 0.711, used as the reference baseline); Round 2 (T=1.0,
100 samples) and Round 3 (T=0.6, 300 samples + BRICS herbal grafting) failed
to surpass EMB-3, with the best Round-3 candidate (r3_6) being a
re-rediscovery of EMB-3 itself. This is interpreted as evidence that EMB-3
sits at a local optimum of the REINVENT 4 mol2mol prior space.

![Figure 3: Round progression](figures/fig3_round_progression.png)
""",
    "04_pigmentation_screening": """
## Figures

**Figure 1.** Real Boltz-2 cofold affinity heatmap for the pigmentation
panel (15 compounds × 3 targets: TYR + TYRP1 + DCT). Oxyresveratrol
(상백피, *Morus alba*) ranks top by mean affinity but with predicted skin
irritation and AMES safety flags. Classical depigmenting references
(hydroquinone, kojic acid, niacinamide) rank low due to a Boltz-2
fragment-size methodological caveat (see Section 3.3), not due to absence
of clinical activity.

![Figure 1: Pigmentation affinity heatmap](figures/fig1_affinity_heatmap.png)

**Figure 2.** Mean affinity × ADMET hERG safety quadrant for the
pigmentation panel. Marker size = molecular weight; color = logP. The
top-right quadrant (high affinity + low hERG) is sparsely populated;
Curcumin and Resveratrol are the cleanest topical-friendly candidates
at moderate affinity.

![Figure 2: Safety × affinity](figures/fig2_safety_affinity_quadrant.png)
""",
    "05_alopecia_screening": """
## Figures

**Figure 1.** Real Boltz-2 cofold affinity heatmap for the alopecia panel
(13 compounds × 3 targets: SRD5A2 + AR + CTNNB1). Top hits Saponin Re
(인삼) and Emodin (하수오) are jointly tied at mean affinity 0.675, with
Emodin leading the AR axis (0.768) and Saponin Re leading the SRD5A2 axis
(0.746). Finasteride (reference SRD5A2 inhibitor) ranks at 0.202 — a
methodological observation reflecting Boltz-2's coverage limitation for
covalent / mechanism-based inhibitors.

![Figure 1: Alopecia affinity heatmap](figures/fig1_affinity_heatmap.png)

**Figure 2.** Affinity × hERG safety quadrant for the alopecia panel.
Note the Emodin and Physcion (하수오 anthraquinones) safety flags
(Skin > 0.92, AMES > 0.71) — these compounds engage the AR axis well
but require careful topical-formulation work to address irritation /
mutagenicity concerns. Biochanin A (콩 / 황기) emerges as the cleanest
combined-criterion candidate (annotated lower right area).

![Figure 2: Alopecia safety × affinity](figures/fig2_safety_affinity_quadrant.png)
""",
    "06_acne_microbiome": """
## Figures

**Figure 1.** Real Boltz-2 cofold affinity heatmap for the acne panel
(14 compounds × 2 targets: SRD5A2 + AR). Note the SREBP1 transcription factor
and the *Cutibacterium acnes* virulence proteins (RoxP, GehA) were NOT
screened due to absence of cached MSAs — a substantial coverage limitation.
Baicalein (황금) leads the panel.

![Figure 1: Acne affinity heatmap](figures/fig1_affinity_heatmap.png)

**Figure 2.** Affinity × hERG safety quadrant for the acne panel.
**Critical safety finding**: Berberine (황련) shows hERG probability **0.977**
— the highest in our entire 4-disease pipeline — combined with AMES 0.911.
Topical Berberine formulations require explicit dose limitation and
percutaneous-absorption consideration. Wogonin (황금) emerges as the
cleanest combined-profile candidate.

![Figure 2: Acne safety × affinity](figures/fig2_safety_affinity_quadrant.png)
""",
    "07_photoaging_egcg": """
## Figures

**Figure 1.** Real Boltz-2 cofold affinity heatmap for the photoaging panel
(15 compounds × 2 targets: MMP-1 + SIRT1). EMB-3 leads the panel (mean 0.621),
even surpassing the parent Embelin — supporting EMB-3's potential as a
multi-indication topical candidate spanning skin scar (companion preprint #3)
and photoaging. Resveratrol leads the SIRT1 axis (0.588), consistent with
established resveratrol–SIRT1 pharmacology. EGCG is moderate (mean 0.520),
not exceptional as v0.1 fabricated.

![Figure 1: Photoaging affinity heatmap](figures/fig1_affinity_heatmap.png)

**Figure 2.** Affinity × hERG safety quadrant for the photoaging panel.
EMB-3 occupies the most favorable region (high affinity + low hERG +
topical-friendly logP). Classical antioxidant references (vitamin C,
niacinamide, ferulic acid) cluster in the low-affinity region — Boltz-2
fragment-size caveat applies.

![Figure 2: Photoaging safety × affinity](figures/fig2_safety_affinity_quadrant.png)
""",
    "09_cross_disease_ipf": """
## Figures

**Figure 1.** EMB-3 multi-target predicted affinity profile from real
Round-1 Boltz-2 cofold (companion preprint #3 [3]). Bars at or above
the moderate-engagement threshold (0.55, red dashed) are highlighted;
PDGFRB at 0.640 (the only canonical anti-fibrotic target with consistent
Open Targets fibrotic-disease association — see Figure 2) is anchored
within the multi-target profile.

![Figure 1: EMB-3 target profile](figures/fig1_emb3_target_profile.png)

**Figure 2.** Real Open Targets v4 GraphQL query: 9 canonical anti-fibrotic
master-switch targets × fibrotic-spectrum diseases (associations at
score ≥ 0.4). PDGFRB shows consistent association across IPF, systemic
scleroderma, ILD, pulmonary fibrosis, dermatofibrosarcoma, and acroosteolysis-
keloid syndrome. Other canonical targets (TGFB1, MMP1, CTGF, SMAD3, MMP3/9,
LOX, COL1A1) have ≤ 1 fibrotic disease above the threshold — illustrating
the disjoint between medicinal-chemistry literature framing and Open Targets
genetic-evidence-weighted scoring.

![Figure 2: Target × disease overlap](figures/fig2_target_disease_overlap.png)
""",
    "10_chronotherapy_jaoryuju": """
## Figures

**Figure 1.** 자오류주(子午流注) 12-meridian × modern skin circadian rhythm
clock. Outer ring: 12 meridian time-windows in the classical 자오류주
framework (담 → 간 → 폐 → 대장 → 위 → 비 → 심 → 소장 → 방광 → 신 → 심포 → 삼초).
Inner radial markers: documented modern skin-rhythm peaks (keratinocyte
proliferation morning, sebum peak midday, MMP rising late afternoon, barrier
permeability evening, DNA-repair / stem-cell rest overnight). The framework-
integration mapping is hypothesis-level, not validated.

![Figure 1: Jaoryuju 24-hour clock](figures/fig1_jaoryuju_clock.png)
""",
    "11_korean_pgx_topical": """
## Figures

**Figure 1.** Korean-population PGx variant frequencies vs Caucasian (CEU)
and Han Chinese references (literature-cited, summary). Note the Korean-
specific high frequencies of CYP2D6\\*10 (~50%) and CYP3A5\\*3 (~75%
homozygote) and the substantially lower HLA-B\\*15:02 vs Han Chinese.
These are the variants that motivate the proposed 23-variant Korean topical-
herb-medicine PGx panel.

![Figure 1: PGx variant frequencies](figures/fig1_pgx_frequencies.png)
""",
    "12_open_source_perspective": """
## Figures

**Figure 1.** Genesis_Medicine 12-tier pipeline architecture overview.
Approximately 50+ modules organized into 12 functional tiers from
Tier 0 (Foundation: Boltz-2, REINVENT4, ADMET-AI, OpenMM, openmmtools,
MACE-OFF24, RDKit) through Tier 11 (Frontier: NaFM, Bayesian trial design,
patent prior-art, SkinAge clock, Chai-1, JUMP-CP, MFDS K-bio landscape).
Apache-2.0 open-source.

![Figure 1: 12-tier pipeline](figures/fig1_12tier_overview.png)
""",
}


def append_figures(preprint_dir: str, figures_text: str) -> bool:
    md_path = PREPRINTS / preprint_dir / "manuscript.md"
    if not md_path.exists():
        print(f"  ⚠️ {md_path} missing")
        return False
    text = md_path.read_text()
    if "## Figures" in text:
        # Replace existing figures section
        # Simple approach: find ## Figures and remove until next ##  or end of section
        before = text.split("## Figures")[0]
        after_parts = text.split("## Figures")[1].split("\n## ", 1)
        if len(after_parts) > 1:
            rest = "\n## " + after_parts[1]
        else:
            rest = ""
        text = before + figures_text.lstrip("\n") + rest
    else:
        # Insert before "## References" or "## Acknowledgments" or end
        for anchor in ["## References", "## Acknowledgments / Contributions",
                         "---\n\n## References", "---\n\n## Acknowledgments"]:
            if anchor in text:
                text = text.replace(anchor, figures_text + "\n" + anchor, 1)
                break
        else:
            text = text.rstrip() + "\n\n" + figures_text + "\n"
    md_path.write_text(text)
    print(f"  ✅ {md_path}")
    return True


def main():
    print("=== Appending Figures sections to manuscripts ===\n")
    for d, content in FIGURES_SECTIONS.items():
        append_figures(d, content)
    print(f"\n✅ {len(FIGURES_SECTIONS)} manuscripts updated with Figures sections")


if __name__ == "__main__":
    main()
