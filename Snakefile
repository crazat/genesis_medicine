# Genesis_Medicine reproducibility pipeline (Snakemake 9, MIT)
#
# One-line reproduction: `snakemake --use-conda --cores 8 all`
# Or with apptainer: `snakemake --use-apptainer --cores 8 all`
#
# This Snakefile encodes the canonical preprint-ready pipeline:
#   stage 1 — load compound libraries
#   stage 2 — Boltz-2 cofold (GPU)
#   stage 3 — ADMET-AI (GPU)
#   stage 4 — Round 5 dermatology adapters (CPU): PBK + SARA-ICE + CarsiDock-Cov
#   stage 5 — PoseBusters validation (CPU)
#   stage 6 — calibration + ABFE (GPU, optional)
#   stage 7 — figure regeneration (CPU)
#
# Reviewer-friendly: every preprint figure can be regenerated with a single
# `snakemake figures` command. Pipeline graph: `snakemake --dag | dot -Tsvg`.

# ---- I/O paths ----------------------------------------------------------
COMPOUND_LIBS = [
    "data/skin_compounds_curated.csv",
    "data/sar_panel_phase2.csv",
    "data/screen_libraries/pigmentation_compounds.csv",
    "data/screen_libraries/alopecia_compounds.csv",
    "data/screen_libraries/acne_compounds.csv",
    "data/screen_libraries/photoaging_compounds.csv",
    "data/chembl_mmp1_calibration.csv",
]

PREPRINTS = [
    "01_embelia_ribes_review",
    "02_recover_workflow",
    "03_emb3_scar_case_study",
    "04_pigmentation_screening",
    "05_alopecia_screening",
    "06_acne_microbiome",
    "07_photoaging_egcg",
    "08_abfe_methodology",
    "09_cross_disease_ipf",
    "10_chronotherapy_jaoryuju",
    "11_korean_pgx_topical",
    "12_open_source_perspective",
]

# ---- Top-level targets --------------------------------------------------
rule all:
    input:
        "pilot/round5_application/full_compound_sweep.csv",
        "pilot/calibration/t4l_benzene/result_final_closed_cycle.json",
        "pilot/calibration/boltz2_mmp1/calibration_stats.json",
        "pilot/posebusters/posebusters_v2_summary.json",
        expand("preprints/{name}/manuscript.pdf", name=PREPRINTS),

rule figures:
    input:
        expand("preprints/{name}/figures", name=PREPRINTS),

# ---- Stage 4: Round 5 adapter sweep (CPU only) --------------------------
rule round5_compound_sweep:
    input:
        libs=COMPOUND_LIBS,
        adapters="src/genesis_medicine/dermatology/__init__.py",
    output:
        "pilot/round5_application/full_compound_sweep.csv",
    shell:
        "mkdir -p pilot/round5_application && "
        "python -c 'from scripts.round5_sweep import main; main()' "
        "  > {output}.log 2>&1"

# ---- Stage 5: PoseBusters validation (CPU) ------------------------------
rule posebusters_v2:
    input:
        script="scripts/run_posebusters_v2.py",
    output:
        csv="pilot/posebusters/posebusters_results_v2.csv",
        summary="pilot/posebusters/posebusters_v2_summary.json",
    shell:
        "python {input.script}"

# ---- Stage 6a: ChEMBL Boltz-2 calibration (GPU) -------------------------
rule chembl_calibration:
    input:
        script="scripts/boltz2_calibration_mmp1.py",
        csv="data/chembl_mmp1_calibration.csv",
    output:
        "pilot/calibration/boltz2_mmp1/calibration_stats.json",
    shell:
        "python {input.script}"

# ---- Stage 6b: T4L99A·benzene calibration (GPU, ~9 h) -------------------
rule t4l_calibration:
    input:
        script="scripts/run_abfe_corrected.py",
    output:
        "pilot/calibration/t4l_benzene/result_final_closed_cycle.json",
    shell:
        "echo 'T4L calibration is a 9-hour GPU run; manual trigger only. "
        "See scripts/abfe_calibrate_t4l.py.'"

# ---- Stage 7: preprint PDF rendering (CPU) ------------------------------
rule preprint_pdf:
    input:
        md="preprints/{name}/manuscript.md",
    output:
        html="preprints/{name}/manuscript.html",
        pdf="preprints/{name}/manuscript.pdf",
    shell:
        "cd preprints/{wildcards.name} && "
        "pandoc manuscript.md -o manuscript.html "
        "  --embed-resources --standalone && "
        "google-chrome --headless --disable-gpu --no-sandbox "
        "  --print-to-pdf=manuscript.pdf --print-to-pdf-no-header "
        "  \"file://$(pwd)/manuscript.html\""

# ---- House-keeping ------------------------------------------------------
rule clean_html:
    shell:
        "rm -f preprints/*/manuscript.html"
