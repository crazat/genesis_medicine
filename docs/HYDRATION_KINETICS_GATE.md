# Hydration and Kinetics Gate

- timestamp: `2026-05-06T12:46:33+09:00`
- rows: `32`
- counts: `{'hydration_priority': 32, 'residence_proxy': 6}`
- purpose: RMSD 안정성만으로는 부족한 water displacement/residence-time follow-up 우선순위를 정한다.

## Top Follow-ups

| target | compound | hydration | residence | ns | RMSD max | next |
|---|---|---|---|---:|---:|---|
| dct | R15_chromanol_Cl_pos9 | WaterKit_or_GIST_priority | residence_time_proxy_candidate | 100.0 | 1.13 | consider SMD/tauRAMD-style unbinding proxy after 100 ns anchor summary |
| tyr | R15_chromanol | WaterKit_or_GIST_priority | residence_time_proxy_candidate | 100.0 | 0.62 | consider SMD/tauRAMD-style unbinding proxy after 100 ns anchor summary |
| tgfb1 | R15_chromanol_Me6_Me9 | WaterKit_or_GIST_priority | residence_time_proxy_candidate | 60.0 | 0.72 | consider SMD/tauRAMD-style unbinding proxy after 100 ns anchor summary |
| dct | R15_chromanol_Cl_pos6 | WaterKit_or_GIST_priority | residence_time_proxy_candidate | 60.0 | 0.72 | consider SMD/tauRAMD-style unbinding proxy after 100 ns anchor summary |
| tyr | R15_chromanol_Cl_pos6 | WaterKit_or_GIST_priority | residence_time_proxy_candidate | 100.0 | 0.62 | consider SMD/tauRAMD-style unbinding proxy after 100 ns anchor summary |
| tgfb1 | R15_chromanol_Cl_pos6 | WaterKit_or_GIST_priority | residence_time_proxy_candidate | 60.0 | 1.22 | consider SMD/tauRAMD-style unbinding proxy after 100 ns anchor summary |
| tgfb1 | R15_chromanol_Cl_pos9 | WaterKit_or_GIST_priority | stability_only_candidate | 100.0 | 0.69 | run hydration-site map before substituent optimization |
| dct | R15_chromanol | WaterKit_or_GIST_priority | stability_only_candidate | 100.0 | 1.13 | run hydration-site map before substituent optimization |
| tgfb1 | R15_chromanol_Me9_Me10 | WaterKit_or_GIST_priority | stability_only_candidate | 60.0 | 0.7 | run hydration-site map before substituent optimization |
| tgfb1 | R15_chromanol | WaterKit_or_GIST_priority | stability_only_candidate | 100.0 | 0.69 | run hydration-site map before substituent optimization |
| tgfb1 | R15_chromanol_Me6_Me10 | WaterKit_or_GIST_priority | stability_only_candidate | 60.0 | 1.18 | run hydration-site map before substituent optimization |
| tgfb1 | R15_chromanol_Cl_pos10 | WaterKit_or_GIST_priority | stability_only_candidate | 60.0 | 1.21 | run hydration-site map before substituent optimization |
| ptgs2 | R15_chromanol | WaterKit_or_GIST_priority | not_ready | 0.0 |  | run hydration-site map before substituent optimization |
| tyr | R15_chromanol_Cl_pos9 | WaterKit_or_GIST_priority | not_ready | 0.0 |  | run hydration-site map before substituent optimization |
| dct | R15_chromanol_Cl_pos10 | WaterKit_or_GIST_priority | not_ready | 0.0 |  | run hydration-site map before substituent optimization |
| tyr | R15_chromanol_Cl_pos10 | WaterKit_or_GIST_priority | not_ready | 0.0 |  | run hydration-site map before substituent optimization |
| tyrp1 | R15_chromanol | WaterKit_or_GIST_priority | not_ready | 0.0 |  | run hydration-site map before substituent optimization |
| tyr | R15_chromanol_Me9_Me10 | WaterKit_or_GIST_priority | not_ready | 0.0 |  | run hydration-site map before substituent optimization |
| tyr | R15_chromanol_Me6_Me9 | WaterKit_or_GIST_priority | not_ready | 0.0 |  | run hydration-site map before substituent optimization |
| dct | R15_chromanol_Me6_Me9 | WaterKit_or_GIST_priority | not_ready | 0.0 |  | run hydration-site map before substituent optimization |
| dct | R15_chromanol_Me9_Me10 | WaterKit_or_GIST_priority | not_ready | 0.0 |  | run hydration-site map before substituent optimization |
| tyr | R15_chromanol_Me6_Me10 | WaterKit_or_GIST_priority | not_ready | 0.0 |  | run hydration-site map before substituent optimization |
| dct | R15_chromanol_Me6_Me10 | WaterKit_or_GIST_priority | not_ready | 0.0 |  | run hydration-site map before substituent optimization |
| mmp1 | R15_chromanol | WaterKit_or_GIST_priority | not_ready | 0.0 |  | run hydration-site map before substituent optimization |
| sirt1 | R15_chromanol | WaterKit_or_GIST_priority | not_ready | 0.0 |  | run hydration-site map before substituent optimization |

## Curator Rule

- hydration priority 후보는 substituent optimization 전에 WaterKit/GIST-lite 계층을 고려한다.
- residence proxy 후보는 60-100 ns 안정성 이후에만 SMD/tauRAMD-style 후속으로 올린다.
- 이 파일은 실제 kinetics claim이 아니라 후속 실험/계산 우선순위다.
