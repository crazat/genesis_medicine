# Stratum Corneum bilayer 시스템 빌드 — charmm36

## 옵션 1: CHARMM-GUI Membrane Builder (권장, 무료 학술)

1. https://charmm-gui.org/?doc=input/membrane.bilayer 접속
2. 새 system 생성:
   - Lipid composition:
     * CER NS (N-stearoyl-D-erythro-sphingosine): 16/leaflet
     * Saturated FFA C24:0 (lignoceric acid): 16/leaflet
     * Cholesterol (CHL1): 16/leaflet
   - Box: 6.0 × 6.0 × 12.0 nm
   - Temperature: 310.0 K
3. 생성된 system 다운로드 → /home/crazat/genesis_medicine/pilot/scaffold_hop/sc_permeation/sc_system/charmmgui_inputs/

## 옵션 2: packmol-memgen (AmberTools)

```bash
packmol-memgen --lipids CER:OLEIC_ACID:CHL --ratio 1:1:1 \
    --aw 30 --w 30 --notprotein --ffwat tip3p
```

## OpenMM 시뮬

CHARMM-GUI 또는 packmol 결과 PDB → OpenMM 8.5 SystemGenerator
(`openmmforcefields` lipid17 또는 charmm36) → langevin NPT.

이 모듈의 `simulate_permeation()` 함수가 후속 처리.
