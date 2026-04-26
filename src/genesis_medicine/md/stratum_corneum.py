"""Stratum Corneum lipid 모델 — IJMS 2025 (Espinoza-Marín et al.)

ceramide CER NS (24:0) + free fatty acid (FFA) (24:0) + cholesterol (CHOL)
1:1:1 ratio, multilamellar. SC intercellular space의 표준 atomistic model.

목적:
  - EMB-3 (logKp -1.86 예측) 실제 SC permeation MD validation
  - ECa 233 (51:38 madecassoside:asiaticoside) reference 비교
  - 외용제 IND 식약처 자료의 in silico 데이터 hook

이 모듈은 SC bilayer system 빌드 + ligand 평형 위치 + Pulled MD 또는 PMF 계산
인터페이스 제공. 실제 ceramide/FFA/CHOL 좌표는 OpenFF 또는 CHARMM-GUI lipid builder
사용 권장.

라이선스: OpenMM (MIT) + ParmEd (LGPL but subprocess) + CHARMM36 lipids (CHARMM
academic, research only — commercial 빌드는 GAFF lipid 또는 SLipids 사용).
"""

from __future__ import annotations

import warnings
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class StratumCorneumConfig:
    """SC bilayer 시스템 파라미터."""

    # Lipid 비율 (mol)
    n_ceramide: int = 16
    n_ffa: int = 16
    n_chol: int = 16

    # 비율 (1:1:1 IJMS 2025 표준 + 1:0.5:1 atopic skin variant 가능)
    ratio: tuple[float, float, float] = (1.0, 1.0, 1.0)

    # Box dimensions (nm)
    box_x: float = 6.0
    box_y: float = 6.0
    box_z: float = 12.0   # 다층 두께

    # Force field
    lipid_ff: str = "charmm36"   # charmm36 | slipids | gaff
    water_model: str = "tip3p"

    # MD parameters
    temperature_K: float = 310.0
    pressure_atm: float = 1.0
    timestep_fs: float = 2.0

    # Permeation simulation
    n_replicas: int = 16
    eq_ns: float = 50.0     # 50 ns equilibration (lipid system은 평형 어려움)
    pull_ns: float = 100.0  # ligand 푸시 시뮬


@dataclass
class PermeationResult:
    """SC permeation MD 결과."""

    compound_name: str
    smiles: str
    log_kp_md: float = 0.0           # MD-derived log Kp (cm/h)
    free_energy_barrier_kcal: float = 0.0
    binding_to_lipid_kcal: float = 0.0
    n_simulations: int = 0
    wall_hours: float = 0.0
    metadata: dict = field(default_factory=dict)


def build_sc_system(cfg: StratumCorneumConfig, out_dir: Path) -> dict:
    """SC bilayer 시스템 빌드.

    실제 빌드는 CHARMM-GUI Membrane Builder (https://charmm-gui.org/?doc=input/membrane.bilayer)
    또는 packmol-memgen (AmberTools) 사용 권장. 여기서는 인터페이스만.

    Returns:
        dict: pdb_path, psf_path (CHARMM의 경우), gro/top (GROMACS), system_xml (OpenMM)
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    instructions_md = out_dir / "BUILD_SC_SYSTEM.md"
    instructions_md.write_text(f"""# Stratum Corneum bilayer 시스템 빌드 — {cfg.lipid_ff}

## 옵션 1: CHARMM-GUI Membrane Builder (권장, 무료 학술)

1. https://charmm-gui.org/?doc=input/membrane.bilayer 접속
2. 새 system 생성:
   - Lipid composition:
     * CER NS (N-stearoyl-D-erythro-sphingosine): {cfg.n_ceramide}/leaflet
     * Saturated FFA C24:0 (lignoceric acid): {cfg.n_ffa}/leaflet
     * Cholesterol (CHL1): {cfg.n_chol}/leaflet
   - Box: {cfg.box_x} × {cfg.box_y} × {cfg.box_z} nm
   - Temperature: {cfg.temperature_K} K
