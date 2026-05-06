# P23 Pigmentation-target Chromanol/Pterocarpan Outline

- timestamp: `2026-05-01T13:13:00+09:00`
- status: `outline started`
- scope: DCT/TYR/TYRP1 중심 pigment-target paper로 분리한다.
- caveat: `in silico only`; wet-lab validation pending; no clinical efficacy claim.

## 독립 질문

R16 topical chromanol analog panel이 DCT/TYR 축에서 반복 가능한 pose-stability와 pigment-target prioritization 신호를 보이는가?

## 핵심 근거

- R16 topical chromanol 30 ns matrix: 18/18 stable, max RMSD 1.38 A, max last-third 1.17 A.
- Pigment representative 60 ns: DCT/TYR 3/3 stable.
- High-confidence structure consensus 후보: `r16_03_dct`, `r16_02_dct`, `r16_02_tyr`.
- Perturbation biology gate에서 DCT/TYR는 `high` priority이며 melanocyte melanin content + tyrosinase activity endpoint와 직접 연결된다.

## Figure/Table Set

1. DCT/TYR/TYRP1 cofold affinity and confidence ranking.
2. R16 pigment 30 ns matrix heatmap.
3. Pigment representative 60 ns RMSD traces/table.
4. PoseBusters pass/review caveat table.
5. Wet-lab endpoint table: B16F10 or human melanocyte melanin content, tyrosinase activity, viability.

## Claim 경계

- Direct pigmentation efficacy나 whitening claim은 쓰지 않는다.
- `gate_status=review`는 raw Boltz pose caveat로 서술하고, MD 안정성과 분리해 해석한다.
- TYRP1은 cofold/pose 근거가 있어도 60-100 ns MD가 없으면 보조/가설 표에 둔다.

## 다음 작업

- P16과 중복되는 TGFB1 topical lead narrative를 제외한다.
- 100 ns anchor triad에서 DCT/TYR 결과가 완료되면 P23 main robustness table에 반영한다.
- CRO/RFQ에는 melanin content, tyrosinase activity, viability endpoint를 우선 연결한다.
