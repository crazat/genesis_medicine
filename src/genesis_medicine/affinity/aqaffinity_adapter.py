"""AQAffinity 어댑터 — SandboxAQ structure-free affinity on OpenFold3.

https://huggingface.co/SandboxAQ/AQAffinity
https://www.sandboxaq.com/post/aqaffinity-open-source-structure-to-affinity-built-on-openfold3-by-sandboxaq

핵심 특징
---------
- OpenFold3 query JSON과 동일한 입력 (sequence + ligand SMILES/CCD).
- OpenFold3 weight (`of3-p2-155k.pt`) 그대로 재사용 + AQAffinity binding
  head ckpt 추가 로딩.
- 구조 (CIF) 출력 없음 — embedding을 dump하고 affinity head가 head-only
  forward로 pKd proxy 점수 출력.
- 라이선스: code Apache-2.0 + weight Apache-2.0 (HF, 1회 연락처 공유 동의).
- 명령:
    aqaffinity predict
        --query_json <of3 input>
        --runner_yaml <of3 runner yml>
        --inference_ckpt_path <of3 weight>
        --binding_affinity_ckpt_path <aqaffinity head ckpt>
        --use_msa_server true|false
        --output_dir <out>

본 어댑터는 ``aqaffinity`` CLI가 PATH 또는 pixi 환경 ``openfold3-cuda12``에
존재한다고 가정한다. 미존재 시 명시적 RuntimeError를 던진다.
"""
from __future__ import annotations

import json
import os
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from loguru import logger
from pydantic import BaseModel, Field

from ..structure.base import LigandSpec, StructurePredictionRequest


class AQAffinityRequest(BaseModel):
    base_request: StructurePredictionRequest
    seed: int = 42
    use_msa_server: bool = False


class AQAffinityResult(BaseModel):
    pkd: float | None = None
    pic50_proxy: float | None = None
    confidence: float | None = None
    raw_score: float | None = None
    target_label: str | None = None
    ligand_label: str | None = None
    output_json: Path | None = None
    engine: str = "aqaffinity"
    engine_version: str = "0.1.x-of3p2"
    wall_seconds: float = 0.0
    metadata: dict[str, Any] = Field(default_factory=dict)


