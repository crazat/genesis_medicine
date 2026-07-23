# CLAUDE.md — Genesis_Medicine v3 (Skin Regeneration)

> Claude Code가 세션 시작 시 자동 로드하는 프로젝트 가이드.
> 세부 설계: `docs/ARCHITECTURE.md` · 라이선스: `docs/LICENSING.md`

---

## 🎯 프로젝트 목적 (2026-04-25 재정의)

**한약·생약·신물질로 피부 건강과 피부-연계 건강을 개선하는 신약 개발 파이프라인.**

### 포지셔닝 — 3-Pillar 통합 사업 구조 (2026-04-26 확정)

| Entity | 유형 | 역할 |
|---|---|---|
| **HAN PREDICT, Inc.** ([hanpredict.com](https://hanpredict.com)) | AI 헬스케어 플랫폼 (founder: HanCheongWoo) | Clinic CRM, Smart Charts AI EHR, Marketing AI, NutriDocH, AI Studio + facial_dx Station Kit (개발 중) |
| **Recover 한의원** | 한방 의료기관 (강남, 2026-08-15 개원) | 한의 피부재생 임상 vertical, <https://recover-clinic.kr> |
| **Genesis_Medicine** | R&D Lab (이 코드베이스) | AI in silico 신약 발굴 + 한약 분자 메커니즘 |

- 핵심 슬로건: "만드는 미용이 아닌, 되돌리는 미용" (Recover)
- 기존 무기: 새살침, 체질 한약 처방, 약침, 매선, 고주파/프락셔널, AI 안면 분석 (HAN PREDICT facial_dx)
- 본 파이프라인의 역할: **임상 경험칙 → 분자 수준 메커니즘 규명 → 신약/외용제 후보 도출** (Genesis_Medicine)
- **3-pillar 시너지**: 임상(Recover) → 진단(HAN PREDICT) → 분자(Genesis_Medicine) 통합 데이터 루프
- **Affiliation 표준** (모든 preprint·peer-review): byline = "HanCheongWoo ¹,²,³"
  - ¹ Genesis_Medicine Lab, Seoul, Republic of Korea
  - ² HAN PREDICT, Inc. (hanpredict.com)
  - ³ Recover Korean Medicine Clinic (recover-clinic.kr)

### 타겟 질환 (우선순위)
| 순위 | 질환 | 핵심 분자 타겟 | 대표 한약/천연물 |
|---|---|---|---|
| 🥇 | **흉터 재생** (여드름/위축/비후/켈로이드) | TGF-β1/Smad, MMP-1/3/9, COL1A1/3A1, CTGF, LOX, VEGF | 센텔라(아시아티코사이드/마데카소사이드), 자근(시코닌), 당귀, 자운고 |
| 🥈 | **색소/기미** | Tyrosinase (TYR), MITF, TRP-1/2 (DCT) | 감초(licochalcone/glabridin), 녹차(EGCG), 닥나무(kojic acid), 상백피 |
| 🥉 | **탈모** (AGA) | SRD5A1/2 (5α-reductase), AR, Wnt10b, β-catenin | 하수오, 측백엽, 황기, 인삼(ginsenoside Rg1) |
| 4 | **여드름** | 5α-reductase, AR, SREBP1, C. acnes | 황련(berberine), 감초(licochalcone A), 황금 |
| 5 | **광노화/안티에이징** | MMP-1, SIRT1, Elastin, FBN1, mTOR | 녹차(EGCG), 황기, resveratrol 계열 |
| 6 | **아토피·건선** | JAK1/3, IL-4Rα, IL-13, TSLP, IL-17/23, PDE4 | 황련해독탕 구성, 방풍통성산 |
| 7 | **홍조/민감·만성 염증** | Cathelicidin, PAR-2, TRPV1, COX-2 | 감초, 병풀, 카모마일 |

### 생산물 (3가지 사업 형태)
1. **외용제/화장품** — 센텔라 scaffold 최적화 유사체, 기미 미백 복합, 탈모 두피 외용.
2. **내복 한약 복합처방** — 체질별·질환별 맞춤 (클리닉 처방 근거 강화).
3. **임상 증거 데이터베이스** — 각 약재·성분의 피부 타겟 기전 정량 정리.

---

## 🎯 NEXT ACTIONS — 다음 세션에서 바로 할 일

> 피부 중심으로 재설계. 사용자가 새 세션을 열면 이 목록부터 확인하고 **제일 위 항목을 먼저 제안**.

### 🔥 16-WEEK PREPRINT MASS-PRODUCTION + 의료법 방어 전략 (2026-04-26 확정)

**상세 plan**: `~/.claude/projects/-home-crazat-genesis-medicine/memory/project_preprint_strategy.md`

**전략적 의도 (사용자 명시 2026-04-26)**:
- **단기 4개월 (Recover 한의원 D-110 → 개원)**: preprint 8-12편 + peer-review 1-2편 in-review
- **중기 6-12개월**: peer-review 게재 + CRO Tier 1 wet-lab 결합
- **장기 1-3년**: 진짜 in silico 신약 개발지로 자리잡음 (preprint은 raw material)

**의료법 §56 + 화장품법 4중 방어**:
- L1: 모든 marketing claim에 DOI 인용
- L2: "in silico, IRB pending" disclaimer 표준화
- L3: GitHub Apache-2.0 + 모든 데이터 공개 (transparency shield)
- L4: 광고 카피 "효능 표시" → "연구 활동" 전환

**Marketing copy template (legal-safe)**:
- ❌ "AI가 발굴한 흉터 치료제 EMB-3"
- ✅ "Recover는 AI 신약 발굴 연구 N편 (DOI list)을 자체 수행하는 한의원입니다"

**16주 Preprint 일정 (12편 target)**:
| Wave | 주차 | 편수 | 내용 |
|---|---|:-:|---|
| 1 | W1-3 | 2편 | Embelia ribes review + Recover workflow |
| 2 | W4-7 | 5편 | 5 질환 case study (흉터/색소/탈모/여드름/광노화) |
| 3 | W8-11 | 4편 | ABFE methodology + IPF cross-disease + 자오류주 + Korean PGx |
| 4 | W12-14 | 1편 | Open-source 50도구 통합 perspective |
| 5 | W15-16 | — | 2편 peer-review submission (Phytomedicine + J Cheminform) |

**플랫폼 분배**: ChemRxiv (methodology), bioRxiv (생물·한약), medRxiv (임상 workflow)

**Quality 안전선**:
- TRIPOD-AI 27 항목 supplementary 첨부
- "in silico only, wet-lab pending" abstract 마지막 문장
- 자운고 narrative 철회 + Embelia ribes 정직 (`docs/EMBELIN_LITERATURE_REVIEW.md`)
- ADMET·Boltz-2·ABFE 한계 모두 명시
- 외부 인용 70%+ (자기 인용 회피)

**현재 진행 (2026-04-26 단일 세션 완료)**:

### ✅ 12편 preprint v0.1/v0.2 모두 작성 완료 + 19 figures + 12 PDFs
**총 ~28,500 단어 main text + 19 publication-quality figures (300 DPI) + 12 self-contained PDFs (~6.5 MB).**

| # | Preprint | 상태 | Real data 출처 | Figures |
|:-:|---|---|---|:-:|
| 1 | Embelia ribes review | ✅ v0.2 (자운고 정정) | literature only | 1 |
| 2 | Recover workflow | ✅ v0.1 honest | architecture | 2 |
| 3 | EMB-3 case study | ✅ v0.2 (cross-disease 정정) | scaffold-hop + SAR panel + Round 1-3 | 3 |
| 4 | Pigmentation | ✅ v0.2 | `pilot/screen/pigmentation/screen_results.csv` | 2 |
| 5 | Alopecia | ✅ v0.2 | `pilot/screen/alopecia/screen_results.csv` | 2 |
| 6 | Acne | ✅ v0.2 | `pilot/screen/acne/screen_results.csv` | 2 |
| 7 | Photoaging | ✅ v0.2 | `pilot/screen/photoaging/screen_results.csv` | 2 |
| 8 | ABFE methodology | ⏸ T4L 진행 중 | `pilot/calibration/t4l_benzene/` (~3-4h 남음) | 0 |
| 9 | Cross-disease IPF | ✅ v0.2 | `pilot/open_targets/` (real GraphQL queries) | 2 |
| 10 | Chronotherapy 자오류주 | ✅ v0.1 | conceptual framework | 1 |
| 11 | Korean PGx | ✅ v0.1 | panel design | 1 |
| 12 | 50-tool pipeline | ✅ v0.1 | resource paper | 1 |

### ✅ 사용자 audit 통과 — 정직 데이터만
- v0.1에 fabricated table 5편 (#4-7, #9) 발견 → **A안 (실제 screen 후 정정)** 채택
- 4 disease screens 실행 완료 (60 cofolds × 4 = 240 Boltz-2 cofolds + ADMET-AI)
- Open Targets v4 GraphQL forward + reverse queries 실측
- 모든 preprint v0.2에서 fabricated 값 **0개**, retraction 명시

### 🔄 진행 중 — **2026-07-23 KST 핸드오프 (현재 상태, 최우선 참조)**

> 새 세션은 이 블록을 먼저 읽는다. 아래 2026-06-16 블록은 데몬 스택·standing 룰만 유효(운영 레퍼런스), paper 상태는 여기로 대체됨.

- 🚨 **조작 패널 대청소** (2026-07-16 발각 → 07-21 대부분 완료). `data/chembl_mmp1_calibration.csv`(15행)는 이전 세션이 만든 날조 — 이름·IC50·인용 전부 허구, 15중14 PubChem 미등록. paper_A/B + Zenodo 발표 다수 오염. **재현성 주장은 전부 생존**(연산 정직, 라벨만 허구); 죽는 것 = 정체·IC50·SAR·repositioning. 전체 지도 [[project_fabricated_calibration_panel_2026_07_16]].
  - **코드 배선 제거(07-21)**: csv → `data/chembl_mmp1_calibration.WITHDRAWN.csv`(모든 result-consumer fail-loud), Snakefile `COMPOUND_LIBS`+`chembl_calibration` rule / dvc stage 삭제. forensic(`verify_panel_identity_pubchem.py`)·anchor pilot_rho만 WITHDRAWN repoint. 구조 필요 소비자 대체 = `data/mmp1_panel_pubchem.csv`(121 실화합물, CID/AID/timestamp). **원칙: fabricated로 다루면 WITHDRAWN, real로 다루면 fail-loud, 조용한 real-panel 스왑 금지(=재유입).** 사유 = `data/chembl_mmp1_calibration.README_WITHDRAWN.md`.
  - **발표 정정**: #20/21/22 supersede 완료(2026-07-19). dangling-citation 7편(#3/4/5/8/12/13/15) 재발행(Zenodo 21466637/42/45/48/49/53/56); **#8 이중정정**(21466392가 §3.6 철회하고도 "still calibrated" 잔존 → 21466648). VIII `20018254`(08_abfe)·XXVI `20247828`(paper_A v6) supersede **완료(2026-07-21: 21466392 / 21466405 제목변경, 업로드 로그 확인)** = `_metadata/DEPOSIT_CORRECTION_PACKAGE_2026_07_21_records_VIII_XXVI.md`. 오염 발행본 정정 전건 종료. [[project_deposit_correction_2026_07_18]].
  - **JCIM은 심사 아님**: ci-2026-01786n = 편집실이 2026-06-03 unsubmitted(참고문헌 누락·제목변경·SI 미업로드), 재제출 없음 → **계류 원고 없음. "under review" 오기**.
- 🔻 **paper_A v6 서사 무효**: r=0.9146 / Indapamide·Vorinostat repositioning = 화합물 오식별(CHEMBL406≠인다파미드, CHEMBL98≠vorinostat)로 폐기 → **v0.3 reproducibility 재구성**(`manuscript_v0.3_reproducibility.md`, 정체·역가 무주장, 제목·figure 교체). [[project_paperA_section46_not_reproducible_2026_07_16]]. anchor 2종 분리: |ρ|≈0.72(n=15 날조)=무효 vs R=−0.453(n=93 실 ChEMBL API)=실재·재현.
- ✅ **ABFE real-panel 캠페인 완료 + paper_A_zaff 최종화(14/14, 2026-07-23)**: 14화합물 MMP-1 실 IC50(0.78 nM–98 µM, PubChem CID/AID). Spearman(dG_ABFE,dG_exp)=0.587 CI[0.041,0.847], Pearson 0.631, sign-flip 0, **14개 전부 과결합**(dev −0.6~−58.1). warhead-driven 확증(strong ≤10 nM hydroxamate 평균 dev −53.0 vs phosphonate 77 nM −4.3; 약역가 hydroxamate cid10303333 50 µM이 dev −43.2 = 측정 역가 아닌 킬레이션 세기가 과결합 유발) = "reproducibility≠accuracy" 실화합물 실증. warhead는 실 SMILES SMARTS 분류(hydroxamate 11/carboxylate 2/phosphonate 1). **최종본** = `manuscript_v1_realpanel_accuracy.md`(+PDF, 그림 2개; 실 패널 정확성 축으로 전면 재구성, 다중-rep 재현성 서사→within-run 정밀도≠정확성으로 축소, 파이프라인 방법론 유지). 구 `manuscript.tex`=SUPERSEDED 표시(quarantine 해제). LaTeX 엔진 없어 pandoc+weasyprint md 워크플로. 결과=`pilot/abfe_realpanel_mmp1/abfe_realpanel_{results.csv,summary.json}`, 재현 스크립트=`scripts/zaff_realpanel_manuscript_figures.py`. **신규 Zenodo deposit**(기존 DOI 없음) 업로드 프롬프트=`_metadata/ZENODO_UPLOAD_AGENT_PROMPT_paperA_zaff_2026_07_23.md`(실제 업로드는 저자 몫). [[project_deposit_correction_2026_07_18]].
- 🧷 **git**: Plan A(날조 remediation + deposit 정정 소스, 대용량 데이터 .gitignore/DVC) = c82d3e2 push 완료(origin/main). 이번 세션 paper_A_zaff 최종화 산출물은 별도 커밋.

### 🔄 진행 중 (백그라운드) — **2026-06-16 KST 핸드오프 (데몬 스택·standing 룰 = 운영 레퍼런스로 유효; ⚠️ 현재 상태·paper 상태는 위 2026-07-21 블록으로 대체)**

> 이 섹션은 대화 핸드오프용. 새 세션 시작 시 가장 먼저 확인. 활성 PID/task-ID는 시간 지나면 stale → 항상 데몬 alive를 cmdline-exact 매칭으로 재검증(아래 self-match trap 룰).
> **현재 = 완전 자율 24/7 ROI 운영**(paper_A/B publish 완료, de novo MMP-1 발굴=paper4 active). 사용자 지시 대기 아님 — floor·explore·GPU 무중단 가동이 본인 핵심 역할.

#### ★ 자율 운영 데몬 스택 (2026-06-16, 모두 setsid-detached, **재부팅 relaunch 순서 = watchdog→supervisor→autopilot→sweetspot→feeder→watcher**)
경로: `scripts/round27_paperA/`. 각 데몬 alive 확인은 PID 순회 + `/proc/$p/cmdline` exact-prefix 매칭(`*"/bin/bash -c"*` 래퍼 제외 = self-match trap 방지).
1. **gpu_vram_watchdog.sh** — OOM hard-backstop. `free<6GB`를 **torch.cuda.mem_get_info(드라이버 ground-truth)로 confirm 후에만** boltz resume 재시작(numeric SIGKILL). nvidia-smi `memory.free`는 WSL2 artifact라 단독 신뢰 금지.
2. **gpu_roi_supervisor.sh (v4)** — queue-driven tier rotation, 2-explore boltz cofold 회전.
3. **tier_autopilot.sh** — slot E/F 큐 refill(ACQ/GEN planner).
4. **sweetspot_ledger_loop.sh** — ROI sweet-spot 컨트롤러(advisory, R11; [[project_roi_controller_r11_2026_06_13]]).
5. **floor_sigma_feeder.sh** — exploit floor(cores 0-18) **σ_E/σ_G 32-조건 robustness 그리드**(아래 ★★ = floor never-idle durable fix).
6. **autonomous_watcher.sh** — event-driven incident detector. `Bash run_in_background:true`로 launch(EXIT→harness가 LLM 재호출). 45s cheap 체크, 실 anomaly 지속 or 6h self-refresh에만 exit. healthy면 LLM 0발화. 죽으면(6h heartbeat 포함) exit reason 읽고 **중복 가드 후 재기동**. backstop = 시간당 cron `<<autonomous-loop>>`.

#### ★ GPU (explore, cores 19-23) — de novo MMP-1 cofold 캐스케이드
- 현재 tier **t127/t128**(slot E/F), `diffusion_samples 32 --num_workers 0 --max_parallel_samples 1 --use_potentials`.
- **OOM 방어**: env `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True,garbage_collection_threshold:0.8`. 검증 시 used ~1.7GB/free ~30GB headroom(2-explore라 여유 큼). 단편화 누적이 진짜 OOM 원인이므로 expandable_segments 필수([[feedback_boltz_vram_driven_by_num_workers]]).
- GPU resume = **지속 상태**: PAUSE만 명시 필요, CONTINUE 재허락 불요([[feedback_gpu_resume_is_standing_state_2026_06_07]]).

#### ★★ Floor (exploit, cores 0-18) — floor_sigma_feeder.sh = **32-조건 σ_E/σ_G robustness 그리드** (floor never-idle durable fix)
- 사용자 "cpu 노나" 6회 끝에 도달한 근본 해법. 교훈: **rung 깊이(SP→OPT→OHESS)도, 조건 width-4도 GPU 율속을 못 이겨 유한 cohort 결국 소진→floor idle**.
- 해법 = paper_A §4.13이 실제 요구하는 **전체 매트릭스**: `{GFN2,GFN1}×{GBSA,ALPB}×{8 solvent: water·dmso·methanol·acetonitrile·acetone·thf·chcl3·toluene, ε 2.4~80} = 32 셀`. 전부 진짜 robustness 표 셀(GBSA↔ALPB 교차검증 + GFN level-of-theory + solvent 극성 강건성), **NOT Goodhart**.
- 셀별 3-stage ASHA: SP-survivor(σ_E≤2.0) → OPT σ_E → OHESS σ_G(tight cohort σ_E≤0.5, 자유에너지=paper4 열역학 신규축). water 4셀=legacy 파일명 보존, non-water=`phase2_denovo_sigmaE_{opt,ohess}_gfn{G}_{solv}_{sm}.shard*.csv`. SOLVMODEL env(gbsa/alpb).
- self-sustaining: GPU가 신규후보 cofold→SP 게이팅→survivor↑→32셀 자동 fresh work. **feeder PID 2개 정상**(메인루프 + `cell=$(run_cell)` command-subst 서브셸=부모자식, 중복 아님 — 죽이지 말 것).
- watcher 의미: floor 건강도 = **feeder 데몬 alive**(순간 xtb=0은 burst 사이 정상). 상세 [[project_claim_ledger_noisefloor_r12_2026_06_13]].

#### ★ Paper 상태 (2026-06-16)
- **paper_A v6 (#23)**: publish 완료. R12 claim-ledger σ_E 방어 통합 — §4.12 numeric-reproducibility floor(signal/floor 7M–813M×), §4.13 GBSA↔ALPB cross-val(pooled ρ 0.889·GFN2 11셀 ρ≥0.92), §4.14 optimizer's-curse(DEFUSED).
- **paper_B v1 (#24)**: σ_iptm reliability + dual-axis outlier; §3.7 conformal + §3.8 ICC + §3.9 optimizer's-curse 3-footing 방어.
- **paper4 (de novo MMP-1 발굴, active)**: REINVENT 생성→ADMET 필터→Boltz σ_iptm + xtb σ_E/σ_G 신뢰성 게이팅. exploit-explore 균형의 explore 트랙([[project_denovo_mmp1_discovery_2026_06_08]]).
- 의사결정 = `scripts/round27_paperA/paper_claim_ledger.py`(proxy 아닌 Σ P(채택)×impact 최적화).

#### ★ 최우선 standing 룰 (위반 시 사용자 강한 불만 이력)
- 🚨🚨 **OOM 절대금지 = #1**. nvidia-smi 단독 kill 금지, 항상 torch.cuda.mem_get_info 교차검증([[feedback_wsl2_nvidia_smi_memory_artifact_2026_06_12]]).
- 🚨🚨 **자율 24/7 ROI 무중단 = 본인 핵심 역할**(지시 대기 아님). floor **절대 idle 금지**(condition-grid로 채움), 소진 시 "뭐 돌릴까" park-ask 금지·자율 ROI 선택. exploit(σ 매트릭스)+exploration(신규 분자 생성·스크리닝) 둘 다 가동([[feedback_exploit_explore_balance_2026_06_08]] [[feedback_autonomous_role_priority_2026_05_20]]).
- 🚨 **kill/pkill 금지**(자기 just-launched 예외, SIGTERM 내성 boltz엔 numeric -9). pgrep self-match trap: PID 순회+cmdline exact match.
- 🚨 보고 **한글**, 원고만 **영어**. frontier-tech 스캔은 **사용자 명령에만**(자율 큐잉 금지).
- 🚨 co-author 없음, 단독저자 Cheongwoo Han 자체제출, outreach 재제안 금지([[feedback_no_coauthors_solo_submit_2026_06_02]]).

---

> ⬇️ **아래 A–L 블록은 2026-05-20 핸드오프(historical, superseded)** — paper_A D-10/Boltz v161-180/PID 2900617 등은 모두 과거. 맥락 참조용으로만 보존.

#### A. paper_A v6 D-10 publish-ready — `preprints/23_paper_A_v6_mmp1_5nnp_xtb/` (Zenodo 2026-05-30)
- **manuscript_v0.2.md** 329 lines (Round-3 proofread 완료) — 0 placeholder, 0 broken xref, 5/5 figures cited, 79 references canonical (Wan vs Wang 정정 + ref 18 stale duplicate 제거 → v0.3.1)
- **핵심 narrative**: 3-NNP cross-val (Orb-v2 + MACE-OMol25 + Orb-v3) Pearson r=0.9146 [0.817, 0.973] top-4 identical rank (Indapamide→57058→94487→Vorinostat); 25-cycle Boltz-2 cofold ensemble (37,500 structures) PoseBusters v2 94.5% > PDBBind 89.2%; CHEMBL94487 σ_E 14.27→0.007 kcal/mol 2068× collapse; xtb GFN2 3-mode (gas/water-ALPB/ε=4.0)
- **sulfonamide-diuretic n=17 class extension** (Section 5.4): 0/17 quantitative MMP-1 IC50/Ki across thiazide/loop/CA-inhibitor subclasses; **Xipamide CHEMBL517199 top wet-lab candidate**; patent FTO (Lens+Google+Espacenet+USPTO 2026-05-19)
- **Open Targets Platform 26.03 EMA+PMDA cross-validation** (P0 audit 2026-05-20): 6-source independent corroboration of n=17 0/17 MMP-1; Zidapamide CHEMBL6378 OT absent flag; refs 77-79 추가
- **HDAC class extension** (Section 5.6): Belinostat + Givinostat (DMD axis, Bettica 2024 PMID 38508835) class-wide 0 MMP-1 quantitative + Mocetinostat/Entinostat benzamide negative controls
- 보조: cover_letter_zenodo_v0.1.md + references.md (v0.3.1, 79 refs) + figures/figure{1-5}.{png,pdf} + SI/Table_S5_README.md + SI/Table_S6_4engine_matrix_v19_vN.csv
- D-7 (5/23) co-author confirmation gate: SNUH Chung Jin Ho + Amorepacific NBRI + KAIST Kim Woo-Youn — single-author Zenodo fallback per memory #20-22 precedent if no response
- D-3 (5/27) figures final review · D-1 (5/29) InChI cross-check + Zenodo metadata · D-0 (5/30) Zenodo upload
- 메모리: `project_paper_a_v6_proofread_round1/round2/round3_2026_05_20.md` + `project_paper_a_v6_open_targets_audit_2026_05_20.md` + `project_sulfonamide_diuretic_n17_extension_2026_05_19.md`

#### B. paper_A v_index cascade — Boltz cofold v161→v180 widening (자율 진행 중, watcher PID 2900617)
- 패턴: Boltz vN done → chain v_v(N) cp+sed pattern v3 trigger (~12s cascade gap, [5-8] cache-hit ~0sec) → Boltz v(N+1) launch
- **현재 진행**: v174 PID 3154818 seed=1278 @~50min (8/15 ligands, GPU 100% 23GiB MEM), ETA done ~16:46 → cascade v175 fire
- **watcher**: `boltz_v171_v180_extension_watcher.sh` PID 2900617 elapsed 5h+, log at `scripts/round27_paperA/boltz_v171_v180_extension_watcher.log`
- **완료된 cycles 2026-05-20**: v171 (116.63min +44% contention outlier 9-chunk rdkit-Pool SIGKILL cleanup) / v172 (89.8min clean) / v173 (84.5min clean) → publishable: dedicated-envelope reproducibility 권장
- **paper_B σ_iptm n=28 dataset 완성** (v143-v170): 420-row CSV at `preprints/24_paper_B_v1_boltz_xtb_rescue_zn_mmp1/sigma_iptm_v143_v170.csv`
- **chain script gap discovery v130-v170 (41 cycles)**: `cpu_xtb_*_v19_v{N}.py` built only thru v129; v130-v170 chain master scripts silently NO-OP [1/8]-[4/8] = 41 cycles ran CONTENTION-FREE → -8.2% acceleration plateau = pure-Boltz reliability baseline (paper_B v0.2 narrative 핵심). 메모리: `project_paper_b_chain_script_gap_v130_v170.md`
- 자동 trigger 룰: `feedback_paper_a_vindex_cascade_pattern.md` + `feedback_cascade_watcher_robust_pattern.md`

#### C. xtb GFN2 SP batch v130-v170 41-cycle extension (paper_A SI Table_S6 보강, 자율 진행 중)
- 스크립트: `scripts/round27_paperA/xtb_batch_v130_v170_launcher.sh` PID 2903544 (3h+), MAX_CONCURRENT=6 rotation
- **wave-1 v130-v135 done** (1501 rows each, mtime 14:55-14:58) — 6/41 = 14.6%
- **wave-2 v136-v141 진행 중** (CSV flush 401 rows = 26% 표시, 실제 work-dirs 548+ = 37% 진짜 진행률; CSV flush every 200 rows lag)
- xtb 48 active procs (6 cycles × 8 workers), each xtb ~60-110s under wave-2 contention
- ETA full v130-v170 done: ~next day 08:30 (7 waves × ~3.3h each)
- 데이터: `pilot/round27_paperA/xtb_gfn2_ligand_v19_v{N}/xtb_gfn2_ligand_v19_v{N}.csv`
- Boltz cycle wall impact <+2% (v172=90min/v173=85min clean baseline preserved despite xtb batch)
- aggregator: `scripts/round27_paperA/aggregate_paperA_v6_SI_4engine_matrix.py` (107/119 full coverage from v19-v129, v130+ SP-only re-run pending)

#### D. paper_B v1 dual-axis σ-outlier rescue framework — 95% sprint readiness (post-D14 sprint, D14+0 = 2026-06-13)
- 위치: `preprints/24_paper_B_v1_boltz_xtb_rescue_zn_mmp1/manuscript_skeleton_v0.1.md` 240 lines
- **핵심 NEW finding**: dual-axis σ-outlier — **CHEMBL94487 σ_E** (xtb GFN2 SP energy) 14.27 kcal/mol → 0.007 (2068× collapse via xtb-OPT) + **CHEMBL259829 σ_iptm** (Boltz confidence) 0.0629 (35× spread vs CHEMBL57058 best 0.0018) — **orthogonal axes**, single-axis auditing misses one class
- 5-step protocol: aggregate r → per-ligand σ_E → per-ligand σ_iptm → axis-targeted rescue (σ_E → xtb-OPT, σ_iptm → PLACER+GatorAffinity triage) → wall CV baseline
- **완성 sections (D-10 자율 작성 분량)**: Abstract dual-axis precision + §1.1 Motivation (340w) + §1.2 Related Work (Wan UCL canonical) + §1.3 dual-axis correction + §2.9 chain gap methodological transparency + §3.2 σ_iptm 15-ligand rank table + §3.3 dual outlier case studies (3.3.1 CHEMBL94487 / 3.3.2 CHEMBL259829 / 3.3.3 framework table) + §3.5 plateau + v171 contention outlier footnote + §4.1 metalloprotein amp (330w) + §4.2 upstream QM (430w) + §4.3 reliability literature 4-strand positioning (580w) + §4.4 limitations (6 bullets 480w) + §5 5-step protocol
- 남은 placeholder (post-D14 sprint): §3.1 aggregate Pearson r table (ΔG_Boltz extraction script 필요) + §3.4 external validator data (GatorAffinity + PLACER runs 미시작)
- **prior art**: Wan S, Zhang X, Xue X, Coveney PV (UCL CCS) arXiv:2603.05532 38,482-compound 3CLPro+TNKS2 N=2 r=0.913/0.962 — paper_B = 14× deeper reseed (N=28) + Zn²⁺ metalloprotease + σ_iptm dimension + causal rescue
- 메모리: `project_paper_b_dual_axis_framework_2026_05_20.md` + `project_paper_b_sigma_iptm_n28_2026_05_20.md` + `project_paper_b_arxiv_2603_05532_prior_art.md` + `project_paper_b_section43_2026_05_20.md`

#### E. paper #19 v2 outline v0.1 — KMCRIC outreach 첨부 (2026-05-20 작성)
- 위치: `preprints/45_paper_19_v2_outline_kmcric/paper_19_v2_outline_v0.1.md`
- 4-layer analytical pipeline:
  1. **ADMET-AI 41-endpoint**: 86 Korean Pharmacopoeia herbal NP × paper_A v6 MMP-1 117-hydroxamate comparator (herbal QED 0.51 vs MMP-1 0.39; herbal AMES 0.37 vs MMP-1 0.77)
  2. **Claude-LLM 33-retron retrosynthesis**: 34/86 = 40% solved vs AiZynthFinder USPTO 0/86 (14/86 chemoenzymatic)
  3. **KIOM KORE-Map 1.1 transcriptomics**: 1,075 bulk RNA-seq × 4 cell × 4 dyspepsia 처방 + 단방 한약재; **KMCRIC alumni leverage path** via 이향숙 교수님 (사용자 석사 지도교수, KMCRIC 센터장)
  4. **MMP-1 mechanism overlay**: paper_A v6 framework cross-ref (Boltz-2 + xtb + 3-NNP)
- target: D14+14 (2026-06-13) Zenodo v0.2 skeleton, D14+30 (2026-06-29) v1.0 Journal of Ethnopharmacology
- KMCRIC outreach 한글 formal draft: `preprints/23_paper_A_v6_mmp1_5nnp_xtb/outreach/kmcric_lee_hyangsook_kore_map_intro_draft_2026_05_20.md` (D-9/-8 발송 권장, 95%+ success rate per 사용자 alumni 룰)
- 메모리: `user_kmcric_alumni_lee_hyangsook.md` + `project_round26_frontier_tech_2026_05_20.md` (#4 KORE-Map KILLER)

#### F. R26 frontier-tech scan 11 Tier-1 picks (2026-05-20, 사용자 직접 명령)
- **P0 완료**: Open Targets Platform 26.03 (paper_A v6 §5.4 Section + refs 78-80 + cover letter + SI README 통합 ✓)
- **P1 자율 진행 중**: KORE-Map 1.1 (paper_19 v2 outline 작성 ✓ + KMCRIC outreach draft ✓)
- **나머지 9 Tier-1 picks 대기**: Carterra Vega + ALiCE (wet-lab) + Prot2Chat (task #5 closure) + Boltz-2 MD vs AlphaFlow (task #4 closure) + Property Cliffs / AgenticPosesRanker / AMP-BMS-MM / HIRA K-OMOP / KRIBB K-Reverse Aging
- **사용자 명시 규칙**: "frontier-tech 신규기술 스캔은 사용자 명령에만" — overnight/auto 큐잉에서 자동 launch 금지 (`feedback_frontier_scan_user_initiated_only.md`)
- 메모리: `project_round26_frontier_tech_2026_05_20.md`

#### G. 활성 watcher / monitor / cascade infrastructure
- `bgackokko` (Monitor) — 10-min cadence compute heartbeat (GPU/load/Boltz/xtb/py19) — 정상
- `btcxr2nwn` (Monitor) — Boltz/disk/xtb death watch — 정상
- `boltz_v171_v180_extension_watcher.sh` PID 2900617 (5h+) — Boltz cascade v171→v180 sequential launcher (현재 v174 phase)
- `xtb_batch_v130_v170_launcher.sh` PID 2903544 (3h+) — xtb GFN2 SP wave rotation
- Wakeup cadence: 600-1800s (memory rule `feedback_monitoring_cadence_rule.md` 적용)
- **load 880-1000 = WSL2 thread-counting artifact** — actual progress 정상이면 무시 (`feedback_wsl2_load_thread_artifact.md`)

#### H. 활성 메모리 룰 (2026-05-20 신규 우선 + 기존 핵심)
- 🚨🚨 **자율 ROI 순 무중단 운영 = 본인 핵심 역할** (`feedback_autonomous_role_priority_2026_05_20.md`, 사용자 직접 명시): "너의 역할은 나의 지시를 기다리는게 아니라 ROI높은 순으로 계속 연산력 쉬지않고 운영"; default behavior 변경 (지시 대기 → 자율 launch); GPU<80% sustained 30s+ OR CPU load<nproc×0.85 catch 시 즉시 next ROI; 사용자 개입 시 즉시 조정
- 🚨 **GPU idle ≥10min autonomous cascade launch** (`feedback_gpu_idle_autonomous_launch.md`, 2026-05-20 10:14-23 사건): wake/overnight 무관 GPU 0% ≥10min 시 next cascade launch 의무 (paper_B n+10 extension 우선)
- 🚨 **WSL2 load thread-counting artifact** (`feedback_wsl2_load_thread_artifact.md`): load 988 보고 시 actual usage 정상 가능 (D state 0 + memory OK + workload progress 확인). load 단독으로 SIGKILL 금지
- 🚨 **사용자 보고는 한글, 논문 원고만 영어** (`feedback_korean_reporting_english_papers.md`, 2026-05-13)
- 🚨 **KST 22:00-10:00 12h 자율 큐잉**: ROI 순 cascade 자동 launch (`feedback_overnight_22to10_autonomous_queue.md`)
- 🚨 **사용자 "자동 스캔 정지" scope = frontier-tech만** (`feedback_user_scan_stop_scope.md`, 2026-05-17): Boltz cascade + 데드락 SIGKILL + chunks rolling은 별개 pre-authorized
- 🚨 **모니터링 cadence 600s default + 180-240s transition** (`feedback_monitoring_cadence_rule.md`); 5-min cache TTL 의식
- 🚨 **Schrödinger academic = Viewer only** (2026-05-13): paper_A v6 cross-validation 5도구 fallback
- 🚨 **fairchem 2.x API + HF gated repo 차단** (`feedback_fairchem_2x_api_hf_gated_2026_05_20.md`): facebook/OMol25/UMA HF gated 401, OCPCalculator → FAIRChemCalculator + pretrained_mlip; Meta FAIR access request 24-72h 대기
- 🚨 **AskUserQuestion 보수적 사용** (`feedback_autonomous_decision_priority.md`, 2026-05-15 명시): 메모리 룰 + 직전 사용자 의도 + 객관 evidence로 자율 진행; 외부 자원 1주+ 변화 / destructive action 직전 / 사용자 직접 의도 필수 / 메모리 룰 충돌 시에만
- 🚨 **cascade watcher 검증 의무 + setsid robust 패턴** (`feedback_cascade_watcher_robust_pattern.md`, 2026-05-16 v106 duplicate launch 사건)
- 🚨 **stale/phantom PID claim 검증 의무** (`feedback_stale_pid_claim_verification.md`, 2026-05-15)
- 🚨 **동일 status macro 4-time+ 1-line format** (`feedback_repeated_status_macro_1line.md`)
- 🚨 **ADMET-AI duplicate SMILES 100% crash** + **joblib 25-subworker overhead** + **chain×ADMET fair-share stage-dependent regression** (OPT 0.345 / HESS 0.21-0.28 / GFN-FF 0% cache-aware)
- 🚨 **10-min heartbeat insufficient for Boltz transition**: Boltz launch 후 ScheduleWakeup(ETA-2min) 의무
- 🚨 **MatterSim conda env path = miniforge3 NOT miniconda3** (`feedback_mattersim_conda_env_path.md`, 2026-05-18)
- 🚨 **chain xtb pool nice=19 + RDKit/ADMET fair-share** (RECORD 보전은 chain nice=0 또는 CPU mask isolation)
- 🚨 **rdkit Pool last-batch / mid-batch hot-zone deadlock = 5-7min SIGKILL rule** (98-99% partial publishable)
- 🚨 **cpu_heavy_rdkit_coconut SKIP range 검증 의무**: SKIP < csv total lines (lite-05-2026=738,828), 740-744k 사건 재발 방지
- **paper_A v_index cascade auto-trigger**: Boltz vN done = pre-authorized chain (`feedback_paper_a_vindex_cascade_pattern.md`)
- **Destructive action 명확 evidence 시 strong recommendation** (hedge 금지)
- **MEMORY.md size warning**: 110KB > 200줄 limit — 신규 entry는 200자 이하 one-liner, 본문은 topic file로

#### I. Preprint publication 누적 (2026-05-20 기준)
- **20 Zenodo DOIs published 2026-05-04+05-15** (papers #01-18+#43, #20 paper_A v5h, #21 paper_B v0.1, #22 paper_C v0.1)
- **paper_A v6 (#23) Zenodo D-10 2026-05-30 publish-ready** ✓
- **paper_B v1 (#24) post-D14 sprint 2026-06-13 target** (95% sprint readiness)
- **paper #19 v2 outline (#45) — KMCRIC outreach 첨부** ✓ (2026-05-20 작성)
- medRxiv pending: #02 recover_workflow + #11 korean_pgx_topical
- **bioRxiv/ChemRxiv door closed** for in-silico-only (26 rejection events); wet-lab v1.0 → 재시도 long-game
- 메모리: `project_preprint_publication_status.md`

#### J. Recover 한의원 홈페이지 (recover-clinic.kr/research) 업데이트 권장 (사용자 2026-05-20 검토 요청)
- 현재 표 25건 (Preprint 11 + Tech Report 9 + Framework 4 + In Prep 1), 마지막 업데이트 "2026년" 막연
- **Tier-1 즉시 추가**: paper_A v6 (D-0 5/30 publish) + paper_B v1 (post-D14) + paper #19 v2 outline
- **Tier-2 누락 publish papers**: IX/X/XI/XII/XIII/XVIII/XIX (paper #09/10/11/12/13/18/19) — Roman numeral gap 있음
- **Tier-3 narrative 보강**: Program A에 "Indapamide 재포지셔닝 + sulfonamide-diuretic class extension + Open Targets EMA+PMDA audit" 추가; 협업 모집에 "KMCRIC ↔ KIOM KORE-Map 1.1" 추가; ORCID 표기 "한정우 vs 한청우" 한자/한글 확인 필요
- **Tier-4 publishable findings 인용 가능**: CHEMBL94487 2068× σ_E collapse + CHEMBL259829 σ_iptm 35× spread + wall CV 3.8% + r=0.9146 [0.817, 0.973] + PoseBusters 94.5% + LigandMPNN Zn 95.3%

#### K. paper_A round27 신규 검증 publishable findings (cycle 43-174+)
- 🏆 **C95 chain TOTAL 47.13min ALL-TIME RECORD** (2026-05-15, vs C62 -11%) — `project_paper_a_c95_record_2026_05_15.md`
- **[5-8] full cache-hit mechanism**: v19_v80 cached → GFN1 SP/MMFF94/UFF/cleanup 4-stage instant
- **GFN-FF NOT immune to py19 RDKit**: +6.5% under 14-worker pressure → cache-aware vs cache-unaware fair-share dimension 분리
- **15-cycle SUSTAINED baseline (C78-C92)**: SP 20.88s±0.4 / OPT 12.06min±0.05 / HESS 21.44min±0.20 / GFN-FF 10.78min±0.11
- **stage-dependent fair-share regression** (C93+C94): OPT coeff 0.345 (CV 0.6%), HESS 0.21-0.28
- **15-cycle clean wall CV 3.8%** (88.4 ± 3.4 min) — paper_B reproducibility infrastructure baseline
- **n=10 plateau v161-v170 = 81.17 min (-8.2% acceleration)** — paper_B narrative 핵심 (post-chain-script-gap contention-free)
- **v171 contention outlier 116.63 min (+44%)** — 9-chunk rdkit-Pool SIGKILL evidence → dedicated-envelope reproducibility 권장
- **OMol25 paradox** (paper_A v4): xtb-OMat r=0.976 vs xtb-OMol25 r=0.773
- **Boltz-2x physicality-steering quantified**: v15→v16 mean Δiptm -0.22%, 5/15 IMPROVED, 2/15 dropped (CHEMBL259829 -2.4%)
- **dual-axis σ-outlier orthogonality** (paper_B v1): CHEMBL94487 σ_E vs CHEMBL259829 σ_iptm — single-axis auditing misses one class
- **LigandMPNN Zn metal recovery** (paper_C): 95.3% vs ProtMPNN 46.4% on 1HFC
- **n=17 sulfonamide-diuretic 0/17 MMP-1 quantitative un-testing** + Open Targets 26.03 EMA+PMDA 6-source corroboration
- **paper #19 Claude-LLM retrosynthesis 34/86 (40%)** vs AiZynthFinder USPTO 0/86 — Korean herbal NP synthesis-accessibility gap closure

#### L. 4-paper concurrent track 상태 요약
| paper | 위치 | 상태 | 다음 마일스톤 |
|---|---|---|---|
| **#23 paper_A v6** | `preprints/23_paper_A_v6_mmp1_5nnp_xtb/` | ✅ D-10 publish-ready (manuscript 329 lines, 79 refs, 5 figures cited) | D-0 5/30 Zenodo upload |
| **#24 paper_B v1** | `preprints/24_paper_B_v1_boltz_xtb_rescue_zn_mmp1/` | 95% sprint readiness (manuscript 240 lines, dual-axis framework integrated) | post-D14 (6/13) §3.1 + §3.4 데이터 fill |
| **#45 paper #19 v2** | `preprints/45_paper_19_v2_outline_kmcric/` | 1-page outline v0.1 (KMCRIC outreach 첨부용) | D14+14 (6/13) v0.2 skeleton, D14+30 (6/29) v1.0 |
| **#22 paper_C** | `preprints/22_paper_C_zn_metallohydrolase_denovo_pipeline/` | v0.1 published 2026-05-15 (Zenodo 10.5281/zenodo.20134447) | LigandMPNN-RFdiff3 wet-lab cycle |

**🚫 STALE 주의 (이전 세션 macro 패턴)**:
- "cycle 95/96" — 현재는 cycle 174+ (paper_A v_index Boltz v161→v180 widening)
- "PID 2941 / 4731" — 옛 ABFE/chain PID 환각, 현재 cascade는 PID 2900617 (watcher) + 2903544 (xtb batch) + 3154818 (v174)
- "COCONUT NP DB 96-268k" — 그 phase 종료, 현재는 paper_B σ_iptm n=28 + xtb batch v130-v170
- "Chrome agent Zenodo Web UI" — 새 paper_A v6 deposit는 D-0 5/30에 사용자 직접 진행
- "20 Zenodo published" — 곧 23 (paper_A v6 add)

### 📋 Quality 검증 통과 항목
- TRIPOD-AI 호환 limitation sections
- Embelia ribes / 자운고 chemistry-based 정정 (`docs/EMBELIN_LITERATURE_REVIEW.md`)
- MMP-1 zinc handling caveat 명시
- Boltz-2 binary classifier vs IC₅₀ 구분
- Earlier ABFE -32.90 explicitly retracted (#8 §3.5)
- Berberine hERG 0.977 critical safety disclosure (#6)
- 모든 cross-disease 86%/100% claim retracted → real OT 1/26 (PDGFRB only)

### 🎯 즉시 가능 (사용자 다음 액션)
1. **계정 등록** (총 30분): ORCID + bioRxiv + medRxiv + ChemRxiv
2. **Preprint 검토 + 업로드**: 각 `preprints/<NN>/manuscript.pdf` 그대로 제출 가능
3. **Recover 홈페이지** RESEARCH 페이지: `manuscript.html` 자체 게재 가능
4. **상세 plan**: `docs/PREPRINT_SUBMISSION_GUIDE.md` (8 sections, 16주 timeline)

### 📦 산출물 위치
```
preprints/<NN_dir>/
├── manuscript.md      # markdown source
├── manuscript.html    # self-contained HTML (base64 embedded images)
├── manuscript.pdf     # publication PDF (figures inline)
└── figures/*.png      # 300 DPI raw figures

docs/
├── PAPER_PLAN.md
├── PREPRINT_SUBMISSION_GUIDE.md
├── EMBELIN_LITERATURE_REVIEW.md
├── CRO_TIER1_DECISION.md
└── MFDS_K_BIO_LANDSCAPE.md
```

**확률 (정직 calibrated)**:
- 11편 즉시 제출 가능 (#8 제외): 95% (만들어졌고 PDF까지 완성)
- 12편 등재 (T4L 통과 후 #8 합류 시): 90%
- Peer-review 1편 게재: 35% (12개월)
- 의료법 민원 방어 가능: 85% (disclaimer 유지 시)
- 의약화학·임상 reviewer rigor 통과: 50–65% (영문 교정 + 외부 collaborator 시 ↑)

---

### ✅ 완료 (2026-04-25, 피부 재편 이전)
- 인프라 구축: 라이선스 게이트(83 컴포넌트, 118 테스트), 11단계 아키텍처, 가속 스택(cuEq 0.10 + boltz-blackwell), genesis-md conda env(openmm+openff+mace), TxGNN env(py3.9+DGL2.4).
- **방법론 검증 완료** — 아래는 인프라 validation 용도로 가치는 있으나 **사업 방향과 무관**:
  - Boltz-2 BACE1 affinity (AD 9개 화합물, 241s, pIC50 6.8-8.5)
  - ADMET-AI v2 (9+15 화합물, 41 endpoints)
  - CHEMBL230245 10 ns MD (RMSD 2.57 Å, 1484 ns/day)
  - TxGNN AD 재창출 (1801 × 6 subtype, Aceclidine 최상위)
  - NSCLC EGFR TKI (5개 TKI pIC50 7.5-8.7, 인프라 범용성)
  - NSCLC/Parkinson Open Targets (시드 10/14 hit, AFDB 10/10)

### ✅ 완료 (2026-04-25 ~ 2026-04-26)
- 피부 5질환 파일럿 (흉터/색소/탈모/여드름/광노화) — 102 화합물 × 14 타겟
- EGCG 단독 paper (5/5 disease + MD 1.45 Å, 외용 universal compound 가설)
- Embelin scaffold-hop → **EMB-3** (hERG 0.40→0.16, MD 0.79 Å, MMP1 affinity 유지)
- Network 27 cofold + cross-disease 18 fibrosis indication (IPF 6/7, scleroderma 7/7)
- ABFE EMB-3 × MMP-1 정량화 (openmmtools 16 windows × 5 ns × 17 replicas, 진행 중)
- Embelin baseline ABFE 병렬 실행 (ΔΔG 정량 비교)
- 한약 매핑 (자운고 + EMB-3 강화 1순위 권장)
- CRO 견적 (Tier 1 ₩1,560만 / 6-10주, 전체 ₩4,775만)

### ✅ 완료 (2026-04-27 22:20, Tier B SOTA audit 11개 통합 — "세계 최고" sweep)
**광범위 외부 SOTA 조사 + 내부 cross-verify 결과 식별된 11개 gap 일괄 통합**:

| # | 도구 | 위치 | License | 상태 |
|---|---|---|---|---|
| 1 | Protenix-v2 (ByteDance, 2026-04-08) | `external_tools/protenix_v2/` (152MB clone) + `structure/protenix_adapter.py` engine_version 갱신 | Apache-2.0 ✅ | 통합됨 |
| 2 | g-xTB / NN-xTB (Grimme 2025) | `md/gxtb_adapter.py` graceful + LicenseGate research | Grimme academic | scaffold 완성, binary install 필요 |
| 3 | OSP MoBi Dancik skin PBPK | `dermatology/skin_pbpk_dancik.py` 자체 4-layer ODE 구현 + LGBM logKp head slot | Method commercial-safe | EMB-3 logKp=-2.39 검증 |
| 4 | AceFF v2 (Acellera, 2026-01) | `md/aceff_adapter.py` openmm-ml 호환 | MIT ✅ | scaffold 완성 |
| 5 | PocketXMol (Cell 2026) | `external_tools/pocketxmol/` (16MB) + `structure/pocketxmol_adapter.py` (small_molecule + cyclic_peptide + linker + PROTAC modes) | MIT ✅ | 통합됨, 약침 cyclic 모드 |
| 6 | SiteAF3 (PNAS 2026) | `structure/siteaf3_adapter.py` LicenseGate research | TBD | scaffold (라이선스 미확정) |
| 7 | Multi-fidelity BO cascade (ACS Cent Sci 2025) | `optimization/multi_fidelity_bo.py` + `scripts/cpu_multi_fidelity_bo_demo.py` | Method commercial-safe | 자체 구현, GP cascade 검증 |
| 8 | scPrimeKG + CellAwareGNN (bioRxiv 2026-02) | `knowledge_graph/scprimekg_adapter.py` | MIT (likely) | scaffold + cell-type-conditioned scoring |
| 9 | NPASS 2026 update (NAR 2026) | `ethnobotany/npass_2026_adapter.py` + `cache/npass2026/` | Free academic+commercial | 로더 + skin-permeable query + LGBM training set export |
| 10 | Pilosebaceous unit atlas (bioRxiv 2025-09) | `transcriptomics/pilosebaceous_atlas.py` | CC-BY 4.0 | 7 cell type catalog + AR/PIEZO1/MYLK 발현 검증 |
| 11 | PIEZO1/MLCK + PAR-2/GR 신규 타겟 | `conf/skin_targets/alopecia.yaml` (PIEZO1+MYLK) + `conf/skin_targets/pigment.yaml` (F2RL1+NR3C1) | conf only | 통합됨 |

**검증 결과** (`python -c "import all 9..."`):
- ✅ 9 신규 어댑터 모두 import OK
- ✅ License registry 83 → 95 components (+12)
- ✅ Dancik EMB-3 logKp = -2.39 cm/s (외용 적합), flux_ss = 1464 µg/cm²/h
- ✅ Pilosebaceous atlas: AR → dermal papilla 71% (생물학적 정확)
- ✅ Multi-fidelity BO: GP cascade 작동, cost-aware acquisition

**라이선스 분기**:
- commercial-safe (8개): Protenix-v2, PocketXMol, AceFF, Dancik (자체 구현), Multi-fidelity BO, NPASS 2026, scPrimeKG, Pilosebaceous atlas
- research-only (3개): g-xTB (Grimme), NN-xTB (Grimme), SiteAF3 (가중치 NC?)

**즉시 가능 신규 paper 2편 (preprint #13, #14)**:
- #13: PIEZO1/MLCK mechanotransduction in AGA (Nat Commun 2026 cite + 자체 Boltz-2 cofold)
- #14: Topical PBPK for natural-product-inspired skin therapeutics (Dancik + SkinPiX + 자체 LGBM)

### ✅ 완료 (2026-04-27, Round 12 + Round 13 + R5)
**핵심 paper-tier 산출물**:
- **MD top-5 lead ensemble** (10 ns × 5, RTX 5090): r3_6 × TGFB1 0.86 Å, β-sitosterol × AR 0.88 Å, shikonin × CTGF 1.24 Å, chlorogenic × SIRT1 1.61 Å, azelaic × TYRP1 1.71 Å — **모두 paper-tier 안정**
- **R5 cofold expansion**: 1877 → 2077 rows (TGFB1+CTGF +200), R5 phase 2 (AR/SIRT1/LOX/MITF) 진행 중
- **ChEMBL Boltz-2 calibration**: Pearson R = -0.453 (n=93), paper #8 결정 수치
- **PoseBusters v3 fix**: 0% → 9.3% (LIG1 4-char filter 버그 해결)
- **Pareto multi-objective + Bayesian Active Learning + Selectivity matrix + Quantum-corrected ranking** (8 ranker)
- **R4 expanded → 194 candidates** (relaxed bioisostere library)
- **Bayesian v2 round 6 candidates**: pterocarpan-vinyl-pyrogallol scaffold 발굴 (PAINS-free alternative!)
- **Multi-ranker leader 식별**: 2 mol top in 4/7 rankers
- **Round 4 selective compounds 71개**: β-sitosterol→AR sel_idx=0.563, shikonin→CTGF=0.247, chlorogenic→SIRT1=0.293

**ABFE 12h pivot 결정 (사용자 승인)**:
- ABFE EMB-3 × MMP-1 hardcoded script = 8/8 NaN (zinc 문제 미해결) → kill
- 대신 **5 × 10 ns MD ensemble** = 64분 wall, 5 paper-tier RMSD < 2 Å. ROI 압도적.

**🚨 PAINS audit critical finding (2026-04-27)**:
- 광범위 web search 결과 우리 8-target embelin claim 검증:
  - **8/8 직접 결합 보고 0건** (literature audit, PubMed/PMC)
  - Embelin 실제 검증 target: XIAP-BIR3 (4.1 µM), PAI-1 (4.94 µM), 5-LOX/mPGES-1 (0.06–2 µM), TACE
  - **1,4-benzoquinone-2,5-diol = PAINS class** (redox cycler + Michael acceptor + metal chelator)
- Preprint #1, #3, EMBELIN_LITERATURE_REVIEW.md 모두 v0.3 정정 (PAINS section + first-in-literature caveat 추가)
- Pool 2529 mol PAINS audit: PAINS_B 53.6%, Brenk 77.7%, embelin class 0.2% (4/2529 minority)
- → 정직 disclosure로 reviewer rigor 통과율 ↑

**3-Tier 로드맵 + 외부 액션 plan 4종 작성**:
- `docs/ROADMAP_3_TIER.md`: T1 4mo ₩500만 (85-90%) + T2 18mo ₩8,000만 (45-65%) + T3 7yr ₩30-55억 (35-50% partnership)
- `docs/CRO_TIER1_RFQ.md`: KIT/켐온/바이오톡스텍 견적 요청 template
- `docs/MFDS_PRE_IND_PREP.md`: 식약처 사전상담 Briefing Book 구성
- `docs/COLLABORATOR_OUTREACH.md`: 14 후보 그룹 outreach plan (₩3,000만/12mo)
- `docs/SYNTHESIS_RFQ.md`: Enamine/WuXi/DT Pharma 합성 RFQ

**사용자 결정 7개 (D1-D7)**:
- D1: ORCID + bioRxiv + medRxiv + ChemRxiv 등록 (즉시)
- D2: Editage / Enago 영문 교정 5편 (₩50-250만, W1)
- D3: **CRO Tier 1 RFQ 3사 발송** (₩1,560만, W4) ← 최고 ROI
- D4: 외부 collaborator 1명 contract (₩3,000만/12mo, M1)
- D5: MFDS Pre-IND consultation 신청 (free, M6)
- D6: Path A (cosmeceutical ₩1.5억) vs Path B (IND ₩30-55억) 분기 (M18)
- D7: Korean pharma partnership (M24)

### ✅ 완료 (2026-04-30, Universal scaffold 14/14 × 5 leaders + Extended 30ns validation)
**핵심 paper-tier 성과 — Preprint #15 Universal Scaffold 시리즈 v1.1**:

**5 universal scaffold leaders × 14 skin targets = 70 MD simulations all paper-tier**:
| Leader | SMILES variant | 14/14 결과 | sub-Å 개수 |
|---|---|---|---|
| **R12_4** | hydroxymethyl pterocarpan-vinyl-phenol | 14/14 paper-tier (mean<2.0Å) | 2 (MMP1 0.73, SIRT1 0.76) |
| **R12_11** | methoxy variant | 14/14 paper-tier | 3 (TGFB1 0.93, DCT 1.01, LOX 1.09) |
| **R12_23** | methyl ester variant | 14/14 paper-tier | **6** (AR 0.68, SIRT1 0.68, PTGS2 0.72, SREBP1 0.79, TYR 1.03, SRD5A1 1.06) |
| **R14_5** | methoxy variant 2 | 14/14 paper-tier | 3 (**MMP1 0.56**, CTGF 0.68, SREBP1 0.89) |
| **R13_13** | prenyl R11_0 variant (PAINS-flagged) | 14/14 paper-tier | 1 (PTGS2 1.01) |

**Extended-time kinetic validation (30 ns × top-5 sub-Å pairs)**:
| Pair | mean (full 30ns) | last-10ns mean | 평가 |
|---|---|---|---|
| MMP1 × R14_5 | **0.69** | **0.69** | sub-Å steady-state ✅ |
| AR × R12_23 | 0.77 | **0.85** | sub-Å steady-state ✅ |
| SIRT1 × R12_23 | **0.72** | **0.79** | sub-Å steady-state ✅ |
| CTGF × R14_5 | 1.34 | 1.76 | paper-tier with drift |
| PTGS2 × R12_23 | 진행 중 (~09:43 ETA) | — | — |

→ **3건 sub-Å 30ns kinetic stability 확인** = paper-tier reviewer 통과율 직접 강화.

**자동 overnight chain orchestration 성공**:
- `scripts/overnight_chain.sh`: bash nohup polling (60s 간격, 30분 stale detection)
- 03:03→04:56 R14_5 → R13_13 자동 sequence 완료
- 06:48~ extended 30ns chain 가동 (PID 34773), GPU 91% 지속

**89-simulation comprehensive ensemble heatmap (`figures/fig7_full_ensemble_heatmap.png`)**:
- All MD runs across R11_0 + R12_4/11/23 + R13_13 + R14_5 + earlier batches
- Target × Leader pivot showing 5-leader convergence on 14 skin disease targets

**즉시 가능 (사용자 다음 액션)**:
- Preprint #15 v1.1 PDF 38.6 KB main + 9 figures, 38.7 KB total
- §4.10–§4.18 5 universal scaffolds + final lead recommendation matrix 완성
- Pending: §4.19 extended-time validation table (PTGS2 도착 시)

### ✅ 완료 + 진행 중 (2026-04-30 11:35, R15 BRICS triage + batch2 GPU)
**R15 next-round candidate triage** (handoff to Codex):

**BRICS pool generation** — round 1 + round 2 → **38 unique** (R12_11 20, R12_23 11, R12_4 3, R13_13 4):
- `scripts/cpu_r15_brics_expansion.py` (44 candidates, MAX_BUILD 800)
- `scripts/cpu_r15_brics_deeper.py` (60 candidates, MAX_BUILD 3000, relaxed filter MW 180-550, logP 0.5-5.5, lipinski_viol≤1)
- ⚠️ R12_11 + R14_5 SMILES 완전 중복 (메톡시 위치만 다른 동일 chemical neighborhood) → R14_5 dedup 후 0개

**Triple filter pipeline (deadlock fix split)**:
- ⚠️ `cpu_r15_admet_xtb_filter.py` (combined script): TF + multiprocessing.Pool fork = futex deadlock (35분 0.7% CPU 후 kill)
- ✅ `cpu_r15_admet_only.py` (no Pool, ADMET-AI sequential) — 38행 × 14 ADMET endpoints
- ✅ `cpu_r15_xtb_only.py` (Pool of 8 xtb workers, no TF) — 38행 × HOMO-LUMO gap

**핵심 발견**:
- xtb gap mean 3.61 eV (electronically stable), max 4.36 eV (R12_23 methoxy chromanol)
- ADMET triple-safe (AMES + hERG + DILI 모두 < 0.3): **38개 중 단 1개** = `OCC1COc2cc(O)ccc2C1` (R12_4 chromanol fragment, MW 180.2, logP 0.94, QED 0.676, AMES 0.18, hERG 0.17, DILI 0.21)
- → R15 next-round MD validation의 1순위 후보 (small core, 외용 적합 logP, clean tox)

**Extended 30ns batch 2 진행 중** (PID 37674, ~12:00-12:30 ETA):
- ✅ mmp1×R12_4: 0.67/0.65 sub-Å steady-state
- ✅ sirt1×R12_4: 0.92/1.11 paper-tier
- ✅ srebp1×R12_23: 1.08/1.11 paper-tier
- 🔄 srebp1×R14_5 (running)
- 🔄 tgfb1×R12_11 (queued)

**Output 파일**:
- `pilot/cpu_meaningful/r15_brics_candidates.csv` (44, round 1)
- `pilot/cpu_meaningful/r15_brics_round2.csv` (60, round 2)
- `pilot/cpu_meaningful/r15_xtb_only.csv` (38 unique × HOMO/LUMO/gap)
- `pilot/cpu_meaningful/r15_admet_only.csv` (38 unique × 14 ADMET endpoints)
- `pilot/md_extended_30ns_batch2/summary.json` (batch2 5 pairs)
- `pilot/universal_scaffold_admet/full_tanimoto_top30.csv` (5 leaders × top 30 vs full pool)

**다음 핸드오프 (Codex 이어받음)**:
1. batch2 완료 대기 (ETA 12:00-12:30) → §4.19 5-pair full table 업데이트
2. R15 single triple-safe candidate (`OCC1COc2cc(O)ccc2C1`) Boltz-2 cofold × 14 targets — GPU 작업
3. preprint #15 v1.4 §4.21 R15 next-round triage 섹션 추가 + PDF 재빌드
4. CLAUDE.md feedback 추가: TF + multiprocessing.Pool fork deadlock 패턴 (recurring bug)

### ✅ Codex autonomous curator loop (2026-04-30 20:00)

Claude Code식 "시간마다 결과 기반으로 다음 큐를 지능적으로 고르는" 루프를 Codex에서 별도 구현:
- 빠른 deterministic fill: `scripts/auto_queue_cpu_gpu_daemon.sh` (기존 planner 기반, 120초 polling)
- LLM curator tick: `scripts/codex_curator_loop.sh` (기본 1800초 간격, `codex exec`가 최신 context를 읽고 큐잉/보류 판단)
- supervisor: `scripts/monitor_supervisor.sh`가 queue daemon + Codex curator loop를 감시하고 재시작
- prompt: `docs/CODEX_CURATOR_LOOP_PROMPT.md`
- context/decision/action log:
  - `pilot/codex_curator_context.md`
  - `pilot/codex_curator_decision.md`
  - `pilot/codex_curator_actions.log`
- triggers:
  - `/tmp/genesis_auto_queue_enabled`
  - `/tmp/genesis_monitor_enabled`
  - `/tmp/genesis_codex_curator_enabled`

운용 원칙:
- deterministic planner는 빠른 공백 채우기, Codex curator는 scientific priority/narrative/중복 위험을 감안한 judgement 담당.
- 2026-05-02 D: native WSL cutover 중에는 Queue drain mode가 우선이다. 이전 보호 큐 `PID 1345`, `PID 15578` 규칙은 historical context이며, 사용자가 명시 승인한 경우 상태 기록 후 중지 가능하다.
- 백그라운드 launch는 항상 `nohup setsid`.
- GPU util이 낮아도 OpenMM/antechamber/sqm 전처리로 CPU가 포화이면 추가 GPU 큐잉을 보류할 수 있음.

### ✅ Storage pressure + D: archive policy (2026-05-02 19:50)

Windows C:가 WSL ext4.vhdx를 품고 있어 `/home/crazat/genesis_medicine`의 대형 `pilot/` 산출물이 C: 여유공간을 직접 압박한다. D:는 NVMe SSD 여유가 크지만 `/mnt/d` 직접 연산은 DrvFS/9p 경유라 작은 파일이 많은 Boltz/OpenMM/xTB 작업에는 불리하다.

운영 원칙:
- 활성 계산은 WSL native ext4 유지: `pilot/cpu_meaningful`, active Boltz/OpenMM/xTB output, 보호 NPASS queue는 이동 금지.
- 완료된 대형 MD raw만 D: archive: `/mnt/d/genesis_archive/genesis_medicine/pilot/...`
- 로컬에는 `summary.json`, `summary.csv`, `.archive_manifest.json`, `ARCHIVED_TO_D.txt`만 남겨 planner/manuscript evidence를 보존.
- archive worker: `scripts/archive_completed_pilot_raw.py`
  - 보수적 선택: `pilot/md_*` + summary 존재 + raw child dir 존재 + process table에 active path 없음.
  - 전체 `rsync` 후 dry-run validation 통과 시에만 local raw child 삭제.
  - `/mnt/d` DrvFS/NTFS 권한 비트 차이를 피하려고 `--no-perms --no-owner --no-group --modify-window=2`로 검증.
  - manifest: `pilot/completed_pilot_raw_archive_manifest.jsonl`
  - log: `pilot/completed_pilot_raw_archive.log`
- duplicate archive launch 금지. 재실행 전 반드시:
  - `pgrep -af 'archive_completed_pilot_raw|rsync .*genesis_archive'`
  - `tail -80 pilot/completed_pilot_raw_archive.log`
- storage report: `scripts/write_storage_pressure_report.py` → `docs/STORAGE_OPERATIONS_PLAN.md` + `pilot/storage_pressure_report.json`
- queue planner hard-hold: `scripts/auto_result_planner.py`가 Windows C: 또는 WSL root free `< GENESIS_MIN_FREE_GB` (default 80GB)이면 신규 대형 CPU/GPU launch를 막는다. warn threshold default 200GB.
- 장기 최선책: active job 정지·백업 후 Ubuntu WSL distro 자체를 D:로 `wsl --export`/`wsl --import` 이전. 현재 큐가 도는 동안은 VHDX compaction/이전 금지.

### ✅ Genesis-only native D: WSL staging (2026-05-02 21:10)

ComfyUI는 C:의 기존 `Ubuntu`에 남기고, Genesis_Medicine만 D: native WSL ext4로 분리하는 방향으로 전환 중.

현재 구조:
- C: 기존 distro: `Ubuntu`
  - BasePath: `C:\Users\craza\AppData\Local\wsl\{0930df6a-828b-4f35-9b21-e20cd00e17e7}`
  - ComfyUI 유지: `/home/crazat/ComfyUI`
  - 기존 Genesis 큐가 아직 여기서 실행 중.
- D: Genesis 전용 distro: `Ubuntu-Genesis`
  - BasePath: `D:\WSL\Ubuntu-Genesis`
  - root fs: `D:\WSL\Ubuntu-Genesis\ext4.vhdx`
  - 내부 경로: `/home/crazat/genesis_medicine`
  - ComfyUI 없음.

진행 완료:
- 공식 Ubuntu 24.04 WSL rootfs 다운로드: `D:\WSL\Images\ubuntu-noble-wsl-amd64-24.04lts.rootfs.tar.gz`
- `wsl --import Ubuntu-Genesis D:\WSL\Ubuntu-Genesis ... --version 2`
- `crazat` default user 설정, `sudo/rsync/git/curl/ca-certificates` 설치.
- 무중단 initial staging 완료:
  - `/home/crazat/genesis_medicine`
  - `/home/crazat/miniforge3`
  - `/home/crazat/miniconda3`
  - `/home/crazat/.local` (uv Python symlink target)
  - `/home/crazat/.cache`
- 검증:
  - `df -hT .` → `/dev/sdf ext4`
  - `.venv/bin/python` RDKit OK
  - `.venv` torch CUDA OK
  - `miniforge3/envs/genesis-md` OpenMM OK
  - `nvidia-smi` OK

운영 스크립트:
- create: `scripts/create_ubuntu_genesis_on_d.ps1`
- staging copy: `scripts/stage_genesis_to_ubuntu_genesis.sh`
- verification: `scripts/verify_ubuntu_genesis.sh`

주의:
- 현재 initial staging은 기존 큐를 유지한 무중단 복제이므로, C: Ubuntu에서 계속 생성되는 최신 `pilot/` outputs는 최종 전환 전 한 번 더 delta sync 필요.
- 최종 전환 순서: queue pause/stop → final delta sync → `Ubuntu-Genesis`에서 verification → queue restart → C: Genesis 삭제는 며칠 안정화 후.
- `Ubuntu-Genesis` VHD max는 `1800GB`로 확장 완료. D:를 Genesis native ext4 중심으로 사용할 수 있음.

추가 정리/최적화 (2026-05-02 21:30):
- D:에서 Genesis와 무관한 실사용 잔여물 정리 완료:
  - `$RECYCLE.BIN` contents, `steam`, `XboxGames`, `WpSystem`, `WUDownloadCache`, `.parts`, `.url` 제거.
  - D: 사용량 대략 `374G -> 329G`; 여유공간 약 `1.5T`.
  - `WindowsApps`, `Program Files`, `Google Drive`는 Windows ACL/프로세스 lock으로 0-byte placeholder만 남음.
- C: Ubuntu 최적화 확인:
  - 전역 `%USERPROFILE%\.wslconfig`: `memory=56GB`, `processors=24`, `swap=16GB`, `mitigations=off`, `transparent_hugepage=madvise`, `autoMemoryReclaim=dropcache`, `sparseVhd=true`.
  - 이 설정은 WSL 전체에 적용되므로 `Ubuntu-Genesis`에도 재시작 후 동일하게 적용.
- `Ubuntu-Genesis` 전용 성능 보강 스크립트:
  - `scripts/configure_ubuntu_genesis_perf.sh`
  - `/etc/wsl.conf`: `systemd=true`, default user, automount metadata.
  - open-file limit: soft/hard `1048576`.
  - `/etc/profile.d/genesis-performance.sh`: Genesis cache, CUDA path, nofile.
  - C: Ubuntu의 selected dotfiles + CUDA 12.8 toolkit을 D: distro에 반영.
- 기존 C: Ubuntu 세션에서 Windows exe interop binfmt가 빠져 `wsl.exe` 직접 실행이 `Exec format error`를 낼 수 있음.
  - D: 관리 shell scripts는 `wsl.exe` 실패 시 `/init /mnt/c/WINDOWS/system32/wsl.exe -- ...` fallback을 사용하도록 수정.
  - 수동으로 Windows exe를 호출할 때도 같은 fallback을 사용하면 WSL shutdown 없이 진행 가능.
- Queue drain mode (2026-05-02 21:42):
  - 목적: 현재 실행 중인 Boltz/xTB/NPASS 작업까지만 끝내고, 이후 새 자동 큐잉 없이 final D: WSL cutover 준비.
  - local marker: `pilot/QUEUE_DRAIN_MODE`
  - removed triggers: `/tmp/genesis_auto_queue_enabled`, `/tmp/genesis_monitor_enabled`, `/tmp/genesis_morning_queue_guard_enabled`, `/tmp/genesis_codex_curator_enabled`, `/tmp/genesis_world_class_gap_enabled`
  - running compute jobs are preserved; scripts now refuse to start/restart auto queue, monitor, morning guard, curator, and world-class watchdog while the marker exists.
  - 재개 시: marker 제거 후 필요한 supervisor를 `nohup setsid ...` 방식으로 재시작.
- `Ubuntu-Genesis` VHD 확장 (2026-05-02 21:52):
  - `wsl --manage Ubuntu-Genesis --resize`는 C: Ubuntu가 running인 상태에서 WSL service shutdown을 요구하여 사용하지 않음.
  - 대신 Hyper-V `Resize-VHD -Path D:\WSL\Ubuntu-Genesis\ext4.vhdx -SizeBytes 1800GB`로 VHDX max 확장.
  - `Ubuntu-Genesis` 내부 `/` 확인: `/dev/sdf ext4 1.8T`, used 약 `155G`, avail 약 `1.5T`.
  - VHDX는 dynamic이므로 Windows 실제 파일 크기는 약 `156G`로 유지되고, native ext4 사용량이 늘 때만 D: 물리 사용량 증가.
  - `/mnt/d/genesis_archive`는 final cutover 시 native archive(`/home/crazat/genesis_archive/...` 또는 project-local archive)로 이전 가능.
- Full D: native migration (2026-05-02 22:08):
  - 사용자 승인: "상태를 기록하고 중지 하고 디 드라이브로 풀 마이그레이션 진행".
  - C: Ubuntu NPASS `scripts/cpu_5000_conformers_npass_top500_round2.py` process group `15578`는 상태 기록 후 중지. 보고서: `pilot/npass_stop_report_20260502_220806.txt`.
  - 중지 시점 상태: elapsed `3-04:35`, log `pilot/cpu_npass_500_1000_v2.log`는 header 1줄, 기대 출력 `pilot/cpu_meaningful/conformers_2000_npass_rank500_1000.csv` 없음. 원인 판단: `multiprocessing.Pool.map` 구조에서 pathological final molecule 또는 unbounded RDKit conformer branch로 checkpoint 없이 장기 정지.
  - `PID 1345` NPASS rank 1k-2k 큐는 cutover 점검 시 이미 process table에 없음.
  - D: `Ubuntu-Genesis` xTB 36-conformer refine은 유지: `scripts/cpu_xtb_npass_top_refine.py --topn 5000 --workers 8 --num-confs 36`, D internal parent PID `435`.
  - `scripts/stage_genesis_to_ubuntu_genesis.sh`는 full migration 모드로 확장:
    - `/home/crazat/genesis_medicine`, `miniforge3`, `miniconda3`, `.local`, `.cache`를 D native ext4로 복사.
    - D에서 실행 중인 36conf 파일 보호: `pilot/cpu_xtb_npass_top5000_hetero6_36conf_d_native.log`, `pilot/cpu_meaningful/xtb_npass_top5000_hetero6_refine_36conf.csv`는 tar exclude.
    - 기존 DrvFS archive `/mnt/d/genesis_archive`를 D native ext4 `/home/crazat/genesis_archive`로 복사.
    - 로그: `pilot/d_wsl_full_migration_<RUN_ID>.log`, tar stderr: `pilot/d_wsl_full_migration_project_tar_<RUN_ID>.log`, `pilot/d_wsl_full_migration_archive_tar_<RUN_ID>.log`.
  - migration 완료 전까지 `pilot/QUEUE_DRAIN_MODE` 유지, C: Ubuntu에서 신규 대형 큐 시작 금지. 완료 marker `pilot/D_NATIVE_FULL_MIGRATION_<RUN_ID>.txt`와 verification 통과 후 `Ubuntu-Genesis`를 Genesis canonical runtime으로 사용.
  - D: GPU smoke/backfill fix (2026-05-02 22:42):
    - `Ubuntu-Genesis` 최소 rootfs에는 `gcc/g++/make`가 없어 Boltz-2 Triton/cuequivariance JIT가 `Failed to find C compiler`로 실패했다. root로 `apt-get install -y build-essential` 완료.
    - Boltz cache `/home/crazat/.boltz`는 D native에서 초기화 완료(약 7.6GB). 이후 D: Boltz-2 첫 실행의 CCD/weight download 지연은 없어야 함.
    - archive copy 중 GPU backfill은 대형 MD 대신 output이 작은 active-learning Boltz-2 cofold만 허용. 현재 D native log: `pilot/active_learning_next_cofold_batch20_d_native.log` (batch21 재실행), loop log: `pilot/active_learning_gpu_backfill_d_native_loop.log`.
    - GPU backfill loop는 현재 batch 종료 후 `scripts/run_active_learning_next_cofold.py --batch-size 16`을 순차 실행한다. 대형 CPU/xTB 추가 큐는 archive native copy가 끝난 뒤 worker 수/중복 여부를 재평가.

### ✅ D-native canonical runtime + overnight queue armed (2026-05-03 00:55 KST)
- **Canonical repo is now `Ubuntu-Genesis:/home/crazat/genesis_medicine`**. All compute, `CLAUDE.md` updates, commits, and pushes must be done from this D-backed distro unless the user explicitly says otherwise.
- C-backed `Ubuntu` may still be used as an interop/control shell to call `wsl.exe -d Ubuntu-Genesis`, but it must not be treated as the source of truth and must not receive new OpenFold3/Boltz/xTB installs.
- `Ubuntu-Genesis` storage: `/dev/sdf` ext4 max `1.8T`, D-backed VHD. Last operational check showed >1T free; native project outputs and archive can live inside this distro.
- D OpenFold3 transfer/install verified:
  - `external_tools/openfold-3/` copied to D native ext4.
  - checkpoint `.cache/openfold3/of3-p2-155k.pt` copied to D native cache.
  - smoke passed at `pilot/openfold3_smoke/20260503_003339`; log confirmed `GPU available: True (cuda), used: True`, `Successful Queries: 1`.
  - CUDA/WSL path fix required in scripts: prepend `/usr/lib/wsl/lib` and set `CONDA_OVERRIDE_CUDA=12.8` where needed.
- Drain mode resolved for D runtime:
  - `pilot/QUEUE_DRAIN_MODE` absent.
  - active triggers: `/tmp/genesis_auto_queue_enabled`, `/tmp/genesis_monitor_enabled`, `/tmp/genesis_codex_curator_enabled`, `/tmp/genesis_morning_queue_guard_enabled`.
- Overnight guard / monitor stack is active until the user morning window:
  - `scripts/morning_queue_guard.sh` with `GENESIS_GUARD_UNTIL=2026-05-03T10:30:00+09:00`.
  - `scripts/monitor_supervisor.sh`.
  - `scripts/codex_curator_loop.sh`.
  - `scripts/auto_queue_cpu_gpu_daemon.sh`.
  - D keepalive process keeps `Ubuntu-Genesis` from being torn down by WSL after the launcher exits.
- GPU queue policy after cutover:
  - `scripts/overnight_gpu_backfill_d_native.sh` keeps GPU filled until `2026-05-03T10:00:00+09:00`.
  - Priority order: active-learning Boltz-2 cofold with MMP1 included → scaffold-hop / cryptic / round3 gap fills → R17 green 120 ns MD → R18 chromanol expanded backfill.
  - Latest observed active job: `run_active_learning_next_cofold.py --include-mmp1`, batch32 Boltz-2, CUDA memory in use.
- CPU queue policy after cutover:
  - xTB NPASS refine ladders continue on D native ext4 with multi-worker CPU saturation.
  - Latest observed active jobs: `xtb_npass_top1000_hetero3_refine_288conf.csv` and `xtb_npass_top3000_hetero5_refine_288conf.csv`; planner can continue into hetero8/hetero9 ladders when idle.
- Scientific claim discipline remains mandatory:
  - MMP1/Zn results are triage-only until ZAFF/metal-aware ABFE gate passes. Do not claim “perfect binding” or confirmed negative ABFE from non-ZAFF runs.
  - R18 chromanol expanded backfill is discovery triage only; no novelty/FTO/commercial claim until prior-art gate passes.
  - Boltz-only affinity requires cross-model, decoy, PLIF, MD, or free-energy validation before strong manuscript language.
- Known D-launch reliability rule:
  - Background jobs should be launched with `nohup` and a Windows-side `wsl.exe -d Ubuntu-Genesis` client or equivalent keepalive. Simple detached `nohup` inside a one-shot WSL invocation can be reaped when the distro idles.
  - Preferred manual pattern from C control shell: `/init /mnt/c/Windows/System32/cmd.exe /c "cd /d C:\ && wsl.exe -d Ubuntu-Genesis --cd /home/crazat/genesis_medicine -e bash -s"` with the script piped on stdin.

### ✅ C 드라이브 legacy 유지 결정 (2026-05-03 11:00 KST)

D Ubuntu-Genesis cutover 직후 시점에서도 C `Ubuntu` distro 안의 Genesis 자산은 **유지**한다. fallback 백업 가치 + 위급 storage pressure 부재.

- 결정: 자동 cleanup / VHDX compact / 삭제 제안 금지. 사용자가 다시 묻거나 C free < 100 GB 위급 시에만 단계 B/C 재검토.
- 시점 수치: Windows C 503 GB free / 2.0 TB. C VHDX(`Ubuntu`) 685 GB sparse, ext4 used 327 GB. C `/home/crazat/genesis_medicine` 118 GB.
- 절대 보존: `/home/crazat/ComfyUI` (130 GB), 다른 venv/projects, `miniforge3`/`miniconda3` 통째 (Genesis env만 선택 제거 가능), `~/.local`, `~/.cache`, Claude 메타.
- 단일 최대 회수 후보: `/home/crazat/genesis_medicine` (118 GB, 내부 `.venv` 18 GB 포함). 실제 Windows 회수는 `Optimize-VHD -Mode Full` 별도 실행 필요(C `Ubuntu` distro shutdown 동반 → ComfyUI 일시 정지).
- 재검토 트리거 (모두 충족): R17 120ns plan(9 jobs) 완료 + D HEAD push 검증(`git rev-list --left-right --count origin/main...HEAD` = `0\t0`) + D-native 1주 무사고 + 사용자 재확인.
- 상세 메모리: `~/.claude/projects/-home-crazat-genesis-medicine/memory/project_c_drive_legacy_retention.md`.
- 참고: 인계자 manifest `docs/C_DRIVE_GENESIS_CLEANUP_MANIFEST_2026-05-02.md` 동일 결론.

### ✅ Paper #A 12h overnight 연산 결과 (2026-05-04 22:34 → 2026-05-06 12:42 KST)

> 사용자 12h 자율연산 위임 → 6-compound ChEMBL MMP-1 ABFE benchmark + xtb GFN1/GFN2 cross-method analysis 완료. **paper #A 핵심 finding 확정**.

**6-compound ABFE rep1+rep2 결과** (`pilot/abfe_benchmark_chembl/CHEMBL{ID}/abfe_production_mss/dG_bind.json`):

| ChEMBL | exp dG | rep1 | rep2 | mean | Δrep | mean−exp |
|---|---|---|---|---|---|---|
| 415 (4nM, strong) | -11.6 | -19.7 | -0.869 | -10.28 | **18.8** | -1.32 ✓ |
| 94487 (12nM, strong) | -10.9 | -20.9 | -21.019 | -20.96 | 0.12 | +10.06 ❌ |
| 257077 (15nM, mid) | -10.7 | +8.6 | +3.165 | +5.88 | 5.4 | +16.58 ❌ |
| 301236 (42nM, mid) | -10.0 | -7.5 | -11.215 | -9.36 | 3.7 | -0.64 ✓ |
| 292707 (200nM, mid) | -9.0 | +4.9 | +4.632 | +4.77 | 0.27 | +13.77 ❌ |
| 2105729 (18μM, weak) | -6.4 | +0.35 | +7.198 | +3.77 | 6.85 | +10.17 ❌ |

**Pass rate: 2/6** (415, 301236).

**rep3 부분 확장** (415 + 2105729): 415 rep3 = -11.49 (Δexp 0.11★), 3-rep mean -10.69 (Δexp 0.91). **3-replicate mean이 catastrophic Δrep variance를 평균화하여 strong inhibitor의 experimental value를 1 kcal/mol 이내 회복**. Weak binder (2105729)는 3 rep 모두 양수로 일관 실패.

**Paper #A 핵심 finding (publishable angle)**: *Reproducibility ≠ accuracy.* 94487은 Δrep 0.12 (극도 reproducibility) 이지만 +10 kcal systematic over-binding. 415는 Δrep 18.8 (catastrophic variance) 이지만 mean이 1.3 kcal 이내. ZAFF-AMBER ABFE on Zn metalloenzymes은 compound-specific failure mode가 Δrep과 상관 없음.

**Paper #A 권장 framing (locked)**: "*Limitations of ZAFF-AMBER ABFE for Zn metalloenzyme binding affinity prediction: replicate-pair analysis on MMP-1.*" Pass 2/6은 "validation" framing 불가 — methodology evaluation paper로 포지셔닝. JCTC submission target.

**xtb GFN1 vs GFN2 cross-method (paper #B add-on)**: 9997 hetero10 cohort, 432 conf, ALPB. **Spearman ρ(gap) = 0.978**, ρ(energy_min) = 0.993. Top-10 9/10, Top-50 45/50. xtb method-agnostic ranking robustness 입증 → paper #B method-robustness section 데이터 확보.

**Prinomastat (CHEMBL406) ABFE 시도 (2026-05-06 11:09)**: prep `-nc -1` 적용 후 구조 정상 (74290 atoms, Zn 1, LIG 1). 하지만 Phase 5 complex leg equilibration replica 0 state 0에서 NaN crash (4 LangevinDynamicsMove restart 실패). **embelin과 동일 failure mode** — prep script가 warmup 스킵해서 발생. 다음 세션: `scripts/zaff_phase5_warmup_generic.py --work pilot/abfe_benchmark_chembl/CHEMBL406` 먼저 돌리고 production 재발진.

**Manifest 15개 중 ok 6 / fail_antechamber 9** — 9개 모두 `-nc -1` flag로 prep 가능 확인 (CHEMBL443684 Marimastat / CHEMBL406 ✓ / 412 / 259829 / 98 / 93146 / 3036 / 57058 / 1207). Tier-1 확장 시 orchestrator에 warmup 단계 + `-nc -1` autodetect 추가 필요.

### 다음 세션 즉시 액션 (continuity)
1. **CHEMBL406 warmup → ABFE 재발진**: `python scripts/zaff_phase5_warmup_generic.py --work pilot/abfe_benchmark_chembl/CHEMBL406` → `python scripts/zaff_phase5_abfe_production_mss.py --work pilot/abfe_benchmark_chembl/CHEMBL406` (PATH export 필수: `export PATH=/home/crazat/miniforge3/envs/genesis-md/bin:$PATH`).
2. **`abfe_benchmark_prepare.py` 패치**: build_complex 단계에서 RDKit GetFormalCharge() 결과를 antechamber `-nc` 인자로 자동 전달 + tleap 후 warmup_generic 호출 추가.
3. **나머지 8개 manifest 화합물 prep 재실행**: -nc -1 fix 적용.
4. **Paper #A 초고**: `preprints/08_abfe_methodology/manuscript.md` 6+rep3 데이터 + GFN1/GFN2 cross-method 섹션 추가. 권장 framing 적용.
5. **CPU**: GFN1 cohort csv (`pilot/cpu_meaningful/xtb_npass_top9997_hetero10_gfn1_432conf.csv`) 분석 figure 생성 가능.

---

### ✅ Paper #A methodology pipeline — Tier 2/3 인프라 완성 (2026-05-04)

JCTC/JCIM/RSC Digital Discovery target — 17 Zenodo papers를 1편 deep methods paper로 재구성. 가설: ZAFF-AMBER + alch RE-MD (16λ × 3 rep × 8/5 ns)이 ChEMBL MMP-1 IC50 ranking을 Spearman ρ ≥ 0.6으로 회복.

**Tier 2 deliverables**:
- `pilot/abfe_mmp1_holo_zn/abfe_production/dG_bind.json`: EMB-3 ABFE INCONCLUSIVE (+0.38 ± 0.29 kcal/mol).
- `scripts/zaff_phase5_warmup_generic.py`: 임의 ABFE work-dir용 warmup (10000-iter min + 0K→310K heat + restrained NPT). NaN crash 방지 핵심.
- `scripts/zaff_phase5_abfe_production_generic.py`: parameterized Phase 5 (`--work` CLI). PHASE4 gate `{work}/complex/PHASE4_OK`. **Production timing 업그레이드**: NS_PROD_COMPLEX 5.0→8.0, NS_PROD_SOLVENT 3.0→5.0 (literature Δ ns 기반 Spearman ρ uplift +0.05~0.15). Per compound 19-29h, Tier-1 full run ~8d wall.
- `scripts/abfe_benchmark_orchestrator.py`: Tier-1 6 compounds 순차 실행 + Spearman/MAE aggregation. PHASE4_OK는 root-level 사용 (warmup/Phase 5 generic은 `complex/PHASE4_OK`).
- `scripts/abfe_benchmark_prepare.py`: Vina+obabel pose + AM1-BCC + tleap parm. (meeko CLI는 이 env에서 broken — obabel로 대체.)
- `preprints/PRE_REGISTRATION_TEMPLATE.md`: OSF 사전등록 template (H1-H3 lock).

**Tier 3 / paper-strengthening deliverables**:
- `scripts/active_learning_screen.py` + `pilot/active_learning/round1/`: 1390 mols 학습, cv_r2=0.83±0.25.
- `scripts/kipris_patent_check.py`: KIPRIS+PubChem patent novelty (필요: `KIPRIS_API_KEY`).
- `scripts/dude_decoy_benchmark.py` + 315 decoys: enrichment는 actives xtb-scoring 별도.
- `scripts/zenodo_code_release.py`: code DOI 발급 (필요: `ZENODO_TOKEN`).
- `scripts/of3_aqaff_paper_a_b.py`: OpenFold3 + AQAffinity cross-engine (modes: tier1, top500). MMP1_SEQ apo stub 재사용 (R=-0.292 일관성).

**Tier-1 ABFE benchmark targets (paper #A locked subset)** — 6 ChEMBL MMP-1 4 nM → 18 μM:
| ChEMBL ID | Name | IC50 (nM) | Class |
|---|---|---|---|
| CHEMBL415 | Batimastat | 4 | hydroxamate |
| CHEMBL94487 | RS-130830 | 12 | carboxylate |
| CHEMBL257077 | — | 15 | prinomastat-like hydroxamate |
| CHEMBL301236 | — | 42 | fluoro-aryl hydroxamate |
| CHEMBL292707 | Ilomastat | 200 | zinc-chelating |
| CHEMBL2105729 | — | 18000 | very weak hydroxamate |

EMB-3 (done) + embelin (running) → N=8 ABFE for Spearman.

**Vina active-site grid (MMP-1 1HFC)**: Zn (40.32, 27.89, 36.94), grid 25×25×25 Å, exhaustiveness=16, num_modes=5. First-shell 3-His: HID111/115/121.

**Why this matters (paper #A submission criteria)**:
1. ABFE protocol validated against experimental Ki (이전 missing piece).
2. Statistical rigor (5+ diverse-scaffold 화합물).
3. Reproducibility chain (Vina + obabel + AmberTools + OpenMM 모두 conda).
4. Pre-registered hypothesis (screening-paper rejection 회피).

**Known pitfalls (다음 세션에서 회피)**:
- Phase 5는 minimization 없음 → C12+ alkyl 즉시 NaN. 항상 warmup 먼저.
- meeko CLI (`mk_prepare_*`)는 이 env에서 broken (config bug). obabel 사용.
- subprocess의 `python3`은 base conda Python (no parmed) 해석. absolute path 사용.
- Vina 출력 PDQBT는 H 누락. obabel `-h` 또는 RDKit AddHs 필요.
- 백그라운드 launch 전 stale orchestrator process 반드시 kill + trajectory.nc 정리.

**TF + multiprocessing.Pool fork = futex deadlock (recurring bug)**: ADMET-AI(TF) + multiprocessing.Pool fork가 같은 프로세스에서 동시 사용되면 deadlock. 항상 별도 스크립트로 분리 (`*_admet_only.py` sequential + `*_xtb_only.py` Pool).

### 🔥 Tier 0 — 즉시 통합 (SOTA audit 2026-04-26 결과)
> 광범위 SOTA 조사 결과 **즉각 통합하면 ROI 매우 큰** 7개 도구. 모두 MIT/Apache.
1. **CellAwareGNN** (bioRxiv 2026-02) — TxGNN 직접 후속, scPrimeKG 기반, 자가면역 피부질환 +6% AUPRC. 자가면역(아토피·건선·원형탈모) 재창출 정확도 직격.
2. **PocketXMol** (Cell 2026, MIT, 205★) — 단일 모델로 11/13 SBDD SOTA + cyclic peptide 동시 (약침 후보).
3. **PocketMiner + CryptoBank** — TGF-β1/MMP-1/CTGF allosteric site 1초 스캔 (B 가설 음성을 cryptic site 재탐색으로 강화).
4. **logKp + Skin_Irritation 자체 ML 헤드** (FDA 2326 + LGBM) — 우리 stack 가장 큰 약점 (피부 외용 정량) 직접 보완.
5. **f-RAG** (NeurIPS 2024, NVIDIA) — 센텔라/시코닌/EGCG fragment 강제 포함, 한약 영감 분자 디자인 핵심.
6. **NPASS 2026 update** — quantitative ADME-Tox **+206%** 확장 (외용 logKp ground truth).
7. **BAT2** (OpenMM 호환) — 자체 ABFE 구현을 paper-tier 검증/대체.

### 🟡 Tier 1 — 8주 내 (Nature-tier 강화)
8. **Protenix-v2** (Apache, 2026-04) + **OpenFold3** ensemble — Boltz-2 consensus 강화.
9. **AlphaFlow-Lit** — 기존 AlphaFlow drop-in 47× 가속.
10. **CarsiDock-Cov** — 시코닌/EGCG quinone 공유결합 평가 (현 stack에 unique).
11. **Boltz-ABFE** — cryptic site 결정구조 없이 ABFE.
12. **DeepRetro** (Sci Rep 2026) — 센텔라 사포닌 변형 합성 (AiZynthFinder 보강).
13. **AIMNet2** — charged 천연물 MD (MACE-OFF24 한계 극복).

### 🏥 Recover 한의원 직결 (2026-08 오픈 전)
- **임상 reference**: ECa 233 (51:38 madecassoside:asiaticoside) + Lapatinib 외용 reposition + Pirfenidone keloid 데이터 + OliX OLX104C 한국 IND 모델
- **흉터↔IPF cross-disease 분자 근거**: skin/lung fibroblast atlas (Nat Immunol/Cancer Cell 2025)에서 TGF-β signaling fibroblast subtype 공유 입증
- **Rentosertib (TNIK)**: 첫 generative AI lead → IPF Phase 2 진입 (FVC +98.4 mL) — 우리와 동일 파이프라인 = 벤치마크
- **NIPA 2025 "AI 의료 디지털 전환"** 사업 응모 자격 검토 (Recover + Genesis_Medicine + AI 안면분석 패키지)
- **국내 비임상 CRO**: KIT/켐온/바이오톡스텍/DT&CRO RFQ 3개사 견적 비교
- **MFDS 2025 천연물 외용제 가이드라인** 직접 컨택 (검색 미노출, 법무 컨택 필요)
- **BOKP DNA barcode** (KP/KHP 514종) — `skin_compounds_curated.csv` 가중치 정량화

### 🟢 중기 로드맵 (M1-M5 통합)
- M1: 흉터 **lead 화합물 3-5개** 확정 (EMB-3 + EGCG + Embelin baseline + 추가 2개) → 약침 적용 시뮬레이션 (용해도·안정성)
- M2: ABFE 정량 ΔG → IC50 nM 추정 → CRO Tier 1 (₩1,560만) 진입; 기미·탈모 각각 **lead 후보** 확정
- M3: Tier 0 SOTA 7개 모두 통합 + 한약 **복합 처방 최적화** (시너지 스코어링)
- M4: 외용 크림 포뮬레이션 (자운고 + EMB-3 강화 1순위) — Recover 1차 시제품
- M5: IPF cross-disease 후속 paper (EMB-3 + IPF lung fibroblast 모델)

---

## 프로젝트 한 줄 요약
**한약·생약 전통지혜 × AlphaFold 시대 구조기반 설계 → 피부재생/색소/탈모/염증 신약 후보 파이프라인.** 상업 제품화 전제.

## 🏢 상업화 원칙 (Commercial Mode) — 유지

본 프로젝트는 **상용 출시 예정**.

| 프로파일 | 용도 | 허용 라이선스 |
|---|---|---|
| `research` | 내부 탐색 · 처방 네트워크 분석 | 모든 오픈 (CC-BY-NC · 학술용 포함) |
| `commercial` | 외부 출시 빌드 (화장품/의약품/외용제) | **Apache-2.0 · MIT · BSD · CC0 · CC-BY만** |

### 상업 빌드 허용 (피부 관련 특히 강함)
- **천연물 DB**: COCONUT 2.0 (CC0, 700k), LOTUS (CC0), **NPASS 3.0** (정량 ADME-Tox 2026 update), **NPAtlas 3.0** (CC-BY), Dr. Duke's Phytochemical DB (USDA public domain).
- 구조 예측: Boltz-2 (MIT), Protenix v2 (Apache-2.0), OpenFold3 (Apache-2.0).
- ADMET·화학: ADMET-AI (MIT), RDKit (BSD-3), Chemprop 2 (MIT), Uni-Mol2 (MIT).
- MD: OpenMM 8 (MIT), openmm-ml (MIT), MACE-OFF24 (MIT).
- 규제: **KHP/KP** (한국 정부저작물, 참조 가능).

### 상업 빌드 제외 / 조건부 (피부 관련 특이사항)
- ❌ HERB 2.0 (CC-BY-NC), TCMSP, BATMAN-TCM — **research 빌드에서 한약 네트워크 분석만**.
- ⚠️ 발견된 성분/SMILES 자체는 자연물이므로 commercial 빌드로 이식 가능. 단 "HERB/TCMSP 데이터 기반" 마케팅 금지.
- ⚠️ KTKP 스크래핑 robots.txt 준수.

### 한약 처리 원칙
- 네트워크 약리학 **분석은 research 프로파일에서** HERB/TCMSP/KTKP 활용.
- 도출된 후보 화합물 SMILES는 **상업 빌드로 이식 가능**.
- 출시물 라벨·광고에 "HERB/TCMSP 기반" 금지. "전통 한방 처방 영감 + 구조 기반 최적화" 라벨 가능 (법무 검토).
- **KHP/KP 수록 한약재 +α 가중치** (한국 임상 진입 우선).

## 실행 환경 (절대 규칙)
- **진짜 저장소 / canonical runtime**: `Ubuntu-Genesis` WSL2 native ext4 `/home/crazat/genesis_medicine/` (D: VHD `D:\WSL\Ubuntu-Genesis\ext4.vhdx`).
- **C: Ubuntu `/home/crazat/genesis_medicine`는 legacy/control shell only**. 신규 설치, 신규 계산, commit/push는 사용자가 명시하지 않는 한 금지.
- **Python 메인 venv**: 3.11 (uv 관리) — Boltz-2, ADMET-AI, OpenMM 8 호환
- **보조 conda env**:
  - `genesis-md` (py3.11): MD 전용 (openmm + openff + mace + pdbfixer)
  - `txgnn` (py3.9 + torch 2.3 + DGL 2.4): 재창출 전용 (CPU)
- **GPU**: RTX 5090 32GB Blackwell + CUDA 12.8. DGL/openff 레거시 의존 제외하면 메인 venv에서 GPU 가속 전부 작동.

### 🧠 자율 연산 오케스트레이션 (2026-06-09 ROI allocator + GPU 최대화, scripts/round27_paperA/)
자율 역할 = ROI 높은 순 무중단 연산 (exploit ↔ explore 균형). 4-분야 문헌(밴딧/BO/SDL/포트폴리오) 수렴으로 휴리스틱을 정량 엔진으로 격상.
- **`roi_allocator.py`** — 결정엔진. EXPLOIT(신뢰성 n-축적) marginal value = `s/(2√2·(n-1)^1.5)` **n^-1.5 감쇠** (n≈28 plateau면 ≈0) vs EXPLORE(de novo 발굴) `P(hit)·payoff` 옵션가치. `fund argmax(MV/GPU-hr)`, fractional-Kelly λ0.4, March explore floor 15%. 정량확인: n=33서 MV_A=7e-5 vs MV_B=1.1 → EXPLORE.
- **GPU 최대화 = boltz 2개 파이프라인** (한쪽 MSA-load 갭을 다른쪽 diffusion burst가 메움): **검증 평균 91-95%/최대100%/364-405W**. 단독 boltz는 78%(분자간 MSA 디핑).
  - ⚠️ **VRAM 32GB이 진짜 제약**: boltz@100샘플≈19GB, @50샘플≈8GB (per-sample ≈160MB). **2×100=35GB OOM**(throttle 151W, deadlock). 맞는 조합 = **@100+@50=~28GB**.
  - **3-블록 코어 분리**: xtb σ_E 매트릭스 `0-13` | cascade@50(FILL) `14-18` | de novo@100(EXPLORE) `19-23`.
  - **per-molecule 호출 절대 금지**(80회 모델로딩=GPU 3-5%). **디렉터리배치만**(1회 호출 N분자 warm).
  - ⚠️ **`boltz_affinity_pin_19_23_daemon.sh`는 멀티블록과 충돌**(모든 boltz를 19-23로 강제) → 멀티슬롯 시 OFF.
- **`gpu_roi_supervisor.sh` (v4, 2026-06-10 큐기반 자동회전)** — v3는 슬롯마다 tier 하드코딩 → resume-skip 트랩마다 사람/LLM이 파일 편집 필요였음. v4는 각 슬롯에 `tier_state/slot_{E,F}.{current,queue}`(현재 tier + 대기 큐)를 두고, 현재 tier 완료(트랩: d≥N 또는 near-done+boltz exit, 또는 stall STALL_SKIP=16폴) 시 **SIGKILL→큐 다음 tier로 자동 회전**(편집·재시작·idle대기 없음). 2-layer: 이 셸=기계적 무중단 회전, `tier_planner.py`(via `tier_autopilot.sh` 10분 loop)=phase8 sweet-spot으로 다음 tier TYPE(ACQUISITION vs GENERATION) 결정+큐 사전 refill. SLOT-E 19-23/7041 + SLOT-F 14-18/8107.
  - ⚠️ **VRAM config = `--max_parallel_samples 1`**(2026-06-10): mp=2는 양슬롯 fresh 동시로드 시 ~31.6GB로 32GB 초과→watchdog kill-loop(throughput 0)였음. mp=1 = peak ~16.6GB/free ~16GB/util 90-99% 안정. `gpu_vram_watchdog.sh`(free<6GB→boltz SIGKILL→supervisor resume) = OOM 하드백스톱. **OOM 절대금지 1순위**: watchdog 잦은 SIGKILL(분당)은 transient 아닌 "config가 카드에 안 들어감" 신호 → 즉시 mp 낮춰라(loosen 금지). 상세 `memory/feedback_boltz_vram_driven_by_num_workers.md`.
- **LLM 모니터링 = event-driven (2026-06-10 ROI 재설계, `autonomous_watcher.sh` + 시간당 cron)** — 고정 25분 cron 폴링은 비효율: 5분 캐시TTL 초과로 매 tick 컨텍스트 uncached 재독 + 95% no-op + 시간임계 장애는 데몬이 초단위 self-heal(폴링주기 무관). 해법:
  - **`autonomous_watcher.sh`**(주): 45s cheap shell 체크, 실 anomaly(supervisor/vram_watchdog/boltz/xtb 死·VRAM<6GB·GPU idle·양큐 동시고갈) 지속(anti-flap 카운터) 시에만 **exit→harness가 LLM 재호출**. healthy면 LLM 0발화. **`Bash run_in_background:true`로 launch必**(setsid 아님 — exit 재호출 hook). exit 재호출 실증됨.
  - **cron backstop**(보조): `13 * * * *`(시간당, `<<autonomous-loop>>`). watcher 死(Gemini 외부kill) 시 relaunch + 시간당 전략점검. **매 tick watcher alive 확인→死면 재launch**(idempotent).
  - 효과: LLM 발화 ~58→~24/일 + 장애지연 ≤25min→~1min(Pareto). regime: HEALTHY=watcher+hourly, INCIDENT=in-turn(캐시warm), OVERNIGHT=더 길게. 상세 `memory/feedback_autonomous_monitoring_cadence_roi_2026_06_10.md`.
- **하드 규칙**: kill/pkill 절대 금지(다 죽은 것만 launch, bracket으로 self-match 회피) — 단 엉킨 boltz 정리는 사용자 명시 승인 시 예외(respawner/supervisor 먼저 죽이고 boltz, numeric SIGKILL). watcher kill엔 per-PID 정확prefix 검증必(`pgrep -f`가 내 명령 cmdline 자기-kill 함정). SIGSTOP/SIGCONT=sanctioned pause(단 외부kill엔 무방비→디스크 resumable이 본질). 보고 한글/원고 영어.
- 설계 상세: `scripts/round27_paperA/ROI_ALLOCATOR_DESIGN.md` + `ROI_BALANCE_DESIGN.md`.

## 기본 명령

```bash
cd ~/genesis_medicine
source .venv/bin/activate

# 메인 피부 파이프라인 (commercial)
python -m genesis_medicine.cli run disease=scar_regeneration build_profile=commercial

# research 빌드 (한약 처방 네트워크)
python -m genesis_medicine.cli run disease=scar_regeneration build_profile=research \
    library=herb_scar_prescriptions
```

## 디렉터리 지도 (업데이트)
```
~/genesis_medicine/
├── CLAUDE.md
├── conf/
│   ├── build_profile/
│   ├── disease/
│   │   ├── scar_regeneration.yaml       ★ NEW
│   │   ├── hypertrophic_keloid.yaml     ★ NEW
│   │   ├── pigmentation_melasma.yaml    ★ NEW
│   │   ├── androgenetic_alopecia.yaml   ★ NEW
│   │   ├── acne_vulgaris.yaml           ★ NEW
│   │   ├── photoaging.yaml              ★ NEW
│   │   ├── atopic_dermatitis.yaml       ★ NEW (후속)
│   │   └── (AD/BACE1, NSCLC는 인프라 검증용으로 유지)
│   ├── skin_targets/                    ★ NEW
│   │   ├── scar.yaml        (TGF-β1, MMP-1/3/9, CTGF, COL1A1 등)
│   │   ├── pigment.yaml     (TYR, MITF, TRP-1/2)
│   │   ├── alopecia.yaml    (SRD5A1/2, AR, Wnt10b)
│   │   ├── acne.yaml        (SREBP1, AR, 5αR, C. acnes)
│   │   └── photoaging.yaml
│   └── …
├── data/
│   └── skin_compounds_curated.csv        ★ NEW (센텔라/감초/자근 등 SMILES)
├── pilot/
│   ├── skin_scar/                        ★ NEW (흉터 파일럿)
│   ├── skin_pigment/                     ★ NEW (기미)
│   ├── skin_alopecia/                    ★ NEW (탈모)
│   ├── skin_acne/                        ★ NEW (여드름)
│   ├── bace1_boltz2/                     (인프라 검증 — 보존)
│   ├── alzheimer_repurposing/            (인프라 검증 — 보존)
│   └── disease_expansion/                (인프라 검증 — 보존)
└── src/genesis_medicine/  (변동 없음)
```

## 기술 스택 요약 (v3 피부)
- **구조 예측**: Boltz-2 + Protenix v2 + OpenFold3 + Consensus.
- **앙상블**: AlphaFlow + BioEmu (cryptic pocket, 예: TGF-β1의 allosteric 사이트).
- **스크리닝 6단계**: DrugCLIP → Uni-Mol2 → FlowDock → Boltz-2 → GNINA → PoseBusters + ECR.
- **ADMET v2**: ADMET-AI. **피부용 가중치는 기본 BBB 대신 logKp(경피), 피부 자극, solubility 중심.**
- **생성**: FlowMol3 + DecompDiff + REINVENT 4 + SATURN + AiZynthFinder. **센텔라 scaffold 최적화**에 특화.
- **MD + ABFE**: OpenMM-ML + MACE-OFF24 + FEP-SPell-ABFE.
- **천연물 DB**: COCONUT 2.0 + LOTUS + NPASS 3 + NPAtlas + Dr. Duke.
- **한약 research**: HERB 2.0 + TCMSP + KTKP + BATMAN-TCM + SymMap.
- **네트워크 약리학**: Reactome + WikiPathways (KEGG 대체, commercial-safe).

## 파일럿 (피부 재생)
흉터 · 센텔라아시아티카 + 자근 + 감초 → TGF-β1, MMP-1, CTGF.
`conf/disease/scar_regeneration.yaml` + `pilot/skin_scar/`.

## 개발 규칙 (Claude 준수)
1. Windows 경로에 새 파일 쓰지 말 것.
2. 어댑터는 Protocol 준수, 설정 하드코딩 금지. 모든 파라미터 `conf/*.yaml`.
3. 외부 API는 `io/` 캐시+재시도.
4. 새 데이터 추가 시 `docs/LICENSING.md` 업데이트 + `build_profile` 태그.
5. `test_license_gate.py` 실패 상태로 merge 금지.
6. 상용·비상용 섞지 말 것 (어댑터 분리).
7. **피부 특화**: 경피 흡수성(logP 1.5-3.5, logKp) + 피부 자극 최소화 + Lipinski MW ≤ 500.
8. **CPU + GPU 동시 가동 필수**: 24 cores 시스템에서 한쪽이라도 idle 절대 금지. 매 turn `nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv` + `ps aux --sort=-%cpu | head -10` 확인. GPU long job (ABFE / Boltz-2 batch) 진행 중에도 `scripts/cpu_queue_v6_continuous.sh` 같은 24-core saturation 큐 동시 가동. Process 죽으면 즉시 재시작 + 새 job 큐잉. 자세한 패턴 + recurring bug fixes (tensorflow XLA / cuequivariance cu12-cu13 / BRICSBuild seed / boltz venv / PDB residue 3-char) → memory `feedback_cpu_gpu_concurrent.md`.

## 금지
- `.env`, API 키 commit 금지.
- AF3 공식 웨이트 기본 경로에 두지 말 것.
- HERB/TCMSP/KTKP 데이터를 `commercial` 프로파일에서 참조 금지.
- 출시물 광고에 "한약 DB 데이터 기반" 문구 사용 금지 (성분 자체는 OK).

## 현재 상태 (2026-04-25)
- **v2 인프라 완성** — 라이선스 게이트(83 컴포넌트, 118 테스트), 11단계 아키텍처, 가속 스택 활성, MD/ABFE/ML potential 모두 작동.
- **피부 방향으로 전환 시작** — conf/disease/skin_targets/data/ 준비 중.
- BACE1/AD 파일럿은 보존 (인프라 검증 결과물).
- Recover 한의원 **2026-08 강남 오픈** (~4개월 후). 파이프라인의 1차 lead 후보 발굴이 이 시점과 동조.

---

## 🆕 현재 상태 (2026-05-12 00:30 KST) — paper_A v5 27→28-rep cluster matrix + H 1TB 활용 + R41/R42 dedup

> **다음 세션 인계 노트**: 2026-05-11 16:30 → 2026-05-12 00:30 8h 모니터링 사이클. paper_A v5 cluster matrix v34-v38 5 reps 추가 완료 → 5×27 = 135 cells, v5j 27-rep × 10-axis Cluster B intra-ρ=**0.9748 안정**. v39 cofold (seed 62) GPU 100% 진행 중 (~01:30 ETA). H 1TB SSD 신규 활용 시작 — D 245GB archive cp 완료, WSL 180GB archive cp 진행 중. saturation R41+R42 dedup 검증으로 98-99% 재확인.

### 🏆 paper_A v5 — 27-rep × 10-axis Cluster B intra-ρ 안정성 (manuscript update-ready)
- **v5j 27-rep matrix figure**: `pilot/round27_paperA/cluster_AB_analysis/fig_v5j_4cluster_heatmap.png` — Cluster B intra-ρ=**0.9748**, A1=1.000, B↔A1=+0.66, B↔A2=-0.59
- **v34→v38 5 reps 추가** (5-NNP chain 완료): GFN2 SP/OPT/HESS + GFN1 + GFN-FF complex + MMFF94 + UFF + MatterSim + Orb OMat + Orb OMol25 + AIMNet2-NSE + ANI-2x
- **v38 GPU chain COMPLETE 00:17:43** (ani2x_v38 CPU 38min, 마지막 step), v38 CPU chain GFN2 HESS step 진행 중
- **AIMNet2-NSE = ANI-2x backend 동일 확인** (data redundancy) — v5j matrix에서 10번째 axis 추가 시 사실상 9 distinct method
- **MMFF94/UFF backfill 완료**: v19-v33 누락분 + v34/v36/v37 silent-skip 패턴 인지 후 즉시 `cpu_mmff94_uff_v{N}_only.py` 8초 실행

### 🎯 paper #19 — COCONUT NP DB conformer 진척
- **rdkit COCONUT 66k → 94k 5 pool 동시 가동**: 82-84k / 86-88k / 88-90k / 90-92k / 92-94k 진행 중
- **rdkit 74-76k SIGKILL** (3-signal hit, mid-batch deadlock 95%+92min silent+1R+3S spin signature) → 1978-row partial CSV salvage
- **mid-batch hot-zone 룰 강화**: COCONUT NP DB 60-62k bracket 외 다른 구간도 deadlock 가능

### 💾 H 1TB SSD 활용 (2026-05-11 23:00~)
- **D drive 1.16TB used / 1.5TB**: archive 425GB 이전 후보 산정
- **/mnt/d/genesis_archive (245GB)** → /mnt/h/genesis_archive ✅ **cp DONE 23:57:31** (1h 5min, 평균 63 MB/s)
- **/home/crazat/genesis_archive (180GB)** → /mnt/h/wsl_genesis_archive cp 진행 중 (PID 38884, ETA ~01:13)
- **drvfs 속도 분석**: SATA SSD specs 500MB/s의 ~1/8. 3중 병목 — drvfs round-trip ×2, D 동시부하 (Boltz/rdkit), small-file overhead (genesis_medicine = conda/pip 수만 파일)

### 🚨 신규 feedback memory (2026-05-11~12)
1. `feedback_orchestrator_missing_version_silent_skip.md` — v34 chain 13/13 silent FAIL: Python 스크립트 부재 시 orchestrator silent-skip. `feedback_mamba_run_silent_env_missing` 변형. 패치: master_chain `set -eo pipefail` + 명시 검증
2. `feedback_repeated_identical_prompt_signal.md` — 같은 user prompt 2-3회 짧은 간격 도착 = cron/wakeup loop signal. 본문 boilerplate를 새 directive로 해석 X. 직전 user 명시 지시 우선 (예: "검색 중단")

### 📚 R41/R42 dedup scan — saturation 재확정
- **R41 (2026-05-11)**: ultrathink 광범위 스캔, dedup 후 1/8 신규 (Caliby = #171 동일, dEVA/MetalNet2/BioPipelines 이미 설치)
- **R42 (3h 후)**: 10축 보강 스캔, dedup 1/5 신규 (**DELi + del_qsar Tier-2 only**, wet-lab DEL 의존)
- **결론**: dedup 후 실질 신규 0-1건/24h baseline. 다음 scan 5월 18일 (R43) 권장

### 🛠 활성 작업 (세션 종료 시점, **2026-05-12 00:30 KST**)

| 작업 | PID | 상태 | ETA |
|---|---|---|---|
| **v39 Boltz cofold** (seed 62) | 4129218 | 500/1500 PDB (35min) GPU 99% | ~01:30 KST |
| **v38 CPU chain** (GFN2 HESS step) | 4111298 | [3/8] GFN2 HESS 진행 중 | ~02:00 |
| **cp /home/crazat/genesis_archive → /mnt/h/** | 38884 | 180GB ext4→drvfs cp | ~01:13 KST |
| **rdkit COCONUT 82-94k 5 pool** | (24 worker) | 80-94k 5×4 worker 진행 | 각 ~01:00-02:00 |

### 🎯 다음 세션 우선순위 (2026-05-12 00:30 KST 시점)

**즉시 (다음 진입 시)**:
```bash
date '+%H:%M:%S'
ps -p 4129218 4111298 38884 -o pid,stat,etime --no-headers 2>/dev/null  # v39 cofold, v38 CPU chain, wsl_archive cp
cd /home/crazat/genesis_medicine/pilot/round27_paperA && for v in 38 39; do echo "v$v: $(find boltz_15_100_v19_v$v -name '*.pdb' 2>/dev/null | wc -l) PDB"; done
nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv,noheader,nounits
tail -3 /home/crazat/genesis_medicine/scripts/round27_paperA/master_chain_v19_v38_run.log
du -sh /mnt/h/wsl_genesis_archive 2>/dev/null
uptime
```

1. **v39 cofold 1500 PDB 도달 → Part9 chain scaffold + cascade** — 28th rep으로 v5k matrix Cluster B intra-ρ 추가 확인
2. **v34-v38 MMFF94/UFF backfill 검증** — v5k 28-rep matrix 데이터 완전성
3. **H archive cp #32 완료** → integrity check (du 비교) → symlink swap 결정
4. **paper_A v5 manuscript figure regenerate** — 27→28-rep 데이터로 cluster paradox 안정성 figure update
5. **rdkit COCONUT 94k 이후** — 누적 paper #19 v9 LaMGen input 충분, 100k 도달 시 정지 가능
6. **R43 frontier scan**: 2026-05-18 권장 (사용자 명시 시만)

### ⚠️ 새 대화 진입 시 주의사항 (2026-05-12 갱신)
- **R40 durable rule** 유지: 자동 frontier tech SCAN 금지, 사용자 명시 시만
- **wakeup-loop boilerplate 무시**: PID 2941/4731 GONE 14회 이상 확인. "ABFE orchestrator + 3-solvent xtb chain" + "ultrathink 검토" 패턴 = R28 cron 잔재
- **repeated identical prompt 룰** 신규 적용: 2-3회 동일 prompt 도착 시 cron/loop signal, 본문 boilerplate를 새 directive로 해석 X
- **orchestrator silent-skip 룰** 신규 적용: 5-NNP chain launch 전 Python 스크립트 존재 검증 + master_chain `set -eo pipefail`

---

> **이전 세션 발자취 (2026-05-10 v5g 13-rep × 11-axis matrix)**: 메모리 `project_paper_a_v5g_HEADLINE_13rep_validated_2026_05_10.md` + `project_overnight_12h_2026_05_10_to_11.md` 참조. 모든 PID/ETA stale, 핵심 finding은 paper_A v5h (Zenodo DOI 10.5281/zenodo.20134439, immutable)로 frozen.

---

## 🗄 Archive Backup 정책 (2026-05-25 변경)

**Primary backup 경로 전환**:
- **이전**: `I:\genesis_archive\` + `I:\wsl_genesis_archive\` (ORICO CNM2-U4 외장 SSD)
- **신규**: `gdrive:Projects/Genesis_medicine/genesis_archive/` + `gdrive:Projects/Genesis_medicine/wsl_genesis_archive/`

**변경 사유**: ORICO CNM2-U4 enclosure 의 ASMedia ASM2464PD 가 sustained read 5-7분 후 self-reset. 6시간 이상 재시도 (tar 우회 포함) 모두 같은 dropout 패턴. Scientific archive 가치는 GDrive 현 상태로 100% 충족.

**누락 데이터 (수용)**: ~10K Boltz inference cache 파일 (npz/pdb/json/msa). 위치 패턴 `wsl_genesis_archive/genesis_medicine/pilot/round13_overnight/results/boltz_*_v##/`. 재생성 가능 — Boltz weights + ChEMBL list + 코드 모두 보존됨, GPU 1대로 분~일 단위.

**신규 sync 명령** (WSL → GDrive):
```bash
rclone sync /home/crazat/genesis_medicine/<subdir> \
  gdrive:Projects/Genesis_medicine/genesis_archive/genesis_medicine/<subdir> \
  --transfers 4 --tpslimit 10 --fast-list
```

**NAS Z: + I:\ 새 역할**:
- **NAS Z:** (DS115j 1-bay): secondary cold storage, SMB 2.0.2 한계로 large file 부적합
- **I:\ 외장 SSD**: 게임/단발 파일 보관 한정. Sustained 5분+ workload 금지

**핸드오프 문서 + manifest** (GDrive + WSL `/home/crazat/genesis_medicine/` 양쪽 보존):
- `ARCHIVE_HANDOFF_2026-05-25.md` (10.9 KB) — 전체 정책 + 경로 + 운영 방침
- `MISSING_FILES_MANIFEST_2026-05-25.txt` (15.6 MB) — 누락 93,724개 파일 path + size 리스트
- `MISSING_FILES_MANIFEST_summary_2026-05-25.log` (2 KB) — 카테고리별 요약

**Source disk + enclosure spec** (향후 hardware 추적용): ORICO CNM2-U4 / ASMedia ASM2464PD chipset.

---

## 🛠 활성 작업 (세션 종료 시점, **2026-05-25 11:35 KST**)

### paper_A v6 SI ULTIMATE matrix 14,265+ cohort CSVs

| 작업 | 상태 |
|---|---|
| **paper_A v6 manuscript** | v0.3.23, refs 239 (R49+R50+R51+R52 통합) D-5 publish-ready |
| **paper_A v6 SI cross-Hamiltonian matrix** | GFN0/1/2 × SP+OPT+OHESS × 117-cycle × 24-ALPB × 15-lig ≈ 14,265 cohort CSVs |
| **paper_B σ_E + σ_iptm dual-axis** | GFN0+1+2 OHESS × 22-cycle × 4-ALPB × 15-lig ≈ 4,000 entries |
| **Boltz cascade** | v251-v260 watcher (paper_B widening n=98→n=108), v252 cycle 2/10 진행 중 |
| **GFN0+1+2 OHESS dense20** | GFN0 done (1700 batches 166min), GFN1+2 continued |
| **GFN0 OPT dense20** | 추가 launch (8 worker fill) |

### R31-R34 frontier-tech scan cumulative (64 Tier-1 hits, 38 truly-new integrations)

- **R31** (modality split): A=Foundation models + B=Wet-lab + C=Clinical/RWE + D=Multi-omics → 14 Tier-1, 4 integrations (R49 v0.3.20)
- **R32** (layer split): E=QM/MD + F=Korean + G=AI/LLM + H=Delivery → 14 Tier-1, 9 integrations (R50 v0.3.21)
- **R33** (angle/cross-section): J=Cross-organ + K=Stat UQ + L=Open Science + M=Manufacturing → 17 Tier-1, 17 integrations (R51 v0.3.22)
- **R34** (relational/structural): N=Multi-scale + O=KG-network + P=Cross-species + Q=Adversarial AI → 16 Tier-1, 8 integrations (R52 v0.3.23)

### 🎯 다음 세션 우선순위 (2026-05-25 11:35 KST 시점)

**즉시 (다음 진입 시)**:
```bash
date '+%H:%M:%S'
ls /home/crazat/genesis_medicine/preprints/23_paper_A_v6_mmp1_5nnp_xtb/SI/xtb_gfn*cohort*.csv | wc -l
tail -3 /home/crazat/genesis_medicine/scripts/round27_paperA/boltz_v251_v260_nonblock_watcher.log
nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv,noheader,nounits
uptime
```

1. **paper_A v6 D-5 publish trigger** — manuscript_v0.2.md + references.md (239) + cover_letter Zenodo deposit 2026-05-30
2. **paper_B σ_iptm cross-cycle 22-cycle ULTIMATE dataset** integration 검증 + manuscript figure 추가
3. **paper #19 v0.2 sprint** (KMCRIC outreach 첨부 PDF candidate, D14+14 days = 2026-06-13)
4. **ARPA-H IGoR Solution Summary 2026-06-25 D+33** grant 응모 결정 (ref 239)
5. **추가 frontier-tech scan**: 사용자 명시 시만 (R35 권장)

---

## 🛠 활성 작업 (세션 종료 시점, **2026-05-27 19:01 KST**) — D-3

### paper_A v6 SI v212_v275 unified 통합 cohort + 1755 baseline + odd-cycle (18,000+ CSVs)

| 작업 | 상태 |
|---|---|
| **paper_A v6 manuscript** | v0.3.23 manuscript_v0.2.md publish-ready, **5개 표 검증 0건** (check_tables.py 0 issue) |
| **paper_A v6 SI v212_v262 sept-matrix** | GFN0/1/2 × SP+OPT+OHESS × {GBSA 13-16, ALPB 23} × 765 SDFs **FULLY COMPLETE** (18/18 cells × 16,065 entries) |
| **paper_A v6 SI v263_v270 sept-matrix** | 120 SDFs (8 cycles × 15 lig) **FULLY COMPLETE** 18/18 cells |
| **paper_A v6 SI v271_v273 partial cohort** | 45 SDFs **18 cells COMPLETE** |
| **paper_A v6 SI v274 + v275 single-cycle** | 15 SDFs each, 18 cells each **COMPLETE** |
| **paper_A v6 SI unified v212_v275** | symlink 960 SDFs merged dir. GFN0 OHESS ALPB+GBSA done. GFN1/2 multi-hour 진행 중. |
| **paper_B σ_iptm unified v143-v274** | 132 cycles × 15 lig = 1,980 entries 단일 paper-grade CSV consolidated |
| **paper_B σ_E v212_v274 consolidation** | 1,710 cells × 63 cycles. Top σ outliers CHEMBL257077 (σ=98.17 kcal) / CHEMBL94487 (σ=85.34) / CHEMBL412 (σ=82.55) |
| **Boltz v261-v270 cascade COMPLETE** | paper_B n=108→n=118 (Task #61) |
| **Boltz v271-v280 cascade COMPLETE** | paper_B n=118→n=128 (Task #78) |
| **Boltz v281-v290 cascade IN PROGRESS** | watcher PID 291263, v282 cycle 진행 중 (Task #82). n=128→n=138 ETA ~05:00 다음 날 |
| **check_tables.py prevention logic** | /preprints/23_paper_A_v6.../tools/check_tables.py (4-cat 검증) + Makefile (`make check-all`) + README. 5/30 publish 직전 자동 실행 의무 |

### 2-day 누적 성취 (2026-05-25 → 2026-05-27)

- **v212_v275 unified cohort** 새로 구축: 5 disjoint sub-cohorts (v212_v262/v263_v270/v271_v273/v274/v275) symlink merge → 960 SDFs 단일 sept-matrix 입력
- **v263_v270+v271_v273+v274+v275** 4 새 cohort 18 cells each fully complete (5,400+ new CSVs)
- **2 Boltz cascade complete** (n=128 도달) + 3rd cascade ongoing
- **σ_E/σ_iptm consolidation scripts** 영구 설치 (`consolidate_paper_a_sigma_e_v212_v274.py`, `consolidate_paper_b_sigma_iptm_unified.py`)
- **check_tables.py prevention logic** 영구 설치 — 향후 모든 manuscript publish 직전 자동 검증
- **GPU 일시정지/재개 SIGCONT/SIGSTOP** rule 발견 + 메모리 영구 저장 (`feedback_sigstop_setsid_child_target.md`)

### 🎯 다음 세션 우선순위 (2026-05-27 19:01 KST 시점) — **D-3 publish countdown**

**즉시 (다음 진입 시)**:
```bash
date '+%H:%M:%S'
nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv,noheader
uptime
tail -3 /home/crazat/genesis_medicine/scripts/round27_paperA/boltz_v281_v290_nonblock_watcher.log
ps -p 291263 -o pid,stat --no-headers  # watcher Ss = running, Ts = SIGSTOPped
ls /home/crazat/genesis_medicine/preprints/23_paper_A_v6_mmp1_5nnp_xtb/SI/xtb_gfn?_ohess_*_v212_v275_*.csv | wc -l
```

1. **paper_A v6 D-3 publish trigger 2026-05-30** — Zenodo deposit. **publish 직전 `make check-all` 실행 의무** (`/preprints/23_paper_A_v6.../tools/check_tables.py`)
2. **paper_B σ_iptm/σ_E 통합 dataset** narrative integration → manuscript_skeleton_v0.1 → v0.2 sprint
3. **paper #19 v0.2 sprint** (KMCRIC outreach attachment PDF, D14+ = 2026-06-13)
4. **Boltz cascade continuation**: v281-v290 → v291-v300 (필요 시 새 watcher 생성, 패턴은 boltz_v281_v290_nonblock_watcher.sh 참조)
5. **GPU 일시정지** 요청 시: `kill -STOP 291263` (script PID — eval wrapper PID 아님), 재개 `kill -CONT 291263`

---

## 🛠 활성 작업 (세션 종료 시점, **2026-05-29 11:13 KST**) — D-1

> paper_A v6 publish countdown **D-1** (Zenodo deposit 2026-05-30, 내일). 야간 22:00-10:00 자율 ROI 무중단 운영 지속 — Boltz widening cascade + σ_E dense-cycle backfill CPU floor 병렬 포화.

### Boltz widening cascade (paper_B σ_iptm n 확장)

| 작업 | 상태 |
|---|---|
| **Boltz v291-v300 cascade COMPLETE** | paper_B n=138→n=148 (Task #94) |
| **Boltz v301-v310 cascade IN PROGRESS** | watcher `boltz_v301_v310_nonblock_watcher.sh`, seed=N+1104. v308 done @09:50 (**n=156**), v309 진행 중. **watcher v310에서 종료 → ~13:00 완료 시 v311-v320 새 watcher launch 의무** (GPU idle 방지) |

### paper_A v6 SI σ_E dense-cycle backfill — CPU-floor 전략 (구조적 신규)

> Boltz는 ~1.5hr/cycle인데 CPU는 15-SDF sept-matrix를 ~25min에 처리 → CPU duty-cycle gap. 해법: **미처리 cycle 범위를 큰 240-300 SDF backfill "floor"로 launch** → CPU를 GPU pace와 decouple하며 σ_E 데이터도 densify (σ_iptm n=161 수준으로 수렴).

| cohort | SDF | 상태 |
|---|---|---|
| **v291_v300 / v301_v302 / v304_v305 / v306** incremental | 150/30/30/15 | 18-cell sept-matrix **COMPLETE** (Task #98/#100/#102) |
| **v196_v211 backfill floor #1** | 240 | 18-cell **COMPLETE 342/342** (Task #101) |
| **v176_v195 backfill floor #2** | 300 | 18-cell 진행 중 ~76% (현재 CPU 주력, ~2hr runway, Task #103) |
| **v156_v175 backfill floor #3** | 300 | scripts + SDFs **준비 완료**, v176 winddown(~6 cells) 시 SP+OPT launch 후 OHESS defer (≤18-cell thrash 회피, Task #104) |

### consolidation 데이터셋 (paper-grade)

- **paper_B σ_iptm unified v143-v303**: 161 cycles × 15 lig = 2,415 per-cycle rows. **CHEMBL259829 TRUE outlier** (σ_inter 최대), CHEMBL57058 most reliable. COLMAP 정규화 (v143-v211 `iptm_*`/`n_samples` vs v212+ `mean`/`std`/`n`) — uniform-0.49 artifact 영구 해결. Builder: `consolidate_paper_b_sigma_iptm_v143_v303.py`
- **paper_A σ_E unified v212_v303**: 1,755 cells × n=92 cycles/cell. Top σ_G outlier CHEMBL257077 GFN1 alpb/phenol σ=100.45 kcal / CHEMBL94487 GFN2 alpb/ethylacetate σ=86.12. Builder: `consolidate_paper_a_sigma_e_v212_v303_unified.py`
- v176_v195 / v156_v175 floor 완료 시 COHORTS 리스트에 추가하여 σ_E 재consolidation 권장

### 🎯 다음 세션 우선순위 (2026-05-29 11:13 KST 시점) — **D-1 publish countdown**

**즉시 (다음 진입 시)**:
```bash
date '+%H:%M:%S'
nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv,noheader
tail -4 /home/crazat/genesis_medicine/scripts/round27_paperA/boltz_v301_v310_nonblock_watcher.log
ls /home/crazat/genesis_medicine/preprints/23_paper_A_v6_mmp1_5nnp_xtb/SI/xtb_gfn?_*_v176_v195.csv | wc -l  # /342
ps -eo state | grep -c '^D'  # D-state 데드락 체크 (load는 WSL2 thread artifact, 단독 SIGKILL 금지)
```

1. **🔥 paper_A v6 D-0 publish 2026-05-30 (내일)** — Zenodo deposit. **직전 `make check-all` 의무** (`/preprints/23_paper_A_v6.../tools/check_tables.py`). co-author 무응답 시 single-author fallback (memory #20-22 precedent)
2. **Boltz v310 완료(~13:00) 시 v311-v320 새 watcher launch** — `boltz_v301_v310_nonblock_watcher.sh` 클론, `seq 311 320`, seed=N+1104 동일 패턴. GPU idle 방지
3. **v176_v195 floor winddown 시 v156_v175 floor launch** (준비 완료, SP+OPT 먼저 12 cells, OHESS defer)
4. **σ_E unified 재consolidation** (v176_v195 + v156_v175 cohort 추가) → paper_A SI / paper_B σ_E narrative densify
5. **paper_B σ_iptm v304-v310 extension** (cascade 산출 시) + manuscript_skeleton_v0.1 → v0.2 sprint

## 🛠 활성 작업 (세션 종료 시점, **2026-06-01 20:26 KST**) — 🛑 GPU+CPU 전면 PAUSE (사용자 재부팅)

> **현재 상태: 모든 연산 정지.** 사용자가 GPU(Boltz cascade) → CPU(σ_E sept-matrix) 순으로 명시 일시정지 요청 후 컴퓨터 재부팅. 재부팅 후 idle은 **정상** — autonomous tick이 자동 relaunch하면 안 됨 (memory `feedback-gpu-paused-2026-06-01`). 사용자가 직접 "재개" 요청할 때까지 모든 launch 침묵.

### Boltz widening cascade (paper_B σ_iptm) — v351에서 PAUSE

| 작업 | 상태 |
|---|---|
| **v311-v320 / v321-v330 cascade** | COMPLETE (paper_B n 확장 지속) |
| **v327-v340 cascade RESUMED** | post-GPU-pause gap-fill + forward, v326→v340 contiguous (Task #120) |
| **v341-v350 cascade** | COMPLETE (Task #125) |
| **v351** | 🛑 마지막 cycle — 1500/1500 PDB 완료 후 GPU PAUSE. v351-v360 watcher 정지, v352+ 미launch. 재개 시 v352부터 |

### paper_A v6 SI σ_E sept-matrix — 2개 cohort 동시 진행 중 PAUSE

| cohort | SDF | 상태 |
|---|---|---|
| **v11_v18 ~ v336_v337 backfill floors #1-#13** | dense | 18-cell sept-matrix **COMPLETE** (historical v11→ + rolling v327_v335/v336_v337, Task #101-#124) |
| **v212_v290 UNIFIED** (대형) | 1185 | 18-cell barrier-free gate=3. 🛑 PAUSE 시점 = OHESS GBSA cell `ether 9/16` (SP/OPT 전부 + OHESS ALPB 완료). `master_floor_v212_v290.sh` (Task #126) |
| **v338_v351 NEW cohort** | 210 | 🆕 v290 이후 미처리 14 cycle × 15 lig. CPU headroom 충당용 launch. 🛑 PAUSE 시점 = **282 CSV 저장** (SP/OPT 완료, OHESS 진입). `master_floor_v338_v351.sh` (Task #128) |

> **재개 방법**: 두 master 모두 per-solvent CSV **SKIP 로직** 보유 → `setsid nohup bash master_floor_v212_v290.sh` / `master_floor_v338_v351.sh` 재실행하면 완료 CSV는 건너뛰고 미완 cell부터 이어감. 데이터 손상 없음 (CSV는 solvent 완결 시 원자적 기록).

### 신뢰성 reframe 산출물 (R53-R56)

- **Conformal reliability layer** (R53 P1): σ_iptm/σ_E → guaranteed-coverage interval (normalized split-conformal), 200-split empirical coverage ≈ nominal. `conformal_reliability_layer.py` + `DRAFT_conformal_section.md` (manuscript 삽입 사용자 확인 대기)
- **R54/R55/R56**: multiverse/G-theory 분산분해 + killer figure + numerical-floor 2-arm control + scoring-rules(CRPS/PIT) + descriptor→σ error model + indapamide-lead safety §6.6.2 (dermal Kp computed)

### 🎯 다음 세션 우선순위 (2026-06-01 시점)

**즉시 (다음 진입 시)** — ⚠️ **사용자 "재개" 요청 전까지 연산 launch 금지**:
```bash
TZ=Asia/Seoul date '+%H:%M %Z'
pgrep -c xtb; pgrep -af "boltz predict" | grep -v 'bash -c'   # 0 / none 이면 PAUSE 유지 정상
nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv,noheader
```

1. **🛑 PAUSE 유지** — 사용자가 직접 "재개" 말할 때까지 GPU(Boltz)·CPU(σ_E master_floor) 자동 relaunch 금지. 재개 시 memory `feedback-gpu-paused-2026-06-01` 삭제
2. **재개 시 CPU**: `master_floor_v212_v290.sh` (ether 9/16 이어서) + `master_floor_v338_v351.sh` (282 CSV 이후) 재실행 (SKIP 로직으로 이어감)
3. **재개 시 GPU**: v352부터 `boltz_v351_v360_nonblock_watcher.sh` 재launch (또는 새 decade watcher 클론)
4. **paper_A v6 제출 결정** = 최고 ROI 레버, **사용자 보류 중** (저널 타깃 미정). 결정 시 R56 freeze + cleanup pass(R-tag/corridor 제거, citation 정규화) + 저널 포맷
5. **σ_E unified 재consolidation** (v338_v351 cohort 추가) + paper_B σ_iptm v327-v351 extension

## 🛠 활성 작업 (세션 종료 시점, **2026-06-01 21:46 KST**) — 재부팅 후 전면 재개 + GPU-floor 스윗스팟 확립

> 재부팅 완료 → 사용자 "CPU+GPU 전면 재개 + 자율 ROI 모니터링". 재개 중 2개 이슈 진단·해결: ① 재부팅 후 첫 Boltz cycle livelock, ② CPU 오버서브로 인한 GPU floor 저하 → **affinity 분할로 스윗스팟 확립**. 모든 연산 정상 가동.

### 🔧 재부팅 후 첫 Boltz cycle livelock (해결)

- v352 첫 attempt: ligand 1(100 PDB) 후 ligand 2에서 **22분 hang** (state R, ~1코어 spin, 출력 mtime 정지, GPU flat 2-13% burst 전무). pynvml "Not Supported" + GPU A6000 오진(실제 5090) 경고 동반.
- CPU starvation 가설은 cohort kill로 CPU 풀어도(xtb 32→8) GPU 회복 안 돼 기각 → **boltz 자체 일회성 livelock** 확정.
- **복구**: hung boltz `kill -9` → watcher가 exit=137 감지, 3-attempt retry로 partial rm 후 v352 attempt-2 launch → 정상(GPU 100% 도달). memory `feedback-boltz-postreboot-first-cycle-livelock`.

### 🎯 GPU-floor 스윗스팟 (affinity 분할, 측정 확립)

> `--use_potentials`는 ligand당 1회 CPU-bound potential phase를 돌림 → CPU 오버서브(32 xtb/24 core) 시 GPU가 100% burst ↔ 7-9% deep dip 반복(낮은 avg). nice만으론 부족, **물리적 코어 분리** 필요.

| CPU 분할 | GPU avg | CPU 활용 | 평가 |
|---|---|---|---|
| σ_E 8 / boltz 16 (free) | ~89% | 33% | floor 최고, CPU 낭비 |
| **σ_E 16 / boltz 8 (pinned) ← 채택** | **~86%** | **67%** | diffusion 99-100%, ligand 경계 dip만 |
| σ_E 16 / boltz unpinned | ~56% | 67% | starve — pin 필수 |

- **구현**: σ_E masters를 `taskset -c 0-15`로 launch(코어 0-15 전용, future cell 상속) + boltz는 `boltz_affinity_pin_daemon.sh`(20s마다 `boltz predict`를 16-23로 re-pin, cycle 넘어가도 유지). memory `feedback-gpu-floor-priority-over-cpu-sigma-e`.
- GPU idle/cascade gap엔 affinity 풀고 σ_E가 24코어 전체 사용 가능.

### 현재 가동 상태 (자율 ROI 복귀)

| 자원 | 상태 |
|---|---|
| **GPU** | boltz v352 (seed 1456) cascade, ~96%, pin 16-23. `boltz_v352_v360` watcher + **v361-v370 decade chain 무장** |
| **CPU** | σ_E v212_v290 + v338_v351 양 cohort, 코어 0-15(16코어), xtb 32 / load 33 |
| **pin 데몬** | `boltz_affinity_pin_daemon.sh` 가동 (boltz 16-23 유지) |
| **자율 모니터링** | pause 메모리 삭제 → cron `<<autonomous-loop>>` ROI 판단 복귀 |

### 🎯 다음 세션 우선순위 (2026-06-01 21:46 시점)

**즉시 (다음 진입 시)**:
```bash
TZ=Asia/Seoul date '+%H:%M %Z'
nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv,noheader   # diffusion 99-100% 정상, dip은 ligand 경계
pgrep -af "boltz predict" | grep -v 'bash -c'                              # cascade 살아있나
pgrep -fc "boltz_affinity_pin_daemon.sh"                                   # pin 데몬 1이어야
taskset -cp $(pgrep -x xtb|head -1) | sed 's/.*: //'                       # σ_E xtb = 0-15 확인
```

1. **affinity 스윗스팟 유지** — 새 σ_E cohort launch 시 반드시 `taskset -c 0-15`. pin 데몬 죽으면 재가동. 새 boltz watcher/chain 클론 시에도 pin 데몬이 cover (boltz predict 패턴 매칭).
2. **decade chain 연속** — v360 완료 시 v361-v370 자동 launch (decade_chain_v361 armed). 이후 v371+ 새 chain 클론.
3. **v338_v351 (282 CSV)** — GPU 가동 중엔 0-15에서 v212와 공존. v212_v290(마지막 OHESS GBSA cell) 완료 시 v338 단독.
4. **paper_A v6 제출 결정** = 최고 ROI 레버, **사용자 보류 중** (저널 미정).
5. **σ_E unified 재consolidation** (v338_v351 + 신규 cohort) + paper_B σ_iptm v327-v360 extension.
