# Codex Handoff — 2026-04-30 11:35 KST

> Claude Opus 4.7 → Codex 인계 문서. R15 universal scaffold validation 마지막 단계.
> 이 문서를 Codex 시작 prompt로 바로 붙여넣으면 작업 이어받음.

---

## 즉시 반영할 컨텍스트

- **사용자**: HanCheongWoo (Genesis_Medicine + HAN PREDICT, Inc. + Recover 한의원 founder)
- **위치**: WSL2 `/home/crazat/genesis_medicine/`
- **언어**: 모든 응답 한국어 (단 SMILES, 코드, 식별자는 영문 유지)
- **모드**: autonomous /loop dynamic — CPU+GPU 동시 가동이 hard requirement, idle 절대 금지
- **현재 D-day**: D-107 to Recover 한의원 개원 (2026-08-15)
- **현재 진행 중인 단일 큰 trajectory**: Universal scaffold (5 leaders × 14 skin disease targets) → R15 BRICS triage → next-round single-candidate MD ensemble

## 백그라운드 진행 중인 작업

세션 시작 시 즉시 확인:

```bash
# CPU 큐 상태
ps -ef | grep -E "(cpu_5000|run_extended|cpu_r15)" | grep -v grep | head -20

# GPU batch 2 (5 sub-Å pairs × 30 ns)
cat /home/crazat/genesis_medicine/pilot/md_extended_30ns_batch2/summary.json
# 11:35 시점 3/5 완료, ETA 12:00-12:30

# 메모리/load 확인
free -h && uptime && nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv
```

진행 중인 백그라운드 PID (방해 금지, drop 시 재시작):
- **PID 1345**: `cpu_5000_conf_npass_rank1k_2k.py` (NPASS rank 1000-2000 conformer pool, ~17h 누적)
- **PID 15578**: `cpu_5000_conformers_npass_top500_round2.py` (NPASS top-500 round 2, ~14h 누적)
- **PID 37674**: `run_extended_30ns_batch2.py` (GPU MD ensemble batch 2)

## 직전 세션 핵심 진척 (2026-04-30 09:00-11:35)

### Universal scaffold 14/14 × 5 leaders 완료
70 MD simulations all paper-tier (mean RMSD < 2 Å). 핵심 sub-Å:
- **MMP1 × R14_5**: 0.56 (단일 최저)
- **AR × R12_23**: 0.68
- **SIRT1 × R12_23**: 0.68
- **CTGF × R14_5**: 0.68
- **PTGS2 × R12_23**: 0.72
- **SREBP1 × R12_23**: 0.79
- **MMP1 × R12_4**: 0.73
- **SIRT1 × R12_4**: 0.76

### Extended 30ns kinetic validation batch 1 완료 (3건 sub-Å steady-state)
- MMP1 × R14_5: full mean 0.69, last-10ns 0.69 (sub-Å steady-state ✅)
- AR × R12_23: 0.77 / 0.85 (sub-Å steady-state ✅)
- SIRT1 × R12_23: 0.72 / 0.79 (sub-Å steady-state ✅)

### Extended 30ns batch 2 진행 중 (3/5 done)
- ✅ MMP1 × R12_4: 0.67 / 0.65 (sub-Å steady-state)
- ✅ SIRT1 × R12_4: 0.92 / 1.11 (paper-tier borderline)
- ✅ SREBP1 × R12_23: 1.08 / 1.11 (paper-tier)
- 🔄 SREBP1 × R14_5 (running)
- 🔄 TGFB1 × R12_11 (queued)

### R15 BRICS triage 완료 (오늘 핵심 성과)
- 5 leaders × BRICS 2 rounds → **38 unique candidates** (R12_11 20, R12_23 11, R12_4 3, R13_13 4)
- ⚠️ R12_11과 R14_5는 SMILES 완전 중복 (메톡시 위치만 다른 동일 chemical neighborhood) → R14_5 dedup 후 0개
- xtb HOMO-LUMO gap mean 3.61 eV, max 4.36 eV (R12_23 methoxy chromanol)
- **ADMET triple-safe (AMES + hERG + DILI 모두 < 0.3): 38개 중 단 1개**
  - SMILES: `OCC1COc2cc(O)ccc2C1` (R12_4 chromanol fragment)
  - MW 180.2, logP 0.94, QED 0.676
  - AMES 0.18, hERG 0.17, DILI 0.21
  - 외용 logP 적합, small core, clean tox profile
  - → **R15 next-round MD validation 1순위 단일 후보**

