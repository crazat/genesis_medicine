"""Residence time (k_off) MD — RL weighted ensemble + steered MD.

drug efficacy 핵심 = residence time (Copeland 2016, NRDD).
정량 ΔG (-32.9 kcal/mol)만으로는 부족 — 결합 → 해리 시간 측정 필요.

방법:
  1. **Steered MD (pulling)** — ligand에 외력 가해 빠른 unbinding 측정 → Jarzynski equality
  2. **Metadynamics** — collective variable (ligand-protein 거리) bias
  3. **Weighted ensemble** (WESTPA) — RL-guided rare event sampling

우리 실용 옵션 (RTX 5090):
  - Steered MD: 10-50 ns × 5 replicas — 1시간 내 가능
  - τ_residence 추정: 0.1-100 ms 범위 (drug-like)
  - **EMB-3 vs Embelin 비교**: 동일 protocol → 직접 비교

라이선스: OpenMM 8.5 (MIT) — 직접 구현. WESTPA (MIT) — 별도 통합.
"""

from __future__ import annotations

import warnings
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

warnings.filterwarnings("ignore")
import numpy as np


@dataclass
class SteeredMDConfig:
    """Steered MD pulling parameters."""

    n_replicas: int = 5
    pull_velocity_nm_per_ns: float = 1.0   # 빠른 pulling (Jarzynski)
    pull_distance_nm: float = 3.0           # 결합 사이트 → bulk water
    spring_constant_kJ_per_nm2: float = 1000.0   # harmonic restraint
    eq_ns_before_pull: float = 5.0
    pull_ns: float = 5.0                     # 1 nm/ns × 3 nm → 3 ns + buffer
    temperature_K: float = 310.0


@dataclass
class ResidenceTimeResult:
    """k_off measurement 결과."""

    compound_smiles: str = ""
    target: str = ""
    delta_g_pull_kcal: float = 0.0          # Jarzynski avg ΔG
    pmf_barrier_kcal: float = 0.0           # PMF 최고점
    n_unbinding_events: int = 0
    estimated_k_off_per_s: float = 0.0      # 1/τ
    residence_time_ms: float = 0.0
    method: str = ""
    metadata: dict = field(default_factory=dict)


def jarzynski_estimate(
    pull_works_kcal: list,
    temperature_K: float = 310.0,
) -> float:
    """Jarzynski equality:
       ΔG = -kT × log(<exp(-W/kT)>)

    Args:
        pull_works_kcal: 각 replica의 pulling work (kcal/mol)

    Returns:
        ΔG (kcal/mol)
    """
    R_kcal = 1.987e-3  # kcal/mol/K
    kT = R_kcal * temperature_K
    works = np.array(pull_works_kcal)
    avg_exp = np.mean(np.exp(-works / kT))
    return float(-kT * np.log(avg_exp))


def estimate_k_off_from_barrier(
    pmf_barrier_kcal: float,
    temperature_K: float = 310.0,
    prefactor_per_s: float = 1e10,   # transition state theory
) -> dict:
    """Eyring equation:
       k_off = (kT/h) × exp(-ΔG_barrier / RT)

    Args:
        pmf_barrier_kcal: PMF 최고점 (kcal/mol)
        prefactor_per_s: TST prefactor (typically 10^9-10^10)
    """
    R_kcal = 1.987e-3
    kT = R_kcal * temperature_K
    k_off = prefactor_per_s * np.exp(-pmf_barrier_kcal / kT)
    return {
        "k_off_per_s": float(k_off),
        "residence_time_s": float(1 / k_off),
        "residence_time_ms": float(1000 / k_off),
        "pmf_barrier_kcal": pmf_barrier_kcal,
    }


