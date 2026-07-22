# paper_C data and tool index

**Paper:** End-to-end de novo design of Zn²⁺ metallohydrolase binders: an open-source canonical pipeline anchored by LigandMPNN's metal-coordination recovery

**Author:** Han, Cheongwoo
**Date:** 2026-05-12
**Draft version:** 0.1

---

## 1. Primary data files

### 1.1 1HFC benchmark (LigandMPNN vs ProteinMPNN)

| File | Description | Size |
|---|---|---|
| `pilot/round12/ligandmpnn_1hfc_gpu/seqs/1HFC_chainA_metals.fa` | 33-sequence FASTA: native + 32 LigandMPNN designs (T=0.1, seed=42, batch=4×8) | ~5 KB |
| `pilot/round12/ligandmpnn_1hfc_gpu/backbones/` | 32 packed PDB outputs from LigandMPNN | ~6 MB total |
| `pilot/round12/seqrec_zn_comparison.json` | Quantitative recovery comparison (Table 1, Table 2) | <1 KB |
| `pilot/round12/esmc_likelihood_ligandmpnn.json` | ESM-C 600M zero-shot likelihood per design (Table 3) | ~30 KB |
| `pilot/round12/esmc_fixed_cat.json` | ESM-C scoring intermediate (concatenation of both methods) | ~25 KB |

### 1.2 MMP-1 binder design walkthrough (negative control)

| File | Description | Notes |
|---|---|---|
| `pilot/round12/ligandmpnn_mmp1/seqs/CHEMBL406_chainA.fa` | 5-sequence FASTA, **`num_ligand_res=0`** (negative control showing silent ProteinMPNN fallback) | Demonstrates HETATM-stripping gotcha |
| `pilot/round12/ligandmpnn_mmp1/backbones/` | Packed PDB outputs (CHEMBL406_chainA_1..4.pdb) | — |
| `pilot/round12/boltz_input/mmp1_chembl406.yaml` | Boltz-2x cofold manifest (for re-validation with corrected HETATM input) | YAML manifest |
| `pilot/round12/boltz_input/mmp1_chembl57058.yaml`, `mmp1_chembl94487.yaml`, `mmp1_chembl98.yaml` | Additional Boltz manifests for the ChEMBL MMP-1 inhibitor set | YAML manifests |
| `pilot/round12/boltz_out/boltz_results_mmp1_chembl406/` | Boltz-2x cofold output | predicted_models + JSON |

### 1.3 Additional benchmark targets (1B8Y, 1KBC)

| File | Status |
|---|---|
| `pilot/round12/ligandmpnn_1B8Y/seqs/` | Output directory exists but empty as of this draft (deferred to v0.2) |
| `pilot/round12/ligandmpnn_1KBC/seqs/` | Output directory exists but empty as of this draft (deferred to v0.2) |

### 1.4 FlowPacker side-chain packing

| File | Description |
|---|---|
| `pilot/round12/flowpacker_1hfc_input/1HFC_chainA.pdb` | Input PDB for FlowPacker (HETATM preserved) |
| `pilot/round12/flowpacker_1hfc.log` | Run log |

### 1.5 BioEmu (ensemble pre-check)

| File | Description |
|---|---|
| `pilot/round12/bioemu_1hfc/sequence.fasta` | BioEmu input |
| `pilot/round12/bioemu_1hfc.log` | Run log |

---

## 2. Pipeline stage tool inventory and versions

