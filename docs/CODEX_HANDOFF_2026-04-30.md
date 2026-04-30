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