def setup_steered_md(
    cif_path: Path,
    ligand_smiles: str,
    target_name: str,
    cfg: SteeredMDConfig | None = None,
    out_dir: Path | None = None,
) -> dict:
    """Steered MD setup (실행은 별도 — GPU 필요).

    실행 순서:
      1. CIF → OpenMM system (EMB-3 ABFE setup_system 재사용)
      2. Equilibration NPT 5 ns
      3. Constant velocity pulling (1 nm/ns) along ligand-protein COM vector
      4. 5 replicas → Jarzynski avg ΔG
      5. PMF reconstruction (umbrella sampling 또는 SMD direct)
    """
    cfg = cfg or SteeredMDConfig()
    out_dir = out_dir or Path(".cache/steered_md")
    out_dir.mkdir(parents=True, exist_ok=True)

    instructions_md = out_dir / "RUN_STEERED_MD.md"
    instructions_md.write_text(f"""# Steered MD setup — {target_name} × ligand

## Config
- Replicas: {cfg.n_replicas}
- Pull velocity: {cfg.pull_velocity_nm_per_ns} nm/ns
- Pull distance: {cfg.pull_distance_nm} nm (bound → unbound)
- Spring K: {cfg.spring_constant_kJ_per_nm2} kJ/(mol·nm²)
- EQ: {cfg.eq_ns_before_pull} ns NPT
- Pull: {cfg.pull_ns} ns
- T: {cfg.temperature_K} K

## OpenMM 구현 핵심

```python
from openmm import CustomCentroidBondForce, CustomExternalForce
import openmm as mm

# Ligand과 protein binding pocket의 COM 거리에 harmonic + moving 평형점
force = CustomCentroidBondForce(2,
    "0.5*K*(distance(g1,g2) - r0(t))^2"
)
force.addPerBondParameter("K")
force.addPerBondParameter("r0(t)")  # time-dependent

# r0(t) = r_init + v * t
# 5 replicas with different starting velocities (random seed)
```

## 결과 분석
1. Each replica: pull_work_kcal[i]
2. Jarzynski: ΔG_unbind = -kT log <exp(-W/kT)>
3. Eyring: k_off = (kT/h) exp(-ΔG/RT)
4. residence time = 1/k_off

## 예상 결과 (drug-like)
- ΔG_unbind: 5-15 kcal/mol
- k_off: 10⁻³-10⁻⁶ /s
- residence time: 1 ms - 1000 s

## EMB-3 vs Embelin 비교 protocol
- 동일 receptor (MMP-1)
- 동일 5 replicas, 동일 protocol
- ΔΔG_residence > 5 kcal/mol → "EMB-3 stays bound 100x longer"
""")
    return {
        "instructions": str(instructions_md),
        "estimated_gpu_hours": cfg.n_replicas * (cfg.eq_ns_before_pull
                                                  + cfg.pull_ns) / 800 * 24,
        "method": "steered_md_jarzynski",
    }


def compare_emb3_vs_embelin_protocol() -> dict:
    """EMB-3 vs Embelin residence time 비교 protocol."""
    return {
        "protocol": "Steered MD with identical conditions",
        "target": "MMP-1 (P03956)",
        "compounds": {
            "EMB-3": "CCCCCC1=C(O)C(=O)C(O)=C(C)C1=O",
            "Embelin": "CCCCCCCCCCCC1=C(C(=O)C=C(C1=O)O)O",
        },
        "metrics": [
            "ΔG_unbind (Jarzynski)",
            "PMF barrier (kcal/mol)",
            "k_off (Eyring)",
            "residence time τ (s, ms)",
        ],
        "expected_outcome": (
            "EMB-3 longer residence (예측): MMP-1 ABFE ΔG_decoupling -32.9 kcal/mol "
            "+ MD 0.79 Å mean RMSD (53% more stable than Embelin 1.70 Å) → "
            "kinetic barrier도 더 클 것"
        ),
        "estimated_gpu_hours_per_compound": 5 * 10 / 800 * 24,  # 5 rep × 10 ns
        "total_gpu_hours": 5 * 10 / 800 * 24 * 2,
    }