@dataclass
class AQAffinityAdapter:
    """OpenFold3 weight 위에 동작하는 AQAffinity binding head.

    OpenFold3Adapter와 의도적으로 같은 query JSON 스키마를 사용한다 →
    metal/cofactor/covalent_bonds 확장이 그대로 전파된다.
    """

    cache_dir: Path
    openfold3_root: Path | None = None
    pixi_bin: Path | None = None
    openfold_cache: Path | None = None
    aqaffinity_root: Path | None = None
    binding_head_ckpt: Path | None = None
    inference_ckpt_path: Path | None = None
    runner_yaml: Path | None = None
    pixi_env: str = "openfold3-cuda12"
    cli_binary: str = "aqaffinity"
    device: str = "cuda:0"
    use_msa_server: bool = False
    use_templates: bool = False
    extra_args: tuple[str, ...] = field(default_factory=tuple)

    engine_name: str = "aqaffinity"
    engine_version: str = "0.1.x-of3p2"

    def __post_init__(self) -> None:
        self.cache_dir = Path(self.cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.openfold3_root = Path(
            self.openfold3_root
            or os.environ.get(
                "GENESIS_OPENFOLD3_ROOT",
                "/home/crazat/genesis_medicine/external_tools/openfold-3",
            )
        )
        self.pixi_bin = Path(
            self.pixi_bin or os.environ.get("PIXI_BIN", "/home/crazat/.pixi/bin/pixi")
        )
        self.openfold_cache = Path(
            self.openfold_cache
            or os.environ.get(
                "OPENFOLD_CACHE", "/home/crazat/genesis_medicine/.cache/openfold3"
            )
        )
        self.aqaffinity_root = Path(
            self.aqaffinity_root
            or os.environ.get(
                "GENESIS_AQAFFINITY_ROOT",
                "/home/crazat/genesis_medicine/external_tools/aqaffinity",
            )
        )
        self.binding_head_ckpt = Path(
            self.binding_head_ckpt
            or os.environ.get(
                "AQAFFINITY_BINDING_CKPT",
                str(self.openfold_cache / "aqaffinity_binding_head.pt"),
            )
        )
        self.inference_ckpt_path = Path(
            self.inference_ckpt_path
            or os.environ.get(
                "OPENFOLD3_INFERENCE_CKPT",
                str(self.openfold_cache / "of3-p2-155k.pt"),
            )
        )
        self.runner_yaml = Path(
            self.runner_yaml
            or os.environ.get(
                "AQAFFINITY_RUNNER_YAML",
                str(
                    self.aqaffinity_root
                    / "examples/inference/L1000/runner.yaml"
                ),
            )
        )

    # ------------------------------------------------------------------
    # Capability flags (Protocol-style)
    # ------------------------------------------------------------------
    def supports_ligands(self) -> bool:
        return True

    def supports_affinity(self) -> bool:
        return True

    def supports_metal_cofactor(self) -> bool:
        # AQAffinity reuses OpenFold3 query schema → ligand-form metal/CCD OK.
        return True

    def is_available(self) -> bool:
        return (
            self.openfold3_root.exists()
            and self.inference_ckpt_path.exists()
            and self.binding_head_ckpt.exists()
        )

    # ------------------------------------------------------------------
    # Main entry — predict affinity for a single (target, ligand) pair
    # ------------------------------------------------------------------
    def predict(self, req: AQAffinityRequest) -> AQAffinityResult:
        t0 = time.time()
        if not self.openfold3_root.exists():
            raise RuntimeError(f"OpenFold3 repo 없음: {self.openfold3_root}")
        if not self.inference_ckpt_path.exists():
            raise RuntimeError(
                f"OpenFold3 ckpt 없음: {self.inference_ckpt_path}. "
                "scripts/run_openfold3_smoke.sh 또는 setup_openfold 먼저 실행."
            )
        if not self.binding_head_ckpt.exists():
            raise RuntimeError(
                f"AQAffinity binding head ckpt 없음: {self.binding_head_ckpt}. "
                "https://huggingface.co/SandboxAQ/AQAffinity 에서 다운로드."
            )

        run_dir = self.cache_dir / f"aqaffinity_{int(t0)}_{req.seed}"
        run_dir.mkdir(parents=True, exist_ok=True)
        input_json = self._write_input(req.base_request, run_dir)
        out_dir = run_dir / "output"
        out_dir.mkdir(exist_ok=True)

        cmd = self._build_cmd(input_json, out_dir, req)
        env = self._build_env()
        logger.info("AQAffinity 실행: {}", " ".join(cmd))

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
                "AQAffinity 실행 실패\n"
                f"stdout:\n{(exc.stdout or '')[-4000:]}\n"
                f"stderr:\n{(exc.stderr or '')[-4000:]}"
            ) from exc
        except FileNotFoundError as exc:
            raise RuntimeError(
                f"AQAffinity CLI 실행 파일을 찾을 수 없음 ({self.cli_binary}). "
                "external_tools/aqaffinity 또는 pixi env에 설치 필요."
            ) from exc

        (run_dir / "stdout.log").write_text(proc.stdout)
        (run_dir / "stderr.log").write_text(proc.stderr)
        return self._parse_output(out_dir, t0)

    # ------------------------------------------------------------------
    # Helpers — query JSON identical to OpenFold3Adapter._write_input
    # but local copy lets us evolve independently when AQAffinity diverges.
    # ------------------------------------------------------------------
    def _write_input(self, req: StructurePredictionRequest, tmp: Path) -> Path:
        from ..structure.openfold3_adapter import build_openfold3_query_payload

        payload = build_openfold3_query_payload(
            req,
            query_id="genesis_aqaffinity",
            include_metal_cofactors=True,
            include_covalent_bonds=True,
        )
        path = tmp / "query.json"
        path.write_text(json.dumps(payload, indent=2))
        return path

    def _build_cmd(
        self, input_json: Path, out_dir: Path, req: AQAffinityRequest
    ) -> list[str]:
        cmd = [
            str(self.pixi_bin),
            "run",
            "-e",
            self.pixi_env,
            self.cli_binary,
            "predict",
            "--query_json",
            str(input_json),
            "--runner_yaml",
            str(self.runner_yaml),
            "--inference_ckpt_path",
            str(self.inference_ckpt_path),
            "--binding_affinity_ckpt_path",
            str(self.binding_head_ckpt),
            f"--use_msa_server={'true' if req.use_msa_server else 'false'}",
            "--output_dir",
            str(out_dir),
        ]
        cmd.extend(self.extra_args)
        return cmd

    def _build_env(self) -> dict[str, str]:
        env = os.environ.copy()
        env.setdefault("OPENFOLD_CACHE", str(self.openfold_cache))
        env.setdefault(
            "XDG_CACHE_HOME", str(self.cache_dir.parent / "xdg")
        )
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
        return env

    def _parse_output(self, out_dir: Path, t0: float) -> AQAffinityResult:
        candidates = (
            sorted(out_dir.rglob("affinity*.json"))
            + sorted(out_dir.rglob("predictions*.json"))
            + sorted(out_dir.rglob("*affinity*.json"))
        )
        if not candidates:
            raise RuntimeError(f"AQAffinity 출력 JSON 없음: {out_dir}")
        path = candidates[0]
        try:
            doc = json.loads(path.read_text())
        except Exception as exc:
            raise RuntimeError(f"AQAffinity JSON 파싱 실패 {path}: {exc}") from exc

        first = doc
        if isinstance(doc, list) and doc:
            first = doc[0]
        elif isinstance(doc, dict):
            for key in ("predictions", "results", "queries"):
                inner = doc.get(key)
                if isinstance(inner, list) and inner:
                    first = inner[0]
                    break
                if isinstance(inner, dict) and inner:
                    first = next(iter(inner.values()))
                    break

        def grab(*keys: str) -> Any:
            for k in keys:
                if isinstance(first, dict) and k in first and first[k] is not None:
                    return first[k]
            return None

        pkd = grab("pkd", "pKd", "predicted_pkd", "binding_affinity_pkd")
        raw_score = grab("score", "affinity_score", "raw_score")
        confidence = grab("confidence", "binding_confidence", "binding_prob")
        target_label = grab("target", "target_id", "protein_id")
        ligand_label = grab("ligand", "ligand_id", "compound_id")
        pic50_proxy = grab("pic50", "pIC50", "predicted_pic50")
        if pic50_proxy is None and isinstance(pkd, (int, float)):
            pic50_proxy = float(pkd)  # AQAffinity reports pKd; pIC50 ≈ pKd as proxy.

        def _f(v: Any) -> float | None:
            try:
                return float(v) if v is not None else None
            except Exception:
                return None

        return AQAffinityResult(
            pkd=_f(pkd),
            pic50_proxy=_f(pic50_proxy),
            confidence=_f(confidence),
            raw_score=_f(raw_score),
            target_label=str(target_label) if target_label is not None else None,
            ligand_label=str(ligand_label) if ligand_label is not None else None,
            output_json=path,
            engine=self.engine_name,
            engine_version=self.engine_version,
            wall_seconds=time.time() - t0,
            metadata={"output_dir": str(out_dir)},
        )
