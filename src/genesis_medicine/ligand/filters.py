"""리간드 라이브러리 필터.

- Lipinski Rule of Five
- PAINS (RDKit Brenk + NIH)
- NP-likeness (Ertl 2008, RDKit Contrib 구현)
- QED
"""

from __future__ import annotations

from functools import lru_cache
from typing import Iterable

from loguru import logger
from rdkit import Chem, RDLogger
from rdkit.Chem import AllChem, Descriptors, QED
from rdkit.Chem.FilterCatalog import FilterCatalog, FilterCatalogParams

RDLogger.DisableLog("rdApp.*")


@lru_cache(maxsize=1)
def _pains_catalog() -> FilterCatalog:
    params = FilterCatalogParams()
    params.AddCatalog(FilterCatalogParams.FilterCatalogs.PAINS)
    params.AddCatalog(FilterCatalogParams.FilterCatalogs.BRENK)
    params.AddCatalog(FilterCatalogParams.FilterCatalogs.NIH)
    return FilterCatalog(params)


def passes_lipinski(mol: Chem.Mol, strict: bool = False) -> bool:
    mw = Descriptors.MolWt(mol)
    logp = Descriptors.MolLogP(mol)
    hba = Descriptors.NumHAcceptors(mol)
    hbd = Descriptors.NumHDonors(mol)
    violations = sum([mw > 500, logp > 5, hba > 10, hbd > 5])
    return violations == 0 if strict else violations <= 1


def passes_pains(mol: Chem.Mol) -> bool:
    return not _pains_catalog().HasMatch(mol)


def qed(mol: Chem.Mol) -> float:
    return float(QED.qed(mol))


def canonical_smiles(smiles: str) -> str | None:
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    return Chem.MolToSmiles(mol, canonical=True)


def inchikey(smiles: str) -> str | None:
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    return Chem.MolToInchiKey(mol)


def filter_library(
    smiles_iter: Iterable[str],
    *,
    mw_range: tuple[float, float] = (150, 700),
    logp_range: tuple[float, float] = (-2.0, 6.0),
    lipinski_strict: bool = False,
    require_pains_clean: bool = True,
) -> list[dict]:
    """SMILES 스트림을 받아 필터링하고 속성 dict 목록 반환."""
    kept = []
    dropped = {"parse": 0, "mw": 0, "logp": 0, "lipinski": 0, "pains": 0}
    for smi in smiles_iter:
        mol = Chem.MolFromSmiles(smi)
        if mol is None:
            dropped["parse"] += 1
            continue
        mw = Descriptors.MolWt(mol)
        if not (mw_range[0] <= mw <= mw_range[1]):
            dropped["mw"] += 1
            continue
        logp = Descriptors.MolLogP(mol)
        if not (logp_range[0] <= logp <= logp_range[1]):
            dropped["logp"] += 1
            continue
        if not passes_lipinski(mol, strict=lipinski_strict):
            dropped["lipinski"] += 1
            continue
        if require_pains_clean and not passes_pains(mol):
            dropped["pains"] += 1
            continue
        kept.append(
            {
                "smiles": Chem.MolToSmiles(mol, canonical=True),
                "inchikey": Chem.MolToInchiKey(mol),
                "mw": mw,
                "logp": logp,
                "qed": qed(mol),
                "hba": Descriptors.NumHAcceptors(mol),
                "hbd": Descriptors.NumHDonors(mol),
                "tpsa": Descriptors.TPSA(mol),
                "rotb": Descriptors.NumRotatableBonds(mol),
            }
        )
    logger.info(f"라이브러리 필터 결과: kept={len(kept)} dropped={dropped}")
    return kept