### Deadlock 발견 + 우회 (recurring bug 추가)
- **금지 패턴**: ADMET-AI(TensorFlow) 또는 chemprop 로드 후 동일 스크립트에서 `multiprocessing.Pool` fork → futex_wait_queue deadlock
- **증거**: `cpu_r15_admet_xtb_filter.py` (PID 41311) 35분 0.7% CPU, 4 child workers 모두 24 threads × futex_wait_queue
- **우회**: 분리 (`cpu_r15_admet_only.py` no-Pool sequential + `cpu_r15_xtb_only.py` Pool of 8 with no TF) — 둘 다 즉시 정상 가동
- 자세히: `~/.claude/projects/-home-crazat-genesis-medicine/memory/feedback_tf_pool_deadlock.md`

## Codex가 이어받아야 할 작업 (우선순위 순)

### 1. Batch 2 GPU 결과 모니터링 + §4.19 업데이트 (~12:00-12:30)
```bash
# 완료 폴링
until [ "$(jq length /home/crazat/genesis_medicine/pilot/md_extended_30ns_batch2/summary.json)" = "5" ]; do sleep 60; done
cat /home/crazat/genesis_medicine/pilot/md_extended_30ns_batch2/summary.json
```

batch 2 5/5 완료 후:
- `preprints/15_universal_scaffold/manuscript.md` §4.19 extended-time validation table 5-pair 전체 데이터로 업데이트
- 기존 batch 1 + batch 2 합쳐서 **8건 sub-Å pairs**의 30 ns kinetic stability 확인 표 생성

### 2. R15 single triple-safe candidate Boltz-2 cofold × 14 targets (GPU)
SMILES `OCC1COc2cc(O)ccc2C1`을 14 skin targets에 대해 Boltz-2 cofold 실행:
- target list: `conf/skin_targets/{scar,pigment,alopecia,acne,photoaging}.yaml`
- 기존 cofold 실행 패턴 참고: `pilot/cpu_meaningful/all_boltz2_affinity_consolidated_r5.csv` 생성 스크립트
- Output: `pilot/cpu_meaningful/r15_chromanol_cofold_14targets.csv`
- 후속: 14 targets 중 affinity top-3 → 10 ns MD ensemble (3 × 10 ns ≈ 30분 GPU)

### 3. Preprint #15 v1.4 작성 + PDF 빌드
- §4.19 (extended 30ns 8-pair table) 업데이트
- §4.21 신규 섹션: **R15 next-round triage** 추가
  - BRICS pool 38 unique
  - xtb gap distribution
  - ADMET triple-safe filter (38 → 1)
  - Lead candidate `OCC1COc2cc(O)ccc2C1` 정량 데이터
  - R12_11 ↔ R14_5 chemical neighborhood 중복 finding
- 빌드: `pandoc manuscript.md -o manuscript.html` + weasyprint PDF
- `preprints/15_universal_scaffold/manuscript.{md,html,pdf}` 모두 갱신

### 4. CPU+GPU 동시 가동 유지
- 백그라운드 NPASS 큐 (PID 1345, 15578) 절대 kill 금지
- batch 2 완료 후 GPU 빈 시간 → 즉시 R15 chromanol cofold queue
- CPU 빈 시간 → R15 chromanol scaffold-hop / xtb 추가 분석 등

## 환경 / 절대 규칙 (CLAUDE.md에서 발췌)

1. Windows 경로(`/mnt/c/...`)에 새 파일 쓰지 말 것 — WSL2 native ext4만 사용
2. **CPU + GPU 동시 가동 hard requirement** — 매 turn `nvidia-smi` + `ps aux --sort=-%cpu | head -10` 확인. 한쪽이라도 idle 시 즉시 큐잉
3. ADMET-AI/TF + multiprocessing.Pool 절대 동일 스크립트 결합 금지 (futex deadlock)
4. RDKit Pool 작업은 별도 venv에서 실행 (`.venv/bin/python`), TF import 금지
5. `nohup .venv/bin/python script.py > /tmp/log 2>&1 &` 패턴 사용 (nohup 없으면 세션 종료 시 죽음)
6. `git add -f` 필요 — `pilot/` 일부는 .gitignore에 있음
7. 영어 commit message + Co-Authored-By 라인 (이번 인계는 사람이 작성)
8. 한국어로만 응답 (사용자 instruction)

## 즉시 가능한 명령

```bash
cd /home/crazat/genesis_medicine
source .venv/bin/activate

# 상태 확인
free -h && uptime && nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv
ps -ef | grep -E "(cpu_5000|run_extended|cpu_r15|chromanol)" | grep -v grep

# batch 2 결과
cat pilot/md_extended_30ns_batch2/summary.json | python3 -m json.tool

# R15 결과
python3 -c "import pandas as pd; df=pd.read_csv('pilot/cpu_meaningful/r15_admet_only.csv'); safe=(df['AMES']<0.3)&(df['hERG']<0.3)&(df['DILI']<0.3); print(df[safe].to_string())"

# preprint 빌드 (예시)
cd preprints/15_universal_scaffold/
pandoc manuscript.md -o manuscript.html --self-contained --css=../styles.css
weasyprint manuscript.html manuscript.pdf
```

