"""License Registry 컴포넌트 키 → BibTeX 인용.

논문 References 섹션 자동화. 새 컴포넌트가 license_registry에 추가되면
여기에 BibTeX 항목을 추가해 주세요.
"""

from __future__ import annotations

from typing import Iterable


# 핵심 논문/도구 BibTeX 데이터베이스
# (license_registry.py의 component key를 BibTeX entry key로 매핑)
_BIBTEX: dict[str, str] = {
    # ==== 구조 예측 ====
    "boltz2": r"""
@article{Wohlwend2025Boltz2,
  title   = {Boltz-2: Towards Accurate and Efficient Binding Affinity Prediction},
  author  = {Wohlwend, Jeremy and Corso, Gabriele and Passaro, Saro and Reveiz, Mateo
             and Leidal, Ken and Wankowicz, Stephanie and Adornato, Stephanie and Jaakkola, Tommi
             and Barzilay, Regina},
  journal = {bioRxiv},
  year    = {2025},
  doi     = {10.1101/2025.06.14.659707},
  url     = {https://github.com/jwohlwend/boltz}
}
""",
    "protenix_v2": r"""
@article{Protenix2026,
  title   = {Protenix-v1: Toward High-Accuracy Open-Source Biomolecular Structure Prediction},
  author  = {Protenix Team, ByteDance AI Lab},
  journal = {bioRxiv},
  year    = {2026},
  doi     = {10.64898/2026.02.05.703733},
  url     = {https://github.com/bytedance/Protenix}
}
""",
    "openfold3": r"""
@misc{OpenFold3preview,
  title  = {{OpenFold3}: A fully open-source biomolecular structure prediction model},
  author = {{OpenFold Consortium}},
  year   = {2025},
  note   = {Apache-2.0 license},
  url    = {https://github.com/aqlaboratory/openfold-3}
}
""",
    "alphafold_db": r"""
@article{Varadi2024AlphaFoldDB,
  title    = {{AlphaFold Protein Structure Database}: Massively expanding the structural
              coverage of protein-sequence space with high-accuracy models},
  author   = {Varadi, Mihaly and others},
  journal  = {Nucleic Acids Research},
  year     = {2024},
  doi      = {10.1093/nar/gkad1011}
}
""",
    "neuralplex3_code": r"""
@article{Iambic2025NP3,
  title   = {NeuralPLexer3: Accurate biomolecular complex structure prediction with flow models},
  author  = {Iambic Therapeutics Team},
  journal = {OpenReview / preprint},
  year    = {2025},
  url     = {https://github.com/iambic-therapeutics/NeuralPLexer3}
}
""",

    # ==== 도킹 / 스크리닝 ====
    "diffdock_l": r"""
@inproceedings{Corso2023DiffDock,
  title     = {{DiffDock}: Diffusion Steps, Twists, and Turns for Molecular Docking},
  author    = {Corso, Gabriele and St{\"a}rk, Hannes and Jing, Bowen and Barzilay, Regina and Jaakkola, Tommi},
  booktitle = {ICLR},
  year      = {2023}
}
""",
    "drugclip": r"""
@inproceedings{Gao2023DrugCLIP,
  title     = {{DrugCLIP}: Contrastive Protein-Molecule Representation Learning for Virtual Screening},
  author    = {Gao, Bowen and others},
  booktitle = {NeurIPS},
  year      = {2023}
}
""",
    "flowdock": r"""
@article{Morehead2025FlowDock,
  title   = {{FlowDock}: Geometric Flow Matching for Generative Protein-Ligand Docking and Affinity Prediction},
  author  = {Morehead, Alex and others},
  journal = {Bioinformatics},
  year    = {2025},
  doi     = {10.1093/bioinformatics/btaf240}
}
""",
    "gnina": r"""
@article{McNutt2021Gnina,
  title   = {{GNINA 1.0}: Molecular docking with deep learning},
  author  = {McNutt, Andrew T and others},
  journal = {Journal of Cheminformatics},
  year    = {2021},
  doi     = {10.1186/s13321-021-00522-2}
}
""",
    "posebusters": r"""
@article{Buttenschoen2024PoseBusters,
  title   = {{PoseBusters}: AI-based docking methods fail to generate physically valid
             poses or generalise to novel sequences},
  author  = {Buttenschoen, Martin and Morris, Garrett M and Deane, Charlotte M},
  journal = {Chemical Science},
  year    = {2024},
  doi     = {10.1039/D3SC04185A}
}
""",
    "posebench_v2": r"""
@article{Morehead2025PoseBench,
  title   = {Assessing the potential of deep learning for protein-ligand docking},
  author  = {Morehead, Alex and others},
  journal = {Nature Machine Intelligence},
  year    = {2025},
  doi     = {10.1038/s42256-025-01160-1}
}
""",

    # ==== 생성 ====
    "flowmol3": r"""
@article{Dunn2025FlowMol3,
  title   = {{FlowMol3}: Flow Matching for 3D De Novo Small-Molecule Generation},
  author  = {Dunn, Ian and others},
  journal = {arXiv preprint},
  year    = {2025},
  doi     = {10.48550/arXiv.2508.12629}
}
""",
    "reinvent4": r"""
@article{Loeffler2024REINVENT4,
  title   = {{REINVENT 4}: Modern AI--driven generative molecule design},
  author  = {Loeffler, Hannes H and others},
  journal = {Journal of Cheminformatics},
  year    = {2024},
  doi     = {10.1186/s13321-024-00812-5}
}
""",
    "saturn": r"""
@article{Atance2025SATURN,
  title   = {Directly optimizing for synthesizability in generative molecular design using retrosynthesis models},
  author  = {Atance, Sara R and others},
  journal = {Chemical Science},
  year    = {2025},
  doi     = {10.1039/D5SC01476J}
}
""",
    "diffsbdd": r"""
@article{Schneuing2024DiffSBDD,
  title   = {Structure-based drug design with equivariant diffusion models},
  author  = {Schneuing, Arne and others},
  journal = {Nature Computational Science},
  year    = {2024}
}
""",
    "bindcraft": r"""
@article{Pacesa2025BindCraft,
  title   = {One-shot design of functional protein binders with {BindCraft}},
  author  = {Pacesa, Martin and Ovchinnikov, Sergey and Correia, Bruno and others},
  journal = {Nature},
  year    = {2025},
  doi     = {10.1038/s41586-025-09429-6}
}
""",

    # ==== ADMET ====
    "admet_ai": r"""
@article{Swanson2024ADMETAI,
  title   = {{ADMET-AI}: a machine learning ADMET platform for evaluation of large-scale chemical libraries},
  author  = {Swanson, Kyle and others},
  journal = {Bioinformatics},
  year    = {2024},
  doi     = {10.1093/bioinformatics/btae416}
}
""",
    "chemprop2": r"""
@article{Heid2024Chemprop2,
  title   = {{Chemprop 2.0}: A Modular Deep Learning Toolkit for Molecular Property Prediction},
  author  = {Heid, Esther and others},
  journal = {Journal of Chemical Information and Modeling},
  year    = {2024}
}
""",

    # ==== KG / 재창출 ====
    "txgnn": r"""
@article{Huang2024TxGNN,
  title   = {A foundation model for clinician-centered drug repurposing},
  author  = {Huang, Kexin and Chandak, Payal and others and Zitnik, Marinka},
  journal = {Nature Medicine},
  year    = {2024},
  doi     = {10.1038/s41591-024-03233-x}
}
""",
    "primekg": r"""
@article{Chandak2023PrimeKG,
  title   = {Building a knowledge graph to enable precision medicine},
  author  = {Chandak, Payal and Huang, Kexin and Zitnik, Marinka},
  journal = {Scientific Data},
  year    = {2023},
  doi     = {10.1038/s41597-023-01960-3}
}
""",
    "open_targets": r"""
@article{Ochoa2023OpenTargets,
  title   = {The next-generation Open Targets Platform},
  author  = {Ochoa, David and others},
  journal = {Nucleic Acids Research},
  year    = {2023},
  doi     = {10.1093/nar/gkac1046}
}
""",

    # ==== MD / FE ====
    "openmm": r"""
@article{Eastman2024OpenMM8,
  title   = {{OpenMM 8}: Molecular Dynamics Simulation with Machine Learning Potentials},
  author  = {Eastman, Peter and others},
  journal = {The Journal of Physical Chemistry B},
  year    = {2024},
  doi     = {10.1021/acs.jpcb.3c06662}
}
""",
    "mace_off24": r"""
@article{Kovacs2024MACEOFF,
  title   = {{MACE-OFF}: Short-Range Transferable Machine Learning Force Fields for Organic Molecules},
  author  = {Kovacs, David Peter and others},
  journal = {Journal of the American Chemical Society},
  year    = {2024},
  doi     = {10.1021/jacs.4c07099}
}
""",
    "fep_spell_abfe": r"""
@article{FEPSPellABFE2025,
  title   = {{FEP-SPell-ABFE}: An Open-Source Automated Alchemical Absolute Binding Free-Energy Calculation Workflow for Drug Discovery},
  author  = {Authors et al.},
  journal = {Journal of Chemical Information and Modeling},
  year    = {2025},
  doi     = {10.1021/acs.jcim.4c01986}
}
""",

    # ==== 천연물 DB ====
    "coconut_2": r"""
@article{Sorokina2025COCONUT2,
  title   = {{COCONUT 2.0}: a comprehensive overhaul and curation of the collection of open natural products database},
  author  = {Sorokina, Maria and others},
  journal = {Nucleic Acids Research},
  year    = {2025},
  doi     = {10.1093/nar/gkae1063}
}
""",
    "lotus": r"""
@article{Rutz2022LOTUS,
  title   = {The {LOTUS} initiative for open knowledge management in natural products research},
  author  = {Rutz, Adriano and others},
  journal = {eLife},
  year    = {2022},
  doi     = {10.7554/eLife.70780}
}
""",
    "npass_3": r"""
@article{NPASS2026,
  title   = {{NPASS} database update 2026: comprehensive quantitative composition,
             bioactivity, and ADME-Tox data of natural products for biomedical research},
  author  = {NPASS Team},
  journal = {Nucleic Acids Research},
  year    = {2026},
  doi     = {10.1093/nar/gkaf1196}
}
""",
    "chembl_35": r"""
@article{Mendez2019ChEMBL,
  title   = {{ChEMBL}: towards direct deposition of bioassay data},
  author  = {Mendez, David and others},
  journal = {Nucleic Acids Research},
  year    = {2019},
  doi     = {10.1093/nar/gky1075}
}
""",
    "pubchem": r"""
@article{Kim2023PubChem,
  title   = {{PubChem 2023} update},
  author  = {Kim, Sunghwan and others},
  journal = {Nucleic Acids Research},
  year    = {2023},
  doi     = {10.1093/nar/gkac956}
}
""",

    # ==== 기타 ====
    "rdkit": r"""
@misc{RDKit,
  title  = {{RDKit}: Open-source cheminformatics},
  author = {{Greg Landrum and contributors}},
  url    = {https://www.rdkit.org},
  year   = {2024}
}
""",
    "mmseqs2": r"""
@article{Steinegger2017MMseqs2,
  title   = {{MMseqs2} enables sensitive protein sequence searching for the analysis of massive data sets},
  author  = {Steinegger, Martin and Soeding, Johannes},
  journal = {Nature Biotechnology},
  year    = {2017},
  doi     = {10.1038/nbt.3988}
}
""",
    "colabfold_code": r"""
@article{Mirdita2022ColabFold,
  title   = {{ColabFold}: making protein folding accessible to all},
  author  = {Mirdita, Milot and others},
  journal = {Nature Methods},
  year    = {2022},
  doi     = {10.1038/s41592-022-01488-1}
}
""",
    "alphaflow": r"""
@inproceedings{Jing2024AlphaFlow,
  title     = {{AlphaFold Meets Flow Matching} for Generating Protein Ensembles},
  author    = {Jing, Bowen and Berger, Bonnie and Jaakkola, Tommi},
  booktitle = {ICML},
  year      = {2024}
}
""",
    "bioemu": r"""
@misc{Microsoft2026BioEmu,
  title  = {{BioEmu}: Boltzmann emulator for protein conformational ensembles},
  author = {{Microsoft Research}},
  year   = {2026},
  url    = {https://github.com/microsoft/bioemu}
}
""",
}


def bibtex_for_components(components: Iterable[str]) -> dict[str, str]:
    """주어진 컴포넌트 키들에 대해 사용 가능한 BibTeX 항목을 dict로 반환."""
    return {k: _BIBTEX[k].strip() for k in components if k in _BIBTEX}


def bibtex_string(components: Iterable[str]) -> str:
    """단일 BibTeX 문자열 (.bib 파일 내용)."""
    entries = bibtex_for_components(components)
    return "\n\n".join(entries.values()) + "\n"


def cite_keys(components: Iterable[str]) -> list[str]:
    """본문에 \\cite{}로 들어갈 BibTeX entry key 목록 추출."""
    out = []
    for c in components:
        if c not in _BIBTEX:
            continue
        # @article{KEY, ... 에서 KEY 추출
        block = _BIBTEX[c]
        first_brace = block.find("{")
        comma = block.find(",", first_brace)
        if first_brace > 0 and comma > first_brace:
            out.append(block[first_brace + 1: comma].strip())
    return out