3. 생성된 system 다운로드 → {out_dir}/charmmgui_inputs/

## 옵션 2: packmol-memgen (AmberTools)

```bash
packmol-memgen --lipids CER:OLEIC_ACID:CHL --ratio 1:1:1 \\
    --aw 30 --w 30 --notprotein --ffwat tip3p
```

## OpenMM 시뮬

CHARMM-GUI 또는 packmol 결과 PDB → OpenMM 8.5 SystemGenerator
(`openmmforcefields` lipid17 또는 charmm36) → langevin NPT.

이 모듈의 `simulate_permeation()` 함수가 후속 처리.
""")

    return {
        "instructions": str(instructions_md),
        "expected_files": [
            "system.pdb", "system.psf", "topol.top", "system.xml",
        ],
        "n_atoms_estimated": (cfg.n_ceramide * 100
                                + cfg.n_ffa * 80
                                + cfg.n_chol * 50) * 2,  # both leaflets
    }


def simulate_permeation(
    sc_system_pdb: Path,
    ligand_smiles: str,
    cfg: StratumCorneumConfig,
    out_dir: Path,
) -> PermeationResult:
    """ligand SC permeation MD 시뮬.

    실행 순서:
      1. Ligand parametrize (OpenFF AM1-BCC)
      2. Place ligand in water phase
      3. Equilibrate (NPT 50 ns)
      4. Steered MD or umbrella sampling (PMF along z-axis)
      5. log Kp 계산: log Kp = -ΔG_barrier / (R*T) + log(D_membrane / h)

    이 함수는 큰 시뮬 실행 — 실제 호출은 별도 스크립트에서.
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # 시작 메타데이터
    log_path = out_dir / "permeation_log.json"
    import json
    log_path.write_text(json.dumps({
        "ligand_smiles": ligand_smiles,
        "sc_system": str(sc_system_pdb),
        "config": {
            "n_replicas": cfg.n_replicas,
            "eq_ns": cfg.eq_ns,
            "pull_ns": cfg.pull_ns,
            "temperature_K": cfg.temperature_K,
        },
        "status": "pending",
        "estimated_gpu_hours": cfg.n_replicas * cfg.pull_ns / 800,  # @ 800ns/day
    }, indent=2))

    # placeholder result
    return PermeationResult(
        compound_name=ligand_smiles[:30],
        smiles=ligand_smiles,
        log_kp_md=0.0,
        free_energy_barrier_kcal=0.0,
        n_simulations=0,
        wall_hours=0.0,
        metadata={
            "stub": True,
            "instruction": ("CHARMM-GUI build → OpenMM 8.5 + AMBER lipid17 / "
                             "charmm36 lipids → 50 ns eq + 100 ns pull MD per "
                             "replica. 추정 시간: "
                             f"{cfg.n_replicas * cfg.pull_ns / 800:.1f} 시간."),
        },
    )


def estimate_log_kp_from_md(
    free_energy_barrier_kcal: float,
    diffusion_coeff_cm2_s: float = 1e-7,
    membrane_thickness_cm: float = 8e-7,   # SC ~ 8 nm
    temperature_K: float = 310.0,
) -> float:
    """ΔG barrier → log Kp 변환 (Diamond & Katz, 1974).

    log Kp = log(D) - log(h) - ΔG / (2.303 * R * T)

    여기서:
      D = lateral diffusion coefficient (cm²/s)
      h = SC thickness (cm)
      ΔG = free energy barrier (kcal/mol)
      R = 1.987e-3 kcal/(mol·K)
    """
    import math
    R_kcal = 1.987e-3
    log_d = math.log10(diffusion_coeff_cm2_s)
    log_h = math.log10(membrane_thickness_cm)
    log_kp = log_d - log_h - free_energy_barrier_kcal / (2.303 * R_kcal * temperature_K)
    return log_kp
