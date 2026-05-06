"""OpenFold3 어댑터 단위 테스트."""

from __future__ import annotations

import json
from pathlib import Path

from genesis_medicine.structure import OpenFold3Adapter
from genesis_medicine.structure.base import LigandSpec, StructurePredictionRequest


def test_openfold3_supports_ligands() -> None:
    adapter = OpenFold3Adapter(cache_dir=Path("/tmp/test_of3"))
    assert adapter.supports_ligands() is True
    assert adapter.supports_affinity() is False
    assert adapter.engine_name == "openfold3"


def test_openfold3_writes_official_query_json(tmp_path) -> None:
    adapter = OpenFold3Adapter(cache_dir=tmp_path)
    req = StructurePredictionRequest(
        protein_sequences=["MKT"],
        ligands=[LigandSpec(smiles="CCO", name="ethanol")],
        use_msa=False,
    )

    query_path = adapter._write_input(req, tmp_path)
    payload = json.loads(query_path.read_text())

    chains = payload["queries"]["genesis_openfold3"]["chains"]
    assert chains[0] == {
        "molecule_type": "protein",
        "chain_ids": ["A"],
        "sequence": "MKT",
    }
    assert chains[1] == {
        "molecule_type": "ligand",
        "chain_ids": "B",
        "smiles": "CCO",
    }


def test_openfold3_parses_smoke_output_shape(tmp_path) -> None:
    out = tmp_path / "output" / "query" / "seed_1"
    out.mkdir(parents=True)
    cif = out / "query_seed_1_sample_1_model.cif"
    cif.write_text("data_fake\n")
    agg = out / "query_seed_1_sample_1_confidences_aggregated.json"
    agg.write_text(json.dumps({"avg_plddt": 78.3, "ptm": 0.66}))
    full = out / "query_seed_1_sample_1_confidences.json"
    full.write_text(json.dumps({"plddt": [70.0, 80.0]}))

    adapter = OpenFold3Adapter(cache_dir=tmp_path)
    result = adapter._parse_output(tmp_path / "output", t0=0.0)

    assert result.cif_path == cif
    assert result.plddt_mean == 78.3
    assert result.plddt_per_residue == [70.0, 80.0]
    assert result.confidence_json == agg