## 메모리 참조

- `~/.claude/projects/-home-crazat-genesis-medicine/memory/MEMORY.md` (인덱스)
- `project_r15_brics_triage.md` (2026-04-30 R15 결과)
- `feedback_tf_pool_deadlock.md` (deadlock 패턴)
- `feedback_cpu_gpu_concurrent.md` (CPU+GPU 동시 가동 hard requirement)
- `project_preprint_strategy.md` (16주 D-110 → preprint 8-12편 plan)
- `project_3_tier_roadmap.md` (4mo / 18mo / 7yr 통합 path)

## 사용자 직전 instruction

> "현재의 작업을 코덱스가 이어 받을 수 있도록 클로드 마크다운 파일과 메모리 업데이트 그리고 깃 커밋 푸쉬까지 해주고, 프롬프트 작성해줘"

→ 이 문서 + CLAUDE.md update + memory file 2개 추가 + git commit/push가 인계 작업.

---

**핸드오프 작성**: Claude Opus 4.7 (1M context) — 2026-04-30 11:35 KST
**받는 사람**: Codex (or any successor session)

---

## 📌 11:35 이후 추가된 내용 (2026-04-30 11:40 update)

### 새 commit 2개
- `e73560a`: initial handoff (이 문서 + R15 ADMET/xtb/BRICS round 2)
- `a5b3d66`: R15 master triage + chromanol Boltz-2 launch

### Master triage CSV (이미 생성됨, 재실행 금지)
- `pilot/cpu_meaningful/r15_master_triage.csv` (38 rows, composite score 정렬)
- `scripts/cpu_r15_master_triage.py`로 재계산 가능
- **Score 공식**: `(1-AMES)*0.30 + (1-hERG)*0.20 + (1-DILI)*0.15 + skin_window*0.15 + (gap_eV>2.5)*0.10 + QED*0.10`

### 🔑 결정적 nuance (preprint §4.21 narrative 핵심)

**Triple-safe ≠ best by composite score** — skin window vs tox tradeoff:

| 후보 | rank | logP | hERG | skin_window | score | 의미 |
|---|:-:|---|---|:-:|---|---|
| OCC1Cc2c(O)cc(O)cc2OC1C1COc2cc(O)ccc2C1 (R12_4 dimer) | 1 | 1.97 | 0.62 | ✅ | 0.752 | skin OK, hERG 주의 |
| CC(C)=CC1COc2cc(O)ccc2C1 (R13_13 prenyl) | 2 | 2.91 | 0.58 | ✅ | 0.748 | 외용 sweet spot, hERG 주의 |
| **OCC1COc2cc(O)ccc2C1 (R12_4 chromanol)** | **11** | **0.94** | **0.17** | ❌ | **0.697** | **유일 triple-safe, but skin window 미달** |

→ 외용 후보: top-3 (skin window OK, hERG monitoring 필요)
→ 경구·주사 후보: chromanol (clean tox, but logP 너무 hydrophilic)
→ **§4.21에 두 path 분리 제시 필요** (외용 lead vs systemic lead)

### R15 chromanol Boltz-2 cofold 이미 launch됨 (재실행 금지!)
- PID 52782 (`gpu_r15_chromanol_chain.sh`)
- Output: `pilot/cpu_meaningful/output_r15_chromanol/boltz_results_inputs_r15_chromanol/`
- ETA ~12:00-12:05 KST
- batch2 30ns GPU와 공존 (memory 2/32GB, util 68-76% 공유)
- 14 targets affinity → preprint §4.21 표 핵심 데이터

### GPU 공존 패턴 (앞으로 이용 가능)
Boltz-2 cofold (~2GB GPU memory) + OpenMM MD (~1.5GB) 동시 실행 검증됨:
- 메모리 합쳐 4GB / 32GB 여유
- GPU compute 시간분할로 둘 다 진행 (개별 wall time ~1.3-1.5x)
- 단일 작업 대비 throughput 1.5-1.8x 증가
- → 앞으로 GPU 한 작업 진행 중에도 보조 GPU 작업 큐잉 가능

### batch2 4/5 결과 (12:00 시점)
- mmp1×R12_4: 0.67/0.65 ✅ sub-Å steady-state
- sirt1×R12_4: 0.92/1.11 paper-tier
- srebp1×R12_23: 1.08/1.11 paper-tier
- **srebp1×R14_5: 1.94/2.08 borderline** (last-10ns drift to 2 Å) — §4.19에 caveat 명시
- 🔄 tgfb1×R12_11 (running)