| Stage | Tool | Version / commit | License | mamba env | Smoke status |
|---|---|---|---|---|---|
| 1. Backbone generation | RFdiffusion3 | 2025 preview release | open | (per Round-12/14 install) | OK |
| 1. Backbone generation (alt) | RFdiffusion2 | Nat Methods 2025 release | open | (per Round-14 install) | OK |
| 2. Sequence design (DEFAULT) | **LigandMPNN** | `ligandmpnn_v_32_010_25.pt` | MIT | `ligandmpnn` | OK |
| 2. Sequence design (ablation baseline) | ProteinMPNN | `proteinmpnn_v_48_010.pt` | MIT | `proteinmpnn` | OK |
| 3. Side-chain packing (DEFAULT) | **FlowPacker** | btaf010 release (gitlab) | open | `flowpacker` (Python 3.10, torch 2.11.0+cu130) | OK |
| 3. Side-chain packing (alt) | AttnPacker | PNAS 2023 release | open | `flowpacker` (partial — torch_cluster wheel issue on sm_120) | smoke partial |
| 4. Cofold validation (open default) | **Boltz-2x** | 2025-2026 with `--use_potentials` | MIT | `boltz` / `boltz2x` | OK |
| 4. Cofold validation (reference) | AlphaFold3 | 2024 official release | non-commercial academic | `alphafold3` | OK |
| 4. Cofold validation (alt) | Chai-1 | 2024 open weights | research | `chai-lab` | OK |
| Oracle (orthogonal QC) | ESM-C 600M | 2024-12 Cambrian release | Cambrian Open License | `esmc` / `esm` | OK |
| 5. (Optional) Integrated design + TTC | Atomistic Binder TTC | ICLR 2026 oral (qmCpJtFZra) | pending public release | — | pending weights |

## 3. Hardware

| Resource | Specification |
|---|---|
| GPU | NVIDIA RTX 5090 (24 GB, sm_120, CUDA 13.0 and 12.8) |
| CPU | 24-core AMD |
| Storage | ~125-130 GB cumulative mamba env footprint; 965 GB+ free on D drive |

## 4. Key numerical results (for reproducibility cross-check)

- **1HFC, 32 LigandMPNN sequences:** mean global recovery 0.630, mean Zn-6 recovery 0.953, mean structural-Zn triad 0.906, mean catalytic-Zn triad 1.000.
- **1HFC, 32 ProteinMPNN sequences:** mean global recovery 0.602, mean Zn-6 recovery 0.464, mean structural-Zn triad 0.000, mean catalytic-Zn triad 0.927.
- **ESM-C 600M oracle (32 designs per method):** LigandMPNN mean LL −1.048 / perplexity 2.85; ProteinMPNN mean LL −1.107 / perplexity 3.03.

## 5. Companion paper cross-references

| Paper | Directory | Relevance |
|---|---|---|
| paper_A | `preprints/20_paper_A_zn_mmp1_cross_nnp_paradox/` | 9-NNP cross-validation ranking; provides energy-ranking infrastructure for the present pipeline |
| paper_B | `preprints/21_paper_B_boltz_cofold_use_potentials_protocol/` | `--use_potentials` Boltz-2x protocol used at stage 4 |

## 6. Korean institutional anchor (for paper #19 cross-reference)

This pipeline contributes to the paper #19 (Korean Herbal Scaffold Cross-reference) Korean institutional contribution map:

| # | Anchor | Affiliation | Paper / Tool |
|---|---|---|---|
| 1 | W.Y. Kim — BInD | KAIST | paper #19 R20 |
| 2 | Lee Gyu-ri × Baker | KAIST + UW | paper_C R20 |
| 3 | SevenNet-Omni | SNU MDIL | paper_A R23 |
| 4 | Sooyoung Cha — Atomistic Binder TTC | SNU | **paper_C stage 5** R27 |
| 5 | (GPCRact candidate) | — | R31 |
| 6 | Baek — small-molecule binder family | SNU | **paper_C compared in Discussion** Nat Commun 2026 |

## 7. Manuscript files

| File | Path |
|---|---|
| Main draft | `manuscript.md` (current directory parent) |
| This index | `_metadata/paper_c_data_index.md` |
| Figures | `figures/` (currently empty; figure generation deferred to v0.2) |

## 8. Pending work for v0.2

- 1B8Y and 1KBC benchmark runs (PDBs prepared, designs not yet generated)
- Figure 1: side-by-side Zn-coordinating recovery bar chart (LigandMPNN vs ProteinMPNN)
- Figure 2: ESM-C perplexity violin plot
- Figure 3: per-position recovery heatmap at the six Zn-coordinating positions
- Figure 4: pipeline schematic (5 stages)
- Atomistic Binder TTC (stage 5) benchmark once weights are released
- Wet-lab validation track (out of scope for v0.2; separate paper)
