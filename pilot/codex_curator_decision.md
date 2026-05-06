# Codex Curator Decision

- timestamp: `2026-05-02T21:31:02+09:00`
- tick_type: `autonomous_curator_tick`
- language: `ko`

## CPU 상태 판단

- `vmstat 1 2` 재확인 기준 CPU idle은 `50%`까지 내려왔지만, tick 초반에는 `76-84%`로 높았다. 이는 `top9997_hetero10_240conf` 12-worker xTB와 보호 NPASS만으로는 CPU를 충분히 채우지 못한 `CPU_IDLE_GAP` 상태다.
- 보호 큐 `PID 15578` 및 자식 프로세스는 그대로 보존했다. `PID 1345` 계열도 종료/변경하지 않았다.
- 기존 non-empty output을 확인한 결과 `xtb_npass_top5000_hetero6_refine_36conf.csv`는 없고, 해당 작업도 실행 중이 아니었다. P18/P19 NPASS atlas/conformer-ladder paper에 직접 필요한 빈 rung이므로 companion CPU task로 큐잉했다.
- 현재 CPU 작업: `top9997_hetero10_240conf` `PID 566734` 계열, 신규 `top5000_hetero6_36conf` `PID 799030` 계열, 보호 NPASS `PID 15578` 계열.

## GPU 상태 판단

- R16/R15/R17 chromanol MD 검증 큐는 R16 anchor 200 ns 및 R17 top/next/expanded green-target 10/30/60 ns까지 안정 완료 상태다.
- active-learning batch17이 완료된 뒤 GPU가 `5%, 1989/32607 MiB`까지 내려갔고, planner는 `active_learning_next_boltz2_cofold`와 `149` runnable pending pair를 추천했다.
- `scripts/auto_queue_cpu_gpu_daemon.sh`가 `2026-05-02T21:30:00+09:00`에 batch18을 자동 큐잉했다. 현재 active GPU job은 `scripts/run_active_learning_next_cofold.py PID 798508`이며, 최종 GPU 상태는 `60%, 10471/32607 MiB`다.
- 수동 GPU 큐잉은 중복 방지를 위해 하지 않았다.

## 새로 확인한 결과

- 필수 paper/evidence/synthesis/active-learning/BO/pocket/consensus-v2/generative/route-enumeration/skin-cell-state/photosafety/quinone/DMTL/spatial/engagement/PBPK/metabolite/genetic/PV/single-cell/benchmark/formulation/free-energy/regulatory/perturbation/hydration/ultra-large/uncertainty/phenomics/CMC/IP/prior-art/FAIR/wet-lab/model-governance/provenance/creative/world-class 생성기와 `cpu_chromanol_pose_sanity_gate.py`, `auto_result_planner.py`를 `.venv`로 실행했고 `GENERATOR_FAILURES=0`이었다.
- active-learning batch17 완료: `pilot/cpu_meaningful/active_learning_next_cofold_batch17.csv`, `16 rows`.
- batch17 최고 signal은 `NPC72839 × LOX` `affinity_probability_binary=0.427971`이다. 기존 전체 상위 `NPC329473 × CTGF` `0.6921`, `NPC228980 × CTGF` `0.6709`보다 낮아 독립 lead claim으로 승격하지 않고 P58 triage evidence로만 둔다.
- `docs/PAPER_FACTORY_QUEUE.md`를 재생성해 P58을 `completed short-cofold rows=251`, `active cofold manifests=267`, `runnable short-cofold pairs=149`, `blocked missing-MSA pairs=160`으로 갱신했다.
- batch18은 manifest 생성 후 구조 예측을 시작했으며, 아직 CSV 완료 파일은 없다.

## 실행한 큐잉

- GPU: daemon이 `active_learning_next_boltz2_cofold` batch18을 자동 큐잉했다. `PID 798508`, log `pilot/active_learning_next_cofold_auto.log`.
- CPU: `CPU_IDLE_GAP` 해소와 P18/P19 ladder 보강을 위해 아래 작업을 수동 큐잉했다.
  - `PID 799030`
  - log `pilot/cpu_xtb_npass_top5000_hetero6_36conf_manual.log`
  - output `pilot/cpu_meaningful/xtb_npass_top5000_hetero6_refine_36conf.csv`
  - command family: `scripts/cpu_xtb_npass_top_refine.py --topn 5000 --workers 8 --num-confs 36 --min-hetero-atoms 6`
- 필수 문서/gate/논문 큐는 batch17 완료분까지 반영했다.

## 보류한 큐잉과 이유

- 추가 GPU job: batch18이 이미 실행 중이므로 중복 방지를 위해 보류했다.
- 신규 long-MD, RBFE/ABFE/FE, 추가 R17 heavy expansion: Markush/FTO, world-class master gate, cross-model/decoy/PLIF, wet-lab/formulation package 전까지 보류한다. 현재 GPU는 active-learning short cofold triage까지만 허용한다.
- 추가 CPU xTB rung: `top5000_hetero6_36conf`를 8-worker로 시작했으므로 이번 tick에서는 더 늘리지 않는다. 다음 tick에서 idle과 batch18 상태를 보고 판단한다.
- batch17 결과의 manuscript 승격: 최고 affinity가 0.428 수준이라 P58/P28 운영 evidence 이상으로 쓰지 않는다. direct Boltz/pose/MD, synthesis/prior-art/FTO, phenotype/wet-lab, cross-model/decoy/PLIF 보강 전까지 lead claim 금지.
- TGFB1은 yellow target caveat를 유지한다. MMP-1은 `docs/MMP1_ZAFF_ABFE_GATE.md`의 `blocked_zaff_not_integrated` 때문에 ZAFF/ABFE-confirmed binding 표현 금지.
- 모든 manuscript 표현은 `in silico only`, `wet-lab validation pending`, `no clinical efficacy claim`으로 제한한다.

## 다음 curator가 우선 확인할 파일/명령

1. `tail -160 pilot/active_learning_next_cofold_auto.log`
2. `ls -lh pilot/cpu_meaningful/active_learning_next_cofold_batch18.csv pilot/cpu_meaningful/active_learning_next_cofold_batch18_manifest.csv`
3. `tail -80 pilot/cpu_xtb_npass_top5000_hetero6_36conf_manual.log`
4. `ls -lh pilot/cpu_meaningful/xtb_npass_top5000_hetero6_refine_36conf.csv pilot/cpu_meaningful/xtb_npass_top9997_hetero10_refine_240conf.csv`
5. `pgrep -af 'run_active_learning_next_cofold|boltz predict|cpu_xtb_npass_top_refine|cpu_5000_conformers'`
6. `/home/crazat/genesis_medicine/.venv/bin/python scripts/auto_result_planner.py`
7. `nvidia-smi --query-gpu=utilization.gpu,memory.used,memory.total --format=csv,noheader`
8. `vmstat 1 3`