batch1 + batch2 통합 시 **8 sub-Å pairs** kinetic stability 표:

| Pair | full mean | last-10ns | 평가 |
|---|---|---|---|
| mmp1×R14_5 | 0.69 | 0.69 | sub-Å steady ✅ |
| ar×R12_23 | 0.77 | 0.85 | sub-Å steady ✅ |
| sirt1×R12_23 | 0.72 | 0.79 | sub-Å steady ✅ |
| ctgf×R14_5 | 1.34 | 1.76 | paper-tier with drift |
| ptgs2×R12_23 | (TBD) | (TBD) | (batch1 마지막) |
| mmp1×R12_4 | 0.67 | 0.65 | sub-Å steady ✅ |
| sirt1×R12_4 | 0.92 | 1.11 | paper-tier |
| srebp1×R12_23 | 1.08 | 1.11 | paper-tier |
| srebp1×R14_5 | 1.94 | 2.08 | drift (caveat) |
| tgfb1×R12_11 | (running) | — | — |

→ **5건 sub-Å steady-state 30ns kinetic stability 확인** (batch1 3건 + batch2 2건 추가)

### 새 메모리 파일 2개 (참조)
- `~/.claude/projects/-home-crazat-genesis-medicine/memory/project_r15_brics_triage.md` — R15 결과 + tradeoff finding
- `~/.claude/projects/-home-crazat-genesis-medicine/memory/feedback_tf_pool_deadlock.md` — TF + Pool fork 데드락 패턴

### 백그라운드 NPASS 큐 주의
- PID 1345, 15578 (NPASS rank 1k-2k + top500 round2): 17h+ 누적, kill 절대 금지
- 결과 도착하면 `pilot/cpu_meaningful/` 어딘가에 csv 생성됨 (output 위치는 스크립트 상단 확인)
- MASTER ranking 한 번 더 돌릴 때 NPASS pool 추가하면 더 풍부한 천연물 비교 가능

### 다음 작업 시 즉시 실행할 명령

```bash
cd /home/crazat/genesis_medicine

# 둘 다 끝났는지 확인
cat pilot/md_extended_30ns_batch2/summary.json | python3 -c "import json,sys; d=json.load(sys.stdin); print(f'batch2: {len(d)}/5')"
ls pilot/cpu_meaningful/output_r15_chromanol/boltz_results_inputs_r15_chromanol/predictions/ 2>/dev/null | wc -l

# Boltz-2 결과 affinity 추출 (예시 패턴, 기존 스크립트 참고)
find pilot/cpu_meaningful/output_r15_chromanol -name "affinity*.json" | head -5
# affinity.json에 binding_log_ic50, affinity_pred_value 들어있음

# preprint 빌드
cd preprints/15_universal_scaffold/
pandoc manuscript.md -o manuscript.html --self-contained
weasyprint manuscript.html manuscript.pdf
```

### preprint #15 v1.4 작성 시 §4.21 권장 골자

```
§4.21 R15 next-round triage
- BRICS 2 rounds → 38 unique candidates (R12_11 20, R12_23 11, R12_4 3, R13_13 4)
- R12_11 ↔ R14_5 SMILES 완전 중복 finding
- xtb HOMO-LUMO gap distribution (electronic stability)
- ADMET filter: triple-safe (AMES+hERG+DILI <0.3) → 단 1개 (chromanol fragment)
- Composite score formula 정의

§4.21.1 외용 lead path (skin window OK, hERG monitoring)
- Top-3 by composite score (R12_4 dimer, R13_13 prenyl, R12_11 methoxy)
- chromanol Boltz-2 cofold 14-target affinity matrix
- vs PIH ranked top → next-round MD candidates

§4.21.2 Systemic lead path (clean tox, hydrophilic)
- chromanol fragment 단독 분석
- 향후 prodrug 변형 가능성 (skin permeation 향상)
- 14-target affinity matrix → 후보 우선순위

§4.21.3 Honest limitation
- Boltz-2 affinity = ChEMBL R=-0.453 calibrated, IC50 nM 직접 변환 안 됨
- 38 → 1 triple-safe는 strict cutoff (0.3) 결과 — 0.5 cutoff 시 5+개로 확장됨
- skin_window 정의 (logP 1.5-3.5)는 Lipinski 외 추가 heuristic, 외용 임상 데이터 caveat
```

---

**최종 push**: `a5b3d66` (origin/main)
**진행 중**: GPU batch2 4/5 + chromanol cofold (ETA 12:05)
**다음 wakeup**: 12:05 KST (autonomous-loop-dynamic)
