"""OpenFold3 어댑터.

https://github.com/aqlaboratory/openfold-3

- 공식 ``run_openfold predict`` CLI를 호출한다.
- OpenFold3는 affinity head가 아니므로 구조 consensus 용도로 사용한다.
- 코드는 Apache-2.0이며, checkpoint/data 사용 조건은 배포처 기준으로 별도 확인한다.
"""

from __future__ import annotations

import json
import os
import subprocess
import time
from pathlib import Path

from loguru import logger

from .base import (
    CovalentBondSpec,
    StructurePredictionRequest,
    StructurePredictionResult,
    StructurePredictor,
)


def _chain_letter(idx: int) -> str:
    """Return single-letter chain id. Wraps via base-26 if >25."""
    if idx < 26:
        return chr(65 + idx)
    # Two-letter ids: AA, AB, ... — OpenFold3 accepts strings ≥1 char.
    first = chr(65 + (idx // 26 - 1))
    second = chr(65 + (idx % 26))
    return f"{first}{second}"


def _bond_payload(bond: CovalentBondSpec | dict) -> dict:
    if isinstance(bond, dict):
        d = bond
    else:
        d = bond.model_dump()
    out = {
        "atom1": [d["atom1_chain"], d["atom1_residue"], d["atom1_name"]],
        "atom2": [d["atom2_chain"], d["atom2_residue"], d["atom2_name"]],
    }
    if d.get("bond_type"):
        out["bond_type"] = d["bond_type"]
    return out


def build_openfold3_query_payload(
    req: StructurePredictionRequest,
    *,
    query_id: str = "genesis_openfold3",
    include_metal_cofactors: bool = True,
    include_covalent_bonds: bool = True,
) -> dict:
    """Build the OpenFold3-format query JSON payload.

    Order of chain assignment:
        1. proteins (A, B, C, …)
        2. SMILES/CCD ligands
        3. metal ions  (CCD code: ZN, CU, FE, …) — one chain per ion
        4. cofactor CCDs (NDP, FAD, …)
        5. RNA chains
        6. DNA chains

    `chain_ids` is single-letter where possible. Cofactors are emitted
    as ``molecule_type: "ligand"`` with ``ccd_codes`` per OpenFold3 spec.
    Covalent bonds (e.g., cyclic peptide head-to-tail, quinone covalent
    docking) are added at the query level when ``include_covalent_bonds``.

    See ``inference_query_format.py`` in the OpenFold3 repo for the full
    schema; we keep our payload narrow on purpose.
    """
    chains: list[dict] = []
    idx = 0

    for seq in req.protein_sequences:
        chains.append(
            {
                "molecule_type": "protein",
                "chain_ids": [_chain_letter(idx)],
                "sequence": seq,
            }
        )
        idx += 1

    for lig in req.ligands:
        chain: dict = {
            "molecule_type": "ligand",
            "chain_ids": _chain_letter(idx),
        }
        if lig.ccd_code:
            chain["ccd_codes"] = lig.ccd_code
        else:
            chain["smiles"] = lig.smiles
        chains.append(chain)
        idx += 1

    if include_metal_cofactors:
        for ion in req.metal_ions:
            chains.append(
                {
                    "molecule_type": "ligand",
                    "chain_ids": _chain_letter(idx),
                    "ccd_codes": ion,
                    "description": f"metal cofactor {ion}",
                }
            )
            idx += 1
        for ccd in req.cofactor_ccds:
            chains.append(
                {
                    "molecule_type": "ligand",
                    "chain_ids": _chain_letter(idx),
                    "ccd_codes": ccd,
                    "description": f"cofactor {ccd}",
                }
            )
            idx += 1

    for rna in req.rna_sequences:
        chains.append(
            {
                "molecule_type": "rna",
                "chain_ids": [_chain_letter(idx)],
                "sequence": rna,
            }
        )
        idx += 1

    for dna in req.dna_sequences:
        chains.append(
            {
                "molecule_type": "dna",
                "chain_ids": [_chain_letter(idx)],
                "sequence": dna,
            }
        )
        idx += 1

    query_body: dict = {"chains": chains}
    if include_covalent_bonds and req.covalent_bonds:
        query_body["covalent_bonds"] = [
            _bond_payload(b) for b in req.covalent_bonds
        ]

    return {"queries": {query_id: query_body}}


class OpenFold3Adapter(StructurePredictor):
    engine_name = "openfold3"
    engine_version = "0.4.x-preview"

    def __init__(
        self,
        cache_dir: Path,
        num_recycles: int = 10,
        num_samples: int = 1,
        use_msa: bool = False,
        msa_dir: Path | None = None,
        device: str = "cuda:0",
        openfold3_root: Path | None = None,
        pixi_bin: Path | None = None,
        openfold_cache: Path | None = None,
        checkpoint_path: Path | None = None,
        runner_yaml: Path | None = None,
        use_templates: bool = False,
    ) -> None:
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.num_recycles = num_recycles
        self.num_samples = num_samples
        self.use_msa = use_msa
        self.msa_dir = msa_dir
        self.device = device
        self.openfold3_root = openfold3_root or Path(
            os.environ.get(
                "GENESIS_OPENFOLD3_ROOT",
                "/home/crazat/genesis_medicine/external_tools/openfold-3",
            )
        )
        self.pixi_bin = pixi_bin or Path(
            os.environ.get("PIXI_BIN", "/home/crazat/.pixi/bin/pixi")
        )
        self.openfold_cache = openfold_cache or Path(
            os.environ.get(
                "OPENFOLD_CACHE",
                "/home/crazat/genesis_medicine/.cache/openfold3",
            )
        )
        self.checkpoint_path = checkpoint_path or self.openfold_cache / "of3-p2-155k.pt"
        self.runner_yaml = (
            runner_yaml
            or self.openfold3_root / "examples/example_runner_yamls/low_mem.yml"
        )
        self.use_templates = use_templates

    def supports_ligands(self) -> bool:
        return True

    def supports_affinity(self) -> bool:
        return False  # AQAffinity는 별도 모듈

    def predict(self, req: StructurePredictionRequest) -> StructurePredictionResult:
        t0 = time.time()
        if not self.openfold3_root.exists():
            raise RuntimeError(f"OpenFold3 repo 없음: {self.openfold3_root}")
        if not self.pixi_bin.exists():
            raise RuntimeError(f"pixi 실행 파일 없음: {self.pixi_bin}")
        if not self.checkpoint_path.exists():
            raise RuntimeError(f"OpenFold3 checkpoint 없음: {self.checkpoint_path}")

        run_dir = self.cache_dir / f"openfold3_{int(t0)}_{req.seed}"
        run_dir.mkdir(parents=True, exist_ok=True)
        input_json = self._write_input(req, run_dir)
        out_dir = run_dir / "output"
        out_dir.mkdir(exist_ok=True)

        cmd = [
            str(self.pixi_bin),
            "run",
            "-e",
            "openfold3-cuda12",
            "run_openfold",
            "predict",
            "--query-json",
            str(input_json),
            "--inference-ckpt-path",
            str(self.checkpoint_path),
            f"--use-msa-server={str(bool(self.use_msa)).lower()}",
            f"--use-templates={str(bool(self.use_templates)).lower()}",
            "--num-diffusion-samples",
            str(max(1, self.num_samples)),
            "--num-model-seeds",
            "1",
            "--runner-yaml",
            str(self.runner_yaml),
            "--output-dir",
            str(out_dir),
        ]

        env = os.environ.copy()
        env.setdefault("OPENFOLD_CACHE", str(self.openfold_cache))
        env.setdefault("XDG_CACHE_HOME", str(self.cache_dir.parent / "xdg"))
        env.setdefault("CUDA_HOME", "/usr/local/cuda-12.8")
        cuda_libs = [
            f"{env['CUDA_HOME']}/targets/x86_64-linux/lib",
            f"{env['CUDA_HOME']}/lib64",
        ]
        env["LD_LIBRARY_PATH"] = ":".join(
            [*cuda_libs, env.get("LD_LIBRARY_PATH", "")]
        )
        if self.device.startswith("cuda:"):
            env.setdefault("CUDA_VISIBLE_DEVICES", self.device.split(":", 1)[1])

        logger.info("OpenFold3 실행: {}", " ".join(cmd))

        try:
            proc = subprocess.run(
                cmd,
                cwd=self.openfold3_root,
                env=env,
                check=True,
                capture_output=True,
                text=True,
            )
        except subprocess.CalledProcessError as exc:
            raise RuntimeError(
                "OpenFold3 실행 실패\n"
                f"stdout:\n{exc.stdout[-4000:]}\n"
                f"stderr:\n{exc.stderr[-4000:]}"
            ) from exc
        except FileNotFoundError as exc:
            raise RuntimeError("OpenFold3 실행 파일을 찾을 수 없음") from exc

        (run_dir / "stdout.log").write_text(proc.stdout)
        (run_dir / "stderr.log").write_text(proc.stderr)
        return self._parse_output(out_dir, t0)

    def _write_input(self, req: StructurePredictionRequest, tmp: Path) -> Path:
        """OpenFold3 query JSON 입력 (metal/cofactor/covalent_bonds 포함)."""
        payload = build_openfold3_query_payload(
            req,
            query_id="genesis_openfold3",
            include_metal_cofactors=True,
            include_covalent_bonds=True,
        )
        path = tmp / "query.json"
        path.write_text(json.dumps(payload, indent=2))
        return path

    def _parse_output(self, out_dir: Path, t0: float) -> StructurePredictionResult:
        cif_files = sorted(out_dir.rglob("*_model.cif")) or sorted(
            out_dir.rglob("*.cif")
        )
        if not cif_files:
            raise RuntimeError(f"OpenFold3 출력 cif 없음: {out_dir}")
        cif_path = cif_files[0]

        agg_files = sorted(out_dir.rglob("*confidences_aggregated.json"))
        conf_files = sorted(out_dir.rglob("*confidences.json")) or sorted(
            out_dir.rglob("*confidence*.json")
        )
        conf_json = (
            agg_files[0]
            if agg_files
            else (conf_files[0] if conf_files else out_dir / "confidence.json")
        )

        plddt_mean = 0.0
        per_res: list[float] = []
        if conf_json.exists():
            conf = json.loads(conf_json.read_text())
            plddt_mean = float(
                conf.get(
                    "avg_plddt",
                    conf.get("plddt_mean", conf.get("mean_plddt", 0.0)),
                )
            )
        if conf_files:
            conf = json.loads(conf_files[0].read_text())
            per_res = conf.get(
                "plddt",
                conf.get("plddt_per_residue", conf.get("per_residue", [])),
            )

        return StructurePredictionResult(
            cif_path=cif_path,
            plddt_mean=plddt_mean,
            plddt_per_residue=per_res,
            confidence_json=conf_json,
            engine=self.engine_name,
            engine_version=self.engine_version,
            wall_seconds=time.time() - t0,
        )
