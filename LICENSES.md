# Third-Party Licenses

This repository (`crazat/genesis_medicine`) is licensed under **Apache-2.0** (see `LICENSE`). Manuscripts in `preprints/` are licensed **CC-BY 4.0** by individual paper.

It bundles or vendors third-party tools in `external/` and `external_tools/`. Each retains its own license. Do not assume the top-level Apache-2.0 covers vendored code; check the per-tool LICENSE file.

## external/

| Tool | License | LICENSE file present | Notes |
|---|---|---|---|
| REINVENT4 | Apache-2.0 | yes | Generative chemistry; mol2mol scaffold-hopping |
| chai-lab (Chai-1) | Apache-2.0 | yes | AlphaFold-3-class cofold |
| PocketXMol | Apache-2.0 | yes | Pocket-conditioned generation |
| TxGNN | MIT | yes | Repurposing graph network |
| alphaflow | Apache-2.0 | yes | Conformational ensemble cofold |
| bioemu | Apache-2.0 | yes | Equilibrium-distribution emulator |

## external_tools/

| Tool | License | LICENSE file present | Notes |
|---|---|---|---|
| openfold-3 | Apache-2.0 | yes | Open-source AlphaFold-3 reimplementation; weights `of3-p2-155k.pt` are Apache-2.0 (preview-2). Path is `openfold-3` (with hyphen). |
| aqaffinity | Apache-2.0 | **MISSING** | SandboxAQ AQAffinity binding-affinity head. Package `pyproject.toml` declares Apache-2.0 but the HuggingFace snapshot did not ship a `LICENSE` file. Upstream repo at `https://huggingface.co/SandboxAQ/AQAffinity` confirms Apache-2.0. Adding a copy of the Apache-2.0 license text here is recommended; we keep this row to surface the gap. |
| protenix_v2 | Apache-2.0 | yes | Protenix v2 alternative cofold engine |
| pocketxmol | (see external/PocketXMol) | yes | Mirror checkout |

## AlphaFold weight licensing notice

**AlphaFold 3 official weights** (DeepMind / Isomorphic Labs) are non-commercial use only. This repository does NOT bundle AlphaFold 3 weights; the active execution path uses Boltz-2 (MIT, weights free), OpenFold3 preview-2 (Apache-2.0, free), and Chai-1 (Apache-2.0, free).

## Database licensing notice

| Database | License | Use restriction |
|---|---|---|
| HERB | CC-BY-NC | Internal research only; commercial use restricted |
| TCMSP | proprietary | Read-only fetch; no redistribution |
| KTKP | KR-public | Korean Traditional Knowledge Portal, public access |
| BATMAN-TCM 2.0 | proprietary | Read-only fetch |
| Open Targets v4 | CC0 | Free for any use including commercial |
| ChEMBL | CC-BY-SA 3.0 | Share-alike; derivatives require same license |
| COCONUT 2.0 | CC0 | Free for any use including commercial |
| LOTUS | CC0 | Free for any use including commercial |
| NPASS 2026 | CC-BY 4.0 | Free with attribution |
| BindingDB | CC-BY 4.0 | Free with attribution |
| PrimeKG | MIT | Free for any use |
| BERN2 | proprietary (Korea Univ. NLP) | Read-only fetch |

## Manuscripts

All preprints in `preprints/<NN>_<slug>/manuscript.md` and the corresponding PDFs are released under **CC-BY 4.0**. Per-paper metadata (`preprints/_metadata/<NN>_<slug>_metadata.json`) records the license and submission DOI.

## Contact for license questions

HanCheongWoo - `crazat7@gmail.com` (ORCID-registered) - ORCID `0009-0004-4805-8815`.

If you find a license inconsistency, please open an issue at https://github.com/crazat/genesis_medicine/issues.
