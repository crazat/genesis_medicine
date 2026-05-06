# P24 Scar/Fibrosis Topical Lead Outline

- timestamp: `2026-05-01T13:13:00+09:00`
- status: `outline started`
- scope: TGFB1/MMP1 중심 scar/fibrosis topical lead paper로 분리한다.
- caveat: `in silico only`; wet-lab validation pending; no clinical efficacy claim.

## 독립 질문

TGFB1 chromanol topical analog stability와 MMP1 extended MD 결과를 결합했을 때, scar/fibrosis phenotype assay로 넘길 우선순위 후보를 합리적으로 좁힐 수 있는가?

## 핵심 근거

- R16 TGFB1 top-6 60 ns: 6/6 stable, max RMSD 1.22 A, max last-third 0.96 A.
- Anchor triad 100 ns: `r16_03_tgfb1__R15_chromanol_Cl_pos9__100ns` stable, mean 0.51 A, max 0.69 A, last-third 0.51 A.
- MMP1 extended 30 ns: `mmp1__r14_5_30ns` and `mmp1__r12_4_30ns` stable.
- Target evidence gate: MMP1 is `green`; TGFB1 is `yellow`, so TGFB1 claim은 fibroblast phenotype endpoint와 같이 제한해 쓴다.

## Figure/Table Set

1. TGFB1 top-6 60 ns analog stability table.
2. Anchor 100 ns progression table: TGFB1 completed, DCT/TYR pending for P16/P23 integration.
3. MMP1 30 ns stability comparison for R12/R14 scaffold context.
4. Evidence/modality gate table showing MMP1 `green`, TGFB1 `yellow`.
5. CRO endpoint table: TGF-beta induced fibroblast COL1A1/ACTA2 qPCR, viability, optional collagen deposition readout.

## Claim 경계

- Anti-fibrotic or scar improvement efficacy claim은 금지한다.
- TGFB1은 yellow evidence target이므로 direct biology claim보다 assay-ready hypothesis로 낮춘다.
- MD RMSD stability는 binding residence time이나 free energy를 대체하지 않으며 FE/OpenFE는 현재 `openfe_missing_install_or_env` 상태다.

## 다음 작업

- P16의 broad topical chromanol lead story와 중복되지 않게 scar/fibrosis endpoint 중심으로 작성한다.
- 100 ns anchor triad가 3/3 완료되면 TGFB1 결과는 P24 robustness section, DCT/TYR는 P23/P16에 분배한다.
- Wet-lab schema priority 1을 CRO RFQ appendix로 확장한다.
