"""BindCraft — 단백질 바인더 one-shot 설계 (Nature 2025, MIT).

https://github.com/martinpacesa/BindCraft

성능
----
- AlphaFold2 가중치 사용
- 10-100% 실험 성공률 (HTS 없이 nM 친화도)
- 세포 표면 수용체 / 알러젠 / de novo 단백질 / 다도메인 nuclease 성공

용도 (Stage 5.5 — B1)
---------------------
저분자 외 신규 모달리티. BACE1 negative regulator 설계, multi-target AD에서
amyloid sequestration 단백질 등.

라이선스
--------
MIT — commercial-safe.

⚠️ Note: AlphaFold2 가중치는 CC-BY-NC-SA 4.0이 아닌 Apache-2.0 → 상업 OK이지만
   사용 시 DeepMind 약관 검토 권장.
"""

from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path
from tempfile import TemporaryDirectory

from loguru import logger
from pydantic import BaseModel, Field


class BinderRequest(BaseModel):
    target_pdb: Path = Field(description="결합 대상 단백질")
    target_hotspot_residues: list[int] = Field(
        default_factory=list, description="결합부 핫스팟 잔기 인덱스"
    )
    binder_length_min: int = 60
    binder_length_max: int = 120
    n_designs: int = 50
    seed: int = 42


class BinderHit(BaseModel):
    sequence: str
    pdb_path: Path
    plddt_mean: float = 0.0
    interface_pae: float = 0.0
    predicted_iptm: float = 0.0
    affinity_estimate_nm: float | None = None


class BinderResult(BaseModel):
    engine: str
    binders: list[BinderHit]
    wall_seconds: float = 0.0
    metadata: dict = Field(default_factory=dict)


class BindCraftAdapter:
    engine_name = "bindcraft"

    def __init__(
        self,
        *,
        cache_dir: Path = Path(".cache/bindcraft"),
        weights_dir: Path | None = None,
        device: str = "cuda:0",
        binary: str = "bindcraft",
    ) -> None:
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.weights_dir = weights_dir
        self.device = device
        self.binary = binary

    def design(self, req: BinderRequest) -> BinderResult:
        t0 = time.time()
        with TemporaryDirectory(prefix="bindcraft_", dir=self.cache_dir) as tmp:
            tmp_dir = Path(tmp)
            config_path = tmp_dir / "config.json"
            config_path.write_text(json.dumps({
                "target": str(req.target_pdb),
                "hotspot_residues": req.target_hotspot_residues,
                "binder_length_min": req.binder_length_min,
                "binder_length_max": req.binder_length_max,
                "n_designs": req.n_designs,
                "seed": req.seed,
            }))
            out_dir = tmp_dir / "designs"
            out_dir.mkdir()

            cmd = [
                self.binary, "design",
                "--config", str(config_path),
                "--output", str(out_dir),
                "--device", self.device,
            ]
            if self.weights_dir:
                cmd += ["--weights_dir", str(self.weights_dir)]

            try:
                subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=14400)
            except FileNotFoundError:
                logger.warning(
                    "BindCraft 미설치. git clone https://github.com/martinpacesa/BindCraft"
                )
                return BinderResult(
                    engine=self.engine_name, binders=[],
                    wall_seconds=time.time() - t0,
                    metadata={"error": "bindcraft not installed"},
                )

            return self._parse_designs(out_dir, t0, req.n_designs)

    def _parse_designs(self, out_dir: Path, t0: float, n_expected: int) -> BinderResult:
        result_json = out_dir / "results.json"
        if not result_json.exists():
            logger.warning("BindCraft 결과 없음 — 디자인 실패")
            return BinderResult(engine=self.engine_name, binders=[],
                                wall_seconds=time.time() - t0)

        data = json.loads(result_json.read_text())
        binders: list[BinderHit] = []
        persistent_dir = self.cache_dir / "designs"
        persistent_dir.mkdir(exist_ok=True)
        for i, entry in enumerate(data.get("designs", [])):
            src = Path(entry["pdb"])
            target = persistent_dir / f"design_{i:03d}.pdb"
            if src.exists():
                target.write_bytes(src.read_bytes())
            binders.append(
                BinderHit(
                    sequence=entry["sequence"],
                    pdb_path=target,
                    plddt_mean=float(entry.get("plddt_mean", 0.0)),
                    interface_pae=float(entry.get("interface_pae", 0.0)),
                    predicted_iptm=float(entry.get("predicted_iptm", 0.0)),
                    affinity_estimate_nm=entry.get("affinity_nm"),
                )
            )

        # 우선순위: predicted_iptm 내림차순
        binders.sort(key=lambda b: b.predicted_iptm, reverse=True)
        logger.info(
            "BindCraft: {}/{} 바인더 디자인 (top iptm={:.3f})",
            len(binders), n_expected,
            binders[0].predicted_iptm if binders else 0.0,
        )
        return BinderResult(
            engine=self.engine_name,
            binders=binders,
            wall_seconds=time.time() - t0,
            metadata={"n_designs_requested": n_expected},
        )
