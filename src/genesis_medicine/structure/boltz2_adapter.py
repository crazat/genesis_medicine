"""Boltz-2 어댑터 (MIT, 2025-06).

https://github.com/jwohlwend/boltz

- AF3-급 공동접힘 + FEP 수준의 친화도 예측을 1000× 속도로 수행.
- 웨이트 포함 완전 오픈 · 상용 허용.
- `pip install boltz` 후 subprocess로 호출 (Python API는 버전마다 변동 심함).
"""

from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path
from tempfile import TemporaryDirectory

import yaml
from loguru import logger

from .base import (
    StructurePredictionRequest,
    StructurePredictionResult,
    StructurePredictor,
)


class Boltz2Adapter(StructurePredictor):
    engine_name = "boltz2"
    engine_version = "2.0"

    def __init__(
        self,
        cache_dir: Path,
        msa_server: str = "colabfold",
        num_recycles: int = 10,
        num_samples: int = 5,
        num_diffn_samples: int = 25,
        predict_affinity: bool = True,
        device: str = "cuda:0",
    ) -> None:
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.msa_server = msa_server
        self.num_recycles = num_recycles
        self.num_samples = num_samples
        self.num_diffn_samples = num_diffn_samples
        self.predict_affinity = predict_affinity
        self.device = device

    def supports_ligands(self) -> bool:
        return True

    def supports_affinity(self) -> bool:
        return True

    def predict(self, req: StructurePredictionRequest) -> StructurePredictionResult:
        t0 = time.time()
        with TemporaryDirectory(prefix="boltz2_", dir=self.cache_dir) as tmp:
            tmp_dir = Path(tmp)
            input_yaml = self._write_input(req, tmp_dir)
            out_dir = tmp_dir / "out"
            out_dir.mkdir()

            cmd = [
                "boltz", "predict", str(input_yaml),
                "--out_dir", str(out_dir),
                "--recycling_steps", str(req.num_recycles),
                "--sampling_steps", str(self.num_diffn_samples),
                "--diffusion_samples", str(self.num_samples),
                "--seed", str(req.seed),
                "--devices", "1",
            ]
            if self.predict_affinity and req.ligands:
                cmd.append("--predict_affinity")
            if req.use_msa and self.msa_server == "colabfold":
                cmd += ["--use_msa_server"]

            logger.info("Boltz-2 실행: {}", " ".join(cmd))
            subprocess.run(cmd, check=True)

            return self._parse_output(out_dir, t0)

    def _write_input(self, req: StructurePredictionRequest, tmp: Path) -> Path:
        sequences = []
        for i, seq in enumerate(req.protein_sequences):
            sequences.append({
                "protein": {"id": f"P{i}", "sequence": seq, "msa": "auto" if req.use_msa else "empty"}
            })
        for i, lig in enumerate(req.ligands):
            entry = {"ligand": {"id": f"L{i}"}}
            if lig.ccd_code:
                entry["ligand"]["ccd"] = lig.ccd_code
            else:
                entry["ligand"]["smiles"] = lig.smiles
            sequences.append(entry)
        for i, rna in enumerate(req.rna_sequences):
            sequences.append({"rna": {"id": f"R{i}", "sequence": rna}})
        for i, dna in enumerate(req.dna_sequences):
            sequences.append({"dna": {"id": f"D{i}", "sequence": dna}})

        payload = {"version": 1, "sequences": sequences}
        yaml_path = tmp / "input.yaml"
        yaml_path.write_text(yaml.safe_dump(payload, sort_keys=False))
        return yaml_path

    def _parse_output(self, out_dir: Path, t0: float) -> StructurePredictionResult:
        cif_files = sorted(out_dir.rglob("*_model_0.cif"))
        if not cif_files:
            raise RuntimeError(f"Boltz-2 출력 cif 없음: {out_dir}")
        cif_path = cif_files[0]

        conf_json = next(out_dir.rglob("confidence*.json"))
        conf = json.loads(conf_json.read_text())
        plddt = conf.get("plddt", {})
        plddt_mean = float(plddt.get("mean", 0.0)) if isinstance(plddt, dict) else float(plddt)
        per_res = plddt.get("per_residue", []) if isinstance(plddt, dict) else []

        affinity_pkd = None
        affinity_conf = None
        aff_files = list(out_dir.rglob("affinity*.json"))
        if aff_files:
            aff = json.loads(aff_files[0].read_text())
            affinity_pkd = float(aff.get("affinity_pred_value", 0.0)) if aff else None
            affinity_conf = float(aff.get("affinity_probability_binary", 0.0)) if aff else None

        return StructurePredictionResult(
            cif_path=cif_path,
            plddt_mean=plddt_mean,
            plddt_per_residue=per_res,
            confidence_json=conf_json,
            affinity_pkd=affinity_pkd,
            affinity_confidence=affinity_conf,
            engine=self.engine_name,
            engine_version=self.engine_version,
            wall_seconds=time.time() - t0,
        )
