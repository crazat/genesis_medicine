#!/usr/bin/env python3
"""Pre-compute MSA + holo template hits for the 13 skin targets so that
OpenFold3 / AQAffinity inference does not need an online ColabFold server
and can use template-aware predictions for metal-dependent targets.

The script is intentionally orchestration-only: it does NOT invoke
``run_openfold predict`` or any GPU job. It writes per-target query JSON
stubs and a manifest that the smoke / cofold scripts will consume.

Outputs:
  pilot/of3_msa_cache/<TARGET>/query_holo.json   — sequence + cofactors + template
  pilot/of3_msa_cache/<TARGET>/template_hits.json
  pilot/of3_msa_cache/manifest.json

The MSA generation step is left to the user to run on D Ubuntu-Genesis once
the queue is unblocked, via:

    pixi run -e openfold3-cuda12 generate_msas \
        --query-json pilot/of3_msa_cache/<TARGET>/query_holo.json \
        --output-dir pilot/of3_msa_cache/<TARGET>/msa

(see external_tools/openfold-3/docs/source/precomputed_msa_how_to.md).
This script just makes sure the inputs are ready and the manifest tracks
which MSAs have been generated.

Drain-mode aware: refuses to launch any subprocess when
pilot/QUEUE_DRAIN_MODE exists. Manifest writing is always allowed.
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from genesis_medicine.structure import (  # noqa: E402
    LigandSpec,
    StructurePredictionRequest,
    augment_request_with_cofactors,
    build_openfold3_query_payload,
    load_registry,
)

# 13 skin targets: (key, UniProt, full canonical SKIN-relevant sequence
# excerpt). For brevity we use AlphaFold DB sequences via UniProt; the
# full-length sequence is fetched at run-time when the user provides
# a UNIPROT_FA cache, otherwise we ship the catalytic-domain stub used in
# the smoke scripts.

TARGETS = {
    "TGFB1": ("P01137", "TGF-β1"),
    "MMP1": ("P03956", "MMP-1 collagenase"),
    "MMP3": ("P08254", "MMP-3 stromelysin"),
    "MMP9": ("P14780", "MMP-9 gelatinase B"),
    "CTGF": ("P29279", "CTGF / CCN2"),
    "LOX": ("P28300", "Lysyl oxidase"),
    "TYR": ("P14679", "Tyrosinase"),
    "TYRP1": ("P17643", "TRP-1"),
    "DCT": ("P40126", "TRP-2 (DCT)"),
    "SRD5A1": ("P18405", "5α-reductase type 1"),
    "SRD5A2": ("P31213", "5α-reductase type 2"),
    "SIRT1": ("Q96EB6", "SIRT1"),
    "AR": ("P10275", "Androgen receptor"),
    "PTGS2": ("P35354", "COX-2"),
    "PIEZO1": ("Q92508", "PIEZO1"),
    "MYLK": ("Q15746", "MLCK"),
}

# Stub catalytic-domain sequences (used when UniProt FASTA cache absent).
STUB_SEQS = {
    "MMP1": (
        "FVLTEGNPRWEQTHLTYRIENYTPDLPRADVDHAIEKAFQLWSNVTPLTFTKVSEGQADIM"
        "ISFVRGDHRDNSPFDGPGGNLAHAFQPGPGIGGDAHFDEDERWTNNFREYNLHRVAAHEL"
        "GHSLGLSHSTDIGALMYPSYTFSGDVQLAQDDIDGIQAIYG"
    ),
}


def _read_uniprot_fasta(uniprot: str) -> str | None:
    cache = Path(os.environ.get("GENESIS_UNIPROT_FASTA_DIR", ROOT / ".cache/uniprot"))
    f = cache / f"{uniprot}.fasta"
    if not f.exists():
        return None
    lines = f.read_text().splitlines()
    seq = "".join(line for line in lines if not line.startswith(">"))
    return seq.replace(" ", "").strip() or None


def _sequence_for(target: str, uniprot: str) -> str | None:
    return _read_uniprot_fasta(uniprot) or STUB_SEQS.get(target)


def main() -> int:
    out_root = ROOT / "pilot/of3_msa_cache"
    out_root.mkdir(parents=True, exist_ok=True)
    registry = load_registry()
    drain = (ROOT / "pilot/QUEUE_DRAIN_MODE").exists()

    manifest_rows: list[dict] = []
    for target, (uniprot, display) in TARGETS.items():
        target_dir = out_root / target
        target_dir.mkdir(parents=True, exist_ok=True)

        seq = _sequence_for(target, uniprot)
        if seq is None:
            manifest_rows.append({
                "target": target,
                "uniprot": uniprot,
                "display": display,
                "status": "needs_uniprot_fasta",
                "note": (
                    f"Cache .cache/uniprot/{uniprot}.fasta missing and no stub. "
                    f"Run: curl -s https://www.uniprot.org/uniprotkb/{uniprot}.fasta "
                    f"-o .cache/uniprot/{uniprot}.fasta"
                ),
            })
            continue

        req = StructurePredictionRequest(protein_sequences=[seq])
        augment_request_with_cofactors(req, target)
        payload = build_openfold3_query_payload(
            req, query_id=f"genesis_{target.lower()}_holo"
        )
        (target_dir / "query_holo.json").write_text(
            json.dumps(payload, indent=2)
        )

        spec = registry.get(target)
        (target_dir / "template_hits.json").write_text(
            json.dumps(
                {
                    "target": target,
                    "uniprot": uniprot,
                    "holo_pdb_examples": list(spec.holo_pdb_examples),
                    "metal_ions": list(spec.metal_ions),
                    "cofactor_ccds": list(spec.cofactor_ccds),
                    "note": spec.note,
                    "msa_status": "pending",
                    "drain_mode": drain,
                },
                indent=2,
                ensure_ascii=False,
            )
        )

        manifest_rows.append({
            "target": target,
            "uniprot": uniprot,
            "display": display,
            "sequence_length": len(seq),
            "metal_ions": list(spec.metal_ions),
            "cofactor_ccds": list(spec.cofactor_ccds),
            "holo_pdb_examples": list(spec.holo_pdb_examples),
            "query_holo": str((target_dir / "query_holo.json").relative_to(ROOT)),
            "template_hits": str((target_dir / "template_hits.json").relative_to(ROOT)),
            "msa_status": "pending",
            "drain_mode": drain,
        })

    manifest_path = out_root / "manifest.json"
    manifest_path.write_text(json.dumps(
        {
            "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "drain_mode": drain,
            "rows": manifest_rows,
            "next_steps": [
                "Populate .cache/uniprot/<UNIPROT>.fasta for any rows whose "
                "status is needs_uniprot_fasta.",
                "On Ubuntu-Genesis (drain mode lifted): "
                "for t in pilot/of3_msa_cache/*/query_holo.json; do "
                "  pixi run -e openfold3-cuda12 generate_msas --query-json $t "
                "  --output-dir $(dirname $t)/msa; "
                "done",
                "Then flip conf/structure/openfold3.yaml::use_msa to true and "
                "set use_templates to true once template hit alignments are present.",
            ],
        },
        indent=2,
        ensure_ascii=False,
    ))

    print(json.dumps({
        "rows": len(manifest_rows),
        "manifest": str(manifest_path.relative_to(ROOT)),
        "drain_mode": drain,
        "needs_fasta": sum(1 for r in manifest_rows if r.get("status") == "needs_uniprot_fasta"),
    }, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
